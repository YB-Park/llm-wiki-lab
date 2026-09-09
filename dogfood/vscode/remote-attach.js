'use strict';

const vscode = require('vscode');
const memoryRead = require('./memory-read-service');
const remoteMemory = require('./remote-memory');
const remotePolicy = require('./remote-project-policy');
const snapshotTransfer = require('./remote-snapshot-transfer');

const BINDING_KEY_PREFIX = 'llmWiki.remoteBinding.v1';
const MAX_BUFFER = 4 * 1024 * 1024;
const TIMEOUT_MS = 15000;

function bindingKey(folder) {
  return `${BINDING_KEY_PREFIX}:${folder.uri.toString()}`;
}

function promptTarget() {
  return vscode.window.showInputBox({
    title: 'LLM Wiki: Personal Wiki',
    prompt: 'SSH host alias or user@host. Uses your existing non-interactive OpenSSH config, keys, agent, proxy/jump, and known-hosts policy.',
    placeHolder: 'personal-wiki-host',
    ignoreFocusOut: true,
    validateInput: (value) => remoteMemory.TARGET_RE.test(String(value || '').trim())
      ? undefined
      : 'Enter one non-interactive SSH target without spaces.',
  });
}

async function authorityJsonAtTarget(context, folder, target, request) {
  return remoteMemory.authorityJson(context, folder, target, request);
}

async function chooseAuthorityTarget(title) {
  const picked = await vscode.window.showQuickPick([
    {
      label: 'This PC',
      description: 'Use this Linux workspace host as the Personal Wiki authority',
      detail: 'No SSH to this PC is required. LLM Wiki uses the same private authority catalog directly on this host.',
      mode: 'local',
    },
    {
      label: 'SSH Host',
      description: 'Use another Linux host as the Personal Wiki authority',
      detail: 'Uses your existing non-interactive OpenSSH config, keys, agent, proxy/jump, and known-hosts policy.',
      mode: 'ssh',
    },
  ], {
    title,
    placeHolder: 'Where is your Personal Wiki authority?',
    ignoreFocusOut: true,
  });
  if (!picked) return undefined;
  if (picked.mode === 'local') return remoteMemory.LOCAL_AUTHORITY_TARGET;
  return String(await promptTarget() || '').trim() || undefined;
}

async function listStoresAtTarget(context, folder, target, { deploy = true } = {}) {
  await remoteMemory.health(context, folder, target, { deploy });
  const row = await authorityJsonAtTarget(context, folder, target, { op: 'list_stores' });
  return (Array.isArray(row.stores) ? row.stores : [])
    .filter((store) => remoteMemory.STORE_ID_RE.test(String(store.store_id || '')) && store.bootstrap_complete === true)
    .map((store) => ({
      storeId: String(store.store_id),
      displayName: String(store.display_name || 'Project Memory').trim().slice(0, 120) || 'Project Memory',
    }));
}

function storeQuickPickItems(stores) {
  const ordered = [...stores].sort((a, b) => (
    a.displayName.localeCompare(b.displayName) || a.storeId.localeCompare(b.storeId)
  ));
  const totals = new Map();
  for (const store of ordered) totals.set(store.displayName, (totals.get(store.displayName) || 0) + 1);
  const seen = new Map();
  return ordered.map((store) => {
    const index = (seen.get(store.displayName) || 0) + 1;
    seen.set(store.displayName, index);
    const duplicate = totals.get(store.displayName) > 1;
    return {
      label: duplicate ? `${store.displayName} (${index})` : store.displayName,
      description: 'Existing Personal Wiki project',
      detail: duplicate ? 'Same display name; choose the exact project instance you intend to use.' : 'Attach this PC to this exact remote project memory.',
      store,
    };
  });
}

async function attachExisting(context, folder, options = {}) {
  if (process.platform !== 'linux') throw new Error('remote_s1_linux_workspace_host_required');
  if (remoteMemory.isConfigured(context, folder)) throw new Error('remote_memory_already_connected');
  const root = memoryRead.wikiRoot(folder);
  remotePolicy.assertFreshLocalMemory(root);

  let target = String(options.target || '').trim();
  if (!target) target = String(await chooseAuthorityTarget('LLM Wiki: Use Existing Personal Wiki Project Memory') || '').trim();
  if (!target) return undefined;
  if (!remoteMemory.TARGET_RE.test(target)) throw new Error('remote_ssh_target_invalid');

  const stores = await listStoresAtTarget(context, folder, target, { deploy: true });
  if (!stores.length) throw new Error('remote_attach_no_existing_project_memory');

  let selected;
  const requestedStoreId = String(options.storeId || '').trim();
  if (requestedStoreId) {
    selected = stores.find((store) => store.storeId === requestedStoreId);
    if (!selected) throw new Error('remote_attach_store_not_found');
  } else {
    const picked = await vscode.window.showQuickPick(storeQuickPickItems(stores), {
      title: 'LLM Wiki: Use Existing Personal Wiki Project Memory',
      placeHolder: 'Choose the exact published Project Memory this workspace should continue using',
      ignoreFocusOut: true,
      matchOnDescription: true,
      matchOnDetail: true,
    });
    if (!picked) return undefined;
    selected = picked.store;
  }

  let confirmed = options.confirmed === true;
  if (!confirmed && context.extensionMode !== vscode.ExtensionMode.Test) {
    const choice = await vscode.window.showWarningMessage(
      `Use published Project Memory “${selected.displayName}” in this workspace?`,
      {
        modal: true,
        detail: 'This is an explicit attach, not a merge. This local Project Memory must still be empty. Its fresh workspace opt-in stays local to this PC, while the portable memory is replaced by the verified remote project you selected. No repository, path, branch, file-content similarity, or folder name is used to choose project identity.',
      },
      'Use Existing Project Memory'
    );
    confirmed = choice === 'Use Existing Project Memory';
  }
  if (!confirmed && context.extensionMode !== vscode.ExtensionMode.Test) return undefined;

  // Fast user-facing recheck, followed by the authoritative writer-locked
  // emptiness check inside remote_attach_import immediately before activation.
  remotePolicy.assertFreshLocalMemory(root);
  const snapshotId = await snapshotTransfer.fetchSnapshot(
    context,
    folder,
    target,
    selected.storeId,
    root,
    { attachEmpty: true }
  );

  // Publish the host-local binding only after the selected remote snapshot was
  // fully verified and atomically materialized. A failed attach leaves no binding.
  const key = bindingKey(folder);
  const row = {
    version: 1,
    target,
    storeId: selected.storeId,
    displayName: selected.displayName,
    snapshotId,
    writable: true,
    refreshPending: false,
    lastError: '',
    connectedAt: new Date().toISOString(),
  };
  await context.workspaceState.update(key, row);
  try {
    await remoteMemory.setContexts(context, folder);
  } catch (error) {
    await context.workspaceState.update(key, undefined);
    throw error;
  }
  return remoteMemory.binding(context, folder);
}

async function chooseConnection(context, folder, createNew) {
  if (remoteMemory.isConfigured(context, folder)) return remoteMemory.refreshReplica(context, folder);
  const picked = await vscode.window.showQuickPick([
    {
      label: 'Publish This Project Memory',
      description: 'Make this workspace’s current Project Memory available through Personal Wiki',
      detail: 'Creates one new opaque Personal Wiki project identity from the current local Project Memory.',
      mode: 'publish',
    },
    {
      label: 'Use Existing Personal Wiki Project Memory',
      description: 'Continue one exact Project Memory that was already published',
      detail: 'Available only while this workspace’s local Project Memory is empty. Nothing is inferred or merged automatically.',
      mode: 'existing',
    },
  ], {
    title: 'LLM Wiki: Personal Wiki',
    placeHolder: 'Publish this Project Memory, or continue an existing published one',
    ignoreFocusOut: true,
  });
  if (!picked) return undefined;

  const target = await chooseAuthorityTarget(
    picked.mode === 'publish'
      ? 'LLM Wiki: Publish This Project Memory'
      : 'LLM Wiki: Use Existing Personal Wiki Project Memory'
  );
  if (!target) return undefined;
  return picked.mode === 'existing'
    ? attachExisting(context, folder, { target })
    : createNew(target);
}

module.exports = {
  BINDING_KEY_PREFIX,
  attachExisting,
  authorityJsonAtTarget,
  bindingKey,
  chooseAuthorityTarget,
  chooseConnection,
  listStoresAtTarget,
  storeQuickPickItems,
};