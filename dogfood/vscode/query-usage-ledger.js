'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const FORMAT = 'llm-wiki-query-usage-v2';
const DAY_RE = /^\d{4}-\d{2}-\d{2}$/;
const SLOT_RE = /^slot-(\d{3})\.json$/;
const MAX_SLOTS = 100;

function storageRoot(context) {
  const value = context && context.globalStorageUri && context.globalStorageUri.fsPath;
  if (typeof value !== 'string' || !path.isAbsolute(value)) {
    throw new Error('query_usage_storage_unavailable');
  }
  return value;
}

function workspaceKey(folder) {
  const uri = folder && folder.uri && typeof folder.uri.toString === 'function' ? folder.uri.toString() : '';
  if (!uri) throw new Error('query_usage_scope_invalid');
  return crypto.createHash('sha256').update(uri, 'utf8').digest('hex');
}

function usageDirectory(context, folder, day) {
  if (!DAY_RE.test(String(day || ''))) throw new Error('query_usage_day_invalid');
  return path.join(storageRoot(context), 'query-usage-v2', workspaceKey(folder), day);
}

function slotPath(directory, slot) {
  if (!Number.isInteger(slot) || slot < 1 || slot > MAX_SLOTS) throw new Error('query_usage_slot_invalid');
  return path.join(directory, `slot-${String(slot).padStart(3, '0')}.json`);
}

function existingSlots(directory) {
  try {
    const slots = new Set();
    for (const name of fs.readdirSync(directory)) {
      const match = SLOT_RE.exec(name);
      if (!match) continue;
      const slot = Number(match[1]);
      if (slot >= 1 && slot <= MAX_SLOTS) slots.add(slot);
    }
    return slots;
  } catch (error) {
    if (error && error.code === 'ENOENT') return new Set();
    throw new Error('query_usage_storage_unavailable');
  }
}

function createSlot(directory, day, slot, imported = false) {
  let descriptor;
  try {
    descriptor = fs.openSync(slotPath(directory, slot), 'wx', 0o600);
    fs.writeFileSync(descriptor, `${JSON.stringify({ format: FORMAT, day, slot, imported: imported === true })}\n`, 'utf8');
    return true;
  } catch (error) {
    if (error && error.code === 'EEXIST') return false;
    throw new Error('query_usage_storage_unavailable');
  } finally {
    if (descriptor !== undefined) {
      try { fs.closeSync(descriptor); } catch (_) {}
    }
  }
}

function ensureDirectory(directory) {
  try {
    fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  } catch (_) {
    throw new Error('query_usage_storage_unavailable');
  }
}

function importLegacyCount(directory, day, legacyCount) {
  const count = Math.max(0, Math.min(MAX_SLOTS, Math.trunc(Number(legacyCount || 0)) || 0));
  for (let slot = 1; slot <= count; slot += 1) createSlot(directory, day, slot, true);
}

function readUsage(context, folder, day, legacyCount = 0) {
  const directory = usageDirectory(context, folder, day);
  const durableCount = existingSlots(directory).size;
  const legacy = Math.max(0, Math.min(MAX_SLOTS, Math.trunc(Number(legacyCount || 0)) || 0));
  return { day, reservedCalls: Math.max(durableCount, legacy) };
}

function reserveUsage(context, folder, day, limit, legacyCount = 0) {
  const dailyCallLimit = Number(limit);
  if (!Number.isInteger(dailyCallLimit) || dailyCallLimit < 1 || dailyCallLimit > MAX_SLOTS) {
    throw new Error('query_usage_limit_invalid');
  }
  const directory = usageDirectory(context, folder, day);
  ensureDirectory(directory);
  importLegacyCount(directory, day, legacyCount);

  for (let slot = 1; slot <= dailyCallLimit; slot += 1) {
    if (createSlot(directory, day, slot, false)) {
      return { allowed: true, day, reservedCalls: existingSlots(directory).size };
    }
  }
  return { allowed: false, day, reservedCalls: existingSlots(directory).size };
}

module.exports = {
  FORMAT,
  MAX_SLOTS,
  existingSlots,
  readUsage,
  reserveUsage,
  storageRoot,
  usageDirectory,
  workspaceKey,
};
