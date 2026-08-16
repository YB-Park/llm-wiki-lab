'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const FORMAT = 'llm-wiki-human-knowledge-v1';
const REQUIRED_KEYS = new Set([
  'format', 'id', 'title', 'statement', 'reasoning', 'sourceIds',
  'supersedesKnowledgeId', 'authorship', 'createdAt', 'integritySha256',
]);

function rootFor(wikiRoot) {
  return path.join(wikiRoot, 'human-knowledge');
}

function privateMkdir(dir) {
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  try { fs.chmodSync(dir, 0o700); } catch (_) {}
}

function privateAtomicWrite(target, text) {
  privateMkdir(path.dirname(target));
  const temp = `${target}.tmp-${process.pid}-${crypto.randomBytes(6).toString('hex')}`;
  fs.writeFileSync(temp, text, { encoding: 'utf8', mode: 0o600 });
  fs.renameSync(temp, target);
  try { fs.chmodSync(target, 0o600); } catch (_) {}
}

function integrityPayload(record) {
  return JSON.stringify([
    record.format,
    record.id,
    record.title,
    record.statement,
    record.reasoning,
    record.sourceIds,
    record.supersedesKnowledgeId,
    record.authorship,
    record.createdAt,
  ]);
}

function integrityFor(record) {
  return crypto.createHash('sha256').update(integrityPayload(record), 'utf8').digest('hex');
}

function validateRecord(record, filename) {
  if (!record || typeof record !== 'object' || Array.isArray(record)) {
    throw new Error(`Human Knowledge corruption detected (${filename}): record is not an object.`);
  }
  const keys = Object.keys(record);
  if (keys.length !== REQUIRED_KEYS.size || keys.some((key) => !REQUIRED_KEYS.has(key))) {
    throw new Error(`Human Knowledge corruption detected (${filename}): record shape is invalid.`);
  }
  if (
    record.format !== FORMAT
    || typeof record.id !== 'string' || !/^hk-[0-9]+-[0-9a-f]+$/.test(record.id)
    || typeof record.title !== 'string'
    || typeof record.statement !== 'string' || !record.statement.trim()
    || typeof record.reasoning !== 'string'
    || !Array.isArray(record.sourceIds) || record.sourceIds.some((value) => typeof value !== 'string')
    || typeof record.supersedesKnowledgeId !== 'string'
    || record.authorship !== 'user_confirmed'
    || typeof record.createdAt !== 'string'
    || typeof record.integritySha256 !== 'string'
  ) {
    throw new Error(`Human Knowledge corruption detected (${filename}): field validation failed.`);
  }
  if (record.integritySha256 !== integrityFor(record)) {
    throw new Error(`Human Knowledge integrity failure (${filename}).`);
  }
  return record;
}

function allRows(wikiRoot) {
  const root = rootFor(wikiRoot);
  if (!fs.existsSync(root)) return [];
  const rows = [];
  for (const name of fs.readdirSync(root).filter((value) => value.endsWith('.json')).sort()) {
    const filePath = path.join(root, name);
    let parsed;
    try {
      parsed = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (error) {
      throw new Error(`Human Knowledge corruption detected (${name}): unreadable JSON.`);
    }
    rows.push(validateRecord(parsed, name));
  }
  const byId = new Map();
  for (const row of rows) {
    if (byId.has(row.id)) throw new Error(`Human Knowledge corruption detected: duplicate id ${row.id}.`);
    byId.set(row.id, row);
  }
  for (const row of rows) {
    if (row.supersedesKnowledgeId && !byId.has(row.supersedesKnowledgeId)) {
      throw new Error(`Human Knowledge lineage failure: ${row.id} supersedes missing ${row.supersedesKnowledgeId}.`);
    }
    if (row.supersedesKnowledgeId === row.id) {
      throw new Error(`Human Knowledge lineage failure: ${row.id} cannot supersede itself.`);
    }
  }
  return rows;
}

function currentRows(wikiRoot) {
  const rows = allRows(wikiRoot);
  const superseded = new Set(rows.map((row) => row.supersedesKnowledgeId).filter(Boolean));
  return rows.filter((row) => !superseded.has(row.id));
}

function tokens(text) {
  return (String(text || '').toLocaleLowerCase().match(/[\p{L}\p{N}_-]+/gu) || []).filter(Boolean);
}

function search(wikiRoot, query, topK = 3) {
  const qtokens = [...new Set(tokens(query))];
  if (!qtokens.length) return [];
  return currentRows(wikiRoot)
    .map((row) => {
      const counts = new Map();
      for (const token of tokens(`${row.title}\n${row.statement}\n${row.reasoning}`)) {
        counts.set(token, (counts.get(token) || 0) + 1);
      }
      const score = qtokens.reduce((sum, token) => sum + Math.min(3, counts.get(token) || 0), 0);
      return { ...row, score };
    })
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score || String(b.createdAt).localeCompare(String(a.createdAt)))
    .slice(0, topK);
}

function currentById(wikiRoot, knowledgeId) {
  if (!knowledgeId) return undefined;
  return currentRows(wikiRoot).find((row) => row.id === knowledgeId);
}

function save(wikiRoot, input) {
  const supersedesKnowledgeId = String(input.supersedesKnowledgeId || '').trim();
  if (supersedesKnowledgeId && !currentById(wikiRoot, supersedesKnowledgeId)) {
    throw new Error(`Human Knowledge supersedes target is missing or not current: ${supersedesKnowledgeId}`);
  }
  const id = `hk-${Date.now()}-${crypto.randomBytes(5).toString('hex')}`;
  const record = {
    format: FORMAT,
    id,
    title: input.title,
    statement: input.statement,
    reasoning: input.reasoning,
    sourceIds: input.sourceIds,
    supersedesKnowledgeId,
    authorship: 'user_confirmed',
    createdAt: new Date().toISOString(),
    integritySha256: '',
  };
  record.integritySha256 = integrityFor(record);
  const root = rootFor(wikiRoot);
  const lines = [
    `# ${record.title}`,
    '',
    '> **HUMAN KNOWLEDGE — USER CONFIRMED**',
    '> This record represents wording the user explicitly confirmed for durable personal knowledge. It is not raw external evidence.',
    record.supersedesKnowledgeId ? `> Replaces prior Human Knowledge: \`${record.supersedesKnowledgeId}\`` : '',
    '',
    '## Current statement',
    '',
    record.statement,
    '',
    '## Why / reasoning',
    '',
    record.reasoning || 'No separate reasoning was recorded.',
    '',
    '## Supporting LLM Wiki sources',
    '',
    ...(record.sourceIds.length ? record.sourceIds.map((sourceId) => `- \`${sourceId}\``) : ['- None recorded.']),
    '',
  ].filter((line) => line !== '');

  // Publish Markdown first; JSON is the searchable record and acts as the
  // semantic publication point. A failed JSON write may leave an inspectable
  // orphan Markdown file, but search never treats it as current knowledge.
  privateAtomicWrite(path.join(root, `${id}.md`), `${lines.join('\n')}\n`);
  privateAtomicWrite(path.join(root, `${id}.json`), `${JSON.stringify(record, null, 2)}\n`);
  return record;
}

module.exports = {
  FORMAT,
  allRows,
  currentById,
  currentRows,
  integrityFor,
  save,
  search,
};
