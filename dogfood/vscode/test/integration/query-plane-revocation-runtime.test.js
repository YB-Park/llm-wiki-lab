'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const queryPlane = require('../../query-plane');
const library = require('../../personal-wiki-library');
const workspaceActivation = require('../../workspace-activation');

function stateStore() {
  const values = new Map();
  return {
    get(key, fallback) { return values.has(key) ? values.get(key) : fallback; },
    async update(key, value) {
      if (value === undefined) values.delete(key); else values.set(key, value);
    },
  };
}

function makeCurrentStore(parent) {
  const root = path.join(parent, '.wiki-lab');
  fs.mkdirSync(path.join(root, 'raw'), { recursive: true });
  fs.writeFileSync(path.join(root, 'config.json'), '{}\n');
  fs.writeFileSync(path.join(root, 'manifest.jsonl'), '');
  workspaceActivation.enableWorkspace(root);
  return root;
}

function makeExternalStore(parent) {
  const root = path.join(parent, 'external', '.wiki-lab');
  fs.mkdirSync(path.join(root, 'raw'), { recursive: true });
  fs.writeFileSync(path.join(root, 'config.json'), '{}\n');
  const sha256 = 'a'.repeat(64);
  fs.writeFileSync(path.join(root, 'manifest.jsonl'), `${JSON.stringify({
    event: 'ingest',
    source_id: 'src-revocation-test',
    object_id: `obj-${sha256}`,
    sha256,
    size_bytes: 1,
    name: 'revocation.md',
  })}\n`);
  return root;
}

suite('LLM Wiki Query Plane revocation boundary', () => {
  test('query and library grants are revalidated immediately before model exposure', async () => {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-f1-reauth-'));
    try {
      const currentRoot = makeCurrentStore(tmp);
      const externalRoot = makeExternalStore(tmp);
      const folder = {
        uri: {
          fsPath: tmp,
          toString: () => 'file:///f1-pre-model-reauthorization',
        },
      };
      const context = { globalState: stateStore(), workspaceState: stateStore() };
      const optIn = workspaceActivation.readWorkspaceOptIn(currentRoot);
      await context.workspaceState.update(queryPlane.grantKey(folder), {
        version: queryPlane.GRANT_VERSION,
        enabled: true,
        provider: 'github_copilot',
        model: queryPlane.MODEL,
        scope: 'current_store',
        evidenceExposure: 'retrieved_admitted_memory_only',
        workspaceEnabledAt: optIn.enabled_at,
        workspaceEpoch: workspaceActivation.workspaceEpoch(optIn),
        dailyCallLimit: 1,
        maxAiCredits: 1,
      });

      const registered = await library.registerStore(context, {
        root: externalRoot,
        currentRoot,
        displayName: 'Project A',
        aliases: ['alpha'],
      });
      await library.setLibraryAccess(context, folder, currentRoot, true);
      const originalHandle = library.resolveNamedStore(context, folder, currentRoot, 'Project A');
      assert.equal(originalHandle.storeId, registered.storeId);

      const allowed = queryPlane.preModelAuthorization(context, folder, 'Project A', originalHandle);
      assert.equal(allowed.state, 'authorized');
      assert.equal(allowed.storeHandle.storeId, registered.storeId);
      assert.ok(allowed.grant);

      await library.setLibraryAccess(context, folder, currentRoot, false);
      const libraryRevoked = queryPlane.preModelAuthorization(context, folder, 'Project A', originalHandle);
      assert.equal(libraryRevoked.state, 'library_scope_revoked');
      assert.match(String(libraryRevoked.error && libraryRevoked.error.message), /library_access_disabled/);

      await library.setLibraryAccess(context, folder, currentRoot, true);
      await context.workspaceState.update(queryPlane.grantKey(folder), undefined);
      const queryRevoked = queryPlane.preModelAuthorization(context, folder, 'Project A', originalHandle);
      assert.equal(queryRevoked.state, 'query_grant_revoked');
    } finally {
      fs.rmSync(tmp, { recursive: true, force: true });
    }
  });
});
