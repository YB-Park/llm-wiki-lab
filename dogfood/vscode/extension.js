'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');

const execFileAsync = promisify(execFile);
const SOURCE_SCHEME = 'llm-wiki-source';
const SELECTED_TOPIC_KEY = 'llmWiki.selectedTopic';
const MAX_BUFFER = 16 * 1024 * 1024;

let output;
let status;

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) {
    throw new Error('Open a VS Code workspace/folder before using LLM Wiki.');
  }
  return folders[0];
}

function configuration() {
  return vscode.workspace.getConfiguration('llmWiki');
}

function coreRoot(context, folder) {
  const configured = String(configuration().get('corePath', '') || '').trim();
  if (configured) {
    return path.isAbsolute(configured) ? configured : path.resolve(folder.uri.fsPath, configured);
  }

  const bundled = path.resolve(context.extensionPath, 'python');
  if (fs.existsSync(path.join(bundled, 'dogfood', 'llm_wiki', 'cli.py'))) {
    return bundled;
  }

  return path.resolve(context.extensionPath, '..', '..');
}

function wikiRoot(folder) {
  const value = String(configuration().get('workspaceDirectory', '.wiki-lab') || '.wiki-lab');
  return path.isAbsolute(value) ? value : path.resolve(folder.uri.fsPath, value);
}

async function runCli(context, folder, args) {
  const python = String(configuration().get('pythonExecutable', 'python3') || 'python3');
  const root = coreRoot(context, folder);
  const pythonPath = process.env.PYTHONPATH
    ? `${root}${path.delimiter}${process.env.PYTHONPATH}`
    : root;
  const fullArgs = ['-m', 'dogfood.llm_wiki.cli', '--root', wikiRoot(folder), ...args];

  try {
    const result = await execFileAsync(python, fullArgs, {
      cwd: folder.uri.fsPath,
      env: { ...process.env, PYTHONPATH: pythonPath },
      maxBuffer: MAX_BUFFER,
      windowsHide: true,
    });
    if (result.stderr && result.stderr.trim()) {
      output.appendLine(`[stderr] ${result.stderr.trim()}`);
    }
    return result.stdout || '';
  } catch (error) {
    const stderr = error && error.stderr ? String(error.stderr).trim() : '';
    const stdout = error && error.stdout ? String(error.stdout).trim() : '';
    const detail = stderr || stdout || (error && error.message) || String(error);
    throw new Error(detail);
  }
}

function parseTopics(stdout) {
  return stdout
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      const match = line.match(/^(\S+)\s+(.*)$/);
      if (!match) {
        throw new Error(`Unexpected topic-list row: ${line}`);
      }
      return { id: match[1], label: match[2] };
    });
}

function parseJsonLines(stdout) {
  return stdout
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

function workspaceTopicKey(folder) {
  return `${SELECTED_TOPIC_KEY}:${folder.uri.toString()}`;
}

async function setSelectedTopic(context, folder, topic) {
  await context.workspaceState.update(workspaceTopicKey(folder), topic || undefined);
  updateStatus(context, folder, topic);
}

function updateStatus(context, folder, topic) {
  if (!status) return;
  const selected = topic || context.workspaceState.get(workspaceTopicKey(folder));
  if (selected && selected.label) {
    status.text = `$(book) Wiki: ${selected.label}`;
    status.tooltip = 'LLM Wiki selected topic — click to change';
  } else {
    status.text = '$(book) Wiki: no topic';
    status.tooltip = 'LLM Wiki — click to select a topic';
  }
  status.show();
}

async function createTopic(context, folder = firstWorkspaceFolder()) {
  const label = await vscode.window.showInputBox({
    title: 'LLM Wiki: Create Topic',
    prompt: 'Human-readable topic label. It stays in the local wiki registry.',
    ignoreFocusOut: true,
    validateInput: (value) => (value.trim() ? undefined : 'Topic label is required.'),
  });
  if (!label) return undefined;

  await runCli(context, folder, ['topic', 'add', label.trim()]);
  const all = parseTopics(await runCli(context, folder, ['topic', 'list']));
  const topic = [...all].reverse().find((row) => row.label === label.trim());
  if (!topic) throw new Error('Topic was created but could not be resolved from the local registry.');
  await setSelectedTopic(context, folder, topic);
  vscode.window.showInformationMessage(`LLM Wiki topic selected: ${topic.label}`);
  return topic;
}

async function selectTopic(context, folder = firstWorkspaceFolder(), forcePrompt = false) {
  const all = parseTopics(await runCli(context, folder, ['topic', 'list']));
  if (!all.length) {
    const choice = await vscode.window.showInformationMessage(
      'No LLM Wiki topics exist in this workspace.',
      'Create Topic'
    );
    if (choice === 'Create Topic') return createTopic(context, folder);
    return undefined;
  }

  const saved = context.workspaceState.get(workspaceTopicKey(folder));
  if (!forcePrompt && saved && all.some((row) => row.id === saved.id)) {
    return all.find((row) => row.id === saved.id);
  }

  const picked = await vscode.window.showQuickPick(
    all.map((row) => ({ label: row.label, description: row.id, topic: row })),
    {
      title: 'LLM Wiki: Select Topic',
      placeHolder: 'Choose the topic for this workspace interaction',
      ignoreFocusOut: true,
    }
  );
  if (!picked) return undefined;
  await setSelectedTopic(context, folder, picked.topic);
  return picked.topic;
}

async function pickQueryClass() {
  const picked = await vscode.window.showQuickPick(
    [
      { label: 'Skip / unknown', description: 'No query-class tag', value: undefined },
      { label: 'Exact / provenance', description: 'Exact fact or source verification', value: 'exact_provenance' },
      { label: 'Synthesis', description: 'Cross-source understanding or summary', value: 'synthesis' },
      { label: 'Decision / history', description: 'Why a decision was made or how it changed', value: 'decision_history' },
      { label: 'Other', description: 'Does not fit the current classes', value: 'other' },
    ],
    {
      title: 'Optional E013 query tag',
      placeHolder: 'Choose a class, or press Esc to skip',
      ignoreFocusOut: true,
    }
  );
  return picked ? picked.value : undefined;
}

function withClass(args, queryClass) {
  return queryClass ? [...args, '--class', queryClass] : args;
}

function sourceUri(folder, topic, row) {
  const params = new URLSearchParams({
    workspace: folder.uri.toString(),
    topic: topic.id,
    name: row.name || row.source_id,
  });
  return vscode.Uri.parse(`${SOURCE_SCHEME}:/${encodeURIComponent(row.source_id)}?${params.toString()}`);
}

function languageForName(name) {
  const ext = path.extname(name || '').toLowerCase();
  const mapping = {
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.json': 'json',
    '.jsonl': 'json',
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.html': 'html',
    '.css': 'css',
    '.sh': 'shellscript',
  };
  return mapping[ext] || 'plaintext';
}

async function openSource(context, folder, topic, row) {
  const uri = sourceUri(folder, topic, row);
  let doc = await vscode.workspace.openTextDocument(uri);
  const language = languageForName(row.name);
  if (language !== 'plaintext') {
    doc = await vscode.languages.setTextDocumentLanguage(doc, language);
  }
  await vscode.window.showTextDocument(doc, { preview: true });
}

async function ingestActive(context, authoritativeUpdate) {
  const folder = firstWorkspaceFolder();
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.uri.scheme !== 'file') {
    vscode.window.showWarningMessage('Open a local file in the editor before ingesting it.');
    return;
  }
  if (editor.document.isDirty) {
    const saved = await editor.document.save();
    if (!saved) return;
  }

  const topic = await selectTopic(context, folder);
  if (!topic) return;
  const args = ['ingest', editor.document.uri.fsPath, '--topic', topic.id];
  if (authoritativeUpdate) args.push('--authoritative-update');
  await runCli(context, folder, args);
  const mode = authoritativeUpdate ? 'authoritative update' : 'evidence';
  vscode.window.showInformationMessage(`LLM Wiki ingested ${path.basename(editor.document.uri.fsPath)} as ${mode} for ${topic.label}.`);
}

async function searchTopic(context) {
  const folder = firstWorkspaceFolder();
  const topic = await selectTopic(context, folder);
  if (!topic) return;
  const query = await vscode.window.showInputBox({
    title: `LLM Wiki: Search — ${topic.label}`,
    prompt: 'Search local raw evidence. Query text is not stored in E013 telemetry.',
    ignoreFocusOut: true,
  });
  if (!query || !query.trim()) return;
  const queryClass = await pickQueryClass();
  let args = ['search', query.trim(), '--json', '--topic', topic.id];
  args = withClass(args, queryClass);

  const rows = parseJsonLines(await runCli(context, folder, args));
  output.clear();
  output.appendLine(`LLM Wiki search — ${topic.label}`);
  output.appendLine(`Query: ${query.trim()}`);
  output.appendLine('');
  for (const row of rows) {
    output.appendLine(`${row.name}  score=${Number(row.score).toFixed(6)}  ${row.source_id}`);
    output.appendLine(String(row.snippet || '').replace(/\s+/g, ' '));
    output.appendLine('');
  }
  output.show(true);

  if (!rows.length) {
    vscode.window.showInformationMessage('LLM Wiki found no matching local evidence.');
    return;
  }

  const picked = await vscode.window.showQuickPick(
    rows.map((row) => ({
      label: row.name,
      description: `${Number(row.score).toFixed(4)} · ${row.source_id}`,
      detail: String(row.snippet || '').replace(/\s+/g, ' '),
      row,
    })),
    {
      title: `LLM Wiki search results — ${topic.label}`,
      placeHolder: 'Open a result as read-only provenance, or Esc to keep the list in Output',
      matchOnDescription: true,
      matchOnDetail: true,
      ignoreFocusOut: true,
    }
  );
  if (picked) await openSource(context, folder, topic, picked.row);
}

async function askLuna(context) {
  const folder = firstWorkspaceFolder();
  const topic = await selectTopic(context, folder);
  if (!topic) return;
  const query = await vscode.window.showInputBox({
    title: `LLM Wiki: Ask Luna — ${topic.label}`,
    prompt: 'Question text is not stored in E013 telemetry. Retrieved evidence will be sent only after explicit confirmation.',
    ignoreFocusOut: true,
  });
  if (!query || !query.trim()) return;
  const queryClass = await pickQueryClass();

  const approved = await vscode.window.showWarningMessage(
    'This will send retrieved evidence context to GitHub Copilot using gpt-5.6-luna. The answer is read-only and cannot mutate canonical wiki state.',
    { modal: true },
    'Send to Luna'
  );
  if (approved !== 'Send to Luna') return;

  const maxCredits = Math.max(1, Number(configuration().get('maxAiCredits', 30)) || 30);
  let args = [
    'ask',
    query.trim(),
    '--topic', topic.id,
    '--model', 'gpt-5.6-luna',
    '--max-ai-credits', String(maxCredits),
    '--allow-model-call',
  ];
  args = withClass(args, queryClass);

  const stdout = await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'LLM Wiki: asking Luna from retrieved evidence…',
      cancellable: false,
    },
    () => runCli(context, folder, args)
  );

  output.clear();
  output.appendLine(`LLM Wiki answer — ${topic.label}`);
  output.appendLine('Model: gpt-5.6-luna');
  output.appendLine('Canonical mutation: none');
  output.appendLine('');
  output.append(stdout.trim());
  output.show(true);
}

async function showCalibration(context) {
  const folder = firstWorkspaceFolder();
  const stdout = await runCli(context, folder, ['calibration', 'export']);
  const doc = await vscode.workspace.openTextDocument({ content: stdout, language: 'json' });
  await vscode.window.showTextDocument(doc, { preview: true });
}

class SourceProvider {
  constructor(context) {
    this.context = context;
  }

  async provideTextDocumentContent(uri) {
    const params = new URLSearchParams(uri.query);
    const workspace = params.get('workspace');
    const topic = params.get('topic');
    const name = params.get('name') || 'source';
    const sourceId = decodeURIComponent(uri.path.replace(/^\//, ''));
    const folder = (vscode.workspace.workspaceFolders || []).find((item) => item.uri.toString() === workspace);
    if (!folder) throw new Error('The workspace for this provenance document is no longer open.');
    if (!topic) throw new Error('Missing topic for provenance document.');

    const stdout = await runCli(this.context, folder, ['source', 'show', sourceId, '--topic', topic]);
    const lines = stdout.split(/\r?\n/);
    const header = lines.shift() || `SOURCE ${sourceId}`;
    return `LLM WIKI READ-ONLY PROVENANCE\n${header}\nname=${name}\n\n${lines.join('\n')}`;
  }
}

async function commandGuard(name, fn) {
  try {
    await fn();
  } catch (error) {
    const message = error && error.message ? error.message : String(error);
    output.appendLine(`[${name}] ${message}`);
    output.show(true);
    vscode.window.showErrorMessage(`LLM Wiki: ${message}`);
  }
}

function activate(context) {
  output = vscode.window.createOutputChannel('LLM Wiki');
  status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  status.command = 'llmWiki.selectTopic';
  context.subscriptions.push(output, status);
  context.subscriptions.push(vscode.workspace.registerTextDocumentContentProvider(SOURCE_SCHEME, new SourceProvider(context)));

  const register = (command, fn) => {
    context.subscriptions.push(vscode.commands.registerCommand(command, () => commandGuard(command, fn)));
  };

  register('llmWiki.init', async () => {
    const folder = firstWorkspaceFolder();
    await runCli(context, folder, ['init']);
    updateStatus(context, folder);
    vscode.window.showInformationMessage('LLM Wiki local workspace initialized. Compiled provider remains disabled.');
  });
  register('llmWiki.createTopic', () => createTopic(context));
  register('llmWiki.selectTopic', async () => {
    const folder = firstWorkspaceFolder();
    await selectTopic(context, folder, true);
  });
  register('llmWiki.ingestActiveFile', () => ingestActive(context, false));
  register('llmWiki.ingestAuthoritativeUpdate', () => ingestActive(context, true));
  register('llmWiki.search', () => searchTopic(context));
  register('llmWiki.ask', () => askLuna(context));
  register('llmWiki.calibration', () => showCalibration(context));

  try {
    const folder = firstWorkspaceFolder();
    updateStatus(context, folder);
  } catch (_) {
    status.hide();
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
