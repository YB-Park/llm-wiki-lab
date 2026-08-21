'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const library = require('../personal-wiki-library');
const workspaceActivation = require('../workspace-activation');

function stateStore() {
  const values = new Map();
  return {
    get(key, fallback) { return values.has(key) ? values.get(key) : fallback; },
    async update(key, value) {
      if (value === undefined) values.delete(key); else values.set(key, value);
    },
  };
}

function context() {
  return { globalState: stateStore(), workspaceState: stateStore() };
}

function makeStore(parent, name) {
  const root = path.join(parent, name);
  fs.mkdirSync(root, { recursive: true });
  fs.writeFileSync(path.join(root, 'config.json'), JSON.stringify({ format: 'llm-wiki-dogfood-v0' }));
  fs.writeFileSync(path.join(root, 'manifest.jsonl'), '');
  return root;
}

function folder(name = 'current') {
  return { uri: { toString: () => `file:///test/${name}` } };
}

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-library-test-'));
  try {
    const currentRoot = makeStore(tmp, 'current');
    const rootA = makeStore(tmp, 'external-a');
    const rootB = makeStore(tmp, 'external-b');
    workspaceActivation.enableWorkspace(currentRoot);

    const ctx = context();
    const currentFolder = folder();
    const a = await library.registerStore(ctx, {
      root: rootA,
      currentRoot,
      displayName: 'Project A',
      aliases: ['alpha'],
    });
    assert.match(a.storeId, library.STORE_ID_RE);
    assert.deepEqual(library.registeredStores(ctx), [{
      storeId: a.storeId,
      displayName: 'Project A',
      aliases: ['alpha'],
    }]);
    assert.throws(
      () => library.resolveNamedStore(ctx, currentFolder, currentRoot, 'Project A'),
      /library_access_disabled/
    );

    await library.setLibraryAccess(ctx, currentFolder, currentRoot, true);
    const handle = library.resolveNamedStore(ctx, currentFolder, currentRoot, 'ALPHA');
    assert.equal(handle.storeId, a.storeId);
    assert.equal(handle.root, fs.realpathSync(rootA));
    assert.deepEqual(handle.scopeRef, { kind: 'library_store', store_id: a.storeId });
    assert.equal(handle.isCurrentStore, false);
    assert.equal(library.resolveStoreId(ctx, currentFolder, currentRoot, a.storeId).storeId, a.storeId);

    await library.registerStore(ctx, {
      root: rootB,
      currentRoot,
      displayName: 'Project B',
      aliases: ['alpha'],
    });
    assert.throws(
      () => library.resolveNamedStore(ctx, currentFolder, currentRoot, 'alpha'),
      /library_store_ambiguous/
    );

    assert.throws(
      () => library.resolveNamedStore(ctx, currentFolder, currentRoot, 'missing'),
      /library_store_not_registered/
    );
    await assert.rejects(
      library.registerStore(ctx, { root: currentRoot, currentRoot, displayName: 'Current' }),
      /library_store_is_current_store/
    );

    workspaceActivation.disableWorkspace(currentRoot);
    workspaceActivation.enableWorkspace(currentRoot);
    assert.equal(library.libraryGrant(ctx, currentFolder, currentRoot), undefined);
    assert.throws(
      () => library.resolveStoreId(ctx, currentFolder, currentRoot, a.storeId),
      /library_access_disabled/
    );

    await library.setLibraryAccess(ctx, currentFolder, currentRoot, true);
    assert.ok(library.libraryGrant(ctx, currentFolder, currentRoot));
    await library.setLibraryAccess(ctx, currentFolder, currentRoot, false);
    assert.equal(library.libraryGrant(ctx, currentFolder, currentRoot), undefined);

    console.log('personal-wiki-library tests: PASS');
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});