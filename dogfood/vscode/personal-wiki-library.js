'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const workspaceActivation = require('./workspace-activation');

const CATALOG_KEY = 'llmWiki.personalWikiLibrary.v1';
const CATALOG_VERSION = 1;
const LIBRARY_GRANT_KEY_PREFIX = 'llmWiki.personalWikiLibraryAccess.v1';
const LIBRARY_GRANT_VERSION = 1;
const LIBRARY_MODE = 'named_store_only';
const STORE_ID_RE = /^libstore-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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

function cleanCatalog(raw) {
  if (!raw || raw.version !== CATALOG_VERSION || !Array.isArray(raw.stores)) {
    return { version: CATALOG_VERSION, stores: [] };
  }
  const stores = raw.stores.filter((row) => (
    row
    && STORE_ID_RE.test(String(row.storeId || ''))
    && typeof row.root === 'string'
    && path.isAbsolute(row.root)
    && typeof row.displayName === 'string'
    && row.displayName.trim()
    && row.readExposure === true
    && row.modelExposure === true
  )).map((row) => ({
    storeId: String(row.storeId),
    root: String(row.root),
    displayName: String(row.displayName).trim().slice(0, 120),
    aliases: normalizeAliases(row.aliases),
    readExposure: true,
    modelExposure: true,
    registeredAt: String(row.registeredAt || ''),
  }));
  return { version: CATALOG_VERSION, stores };
}

function catalog(context) {
  return cleanCatalog(context.globalState.get(CATALOG_KEY));
}

async function saveCatalog(context, value) {
  await context.globalState.update(CATALOG_KEY, cleanCatalog(value));
}

function canonicalRoot(root) {
  if (!root || !path.isAbsolute(root)) throw new Error('library_store_invalid');
  try {
    return fs.realpathSync(root);
  } catch (_) {
    throw new Error('library_store_unavailable');
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
  const current = catalog(context);
  const existing = current.stores.find((row) => row.root === root);
  const row = {
    storeId: existing ? existing.storeId : `libstore-${crypto.randomUUID()}`,
    root,
    displayName,
    aliases,
    readExposure: true,
    modelExposure: true,
    registeredAt: existing && existing.registeredAt ? existing.registeredAt : new Date().toISOString(),
  };
  const stores = current.stores.filter((item) => item.storeId !== row.storeId);
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
  if (row.mode !== LIBRARY_MODE || row.workspaceEnabledAt !== optIn.enabled_at) return undefined;
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

function storeHandle(row) {
  return {
    storeId: row.storeId,
    displayName: row.displayName,
    root: row.root,
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
  const row = matches[0];
  try {
    if (!fs.statSync(row.root).isDirectory()) throw new Error('not-directory');
  } catch (_) {
    throw new Error('library_store_unavailable');
  }
  if (!workspaceActivation.isCoreInitialized(row.root)) throw new Error('library_store_damaged');
  return storeHandle(row);
}

function resolveStoreId(context, folder, currentRoot, storeId) {
  const id = String(storeId || '').trim();
  if (!STORE_ID_RE.test(id)) throw new Error('library_store_id_invalid');
  const current = authorizedCatalog(context, folder, currentRoot);
  const row = current.stores.find((item) => item.storeId === id && item.readExposure === true && item.modelExposure === true);
  if (!row) throw new Error('library_store_not_registered');
  try {
    if (!fs.statSync(row.root).isDirectory()) throw new Error('not-directory');
  } catch (_) {
    throw new Error('library_store_unavailable');
  }
  if (!workspaceActivation.isCoreInitialized(row.root)) throw new Error('library_store_damaged');
  return storeHandle(row);
}

function registeredStores(context) {
  return catalog(context).stores.map((row) => ({
    storeId: row.storeId,
    displayName: row.displayName,
    aliases: [...row.aliases],
  }));
}

module.exports = {
  CATALOG_KEY,
  CATALOG_VERSION,
  LIBRARY_GRANT_VERSION,
  LIBRARY_MODE,
  STORE_ID_RE,
  catalog,
  grantKey,
  libraryGrant,
  normalizeAlias,
  registerStore,
  registeredStores,
  removeStore,
  resolveNamedStore,
  resolveStoreId,
  setLibraryAccess,
};