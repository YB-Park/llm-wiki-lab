'use strict';

const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');

const execFileAsync = promisify(execFile);

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
}

function explicitSettingValue() {
  const inspected = configuration().inspect('pythonExecutable');
  if (!inspected) return '';
  const values = [
    inspected.workspaceFolderValue,
    inspected.workspaceValue,
    inspected.globalValue,
  ];
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) return value.trim();
  }
  return '';
}

function resolveCandidate(folder, value) {
  if (path.isAbsolute(value) || (!value.includes('/') && !value.includes('\\'))) return value;
  return path.resolve(folder.uri.fsPath, value);
}

function pythonCandidates(folder, platform = process.platform) {
  const explicit = explicitSettingValue();
  if (explicit) return [{ executable: resolveCandidate(folder, explicit), source: 'configured' }];
  const names = platform === 'win32'
    ? ['python', 'py', 'python3']
    : ['python3', 'python'];
  return names.map((executable) => ({ executable, source: 'auto' }));
}

async function executableAvailable(executable, cwd) {
  try {
    await execFileAsync(executable, ['--version'], {
      cwd,
      windowsHide: true,
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    });
    return true;
  } catch (_) {
    return false;
  }
}

async function resolvePythonRuntime(folder) {
  for (const candidate of pythonCandidates(folder)) {
    if (await executableAvailable(candidate.executable, folder.uri.fsPath)) return candidate;
  }
  return undefined;
}

module.exports = {
  explicitSettingValue,
  pythonCandidates,
  resolvePythonRuntime,
};
