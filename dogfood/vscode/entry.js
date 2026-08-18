'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const base = require('./extension');
const { registerAgentTools } = require('./agent-tools');
const { classifyGitSafety } = require('./git-safety');
const workspaceActivation = require('./workspace-activation');
const { discoverCopilotModels } = require('./lm-discovery');

const execFileAsync = promisify(execFile);
const WORKSPACE_ENABLED_CONTEXT = 'llmWiki.workspaceEnabled';
const AGENT_TOOL_COUNT = 5;
const MULTI_ROOT_MESSAGE = 'LLM Wiki currently supports one workspace folder at a time. Open the project as a single-folder workspace before using project memory.';
let doctorOutput;
let baseSurfaceRegistered = false;
let agentToolDisposables = [];
let agentToolsRegistered = false;

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before using LLM Wiki.');
  if (folders.length !== 1) throw new Error(MULTI_ROOT_MESSAGE);
  return folders[0];
}

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
}

function wikiRoot(folder) {
  const value = String(configuration().get('workspaceDirectory', '.wiki-lab') || '.wiki-lab');
  return path.isAbsolute(value) ? value : path.resolve(folder.uri.fsPath, value);
}

function requireWorkspaceEnabled() {
  const folder = firstWorkspaceFolder();
  if (!workspaceActivation.isWorkspaceEnabled(wikiRoot(folder))) {
    throw new Error('LLM Wiki is not enabled for this workspace. Run LLM Wiki: Set Up Project Memory first.');
  }
  return folder;
}

function coreRoot(context, folder) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) {
    return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  }
  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'cli.py'))) return bundled;
  return path.resolve(context.extensionPath, '..', '..');
}

function pythonExecutable(folder) {
  const configured = String(configuration().get('pythonExecutable', 'python3') || 'python3');
  if (path.isAbsolute(configured) || (!configured.includes('/') && !configured.includes('\\'))) return configured;
  return path.resolve(folder.uri.fsPath, configured);
}

function coreMode(context) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) return 'configured';
  const bundledCli = path.join(context.extensionPath, 'python', 'dogfood', 'llm_wiki', 'cli.py');
  return fs.existsSync(bundledCli) ? 'bundled' : 'development';
}

async function executableAvailable(executable, args, cwd) {
  try {
    await execFileAsync(executable, args, {
      cwd,
      windowsHide: true,
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    });
    return true;
  } catch (_) {
    return false;
  }
}

async function runCoreCommand(context, folder, args) {
  const core = coreRoot(context, folder);
  const result = await execFileAsync(
    pythonExecutable(folder),
    ['-m', 'dogfood.llm_wiki.cli', '--root', wikiRoot(folder), ...args],
    {
      cwd: core,
      windowsHide: true,
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    }
  );
  return String(result.stdout || '');
}

async function alphaIntegrity(context, folder) {
  return JSON.parse(await runCoreCommand(context, folder, ['integrity']));
}

async function setWorkspaceToolContext(enabled) {
  await vscode.commands.executeCommand('setContext', WORKSPACE_ENABLED_CONTEXT, enabled === true);
}

async function lifecycleConfirm(context, message, detail, button) {
  if (context.extensionMode === vscode.ExtensionMode.Test) return true;
  const choice = await vscode.window.showWarningMessage(message, { modal: true, detail }, button);
  return choice === button;
}

async function showSetupAction(message, action) {
  const choice = await vscode.window.showWarningMessage(message, action);
  return choice === action;
}

function ensureBaseSurfaceRegistered(context) {
  if (baseSurfaceRegistered) return;
  base.activate(context);
  baseSurfaceRegistered = true;
}

function ensureAgentToolsRegistered(context) {
  if (agentToolsRegistered) return;
  const before = context.subscriptions.length;
  registerAgentTools(context);
  const added = context.subscriptions.slice(before);
  if (added.length !== AGENT_TOOL_COUNT) {
    for (const disposable of added) disposable.dispose();
    throw new Error(`Expected ${AGENT_TOOL_COUNT} LLM Wiki Agent tool registrations, got ${added.length}.`);
  }
  agentToolDisposables = added;
  agentToolsRegistered = true;
}

function unregisterAgentTools() {
  for (const disposable of agentToolDisposables) disposable.dispose();
  agentToolDisposables = [];
  agentToolsRegistered = false;
}

async function applyWorkspaceRuntimeAvailability(context, enabled) {
  if (enabled) {
    ensureBaseSurfaceRegistered(context);
    ensureAgentToolsRegistered(context);
  } else {
    unregisterAgentTools();
  }
  if (baseSurfaceRegistered && typeof base.setStatusVisible === 'function') {
    base.setStatusVisible(enabled);
  }
  await setWorkspaceToolContext(enabled);
}

async function refreshWorkspaceRuntimeAvailability(context) {
  const folders = vscode.workspace.workspaceFolders || [];
  const enabled = folders.length === 1 && workspaceActivation.isWorkspaceEnabled(wikiRoot(folders[0]));
  await applyWorkspaceRuntimeAvailability(context, enabled);
  return enabled;
}

async function initializeWorkspace(context) {
  const folder = firstWorkspaceFolder();
  const root = wikiRoot(folder);
  if (workspaceActivation.isWorkspaceEnabled(root)) {
    await applyWorkspaceRuntimeAvailability(context, true);
    return true;
  }

  const storePresent = workspaceActivation.hasWorkspaceState(root);
  const existingStore = workspaceActivation.isCoreInitialized(root);
  if (storePresent && !existingStore) {
    await applyWorkspaceRuntimeAvailability(context, false);
    const inspect = await showSetupAction(
      'Project memory cannot be enabled because the existing local memory store is incomplete or damaged. LLM Wiki will not overwrite it.',
      'Check Setup'
    );
    if (inspect) await doctor(context);
    return false;
  }

  const gitSafety = await classifyGitSafety(folder.uri.fsPath, root);
  if (gitSafety === 'UNPROTECTED') {
    vscode.window.showWarningMessage(
      'Project memory is not enabled because its local .wiki-lab/ directory could be committed to Git. Add .wiki-lab/ to .git/info/exclude (this machine) or .gitignore (the project), then run setup again.'
    );
    await applyWorkspaceRuntimeAvailability(context, false);
    return false;
  }

  const python = pythonExecutable(folder);
  const pythonReady = await executableAvailable(python, ['--version'], folder.uri.fsPath);
  if (!pythonReady) {
    const openSettings = await showSetupAction(
      `Project memory needs Python, but “${python}” could not be started. Install Python or choose a different executable in LLM Wiki settings.`,
      'Open Settings'
    );
    if (openSettings) await vscode.commands.executeCommand('workbench.action.openSettings', 'llmWiki.pythonExecutable');
    await applyWorkspaceRuntimeAvailability(context, false);
    return false;
  }

  const confirmed = await lifecycleConfirm(
    context,
    'Enable project memory for this workspace?',
    existingStore
      ? 'An existing local LLM Wiki store was found. Enabling it lets your Agent use that project memory in this workspace. AI summaries remain a separate optional setting. This setup makes no model call.'
      : 'LLM Wiki will create a private local project-memory store and let your Agent use it in this workspace. Only information you explicitly save can become durable memory. AI summaries remain off unless you enable them separately. This setup makes no model call.',
    'Enable Project Memory'
  );
  if (!confirmed) return false;

  await runCoreCommand(context, folder, ['init']);
  const report = await alphaIntegrity(context, folder);
  if (!report || report.ok !== true) {
    await applyWorkspaceRuntimeAvailability(context, false);
    throw new Error('LLM Wiki initialization completed but integrity validation did not pass. Workspace integration was not enabled.');
  }

  workspaceActivation.enableWorkspace(root);
  await applyWorkspaceRuntimeAvailability(context, true);
  return true;
}

async function disableWorkspace(context) {
  const folder = firstWorkspaceFolder();
  const root = wikiRoot(folder);
  if (!workspaceActivation.readWorkspaceOptIn(root)) {
    await applyWorkspaceRuntimeAvailability(context, false);
    return false;
  }

  const confirmed = await lifecycleConfirm(
    context,
    'Disable project memory for this workspace?',
    'Saved LLM Wiki data stays on disk. LLM Wiki stops participating in Agent conversations here until you enable the workspace again.',
    'Disable Project Memory'
  );
  if (!confirmed) return false;

  // Stored Wiki data was preserved. Only the workspace opt-in marker is removed.
  workspaceActivation.disableWorkspace(root);
  await applyWorkspaceRuntimeAvailability(context, false);
  return true;
}

async function doctor(context) {
  const folder = firstWorkspaceFolder();
  const python = pythonExecutable(folder);
  const root = wikiRoot(folder);
  const storePresent = workspaceActivation.hasWorkspaceState(root);
  const storeInitialized = workspaceActivation.isCoreInitialized(root);
  const workspaceEnabled = workspaceActivation.isWorkspaceEnabled(root);
  const configPath = path.join(root, 'config.json');
  const pythonReady = await executableAvailable(python, ['--version'], folder.uri.fsPath);

  let coreReady = false;
  let compiledDisabled = false;
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      coreReady = pythonReady && config.format === 'llm-wiki-dogfood-v0';
      compiledDisabled = config.compiled_provider === 'disabled';
    } catch (_) {
      coreReady = false;
    }
  }

  let integrityReady = false;
  let rawIntegrityStatus = storePresent ? 'check_failed' : 'not_initialized';
  let manifestIntegrityStatus = storePresent ? 'check_failed' : 'not_initialized';
  let provenanceIntegrityStatus = storePresent ? 'check_failed' : 'not_initialized';
  if (coreReady) {
    try {
      const report = await alphaIntegrity(context, folder);
      integrityReady = report && report.ok === true;
      rawIntegrityStatus = String((report.raw && report.raw.status) || 'check_failed');
      manifestIntegrityStatus = String(
        (report.canonical_logs && report.canonical_logs.manifest && report.canonical_logs.manifest.status) || 'check_failed'
      );
      provenanceIntegrityStatus = String(
        (report.canonical_logs && report.canonical_logs.provenance && report.canonical_logs.provenance.status) || 'check_failed'
      );
    } catch (_) {
      integrityReady = false;
      rawIntegrityStatus = 'check_failed';
      manifestIntegrityStatus = 'check_failed';
      provenanceIntegrityStatus = 'check_failed';
    }
  }

  const gitSafety = await classifyGitSafety(folder.uri.fsPath, root);
  const gitSafeForEvidence = gitSafety !== 'UNPROTECTED';
  const copilotReady = await executableAvailable('copilot', ['--version'], folder.uri.fsPath);
  const localReady = storeInitialized && coreReady && compiledDisabled && integrityReady;
  const askReady = localReady && copilotReady;
  const realisticDogfoodReady = localReady && gitSafeForEvidence && workspaceEnabled;
  const maintenanceOn = configuration().get('agentWikiMaintenanceEnabled', false) === true;
  const maintenanceGuard = Number(configuration().get('agentWikiMaintenanceMaxAiCredits', 30));
  const storeLabel = storeInitialized ? 'INITIALIZED' : (storePresent ? 'INCOMPLETE' : 'NOT_INITIALIZED');

  doctorOutput.clear();
  doctorOutput.appendLine('LLM Wiki — Setup & Health');
  doctorOutput.appendLine('Checks only: 0 model calls / 0 state changes');
  doctorOutput.appendLine('Model calls: 0');
  doctorOutput.appendLine('State changes: 0');
  doctorOutput.appendLine('');
  doctorOutput.appendLine(`Project memory: ${workspaceEnabled ? 'ON' : (storeInitialized ? 'OFF' : 'NOT SET UP')}`);
  doctorOutput.appendLine(`Workspace opt-in: ${workspaceEnabled ? 'ENABLED' : 'NOT_ENABLED'}`);
  doctorOutput.appendLine(`Agent tools: ${workspaceEnabled ? 'AVAILABLE' : 'HIDDEN'}`);
  doctorOutput.appendLine(`Local memory store: ${storeLabel}`);
  doctorOutput.appendLine(`Python runtime: ${pythonReady ? 'FOUND' : 'MISSING'}${pythonReady ? '' : ` — configured as ${python}`}`);
  doctorOutput.appendLine(`Local data integrity: ${!storePresent ? 'NOT CHECKED' : (integrityReady ? 'PASS' : 'NEEDS ATTENTION')}`);
  doctorOutput.appendLine(`Git privacy: ${gitSafety === 'UNPROTECTED' ? 'NEEDS ATTENTION — local memory directory is not ignored by Git' : 'PASS'} (${gitSafety})`);
  doctorOutput.appendLine(`AI summaries: ${maintenanceOn ? 'ON' : 'OFF'}`);
  doctorOutput.appendLine(`Copilot CLI executable: ${copilotReady ? 'FOUND' : 'NOT FOUND'}`);
  doctorOutput.appendLine('AI-summary model-call readiness: NOT VERIFIED (this check intentionally makes no model calls)');
  doctorOutput.appendLine('');
  if (!storePresent) {
    doctorOutput.appendLine('Next action: run “LLM Wiki: Set Up Project Memory”.');
  } else if (!storeInitialized || !integrityReady) {
    doctorOutput.appendLine('Next action: inspect or restore the local LLM Wiki store before writing more memory. Setup will not overwrite damaged history.');
  } else if (!gitSafeForEvidence) {
    doctorOutput.appendLine('Next action: add .wiki-lab/ (or your configured memory directory) to .git/info/exclude for a local-only choice, or .gitignore for the project; then run setup again.');
  } else if (!workspaceEnabled) {
    doctorOutput.appendLine('Next action: run “LLM Wiki: Set Up Project Memory” to explicitly enable this workspace.');
  } else if (maintenanceOn && !copilotReady) {
    doctorOutput.appendLine('Next action: local project memory is ready. AI summaries are enabled but need GitHub Copilot CLI installed and authenticated.');
  } else {
    doctorOutput.appendLine('Local project memory is ready. Continue in normal Agent chat.');
  }
  doctorOutput.appendLine('');
  doctorOutput.appendLine('Technical details');
  doctorOutput.appendLine(`Core: ${coreReady ? 'PASS' : (storePresent ? 'FAIL' : 'NOT_INITIALIZED')} mode=${coreMode(context)}`);
  doctorOutput.appendLine(`Core compiled provider: ${compiledDisabled ? 'disabled (expected; not used by AI summaries)' : (storePresent ? 'CHECK_FAILED' : 'NOT_CHECKED')}`);
  doctorOutput.appendLine(`Raw integrity: ${!storePresent ? 'NOT_CHECKED' : (rawIntegrityStatus === 'clean' ? 'PASS' : 'FAIL')} status=${rawIntegrityStatus}`);
  doctorOutput.appendLine(
    `Canonical logs: ${!storePresent ? 'NOT_CHECKED' : (manifestIntegrityStatus === 'clean' && provenanceIntegrityStatus === 'clean' ? 'PASS' : 'FAIL')} ` +
    `manifest=${manifestIntegrityStatus} provenance=${provenanceIntegrityStatus}`
  );
  doctorOutput.appendLine(`AI-summary per-call guard setting: ${maintenanceGuard}`);
  doctorOutput.show(true);

  return {
    storePresent,
    storeInitialized,
    workspaceEnabled,
    pythonReady,
    coreReady,
    compiledDisabled,
    integrityReady,
    rawIntegrityStatus,
    manifestIntegrityStatus,
    provenanceIntegrityStatus,
    gitSafety,
    copilotReady,
    localReady,
    realisticDogfoodReady,
    askReady,
    maintenanceOn,
    maintenanceGuard,
  };
}

async function discoverModels() {
  requireWorkspaceEnabled();
  const report = await discoverCopilotModels();
  const doc = await vscode.workspace.openTextDocument({
    content: `${JSON.stringify(report, null, 2)}\n`,
    language: 'json',
  });
  await vscode.window.showTextDocument(doc, { preview: true });

  if (!report.apiAvailable) {
    vscode.window.showWarningMessage('LLM Wiki LM spike: VS Code Language Model API is unavailable in this session. No generation call was made.');
  } else if (report.selectionStatus === 'ERROR') {
    vscode.window.showWarningMessage('LLM Wiki LM spike: Copilot model discovery failed in this session. No fallback and no generation call were used.');
  } else if (!report.exactLuna.exactMetadataSignal) {
    vscode.window.showWarningMessage('LLM Wiki LM spike: no exact gpt-5.6-luna id/family signal was found. No fallback and no generation call were used.');
  } else {
    vscode.window.showInformationMessage('LLM Wiki LM spike: exact gpt-5.6-luna metadata signal found. Generation calls remain disabled in this discovery step.');
  }

  return report;
}

function humanKnowledgeNoteTemplate(title) {
  return [
    `# ${title}`,
    '',
    '> Human-owned draft. Saving this file does not ingest, promote, or mutate LLM Wiki state.',
    '',
    '## Current statement',
    '',
    'Write what you currently believe, learned, or decided.',
    '',
    '## Why / reasoning',
    '',
    'Capture the reasoning you want your future self to recover.',
    '',
    '## Supporting evidence',
    '',
    '- Add links, filenames, or LLM Wiki source IDs that you personally verified.',
    '',
    '## Open questions',
    '',
    '- What remains uncertain or worth revisiting?',
    '',
  ].join('\n');
}

async function newHumanKnowledgeNote(options = {}) {
  requireWorkspaceEnabled();
  const suppliedTitle = options && typeof options.title === 'string' ? options.title.trim() : '';
  const title = suppliedTitle || await vscode.window.showInputBox({
    title: 'LLM Wiki: New Human Knowledge Note',
    prompt: 'A human-owned Markdown draft. Creating it does not mutate Wiki state.',
    ignoreFocusOut: true,
    validateInput: (value) => (value.trim() ? undefined : 'A note title is required.'),
  });
  if (!title || !title.trim()) return undefined;

  const doc = await vscode.workspace.openTextDocument({
    content: humanKnowledgeNoteTemplate(title.trim()),
    language: 'markdown',
  });
  await vscode.window.showTextDocument(doc, { preview: false });
  return doc;
}

async function configureAgentWikiMaintenance() {
  requireWorkspaceEnabled();
  const config = configuration();
  const enabled = config.get('agentWikiMaintenanceEnabled', false) === true;

  if (!enabled) {
    const guard = Number(config.get('agentWikiMaintenanceMaxAiCredits', 30));
    const choice = await vscode.window.showWarningMessage(
      'Turn on AI summaries for this workspace?',
      {
        modal: true,
        detail: `After you explicitly save a source, LLM Wiki may send that saved content to GitHub Copilot (gpt-5.6-luna) to build a rebuildable summary. Local source evidence and your confirmed decisions remain separate. Preferred per-call guard: ${guard}.`,
      },
      'Turn On AI Summaries'
    );
    if (choice !== 'Turn On AI Summaries') return undefined;
    await config.update('agentWikiMaintenanceEnabled', true, vscode.ConfigurationTarget.Workspace);
    return true;
  }

  const choice = await vscode.window.showInformationMessage(
    'AI summaries are on for this workspace. Local project memory continues to work if you turn them off.',
    'Turn Off AI Summaries'
  );
  if (choice !== 'Turn Off AI Summaries') return undefined;
  await config.update('agentWikiMaintenanceEnabled', false, vscode.ConfigurationTarget.Workspace);
  return false;
}

async function commandBoundary(label, fn) {
  try {
    return await fn();
  } catch (error) {
    const detail = error && error.message ? error.message : String(error);
    if (detail === MULTI_ROOT_MESSAGE) {
      vscode.window.showErrorMessage(MULTI_ROOT_MESSAGE);
      return undefined;
    }
    const choice = await vscode.window.showErrorMessage(
      `LLM Wiki could not complete “${label}”.`,
      'Check Setup'
    );
    if (choice === 'Check Setup' && label !== 'Check Setup and Health') {
      await vscode.commands.executeCommand('llmWiki.doctor');
    }
    return undefined;
  }
}

async function activate(context) {
  doctorOutput = vscode.window.createOutputChannel('LLM Wiki Doctor');
  context.subscriptions.push(doctorOutput);

  await refreshWorkspaceRuntimeAvailability(context);
  context.subscriptions.push(vscode.workspace.onDidChangeWorkspaceFolders(() => {
    void refreshWorkspaceRuntimeAvailability(context);
  }));
  context.subscriptions.push(vscode.workspace.onDidChangeConfiguration((event) => {
    if (event.affectsConfiguration('llmWiki.workspaceDirectory')) void refreshWorkspaceRuntimeAvailability(context);
  }));

  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.enableWorkspace', () => commandBoundary('Set Up Project Memory', () => initializeWorkspace(context))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.disableWorkspace', () => commandBoundary('Disable for This Workspace', () => disableWorkspace(context))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.newKnowledgeNote', (options) => commandBoundary('New Human Knowledge Note', () => newHumanKnowledgeNote(options || {}))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.configureAgentWikiMaintenance', () => commandBoundary('Configure AI Summaries', () => configureAgentWikiMaintenance())));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => commandBoundary('Check Setup and Health', () => doctor(context))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.experimentalDiscoverCopilotModels', () => commandBoundary('Discover Copilot Models', () => discoverModels())));
}

function deactivate() {
  unregisterAgentTools();
  base.deactivate();
}

module.exports = { activate, deactivate };
