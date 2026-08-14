'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const base = require('./extension');

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

async function doctor(context) {
  const folder = firstWorkspaceFolder();
  const python = String(configuration().get('pythonExecutable', 'python3') || 'python3');
  const pythonReady = await executableAvailable(python, ['--version'], folder.uri.fsPath);

  // Reuse the real extension -> Python-core command boundary. This may initialize
  // empty local workspace metadata, but it ingests nothing and makes no model call.
  if (pythonReady) await vscode.commands.executeCommand('llmWiki.init');

  let coreReady = false;
  let compiledDisabled = false;
  try {
    const config = JSON.parse(fs.readFileSync(path.join(wikiRoot(folder), 'config.json'), 'utf8'));
    coreReady = pythonReady && config.format === 'llm-wiki-dogfood-v0';
    compiledDisabled = config.compiled_provider === 'disabled';
  } catch (_) {
    coreReady = false;
  }

  const copilotReady = await executableAvailable('copilot', ['--version'], folder.uri.fsPath);
  const askReady = coreReady && compiledDisabled && copilotReady;

  doctorOutput.clear();
  doctorOutput.appendLine('LLM Wiki Doctor');
  doctorOutput.appendLine('Model calls: 0');
  doctorOutput.appendLine(`Python: ${pythonReady ? 'PASS' : 'FAIL'}`);
  doctorOutput.appendLine(`Core: ${coreReady ? 'PASS' : 'FAIL'} mode=${coreMode(context)}`);
  doctorOutput.appendLine(`Compiled provider: ${compiledDisabled ? 'disabled' : 'CHECK_FAILED'}`);
  doctorOutput.appendLine(`Copilot CLI: ${copilotReady ? 'PASS' : 'NOT_FOUND'}`);
  doctorOutput.appendLine(`Local raw/search/provenance: ${coreReady && compiledDisabled ? 'READY' : 'UNAVAILABLE'}`);
  doctorOutput.appendLine(`Ask Luna: ${askReady ? 'READY' : 'UNAVAILABLE'}`);
  doctorOutput.show(true);

  if (coreReady && compiledDisabled) {
    const suffix = copilotReady ? 'Ask Luna is also ready.' : 'Local Wiki is ready; install/authenticate Copilot CLI only when you want Ask Luna.';
    vscode.window.showInformationMessage(`LLM Wiki Doctor: local core ready. ${suffix}`);
  } else {
    vscode.window.showWarningMessage('LLM Wiki Doctor: local core is not ready. Open the LLM Wiki Doctor output for the failing boundary.');
  }
}

async function activate(context) {
  await base.activate(context);
  doctorOutput = vscode.window.createOutputChannel('LLM Wiki Doctor');
  context.subscriptions.push(doctorOutput);
  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => doctor(context)));
}

function deactivate() {
  return base.deactivate();
}

module.exports = { activate, deactivate };
