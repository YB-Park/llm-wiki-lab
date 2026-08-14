'use strict';

const assert = require('node:assert/strict');
const vscode = require('vscode');

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
});
