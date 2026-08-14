'use strict';

const crypto = require('node:crypto');
const path = require('node:path');

function parseIngestReceipt(stdout) {
  const match = String(stdout || '').match(/\bINGEST\s+source=(\S+)\s+object=\S+\s+sha256=([0-9a-f]{64})\b/);
  return match ? { sourceId: match[1], sha256: match[2] } : undefined;
}

function workspaceRelativePath(workspacePath, filePath) {
  const relative = path.relative(workspacePath, filePath);
  if (!relative || relative.startsWith('..' + path.sep) || relative === '..' || path.isAbsolute(relative)) return undefined;
  return relative.split(path.sep).join('/');
}

function resolveWorkspaceRelative(workspacePath, relativePath) {
  const value = String(relativePath || '');
  if (!value || path.isAbsolute(value)) return undefined;
  const target = path.resolve(workspacePath, ...value.split('/'));
  const relative = path.relative(workspacePath, target);
  if (!relative || relative.startsWith('..' + path.sep) || relative === '..' || path.isAbsolute(relative)) return undefined;
  return target;
}

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function locatorForRow(locatorMap, row) {
  const ids = Array.isArray(row && row.source_ids) && row.source_ids.length
    ? row.source_ids
    : [row && row.source_id].filter(Boolean);
  for (const sourceId of ids) {
    const locator = locatorMap && locatorMap[sourceId];
    if (!locator) continue;
    if (locator.sha256 && row.sha256 && locator.sha256 !== row.sha256) continue;
    if (typeof locator.relativePath !== 'string' || !locator.relativePath) continue;
    return { sourceId, relativePath: locator.relativePath, sha256: locator.sha256 || row.sha256 };
  }
  return undefined;
}

module.exports = {
  locatorForRow,
  parseIngestReceipt,
  resolveWorkspaceRelative,
  sha256,
  workspaceRelativePath,
};
