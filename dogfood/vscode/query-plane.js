'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile, spawn } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const humanKnowledge = require('./human-knowledge');
const { boundedProcessFailure } = require('./process-errors');
const { resolvePythonRuntime } = require('./python-runtime');

const execFileAsync = promisify(execFile);
const TOOL = 'llmWiki_consultMemory';
const CONFIGURE_COMMAND = 'llmWiki.configureQueryPlane';
const MODEL = 'gpt-5.6-luna';
const MAX_BUFFER = 16 * 1024 * 1024;
const RAW_DISCOVERY_LIMIT = 6;
const RAW_INTERNAL_LIMIT = 8;
const RAW_READ_CHARS = 6000;
const DERIVED_LIMIT = 3;
const HUMAN_LIMIT = 3;

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before using LLM Wiki tools.');
  if (folders.length !== 1) throw new Error('LLM Wiki currently supports one workspace folder at a time.');
  return folders[0];
}

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
}

function queryPlaneEnabled() {
  return configuration().get('queryPlaneEnabled', false) === true;
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

function pythonEnv(context, folder) {
  const root = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH ? `${root}${path.delimiter}${process.env.PYTHONPATH}` : root;
  return { ...process.env, PYTHONPATH: pythonPath };
}

async function runPythonModule(context, folder, moduleName, args) {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const fullArgs = ['-m', moduleName, '--root', wikiRoot(folder), ...args];
  try {
    const result = await execFileAsync(runtime.executable, fullArgs, {
      cwd: folder.uri.fsPath,
      env: pythonEnv(context, folder),
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

async function runPythonModuleStdin(context, folder, moduleName, args, input) {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const fullArgs = ['-m', moduleName, '--root', wikiRoot(folder), ...args];
  return new Promise((resolve, reject) => {
    const child = spawn(runtime.executable, fullArgs, {
      cwd: folder.uri.fsPath,
      env: pythonEnv(context, folder),
      windowsHide: true,
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    const stdout = [];
    const stderr = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let settled = false;

    const finish = (error, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (error) reject(error); else resolve(value);
    };

    const timer = setTimeout(() => {
      child.kill();
      finish(new Error('query_plane_timeout'));
    }, 905000);

    child.stdout.on('data', (chunk) => {
      stdoutBytes += chunk.length;
      if (stdoutBytes > MAX_BUFFER) {
        child.kill();
        finish(new Error('query_plane_stdout_too_large'));
        return;
      }
      stdout.push(chunk);
    });
    child.stderr.on('data', (chunk) => {
      stderrBytes += chunk.length;
      if (stderrBytes <= MAX_BUFFER) stderr.push(chunk);
    });
    child.on('error', (error) => finish(error));
    child.on('close', (code) => {
      const out = Buffer.concat(stdout).toString('utf8');
      const err = Buffer.concat(stderr).toString('utf8');
      if (code !== 0) {
        finish(new Error(boundedProcessFailure(err.trim() || out.trim() || `query_plane_exit_${code}`)));
        return;
      }
      finish(null, out);
    });
    child.stdin.end(input, 'utf8');
  });
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

async function collectQueryPlanePayload(context, folder, question) {
  const [rawStdout, derivedStdout] = await Promise.all([
    runPythonModule(context, folder, 'dogfood.llm_wiki.cli', ['discover', question, '--top-k-per-topic', '3', '--json']),
    runPythonModule(context, folder, 'dogfood.llm_wiki.agent_wiki_cli', ['search', question, '--top-k', String(DERIVED_LIMIT), '--json']),
  ]);
  const rawHits = parseJsonLines(rawStdout).slice(0, RAW_DISCOVERY_LIMIT);
  const derivedRows = parseJsonLines(derivedStdout).slice(0, DERIVED_LIMIT);
  const humanRows = humanKnowledge.search(wikiRoot(folder), question, HUMAN_LIMIT);

  const targets = [];
  const seen = new Set();
  const addTarget = (sourceId, topicId) => {
    if (!sourceId || seen.has(sourceId) || targets.length >= RAW_INTERNAL_LIMIT) return;
    seen.add(sourceId);
    targets.push({ sourceId, topicId: String(topicId || '').trim() });
  };
  rawHits.forEach((row) => addTarget(firstSourceId(row), row.topic_id));
  derivedRows.forEach((row) => addTarget(String(row.source_id || '').trim(), row.topic_id));

  const raw = [];
  for (const target of targets) {
    const args = ['read', target.sourceId, '--start-char', '0', '--max-chars', String(RAW_READ_CHARS)];
    if (target.topicId) args.push('--topic', target.topicId);
    try {
      const row = JSON.parse((await runPythonModule(context, folder, 'dogfood.llm_wiki.agent_memory_cli', args)).trim());
      raw.push({
        source_id: row.source_id,
        topic_id: row.topic_id || target.topicId || '',
        status: row.status || 'unknown',
        contested: row.contested === true,
        name: row.name || '',
        text: row.text || '',
        has_more: row.has_more === true,
      });
    } catch (_) {
      // A damaged/stale individual candidate must not silently become authority.
      // Omit it; the internal worker can return insufficient authority if the
      // remaining verified terminal objects do not establish the proposition.
    }
  }

  const human = humanRows.map((row) => ({
    id: row.id,
    title: row.title || '',
    statement: row.statement || '',
    reasoning: row.reasoning || '',
  }));
  const derived = derivedRows.map((row) => ({
    source_id: row.source_id,
    topic_id: row.topic_id || '',
    title: row.title || '',
    snippet: row.snippet || '',
  }));
  return { question, raw, human, derived };
}

function formatBrief(row) {
  const brief = row && row.brief ? row.brief : {};
  return [
    'LLM_WIKI_BRIEF v1',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    `model=${row.model || MODEL}`,
    `model_calls=${Number(row.model_calls || 0)}`,
    `insufficient_authority=${brief.insufficient_authority === true ? 'true' : 'false'}`,
    `answer_json=${JSON.stringify(String(brief.answer || ''))}`,
    `terminal_refs_json=${JSON.stringify(Array.isArray(brief.terminal_refs) ? brief.terminal_refs : [])}`,
    'policy=Terminal RAW_MEMORY/HUMAN_KNOWLEDGE provenance is retained. DERIVED_MEMORY is never terminal authority. The internal retrieval/composition trace is intentionally not returned.',
  ].join('\n');
}

function disabledResult() {
  return [
    'LLM_WIKI_BRIEF v1',
    'state=query_plane_disabled',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    'model_calls=0',
    'fallback=none',
    'policy=Do not automatically dump raw Wiki memory into the Main Agent. Query reasoning requires the separate workspace grant llmWiki.queryPlaneEnabled.',
  ].join('\n');
}

function unavailableResult(error) {
  return [
    'LLM_WIKI_BRIEF v1',
    'state=query_plane_unavailable',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    'model_calls=0_or_failed_attempt',
    'fallback=none',
    `failure_json=${JSON.stringify(boundedProcessFailure(error && error.message ? error.message : String(error)))}`,
    'policy=Do not automatically fall back by loading broad raw Wiki context into the Main Agent. Continue without Wiki memory or ask the user before diagnostic/raw drill-down.',
  ].join('\n');
}

class WikiConsultTool {
  constructor(context) { this.context = context; }

  prepareInvocation(options) {
    const query = String((options.input && options.input.query) || '').trim();
    return { invocationMessage: `Consulting project memory for “${query.slice(0, 80)}”` };
  }

  async invoke(options) {
    const folder = firstWorkspaceFolder();
    const question = String((options.input && options.input.query) || '').trim();
    if (!question) throw new Error('wikiConsult.query must be a non-empty self-contained question.');
    if (question.length > 2000) throw new Error('wikiConsult.query must be 2000 characters or fewer.');
    if (!isWikiInitialized(folder)) {
      return new vscode.LanguageModelToolResult([
        new vscode.LanguageModelTextPart('LLM_WIKI_BRIEF v1\nstate=not_initialized\nauthority=read_only_query_result\ncanonical_mutation=none\nmodel_calls=0'),
      ]);
    }
    if (!queryPlaneEnabled()) {
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(disabledResult())]);
    }

    try {
      const payload = await collectQueryPlanePayload(this.context, folder, question);
      const stdout = await runPythonModuleStdin(
        this.context,
        folder,
        'dogfood.llm_wiki.query_plane_cli',
        ['--model', MODEL, '--max-ai-credits', '30'],
        JSON.stringify(payload)
      );
      const row = JSON.parse(stdout.trim());
      if (row.format !== 'llm-wiki-query-plane-v0' || row.status !== 'OK') throw new Error('query_plane_result_contract_invalid');
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(formatBrief(row))]);
    } catch (error) {
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(unavailableResult(error))]);
    }
  }
}

async function configureQueryPlane(context) {
  const config = configuration();
  const currentlyEnabled = queryPlaneEnabled();
  if (context.extensionMode === vscode.ExtensionMode.Test) {
    await config.update('queryPlaneEnabled', !currentlyEnabled, vscode.ConfigurationTarget.Workspace);
    return;
  }
  if (currentlyEnabled) {
    const choice = await vscode.window.showWarningMessage(
      'Disable Luna-backed Wiki query reasoning for this workspace?',
      { modal: true, detail: 'Disabling stops future wikiConsult model calls. Saved Wiki data is preserved.' },
      'Disable Query Reasoning'
    );
    if (choice === 'Disable Query Reasoning') {
      await config.update('queryPlaneEnabled', false, vscode.ConfigurationTarget.Workspace);
      vscode.window.showInformationMessage('LLM Wiki query reasoning is disabled for this workspace.');
    }
    return;
  }

  const choice = await vscode.window.showWarningMessage(
    'Enable Luna-backed Wiki query reasoning for this workspace?',
    {
      modal: true,
      detail: 'When enabled, ordinary wikiConsult calls may send retrieved saved Wiki evidence to GitHub Copilot using exact gpt-5.6-luna for read-only query reasoning. This grant does not admit new memory, change Human Knowledge, or authorize canonical mutations.',
    },
    'Enable Query Reasoning'
  );
  if (choice === 'Enable Query Reasoning') {
    await config.update('queryPlaneEnabled', true, vscode.ConfigurationTarget.Workspace);
    vscode.window.showInformationMessage('LLM Wiki query reasoning is enabled for this workspace.');
  }
}

function registerQueryPlane(context) {
  if (!vscode.lm || typeof vscode.lm.registerTool !== 'function') {
    throw new Error('LLM Wiki Query Plane requires the stable VS Code Language Model Tool API (VS Code 1.95+).');
  }
  context.subscriptions.push(vscode.commands.registerCommand(CONFIGURE_COMMAND, () => configureQueryPlane(context)));
  context.subscriptions.push(vscode.lm.registerTool(TOOL, new WikiConsultTool(context)));
}

module.exports = {
  CONFIGURE_COMMAND,
  MODEL,
  TOOL,
  WikiConsultTool,
  collectQueryPlanePayload,
  disabledResult,
  formatBrief,
  queryPlaneEnabled,
  registerQueryPlane,
  unavailableResult,
};
