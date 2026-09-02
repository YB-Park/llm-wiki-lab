'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const vscode = require('vscode');
const library = require('./personal-wiki-library');
const memoryRead = require('./memory-read-service');
const remoteAttach = require('./remote-attach');
const remoteMemory = require('./remote-memory');
const remotePolicy = require('./remote-project-policy');
const { boundedProcessFailure } = require('./process-errors');
const { resolvePythonRuntime } = require('./python-runtime');

const MAX_BUFFER = 4 * 1024 * 1024;
const TIMEOUT_MS = 60000;

function coreRoot(context, folder) {
  const configured = String(vscode.workspace.getConfiguration('llmWiki').get('corePath', '') || '').trim();
  if (configured) return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'remote_snapshot.py'))) return bundled;
  return path.resolve(context.extensionPath, '..', '..');
}

function pythonEnv(core) {
  const pythonPath = process.env.PYTHONPATH ? `${core}${path.delimiter}${process.env.PYTHONPATH}` : core;
  return { ...process.env, PYTHONPATH: pythonPath };
}

function remoteCacheRoot(context, target, storeId) {
  if (!remoteMemory.TARGET_RE.test(String(target || ''))) throw new Error('remote_ssh_target_invalid');
  if (!remoteMemory.STORE_ID_RE.test(String(storeId || ''))) throw new Error('remote_store_id_invalid');
  const base = context.globalStorageUri && context.globalStorageUri.fsPath;
  if (!base || !path.isAbsolute(base)) throw new Error('remote_library_global_storage_unavailable');
  return path.join(base, 'remote-library', remotePolicy.authorityCacheKey(target), String(storeId), 'wiki');
}

function waitProcess(child, { captureStdout = true } = {}) {
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
      reject(new Error('remote_process_timeout'));
    }, TIMEOUT_MS);
    if (captureStdout) {
      child.stdout.on('data', (chunk) => {
        stdoutBytes += chunk.length;
        if (stdoutBytes > MAX_BUFFER) {
          if (!settled) {
            settled = true;
            clearTimeout(timer);
            try { child.kill('SIGKILL'); } catch (_) {}
            reject(new Error('remote_process_stdout_too_large'));
          }
          return;
        }
        stdout.push(Buffer.from(chunk));
      });
    }
    child.stderr.on('data', (chunk) => {
      stderrBytes += chunk.length;
      if (stderrBytes <= MAX_BUFFER) stderr.push(Buffer.from(chunk));
    });
    child.on('error', (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(error);
    });
    child.on('close', (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({ code, stdout: Buffer.concat(stdout), stderr: Buffer.concat(stderr) });
    });
  });
}

async function fetchRemoteStoreSnapshot(context, folder, target, storeId) {
  await remoteMemory.health(context, folder, target, { deploy: true });
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const core = coreRoot(context, folder);
  const root = remoteCacheRoot(context, target, storeId);
  fs.mkdirSync(path.dirname(root), { recursive: true, mode: 0o700 });

  const ssh = spawn('ssh', remoteMemory.sshArgs(target, remoteMemory.HELPER_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdin.end(`${JSON.stringify({ protocol: remoteMemory.PROTOCOL, op: 'snapshot_export', store_id: storeId })}\n`, 'utf8');

  const importer = spawn(runtime.executable, [
    '-m', 'dogfood.llm_wiki.remote_snapshot', 'import',
    '--root', root,
    '--replace-host-local',
  ], {
    cwd: folder.uri.fsPath,
    env: pythonEnv(core),
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdout.pipe(importer.stdin);

  const [sshResult, importResult] = await Promise.all([
    waitProcess(ssh, { captureStdout: false }),
    waitProcess(importer, { captureStdout: true }),
  ]);
  if (sshResult.code !== 0) {
    throw new Error(`remote_snapshot_fetch_failed:${boundedProcessFailure(sshResult.stderr.toString('utf8'))}`);
  }
  if (importResult.code !== 0) {
    throw new Error(`remote_snapshot_verify_failed:${boundedProcessFailure(importResult.stderr.toString('utf8'))}`);
  }
  let imported;
  try { imported = JSON.parse(importResult.stdout.toString('utf8')); } catch (_) {
    throw new Error('remote_snapshot_import_response_invalid');
  }
  if (!imported || imported.status !== 'IMPORTED' || !remoteMemory.SNAPSHOT_ID_RE.test(String(imported.snapshot_id || ''))) {
    throw new Error('remote_snapshot_import_response_invalid');
  }
  return { root, snapshotId: String(imported.snapshot_id) };
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
