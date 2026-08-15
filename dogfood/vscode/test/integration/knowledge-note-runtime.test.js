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
        timer = setTimeout(() => reject(new Error(`VS-KNOWLEDGE-NOTE-STAGE timeout=${label}`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

suite('LLM Wiki 0.1.7 Human Knowledge Note', () => {
  test('opens an untitled human-owned Markdown draft without canonical mutation', async () => {
    const folder = (vscode.workspace.workspaceFolders || [])[0];
    assert.ok(folder, 'integration test workspace is not open');
    const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
    fs.rmSync(wikiRoot, { recursive: true, force: true });

    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'LLM Wiki extension was not discovered');
    await extension.activate();

    const commands = new Set(await vscode.commands.getCommands(true));
    assert.ok(commands.has('llmWiki.newKnowledgeNote'), 'human Knowledge Note command is not registered');

    await stage('init', vscode.commands.executeCommand('llmWiki.init'));
    const manifestPath = path.join(wikiRoot, 'manifest.jsonl');
    const manifestBefore = fs.readFileSync(manifestPath);
    const eventsPath = path.join(wikiRoot, 'workload-events.jsonl');
    assert.equal(fs.existsSync(eventsPath), false, 'fresh init should not create workload telemetry');

    await stage(
      'new-human-knowledge-note',
      vscode.commands.executeCommand('llmWiki.newKnowledgeNote', { title: 'Why gateway timeout is 15 seconds' })
    );

    const active = vscode.window.activeTextEditor;
    assert.ok(active, 'Knowledge Note command did not open an editor');
    assert.equal(active.document.isUntitled, true, 'Knowledge Note v0 must remain a user-owned unsaved draft');
    assert.equal(active.document.languageId, 'markdown');
    const text = active.document.getText();
    assert.match(text, /^# Why gateway timeout is 15 seconds/m);
    assert.match(text, /Human-owned draft\. Saving this file does not ingest, promote, or mutate LLM Wiki state\./);
    assert.match(text, /^## Current statement$/m);
    assert.match(text, /^## Why \/ reasoning$/m);
    assert.match(text, /^## Supporting evidence$/m);
    assert.match(text, /^## Open questions$/m);
    assert.doesNotMatch(text, /^Type:/m, 'v0 must not invent a knowledge ontology');
    assert.doesNotMatch(text, /^Status:/m, 'v0 must not invent a knowledge lifecycle schema');

    assert.deepEqual(fs.readFileSync(manifestPath), manifestBefore, 'draft creation must not mutate canonical manifest');
    assert.equal(fs.existsSync(eventsPath), false, 'draft creation must not manufacture E013 telemetry');
  });
});
