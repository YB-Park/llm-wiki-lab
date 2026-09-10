'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');
const library = require('./personal-wiki-library');
const memoryRead = require('./memory-read-service');
const remoteAttach = require('./remote-attach');
const remoteMemory = require('./remote-memory');
const remotePolicy = require('./remote-project-policy');
const snapshotTransfer = require('./remote-snapshot-transfer');

function remoteCacheRoot(context, target, storeId) {
  if (!remoteMemory.TARGET_RE.test(String(target || ''))) throw new Error('remote_ssh_target_invalid');
  if (!remoteMemory.STORE_ID_RE.test(String(storeId || ''))) throw new Error('remote_store_id_invalid');
  const base = context.globalStorageUri && context.globalStorageUri.fsPath;
  if (!base || !path.isAbsolute(base)) throw new Error('remote_library_global_storage_unavailable');
  return path.join(base, 'remote-library', remotePolicy.authorityCacheKey(target), String(storeId), 'wiki');
}

async function fetchRemoteStoreSnapshot(context, folder, target, storeId) {
  await remoteMemory.health(context, folder, target, { deploy: true });
  const root = remoteCacheRoot(context, target, storeId);
  const parent = path.dirname(root);
  fs.mkdirSync(parent, { recursive: true, mode: 0o700 });
  try { fs.chmodSync(parent, 0o700); } catch (_) {}
  const snapshotId = await snapshotTransfer.fetchSnapshot(
    context,
    folder,
    target,
    storeId,
    root,
    { attachEmpty: false }
  );
  return { root, snapshotId };
}

function remoteStoreItems(stores) {
  return remoteAttach.storeQuickPickItems(stores).map((item) => ({
    ...item,
    description: 'Personal Wiki · read-only copy',
    detail: item.detail.includes('Same display name')
      ? item.detail
      : 'Download a verified local read-only copy, then register it under the existing named-project access boundary.',
  }));
}

async function addRemoteProject(context, folder, options = {}) {
  const binding = remoteMemory.binding(context, folder);
  if (!binding) throw new Error('remote_memory_not_connected');
  const stores = (await remoteAttach.listStoresAtTarget(context, folder, binding.target, { deploy: true }))
    .filter((store) => store.storeId !== binding.storeId);
  if (!stores.length) throw new Error('remote_library_no_other_projects');

  let selected;
  const requestedStoreId = String(options.storeId || '').trim();
  if (requestedStoreId) {
    selected = stores.find((store) => store.storeId === requestedStoreId);
    if (!selected) throw new Error('remote_library_store_not_found');
  } else {
    const picked = await vscode.window.showQuickPick(remoteStoreItems(stores), {
      title: 'LLM Wiki: Add Personal Wiki Project',
      placeHolder: 'Choose one exact remote project to cache and register read-only',
      ignoreFocusOut: true,
      matchOnDescription: true,
      matchOnDetail: true,
    });
    if (!picked) return undefined;
    selected = picked.store;
  }

  let approved = options.confirmed === true;
  if (!approved && context.extensionMode !== vscode.ExtensionMode.Test) {
    const choice = await vscode.window.showWarningMessage(
      `Add “${selected.displayName}” as read-only project memory?`,
      {
        modal: true,
        detail: 'LLM Wiki will fetch one verified snapshot from your Personal Wiki into private host-local extension storage, then register that exact cached project under the existing named-project boundary. It will not write to the other project, search all projects automatically, or expose the SSH target to the model.',
      },
      'Add Read-only Project'
    );
    approved = choice === 'Add Read-only Project';
  }
  if (!approved && context.extensionMode !== vscode.ExtensionMode.Test) return undefined;

  const cached = await fetchRemoteStoreSnapshot(context, folder, binding.target, selected.storeId);
  const row = await library.registerStore(context, {
    root: cached.root,
    currentRoot: memoryRead.wikiRoot(folder),
    displayName: selected.displayName,
    aliases: [],
  });

  const currentRoot = memoryRead.wikiRoot(folder);
  if (!library.libraryGrant(context, folder, currentRoot) && context.extensionMode !== vscode.ExtensionMode.Test) {
    const access = await vscode.window.showInformationMessage(
      `Added “${row.displayName}”. Allow this workspace to consult explicitly named added projects?`,
      'Allow Here',
      'Not Now'
    );
    if (access === 'Allow Here') await library.setLibraryAccess(context, folder, currentRoot, true);
  }
  return { ...row, remoteStoreId: selected.storeId, snapshotId: cached.snapshotId };
}

module.exports = {
  addRemoteProject,
  fetchRemoteStoreSnapshot,
  remoteCacheRoot,
  remoteStoreItems,
};