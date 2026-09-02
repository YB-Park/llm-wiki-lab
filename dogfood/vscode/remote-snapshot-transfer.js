'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const vscode = require('vscode');
const remoteMemory = require('./remote-memory');
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

async function fetchSnapshot(context, folder, target, storeId, destination, options = {}) {
  if (!remoteMemory.TARGET_RE.test(String(target || ''))) throw new Error('remote_ssh_target_invalid');
  if (!remoteMemory.STORE_ID_RE.test(String(storeId || ''))) throw new Error('remote_store_id_invalid');
  if (!path.isAbsolute(destination)) throw new Error('remote_snapshot_destination_invalid');
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const core = coreRoot(context, folder);

  const ssh = spawn('ssh', remoteMemory.sshArgs(target, remoteMemory.HELPER_COMMAND), {
    cwd: folder.uri.fsPath,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  ssh.stdin.end(`${JSON.stringify({ protocol: remoteMemory.PROTOCOL, op: 'snapshot_export', store_id: storeId })}\n`, 'utf8');

  const attachEmpty = options.attachEmpty === true;
  const moduleName = attachEmpty
    ? 'dogfood.llm_wiki.remote_attach_import'
    : 'dogfood.llm_wiki.remote_snapshot';
  const args = attachEmpty
    ? ['-m', moduleName, '--root', destination]
    : ['-m', moduleName, 'import', '--root', destination, '--replace-host-local'];
  const importer = spawn(runtime.executable, args, {
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
    const detail = boundedProcessFailure(importResult.stderr.toString('utf8') || importResult.stdout.toString('utf8'));
    throw new Error(`remote_snapshot_verify_failed:${detail}`);
  }
  let imported;
  try { imported = JSON.parse(importResult.stdout.toString('utf8')); } catch (_) {
    throw new Error('remote_snapshot_import_response_invalid');
  }
  if (!imported || imported.status !== 'IMPORTED' || !remoteMemory.SNAPSHOT_ID_RE.test(String(imported.snapshot_id || ''))) {
    throw new Error('remote_snapshot_import_response_invalid');
  }
  return String(imported.snapshot_id);
}

module.exports = {
  fetchSnapshot,
  waitProcess,
};
