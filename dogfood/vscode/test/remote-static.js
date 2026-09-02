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

must('attach-explicit-existing-choice', remoteAttach.includes('Use Existing Project Memory'));
must('attach-explicit-new-choice', remoteAttach.includes('Create New Project Memory'));
must('attach-no-identity-inference', remoteAttach.includes('No repository, path, branch, file-content similarity, or folder name is used to choose project identity.'));
must('attach-no-merge', remoteAttach.includes('This is an explicit attach, not a merge.'));
assert.ok((remoteAttach.match(/assertFreshLocalMemory\(root\)/g) || []).length >= 2, 'REMOTE-STATIC attach-rechecks-local-empty');
must('attach-exact-store-id', remoteAttach.includes("stores.find((store) => store.storeId === requestedStoreId)"));
must('attach-only-bootstrapped-store', remoteAttach.includes('store.bootstrap_complete === true'));
must('attach-materializes-via-verified-refresh', remoteAttach.includes('remoteMemory.refreshReplica(context, folder)'));
must('attach-rolls-back-binding-on-failure', remoteAttach.includes('context.workspaceState.update(key, undefined)'));
mustNot('attach-no-repo-discovery', remoteAttach.includes('git remote') || remoteAttach.includes('repositoryUrl'));

must('fresh-policy-only-baseline-files', remotePolicy.includes("'config.json'") && remotePolicy.includes("'manifest.jsonl'") && remotePolicy.includes("'raw'") && remotePolicy.includes("'workspace-opt-in.json'"));
must('fresh-policy-manifest-empty', remotePolicy.includes('manifestStat.size !== 0'));
must('fresh-policy-raw-empty', remotePolicy.includes('fs.readdirSync(raw).length !== 0'));
must('fresh-policy-extra-portable-fails', remotePolicy.includes('!FRESH_LOCAL_ENTRIES.has(name)'));
must('fresh-policy-symlink-failclosed', remotePolicy.includes('stat.isSymbolicLink()'));
must('fresh-policy-opt-in-required-local', remotePolicy.includes("safeLstat(optIn, 'file')"));

must('remote-library-host-local-global-storage', remoteLibrary.includes('context.globalStorageUri'));
must('remote-library-target-path-hashed', remoteLibrary.includes('remotePolicy.authorityCacheKey(target)'));
mustNot('remote-library-no-raw-target-in-cache-path', remoteLibrary.includes("path.join(base, 'remote-library', target"));
must('remote-library-excludes-current-store', remoteLibrary.includes('store.storeId !== binding.storeId'));
must('remote-library-verified-snapshot-import', remoteLibrary.includes("'dogfood.llm_wiki.remote_snapshot', 'import'") && remoteLibrary.includes("'--replace-host-local'"));
must('remote-library-reuses-existing-federation', remoteLibrary.includes('library.registerStore(context'));
must('remote-library-separate-workspace-grant', remoteLibrary.includes('library.setLibraryAccess(context, folder, currentRoot, true)'));
must('remote-library-explicit-readonly-disclosure', remoteLibrary.includes('Add Read-only Project'));
mustNot('remote-library-no-model-call', remoteLibrary.includes('vscode.lm') || remoteLibrary.includes('runComposer') || remoteLibrary.includes('--allow-model-call'));

must('library-ui-local-source-still-explicit', libraryUi.includes('Add a project from this computer'));
must('library-ui-remote-source-explicit', libraryUi.includes('Add or refresh a project from Personal Wiki'));
must('library-ui-remote-only-when-connected', libraryUi.includes("...(remoteConnected ? [{"));
must('library-ui-remote-action-delegates', libraryUi.includes("action === 'remote-register'") && libraryUi.includes('remoteLibrary.addRemoteProject'));

const sshBoundary = `${remoteMemory}\n${remoteAttach}\n${remoteLibrary}`;
must('ssh-batch-mode', sshBoundary.includes('BatchMode=yes'));
mustNot('ssh-never-disables-host-key-checking', sshBoundary.includes('StrictHostKeyChecking=no'));
mustNot('ssh-never-null-known-hosts', sshBoundary.includes('UserKnownHostsFile=/dev/null'));
mustNot('no-background-sync-loop', sshBoundary.includes('setInterval(') || sshBoundary.includes('setTimeout(async') || sshBoundary.includes('watchFile('));

console.log('REMOTE-STATIC PASS explicit-attach=yes remote-library=verified-named-readonly offline-write=blocked extensionKind=workspace symlinkFailClosed=yes');
