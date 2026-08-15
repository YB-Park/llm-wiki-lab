'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const entry = fs.readFileSync(path.join(root, 'entry.js'), 'utf8');
const extension = fs.readFileSync(path.join(root, 'extension.js'), 'utf8');
const productHelpers = fs.readFileSync(path.join(root, 'product-helpers.js'), 'utf8');
const gitSafety = fs.readFileSync(path.join(root, 'git-safety.js'), 'utf8');
const lmDiscovery = fs.readFileSync(path.join(root, 'lm-discovery.js'), 'utf8');
const bundler = fs.readFileSync(path.join(root, 'scripts', 'bundle-core.js'), 'utf8');

const commands = new Set((manifest.contributes.commands || []).map((row) => row.command));
const extensionCommands = [
  'llmWiki.init',
  'llmWiki.createTopic',
  'llmWiki.selectTopic',
  'llmWiki.ingestActiveFile',
  'llmWiki.ingestAuthoritativeUpdate',
  'llmWiki.search',
  'llmWiki.discoverAcrossTopics',
  'llmWiki.markCorrection',
  'llmWiki.markChange',
  'llmWiki.markDispute',
  'llmWiki.feedback',
  'llmWiki.ask',
  'llmWiki.calibration',
];
for (const command of extensionCommands) {
  assert(commands.has(command), `missing command: ${command}`);
  assert(extension.includes(`'${command}'`), `command not wired in extension.js: ${command}`);
}
assert(commands.has('llmWiki.newKnowledgeNote'), 'missing human Knowledge Note command');
assert(entry.includes("registerCommand('llmWiki.newKnowledgeNote'"), 'Knowledge Note command not wired in entry.js');
assert(entry.includes('Human-owned draft. Saving this file does not ingest, promote, or mutate LLM Wiki state.'), 'Knowledge Note must state no Wiki mutation');
assert(entry.includes("language: 'markdown'"), 'Knowledge Note must open as Markdown');
assert(!entry.includes("executeCommand('llmWiki.ingestActiveFile')"), 'Knowledge Note creation must never auto-ingest');
assert(!entry.includes("executeCommand('llmWiki.ask')"), 'Knowledge Note creation must never auto-call the model');
assert(commands.has('llmWiki.doctor'), 'missing Doctor command');
assert(entry.includes("'llmWiki.doctor'"), 'Doctor command not wired in entry.js');
assert(commands.has('llmWiki.experimentalDiscoverCopilotModels'), 'missing experimental LM discovery command');
assert(entry.includes("'llmWiki.experimentalDiscoverCopilotModels'"), 'LM discovery command not wired in entry.js');
assert.equal(commands.size, 16, '0.1.7 command surface count changed unexpectedly');

assert.equal(manifest.version, '0.1.7');
assert.equal(manifest.main, './entry.js');
assert.equal(manifest.private, true);
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false, 'extension must not run in untrusted workspaces');
assert.equal(manifest.contributes.configuration.properties['llmWiki.maxAiCredits'].default, 30);
assert.equal(manifest.devDependencies['@vscode/vsce'], '3.9.2', 'VSIX packager version must remain pinned');
assert(manifest.scripts['package:vsix'].includes('bundle:core'), 'VSIX packaging must bundle the shared core first');
assert(manifest.scripts.check.includes('product-helpers.js'), 'static check must cover local navigation helper');

assert(extension.includes("'gpt-5.6-luna'"), 'Luna must remain the pinned dogfood model');
assert(extension.includes("'--allow-model-call'"), 'Ask path must explicitly opt into the model call');
assert(extension.includes('{ modal: true }'), 'trust-sensitive paths must use explicit modal confirmation where required');
assert(extension.includes('Canonical mutation: none'), 'Ask output must state that it is read-only');
assert(extension.includes("register('llmWiki.ask', () => askLuna(context));"), 'Ask command must not accept programmatic options that could bypass consent');
assert(extension.includes("register('llmWiki.createTopic', (options)"), 'Create Topic should support safe programmatic local-only validation');
assert(extension.includes("register('llmWiki.search', (options)"), 'Search should support safe programmatic local-only validation');
assert(extension.includes("register('llmWiki.discoverAcrossTopics', (options)"), 'cross-topic discovery should support safe programmatic validation');
assert(extension.includes('openFirstResult === true'), 'programmatic search may open provenance without UI monkeypatching');
assert(!extension.includes('allowModelCall'), 'no command-option model authorization flag is permitted');
assert(!extension.includes('skipConsent'), 'no command-option consent bypass is permitted');
assert(extension.includes("const SOURCE_SCHEME = 'llm-wiki-source'"), 'provenance must use a read-only virtual document scheme');
assert(extension.includes("['source', 'show'"), 'opening provenance must go through the core source-show path');
assert(extension.includes("['calibration', 'export']"), 'calibration summary must come from the sanitized core export');
assert(extension.includes("['discover', query.trim(), '--json']"), 'forgotten-topic discovery must use the current-view discovery core path');
assert(extension.includes("['source', 'correct'"), 'VS Code correction must call the explicit typed core operation');
assert(extension.includes("'source', 'change'"), 'VS Code change must call the explicit typed core operation');
assert(extension.includes("['source', 'dispute'"), 'VS Code dispute must call the explicit typed core operation');
assert(extension.includes("['feedback', outcome, '--topic'"), 'VS Code feedback must use fixed-code core telemetry');
assert(extension.includes("path.resolve(context.extensionPath, 'python')"), 'installed extension must look for the generated bundled core');
assert(extension.includes("path.resolve(context.extensionPath, '..', '..')"), 'development extension must retain the shared repository-core fallback');
assert(!extension.includes('shell: true'), 'extension must not invoke CLI through a shell');
assert(!extension.includes('compiled_provider ='), 'extension must not implement or enable a compiled provider');

assert(extension.includes('SOURCE_LOCATORS_KEY'), 'workspace navigation hints must be a separate extension-local layer');
assert(extension.includes('sha256(fs.readFileSync(target))'), 'original workspace source must be content-verified before navigation');
assert(extension.includes('opening immutable evidence snapshot instead'), 'changed/missing workspace source must fall back to immutable evidence');
assert(productHelpers.includes('workspaceRelativePath'), 'navigation helper must store relative workspace locators');
assert(productHelpers.includes('resolveWorkspaceRelative'), 'navigation helper must constrain locators to the workspace');
assert(productHelpers.includes('locatorForRow'), 'navigation helper must bind locator to evidence source/SHA');
assert(!productHelpers.includes('manifest.jsonl'), 'navigation helper must not write canonical manifest identity');

assert(entry.includes("executeCommand('llmWiki.init')"), 'Doctor must reuse the real extension-to-core boundary');
assert(entry.includes("executableAvailable('copilot', ['--version']"), 'Doctor may only probe Copilot availability/version');
assert(entry.includes("doctorOutput.appendLine('Model calls: 0')"), 'Doctor must state zero model calls');
assert(entry.includes('classifyGitSafety'), 'Doctor must classify Git raw-store safety');
assert(entry.includes('Git raw-store safety:'), 'Doctor must report only the Git-safety classification');
assert(entry.includes('Realistic evidence dogfood:'), 'Doctor must distinguish core readiness from safe evidence readiness');
assert(!entry.includes('--allow-model-call'), 'entry wrapper must never authorize a model call');
assert(!entry.includes('sendRequest'), 'entry wrapper must not generate via VS Code LM API during discovery spike');
assert(!entry.includes('process.env'), 'Doctor/discovery wrapper must not inspect environment metadata');

assert(lmDiscovery.includes("const REQUIRED_LUNA_ID = 'gpt-5.6-luna'"), 'LM discovery must use exact pinned Luna identifier');
assert(lmDiscovery.includes("selectChatModels({ vendor: 'copilot' })"), 'LM discovery must query only Copilot model metadata');
assert(lmDiscovery.includes('generationCalls: 0'), 'LM discovery must report zero generation calls');
assert(lmDiscovery.includes('row.id === REQUIRED_LUNA_ID'), 'LM discovery must test exact id match');
assert(lmDiscovery.includes('row.family === REQUIRED_LUNA_ID'), 'LM discovery must test exact family match');
assert(!lmDiscovery.includes('sendRequest'), 'LM discovery must never generate text');
assert(!lmDiscovery.includes('includes(REQUIRED_LUNA_ID)'), 'LM discovery must not use fuzzy/substring Luna matching');
assert(!lmDiscovery.includes('toLowerCase'), 'LM discovery must not normalize fuzzy name matches into acceptance');

assert(gitSafety.includes("['rev-parse', '--is-inside-work-tree']"), 'Git safety must detect local work-tree membership deterministically');
assert(gitSafety.includes("['check-ignore', '-q', '--'"), 'Git safety must use local ignore inspection');
assert(gitSafety.includes("return 'NOT_GIT'"), 'Git safety must distinguish non-Git workspaces');
assert(gitSafety.includes("return 'UNPROTECTED'"), 'Git safety must distinguish unprotected stores');
assert(gitSafety.includes("return ignored ? 'PROTECTED' : 'UNPROTECTED'"), 'Git safety must classify ignored stores as protected');
assert(!gitSafety.includes('writeFile'), 'Git safety classifier must never mutate Git ignore files');
assert(!gitSafety.includes('appendFile'), 'Git safety classifier must never mutate local exclude files');
assert(!gitSafety.includes("'add'"), 'Git safety classifier must never stage files');
assert(!gitSafety.includes('process.env'), 'Git safety classifier must not inspect environment metadata');

assert(bundler.includes("path.join(dogfoodRoot, 'llm_wiki')"), 'bundler must copy from the shared core source of truth');
assert(bundler.includes("path.join(bundleRoot, 'dogfood')"), 'bundler must preserve the dogfood Python package layout');

console.log('VS-CODE-DOGFOOD-STATIC PASS version=0.1.7 commands=16 knowledgeNote=human-owned-no-auto-mutation productP1P4=sealed citationBoundary=core-bundled lmDiscoveryGeneration=0 exactLunaOnly=yes doctorModelCalls=0 gitSafety=read-only consentBypass=no bundledCore=generated compiledProvider=not-implemented');
