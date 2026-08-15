'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');

function toolText(result) {
  return result.content
    .filter((part) => part instanceof vscode.LanguageModelTextPart)
    .map((part) => part.value)
    .join('\n');
}

suite('LLM Wiki Agent Tools', () => {
  test('registers bounded tools and keeps ambient raw+derived search read-only', async () => {
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
      const text = toolText(result);

      assert.match(text, /LLM_WIKI_MEMORY_RESULT v2/);
      assert.match(text, /authority=read_only/);
      assert.match(text, /canonical_mutation=none/);
      assert.match(text, /raw_candidate_count=1/);
      assert.match(text, /derived_candidate_count=0/);
      assert.match(text, /RAW_MEMORY R1/);
      assert.match(text, /epistemic_status=canonical_raw_evidence/);
      assert.match(text, /juniper retry budget is 73/);
      assert.match(text, /source_ids=src-/);
      assert.match(text, /DERIVED_MEMORY is model-generated, noncanonical synthesis\/navigation aid/);

      assert.equal(fs.readFileSync(manifestPath, 'utf8'), manifestBefore, 'ambient memory lookup must not mutate canonical history');
      const workloadAfter = fs.existsSync(workloadPath) ? fs.readFileSync(workloadPath, 'utf8') : '';
      assert.equal(workloadAfter, workloadBefore, 'ambient discovery must not manufacture E013 query/visit telemetry');
    } finally {
      fs.rmSync(evidencePath, { force: true });
    }
  });

  test('explicit remember stays zero-model and publishes no derived note when maintenance grant is off', async () => {
    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'development extension was not discovered by VS Code');
    await extension.activate();

    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    const sourcePath = path.join(folder.uri.fsPath, 'runtime-remember-source.md');
    const config = vscode.workspace.getConfiguration('llmWiki');
    fs.rmSync(wikiRoot, { recursive: true, force: true });
    fs.writeFileSync(
      sourcePath,
      '# Remember source\n\nKeep the cobalt deployment timeout at 15 seconds until a human explicitly changes the decision.\n',
      'utf8'
    );

    try {
      await config.update('agentWikiMaintenanceEnabled', false, vscode.ConfigurationTarget.Workspace);
      const result = await vscode.lm.invokeTool('llmWiki_rememberSource', {
        input: { filePath: sourcePath },
        toolInvocationToken: undefined,
      });
      const text = toolText(result);

      assert.match(text, /LLM_WIKI_REMEMBER_RESULT v2/);
      assert.match(text, /authority=explicit_source_admission/);
      assert.match(text, /source_id=src-/);
      assert.match(text, /model_calls=0/);
      assert.match(text, /derived_agent_wiki_maintenance=SKIPPED_NO_WORKSPACE_GRANT/);
      assert.match(text, /human_authorship_persisted=no/);
      assert.match(text, /canonical_semantic_mutation=none/);

      const manifestPath = path.join(wikiRoot, 'manifest.jsonl');
      const manifestRows = fs.readFileSync(manifestPath, 'utf8').trim().split(/\r?\n/).map((line) => JSON.parse(line));
      const ingestRows = manifestRows.filter((row) => row.event === 'ingest');
      assert.equal(ingestRows.length, 1, 'remember tool should perform exactly one raw admission for a new file');
      assert.equal(ingestRows[0].name, 'runtime-remember-source.md');
      assert.equal(fs.existsSync(path.join(wikiRoot, 'agent-wiki', 'source-notes')), false, 'maintenance-disabled remember must not publish Agent Wiki notes');
    } finally {
      await config.update('agentWikiMaintenanceEnabled', false, vscode.ConfigurationTarget.Workspace);
      fs.rmSync(sourcePath, { force: true });
    }
  });
});
