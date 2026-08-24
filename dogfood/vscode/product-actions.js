'use strict';

const path = require('node:path');
const vscode = require('vscode');

const REMEMBER_COMMAND = 'llmWiki.rememberActiveFile';
const REVIEW_CHANGES_COMMAND = 'llmWiki.reviewPendingChanges';
const REMEMBER_TOOL = 'llmWiki_rememberSource';
const SEARCH_TOOL = 'llmWiki_searchMemory';
const RESOLVE_LINEAGE_TOOL = 'llmWiki_resolveLineage';

function toolText(result) {
  if (!result || !Array.isArray(result.content)) return '';
  return result.content
    .map((part) => (part && typeof part.value === 'string' ? part.value : ''))
    .filter(Boolean)
    .join('\n');
}

function field(text, key) {
  const prefix = `${key}=`;
  const line = String(text || '').split(/\r?\n/).find((row) => row.startsWith(prefix));
  return line ? line.slice(prefix.length) : '';
}

function decodeJsonField(value) {
  if (!value) return '';
  try {
    return JSON.parse(value);
  } catch (_) {
    return value;
  }
}

function activeLocalFile(resource) {
  if (resource && resource.scheme === 'file') return resource.fsPath;
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.uri.scheme !== 'file') return undefined;
  return editor.document.uri.fsPath;
}

async function invokeTool(name, input) {
  if (!vscode.lm || typeof vscode.lm.invokeTool !== 'function') {
    throw new Error('This LLM Wiki action requires VS Code 1.95+ Language Model Tool APIs.');
  }
  return vscode.lm.invokeTool(name, { input, toolInvocationToken: undefined });
}

function parsePendingDecisions(text) {
  const lines = String(text || '').split(/\r?\n/);
  const start = lines.indexOf('PENDING_LINEAGE_DECISIONS');
  if (start < 0) return [];
  const rows = [];
  let current;
  for (const line of lines.slice(start + 1)) {
    if (!line || line === 'POLICY') break;
    if (line.startsWith('decision_id=')) {
      if (current && current.id) rows.push(current);
      current = { id: line.slice('decision_id='.length), predecessors: [] };
      continue;
    }
    if (!current) continue;
    if (line.startsWith('workspace_file_json=')) current.workspaceFile = decodeJsonField(line.slice('workspace_file_json='.length));
    else if (line.startsWith('predecessor_source_ids=')) current.predecessors = line.slice('predecessor_source_ids='.length).split(',').filter(Boolean);
    else if (line.startsWith('successor_source_id=')) current.successor = line.slice('successor_source_id='.length);
    else if (line.startsWith('topic_id=')) current.topicId = line.slice('topic_id='.length);
  }
  if (current && current.id) rows.push(current);
  return rows;
}

async function pendingDecisions() {
  const result = await invokeTool(SEARCH_TOOL, {
    query: 'saved file history decisions waiting for review',
    maxResults: 1,
  });
  return parsePendingDecisions(toolText(result));
}

async function rememberActiveFile(context, resource) {
  const filePath = activeLocalFile(resource);
  if (!filePath) {
    vscode.window.showInformationMessage('Open a local project file, then choose Remember in Project Memory.');
    return undefined;
  }

  const result = await invokeTool(REMEMBER_TOOL, { filePath });
  const text = toolText(result);
  if (text.includes('status=CANCELLED_BY_USER')) return text;

  const relativePath = decodeJsonField(field(text, 'workspace_file_json')) || path.basename(filePath);
  const pending = field(text, 'pending_lineage_decision') === 'yes';
  const reused = field(text, 'raw_admission') === 'reused_existing';

  if (pending) {
    const choice = await vscode.window.showInformationMessage(
      `Saved ${relativePath} to project memory. A previous saved version needs one meaning decision.`,
      'Review Change'
    );
    if (choice === 'Review Change') await reviewPendingChanges(context);
  } else if (reused) {
    vscode.window.showInformationMessage(`${relativePath} is already in project memory.`);
  } else {
    vscode.window.showInformationMessage(`Saved ${relativePath} to project memory.`);
  }
  await vscode.commands.executeCommand('llmWiki.refreshOverview');
  return text;
}

async function choosePendingDecision(rows) {
  if (!rows.length) return undefined;
  if (rows.length === 1) return rows[0];
  const picked = await vscode.window.showQuickPick(
    rows.map((row) => ({
      label: path.basename(row.workspaceFile || 'Saved file'),
      description: row.workspaceFile || '',
      detail: 'A newer saved revision is waiting for you to say what the change means.',
      row,
    })),
    {
      title: 'Review saved-file changes',
      placeHolder: 'Choose a file change to review',
      ignoreFocusOut: true,
    }
  );
  return picked && picked.row;
}

async function choosePredecessor(row) {
  if (!row.predecessors || !row.predecessors.length) return undefined;
  if (row.predecessors.length === 1) return row.predecessors[0];
  const picked = await vscode.window.showQuickPick(
    row.predecessors.map((sourceId, index) => ({
      label: `Earlier saved version ${index + 1}`,
      description: sourceId,
      sourceId,
    })),
    {
      title: `Which earlier version of ${path.basename(row.workspaceFile || 'this file')} are you comparing?`,
      placeHolder: 'The next confirmation shows the verified changed text before anything is recorded',
      ignoreFocusOut: true,
    }
  );
  return picked && picked.sourceId;
}

async function chooseRelation() {
  const picked = await vscode.window.showQuickPick([
    {
      label: 'The older version was wrong — this fixes it',
      description: 'Correction',
      value: 'correction',
    },
    {
      label: 'Things changed over time — both were right at different times',
      description: 'Change over time',
      value: 'change',
    },
    {
      label: 'They disagree and this is not resolved yet',
      description: 'Unresolved disagreement',
      value: 'dispute',
    },
    {
      label: 'Use the newer version going forward',
      description: 'Replace the older version without claiming why',
      value: 'supersede',
    },
    {
      label: 'These should stay separate',
      description: 'No historical relation',
      value: 'independent',
    },
  ], {
    title: 'What does this saved-file change mean?',
    placeHolder: 'Choose the meaning; LLM Wiki will show verified old/new evidence before the final confirmation',
    ignoreFocusOut: true,
  });
  return picked && picked.value;
}

async function chooseEffectiveAt() {
  const picked = await vscode.window.showQuickPick([
    {
      label: 'From now',
      description: 'Use the current time as when the newer version became valid',
      value: new Date().toISOString(),
    },
    {
      label: 'Choose a date/time…',
      description: 'Enter a timezone-aware ISO timestamp',
      value: 'custom',
    },
  ], {
    title: 'When did the newer version become valid?',
    ignoreFocusOut: true,
  });
  if (!picked) return undefined;
  if (picked.value !== 'custom') return picked.value;
  return vscode.window.showInputBox({
    title: 'When did the newer version become valid?',
    prompt: 'Enter a timezone-aware ISO timestamp. Example: 2026-08-24T12:30:00+09:00',
    value: new Date().toISOString(),
    ignoreFocusOut: true,
    validateInput: (value) => {
      const text = String(value || '').trim();
      if (!text) return 'A date/time is required.';
      if (!/(?:Z|[+-]\d\d:\d\d)$/.test(text) || Number.isNaN(Date.parse(text))) return 'Use a valid timezone-aware ISO timestamp.';
      return undefined;
    },
  });
}

async function reviewPendingChanges(context) {
  const rows = await pendingDecisions();
  if (!rows.length) {
    vscode.window.showInformationMessage('No saved-file changes are waiting for review.');
    return false;
  }

  const row = await choosePendingDecision(rows);
  if (!row) return undefined;
  const predecessorSourceId = await choosePredecessor(row);
  if (!predecessorSourceId) return undefined;
  const relation = await chooseRelation();
  if (!relation) return undefined;
  const effectiveAt = relation === 'change' ? await chooseEffectiveAt() : undefined;
  if (relation === 'change' && !effectiveAt) return undefined;

  const result = await invokeTool(RESOLVE_LINEAGE_TOOL, {
    decisionId: row.id,
    relation,
    predecessorSourceId,
    ...(effectiveAt ? { effectiveAt } : {}),
  });
  const text = toolText(result);
  if (text.includes('status=CANCELLED_BY_USER')) return false;

  vscode.window.showInformationMessage(`Saved what the change to ${path.basename(row.workspaceFile || 'the file')} means.`);
  await vscode.commands.executeCommand('llmWiki.refreshOverview');
  return true;
}

function registerProductActions(context) {
  context.subscriptions.push(vscode.commands.registerCommand(
    REMEMBER_COMMAND,
    (resource) => rememberActiveFile(context, resource)
  ));
  context.subscriptions.push(vscode.commands.registerCommand(
    REVIEW_CHANGES_COMMAND,
    () => reviewPendingChanges(context)
  ));
}

module.exports = {
  REMEMBER_COMMAND,
  REVIEW_CHANGES_COMMAND,
  parsePendingDecisions,
  pendingDecisions,
  registerProductActions,
  rememberActiveFile,
  reviewPendingChanges,
  toolText,
};
