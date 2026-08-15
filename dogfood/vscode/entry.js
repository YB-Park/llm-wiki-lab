'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const base = require('./extension');
const { registerAgentTools } = require('./agent-tools');
const { classifyGitSafety } = require('./git-safety');
const { discoverCopilotModels } = require('./lm-discovery');

const execFileAsync = promisify(execFile);
let doctorOutput;

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before running LLM Wiki Doctor.');
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

async function alphaIntegrity(context, folder) {
  const core = coreRoot(context, folder);
  const result = await execFileAsync(
    pythonExecutable(folder),
    ['-m', 'dogfood.llm_wiki.cli', '--root', wikiRoot(folder), 'integrity'],
    {
      cwd: core,
      windowsHide: true,
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    }
  );
  return JSON.parse(String(result.stdout || ''));
}

async function doctor(context) {
  const folder = firstWorkspaceFolder();
  const python = pythonExecutable(folder);
  const root = wikiRoot(folder);
  const pythonReady = await executableAvailable(python, ['--version'], folder.uri.fsPath);

  if (pythonReady) await vscode.commands.executeCommand('llmWiki.init');

  let coreReady = false;
  let compiledDisabled = false;
  try {
    const config = JSON.parse(fs.readFileSync(path.join(root, 'config.json'), 'utf8'));
    coreReady = pythonReady && config.format === 'llm-wiki-dogfood-v0';
    compiledDisabled = config.compiled_provider === 'disabled';
  } catch (_) {
    coreReady = false;
  }

  let integrityReady = false;
  let rawIntegrityStatus = 'not_checked';
  let manifestIntegrityStatus = 'not_checked';
  let provenanceIntegrityStatus = 'not_checked';
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
  const localReady = coreReady && compiledDisabled && integrityReady;
  const askReady = localReady && copilotReady;
  const realisticDogfoodReady = localReady && gitSafeForEvidence;
  const maintenanceOn = configuration().get('agentWikiMaintenanceEnabled', false) === true;
  const maintenanceGuard = Number(configuration().get('agentWikiMaintenanceMaxAiCredits', 30));

  doctorOutput.clear();
  doctorOutput.appendLine('LLM Wiki Doctor');
  doctorOutput.appendLine('Model calls: 0');
  doctorOutput.appendLine(`Python: ${pythonReady ? 'PASS' : 'FAIL'}`);
  doctorOutput.appendLine(`Core: ${coreReady ? 'PASS' : 'FAIL'} mode=${coreMode(context)}`);
  doctorOutput.appendLine(`Compiled provider: ${compiledDisabled ? 'disabled' : 'CHECK_FAILED'}`);
  doctorOutput.appendLine(`Raw integrity: ${rawIntegrityStatus === 'clean' ? 'PASS' : 'FAIL'} status=${rawIntegrityStatus}`);
  doctorOutput.appendLine(
    `Canonical logs: ${manifestIntegrityStatus === 'clean' && provenanceIntegrityStatus === 'clean' ? 'PASS' : 'FAIL'} ` +
    `manifest=${manifestIntegrityStatus} provenance=${provenanceIntegrityStatus}`
  );
  doctorOutput.appendLine(`Git raw-store safety: ${gitSafety}`);
  doctorOutput.appendLine(`Copilot CLI: ${copilotReady ? 'PASS' : 'NOT_FOUND'}`);
  doctorOutput.appendLine(`Local raw/search/provenance: ${localReady ? 'READY' : 'UNAVAILABLE'}`);
  doctorOutput.appendLine(`Realistic evidence dogfood: ${realisticDogfoodReady ? 'READY' : 'BLOCKED'}`);
  doctorOutput.appendLine(`Ask Luna: ${askReady ? 'READY' : 'UNAVAILABLE'}`);
  doctorOutput.appendLine(`Agent Wiki maintenance: ${maintenanceOn ? 'ENABLED' : 'DISABLED'} model=gpt-5.6-luna guard=${maintenanceGuard}`);
  doctorOutput.show(true);

  if (coreReady && !integrityReady) {
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
  firstWorkspaceFolder();
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

async function activate(context) {
  await base.activate(context);
  registerAgentTools(context);
  doctorOutput = vscode.window.createOutputChannel('LLM Wiki Doctor');
  context.subscriptions.push(doctorOutput);
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.newKnowledgeNote', (options) => newHumanKnowledgeNote(options || {})));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.configureAgentWikiMaintenance', () => configureAgentWikiMaintenance()));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => doctor(context)));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.experimentalDiscoverCopilotModels', () => discoverModels()));
}

function deactivate() {
  return base.deactivate();
}

module.exports = { activate, deactivate };
