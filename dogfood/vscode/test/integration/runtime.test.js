'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');

async function stage(label, promise, timeoutMs = 8000) {
  let timer;
  try {
    return await Promise.race([
      Promise.resolve(promise),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`VS-RUNTIME-STAGE timeout=${label}`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

suite('LLM Wiki Dogfood Extension Host', () => {
  test('loads extension and registers the VS Code-first command surface', async () => {
    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'development extension was not discovered by VS Code');

    await extension.activate();
    assert.equal(extension.isActive, true, 'extension did not activate');

    const commands = new Set(await vscode.commands.getCommands(true));
    for (const command of [
      'llmWiki.init',
      'llmWiki.createTopic',
      'llmWiki.selectTopic',
      'llmWiki.ingestActiveFile',
      'llmWiki.ingestAuthoritativeUpdate',
      'llmWiki.search',
      'llmWiki.ask',
      'llmWiki.calibration',
      'llmWiki.doctor',
      'llmWiki.experimentalDiscoverCopilotModels',
    ]) {
      assert.ok(commands.has(command), `missing runtime command: ${command}`);
    }
  });

  test('executes Initialize Workspace through the editor-to-core bridge', async () => {
    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    fs.rmSync(wikiRoot, { recursive: true, force: true });

    await vscode.commands.executeCommand('llmWiki.init');

    const configPath = path.join(wikiRoot, 'config.json');
    assert.ok(fs.existsSync(configPath), 'VS Code command did not initialize the local wiki core');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    assert.equal(config.compiled_provider, 'disabled');
    assert.equal(config.format, 'llm-wiki-dogfood-v0');
  });

  test('Doctor reuses the real core boundary and reports Git-protected realistic dogfood readiness', async () => {
    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    fs.rmSync(wikiRoot, { recursive: true, force: true });

    const result = await vscode.commands.executeCommand('llmWiki.doctor');

    const configPath = path.join(wikiRoot, 'config.json');
    assert.ok(fs.existsSync(configPath), 'Doctor did not reach the real local core boundary');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    assert.equal(config.compiled_provider, 'disabled');
    assert.equal(config.format, 'llm-wiki-dogfood-v0');
    assert.ok(result, 'Doctor did not return its sanitized readiness result');
    assert.equal(result.coreReady, true);
    assert.equal(result.compiledDisabled, true);
    assert.equal(result.gitSafety, 'PROTECTED');
    assert.equal(result.realisticDogfoodReady, true);
  });

  test('runs topic -> active-file ingest -> search -> read-only provenance entirely through VS Code commands', async () => {
    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    const evidencePath = path.join(folder.uri.fsPath, 'runtime-vscode-evidence.md');
    fs.rmSync(wikiRoot, { recursive: true, force: true });
    fs.writeFileSync(evidencePath, '# Runtime evidence\n\nThe cedar quota decision is 41 units because the project preferred bounded cache growth.\n', 'utf8');

    try {
      await stage('init', vscode.commands.executeCommand('llmWiki.init'));
      await stage(
        'create-topic',
        vscode.commands.executeCommand('llmWiki.createTopic', { label: 'runtime-vscode-topic' })
      );

      const evidenceDoc = await stage('open-evidence-document', vscode.workspace.openTextDocument(vscode.Uri.file(evidencePath)));
      await stage('show-evidence-editor', vscode.window.showTextDocument(evidenceDoc, { preview: false }));
      await stage('ingest-active-file', vscode.commands.executeCommand('llmWiki.ingestActiveFile'));
      await stage(
        'search-and-open-provenance',
        vscode.commands.executeCommand('llmWiki.search', {
          query: 'cedar quota',
          queryClass: 'exact_provenance',
          openFirstResult: true,
        })
      );

      const active = vscode.window.activeTextEditor;
      assert.ok(active, 'provenance document was not opened');
      assert.equal(active.document.uri.scheme, 'llm-wiki-source');
      const text = active.document.getText();
      assert.match(text, /LLM WIKI READ-ONLY PROVENANCE/);
      assert.match(text, /cedar quota decision is 41 units/);

      const rawDir = path.join(wikiRoot, 'raw');
      const rawFiles = fs.readdirSync(rawDir).filter((name) => !name.startsWith('.'));
      assert.equal(rawFiles.length, 1, 'active-file ingest did not create exactly one immutable raw object');

      const config = JSON.parse(fs.readFileSync(path.join(wikiRoot, 'config.json'), 'utf8'));
      assert.equal(config.compiled_provider, 'disabled');
    } finally {
      fs.rmSync(evidencePath, { force: true });
    }
  });
});
