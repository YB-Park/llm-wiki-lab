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
let doctorOutput;
let baseSurfaceRegistered = false;
let agentToolDisposables = [];
let agentToolsRegistered = false;

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before using LLM Wiki.');
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
    throw new Error('LLM Wiki is not enabled for this workspace. Run LLM Wiki: Initialize Workspace first.');
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

async function lifecycleConfirm(context, message, button) {
  if (context.extensionMode === vscode.ExtensionMode.Test) return true;
  const choice = await vscode.window.showWarningMessage(message, { modal: true }, button);
  return choice === button;
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
  await setWorkspaceToolContext(enabled);
}

async function refreshWorkspaceRuntimeAvailability(context) {
  const folders = vscode.workspace.workspaceFolders || [];
  const enabled = folders.length > 0 && workspaceActivation.isWorkspaceEnabled(wikiRoot(folders[0]));
  await applyWorkspaceRuntimeAvailability(context, enabled);
  return enabled;
}

async function initializeWorkspace(context) {
  const folder = firstWorkspaceFolder();
  const root = wikiRoot(folder);
  if (workspaceActivation.isWorkspaceEnabled(root)) {
    await applyWorkspaceRuntimeAvailability(context, true);
    vscode.window.showInformationMessage('LLM Wiki is already initialized and enabled for this workspace.');
    return true;
  }

  const storePresent = workspaceActivation.hasWorkspaceState(root);
  const existingStore = workspaceActivation.isCoreInitialized(root);
  if (storePresent && !existingStore) {
    await applyWorkspaceRuntimeAvailability(context, false);
    vscode.window.showWarningMessage(
      'LLM Wiki initialization was not performed because an incomplete or damaged Wiki store already exists. Run Doctor and restore/repair the store boundary explicitly; Initialize Workspace will not recreate missing canonical state.'
    );
    return false;
  }

  const gitSafety = await classifyGitSafety(folder.uri.fsPath, root);
  if (gitSafety === 'UNPROTECTED') {
    vscode.window.showWarningMessage(
      'LLM Wiki initialization was not performed because the Wiki directory is not protected from this Git repository. Add .wiki-lab/ to .git/info/exclude (local only) or .gitignore, then run Initialize Workspace again.'
    );
    await applyWorkspaceRuntimeAvailability(context, false);
    return false;
  }

  const python = pythonExecutable(folder);
  const pythonReady = await executableAvailable(python, ['--version'], folder.uri.fsPath);
  if (!pythonReady) {
    vscode.window.showWarningMessage(`LLM Wiki initialization was not performed because the configured Python executable is unavailable: ${python}`);
    await applyWorkspaceRuntimeAvailability(context, false);
    return false;
  }

  const confirmed = await lifecycleConfirm(
    context,
    existingStore
      ? 'Enable LLM Wiki for this workspace? An existing local Wiki store was found. This explicit opt-in makes the LLM Wiki runtime and five Agent tools available in this workspace. Doctor remains diagnostic only and no model call is made by initialization.'
      : 'Initialize and enable LLM Wiki for this workspace? This creates a private local Wiki store and makes the LLM Wiki runtime and five Agent tools available in this workspace. Doctor remains diagnostic only and no model call is made by initialization.',
    'Initialize LLM Wiki'
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
  vscode.window.showInformationMessage('LLM Wiki initialized and enabled for this workspace. Agent memory tools are now available.');
  return true;
}

async function disableWorkspace(context) {
  const folder = firstWorkspaceFolder();
  const root = wikiRoot(folder);
  if (!workspaceActivation.readWorkspaceOptIn(root)) {
    await applyWorkspaceRuntimeAvailability(context, false);
    vscode.window.showInformationMessage('LLM Wiki integration is already disabled for this workspace. Stored Wiki data was not changed.');
    return false;
  }

  const confirmed = await lifecycleConfirm(
    context,
    'Disable LLM Wiki for this workspace? Agent tools will become unavailable and operational commands will be hidden, but the local Wiki data will be preserved.',
    'Disable LLM Wiki'
  );
  if (!confirmed) return false;

  workspaceActivation.disableWorkspace(root);
  await applyWorkspaceRuntimeAvailability(context, false);
  vscode.window.showInformationMessage('LLM Wiki disabled for this workspace. Stored Wiki data was preserved.');
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
  doctorOutput.appendLine('LLM Wiki Doctor');
  doctorOutput.appendLine('Model calls: 0');
  doctorOutput.appendLine('State changes: 0');
  doctorOutput.appendLine(`Workspace store: ${storeLabel}`);
  doctorOutput.appendLine(`Workspace opt-in: ${workspaceEnabled ? 'ENABLED' : 'NOT_ENABLED'}`);
  doctorOutput.appendLine(`Agent tools: ${workspaceEnabled ? 'AVAILABLE' : 'HIDDEN'}`);
  doctorOutput.appendLine(`Operational commands: ${workspaceEnabled ? 'AVAILABLE' : 'DISABLED'}`);
  doctorOutput.appendLine(`Python: ${pythonReady ? 'PASS' : 'FAIL'}`);
  doctorOutput.appendLine(`Core: ${coreReady ? 'PASS' : (storePresent ? 'FAIL' : 'NOT_INITIALIZED')} mode=${coreMode(context)}`);
  doctorOutput.appendLine(`Compiled provider: ${compiledDisabled ? 'disabled' : (storePresent ? 'CHECK_FAILED' : 'NOT_CHECKED')}`);
  doctorOutput.appendLine(`Raw integrity: ${!storePresent ? 'NOT_CHECKED' : (rawIntegrityStatus === 'clean' ? 'PASS' : 'FAIL')} status=${rawIntegrityStatus}`);
  doctorOutput.appendLine(
    `Canonical logs: ${!storePresent ? 'NOT_CHECKED' : (manifestIntegrityStatus === 'clean' && provenanceIntegrityStatus === 'clean' ? 'PASS' : 'FAIL')} ` +
    `manifest=${manifestIntegrityStatus} provenance=${provenanceIntegrityStatus}`
  );
  doctorOutput.appendLine(`Git raw-store safety: ${gitSafety}`);
  doctorOutput.appendLine(`Copilot CLI: ${copilotReady ? 'PASS' : 'NOT_FOUND'}`);
  doctorOutput.appendLine(`Local raw/search/provenance: ${localReady ? 'READY' : 'UNAVAILABLE'}`);
  doctorOutput.appendLine(`Realistic evidence dogfood: ${realisticDogfoodReady ? 'READY' : 'BLOCKED'}`);
  doctorOutput.appendLine(`Ask Luna: ${askReady ? 'READY' : 'UNAVAILABLE'}`);
  doctorOutput.appendLine(`Agent Wiki maintenance: ${maintenanceOn ? 'ENABLED' : 'DISABLED'} model=gpt-5.6-luna guard=${maintenanceGuard}`);
  doctorOutput.show(true);

  if (!storePresent) {
    vscode.window.showInformationMessage('LLM Wiki Doctor: this workspace is not initialized. Doctor made no changes. Run LLM Wiki: Initialize Workspace to opt in.');
  } else if (!storeInitialized) {
    vscode.window.showWarningMessage('LLM Wiki Doctor: an incomplete or damaged local Wiki store exists. Doctor made no changes. Do not reinitialize over it; inspect integrity/backup state.');
  } else if (!workspaceEnabled) {
    vscode.window.showInformationMessage('LLM Wiki Doctor: a local Wiki store exists, but workspace integration is not explicitly enabled. Doctor made no changes. Run Initialize Workspace to opt in.');
  } else if (coreReady && !integrityReady) {
    vscode.window.showWarningMessage(
      'LLM Wiki Doctor: local integrity check failed. No repair was attempted; inspect the Doctor output before using this Wiki.'
    );
  } else if (localReady && !gitSafeForEvidence) {
    vscode.window.showWarningMessage(
      'LLM Wiki Doctor: local core is ready, but the local wiki store is not protected from this Git workspace. Do not ingest sensitive evidence until Git protection is configured.'
    );
  } else if (localReady) {
    const suffix = copilotReady ? 'Ask Luna is also ready.' : 'Local Wiki is ready; install/authenticate Copilot CLI only when you want Ask Luna.';
    vscode.window.showInformationMessage(`LLM Wiki Doctor: local core ready. ${suffix}`);
  } else {
    vscode.window.showWarningMessage('LLM Wiki Doctor: local core is not ready. Open the LLM Wiki Doctor output for the failing boundary.');
  }

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
  vscode.window.showInformationMessage(
    'LLM Wiki opened a human-owned draft. Save it where you want; ingest remains a separate explicit action.'
  );
  return doc;
}

async function configureAgentWikiMaintenance() {
  requireWorkspaceEnabled();
  const config = configuration();
  const enabled = config.get('agentWikiMaintenanceEnabled', false) === true;
  const action = await vscode.window.showQuickPick(
    [
      { label: 'Enable Agent Wiki maintenance for this workspace', value: true },
      { label: 'Disable Agent Wiki maintenance for this workspace', value: false },
    ],
    {
      title: 'LLM Wiki: Configure Agent Wiki Maintenance',
      placeHolder: enabled ? 'Currently enabled' : 'Currently disabled',
      ignoreFocusOut: true,
    }
  );
  if (!action) return undefined;

  if (action.value) {
    const guard = Number(config.get('agentWikiMaintenanceMaxAiCredits', 30));
    const choice = await vscode.window.showWarningMessage(
      `Enable Agent Wiki maintenance for this workspace? After you explicitly remember a source, its admitted bytes may be sent to exact gpt-5.6-luna to create/reuse a noncanonical, rebuildable derived note. Per-call AI-credit guard: ${guard}. Raw evidence/Human Knowledge/canonical correction-change-dispute semantics remain outside this grant.`,
      { modal: true },
      'Enable Maintenance'
    );
    if (choice !== 'Enable Maintenance') return undefined;
  }

  await config.update('agentWikiMaintenanceEnabled', action.value, vscode.ConfigurationTarget.Workspace);
  vscode.window.showInformationMessage(
    action.value
      ? 'LLM Wiki Agent Wiki maintenance enabled for this workspace. It runs only after explicit source admission.'
      : 'LLM Wiki Agent Wiki maintenance disabled for this workspace. Remember still captures raw evidence without model maintenance.'
  );
  return action.value;
}

async function commandBoundary(label, fn) {
  try {
    return await fn();
  } catch (error) {
    const detail = error && error.message ? error.message : String(error);
    vscode.window.showErrorMessage(`LLM Wiki ${label} failed: ${detail}`);
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

  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.enableWorkspace', () => commandBoundary('Initialize Workspace', () => initializeWorkspace(context))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.disableWorkspace', () => commandBoundary('Disable Workspace', () => disableWorkspace(context))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.newKnowledgeNote', (options) => commandBoundary('New Human Knowledge Note', () => newHumanKnowledgeNote(options || {}))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.configureAgentWikiMaintenance', () => commandBoundary('Configure Agent Wiki Maintenance', () => configureAgentWikiMaintenance())));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => commandBoundary('Doctor', () => doctor(context))));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.experimentalDiscoverCopilotModels', () => commandBoundary('Discover Copilot Models', () => discoverModels())));
}

function deactivate() {
  unregisterAgentTools();
  base.deactivate();
}

module.exports = { activate, deactivate };
