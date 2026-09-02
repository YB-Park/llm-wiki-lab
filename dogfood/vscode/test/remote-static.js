'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const productView = fs.readFileSync(path.join(root, 'product-view.js'), 'utf8');
const remoteMemory = fs.readFileSync(path.join(root, 'remote-memory.js'), 'utf8');
const remoteAttach = fs.readFileSync(path.join(root, 'remote-attach.js'), 'utf8');
const remotePolicy = fs.readFileSync(path.join(root, 'remote-project-policy.js'), 'utf8');
const remoteLibrary = fs.readFileSync(path.join(root, 'remote-library.js'), 'utf8');
const snapshotTransfer = fs.readFileSync(path.join(root, 'remote-snapshot-transfer.js'), 'utf8');
const attachImporter = fs.readFileSync(path.resolve(root, '..', 'llm_wiki', 'remote_attach_import.py'), 'utf8');
const libraryUi = fs.readFileSync(path.join(root, 'personal-wiki-library-ui.js'), 'utf8');

function must(label, condition) {
  assert.ok(condition, `REMOTE-STATIC ${label}`);
}
function mustNot(label, condition) {
  assert.ok(!condition, `REMOTE-STATIC ${label}`);
}

assert.deepEqual(manifest.extensionKind, ['workspace'], 'REMOTE-STATIC extension-kind-workspace');
must('connect-command', (manifest.contributes.commands || []).some((row) => row.command === 'llmWiki.connectPersonalWiki'));
must('refresh-command', (manifest.contributes.commands || []).some((row) => row.command === 'llmWiki.refreshPersonalWiki'));
for (const name of ['llmWiki_rememberSource', 'llmWiki_rememberHumanKnowledge', 'llmWiki_resolveLineage']) {
  const tool = manifest.contributes.languageModelTools.find((row) => row.name === name);
  must(`offline-write-tool-gated:${name}`, tool && tool.when.includes('llmWiki.remoteWritable'));
}

must('product-connection-choice', productView.includes('remoteAttach.chooseConnection'));
must('product-readonly-state', productView.includes('Offline · read only') && productView.includes('Refresh pending · read only'));
must('product-no-write-while-readonly', productView.includes('Unavailable while read only'));

const attachStart = remoteAttach.indexOf('async function attachExisting');
const attachEnd = remoteAttach.indexOf('async function chooseConnection', attachStart);
must('attach-function-bounded', attachStart >= 0 && attachEnd > attachStart);
const attachExistingBody = remoteAttach.slice(attachStart, attachEnd);
must('attach-explicit-existing-choice', attachExistingBody.includes('Use Existing Project Memory'));
must('attach-no-identity-inference', attachExistingBody.includes('No repository, path, branch, file-content similarity, or folder name is used to choose project identity.'));
must('attach-no-merge', attachExistingBody.includes('This is an explicit attach, not a merge.'));
assert.ok((attachExistingBody.match(/assertFreshLocalMemory\(root\)/g) || []).length >= 2, 'REMOTE-STATIC attach-fast-rechecks-local-empty');
must('attach-exact-store-id', attachExistingBody.includes("stores.find((store) => store.storeId === requestedStoreId)"));
must('attach-only-bootstrapped-store', remoteAttach.includes('store.bootstrap_complete === true'));
must('attach-uses-shared-snapshot-transfer', attachExistingBody.includes('snapshotTransfer.fetchSnapshot'));
must('attach-selects-writer-locked-import', attachExistingBody.includes('{ attachEmpty: true }'));
const attachTransferIndex = attachExistingBody.indexOf('const snapshotId = await snapshotTransfer.fetchSnapshot');
const bindingPublishIndex = attachExistingBody.indexOf('await context.workspaceState.update(key, row)');
must('attach-binding-after-verified-materialization', attachTransferIndex >= 0 && bindingPublishIndex > attachTransferIndex);
mustNot('attach-no-temporary-binding-before-transfer', attachExistingBody.slice(0, attachTransferIndex).includes('workspaceState.update(key'));
mustNot('attach-no-refresh-via-published-binding', attachExistingBody.includes('remoteMemory.refreshReplica(context, folder)'));
mustNot('attach-no-repo-discovery', attachExistingBody.includes('git remote') || attachExistingBody.includes('repositoryUrl'));
must('attach-explicit-new-choice', remoteAttach.includes('Create New Project Memory'));

must('attach-importer-posix-only', attachImporter.includes('os.name != "posix"'));
must('attach-importer-writer-lock', attachImporter.includes('with store_writer_lock(root):'));
must('attach-importer-final-empty-check-under-lock', attachImporter.indexOf('with store_writer_lock(root):') < attachImporter.indexOf('assert_empty_attach_destination(root)'));
must('attach-importer-preserves-host-local', attachImporter.includes('preserve_host_local=True'));
must('attach-importer-integrity-gate', attachImporter.includes('audit_alpha_integrity(root).get("ok") is not True'));
must('attach-importer-allows-lock-rendezvous-only', attachImporter.includes('LOCK_FILE'));

must('fresh-policy-only-baseline-files', remotePolicy.includes("'config.json'") && remotePolicy.includes("'manifest.jsonl'") && remotePolicy.includes("'raw'") && remotePolicy.includes("'workspace-opt-in.json'"));
must('fresh-policy-manifest-empty', remotePolicy.includes('manifestStat.size !== 0'));
must('fresh-policy-raw-empty', remotePolicy.includes('fs.readdirSync(raw).length !== 0'));
must('fresh-policy-extra-portable-fails', remotePolicy.includes('!FRESH_LOCAL_ENTRIES.has(name)'));
must('fresh-policy-symlink-failclosed', remotePolicy.includes('stat.isSymbolicLink()'));
must('fresh-policy-opt-in-required-local', remotePolicy.includes("safeLstat(optIn, 'file')"));

must('snapshot-transfer-binary-stream', snapshotTransfer.includes('ssh.stdout.pipe(importer.stdin)'));
must('snapshot-transfer-attach-module', snapshotTransfer.includes("'dogfood.llm_wiki.remote_attach_import'"));
must('snapshot-transfer-cache-module', snapshotTransfer.includes("'dogfood.llm_wiki.remote_snapshot'"));
must('snapshot-transfer-cache-replaces-hostlocal', snapshotTransfer.includes("'--replace-host-local'"));
must('snapshot-transfer-verifies-snapshot-id', snapshotTransfer.includes('remoteMemory.SNAPSHOT_ID_RE.test'));

must('remote-library-host-local-global-storage', remoteLibrary.includes('context.globalStorageUri'));
must('remote-library-target-path-hashed', remoteLibrary.includes('remotePolicy.authorityCacheKey(target)'));
mustNot('remote-library-no-raw-target-in-cache-path', remoteLibrary.includes("path.join(base, 'remote-library', target"));
must('remote-library-private-parent', remoteLibrary.includes('fs.chmodSync(parent, 0o700)'));
must('remote-library-excludes-current-store', remoteLibrary.includes('store.storeId !== binding.storeId'));
must('remote-library-uses-shared-verified-transfer', remoteLibrary.includes('snapshotTransfer.fetchSnapshot'));
must('remote-library-not-attach-mode', remoteLibrary.includes('{ attachEmpty: false }'));
must('remote-library-reuses-existing-federation', remoteLibrary.includes('library.registerStore(context'));
must('remote-library-separate-workspace-grant', remoteLibrary.includes('library.setLibraryAccess(context, folder, currentRoot, true)'));
must('remote-library-explicit-readonly-disclosure', remoteLibrary.includes('Add Read-only Project'));
mustNot('remote-library-no-model-call', remoteLibrary.includes('vscode.lm') || remoteLibrary.includes('runComposer') || remoteLibrary.includes('--allow-model-call'));

must('library-ui-local-source-still-explicit', libraryUi.includes('Add a project from this computer'));
must('library-ui-remote-source-explicit', libraryUi.includes('Add or refresh a project from Personal Wiki'));
must('library-ui-remote-only-when-connected', libraryUi.includes("...(remoteConnected ? [{"));
must('library-ui-remote-action-delegates', libraryUi.includes("action === 'remote-register'") && libraryUi.includes('remoteLibrary.addRemoteProject'));

const sshBoundary = `${remoteMemory}\n${remoteAttach}\n${remoteLibrary}\n${snapshotTransfer}`;
must('ssh-batch-mode', sshBoundary.includes('BatchMode=yes'));
mustNot('ssh-never-disables-host-key-checking', sshBoundary.includes('StrictHostKeyChecking=no'));
mustNot('ssh-never-null-known-hosts', sshBoundary.includes('UserKnownHostsFile=/dev/null'));
mustNot('no-background-sync-loop', sshBoundary.includes('setInterval(') || sshBoundary.includes('setTimeout(async') || sshBoundary.includes('watchFile('));

console.log('REMOTE-STATIC PASS explicit-attach=yes writerLockedAttach=yes remote-library=verified-named-readonly offline-write=blocked extensionKind=workspace symlinkFailClosed=yes');
