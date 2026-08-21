'use strict';

const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const { defaultPythonNames } = require('./python-runtime-policy');

const execFileAsync = promisify(execFile);
const runtimeCache = new Map();
const autoRuntimeCache = new Map();

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
  return defaultPythonNames(platform).map((executable) => ({ executable, source: 'auto' }));
}

function autoPythonCandidates(platform = process.platform) {
  return defaultPythonNames(platform).map((executable) => ({ executable, source: 'auto-isolated' }));
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
  const explicit = explicitSettingValue();
  const key = `${folder.uri.toString()}|${process.platform}|${explicit}`;
  if (runtimeCache.has(key)) return runtimeCache.get(key);
  for (const candidate of pythonCandidates(folder)) {
    if (await executableAvailable(candidate.executable, folder.uri.fsPath)) {
      runtimeCache.set(key, candidate);
      return candidate;
    }
  }
  runtimeCache.set(key, undefined);
  return undefined;
}

async function resolveAutoPythonRuntime(folder) {
  const key = `${folder.uri.toString()}|${process.platform}`;
  if (autoRuntimeCache.has(key)) return autoRuntimeCache.get(key);
  for (const candidate of autoPythonCandidates()) {
    if (await executableAvailable(candidate.executable, folder.uri.fsPath)) {
      autoRuntimeCache.set(key, candidate);
      return candidate;
    }
  }
  autoRuntimeCache.set(key, undefined);
  return undefined;
}

function clearPythonRuntimeCache() {
  runtimeCache.clear();
  autoRuntimeCache.clear();
}

module.exports = {
  autoPythonCandidates,
  clearPythonRuntimeCache,
  explicitSettingValue,
  pythonCandidates,
  resolveAutoPythonRuntime,
  resolvePythonRuntime,
};
