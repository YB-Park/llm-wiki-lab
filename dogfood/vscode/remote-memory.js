'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const vscode = require('vscode');
const { resolvePythonRuntime } = require('./python-runtime');
const { boundedProcessFailure } = require('./process-errors');

const PROTOCOL = 'LLM-WIKI-REMOTE-HELPER-v1';
const BINDING_KEY_PREFIX = 'llmWiki.remoteBinding.v1';
const REMOTE_CONFIGURED_CONTEXT = 'llmWiki.remoteConfigured';
const REMOTE_WRITABLE_CONTEXT = 'llmWiki.remoteWritable';
const REPLICA_READ_MODULE = 'dogfood.llm_wiki.replica_read_cli';
const MAX_CONTROL_BUFFER = 16 * 1024 * 1024;
const SSH_TIMEOUT_MS = 15000;
const STORE_ID_RE = /^project-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SNAPSHOT_ID_RE = /^[0-9a-f]{64}$/;
const TARGET_RE = /^[^\s\x00-\x1f\x7f]{1,255}$/;

const INSTALL_COMMAND = 'set -eu; umask 077; root="${XDG_DATA_HOME:-$HOME/.local/share}/llm-wiki/remote-runtime/current"; mkdir -p "$root"; rm -rf "$root/dogfood"; tar -xf - -C "$root"';
const HELPER_COMMAND = 'set -eu; root="${XDG_DATA_HOME:-$HOME/.local/share}/llm-wiki/remote-runtime/current"; PYTHONPATH="$root" python3 -m dogfood.llm_wiki.remote_helper';

class RemoteTransportError extends Error {
  constructor(message) {
    super(message);
    this.name = 'RemoteTransportError';
  }
}

class RemoteOperationError extends Error {
  constructor(message, response = undefined) {
    super(message);
    this.name = 'RemoteOperationError';
    this.response = response;
  }
}

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
}

function wikiRoot(folder) {
  const value = String(configuration().get('workspaceDirectory', '.wiki-lab') || '.wiki-lab');
  return path.isAbsolute(value) ? value : path.resolve(folder.uri.fsPath, value);
}

function coreRoot(context, folder) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'remote_helper.py'))) return bundled;
  return path.resolve(context.extensionPath, '..', '..');
}

function bindingKey(folder) {
  return `${BINDING_KEY_PREFIX}:${folder.uri.toString()}`;
}

function validateBinding(raw) {
  if (!raw) return undefined;
  if (
    raw.version !== 1
    || typeof raw.target !== 'string'
    || !TARGET_RE.test(raw.target)
    || typeof raw.storeId !== 'string'
    || !STORE_ID_RE.test(raw.storeId)
    || typeof raw.displayName !== 'string'
  ) {
    throw new Error('remote_binding_corrupt');
  }
  return {
    version: 1,
    target: raw.target,
    storeId: raw.storeId,
    displayName: raw.displayName,
    snapshotId: String(raw.snapshotId || ''),
    writable: raw.writable === true,
    refreshPending: raw.refreshPending === true,
    lastError: String(raw.lastError || ''),
    connectedAt: String(raw.connectedAt || ''),
  };
}

function binding(context, folder) {
  return validateBinding(context.workspaceState.get(bindingKey(folder)));
}

function isConfigured(context, folder) {
  return Boolean(binding(context, folder));
}

async function saveBinding(context, folder, row) {
  const normalized = validateBinding(row);
  await context.workspaceState.update(bindingKey(folder), normalized);
  await vscode.commands.executeCommand('setContext', REMOTE_CONFIGURED_CONTEXT, Boolean(normalized));
  await vscode.commands.executeCommand('setContext', REMOTE_WRITABLE_CONTEXT, Boolean(normalized && normalized.writable && !normalized.refreshPending));
  return normalized;
}

async function setContexts(context, folder) {
  let row;
  try { row = binding(context, folder); } catch (_) { row = undefined; }
  await vscode.commands.executeCommand('setContext', REMOTE_CONFIGURED_CONTEXT, Boolean(row));
  await vscode.commands.executeCommand('setContext', REMOTE_WRITABLE_CONTEXT, Boolean(row && row.writable && !row.refreshPending));
}

function sshArgs(target, command) {
  if (!TARGET_RE.test(String(target || ''))) throw new Error('remote_ssh_target_invalid');
  return ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', '-T', target, command];
}

function processResult(child, { timeoutMs = SSH_TIMEOUT_MS, maxBuffer = MAX_CONTROL_BUFFER } = {}) {
  return new Promise((resolve, reject) => {
    const stdout = [];
    const stderr = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let settled = false;
    const timer = setTimeout(() => {
      if (settled) return;
      try { child.kill('SIGKILL'); } catch (_) {}
      settled = true;
      reject(new RemoteTransportError('remote_process_timeout'));
    }, timeoutMs);

    child.stdout.on('data', (chunk) => {
      stdoutBytes += chunk.length;
      if (stdoutBytes > maxBuffer) {
        try { child.kill('SIGKILL'); } catch (_) {}
        if (!settled) {
          settled = true;
          clearTimeout(timer);
          reject(new RemoteTransportError('remote_process_stdout_too_large'));
        }
        return;
      }
      stdout.push(Buffer.from(chunk));
    });
    child.stderr.on('data', (chunk) => {
      stderrBytes += chunk.length;
      if (stderrBytes <= maxBuffer) stderr.push(Buffer.from(chunk));
    });
    child.on('error', (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(new RemoteTransportError(`remote_process_error:${boundedProcessFailure(error && error.message ? error.message : String(error))}`));
    });
    child.on('close', (code, signal) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({ code, signal, stdout: Buffer.concat(stdout), stderr: Buffer.concat(stderr) });
    });
  });
}

function pythonEnv(core) {
  const pythonPath = process.env.PYTHONPATH ? `${core}${path.delimiter}${process.env.PYTHONPATH}` : core;
  return { ...process.env, PYTHONPATH: pythonPath };
}

async function deployRuntime(context, folder, target) {
  if (process.platform !== 'linux') throw new Error('remote_s1_linux_workspace_host_required');
  const core = coreRoot(context, folder);
  for (const required of [
    'dogfood/__init__.py',
    'dogfood/llm_wiki/remote_helper.py',
    'dogfood/llm_wiki/remote_snapshot.py',
    'dogfood/llm_wiki/replica_read_cli.py',
  ]) {
    if (!fs.existsSync(path.join(core, required))) throw new Error(`remote_runtime_missing:${required}`);
  }

  const archive = spawn('tar', ['-C', core, '-cf', '-', 'dogfood/__init__.py', 'dogfood/llm_wiki'], {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  const ssh = spawn('ssh', sshArgs(target, INSTALL_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  archive.stdout.pipe(ssh.stdin);
  const [archiveResult, sshResult] = await Promise.all([
    processResult(archive, { timeoutMs: 30000, maxBuffer: 1024 * 1024 }),
    processResult(ssh, { timeoutMs: 30000, maxBuffer: 1024 * 1024 }),
  ]);
  if (archiveResult.code !== 0) throw new RemoteTransportError(`remote_runtime_archive_failed:${boundedProcessFailure(archiveResult.stderr.toString('utf8'))}`);
  if (sshResult.code !== 0) throw new RemoteTransportError(`remote_runtime_install_failed:${boundedProcessFailure(sshResult.stderr.toString('utf8'))}`);
}

async function sshJson(folder, target, request, payload = Buffer.alloc(0)) {
  const ssh = spawn('ssh', sshArgs(target, HELPER_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdin.write(`${JSON.stringify({ protocol: PROTOCOL, ...request })}\n`, 'utf8');
  if (payload.length) ssh.stdin.write(payload);
  ssh.stdin.end();
  const result = await processResult(ssh);
  if (result.code !== 0 && !result.stdout.length) {
    throw new RemoteTransportError(`remote_ssh_failed:${boundedProcessFailure(result.stderr.toString('utf8'))}`);
  }
  let row;
  try {
    row = JSON.parse(result.stdout.toString('utf8'));
  } catch (_) {
    throw new RemoteTransportError(`remote_helper_response_invalid:${boundedProcessFailure(result.stderr.toString('utf8'))}`);
  }
  if (!row || row.ok !== true) {
    throw new RemoteOperationError(String((row && row.error) || 'remote_helper_failed'), row);
  }
  return row;
}

async function health(context, folder, target, { deploy = false } = {}) {
  if (deploy) await deployRuntime(context, folder, target);
  const row = await sshJson(folder, target, { op: 'health' });
  if (row.protocol !== PROTOCOL || !String(row.platform || '').startsWith('linux')) {
    throw new RemoteOperationError('remote_helper_incompatible', row);
  }
  return row;
}

async function localSnapshotExportProcess(context, folder) {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const core = coreRoot(context, folder);
  return spawn(runtime.executable, ['-m', 'dogfood.llm_wiki.remote_snapshot', 'export', '--root', wikiRoot(folder)], {
    cwd: folder.uri.fsPath,
    env: pythonEnv(core),
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

async function bootstrapStore(context, folder, target, storeId) {
  const exporter = await localSnapshotExportProcess(context, folder);
  const ssh = spawn('ssh', sshArgs(target, HELPER_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdin.write(`${JSON.stringify({ protocol: PROTOCOL, op: 'bootstrap_store', store_id: storeId })}\n`, 'utf8');
  exporter.stdout.pipe(ssh.stdin);
  const [exportResult, sshResult] = await Promise.all([
    processResult(exporter, { timeoutMs: 60000, maxBuffer: 1024 * 1024 }),
    processResult(ssh, { timeoutMs: 60000, maxBuffer: MAX_CONTROL_BUFFER }),
  ]);
  if (exportResult.code !== 0) throw new RemoteOperationError(`remote_local_snapshot_export_failed:${boundedProcessFailure(exportResult.stderr.toString('utf8'))}`);
  if (sshResult.code !== 0 && !sshResult.stdout.length) throw new RemoteTransportError(`remote_bootstrap_transport_failed:${boundedProcessFailure(sshResult.stderr.toString('utf8'))}`);
  let row;
  try { row = JSON.parse(sshResult.stdout.toString('utf8')); } catch (_) { throw new RemoteTransportError('remote_bootstrap_response_invalid'); }
  if (!row || row.ok !== true) throw new RemoteOperationError(String((row && row.error) || 'remote_bootstrap_failed'), row);
  return row;
}

async function refreshReplicaWithBinding(context, folder, row) {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const core = coreRoot(context, folder);
  const ssh = spawn('ssh', sshArgs(row.target, HELPER_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdin.end(`${JSON.stringify({ protocol: PROTOCOL, op: 'snapshot_export', store_id: row.storeId })}\n`, 'utf8');

  const importer = spawn(runtime.executable, ['-m', 'dogfood.llm_wiki.remote_snapshot', 'import', '--root', wikiRoot(folder)], {
    cwd: folder.uri.fsPath,
    env: pythonEnv(core),
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdout.pipe(importer.stdin);
  const [sshResult, importResult] = await Promise.all([
    processResult(ssh, { timeoutMs: 60000, maxBuffer: 1024 * 1024 }),
    processResult(importer, { timeoutMs: 60000, maxBuffer: 1024 * 1024 }),
  ]);
  if (sshResult.code !== 0) throw new RemoteTransportError(`remote_snapshot_fetch_failed:${boundedProcessFailure(sshResult.stderr.toString('utf8'))}`);
  if (importResult.code !== 0) throw new RemoteOperationError(`remote_snapshot_verify_failed:${boundedProcessFailure(importResult.stderr.toString('utf8'))}`);
  let imported;
  try { imported = JSON.parse(importResult.stdout.toString('utf8')); } catch (_) { throw new RemoteOperationError('remote_snapshot_import_response_invalid'); }
  if (!imported || imported.status !== 'IMPORTED' || !SNAPSHOT_ID_RE.test(String(imported.snapshot_id || ''))) {
    throw new RemoteOperationError('remote_snapshot_import_response_invalid');
  }
  return String(imported.snapshot_id);
}

async function refreshReplica(context, folder) {
  const current = binding(context, folder);
  if (!current) throw new Error('remote_memory_not_connected');
  try {
    const snapshotId = await refreshReplicaWithBinding(context, folder, current);
    return saveBinding(context, folder, { ...current, snapshotId, writable: true, refreshPending: false, lastError: '' });
  } catch (error) {
    const detail = error && error.message ? error.message : String(error);
    await saveBinding(context, folder, { ...current, writable: false, refreshPending: current.refreshPending, lastError: detail.slice(0, 300) });
    throw error;
  }
}

async function connect(context, folder, options = {}) {
  if (process.platform !== 'linux') throw new Error('remote_s1_linux_workspace_host_required');
  const root = wikiRoot(folder);
  if (!fs.existsSync(path.join(root, 'config.json')) || !fs.existsSync(path.join(root, 'manifest.jsonl'))) {
    throw new Error('remote_requires_initialized_project_memory');
  }

  const current = binding(context, folder);
  let target = String(options.target || (current && current.target) || '').trim();
  if (!target) {
    target = String(await vscode.window.showInputBox({
      title: 'LLM Wiki: Connect Personal Wiki',
      prompt: 'SSH host alias or user@host. Uses your existing non-interactive OpenSSH config/keys/agent.',
      placeHolder: 'personal-wiki-host',
      ignoreFocusOut: true,
      validateInput: (value) => TARGET_RE.test(String(value || '').trim()) ? undefined : 'Enter one non-interactive SSH target without spaces.',
    }) || '').trim();
  }
  if (!target) return undefined;
  if (!TARGET_RE.test(target)) throw new Error('remote_ssh_target_invalid');
  if (current && current.target !== target) throw new Error('remote_binding_target_change_requires_explicit_migration');

  await health(context, folder, target, { deploy: true });
  if (current) return refreshReplica(context, folder);

  const displayName = String(options.displayName || folder.name || 'Project Memory').trim().slice(0, 120) || 'Project Memory';
  const created = await sshJson(folder, target, { op: 'create_store', display_name: displayName, bootstrap: true });
  const storeId = String(created.store && created.store.store_id || '');
  if (!STORE_ID_RE.test(storeId)) throw new RemoteOperationError('remote_store_create_response_invalid', created);
  const bootstrap = await bootstrapStore(context, folder, target, storeId);
  const temporary = {
    version: 1,
    target,
    storeId,
    displayName,
    snapshotId: String(bootstrap.snapshot_id || ''),
    writable: true,
    refreshPending: false,
    lastError: '',
    connectedAt: new Date().toISOString(),
  };
  const snapshotId = await refreshReplicaWithBinding(context, folder, temporary);
  return saveBinding(context, folder, { ...temporary, snapshotId });
}

function mutationKind(moduleName, args) {
  if (!Array.isArray(args) || !args.length) return '';
  const command = String(args[0]);
  if (moduleName === 'dogfood.llm_wiki.cli') {
    if (command === 'init' || command === 'ingest' || command === 'feedback') return command;
    if (command === 'topic' && args[1] === 'add') return 'topic-add';
    if (command === 'source' && ['supersede', 'correct', 'change', 'dispute'].includes(args[1])) return `source-${args[1]}`;
    return '';
  }
  if (moduleName === 'dogfood.llm_wiki.agent_state_cli') {
    if (['locator-set', 'pending-add', 'pending-resolve', 'usage-reserve'].includes(command)) return `agent-state-${command}`;
    return '';
  }
  if (moduleName === 'dogfood.llm_wiki.agent_wiki_cli' && command === 'build') return 'agent-wiki-build';
  return '';
}

function replicaArgsForInvocation(moduleName, args) {
  if (!Array.isArray(args) || !args.length) return undefined;
  const command = String(args[0]);
  if (moduleName === 'dogfood.llm_wiki.cli') {
    if (command === 'integrity' || command === 'discover' || command === 'history') return [...args];
    if (command === 'search') return [...args];
    if (command === 'topic' && args[1] === 'list') return ['topic-list', ...args.slice(2)];
    if (command === 'source' && args[1] === 'list') return ['source-list', ...args.slice(2)];
    if (command === 'source' && args[1] === 'status') return ['source-status', ...args.slice(2)];
    if (command === 'source' && args[1] === 'show') return ['source-show', ...args.slice(2)];
    return undefined;
  }
  if (moduleName === 'dogfood.llm_wiki.agent_state_cli') {
    if (command === 'locator-list' || command === 'pending-list' || command === 'usage-status') return [...args];
    return undefined;
  }
  if (moduleName === 'dogfood.llm_wiki.agent_memory_cli') {
    if (command === 'read' || command === 'relevant' || command === 'compare') return [...args];
    return undefined;
  }
  if (moduleName === 'dogfood.llm_wiki.agent_wiki_cli') {
    if (command === 'search') return ['agent-wiki-search', ...args.slice(1)];
    if (command === 'show') return ['agent-wiki-show', ...args.slice(1)];
    return undefined;
  }
  return undefined;
}

function isReplicaReadInvocation(moduleName, args) {
  return Boolean(replicaArgsForInvocation(moduleName, args));
}

// Compatibility name retained for existing Agent tool dispatch. In remote mode
// every classified core invocation must cross this adapter: mutations go to the
// exact remote store; reads go only to the last verified immutable replica.
function isMutatingCoreInvocation(moduleName, args) {
  return Boolean(mutationKind(moduleName, args) || replicaArgsForInvocation(moduleName, args));
}

async function runCoreRead(context, folder, moduleName, args) {
  const current = binding(context, folder);
  if (!current) throw new Error('remote_memory_not_connected');
  if (!SNAPSHOT_ID_RE.test(current.snapshotId)) throw new Error('REMOTE_REPLICA_UNVERIFIED: no verified snapshot is available');
  const replicaArgs = replicaArgsForInvocation(moduleName, args);
  if (!replicaArgs) throw new Error('REMOTE_READ_OPERATION_NOT_CLASSIFIED');
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const core = coreRoot(context, folder);
  const child = spawn(runtime.executable, [
    '-m', REPLICA_READ_MODULE,
    '--root', wikiRoot(folder),
    '--expected-snapshot-id', current.snapshotId,
    ...replicaArgs,
  ], {
    cwd: folder.uri.fsPath,
    env: pythonEnv(core),
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  const result = await processResult(child, { timeoutMs: 30000, maxBuffer: MAX_CONTROL_BUFFER });
  if (result.code !== 0) {
    const detail = boundedProcessFailure(result.stderr.toString('utf8') || result.stdout.toString('utf8') || 'replica_read_failed');
    throw new Error(`REMOTE_REPLICA_READ_FAILED: ${detail}`);
  }
  return result.stdout.toString('utf8');
}

function uploadPayloadForInvocation(moduleName, args) {
  if (moduleName !== 'dogfood.llm_wiki.cli' || args[0] !== 'ingest') return { args: [...args], uploads: [], payload: Buffer.alloc(0) };
  const nextArgs = [...args];
  const uploads = [];
  const payloads = [];
  for (let index = 1; index < nextArgs.length; index += 1) {
    const value = String(nextArgs[index]);
    if (value.startsWith('--')) break;
    const stat = fs.statSync(value);
    if (!stat.isFile()) throw new Error('remote_ingest_requires_regular_file');
    const payload = fs.readFileSync(value);
    const token = `__LLM_WIKI_UPLOAD_${uploads.length}__`;
    uploads.push({
      token,
      name: path.basename(value),
      size: payload.length,
      sha256: crypto.createHash('sha256').update(payload).digest('hex'),
    });
    payloads.push(payload);
    nextArgs[index] = token;
  }
  return { args: nextArgs, uploads, payload: Buffer.concat(payloads) };
}

async function markOffline(context, folder, current, detail, refreshPending = current.refreshPending) {
  await saveBinding(context, folder, {
    ...current,
    writable: false,
    refreshPending,
    lastError: String(detail || 'remote_unavailable').slice(0, 300),
  });
}

async function runCoreMutation(context, folder, moduleName, args) {
  const current = binding(context, folder);
  if (!current) throw new Error('remote_memory_not_connected');
  const kind = mutationKind(moduleName, args);
  if (!kind) {
    if (replicaArgsForInvocation(moduleName, args)) return runCoreRead(context, folder, moduleName, args);
    throw new Error('remote_core_operation_not_classified');
  }
  if (current.refreshPending) {
    try {
      await refreshReplica(context, folder);
    } catch (_) {
      throw new Error('REMOTE_OFFLINE_READ_ONLY: remote state must be re-read before another write');
    }
  }

  const upload = uploadPayloadForInvocation(moduleName, args);
  let response;
  try {
    response = await sshJson(folder, current.target, {
      op: 'run_core',
      store_id: current.storeId,
      module: moduleName,
      args: upload.args,
      uploads: upload.uploads,
    }, upload.payload);
  } catch (error) {
    if (error instanceof RemoteOperationError) throw error;
    const detail = error && error.message ? error.message : String(error);
    await markOffline(context, folder, current, detail);
    throw new Error(`REMOTE_OFFLINE_READ_ONLY: ${boundedProcessFailure(detail)}`);
  }

  const stdout = String(response.stdout || '');
  try {
    await refreshReplica(context, folder);
  } catch (error) {
    const detail = error && error.message ? error.message : String(error);
    await markOffline(context, folder, { ...current, refreshPending: true }, detail, true);
    throw new Error(`REMOTE_WRITE_COMMITTED_REFRESH_PENDING: ${boundedProcessFailure(detail)}`);
  }
  return stdout;
}

async function saveHumanKnowledge(context, folder, input) {
  const current = binding(context, folder);
  if (!current) throw new Error('remote_memory_not_connected');
  if (current.refreshPending) {
    try {
      await refreshReplica(context, folder);
    } catch (_) {
      throw new Error('REMOTE_OFFLINE_READ_ONLY: remote state must be re-read before another write');
    }
  }
  let response;
  try {
    response = await sshJson(folder, current.target, {
      op: 'save_human_knowledge',
      store_id: current.storeId,
      title: input.title,
      statement: input.statement,
      reasoning: input.reasoning,
      source_ids: input.sourceIds,
      supersedes_knowledge_id: input.supersedesKnowledgeId,
    });
  } catch (error) {
    if (error instanceof RemoteOperationError) throw error;
    const detail = error && error.message ? error.message : String(error);
    await markOffline(context, folder, current, detail);
    throw new Error(`REMOTE_OFFLINE_READ_ONLY: ${boundedProcessFailure(detail)}`);
  }
  try {
    await refreshReplica(context, folder);
  } catch (error) {
    const detail = error && error.message ? error.message : String(error);
    await markOffline(context, folder, { ...current, refreshPending: true }, detail, true);
    throw new Error(`REMOTE_WRITE_COMMITTED_REFRESH_PENDING: ${boundedProcessFailure(detail)}`);
  }
  return response.record;
}

async function listStores(context, folder) {
  const current = binding(context, folder);
  if (!current) throw new Error('remote_memory_not_connected');
  return (await sshJson(folder, current.target, { op: 'list_stores' })).stores || [];
}

function status(context, folder) {
  const row = binding(context, folder);
  if (!row) return { configured: false, writable: false, mode: 'local' };
  return {
    configured: true,
    writable: row.writable === true && row.refreshPending !== true,
    mode: row.writable === true && row.refreshPending !== true ? 'remote_read_write' : 'offline_read_only',
    target: row.target,
    storeId: row.storeId,
    displayName: row.displayName,
    snapshotId: row.snapshotId,
    refreshPending: row.refreshPending,
    lastError: row.lastError,
  };
}

module.exports = {
  HELPER_COMMAND,
  INSTALL_COMMAND,
  PROTOCOL,
  REMOTE_CONFIGURED_CONTEXT,
  REMOTE_WRITABLE_CONTEXT,
  REPLICA_READ_MODULE,
  RemoteOperationError,
  RemoteTransportError,
  SNAPSHOT_ID_RE,
  STORE_ID_RE,
  TARGET_RE,
  binding,
  connect,
  deployRuntime,
  health,
  isConfigured,
  isMutatingCoreInvocation,
  isReplicaReadInvocation,
  listStores,
  mutationKind,
  refreshReplica,
  replicaArgsForInvocation,
  runCoreMutation,
  runCoreRead,
  saveHumanKnowledge,
  setContexts,
  sshArgs,
  status,
  uploadPayloadForInvocation,
};
