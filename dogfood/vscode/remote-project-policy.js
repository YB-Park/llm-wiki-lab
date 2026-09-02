'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const FRESH_LOCAL_ENTRIES = new Set([
  'config.json',
  'manifest.jsonl',
  'raw',
  'workspace-opt-in.json',
  '.writer.lock',
]);

function safeLstat(target, expected) {
  let stat;
  try { stat = fs.lstatSync(target); } catch (_) {
    throw new Error('remote_attach_requires_initialized_empty_local_memory');
  }
  if (stat.isSymbolicLink()) throw new Error('remote_attach_requires_initialized_empty_local_memory');
  if (expected === 'file' && !stat.isFile()) throw new Error('remote_attach_requires_initialized_empty_local_memory');
  if (expected === 'directory' && !stat.isDirectory()) throw new Error('remote_attach_requires_initialized_empty_local_memory');
  return stat;
}

function assertFreshLocalMemory(root) {
  safeLstat(root, 'directory');
  const config = path.join(root, 'config.json');
  const manifest = path.join(root, 'manifest.jsonl');
  const raw = path.join(root, 'raw');
  const optIn = path.join(root, 'workspace-opt-in.json');
  const writerLock = path.join(root, '.writer.lock');
  safeLstat(config, 'file');
  const manifestStat = safeLstat(manifest, 'file');
  safeLstat(raw, 'directory');
  safeLstat(optIn, 'file');
  if (fs.existsSync(writerLock)) safeLstat(writerLock, 'file');

  if (manifestStat.size !== 0) throw new Error('remote_attach_requires_empty_local_memory');
  if (fs.readdirSync(raw).length !== 0) throw new Error('remote_attach_requires_empty_local_memory');

  for (const name of fs.readdirSync(root)) {
    if (!FRESH_LOCAL_ENTRIES.has(name)) throw new Error('remote_attach_requires_empty_local_memory');
  }
  return true;
}

function authorityCacheKey(target) {
  return crypto.createHash('sha256').update(String(target || ''), 'utf8').digest('hex').slice(0, 24);
}

module.exports = {
  FRESH_LOCAL_ENTRIES,
  assertFreshLocalMemory,
  authorityCacheKey,
  safeLstat,
};
