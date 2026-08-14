'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const base = require('./extension');
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
  const python = String(configuration().get('pythonExecutable', 'python3') || 'python3');
  const core = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH
    ? `${core}${path.delimiter}${process.env.PYTHONPATH}`
    : core;
  const result = await execFileAsync(
    python,
    ['-m', 'dogfood.llm_wiki.cli', '--root', wikiRoot(folder), 'integrity'],
    {
      cwd: folder.uri.fsPath,
      env: { ...process.env, PYTHONPATH: pythonPath },
      windowsHide: true,
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    }
  );
  return JSON.parse(String(result.stdout || ''));
}

async function doctor(context) {
  const folder = firstWorkspaceFolder();
  const python = String(configuration().get('pythonExecutable', 'python3') || 'python3');
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

async function activate(context) {
  await base.activate(context);
  doctorOutput = vscode.window.createOutputChannel('LLM Wiki Doctor');
  context.subscriptions.push(doctorOutput);
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => doctor(context)));
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.experimentalDiscoverCopilotModels', () => discoverModels()));
}

function deactivate() {
  return base.deactivate();
}

module.exports = { activate, deactivate };
