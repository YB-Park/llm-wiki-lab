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

async function resetAndEnable() {
  const folder = (vscode.workspace.workspaceFolders || [])[0];
  assert.ok(folder, 'integration test workspace is not open');
  const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
  try {
    await vscode.commands.executeCommand('llmWiki.disableWorkspace');
  } catch (_) {}
  fs.rmSync(wikiRoot, { recursive: true, force: true });
  const enabled = await stage('enable-workspace', vscode.commands.executeCommand('llmWiki.enableWorkspace'));
  assert.equal(enabled, true, 'explicit workspace opt-in failed');
  return { folder, wikiRoot };
}

suite('LLM Wiki Product Surface', () => {
  test('registers the operational and actionable command surface after explicit workspace opt-in', async () => {
    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'LLM Wiki extension was not discovered');
    await extension.activate();
    await resetAndEnable();

    const commands = new Set(await vscode.commands.getCommands(true));
    for (const command of [
      'llmWiki.newKnowledgeNote',
      'llmWiki.discoverAcrossTopics',
      'llmWiki.markCorrection',
      'llmWiki.markChange',
      'llmWiki.markDispute',
      'llmWiki.feedback',
      'llmWiki.rememberActiveFile',
      'llmWiki.reviewPendingChanges',
      'llmWiki.configureAiAnswersFriendly',
    ]) {
      assert.ok(commands.has(command), `missing product command after opt-in: ${command}`);
    }
  });

  test('contextual remember reuses the registered guarded remember tool end to end', async () => {
    const { folder, wikiRoot } = await resetAndEnable();
    const sourcePath = path.join(folder.uri.fsPath, 'runtime-contextual-remember.md');
    fs.writeFileSync(sourcePath, '# Remember me\n\nactionable-safe-admission-evidence\n', 'utf8');

    try {
      const result = await stage(
        'remember-context-action',
        vscode.commands.executeCommand('llmWiki.rememberActiveFile', vscode.Uri.file(sourcePath)),
        20000
      );
      assert.match(String(result || ''), /LLM_WIKI_REMEMBER_RESULT/);
      assert.match(String(result || ''), /authority=human_confirmed_source_admission|authority=existing_source_reuse/);
      const rawRoot = path.join(wikiRoot, 'raw');
      const admitted = fs.existsSync(rawRoot)
        ? fs.readdirSync(rawRoot, { recursive: true }).filter((name) => String(name).endsWith('.bin'))
        : [];
      assert.ok(admitted.length >= 1, 'contextual remember did not create canonical raw evidence');
    } finally {
      fs.rmSync(sourcePath, { force: true });
    }
  });

  test('discovers forgotten-topic current evidence through the real VS Code-to-core bridge', async () => {
    const { folder } = await resetAndEnable();
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    const alphaPath = path.join(folder.uri.fsPath, 'runtime-product-alpha.md');
    const betaPath = path.join(folder.uri.fsPath, 'runtime-product-beta.md');
    fs.writeFileSync(alphaPath, '# Alpha\n\nunique-amber-orchid product discovery evidence\n', 'utf8');
    fs.writeFileSync(betaPath, '# Beta\n\nseparate cobalt evidence\n', 'utf8');

    try {
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
