'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');

suite('LLM Wiki Agent Tools', () => {
  test('registers bounded language model tools and keeps ambient search read-only', async () => {
    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'development extension was not discovered by VS Code');
    await extension.activate();

    const toolNames = new Set(vscode.lm.tools.map((tool) => tool.name));
    assert.ok(toolNames.has('llmWiki_searchMemory'), 'ambient memory search tool is not registered');
    assert.ok(toolNames.has('llmWiki_rememberSource'), 'explicit remember tool is not registered');

    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    const evidencePath = path.join(folder.uri.fsPath, 'runtime-agent-tool-evidence.md');
    fs.rmSync(wikiRoot, { recursive: true, force: true });
    fs.writeFileSync(
      evidencePath,
      '# Ambient memory evidence\n\nThe juniper retry budget is 73 because bounded recovery mattered more than aggressive retries.\n',
      'utf8'
    );

    try {
      await vscode.commands.executeCommand('llmWiki.init');
      await vscode.commands.executeCommand('llmWiki.createTopic', { label: 'runtime-agent-memory' });
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(evidencePath));
      await vscode.window.showTextDocument(doc, { preview: false });
      await vscode.commands.executeCommand('llmWiki.ingestActiveFile');

      const manifestPath = path.join(wikiRoot, 'manifest.jsonl');
      const manifestBefore = fs.readFileSync(manifestPath, 'utf8');
      const workloadPath = path.join(wikiRoot, 'workload-events.jsonl');
      const workloadBefore = fs.existsSync(workloadPath) ? fs.readFileSync(workloadPath, 'utf8') : '';

      const result = await vscode.lm.invokeTool('llmWiki_searchMemory', {
        input: { query: 'juniper retry budget', maxResults: 3 },
        toolInvocationToken: undefined,
      });
      const text = result.content
        .filter((part) => part instanceof vscode.LanguageModelTextPart)
        .map((part) => part.value)
        .join('\n');

      assert.match(text, /LLM_WIKI_MEMORY_RESULT v1/);
      assert.match(text, /authority=read_only/);
      assert.match(text, /canonical_mutation=none/);
      assert.match(text, /juniper retry budget is 73/);
      assert.match(text, /source_ids=src-/);
      assert.match(text, /This tool result authorizes reading only/);

      assert.equal(fs.readFileSync(manifestPath, 'utf8'), manifestBefore, 'ambient memory lookup must not mutate canonical history');
      const workloadAfter = fs.existsSync(workloadPath) ? fs.readFileSync(workloadPath, 'utf8') : '';
      assert.equal(workloadAfter, workloadBefore, 'ambient discovery must not manufacture E013 query/visit telemetry');
    } finally {
      fs.rmSync(evidencePath, { force: true });
    }
  });
});
