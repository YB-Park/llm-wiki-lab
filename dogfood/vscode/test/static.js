'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const extension = fs.readFileSync(path.join(root, 'extension.js'), 'utf8');

const commands = new Set((manifest.contributes.commands || []).map((row) => row.command));
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
  assert(commands.has(command), `missing command: ${command}`);
  assert(extension.includes(`'${command}'`), `command not wired in extension.js: ${command}`);
}

assert.equal(manifest.main, './extension.js');
assert.equal(manifest.private, true);
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false, 'extension must not run in untrusted workspaces');
assert.equal(manifest.contributes.configuration.properties['llmWiki.maxAiCredits'].default, 30);

assert(extension.includes("'gpt-5.6-luna'"), 'Luna must remain the pinned dogfood model');
assert(extension.includes("'--allow-model-call'"), 'Ask path must explicitly opt into the model call');
assert(extension.includes('{ modal: true }'), 'Ask path must use an explicit modal confirmation');
assert(extension.includes('Canonical mutation: none'), 'Ask output must state that it is read-only');
assert(extension.includes("const SOURCE_SCHEME = 'llm-wiki-source'"), 'provenance must use a read-only virtual document scheme');
assert(extension.includes("['source', 'show'"), 'opening provenance must go through the core source-show path');
assert(extension.includes("['calibration', 'export']"), 'calibration summary must come from the sanitized core export');
assert(!extension.includes('shell: true'), 'extension must not invoke CLI through a shell');
assert(!extension.includes('compiled_provider ='), 'extension must not implement or enable a compiled provider');

console.log('VS-CODE-DOGFOOD-STATIC PASS commands=8 trustedWorkspaceOnly=yes model=gpt-5.6-luna compiledProvider=not-implemented');
