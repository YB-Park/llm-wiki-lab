'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');

async function stage(label, promise, timeoutMs = 10000) {
  let timer;
  try {
    return await Promise.race([
      Promise.resolve(promise),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`VS-PRODUCT-STAGE timeout=${label}`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

suite('LLM Wiki 0.1.4 Product Surface', () => {
  test('registers the E010 P1-P4 customer command surface', async () => {
    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'LLM Wiki extension was not discovered');
    await extension.activate();

    const commands = new Set(await vscode.commands.getCommands(true));
    for (const command of [
      'llmWiki.discoverAcrossTopics',
      'llmWiki.markCorrection',
      'llmWiki.markChange',
      'llmWiki.markDispute',
      'llmWiki.feedback',
    ]) {
      assert.ok(commands.has(command), `missing product command: ${command}`);
    }
  });

  test('discovers forgotten-topic current evidence through the real VS Code-to-core bridge', async () => {
    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    const alphaPath = path.join(folder.uri.fsPath, 'runtime-product-alpha.md');
    const betaPath = path.join(folder.uri.fsPath, 'runtime-product-beta.md');
    fs.rmSync(wikiRoot, { recursive: true, force: true });
    fs.writeFileSync(alphaPath, '# Alpha\n\nunique-amber-orchid product discovery evidence\n', 'utf8');
    fs.writeFileSync(betaPath, '# Beta\n\nseparate cobalt evidence\n', 'utf8');

    try {
      await stage('init', vscode.commands.executeCommand('llmWiki.init'));
      await stage('create-alpha', vscode.commands.executeCommand('llmWiki.createTopic', { label: 'runtime-product-alpha' }));
      const alphaDoc = await stage('open-alpha', vscode.workspace.openTextDocument(vscode.Uri.file(alphaPath)));
      await stage('show-alpha', vscode.window.showTextDocument(alphaDoc, { preview: false }));
      await stage('ingest-alpha', vscode.commands.executeCommand('llmWiki.ingestActiveFile'));

      await stage('create-beta', vscode.commands.executeCommand('llmWiki.createTopic', { label: 'runtime-product-beta' }));
      const betaDoc = await stage('open-beta', vscode.workspace.openTextDocument(vscode.Uri.file(betaPath)));
      await stage('show-beta', vscode.window.showTextDocument(betaDoc, { preview: false }));
      await stage('ingest-beta', vscode.commands.executeCommand('llmWiki.ingestActiveFile'));

      await stage(
        'discover-across-topics',
        vscode.commands.executeCommand('llmWiki.discoverAcrossTopics', {
          query: 'unique amber orchid',
          openFirstResult: true,
        })
      );

      const active = vscode.window.activeTextEditor;
      assert.ok(active, 'cross-topic discovery did not open evidence');
      assert.equal(active.document.uri.scheme, 'llm-wiki-source', 'programmatic validation must open immutable provenance');
      assert.match(active.document.getText(), /unique-amber-orchid product discovery evidence/);

      const eventsPath = path.join(wikiRoot, 'workload-events.jsonl');
      const events = fs.existsSync(eventsPath) ? fs.readFileSync(eventsPath, 'utf8') : '';
      assert.doesNotMatch(events, /"event":\s*"query"/, 'cross-topic discovery must not manufacture an E013 visit');
    } finally {
      fs.rmSync(alphaPath, { force: true });
      fs.rmSync(betaPath, { force: true });
    }
  });
});
