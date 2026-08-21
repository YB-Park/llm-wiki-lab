'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const vscode = require('vscode');
const memoryRead = require('./memory-read-service');
const { boundedProcessFailure } = require('./process-errors');
const { resolvePythonRuntime } = require('./python-runtime');

const TOOL = 'llmWiki_consultMemory';
const CONFIGURE_COMMAND = 'llmWiki.configureQueryPlane';
const MODEL = 'gpt-5.6-luna';
const GRANT_VERSION = 1;
const MAX_BUFFER = 16 * 1024 * 1024;
const GRANT_KEY_PREFIX = 'llmWiki.queryPlaneGrant.v1';
const USAGE_KEY_PREFIX = 'llmWiki.queryPlaneUsage.v1';

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before using LLM Wiki tools.');
  if (folders.length !== 1) throw new Error('LLM Wiki currently supports one workspace folder at a time. Open the project as a single-folder workspace before using project memory.');
  return folders[0];
}

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
}

function coreRoot(context, folder) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'cli.py'))) return bundled;
  return path.resolve(context.extensionPath, '..', '..');
}

function pythonEnv(context, folder) {
  const root = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH ? `${root}${path.delimiter}${process.env.PYTHONPATH}` : root;
  return { ...process.env, PYTHONPATH: pythonPath };
}

function grantKey(folder) {
  return `${GRANT_KEY_PREFIX}:${folder.uri.toString()}`;
}

function localDayKey() {
  const now = new Date();
  const yyyy = String(now.getFullYear()).padStart(4, '0');
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function usageKey(folder, day = localDayKey()) {
  return `${USAGE_KEY_PREFIX}:${folder.uri.toString()}:${day}`;
}

function queryGrant(context, folder) {
  const row = context.workspaceState.get(grantKey(folder));
  if (!row || row.version !== GRANT_VERSION || row.enabled !== true) return undefined;
  if (row.model !== MODEL || row.scope !== 'current_store' || row.provider !== 'github_copilot') return undefined;
  const dailyCallLimit = Number(row.dailyCallLimit);
  const maxAiCredits = Number(row.maxAiCredits);
  if (!Number.isInteger(dailyCallLimit) || dailyCallLimit < 1 || dailyCallLimit > 100) return undefined;
  if (!Number.isInteger(maxAiCredits) || maxAiCredits < 1 || maxAiCredits > 100) return undefined;
  return { ...row, dailyCallLimit, maxAiCredits };
}

function queryPlaneEnabled(context, folder) {
  return Boolean(queryGrant(context, folder));
}

function queryUsage(context, folder) {
  const day = localDayKey();
  const row = context.workspaceState.get(usageKey(folder, day), {});
  return { day, reservedCalls: Math.max(0, Math.trunc(Number(row.reservedCalls || 0)) || 0) };
}

async function reserveQueryCall(context, folder, grant) {
  const usage = queryUsage(context, folder);
  if (usage.reservedCalls >= grant.dailyCallLimit) {
    return { allowed: false, ...usage, dailyCallLimit: grant.dailyCallLimit, maxAiCredits: grant.maxAiCredits };
  }
  const reservedCalls = usage.reservedCalls + 1;
  await context.workspaceState.update(usageKey(folder, usage.day), { reservedCalls });
  return {
    allowed: true,
    day: usage.day,
    reservedCalls,
    dailyCallLimit: grant.dailyCallLimit,
    maxAiCredits: grant.maxAiCredits,
  };
}

const runComposerStdin = async (context, folder, args, input) => {
  const runtime = await resolvePythonRuntime(folder);
  if (!runtime) throw new Error('python_runtime_not_found');
  const fullArgs = ['-m', 'dogfood.llm_wiki.query_plane_cli', ...args];
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
};

function formatBrief(row, usage) {
  const brief = row && row.brief ? row.brief : {};
  return [
    'LLM_WIKI_BRIEF v2',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    `scope=${row && row.scope && row.scope.kind ? row.scope.kind : 'current_store'}`,
    `query_profile=${row.query_profile || memoryRead.QUERY_PROFILE_V1.id}`,
    `model=${row.model || MODEL}`,
    `model_calls=${Number(row.model_calls || 0)}`,
    `query_reserved_today=${usage && Number(usage.reservedCalls || 0)}`,
    `query_daily_call_limit=${usage && Number(usage.dailyCallLimit || 0)}`,
    `query_max_ai_credits=${usage && Number(usage.maxAiCredits || 0)}`,
    `insufficient_authority=${brief.insufficient_authority === true ? 'true' : 'false'}`,
    `answer_json=${JSON.stringify(String(brief.answer || ''))}`,
    `terminal_refs_json=${JSON.stringify(Array.isArray(brief.terminal_refs) ? brief.terminal_refs : [])}`,
    'policy=Terminal RAW_MEMORY/HUMAN_KNOWLEDGE provenance is retained with scope-qualified refs. DERIVED_MEMORY and pending-lineage state are nonterminal. The internal retrieval/composition trace is intentionally not returned.',
  ].join('\n');
}

function disabledResult() {
  return [
    'LLM_WIKI_BRIEF v2',
    'state=query_plane_disabled',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    'model_calls=0',
    'fallback=none',
    'policy=Do not automatically dump raw Wiki memory into the Main Agent. Query reasoning requires a separate local, revocable workspace grant plus explicit user-chosen daily-call and per-response AI-credit guards.',
  ].join('\n');
}

function budgetBlockedResult(grant, usage) {
  return [
    'LLM_WIKI_BRIEF v2',
    'state=query_plane_budget_paused',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    'model_calls=0',
    'fallback=none',
    `query_reserved_today=${usage.reservedCalls}`,
    `query_daily_call_limit=${grant.dailyCallLimit}`,
    `query_max_ai_credits=${grant.maxAiCredits}`,
    'policy=The local query-reasoning daily call cap has been reached. Do not silently fall back to broad raw Wiki context.',
  ].join('\n');
}

function unavailableResult(error, usage) {
  return [
    'LLM_WIKI_BRIEF v2',
    'state=query_plane_unavailable',
    'authority=read_only_query_result',
    'canonical_mutation=none',
    'model_calls=0_or_failed_attempt',
    'fallback=none',
    `query_reserved_today=${usage && Number(usage.reservedCalls || 0)}`,
    `query_daily_call_limit=${usage && Number(usage.dailyCallLimit || 0)}`,
    `query_max_ai_credits=${usage && Number(usage.maxAiCredits || 0)}`,
    `failure_json=${JSON.stringify(boundedProcessFailure(error && error.message ? error.message : String(error)))}`,
    'policy=Do not automatically fall back by loading broad raw Wiki context into the Main Agent. Continue without Wiki memory or use explicit diagnostic/raw drill-down.',
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
    if (!memoryRead.isWikiInitialized(folder)) {
      return new vscode.LanguageModelToolResult([
        new vscode.LanguageModelTextPart('LLM_WIKI_BRIEF v2\nstate=not_initialized\nauthority=read_only_query_result\ncanonical_mutation=none\nmodel_calls=0'),
      ]);
    }

    const grant = queryGrant(this.context, folder);
    if (!grant) {
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(disabledResult())]);
    }
    const usage = await reserveQueryCall(this.context, folder, grant);
    if (!usage.allowed) {
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(budgetBlockedResult(grant, usage))]);
    }

    try {
      const payload = await memoryRead.collectQueryEvidence(this.context, folder, question);
      const stdout = await runComposerStdin(
        this.context,
        folder,
        ['--model', MODEL, '--max-ai-credits', String(grant.maxAiCredits)],
        JSON.stringify(payload)
      );
      const row = JSON.parse(stdout.trim());
      if (row.format !== 'llm-wiki-query-plane-v1' || row.status !== 'OK') throw new Error('query_plane_result_contract_invalid');
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(formatBrief(row, usage))]);
    } catch (error) {
      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(unavailableResult(error, usage))]);
    }
  }
}

async function configureQueryPlane(context) {
  const folder = firstWorkspaceFolder();
  const current = queryGrant(context, folder);
  if (current) {
    const choice = context.extensionMode === vscode.ExtensionMode.Test
      ? 'Disable Query Reasoning'
      : await vscode.window.showWarningMessage(
        'Disable Luna-backed Wiki query reasoning for this workspace?',
        { modal: true, detail: 'Disabling stops future wikiConsult model calls. Saved Wiki data and existing query usage records are preserved.' },
        'Disable Query Reasoning'
      );
    if (choice === 'Disable Query Reasoning') {
      await context.workspaceState.update(grantKey(folder), undefined);
      if (context.extensionMode !== vscode.ExtensionMode.Test) vscode.window.showInformationMessage('LLM Wiki query reasoning is disabled for this workspace.');
      return false;
    }
    return undefined;
  }

  const choice = context.extensionMode === vscode.ExtensionMode.Test
    ? 'Continue'
    : await vscode.window.showWarningMessage(
      'Enable Luna-backed Wiki query reasoning for this workspace?',
      {
        modal: true,
        detail: 'When enabled, a wikiConsult call may send a bounded set of already-admitted Wiki evidence to GitHub Copilot using exact gpt-5.6-luna for read-only query reasoning. This is separate from AI-summary permission, source admission, Human Knowledge authorship, and canonical history changes. You will choose both a local daily model-call cap and a Copilot per-response AI-credit soft guard next.',
      },
      'Continue'
    );
  if (choice !== 'Continue') return undefined;

  let dailyCallLimit = 1;
  let maxAiCredits = 1;
  if (context.extensionMode !== vscode.ExtensionMode.Test) {
    const rawDaily = await vscode.window.showInputBox({
      title: 'LLM Wiki: Query reasoning daily call cap',
      prompt: 'Choose the maximum number of model-backed wikiConsult attempts allowed today in this workspace. This is a local safety cap, not a billing estimate.',
      placeHolder: 'Enter an integer from 1 to 100',
      ignoreFocusOut: true,
      validateInput: (value) => {
        const number = Number(value);
        return Number.isInteger(number) && number >= 1 && number <= 100 ? undefined : 'Enter an integer from 1 to 100.';
      },
    });
    if (rawDaily === undefined) return undefined;
    dailyCallLimit = Number(rawDaily);

    const rawCredits = await vscode.window.showInputBox({
      title: 'LLM Wiki: Query reasoning per-response AI-credit guard',
      prompt: 'Choose the Copilot CLI soft maximum AI credits for each wikiConsult response. This is a provider usage/cost guard, not an exact bill; LLM Wiki does not choose a default for you.',
      placeHolder: 'Enter an integer from 1 to 100',
      ignoreFocusOut: true,
      validateInput: (value) => {
        const number = Number(value);
        return Number.isInteger(number) && number >= 1 && number <= 100 ? undefined : 'Enter an integer from 1 to 100.';
      },
    });
    if (rawCredits === undefined) return undefined;
    maxAiCredits = Number(rawCredits);
  }

  const grant = {
    version: GRANT_VERSION,
    enabled: true,
    provider: 'github_copilot',
    model: MODEL,
    scope: 'current_store',
    evidenceExposure: 'retrieved_admitted_memory_only',
    dailyCallLimit,
    maxAiCredits,
  };
  await context.workspaceState.update(grantKey(folder), grant);
  if (context.extensionMode !== vscode.ExtensionMode.Test) vscode.window.showInformationMessage('LLM Wiki query reasoning is enabled locally for this workspace.');
  return true;
}

function registerQueryPlaneCommand(context) {
  context.subscriptions.push(vscode.commands.registerCommand(CONFIGURE_COMMAND, () => configureQueryPlane(context)));
}

function registerQueryPlaneTool(context) {
  if (!vscode.lm || typeof vscode.lm.registerTool !== 'function') {
    throw new Error('LLM Wiki Query Plane requires the stable VS Code Language Model Tool API (VS Code 1.95+).');
  }
  context.subscriptions.push(vscode.lm.registerTool(TOOL, new WikiConsultTool(context)));
}

module.exports = {
  CONFIGURE_COMMAND,
  GRANT_VERSION,
  MODEL,
  TOOL,
  WikiConsultTool,
  budgetBlockedResult,
  configureQueryPlane,
  disabledResult,
  formatBrief,
  grantKey,
  queryGrant,
  queryPlaneEnabled,
  queryUsage,
  registerQueryPlaneCommand,
  registerQueryPlaneTool,
  reserveQueryCall,
  unavailableResult,
};
