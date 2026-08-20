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
});

function configuration() {
  return require('vscode').workspace.getConfiguration('llmWiki');
}

function wikiRoot(folder) {
  const value = String(configuration().get('workspaceDirectory', '.wiki-lab') || '.wiki-lab');
  return path.isAbsolute(value) ? value : path.resolve(folder.uri.fsPath, value);
}

function coreRoot(context, folder) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'cli.py'))) return bundled;
  return path.resolve(context.extensionPath, '..', '..');
}

function isWikiInitialized(folder) {
  const root = wikiRoot(folder);
  return fs.existsSync(path.join(root, 'config.json')) && fs.existsSync(path.join(root, 'manifest.jsonl'));
}

async function runPythonModule(context, folder, moduleName, args) {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const root = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH ? `${root}${path.delimiter}${process.env.PYTHONPATH}` : root;
  const fullArgs = ['-m', moduleName, '--root', wikiRoot(folder), ...args];
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
  const [rawStdout, derivedStdout, pendingStdout] = await Promise.all([
    runPythonModule(context, folder, 'dogfood.llm_wiki.cli', ['discover', query, '--top-k-per-topic', '3', '--json']),
    runPythonModule(context, folder, 'dogfood.llm_wiki.agent_wiki_cli', ['search', query, '--top-k', String(derivedLimit), '--json']),
    runPythonModule(context, folder, 'dogfood.llm_wiki.agent_state_cli', ['pending-list']),
  ]);
  return {
    rawRows: parseJsonLines(rawStdout).slice(0, maxResults),
    derivedRows: parseJsonLines(derivedStdout),
    humanRows: humanKnowledge.search(wikiRoot(folder), query, 3),
    pendingRows: parseJsonLines(pendingStdout),
  };
}

function navigationQuery(question, derivedRow) {
  const title = String(derivedRow.title || '').trim();
  const snippet = String(derivedRow.snippet || '').trim().slice(0, 500);
  return [question, title, snippet].filter(Boolean).join('\n');
}

async function collectQueryEvidence(context, folder, question, profile = QUERY_PROFILE_V1) {
  const memory = await collectMemoryRows(context, folder, question, { maxResults: profile.rawDiscoveryLimit });
  const rawHits = memory.rawRows.slice(0, profile.rawDiscoveryLimit);
  const derivedRows = memory.derivedRows.slice(0, profile.derivedLimit);
  const humanRows = memory.humanRows.slice(0, profile.humanLimit);

  const targets = [];
  const seen = new Set();
  const addTarget = (sourceId, topicId, query, equivalentSourceIds = [], objectId = '') => {
    if (!sourceId || seen.has(sourceId) || targets.length >= profile.rawInternalLimit) return;
    seen.add(sourceId);
    targets.push({ sourceId, topicId: String(topicId || '').trim(), query, equivalentSourceIds, objectId });
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
      '--query', target.query,
      '--max-chars', String(profile.relevantRegionChars),
    ];
    if (target.topicId) args.push('--topic', target.topicId);
    let row;
    try {
      row = JSON.parse((await runPythonModule(context, folder, 'dogfood.llm_wiki.agent_memory_cli', args)).trim());
    } catch (error) {
      throw new Error(`query_plane_candidate_verification_failed:${target.sourceId}`);
    }
    if (row.format !== 'llm-wiki-agent-relevant-read-v0' || row.source_id !== target.sourceId) {
      throw new Error(`query_plane_candidate_identity_mismatch:${target.sourceId}`);
    }
    raw.push({
      scope_ref: { kind: 'current_store' },
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
    scope_ref: { kind: 'current_store' },
    id: row.id,
    title: row.title || '',
    statement: row.statement || '',
    reasoning: row.reasoning || '',
    supporting_source_ids: Array.isArray(row.sourceIds) ? row.sourceIds : [],
    supersedes_knowledge_id: row.supersedesKnowledgeId || '',
  }));
  const derived = derivedRows.map((row) => ({
    scope_ref: { kind: 'current_store' },
    source_id: row.source_id,
    topic_id: row.topic_id || '',
    title: row.title || '',
    snippet: row.snippet || '',
  }));
  const pending = memory.pendingRows.slice(0, 5).map((row) => ({
    scope_ref: { kind: 'current_store' },
    decision_id: row.id,
    topic_id: row.topic_id || '',
    predecessor_source_ids: Array.isArray(row.predecessor_source_ids) ? row.predecessor_source_ids : [],
    successor_source_id: row.successor_source_id || '',
  }));

  return {
    question,
    scope: { kind: 'current_store' },
    query_profile: profile.id,
    raw,
    human,
    derived,
    pending,
  };
}

module.exports = {
  QUERY_PROFILE_V1,
  collectMemoryRows,
  collectQueryEvidence,
  isWikiInitialized,
  parseJsonLines,
  runPythonModule,
  wikiRoot,
};