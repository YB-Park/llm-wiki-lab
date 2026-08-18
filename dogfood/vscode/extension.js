'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const vscode = require('vscode');
const { locatorForRow, parseIngestReceipt, resolveWorkspaceRelative, sha256, workspaceRelativePath } = require('./product-helpers');

const execFileAsync = promisify(execFile);
const SOURCE_SCHEME = 'llm-wiki-source';
const SELECTED_TOPIC_KEY = 'llmWiki.selectedTopic';
const SOURCE_LOCATORS_KEY = 'llmWiki.sourceLocators.v1';
const MAX_BUFFER = 16 * 1024 * 1024;
const QUERY_CLASSES = new Set(['exact_provenance', 'synthesis', 'decision_history', 'other']);

let output;
let status;

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) {
    throw new Error('Open a VS Code workspace/folder before using LLM Wiki.');
  }
  if (folders.length !== 1) {
    throw new Error('LLM Wiki currently supports one workspace folder at a time. Open the project as a single-folder workspace before using project memory.');
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

function workspaceLocatorKey(folder) {
  return `${SOURCE_LOCATORS_KEY}:${folder.uri.toString()}`;
}

function sourceLocators(context, folder) {
  return context.workspaceState.get(workspaceLocatorKey(folder), {});
}

async function rememberSourceLocator(context, folder, sourceId, filePath, digest) {
  const relativePath = workspaceRelativePath(folder.uri.fsPath, filePath);
  if (!sourceId || !relativePath || !digest) return;
  const next = { ...sourceLocators(context, folder), [sourceId]: { relativePath, sha256: digest } };
  await context.workspaceState.update(workspaceLocatorKey(folder), next);
}

function displayLocator(context, folder, row) {
  const locator = locatorForRow(sourceLocators(context, folder), row);
  return locator ? locator.relativePath : (row.name || row.source_id || 'source');
}

async function setSelectedTopic(context, folder, topic) {
  await context.workspaceState.update(workspaceTopicKey(folder), topic || undefined);
  updateStatus(context, folder, topic);
}

function setStatusVisible(enabled) {
  if (!status) return;
  if (enabled) status.show();
  else status.hide();
}

function updateStatus(_context, _folder, _topic) {
  if (!status) return;
  status.text = '$(book) LLM Wiki';
  status.tooltip = 'Project memory is on for this workspace — click to check setup and health';
  status.show();
}

async function createTopic(context, folder = firstWorkspaceFolder(), options = {}) {
  const suppliedLabel = options && typeof options.label === 'string' ? options.label.trim() : '';
  const label = suppliedLabel || await vscode.window.showInputBox({
    title: 'LLM Wiki: Create Topic',
    prompt: 'Human-readable topic label. It stays in the local wiki registry.',
    ignoreFocusOut: true,
    validateInput: (value) => (value.trim() ? undefined : 'Topic label is required.'),
  });
  if (!label) return undefined;
  const normalizedLabel = label.trim();

  await runCli(context, folder, ['topic', 'add', normalizedLabel]);
  const all = parseTopics(await runCli(context, folder, ['topic', 'list']));
  const topic = [...all].reverse().find((row) => row.label === normalizedLabel);
  if (!topic) throw new Error('Topic was created but could not be resolved from the local registry.');
  await setSelectedTopic(context, folder, topic);
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

function queryClassFromOptions(options) {
  if (!options || !Object.prototype.hasOwnProperty.call(options, 'queryClass')) return undefined;
  if (options.queryClass === undefined || options.queryClass === null || options.queryClass === '') return null;
  const value = String(options.queryClass);
  if (!QUERY_CLASSES.has(value)) throw new Error(`Unsupported query class: ${value}`);
  return value;
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

async function openSource(context, folder, topic, row, options = {}) {
  const preferWorkspaceFile = options.preferWorkspaceFile !== false;
  const locator = preferWorkspaceFile ? locatorForRow(sourceLocators(context, folder), row) : undefined;
  if (locator) {
    const target = resolveWorkspaceRelative(folder.uri.fsPath, locator.relativePath);
    if (target && fs.existsSync(target) && fs.statSync(target).isFile()) {
      const digest = sha256(fs.readFileSync(target));
      if (digest === (row.sha256 || locator.sha256)) {
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(target));
        await vscode.window.showTextDocument(doc, { preview: true });
        return;
      }
      vscode.window.showWarningMessage(
        `LLM Wiki: ${locator.relativePath} changed after ingest; opening immutable evidence snapshot instead.`
      );
    }
  }

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
  const stdout = await runCli(context, folder, args);
  const receipt = parseIngestReceipt(stdout);
  if (receipt) {
    await rememberSourceLocator(context, folder, receipt.sourceId, editor.document.uri.fsPath, receipt.sha256);
  }
  // Routine success stays quiet; the explicit command/Agent flow already provides context.
}

async function searchTopic(context, options = {}) {
  const folder = firstWorkspaceFolder();
  const topic = await selectTopic(context, folder);
  if (!topic) return;

  const suppliedQuery = options && typeof options.query === 'string' ? options.query.trim() : '';
  const query = suppliedQuery || await vscode.window.showInputBox({
    title: `LLM Wiki: Search — ${topic.label}`,
    prompt: 'Search local raw evidence. Query text is not stored in E013 telemetry.',
    ignoreFocusOut: true,
  });
  if (!query || !query.trim()) return;

  const optionClass = queryClassFromOptions(options);
  const hasProgrammaticClass = options && Object.prototype.hasOwnProperty.call(options, 'queryClass');
  const queryClass = hasProgrammaticClass ? optionClass || undefined : await pickQueryClass();
  let args = ['search', query.trim(), '--json', '--topic', topic.id];
  args = withClass(args, queryClass);

  const rows = parseJsonLines(await runCli(context, folder, args));
  output.clear();
  output.appendLine(`LLM Wiki search — ${topic.label}`);
  output.appendLine(`Query: ${query.trim()}`);
  output.appendLine('');
  for (const row of rows) {
    output.appendLine(`${displayLocator(context, folder, row)}  score=${Number(row.score).toFixed(6)}  ${row.source_id}`);
    output.appendLine(String(row.snippet || '').replace(/\s+/g, ' '));
    output.appendLine('');
  }
  output.show(true);

  if (!rows.length) {
    vscode.window.showInformationMessage('LLM Wiki found no matching local evidence.');
    return;
  }

  if (options && options.openFirstResult === true) {
    await openSource(context, folder, topic, rows[0], { preferWorkspaceFile: false });
    return;
  }

  const picked = await vscode.window.showQuickPick(
    rows.map((row) => ({
      label: displayLocator(context, folder, row),
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

async function discoverAcrossTopics(context, options = {}) {
  const folder = firstWorkspaceFolder();
  const suppliedQuery = options && typeof options.query === 'string' ? options.query.trim() : '';
  const query = suppliedQuery || await vscode.window.showInputBox({
    title: 'LLM Wiki: Find Evidence Across Topics',
    prompt: 'Discovery searches each topic current view. It does not count as an E013 visit.',
    ignoreFocusOut: true,
  });
  if (!query || !query.trim()) return;

  const rows = parseJsonLines(await runCli(context, folder, ['discover', query.trim(), '--json']));
  rows.sort((a, b) => Number(b.score) - Number(a.score));
  if (!rows.length) {
    vscode.window.showInformationMessage('LLM Wiki found no current evidence across topics.');
    return;
  }

  if (options && options.openFirstResult === true) {
    const row = rows[0];
    const topic = { id: row.topic_id, label: row.topic_label };
    await setSelectedTopic(context, folder, topic);
    await openSource(context, folder, topic, row, { preferWorkspaceFile: false });
    return;
  }

  const picked = await vscode.window.showQuickPick(
    rows.map((row) => ({
      label: displayLocator(context, folder, row),
      description: `${row.topic_label} · ${Number(row.score).toFixed(4)}`,
      detail: String(row.snippet || '').replace(/\s+/g, ' '),
      row,
    })),
    {
      title: 'LLM Wiki: Find Evidence Across Topics',
      placeHolder: 'Choose current evidence; selecting it switches the active topic',
      matchOnDescription: true,
      matchOnDetail: true,
      ignoreFocusOut: true,
    }
  );
  if (!picked) return;
  const topic = { id: picked.row.topic_id, label: picked.row.topic_label };
  await setSelectedTopic(context, folder, topic);
  await openSource(context, folder, topic, picked.row);
}

async function currentSources(context, folder, topic) {
  return parseJsonLines(await runCli(context, folder, ['source', 'list', '--topic', topic.id, '--json']));
}

async function pickSource(context, folder, topic, title, excludeSourceId) {
  const rows = (await currentSources(context, folder, topic)).filter((row) => row.source_id !== excludeSourceId);
  const picked = await vscode.window.showQuickPick(
    rows.map((row) => ({
      label: displayLocator(context, folder, row),
      description: `${row.contested ? 'contested · ' : ''}${row.source_id}`,
      row,
    })),
    { title, placeHolder: 'Choose an explicit current evidence revision', ignoreFocusOut: true }
  );
  return picked ? picked.row : undefined;
}

async function markCorrection(context) {
  const folder = firstWorkspaceFolder();
  const topic = await selectTopic(context, folder);
  if (!topic) return;
  const predecessor = await pickSource(context, folder, topic, 'LLM Wiki: Correction — incorrect predecessor');
  if (!predecessor) return;
  const successor = await pickSource(context, folder, topic, 'LLM Wiki: Correction — correcting successor', predecessor.source_id);
  if (!successor) return;
  const approved = await vscode.window.showWarningMessage(
    `Mark ${predecessor.name} as erroneous and ${successor.name} as its correction?`,
    { modal: true }, 'Record Correction'
  );
  if (approved !== 'Record Correction') return;
  await runCli(context, folder, ['source', 'correct', predecessor.source_id, successor.source_id, '--topic', topic.id]);
  vscode.window.showInformationMessage('LLM Wiki recorded explicit correction. Raw/history remain preserved.');
}

async function markChange(context) {
  const folder = firstWorkspaceFolder();
  const topic = await selectTopic(context, folder);
  if (!topic) return;
  const predecessor = await pickSource(context, folder, topic, 'LLM Wiki: Change — earlier state');
  if (!predecessor) return;
  const successor = await pickSource(context, folder, topic, 'LLM Wiki: Change — later state', predecessor.source_id);
  if (!successor) return;
  const effectiveAt = await vscode.window.showInputBox({
    title: 'LLM Wiki: Change — effective time',
    prompt: 'Timezone-aware ISO 8601 instant, e.g. 2026-08-01T09:00:00+09:00',
    ignoreFocusOut: true,
    validateInput: (value) => value.trim() ? undefined : 'Effective time is required.',
  });
  if (!effectiveAt) return;
  await runCli(context, folder, [
    'source', 'change', predecessor.source_id, successor.source_id,
    '--topic', topic.id, '--effective-at', effectiveAt.trim(),
  ]);
  vscode.window.showInformationMessage('LLM Wiki recorded explicit change-over-time. Raw/history remain preserved.');
}

async function markDispute(context) {
  const folder = firstWorkspaceFolder();
  const topic = await selectTopic(context, folder);
  if (!topic) return;
  const left = await pickSource(context, folder, topic, 'LLM Wiki: Dispute — first current evidence');
  if (!left) return;
  const right = await pickSource(context, folder, topic, 'LLM Wiki: Dispute — conflicting current evidence', left.source_id);
  if (!right) return;
  const approved = await vscode.window.showWarningMessage(
    `Record unresolved disagreement between ${left.name} and ${right.name}? Neither becomes the winner.`,
    { modal: true }, 'Record Dispute'
  );
  if (approved !== 'Record Dispute') return;
  await runCli(context, folder, ['source', 'dispute', left.source_id, right.source_id, '--topic', topic.id]);
  vscode.window.showInformationMessage('LLM Wiki recorded unresolved dispute; both evidence revisions remain current.');
}

async function recordFeedback(context, topic, presetOutcome) {
  const folder = firstWorkspaceFolder();
  const activeTopic = topic || await selectTopic(context, folder);
  if (!activeTopic) return;
  let outcome = presetOutcome;
  if (!outcome) {
    const picked = await vscode.window.showQuickPick(
      [
        { label: 'Helpful', value: 'helpful' },
        { label: 'Not helpful', value: 'not_helpful' },
      ],
      { title: 'LLM Wiki: Feedback', placeHolder: 'Fixed-code local feedback only', ignoreFocusOut: true }
    );
    if (!picked) return;
    outcome = picked.value;
  }
  const reasons = outcome === 'helpful'
    ? [
        { label: 'Correct', value: 'correct' },
        { label: 'Helped find the source', value: 'found_source' },
        { label: 'Other', value: 'other' },
        { label: 'Skip reason', value: undefined },
      ]
    : [
        { label: 'Missing source', value: 'missing_source' },
        { label: 'Wrong', value: 'wrong' },
        { label: 'Incomplete', value: 'incomplete' },
        { label: 'Other', value: 'other' },
        { label: 'Skip reason', value: undefined },
      ];
  const pickedReason = await vscode.window.showQuickPick(reasons, {
    title: 'LLM Wiki: Feedback reason (optional)',
    placeHolder: 'No free text is stored',
    ignoreFocusOut: true,
  });
  if (!pickedReason) return;
  const args = ['feedback', outcome, '--topic', activeTopic.id];
  if (pickedReason.value) args.push('--reason', pickedReason.value);
  await runCli(context, folder, args);
  vscode.window.showInformationMessage('LLM Wiki recorded local fixed-code feedback.');
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

  const feedback = await vscode.window.showInformationMessage(
    'Was this LLM Wiki answer useful?', 'Helpful', 'Not helpful'
  );
  if (feedback === 'Helpful') await recordFeedback(context, topic, 'helpful');
  if (feedback === 'Not helpful') await recordFeedback(context, topic, 'not_helpful');
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
    const choice = await vscode.window.showErrorMessage(
      'LLM Wiki could not complete this advanced command. Details are available in the local LLM Wiki Output channel.',
      'Check Setup'
    );
    if (choice === 'Check Setup') await vscode.commands.executeCommand('llmWiki.doctor');
  }
}

function activate(context) {
  output = vscode.window.createOutputChannel('LLM Wiki');
  status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  status.command = 'llmWiki.doctor';
  context.subscriptions.push(output, status);
  context.subscriptions.push(vscode.workspace.registerTextDocumentContentProvider(SOURCE_SCHEME, new SourceProvider(context)));

  const register = (command, fn) => {
    context.subscriptions.push(vscode.commands.registerCommand(command, (...args) => commandGuard(command, () => fn(...args))));
  };

  register('llmWiki.init', async () => {
    const folder = firstWorkspaceFolder();
    await runCli(context, folder, ['init']);
    updateStatus(context, folder);
    // Internal compatibility command: no routine success notification.
  });
  register('llmWiki.createTopic', (options) => createTopic(context, firstWorkspaceFolder(), options || {}));
  register('llmWiki.selectTopic', async () => {
    const folder = firstWorkspaceFolder();
    await selectTopic(context, folder, true);
  });
  register('llmWiki.ingestActiveFile', () => ingestActive(context, false));
  register('llmWiki.ingestAuthoritativeUpdate', () => ingestActive(context, true));
  register('llmWiki.search', (options) => searchTopic(context, options || {}));
  register('llmWiki.discoverAcrossTopics', (options) => discoverAcrossTopics(context, options || {}));
  register('llmWiki.markCorrection', () => markCorrection(context));
  register('llmWiki.markChange', () => markChange(context));
  register('llmWiki.markDispute', () => markDispute(context));
  register('llmWiki.feedback', () => recordFeedback(context));
  register('llmWiki.ask', () => askLuna(context));
  register('llmWiki.calibration', () => showCalibration(context));

  try {
    const folder = firstWorkspaceFolder();
    updateStatus(context, folder);
  } catch (_) {
    status.hide();
  }
}

function deactivate() {
  if (status) status.hide();
}

module.exports = { activate, deactivate, setStatusVisible };
