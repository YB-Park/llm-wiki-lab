'use strict';

const { spawn } = require('node:child_process');
const vscode = require('vscode');
const remoteMemory = require('./remote-memory');
const remotePolicy = require('./remote-project-policy');
const { boundedProcessFailure } = require('./process-errors');

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

function sshJsonAtTarget(folder, target, request) {
  if (!remoteMemory.TARGET_RE.test(String(target || ''))) throw new Error('remote_ssh_target_invalid');
  const child = spawn('ssh', remoteMemory.sshArgs(target, remoteMemory.HELPER_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  child.stdin.end(`${JSON.stringify({ protocol: remoteMemory.PROTOCOL, ...request })}\n`, 'utf8');

  return new Promise((resolve, reject) => {
    const stdout = [];
    const stderr = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let settled = false;
    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      try { child.kill('SIGKILL'); } catch (_) {}
      reject(new remoteMemory.RemoteTransportError('remote_process_timeout'));
    }, TIMEOUT_MS);

    child.stdout.on('data', (chunk) => {
      stdoutBytes += chunk.length;
      if (stdoutBytes > MAX_BUFFER) {
        if (!settled) {
          settled = true;
          clearTimeout(timer);
          try { child.kill('SIGKILL'); } catch (_) {}
          reject(new remoteMemory.RemoteTransportError('remote_process_stdout_too_large'));
        }
        return;
      }
      stdout.push(Buffer.from(chunk));
    });
    child.stderr.on('data', (chunk) => {
      stderrBytes += chunk.length;
      if (stderrBytes <= MAX_BUFFER) stderr.push(Buffer.from(chunk));
    });
    child.on('error', (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(new remoteMemory.RemoteTransportError(`remote_process_error:${boundedProcessFailure(error && error.message ? error.message : String(error))}`));
    });
    child.on('close', (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (code !== 0 && !stdoutBytes) {
        reject(new remoteMemory.RemoteTransportError(`remote_ssh_failed:${boundedProcessFailure(Buffer.concat(stderr).toString('utf8'))}`));
        return;
      }
      let row;
      try { row = JSON.parse(Buffer.concat(stdout).toString('utf8')); } catch (_) {
        reject(new remoteMemory.RemoteTransportError('remote_helper_response_invalid'));
        return;
      }
      if (!row || row.ok !== true) {
        reject(new remoteMemory.RemoteOperationError(String((row && row.error) || 'remote_helper_failed'), row));
        return;
      }
      resolve(row);
    });
  });
}

async function listStoresAtTarget(context, folder, target, { deploy = true } = {}) {
  await remoteMemory.health(context, folder, target, { deploy });
  const row = await sshJsonAtTarget(folder, target, { op: 'list_stores' });
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
  const root = remoteMemory.status(context, folder).configured ? undefined : require('./memory-read-service').wikiRoot(folder);
  remotePolicy.assertFreshLocalMemory(root);

  let target = String(options.target || '').trim();
  if (!target) target = String(await promptTarget() || '').trim();
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
      title: 'LLM Wiki: Use Existing Project Memory',
      placeHolder: 'Choose the exact Personal Wiki project this PC should continue using',
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
      `Use “${selected.displayName}” as this workspace's Project Memory?`,
      {
        modal: true,
        detail: 'This is an explicit attach, not a merge. This local Project Memory must still be empty. Its fresh workspace opt-in stays local to this PC, while the portable memory is replaced by the verified remote project you selected. No repository, path, branch, file-content similarity, or folder name is used to choose project identity.',
      },
      'Use Existing Project Memory'
    );
    confirmed = choice === 'Use Existing Project Memory';
  }
  if (!confirmed && context.extensionMode !== vscode.ExtensionMode.Test) return undefined;

  // Re-check immediately before the first local materialization. Any local memory
  // admitted while the picker was open makes attach fail closed rather than merge.
  remotePolicy.assertFreshLocalMemory(root);

  const key = bindingKey(folder);
  const temporary = {
    version: 1,
    target,
    storeId: selected.storeId,
    displayName: selected.displayName,
    snapshotId: '',
    writable: false,
    refreshPending: false,
    lastError: '',
    connectedAt: new Date().toISOString(),
  };
  await context.workspaceState.update(key, temporary);
  await remoteMemory.setContexts(context, folder);
  try {
    return await remoteMemory.refreshReplica(context, folder);
  } catch (error) {
    await context.workspaceState.update(key, undefined);
    await remoteMemory.setContexts(context, folder);
    throw error;
  }
}

async function chooseConnection(context, folder, createNew) {
  if (remoteMemory.isConfigured(context, folder)) return remoteMemory.refreshReplica(context, folder);
  const picked = await vscode.window.showQuickPick([
    {
      label: 'Create New Project Memory',
      description: 'New independent Personal Wiki project',
      detail: 'Publish this workspace’s current Project Memory as a new remote project identity.',
      mode: 'new',
    },
    {
      label: 'Use Existing Project Memory',
      description: 'Continue one exact Personal Wiki project',
      detail: 'Available only while local Project Memory is empty. Nothing is inferred or merged automatically.',
      mode: 'existing',
    },
  ], {
    title: 'LLM Wiki: Connect Personal Wiki',
    placeHolder: 'Choose how this workspace should connect',
    ignoreFocusOut: true,
  });
  if (!picked) return undefined;
  return picked.mode === 'existing' ? attachExisting(context, folder) : createNew();
}

module.exports = {
  BINDING_KEY_PREFIX,
  attachExisting,
  bindingKey,
  chooseConnection,
  listStoresAtTarget,
  sshJsonAtTarget,
  storeQuickPickItems,
};
