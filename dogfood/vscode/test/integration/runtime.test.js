'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');

function stubWindowMethod(name, replacement) {
  const original = vscode.window[name];
  vscode.window[name] = replacement;
  return () => {
    vscode.window[name] = original;
  };
}

async function withWindowStubs(stubs, fn) {
  const restores = Object.entries(stubs).map(([name, replacement]) => stubWindowMethod(name, replacement));
  try {
    return await fn();
  } finally {
    for (const restore of restores.reverse()) restore();
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

  test('runs topic -> active-file ingest -> search -> read-only provenance entirely through VS Code commands', async () => {
    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    const evidencePath = path.join(folder.uri.fsPath, 'runtime-vscode-evidence.md');
    fs.rmSync(wikiRoot, { recursive: true, force: true });
    fs.writeFileSync(evidencePath, '# Runtime evidence\n\nThe cedar quota decision is 41 units because the project preferred bounded cache growth.\n', 'utf8');

    let searchResultPicked = false;
    try {
      await withWindowStubs(
        {
          showInputBox: async (options) => {
            const title = String(options && options.title || '');
            if (title.includes('Create Topic')) return 'runtime-vscode-topic';
            if (title.includes('Search')) return 'cedar quota';
            throw new Error(`unexpected showInputBox: ${title}`);
          },
          showQuickPick: async (items, options) => {
            const title = String(options && options.title || '');
            if (title === 'Optional E013 query tag') {
              return items.find((item) => item.value === 'exact_provenance');
            }
            if (title.includes('search results')) {
              searchResultPicked = true;
              return items[0];
            }
            throw new Error(`unexpected showQuickPick: ${title}`);
          },
          showInformationMessage: async () => undefined,
        },
        async () => {
          await vscode.commands.executeCommand('llmWiki.init');
          await vscode.commands.executeCommand('llmWiki.createTopic');

          const evidenceDoc = await vscode.workspace.openTextDocument(vscode.Uri.file(evidencePath));
          await vscode.window.showTextDocument(evidenceDoc, { preview: false });
          await vscode.commands.executeCommand('llmWiki.ingestActiveFile');
          await vscode.commands.executeCommand('llmWiki.search');
        }
      );

      assert.equal(searchResultPicked, true, 'search result Quick Pick was not reached');
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
