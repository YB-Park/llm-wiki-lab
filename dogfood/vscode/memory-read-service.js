'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const humanKnowledge = require('./human-knowledge');
const { boundedProcessFailure } = require('./process-errors');
const { resolvePythonRuntime } = require('./python-runtime');

const execFileAsync = promisify(execFile);
const MAX_BUFFER = 16 * 1024 * 1024;

const QUERY_PROFILE_V1 = Object.freeze({
  id: 'current-store-l0-v1',
  rawDiscoveryLimit: 6,
  rawInternalLimit: 8,
  derivedLimit: 3,
  humanLimit: 3,
  relevantRegionChars: 6000,
  relevantQueryChars: 2000,
});

const NAMED_STORE_QUERY_PROFILE_V1 = Object.freeze({
  ...QUERY_PROFILE_V1,
  id: 'named-store-l0-v1',
});

function configuration() {
  return require('vscode').workspace.getConfiguration('llmWiki');
}

function wikiRoot(folder) {
  const value = String(configuration().get('workspaceDirectory', '.wiki-lab') || '.wiki-lab');
  return path.isAbsolute(value) ? value : path.resolve(folder.uri.fsPath, value);
}

function currentStoreHandle(folder) {
  return {
    root: wikiRoot(folder),
    isCurrentStore: true,
    displayName: '',
    scopeRef: { kind: 'current_store' },
  };
}

function normalizeStoreHandle(folder, handle) {
  if (!handle) return currentStoreHandle(folder);
  if (handle.isCurrentStore === true) return currentStoreHandle(folder);
  const scopeRef = handle.scopeRef;
  if (
    !scopeRef
    || scopeRef.kind !== 'library_store'
    || typeof scopeRef.store_id !== 'string'
    || !/^libstore-[0-9a-f-]+$/i.test(scopeRef.store_id)
    || typeof handle.root !== 'string'
    || !path.isAbsolute(handle.root)
  ) {
    throw new Error('library_store_invalid');
  }
  return {
    root: handle.root,
    isCurrentStore: false,
    storeId: scopeRef.store_id,
    displayName: String(handle.displayName || ''),
    scopeRef: { kind: 'library_store', store_id: scopeRef.store_id },
  };
}

function coreRoot(context, folder) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'cli.py'))) return bundled;
  return path.resolve(context.extensionPath, '..', '..');
}

function isWikiInitialized(folder, storeHandle) {
  const root = normalizeStoreHandle(folder, storeHandle).root;
  return fs.existsSync(path.join(root, 'config.json')) && fs.existsSync(path.join(root, 'manifest.jsonl'));
}

async function runPythonModule(context, folder, moduleName, args, options = {}) {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const core = coreRoot(context, folder);
  const store = normalizeStoreHandle(folder, options.storeHandle);
  const pythonPath = process.env.PYTHONPATH ? `${core}${path.delimiter}${process.env.PYTHONPATH}` : core;
  const fullArgs = ['-m', moduleName, '--root', store.root, ...args];
  try {
    const result = await execFileAsync(runtime.executable, fullArgs, {
      cwd: folder.uri.fsPath,
      env: { ...process.env, PYTHONPATH: pythonPath },
      maxBuffer: MAX_BUFFER,
      windowsHide: true,
    });
    return String(result.stdout || '');
  } catch (error) {
    const stderr = error && error.stderr ? String(error.stderr).trim() : '';
    const stdout = error && error.stdout ? String(error.stdout).trim() : '';
    const detail = stderr || stdout || (error && error.message) || String(error);
    throw new Error(boundedProcessFailure(detail));
  }
}

async function assertStoreIntegrity(context, folder, storeHandle) {
  const store = normalizeStoreHandle(folder, storeHandle);
  if (!isWikiInitialized(folder, store)) {
    if (!store.isCurrentStore) throw new Error('library_store_damaged');
    return false;
  }
  try {
    const row = JSON.parse((await runPythonModule(
      context,
      folder,
      'dogfood.llm_wiki.cli',
      ['integrity'],
      { storeHandle: store }
    )).trim());
    if (!row || row.ok !== true) throw new Error('integrity-failed');
    return true;
  } catch (_) {
    if (!store.isCurrentStore) throw new Error('library_store_damaged');
    return false;
  }
}

function parseJsonLines(stdout) {
  return String(stdout || '')
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

function firstSourceId(row) {
  if (Array.isArray(row.source_ids) && row.source_ids.length) return String(row.source_ids[0] || '').trim();
  return String(row.source_id || '').trim();
}

async function collectMemoryRows(context, folder, query, options = {}) {
  const maxResults = Math.max(1, Math.min(8, Math.trunc(Number(options.maxResults || 5)) || 5));
  const derivedLimit = Math.min(3, maxResults);
  const store = normalizeStoreHandle(folder, options.storeHandle);
  const callOptions = { storeHandle: store };
  const [rawStdout, derivedStdout, pendingStdout] = await Promise.all([
    runPythonModule(context, folder, 'dogfood.llm_wiki.cli', ['discover', query, '--top-k-per-topic', '3', '--json'], callOptions),
    runPythonModule(context, folder, 'dogfood.llm_wiki.agent_wiki_cli', ['search', query, '--top-k', String(derivedLimit), '--json'], callOptions),
    runPythonModule(context, folder, 'dogfood.llm_wiki.agent_state_cli', ['pending-list'], callOptions),
  ]);
  return {
    rawRows: parseJsonLines(rawStdout).slice(0, maxResults),
    derivedRows: parseJsonLines(derivedStdout),
    humanRows: humanKnowledge.search(store.root, query, 3),
    pendingRows: parseJsonLines(pendingStdout),
  };
}

function navigationQuery(question, derivedRow) {
  const title = String(derivedRow.title || '').trim();
  const snippet = String(derivedRow.snippet || '').trim().slice(0, 500);
  return [question, title, snippet].filter(Boolean).join('\n');
}

function mergedTargetQuery(target, maxChars) {
  return [...new Set(target.queryHints.map((value) => String(value || '').trim()).filter(Boolean))]
    .join('\n')
    .slice(0, maxChars);
}

async function collectQueryEvidence(context, folder, question, profile, storeHandle) {
  const store = normalizeStoreHandle(folder, storeHandle);
  const effectiveProfile = profile || (store.isCurrentStore ? QUERY_PROFILE_V1 : NAMED_STORE_QUERY_PROFILE_V1);
  const scopeRef = store.scopeRef;
  const memory = await collectMemoryRows(context, folder, question, {
    maxResults: effectiveProfile.rawDiscoveryLimit,
    storeHandle: store,
  });
  const rawHits = memory.rawRows.slice(0, effectiveProfile.rawDiscoveryLimit);
  const derivedRows = memory.derivedRows.slice(0, effectiveProfile.derivedLimit);
  const humanRows = memory.humanRows.slice(0, effectiveProfile.humanLimit);

  const targets = [];
  const bySource = new Map();
  const addTarget = (sourceId, topicId, queryHint, equivalentSourceIds = [], objectId = '') => {
    if (!sourceId) return;
    const existing = bySource.get(sourceId);
    if (existing) {
      if (queryHint) existing.queryHints.push(queryHint);
      if (!existing.topicId && topicId) existing.topicId = String(topicId).trim();
      if (!existing.objectId && objectId) existing.objectId = String(objectId);
      for (const equivalentId of equivalentSourceIds.map(String)) {
        if (equivalentId && !existing.equivalentSourceIds.includes(equivalentId)) existing.equivalentSourceIds.push(equivalentId);
      }
      return;
    }
    if (targets.length >= effectiveProfile.rawInternalLimit) return;
    const target = {
      sourceId,
      topicId: String(topicId || '').trim(),
      queryHints: queryHint ? [queryHint] : [],
      equivalentSourceIds: [...new Set(equivalentSourceIds.map(String).filter(Boolean))],
      objectId: String(objectId || ''),
    };
    bySource.set(sourceId, target);
    targets.push(target);
  };

  for (const row of rawHits) {
    const sourceId = firstSourceId(row);
    const equivalentSourceIds = Array.isArray(row.source_ids) ? row.source_ids.map(String) : [sourceId].filter(Boolean);
    addTarget(sourceId, row.topic_id, question, equivalentSourceIds, String(row.object_id || ''));
  }
  for (const row of derivedRows) {
    addTarget(String(row.source_id || '').trim(), row.topic_id, navigationQuery(question, row));
  }

  const raw = [];
  for (const target of targets) {
    const args = [
      'relevant', target.sourceId,
      '--query', mergedTargetQuery(target, effectiveProfile.relevantQueryChars),
      '--max-chars', String(effectiveProfile.relevantRegionChars),
    ];
    if (target.topicId) args.push('--topic', target.topicId);
    let row;
    try {
      row = JSON.parse((await runPythonModule(
        context,
        folder,
        'dogfood.llm_wiki.agent_memory_cli',
        args,
        { storeHandle: store }
      )).trim());
    } catch (_) {
      throw new Error(`query_plane_candidate_verification_failed:${target.sourceId}`);
    }
    if (row.format !== 'llm-wiki-agent-relevant-read-v0' || row.source_id !== target.sourceId) {
      throw new Error(`query_plane_candidate_identity_mismatch:${target.sourceId}`);
    }
    raw.push({
      scope_ref: { ...scopeRef },
      source_id: row.source_id,
      equivalent_source_ids: target.equivalentSourceIds.length ? target.equivalentSourceIds : [row.source_id],
      object_id: row.object_id || target.objectId || '',
      sha256: row.sha256 || '',
      topic_id: row.topic_id || target.topicId || '',
      status: row.status || 'unknown',
      contested: row.contested === true,
      name: row.name || '',
      start_char: Number(row.start_char || 0),
      end_char: Number(row.end_char || 0),
      total_chars: Number(row.total_chars || 0),
      has_more_before: row.has_more_before === true,
      has_more_after: row.has_more_after === true,
      text: row.text || '',
    });
  }

  const human = humanRows.map((row) => ({
    scope_ref: { ...scopeRef },
    id: row.id,
    title: row.title || '',
    statement: row.statement || '',
    reasoning: row.reasoning || '',
    supporting_source_ids: Array.isArray(row.sourceIds) ? row.sourceIds : [],
    supersedes_knowledge_id: row.supersedesKnowledgeId || '',
  }));
  const derived = derivedRows.map((row) => ({
    scope_ref: { ...scopeRef },
    source_id: row.source_id,
    topic_id: row.topic_id || '',
    title: row.title || '',
    snippet: row.snippet || '',
  }));
  const pending = memory.pendingRows.slice(0, 5).map((row) => ({
    scope_ref: { ...scopeRef },
    decision_id: row.id,
    topic_id: row.topic_id || '',
    predecessor_source_ids: Array.isArray(row.predecessor_source_ids) ? row.predecessor_source_ids : [],
    successor_source_id: row.successor_source_id || '',
  }));

  return {
    question,
    scope: { ...scopeRef },
    query_profile: effectiveProfile.id,
    raw,
    human,
    derived,
    pending,
  };
}

async function readSource(context, folder, sourceId, options = {}) {
  const store = normalizeStoreHandle(folder, options.storeHandle);
  if (!store.isCurrentStore) await assertStoreIntegrity(context, folder, store);
  const startChar = Math.max(0, Math.trunc(Number(options.startChar || 0)) || 0);
  const maxChars = Math.max(500, Math.min(12000, Math.trunc(Number(options.maxChars || 6000)) || 6000));
  const topicId = String(options.topicId || '').trim();
  const args = ['read', sourceId, '--start-char', String(startChar), '--max-chars', String(maxChars)];
  if (topicId) args.push('--topic', topicId);
  const row = JSON.parse((await runPythonModule(
    context,
    folder,
    'dogfood.llm_wiki.agent_memory_cli',
    args,
    { storeHandle: store }
  )).trim());

  let derived = '';
  try {
    derived = await runPythonModule(
      context,
      folder,
      'dogfood.llm_wiki.agent_wiki_cli',
      ['show', sourceId],
      { storeHandle: store }
    );
  } catch (_) {
    derived = '';
  }
  return { row, derived: derived ? derived.slice(0, 6000) : '', store };
}

module.exports = {
  NAMED_STORE_QUERY_PROFILE_V1,
  QUERY_PROFILE_V1,
  assertStoreIntegrity,
  collectMemoryRows,
  collectQueryEvidence,
  currentStoreHandle,
  isWikiInitialized,
  mergedTargetQuery,
  normalizeStoreHandle,
  parseJsonLines,
  readSource,
  runPythonModule,
  wikiRoot,
};