'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const vscode = require('vscode');

function toolText(result) {
  return result.content
    .filter((part) => part instanceof vscode.LanguageModelTextPart)
    .map((part) => part.value)
    .join('\n');
}

function field(text, name) {
  const match = String(text).match(new RegExp(`^${name}=([^\\n]*)$`, 'm'));
  return match ? match[1].trim() : '';
}

function firstMemorySourceId(text) {
  const value = (String(text).match(/^source_ids=([^\n]+)$/m) || [])[1];
  assert.ok(value, 'wikiMemory result did not expose source_ids');
  const ids = value.split(',').map((item) => item.trim()).filter(Boolean);
  assert.ok(ids.length > 0, 'wikiMemory source_ids was empty');
  return ids[0];
}

function escapedRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function treeSnapshot(root) {
  const rows = [];
  const visit = (target, relative) => {
    const stat = fs.statSync(target);
    const mode = stat.mode & 0o777;
    if (stat.isDirectory()) {
      rows.push({ relative, kind: 'dir', mode });
      for (const name of fs.readdirSync(target).sort()) {
        visit(path.join(target, name), relative === '.' ? name : `${relative}/${name}`);
      }
      return;
    }
    if (stat.isFile()) {
      rows.push({
        relative,
        kind: 'file',
        mode,
        sha256: crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex'),
      });
    }
  };
  visit(root, '.');
  return rows;
}

async function resetAndEnable() {
  const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
  assert.ok(extension, 'development extension was not discovered by VS Code');
  await extension.activate();
  const folder = (vscode.workspace.workspaceFolders || [])[0];
  assert.ok(folder);
  const wikiRoot = path.join(folder.uri.fsPath, '.wiki-lab');
  try { await vscode.commands.executeCommand('llmWiki.disableWorkspace'); } catch (_) {}
  fs.rmSync(wikiRoot, { recursive: true, force: true });
  const enabled = await vscode.commands.executeCommand('llmWiki.enableWorkspace');
  assert.equal(enabled, true);
  return { folder, wikiRoot };
}

function python() {
  return process.platform === 'win32' ? 'python' : 'python3';
}

function repoRoot() {
  return path.resolve(__dirname, '..', '..', '..', '..');
}

function runCore(root, args) {
  return execFileSync(
    python(),
    ['-m', 'dogfood.llm_wiki.cli', '--root', root, ...args],
    { cwd: repoRoot(), encoding: 'utf8', windowsHide: true }
  );
}

function externalStoreWithEvidence() {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-f1-external-'));
  const root = path.join(parent, '.wiki-lab');
  const evidence = path.join(parent, 'external-authority.md');
  fs.writeFileSync(evidence, 'Project A decided the orchid retry budget is 914 because rollback cost dominated.\n', 'utf8');
  runCore(root, ['init']);
  runCore(root, ['topic', 'add', 'external-f1']);
  runCore(root, ['ingest', evidence, '--topic', 'external-f1']);
  const rows = runCore(root, ['discover', 'orchid retry budget', '--top-k-per-topic', '3', '--json'])
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line));
  assert.ok(rows.length > 0, 'external store discover produced no source');
  const sourceId = String((rows[0].source_ids || [rows[0].source_id])[0] || '');
  assert.match(sourceId, /^src-/);

  if (process.platform !== 'win32') {
    fs.chmodSync(root, 0o755);
    fs.chmodSync(path.join(root, 'raw'), 0o755);
    for (const name of ['config.json', 'manifest.jsonl', 'topics.json']) fs.chmodSync(path.join(root, name), 0o644);
  }
  return { parent, root, sourceId };
}

suite('LLM Wiki Personal Wiki F1', () => {
  test('named-store grants, strict read-only isolation, scoped provenance, and write isolation survive Extension Host lifecycle', async () => {
    const { folder, wikiRoot } = await resetAndEnable();
    const external = externalStoreWithEvidence();
    const currentFile = path.join(folder.uri.fsPath, 'f1-current-only.md');
    const sitecustomize = path.join(folder.uri.fsPath, 'sitecustomize.py');
    const siteSentinel = path.join(folder.uri.fsPath, 'f1-sitecustomize-ran.txt');
    fs.writeFileSync(currentFile, 'Current project alone contains the sapphire marker 271.\n', 'utf8');
    const config = vscode.workspace.getConfiguration('llmWiki');
    const oldPythonPath = process.env.PYTHONPATH;

    try {
      const registered = await vscode.commands.executeCommand('llmWiki.configurePersonalWikiLibrary', {
        action: 'register',
        root: external.root,
        displayName: 'Project A',
        aliases: ['alpha'],
      });
      assert.ok(registered && registered.storeId);
      const scopeRef = { kind: 'library_store', store_id: registered.storeId };
      assert.doesNotMatch(JSON.stringify(registered), new RegExp(escapedRegex(external.root)));
      const externalBaseline = treeSnapshot(external.root);

      await assert.rejects(
        vscode.lm.invokeTool('llmWiki_readScopedSource', {
          input: { sourceId: external.sourceId, scopeRef, maxChars: 1000 }, toolInvocationToken: undefined,
        }),
        /library_access_disabled/
      );
      assert.deepEqual(treeSnapshot(external.root), externalBaseline, 'authorization failure must not touch the external store');

      const libraryEnabled = await vscode.commands.executeCommand('llmWiki.configurePersonalWikiLibrary', { action: 'enable' });
      assert.equal(libraryEnabled, true);

      const queryDisabled = toolText(await vscode.lm.invokeTool('llmWiki_consultMemory', {
        input: { query: 'What did Project A decide about orchid retries?', store: 'Project A' }, toolInvocationToken: undefined,
      }));
      assert.match(queryDisabled, /state=query_plane_disabled/);
      assert.match(queryDisabled, /model_calls=0/);
      assert.match(queryDisabled, /fallback=none/);
      assert.deepEqual(treeSnapshot(external.root), externalBaseline);

      await config.update('corePath', 'THIS-F1-EXTERNAL-READ-MUST-NOT-USE', vscode.ConfigurationTarget.Workspace);
      await config.update('pythonExecutable', 'THIS-F1-EXTERNAL-READ-MUST-NOT-USE', vscode.ConfigurationTarget.Workspace);
      fs.writeFileSync(sitecustomize, `require = None\nopen(${JSON.stringify(siteSentinel)}, 'w').write('ran')\n`, 'utf8');
      process.env.PYTHONPATH = folder.uri.fsPath;

      const externalRead = toolText(await vscode.lm.invokeTool('llmWiki_readScopedSource', {
        input: { sourceId: external.sourceId, scopeRef, maxChars: 1000 }, toolInvocationToken: undefined,
      }));
      assert.match(externalRead, /LLM_WIKI_SOURCE_READ v3/);
      assert.match(externalRead, /scope=library_store/);
      assert.equal(JSON.parse(field(externalRead, 'scope_ref_json')).store_id, registered.storeId);
      assert.equal(JSON.parse(field(externalRead, 'scope_label_json')), 'Project A');
      assert.match(externalRead, /orchid retry budget is 914/);
      assert.doesNotMatch(externalRead, new RegExp(escapedRegex(external.root)));
      assert.equal(fs.existsSync(siteSentinel), false, 'isolated external reads must ignore current-workspace sitecustomize/PYTHONPATH');
      assert.deepEqual(treeSnapshot(external.root), externalBaseline, 'external provenance reads must be byte- and mode-preserving');

      await config.update('corePath', '', vscode.ConfigurationTarget.Workspace);
      await config.update('pythonExecutable', '', vscode.ConfigurationTarget.Workspace);
      if (oldPythonPath === undefined) delete process.env.PYTHONPATH; else process.env.PYTHONPATH = oldPythonPath;
      fs.rmSync(sitecustomize, { force: true });

      await vscode.commands.executeCommand('llmWiki.createTopic', { label: 'f1-current-only' });
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(currentFile));
      await vscode.window.showTextDocument(doc, { preview: false });
      await vscode.commands.executeCommand('llmWiki.ingestActiveFile');
      assert.deepEqual(treeSnapshot(external.root), externalBaseline, 'current-store source admission must not mutate the external store');
      const currentSearch = toolText(await vscode.lm.invokeTool('llmWiki_searchMemory', {
        input: { query: 'sapphire marker 271', maxResults: 3 }, toolInvocationToken: undefined,
      }));
      const currentSourceId = firstMemorySourceId(currentSearch);
      assert.match(currentSourceId, /^src-/);

      await assert.rejects(
        vscode.lm.invokeTool('llmWiki_readScopedSource', {
          input: { sourceId: currentSourceId, scopeRef, maxChars: 1000 }, toolInvocationToken: undefined,
        }),
        /library_store_source_not_found/,
        'an external scope miss must never retry the same source ID against the current store'
      );
      assert.deepEqual(treeSnapshot(external.root), externalBaseline, 'wrong-scope failure must not touch either fallback store state');

      const hk = toolText(await vscode.lm.invokeTool('llmWiki_rememberHumanKnowledge', {
        input: { statement: 'F1 write isolation test belongs to the current project only.' }, toolInvocationToken: undefined,
      }));
      assert.match(hk, /LLM_WIKI_HUMAN_KNOWLEDGE_RESULT v2/);
      assert.deepEqual(treeSnapshot(external.root), externalBaseline, 'current-store Human Knowledge must not create or modify any external artifact');

      const queryEnabled = await vscode.commands.executeCommand('llmWiki.configureQueryPlane');
      assert.equal(queryEnabled, true);
      const libraryDisabled = await vscode.commands.executeCommand('llmWiki.configurePersonalWikiLibrary', { action: 'disable' });
      assert.equal(libraryDisabled, false);
      const scopeBlocked = toolText(await vscode.lm.invokeTool('llmWiki_consultMemory', {
        input: { query: 'What did Project A decide about orchid retries?', store: 'Project A' }, toolInvocationToken: undefined,
      }));
      assert.match(scopeBlocked, /state=library_scope_blocked/);
      assert.match(scopeBlocked, /failure_json="library_access_disabled"/);
      assert.match(scopeBlocked, /model_calls=0/);
      assert.match(scopeBlocked, /fallback=none/);
      assert.deepEqual(treeSnapshot(external.root), externalBaseline);

      await vscode.commands.executeCommand('llmWiki.configurePersonalWikiLibrary', { action: 'enable' });
      const disabledWorkspace = await vscode.commands.executeCommand('llmWiki.disableWorkspace');
      assert.equal(disabledWorkspace, true);
      await assert.rejects(
        vscode.lm.invokeTool('llmWiki_readScopedSource', {
          input: { sourceId: external.sourceId, scopeRef }, toolInvocationToken: undefined,
        }),
        undefined,
        'workspace disable must make scoped external reads non-invokable'
      );

      const reenabled = await vscode.commands.executeCommand('llmWiki.enableWorkspace');
      assert.equal(reenabled, true);
      await assert.rejects(
        vscode.lm.invokeTool('llmWiki_readScopedSource', {
          input: { sourceId: external.sourceId, scopeRef }, toolInvocationToken: undefined,
        }),
        /library_access_disabled/,
        'workspace opt-in epoch change must invalidate the old library access grant'
      );
      assert.deepEqual(treeSnapshot(external.root), externalBaseline);

      assert.ok(fs.existsSync(path.join(wikiRoot, 'manifest.jsonl')));
      assert.ok(fs.existsSync(path.join(external.root, 'manifest.jsonl')));
    } finally {
      await config.update('corePath', '', vscode.ConfigurationTarget.Workspace);
      await config.update('pythonExecutable', '', vscode.ConfigurationTarget.Workspace);
      if (oldPythonPath === undefined) delete process.env.PYTHONPATH; else process.env.PYTHONPATH = oldPythonPath;
      fs.rmSync(currentFile, { force: true });
      fs.rmSync(sitecustomize, { force: true });
      fs.rmSync(siteSentinel, { force: true });
      fs.rmSync(external.parent, { recursive: true, force: true });
    }
  });
});
