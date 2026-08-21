'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const workspaceActivation = require('./workspace-activation');

const CATALOG_KEY = 'llmWiki.personalWikiLibrary.v2';
const CATALOG_VERSION = 2;
const LIBRARY_GRANT_KEY_PREFIX = 'llmWiki.personalWikiLibraryAccess.v1';
const LIBRARY_GRANT_VERSION = 1;
const LIBRARY_MODE = 'named_store_only';
const STORE_ID_RE = /^libstore-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const AUTHORITY_ANCHOR_RE = /^[0-9a-f]{64}$/;
const MANIFEST_ANCHOR_READ_LIMIT = 64 * 1024;

function normalizeAlias(value) {
  return String(value || '').trim().toLocaleLowerCase('en-US');
}

function normalizeAliases(values) {
  const result = [];
  for (const value of Array.isArray(values) ? values : []) {
    const text = String(value || '').trim();
    if (!text) continue;
    const key = normalizeAlias(text);
    if (!result.some((item) => normalizeAlias(item) === key)) result.push(text.slice(0, 120));
  }
  return result.slice(0, 12);
}

function emptyCatalog() {
  return { version: CATALOG_VERSION, stores: [] };
}

function validateCatalog(raw) {
  if (!raw || raw.version !== CATALOG_VERSION) return emptyCatalog();
  if (!Array.isArray(raw.stores)) throw new Error('library_catalog_corrupt');

  const stores = [];
  const ids = new Set();
  const roots = new Set();
  for (const row of raw.stores) {
    if (
      !row
      || !STORE_ID_RE.test(String(row.storeId || ''))
      || typeof row.root !== 'string'
      || !path.isAbsolute(row.root)
      || typeof row.displayName !== 'string'
      || !row.displayName.trim()
      || !Array.isArray(row.aliases)
      || row.readExposure !== true
      || row.modelExposure !== true
      || !AUTHORITY_ANCHOR_RE.test(String(row.authorityAnchor || ''))
    ) {
      throw new Error('library_catalog_corrupt');
    }
    const storeId = String(row.storeId);
    const root = String(row.root);
    if (ids.has(storeId) || roots.has(root)) throw new Error('library_catalog_corrupt');
    ids.add(storeId);
    roots.add(root);
    stores.push({
      storeId,
      root,
      displayName: String(row.displayName).trim().slice(0, 120),
      aliases: normalizeAliases(row.aliases),
      readExposure: true,
      modelExposure: true,
      authorityAnchor: String(row.authorityAnchor),
      registeredAt: String(row.registeredAt || ''),
    });
  }
  return { version: CATALOG_VERSION, stores };
}

function catalog(context) {
  return validateCatalog(context.globalState.get(CATALOG_KEY));
}

async function saveCatalog(context, value) {
  await context.globalState.update(CATALOG_KEY, validateCatalog(value));
}

function canonicalRoot(root) {
  if (!root || !path.isAbsolute(root)) throw new Error('library_store_invalid');
  try {
    return fs.realpathSync(root);
  } catch (_) {
    throw new Error('library_store_unavailable');
  }
}

function manifestAuthorityAnchor(root) {
  const manifest = path.join(root, 'manifest.jsonl');
  let descriptor;
  try {
    const stat = fs.statSync(manifest);
    if (!stat.isFile() || stat.size <= 0) throw new Error('empty');
    descriptor = fs.openSync(manifest, 'r');
    const size = Math.min(stat.size, MANIFEST_ANCHOR_READ_LIMIT);
    const buffer = Buffer.alloc(size);
    const bytesRead = fs.readSync(descriptor, buffer, 0, size, 0);
    const text = buffer.subarray(0, bytesRead).toString('utf8');
    const lastNewline = text.lastIndexOf('\n');
    if (lastNewline < 0) throw new Error('unterminated');
    const first = text.slice(0, lastNewline + 1).split(/\r?\n/).find((line) => line.trim());
    if (!first) throw new Error('empty');
    const event = JSON.parse(first);
    if (
      !event
      || event.event !== 'ingest'
      || typeof event.source_id !== 'string'
      || !event.source_id.startsWith('src-')
      || typeof event.sha256 !== 'string'
      || !AUTHORITY_ANCHOR_RE.test(event.sha256)
    ) {
      throw new Error('invalid');
    }
    return crypto.createHash('sha256').update(first.trim(), 'utf8').digest('hex');
  } catch (_) {
    throw new Error('library_store_no_authority_anchor');
  } finally {
    if (descriptor !== undefined) {
      try { fs.closeSync(descriptor); } catch (_) {}
    }
  }
}

async function registerStore(context, options) {
  const root = canonicalRoot(options && options.root);
  const currentRoot = options && options.currentRoot ? canonicalRoot(options.currentRoot) : '';
  if (currentRoot && root === currentRoot) throw new Error('library_store_is_current_store');
  if (!workspaceActivation.isCoreInitialized(root)) throw new Error('library_store_not_initialized');

  const displayName = String((options && options.displayName) || '').trim();
  if (!displayName || displayName.length > 120) throw new Error('library_store_display_name_invalid');
  const aliases = normalizeAliases(options && options.aliases);
  const authorityAnchor = manifestAuthorityAnchor(root);
  const current = catalog(context);
  const existing = current.stores.find((row) => row.root === root);
  const sameAuthority = existing && existing.authorityAnchor === authorityAnchor;
  const row = {
    storeId: sameAuthority ? existing.storeId : `libstore-${crypto.randomUUID()}`,
    root,
    displayName,
    aliases,
    readExposure: true,
    modelExposure: true,
    authorityAnchor,
    registeredAt: sameAuthority && existing.registeredAt ? existing.registeredAt : new Date().toISOString(),
  };
  const stores = current.stores.filter((item) => item.root !== root && item.storeId !== row.storeId);
  stores.push(row);
  await saveCatalog(context, { version: CATALOG_VERSION, stores });
  return { storeId: row.storeId, displayName: row.displayName, aliases: row.aliases };
}

async function removeStore(context, storeId) {
  const id = String(storeId || '').trim();
  if (!STORE_ID_RE.test(id)) throw new Error('library_store_id_invalid');
  const current = catalog(context);
  const stores = current.stores.filter((row) => row.storeId !== id);
  if (stores.length === current.stores.length) return false;
  await saveCatalog(context, { version: CATALOG_VERSION, stores });
  return true;
}

function grantKey(folder) {
  return `${LIBRARY_GRANT_KEY_PREFIX}:${folder.uri.toString()}`;
}

function libraryGrant(context, folder, currentRoot) {
  const row = context.workspaceState.get(grantKey(folder));
  const optIn = workspaceActivation.readWorkspaceOptIn(currentRoot);
  if (!row || !optIn || row.version !== LIBRARY_GRANT_VERSION || row.enabled !== true) return undefined;
  const storedEpoch = String(row.workspaceEpoch || row.workspaceEnabledAt || '');
  if (row.mode !== LIBRARY_MODE || !storedEpoch || storedEpoch !== workspaceActivation.workspaceEpoch(optIn)) return undefined;
  return { ...row };
}

async function setLibraryAccess(context, folder, currentRoot, enabled) {
  if (!enabled) {
    await context.workspaceState.update(grantKey(folder), undefined);
    return false;
  }
  const optIn = workspaceActivation.readWorkspaceOptIn(currentRoot);
  if (!optIn) throw new Error('library_workspace_not_enabled');
  await context.workspaceState.update(grantKey(folder), {
    version: LIBRARY_GRANT_VERSION,
    enabled: true,
    mode: LIBRARY_MODE,
    workspaceEnabledAt: optIn.enabled_at,
    workspaceEpoch: workspaceActivation.workspaceEpoch(optIn),
  });
  return true;
}

function namesForStore(row) {
  return [row.displayName, ...row.aliases].map(normalizeAlias).filter(Boolean);
}

function authorizedCatalog(context, folder, currentRoot) {
  if (!libraryGrant(context, folder, currentRoot)) throw new Error('library_access_disabled');
  return catalog(context);
}

function verifyStoreRow(row) {
  let resolved;
  try {
    resolved = fs.realpathSync(row.root);
    if (resolved !== row.root || !fs.statSync(row.root).isDirectory()) throw new Error('identity');
  } catch (error) {
    if (error && error.message === 'identity') throw new Error('library_store_identity_changed');
    throw new Error('library_store_unavailable');
  }
  if (!workspaceActivation.isCoreInitialized(row.root)) throw new Error('library_store_damaged');
  let anchor;
  try {
    anchor = manifestAuthorityAnchor(row.root);
  } catch (_) {
    throw new Error('library_store_identity_changed');
  }
  if (anchor !== row.authorityAnchor) throw new Error('library_store_identity_changed');
  return row;
}

function verifyStoreHandle(handle) {
  if (
    !handle
    || typeof handle.root !== 'string'
    || !path.isAbsolute(handle.root)
    || !AUTHORITY_ANCHOR_RE.test(String(handle.authorityAnchor || ''))
  ) {
    throw new Error('library_store_invalid');
  }
  verifyStoreRow({ root: handle.root, authorityAnchor: String(handle.authorityAnchor) });
  return handle;
}

function storeHandle(row) {
  return {
    storeId: row.storeId,
    displayName: row.displayName,
    root: row.root,
    authorityAnchor: row.authorityAnchor,
    isCurrentStore: false,
    scopeRef: { kind: 'library_store', store_id: row.storeId },
  };
}

function resolveNamedStore(context, folder, currentRoot, requestedName) {
  const needle = normalizeAlias(requestedName);
  if (!needle) throw new Error('library_store_name_required');
  const current = authorizedCatalog(context, folder, currentRoot);
  const matches = current.stores.filter((row) => (
    row.readExposure === true
    && row.modelExposure === true
    && namesForStore(row).includes(needle)
  ));
  if (matches.length === 0) throw new Error('library_store_not_registered');
  if (matches.length !== 1) throw new Error('library_store_ambiguous');
  return storeHandle(verifyStoreRow(matches[0]));
}

function resolveStoreId(context, folder, currentRoot, storeId) {
  const id = String(storeId || '').trim();
  if (!STORE_ID_RE.test(id)) throw new Error('library_store_id_invalid');
  const current = authorizedCatalog(context, folder, currentRoot);
  const matches = current.stores.filter((item) => item.storeId === id && item.readExposure === true && item.modelExposure === true);
  if (matches.length === 0) throw new Error('library_store_not_registered');
  if (matches.length !== 1) throw new Error('library_catalog_corrupt');
  return storeHandle(verifyStoreRow(matches[0]));
}

function registeredStores(context) {
  return catalog(context).stores.map((row) => ({
    storeId: row.storeId,
    displayName: row.displayName,
    aliases: [...row.aliases],
  }));
}

module.exports = {
  AUTHORITY_ANCHOR_RE,
  CATALOG_KEY,
  CATALOG_VERSION,
  LIBRARY_GRANT_VERSION,
  LIBRARY_MODE,
  STORE_ID_RE,
  catalog,
  grantKey,
  libraryGrant,
  manifestAuthorityAnchor,
  normalizeAlias,
  registerStore,
  registeredStores,
  removeStore,
  resolveNamedStore,
  resolveStoreId,
  setLibraryAccess,
  verifyStoreHandle,
};
