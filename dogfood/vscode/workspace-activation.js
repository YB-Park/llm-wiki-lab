'use strict';

const fs = require('node:fs');
const path = require('node:path');

const WORKSPACE_OPT_IN_FORMAT = 'llm-wiki-workspace-opt-in-v1';
const WORKSPACE_OPT_IN_FILE = 'workspace-opt-in.json';

function markerPath(root) {
  return path.join(root, WORKSPACE_OPT_IN_FILE);
}

function hasWorkspaceState(root) {
  try {
    return fs.statSync(root).isDirectory() && fs.readdirSync(root).length > 0;
  } catch (_) {
    return false;
  }
}

function isCoreInitialized(root) {
  return fs.existsSync(path.join(root, 'config.json')) && fs.existsSync(path.join(root, 'manifest.jsonl'));
}

function readWorkspaceOptIn(root) {
  try {
    const row = JSON.parse(fs.readFileSync(markerPath(root), 'utf8'));
    return row && row.format === WORKSPACE_OPT_IN_FORMAT && row.enabled === true ? row : undefined;
  } catch (_) {
    return undefined;
  }
}

function isWorkspaceEnabled(root) {
  return isCoreInitialized(root) && Boolean(readWorkspaceOptIn(root));
}

function enableWorkspace(root) {
  if (!isCoreInitialized(root)) {
    throw new Error('Cannot enable LLM Wiki Agent integration before the local Wiki store is initialized.');
  }
  fs.mkdirSync(root, { recursive: true });
  const target = markerPath(root);
  const temporary = `${target}.tmp-${process.pid}-${Date.now()}`;
  const row = {
    format: WORKSPACE_OPT_IN_FORMAT,
    enabled: true,
    enabled_at: new Date().toISOString(),
  };
  fs.writeFileSync(temporary, `${JSON.stringify(row, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
  if (fs.existsSync(target)) fs.unlinkSync(target);
  fs.renameSync(temporary, target);
  return row;
}

function disableWorkspace(root) {
  const target = markerPath(root);
  if (!fs.existsSync(target)) return false;
  fs.unlinkSync(target);
  return true;
}

module.exports = {
  WORKSPACE_OPT_IN_FILE,
  WORKSPACE_OPT_IN_FORMAT,
  disableWorkspace,
  enableWorkspace,
  hasWorkspaceState,
  isCoreInitialized,
  isWorkspaceEnabled,
  markerPath,
  readWorkspaceOptIn,
};
