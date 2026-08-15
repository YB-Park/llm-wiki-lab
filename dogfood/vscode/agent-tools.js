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
const AGENT_INBOX_LABEL = 'Agent Inbox';
const AGENT_WIKI_MODEL = 'gpt-5.6-luna';
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

function maintenanceEnabled() {
  return configuration().get('agentWikiMaintenanceEnabled', false) === true;
}

function maintenanceCreditGuard() {
  const raw = Number(configuration().get('agentWikiMaintenanceMaxAiCredits', 30));
  if (!Number.isFinite(raw)) return 30;
  return Math.max(30, Math.min(100, Math.trunc(raw)));
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

async function runPythonModule(context, folder, moduleName, args) {
  const python = String(configuration().get('pythonExecutable', 'python3') || 'python3');
  const root = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH ? `${root}${path.delimiter}${process.env.PYTHONPATH}` : root;
  const fullArgs = ['-m', moduleName, '--root', wikiRoot(folder), ...args];
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

function runCli(context, folder, args) {
  return runPythonModule(context, folder, 'dogfood.llm_wiki.cli', args);
}

function runAgentWikiCli(context, folder, args) {
  return runPythonModule(context, folder, 'dogfood.llm_wiki.agent_wiki_cli', args);
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

async function resolveAdmissionTopic(context, folder) {
  let all = parseTopics(await runCli(context, folder, ['topic', 'list']));
  const saved = context.workspaceState.get(selectedTopicKey(folder));
  if (saved && all.some((row) => row.id === saved.id)) return all.find((row) => row.id === saved.id);
  if (all.length === 1) {
    await context.workspaceState.update(selectedTopicKey(folder), all[0]);
    return all[0];
  }

  let inbox = all.find((row) => row.label === AGENT_INBOX_LABEL);
  if (!inbox) {
    await runCli(context, folder, ['topic', 'add', AGENT_INBOX_LABEL]);
    all = parseTopics(await runCli(context, folder, ['topic', 'list']));
    inbox = [...all].reverse().find((row) => row.label === AGENT_INBOX_LABEL);
  }
  if (!inbox) throw new Error('LLM Wiki could not resolve the deterministic Agent Inbox filing topic.');
  await context.workspaceState.update(selectedTopicKey(folder), inbox);
  return inbox;
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

function formatMemoryResult(rawRows, derivedRows = []) {
  const lines = [
    'LLM_WIKI_MEMORY_RESULT v2',
    'authority=read_only',
    'raw_scope=current_evidence_across_topics',
    'derived_scope=current_source_agent_wiki_notes',
    'canonical_mutation=none',
    `raw_candidate_count=${rawRows.length}`,
    `derived_candidate_count=${derivedRows.length}`,
    '',
  ];
  rawRows.forEach((row, index) => {
    const sourceIds = Array.isArray(row.source_ids) && row.source_ids.length ? row.source_ids : [row.source_id].filter(Boolean);
    lines.push(`RAW_MEMORY R${index + 1}`);
    lines.push('epistemic_status=canonical_raw_evidence');
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
  derivedRows.forEach((row, index) => {
    lines.push(`DERIVED_MEMORY D${index + 1}`);
    lines.push('epistemic_status=derived_noncanonical_agent_wiki');
    lines.push(`topic_id=${row.topic_id || ''}`);
    lines.push(`source_ids=${row.source_id || ''}`);
    lines.push(`title=${row.title || ''}`);
    lines.push(`score=${Number(row.score || 0).toFixed(6)}`);
    lines.push('snippet:');
    lines.push(String(row.snippet || '').trim());
    lines.push('');
  });
  lines.push('POLICY');
  lines.push('- Use only memories that materially help the current user request.');
  lines.push('- RAW_MEMORY is the factual/provenance authority. Duplicate raw source IDs for identical bytes are not independent corroboration.');
  lines.push('- DERIVED_MEMORY is model-generated, noncanonical synthesis/navigation aid. It is not raw evidence, independent corroboration, or Human Knowledge authorship.');
  lines.push('- For load-bearing factual claims surfaced by DERIVED_MEMORY, prefer the underlying current RAW_MEMORY/source provenance and preserve uncertainty/conflict.');
  lines.push('- This tool result authorizes reading only. It never authorizes persistence, correction, change, dispute, supersession, or deletion.');
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
        new vscode.LanguageModelTextPart('LLM_WIKI_MEMORY_RESULT v2\nauthority=read_only\nstate=not_initialized\nraw_candidate_count=0\nderived_candidate_count=0\ncanonical_mutation=none'),
      ]);
    }
    const maxResults = normalizeMaxResults(options.input && options.input.maxResults);
    const [rawStdout, derivedStdout] = await Promise.all([
      runCli(this.context, folder, ['discover', query, '--top-k-per-topic', '3', '--json']),
      runAgentWikiCli(this.context, folder, ['search', query, '--top-k', String(Math.min(3, maxResults)), '--json']),
    ]);
    const rawRows = parseJsonLines(rawStdout).slice(0, maxResults);
    const derivedRows = parseJsonLines(derivedStdout);
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(formatMemoryResult(rawRows, derivedRows)),
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
    const maintenance = maintenanceEnabled();
    const guard = maintenanceCreditGuard();
    const maintenanceText = maintenance
      ? ` Your standing workspace Agent Wiki maintenance grant is ON: after admission, the admitted source bytes may be sent to exact ${AGENT_WIKI_MODEL} to create/reuse a noncanonical derived source note (per-call guard ${guard} AI credits).`
      : ' Agent Wiki model maintenance is OFF, so this invocation makes no model call.';
    return {
      invocationMessage: `Remembering ${target} in LLM Wiki`,
      confirmationMessages: {
        title: 'Remember source in LLM Wiki?',
        message: `This admits ${target} as immutable raw evidence. LLM Wiki reuses the selected topic when available, otherwise files it into deterministic Agent Inbox.${maintenanceText} This never authorizes correction/change/dispute, Human Knowledge inference, supersession, or deletion.`,
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
    const topic = await resolveAdmissionTopic(this.context, folder);
    const stdout = await runCli(this.context, folder, ['ingest', target.filePath, '--topic', topic.id]);
    const receipt = parseIngestReceipt(stdout);
    if (!receipt) throw new Error('LLM Wiki ingest completed without a parseable source receipt.');
    await rememberLocator(this.context, folder, receipt.sourceId, target.relativePath, receipt.sha256);

    let maintenance = {
      status: 'SKIPPED_NO_WORKSPACE_GRANT',
      modelCalls: 0,
      model: '',
      policy: '',
    };
    if (maintenanceEnabled()) {
      try {
        const maintenanceStdout = await runAgentWikiCli(this.context, folder, [
          'build', receipt.sourceId,
          '--topic', topic.id,
          '--model', AGENT_WIKI_MODEL,
          '--max-ai-credits', String(maintenanceCreditGuard()),
          '--allow-model-call',
        ]);
        const row = JSON.parse(maintenanceStdout.trim());
        maintenance = {
          status: String(row.status || 'UNKNOWN'),
          modelCalls: Number(row.model_calls || 0),
          model: String(row.model || AGENT_WIKI_MODEL),
          policy: String(row.policy || ''),
        };
      } catch (error) {
        maintenance = { status: 'FAILED_AFTER_RAW_ADMISSION', modelCalls: 'unknown', model: AGENT_WIKI_MODEL, policy: '' };
        vscode.window.showWarningMessage(
          `LLM Wiki remembered the raw source, but Agent Wiki maintenance failed. Raw admission was preserved. ${error && error.message ? error.message : error}`
        );
      }
    }

    const text = [
      'LLM_WIKI_REMEMBER_RESULT v2',
      'authority=explicit_source_admission',
      `topic=${topic.label}`,
      `topic_id=${topic.id}`,
      `source_id=${receipt.sourceId}`,
      `sha256=${receipt.sha256}`,
      `workspace_file=${target.relativePath}`,
      `model_calls=${maintenance.modelCalls}`,
      `derived_agent_wiki_maintenance=${maintenance.status}`,
      `maintenance_model=${maintenance.model}`,
      `maintenance_policy=${maintenance.policy}`,
      'human_authorship_persisted=no',
      'canonical_semantic_mutation=none',
      '',
      'The source is admitted as raw/provenance evidence because the user explicitly asked to remember it. Filing is organizational only. Any Agent Wiki note is derived/noncanonical/rebuildable and is not raw evidence or Human Knowledge. Do not reinterpret this admission or maintenance as correction, change, dispute, supersession, or a durable statement of the user’s belief.',
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
  AGENT_INBOX_LABEL,
  AGENT_WIKI_MODEL,
  REMEMBER_TOOL,
  SEARCH_TOOL,
  formatMemoryResult,
  maintenanceCreditGuard,
  maintenanceEnabled,
  normalizeMaxResults,
  registerAgentTools,
};
