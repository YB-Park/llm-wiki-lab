'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const { parseIngestReceipt, workspaceRelativePath } = require('./product-helpers');

const execFileAsync = promisify(execFile);
const SELECTED_TOPIC_KEY = 'llmWiki.selectedTopic';
const SOURCE_LOCATORS_KEY = 'llmWiki.sourceLocators.v1';
const MAX_BUFFER = 16 * 1024 * 1024;
const SEARCH_TOOL = 'llmWiki_searchMemory';
const REMEMBER_TOOL = 'llmWiki_rememberSource';

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before using LLM Wiki tools.');
  return folders[0];
}

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
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

async function runCli(context, folder, args) {
  const python = String(configuration().get('pythonExecutable', 'python3') || 'python3');
  const root = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH ? `${root}${path.delimiter}${process.env.PYTHONPATH}` : root;
  const fullArgs = ['-m', 'dogfood.llm_wiki.cli', '--root', wikiRoot(folder), ...args];
  try {
    const result = await execFileAsync(python, fullArgs, {
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
    throw new Error(detail);
  }
}

function parseJsonLines(stdout) {
  return String(stdout || '')
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

function parseTopics(stdout) {
  return String(stdout || '')
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      const match = line.match(/^(\S+)\s+(.*)$/);
      if (!match) throw new Error(`Unexpected topic-list row: ${line}`);
      return { id: match[1], label: match[2] };
    });
}

function selectedTopicKey(folder) {
  return `${SELECTED_TOPIC_KEY}:${folder.uri.toString()}`;
}

function sourceLocatorKey(folder) {
  return `${SOURCE_LOCATORS_KEY}:${folder.uri.toString()}`;
}

async function resolveSelectedTopic(context, folder) {
  const all = parseTopics(await runCli(context, folder, ['topic', 'list']));
  if (!all.length) {
    throw new Error('No LLM Wiki topic exists. Create a topic before asking the agent to remember a source.');
  }
  const saved = context.workspaceState.get(selectedTopicKey(folder));
  if (saved && all.some((row) => row.id === saved.id)) return all.find((row) => row.id === saved.id);
  if (all.length === 1) {
    await context.workspaceState.update(selectedTopicKey(folder), all[0]);
    return all[0];
  }
  throw new Error('Multiple LLM Wiki topics exist and none is selected. Run “LLM Wiki: Select Topic” once, then retry the remember request.');
}

function isWikiInitialized(folder) {
  const root = wikiRoot(folder);
  return fs.existsSync(path.join(root, 'config.json')) && fs.existsSync(path.join(root, 'manifest.jsonl'));
}

function normalizeMaxResults(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 5;
  return Math.max(1, Math.min(8, Math.trunc(parsed)));
}

function formatMemoryResult(rows) {
  const lines = [
    'LLM_WIKI_MEMORY_RESULT v1',
    'authority=read_only',
    'scope=current_evidence_across_topics',
    'canonical_mutation=none',
    `candidate_count=${rows.length}`,
    '',
  ];
  rows.forEach((row, index) => {
    const sourceIds = Array.isArray(row.source_ids) && row.source_ids.length ? row.source_ids : [row.source_id].filter(Boolean);
    lines.push(`MEMORY M${index + 1}`);
    lines.push(`topic=${row.topic_label || row.topic_id || ''}`);
    lines.push(`topic_id=${row.topic_id || ''}`);
    lines.push(`source_ids=${sourceIds.join(',')}`);
    lines.push(`object_id=${row.object_id || ''}`);
    lines.push(`name=${row.name || ''}`);
    lines.push(`score=${Number(row.score || 0).toFixed(6)}`);
    lines.push('snippet:');
    lines.push(String(row.snippet || '').trim());
    lines.push('');
  });
  lines.push('POLICY');
  lines.push('- Use only memories that materially help the current user request.');
  lines.push('- source_ids are provenance handles; duplicate source IDs for identical bytes are not independent corroboration.');
  lines.push('- This tool result authorizes reading only. It never authorizes persistence, correction, change, dispute, supersession, or deletion.');
  lines.push('- If the evidence is insufficient or conflicting, preserve that uncertainty in the answer.');
  return lines.join('\n');
}

function resolveWorkspaceFile(folder, requestedPath) {
  let candidate;
  if (requestedPath) {
    if (!path.isAbsolute(requestedPath)) throw new Error('rememberSource.filePath must be an absolute local path.');
    candidate = requestedPath;
  } else {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.uri.scheme !== 'file') {
      throw new Error('No filePath was supplied and there is no active local file to remember.');
    }
    candidate = editor.document.uri.fsPath;
  }

  const workspaceReal = fs.realpathSync(folder.uri.fsPath);
  const fileReal = fs.realpathSync(candidate);
  const relative = workspaceRelativePath(workspaceReal, fileReal);
  if (!relative) throw new Error('LLM Wiki rememberSource only admits files inside the current workspace.');
  const stat = fs.statSync(fileReal);
  if (!stat.isFile()) throw new Error('LLM Wiki rememberSource only admits regular files.');
  return { filePath: fileReal, relativePath: relative };
}

async function rememberLocator(context, folder, sourceId, relativePath, digest) {
  if (!sourceId || !relativePath || !digest) return;
  const key = sourceLocatorKey(folder);
  const current = context.workspaceState.get(key, {});
  await context.workspaceState.update(key, {
    ...current,
    [sourceId]: { relativePath, sha256: digest },
  });
}

class WikiMemorySearchTool {
  constructor(context) {
    this.context = context;
  }

  prepareInvocation(options) {
    const query = String((options.input && options.input.query) || '').trim();
    return { invocationMessage: `Searching current LLM Wiki memory for “${query.slice(0, 80)}”` };
  }

  async invoke(options) {
    const folder = firstWorkspaceFolder();
    const query = String((options.input && options.input.query) || '').trim();
    if (!query) throw new Error('A non-empty memory query is required.');
    if (!isWikiInitialized(folder)) {
      return new vscode.LanguageModelToolResult([
        new vscode.LanguageModelTextPart('LLM_WIKI_MEMORY_RESULT v1\nauthority=read_only\nstate=not_initialized\ncandidate_count=0\ncanonical_mutation=none'),
      ]);
    }
    const maxResults = normalizeMaxResults(options.input && options.input.maxResults);
    const rows = parseJsonLines(await runCli(this.context, folder, ['discover', query, '--top-k-per-topic', '3', '--json']))
      .slice(0, maxResults);
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(formatMemoryResult(rows)),
    ]);
  }
}

class WikiRememberSourceTool {
  constructor(context) {
    this.context = context;
  }

  prepareInvocation(options) {
    const requested = String((options.input && options.input.filePath) || '').trim();
    const target = requested || 'the active editor file';
    return {
      invocationMessage: `Remembering ${target} in LLM Wiki`,
      confirmationMessages: {
        title: 'Remember source in LLM Wiki?',
        message: `This admits **${target}** as immutable raw evidence in the currently selected LLM Wiki topic. It does not authorize correction/change/dispute, Human Knowledge authorship, deletion, or a model call.`,
      },
    };
  }

  async invoke(options) {
    const folder = firstWorkspaceFolder();
    const requestedPath = String((options.input && options.input.filePath) || '').trim();
    const target = resolveWorkspaceFile(folder, requestedPath || undefined);
    const active = vscode.window.activeTextEditor;
    if (active && active.document.uri.scheme === 'file' && path.resolve(active.document.uri.fsPath) === path.resolve(target.filePath) && active.document.isDirty) {
      const saved = await active.document.save();
      if (!saved) throw new Error('The active file could not be saved, so LLM Wiki did not ingest it.');
    }

    await runCli(this.context, folder, ['init']);
    const topic = await resolveSelectedTopic(this.context, folder);
    const stdout = await runCli(this.context, folder, ['ingest', target.filePath, '--topic', topic.id]);
    const receipt = parseIngestReceipt(stdout);
    if (!receipt) throw new Error('LLM Wiki ingest completed without a parseable source receipt.');
    await rememberLocator(this.context, folder, receipt.sourceId, target.relativePath, receipt.sha256);

    const text = [
      'LLM_WIKI_REMEMBER_RESULT v1',
      'authority=explicit_source_admission',
      `topic=${topic.label}`,
      `topic_id=${topic.id}`,
      `source_id=${receipt.sourceId}`,
      `sha256=${receipt.sha256}`,
      `workspace_file=${target.relativePath}`,
      'model_calls=0',
      'human_authorship_persisted=no',
      'canonical_semantic_mutation=none',
      'derived_agent_wiki_maintenance=not_run_in_slice_1',
      '',
      'The source is admitted as raw/provenance evidence because the user explicitly asked to remember it. Do not reinterpret this admission as correction, change, dispute, supersession, or a durable statement of the user’s belief.',
    ].join('\n');
    return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(text)]);
  }
}

function registerAgentTools(context) {
  if (!vscode.lm || typeof vscode.lm.registerTool !== 'function') {
    throw new Error('LLM Wiki Agent tools require the stable VS Code Language Model Tool API (VS Code 1.95+).');
  }
  context.subscriptions.push(vscode.lm.registerTool(SEARCH_TOOL, new WikiMemorySearchTool(context)));
  context.subscriptions.push(vscode.lm.registerTool(REMEMBER_TOOL, new WikiRememberSourceTool(context)));
}

module.exports = {
  REMEMBER_TOOL,
  SEARCH_TOOL,
  formatMemoryResult,
  normalizeMaxResults,
  registerAgentTools,
};
