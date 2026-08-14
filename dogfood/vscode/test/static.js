'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const entry = fs.readFileSync(path.join(root, 'entry.js'), 'utf8');
const extension = fs.readFileSync(path.join(root, 'extension.js'), 'utf8');
const bundler = fs.readFileSync(path.join(root, 'scripts', 'bundle-core.js'), 'utf8');

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
assert(commands.has('llmWiki.doctor'), 'missing Doctor command');
assert(entry.includes("'llmWiki.doctor'"), 'Doctor command not wired in entry.js');

assert.equal(manifest.main, './entry.js');
assert.equal(manifest.private, true);
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false, 'extension must not run in untrusted workspaces');
assert.equal(manifest.contributes.configuration.properties['llmWiki.maxAiCredits'].default, 30);
assert.equal(manifest.devDependencies['@vscode/vsce'], '3.9.2', 'VSIX packager version must remain pinned');
assert(manifest.scripts['package:vsix'].includes('bundle:core'), 'VSIX packaging must bundle the shared core first');

assert(extension.includes("'gpt-5.6-luna'"), 'Luna must remain the pinned dogfood model');
assert(extension.includes("'--allow-model-call'"), 'Ask path must explicitly opt into the model call');
assert(extension.includes('{ modal: true }'), 'Ask path must use an explicit modal confirmation');
assert(extension.includes('Canonical mutation: none'), 'Ask output must state that it is read-only');
assert(extension.includes("const SOURCE_SCHEME = 'llm-wiki-source'"), 'provenance must use a read-only virtual document scheme');
assert(extension.includes("['source', 'show'"), 'opening provenance must go through the core source-show path');
assert(extension.includes("['calibration', 'export']"), 'calibration summary must come from the sanitized core export');
assert(extension.includes("path.resolve(context.extensionPath, 'python')"), 'installed extension must look for the generated bundled core');
assert(extension.includes("path.resolve(context.extensionPath, '..', '..')"), 'development extension must retain the shared repository-core fallback');
assert(!extension.includes('shell: true'), 'extension must not invoke CLI through a shell');
assert(!extension.includes('compiled_provider ='), 'extension must not implement or enable a compiled provider');

assert(entry.includes("executeCommand('llmWiki.init')"), 'Doctor must reuse the real extension-to-core boundary');
assert(entry.includes("executableAvailable('copilot', ['--version']"), 'Doctor may only probe Copilot availability/version');
assert(entry.includes("doctorOutput.appendLine('Model calls: 0')"), 'Doctor must state zero model calls');
assert(!entry.includes('--allow-model-call'), 'Doctor wrapper must never authorize a model call');
assert(!entry.includes('gpt-5.6-luna'), 'Doctor wrapper must not invoke or select a model');
assert(!entry.includes('process.env'), 'Doctor output/probing must not inspect environment metadata');

assert(bundler.includes("path.join(dogfoodRoot, 'llm_wiki')"), 'bundler must copy from the shared core source of truth');
assert(bundler.includes("path.join(bundleRoot, 'dogfood')"), 'bundler must preserve the dogfood Python package layout');

console.log('VS-CODE-DOGFOOD-STATIC PASS commands=9 doctorModelCalls=0 trustedWorkspaceOnly=yes model=gpt-5.6-luna bundledCore=generated compiledProvider=not-implemented');
