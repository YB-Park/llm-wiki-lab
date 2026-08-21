'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const WORKSPACE_OPT_IN_FORMAT = 'llm-wiki-workspace-opt-in-v1';
const WORKSPACE_OPT_IN_FILE = 'workspace-opt-in.json';
const EPOCH_ID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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
    if (!row || row.format !== WORKSPACE_OPT_IN_FORMAT || row.enabled !== true) return undefined;
    if (typeof row.enabled_at !== 'string' || !row.enabled_at.trim()) return undefined;
    if (row.epoch_id !== undefined && !EPOCH_ID_RE.test(String(row.epoch_id))) return undefined;
    return row;
  } catch (_) {
    return undefined;
  }
}

function workspaceEpoch(row) {
  if (!row || row.enabled !== true) return '';
  if (typeof row.epoch_id === 'string' && EPOCH_ID_RE.test(row.epoch_id)) return row.epoch_id;
  return typeof row.enabled_at === 'string' ? row.enabled_at : '';
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
    epoch_id: crypto.randomUUID(),
  };
  fs.writeFileSync(temporary, `${JSON.stringify(row, null, 2)}\n`, {
    encoding: 'utf8',
    flag: 'wx',
    mode: 0o600,
  });
  if (fs.existsSync(target)) fs.unlinkSync(target);
  fs.renameSync(temporary, target);
  try { fs.chmodSync(target, 0o600); } catch (_) {}
  return row;
}

function disableWorkspace(root) {
  const target = markerPath(root);
  if (!fs.existsSync(target)) return false;
  fs.unlinkSync(target);
  return true;
}

module.exports = {
  EPOCH_ID_RE,
  WORKSPACE_OPT_IN_FILE,
  WORKSPACE_OPT_IN_FORMAT,
  disableWorkspace,
  enableWorkspace,
  hasWorkspaceState,
  isCoreInitialized,
  isWorkspaceEnabled,
  markerPath,
  readWorkspaceOptIn,
  workspaceEpoch,
};
