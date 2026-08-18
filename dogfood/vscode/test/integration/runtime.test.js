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
        timer = setTimeout(() => reject(new Error(`VS-RUNTIME-STAGE timeout=${label}`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function workspace() {
  const folder = (vscode.workspace.workspaceFolders || [])[0];
  assert.ok(folder, 'integration test workspace is not open');
  return { folder, wikiRoot: path.join(folder.uri.fsPath, '.wiki-lab') };
}

async function resetWorkspace() {
  const { wikiRoot } = workspace();
  try {
    await vscode.commands.executeCommand('llmWiki.disableWorkspace');
  } catch (_) {}
  fs.rmSync(wikiRoot, { recursive: true, force: true });
  return wikiRoot;
}

async function enableWorkspace() {
  const result = await stage('enable-workspace', vscode.commands.executeCommand('llmWiki.enableWorkspace'));
  assert.equal(result, true, 'explicit workspace opt-in did not succeed in Extension Host test mode');
  const { wikiRoot } = workspace();
  assert.ok(fs.existsSync(path.join(wikiRoot, 'workspace-opt-in.json')), 'explicit opt-in marker was not created');
  return wikiRoot;
}

suite('LLM Wiki Dogfood Extension Host', () => {
  test('loads lifecycle surface without implicitly initializing the workspace', async () => {
    const { wikiRoot } = workspace();
    fs.rmSync(wikiRoot, { recursive: true, force: true });

    const extension = vscode.extensions.getExtension('llm-wiki-lab.llm-wiki-dogfood');
    assert.ok(extension, 'development extension was not discovered by VS Code');
    await extension.activate();
    assert.equal(extension.isActive, true, 'extension did not activate');

    assert.equal(fs.existsSync(wikiRoot), false, 'extension activation must not initialize a Wiki store');
    const result = await vscode.commands.executeCommand('llmWiki.doctor');
    assert.ok(result, 'Doctor did not return its sanitized readiness result');
    assert.equal(result.storeInitialized, false);
    assert.equal(result.workspaceEnabled, false);
    assert.equal(result.coreReady, false);
    assert.equal(result.localReady, false);
    assert.equal(result.realisticDogfoodReady, false);
    assert.equal(fs.existsSync(wikiRoot), false, 'Doctor must not initialize or mutate an uninitialized workspace');
  });

  test('explicit Initialize Workspace creates the store and workspace opt-in marker', async () => {
    const wikiRoot = await resetWorkspace();
    await enableWorkspace();

    const configPath = path.join(wikiRoot, 'config.json');
    assert.ok(fs.existsSync(configPath), 'Initialize Workspace did not initialize the local Wiki core');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    assert.equal(config.compiled_provider, 'disabled');
    assert.equal(config.format, 'llm-wiki-dogfood-v0');

    const marker = JSON.parse(fs.readFileSync(path.join(wikiRoot, 'workspace-opt-in.json'), 'utf8'));
    assert.equal(marker.format, 'llm-wiki-workspace-opt-in-v1');
    assert.equal(marker.enabled, true);

    const result = await vscode.commands.executeCommand('llmWiki.doctor');
    assert.equal(result.storeInitialized, true);
    assert.equal(result.workspaceEnabled, true);
    assert.equal(result.coreReady, true);
    assert.equal(result.integrityReady, true);
    assert.equal(result.gitSafety, 'PROTECTED');
    assert.equal(result.realisticDogfoodReady, true);
  });

  test('Disable Workspace preserves the store but removes explicit opt-in', async () => {
    const wikiRoot = await resetWorkspace();
    await enableWorkspace();
    const manifestBefore = fs.readFileSync(path.join(wikiRoot, 'manifest.jsonl'));

    const disabled = await stage('disable-workspace', vscode.commands.executeCommand('llmWiki.disableWorkspace'));
    assert.equal(disabled, true);
    assert.equal(fs.existsSync(path.join(wikiRoot, 'workspace-opt-in.json')), false, 'disable must remove only the opt-in marker');
    assert.ok(fs.existsSync(path.join(wikiRoot, 'config.json')), 'disable must preserve the Wiki store');
    assert.deepEqual(fs.readFileSync(path.join(wikiRoot, 'manifest.jsonl')), manifestBefore, 'disable must not mutate canonical history');

    const result = await vscode.commands.executeCommand('llmWiki.doctor');
    assert.equal(result.storeInitialized, true);
    assert.equal(result.workspaceEnabled, false);
    assert.equal(result.realisticDogfoodReady, false);
  });

  test('Doctor detects a torn canonical manifest without repairing or replaying its prefix', async () => {
    const wikiRoot = await resetWorkspace();
    await enableWorkspace();

    const manifest = path.join(wikiRoot, 'manifest.jsonl');
    fs.writeFileSync(manifest, '{"event":"partial"', 'utf8');
    const before = fs.readFileSync(manifest);

    const result = await vscode.commands.executeCommand('llmWiki.doctor');

    assert.equal(result.coreReady, true);
    assert.equal(result.integrityReady, false);
    assert.equal(result.manifestIntegrityStatus, 'torn_tail');
    assert.equal(result.rawIntegrityStatus, 'not_checked_manifest_damaged');
    assert.equal(result.localReady, false);
    assert.equal(result.realisticDogfoodReady, false);
    assert.deepEqual(fs.readFileSync(manifest), before, 'Doctor must not truncate or repair the torn manifest');
  });

  test('Doctor detects a missing initialized manifest without recreating empty history', async () => {
    const wikiRoot = await resetWorkspace();
    await enableWorkspace();

    const manifest = path.join(wikiRoot, 'manifest.jsonl');
    const rawSentinel = path.join(wikiRoot, 'raw', 'surviving-sentinel.txt');
    fs.writeFileSync(rawSentinel, 'surviving raw bytes', 'utf8');
    fs.rmSync(manifest, { force: true });
    assert.equal(fs.existsSync(manifest), false);

    const result = await vscode.commands.executeCommand('llmWiki.doctor');

    assert.equal(result.coreReady, true);
    assert.equal(result.integrityReady, false);
    assert.equal(result.manifestIntegrityStatus, 'missing');
    assert.equal(result.rawIntegrityStatus, 'not_checked_manifest_missing');
    assert.equal(result.localReady, false);
    assert.equal(result.realisticDogfoodReady, false);
    assert.equal(fs.existsSync(manifest), false, 'Doctor must not recreate missing canonical history');
    assert.equal(fs.readFileSync(rawSentinel, 'utf8'), 'surviving raw bytes', 'Doctor must not reinterpret or mutate surviving raw bytes');
  });

  test('Doctor detects a missing referenced raw object while canonical logs remain clean', async () => {
    const wikiRoot = await resetWorkspace();
    await enableWorkspace();

    const sha = '0'.repeat(64);
    const manifest = path.join(wikiRoot, 'manifest.jsonl');
    const row = {
      event: 'ingest',
      record_schema: 'llm-wiki-source-v1',
      recorded_at: '2026-08-15T00:00:00+00:00',
      source_id: 'src-doctor-missing-raw',
      object_id: `obj-${sha}`,
      sha256: sha,
      origin_id: null,
      name: 'missing.md',
      size_bytes: 12,
      duplicate_content: false,
    };
    fs.writeFileSync(manifest, `${JSON.stringify(row)}\n`, 'utf8');

    const result = await vscode.commands.executeCommand('llmWiki.doctor');

    assert.equal(result.coreReady, true);
    assert.equal(result.integrityReady, false);
    assert.equal(result.manifestIntegrityStatus, 'clean');
    assert.equal(result.provenanceIntegrityStatus, 'clean');
    assert.equal(result.rawIntegrityStatus, 'failed');
    assert.equal(result.localReady, false);
    assert.equal(result.realisticDogfoodReady, false);
    assert.equal(fs.existsSync(path.join(wikiRoot, 'raw', `${sha}.txt`)), false, 'Doctor must not invent missing raw evidence');
  });

  test('runs topic -> active-file ingest -> search -> read-only provenance after explicit opt-in', async () => {
    const { folder } = workspace();
    const wikiRoot = await resetWorkspace();
    const evidencePath = path.join(folder.uri.fsPath, 'runtime-vscode-evidence.md');
    fs.writeFileSync(evidencePath, '# Runtime evidence\n\nThe cedar quota decision is 41 units because the project preferred bounded cache growth.\n', 'utf8');

    try {
      await enableWorkspace();
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
