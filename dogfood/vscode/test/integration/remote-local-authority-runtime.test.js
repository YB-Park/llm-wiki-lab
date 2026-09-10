'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vscode = require('vscode');

async function stage(label, promise, timeoutMs = 30000) {
  let timer;
  try {
    return await Promise.race([
      Promise.resolve(promise),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`VS-REMOTE-LOCAL-STAGE timeout=${label}`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function fakeContext(extensionPath) {
  const state = new Map();
  return {
    extensionPath,
    workspaceState: {
      get(key) { return state.get(key); },
      async update(key, value) {
        if (value === undefined) state.delete(key);
        else state.set(key, value);
      },
    },
  };
}

async function resetAndEnable() {
  const folder = (vscode.workspace.workspaceFolders || [])[0];
  assert.ok(folder, 'integration test workspace is not open');
  const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
  try { await vscode.commands.executeCommand('llmWiki.disableWorkspace'); } catch (_) {}
  fs.rmSync(wikiRoot, { recursive: true, force: true });
  const enabled = await stage('enable-workspace', vscode.commands.executeCommand('llmWiki.enableWorkspace'));
  assert.equal(enabled, true, 'explicit workspace opt-in failed');
  return { folder, wikiRoot };
}

suite('LLM Wiki local Personal Wiki authority', () => {
  test('publishes current Project Memory locally without invoking ssh', async function () {
    if (process.platform !== 'linux') this.skip();

    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'LLM Wiki extension was not discovered');
    await extension.activate();

    const { folder, wikiRoot } = await resetAndEnable();
    const remoteMemory = require(path.join(extension.extensionPath, 'remote-memory.js'));
    const authorityHome = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-local-authority-'));
    const fakeBin = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-no-self-ssh-'));
    const sshCalled = path.join(fakeBin, 'ssh-called');
    const fakeSsh = path.join(fakeBin, 'ssh');
    fs.writeFileSync(fakeSsh, '#!/bin/sh\ntouch "$LLM_WIKI_TEST_SSH_CALLED"\necho self-ssh-forbidden >&2\nexit 97\n', { mode: 0o755 });

    const oldRemoteHome = process.env.LLM_WIKI_REMOTE_HOME;
    const oldSshCalled = process.env.LLM_WIKI_TEST_SSH_CALLED;
    const oldPath = process.env.PATH;
    process.env.LLM_WIKI_REMOTE_HOME = authorityHome;
    process.env.LLM_WIKI_TEST_SSH_CALLED = sshCalled;
    process.env.PATH = `${fakeBin}${path.delimiter}${oldPath || ''}`;

    try {
      const context = fakeContext(extension.extensionPath);
      const row = await stage(
        'local-authority-connect',
        remoteMemory.connect(context, folder, { target: remoteMemory.LOCAL_AUTHORITY_TARGET }),
        60000
      );

      assert.ok(row, 'local authority connect returned no binding');
      assert.equal(row.target, remoteMemory.LOCAL_AUTHORITY_TARGET);
      assert.equal(row.writable, true);
      assert.match(row.storeId, remoteMemory.STORE_ID_RE);
      assert.match(row.snapshotId, remoteMemory.SNAPSHOT_ID_RE);
      assert.equal(fs.existsSync(sshCalled), false, 'local authority path invoked ssh');

      const catalogPath = path.join(authorityHome, 'catalog.json');
      assert.ok(fs.existsSync(catalogPath), 'local authority catalog was not created');
      const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
      const published = catalog.stores.find((store) => store.store_id === row.storeId);
      assert.ok(published, 'published store is missing from local authority catalog');
      assert.equal(published.bootstrap_complete, true);

      const stores = await stage('local-authority-list', remoteMemory.listStores(context, folder));
      assert.ok(stores.some((store) => store.store_id === row.storeId), 'local authority list did not return published store');
      assert.equal(fs.existsSync(path.join(wikiRoot, 'workspace-opt-in.json')), true, 'local workspace opt-in was not preserved');
      assert.equal(fs.existsSync(sshCalled), false, 'local authority list invoked ssh');

      const key = remoteMemory.bindingKey ? remoteMemory.bindingKey(folder) : `llmWiki.remoteBinding.v1:${folder.uri.toString()}`;
      await context.workspaceState.update(key, {
        ...row,
        writable: false,
        refreshPending: true,
        lastError: 'remote_snapshot_fetch_failed:remote_authority_process_failed',
      });
      const recovered = await stage(
        'local-authority-recover-refresh-pending',
        remoteMemory.refreshReplica(context, folder),
        60000
      );
      assert.equal(recovered.refreshPending, false, 'explicit refresh did not clear refreshPending');
      assert.equal(recovered.writable, true, 'explicit refresh did not restore write authority');
      assert.equal(recovered.lastError, '', 'explicit refresh did not clear the previous failure');
      assert.equal(fs.existsSync(sshCalled), false, 'refresh-pending recovery invoked ssh for local authority');
      assert.match(remoteMemory.diagnosticCode('remote_snapshot_fetch_failed:snapshot_source_integrity_failed'), /^remote_snapshot_fetch_failed:/);
    } finally {
      if (oldRemoteHome === undefined) delete process.env.LLM_WIKI_REMOTE_HOME;
      else process.env.LLM_WIKI_REMOTE_HOME = oldRemoteHome;
      if (oldSshCalled === undefined) delete process.env.LLM_WIKI_TEST_SSH_CALLED;
      else process.env.LLM_WIKI_TEST_SSH_CALLED = oldSshCalled;
      process.env.PATH = oldPath;
      fs.rmSync(authorityHome, { recursive: true, force: true });
      fs.rmSync(fakeBin, { recursive: true, force: true });
    }
  });
});
