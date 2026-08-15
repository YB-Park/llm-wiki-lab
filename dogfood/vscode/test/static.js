'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const entry = fs.readFileSync(path.join(root, 'entry.js'), 'utf8');
const extension = fs.readFileSync(path.join(root, 'extension.js'), 'utf8');
const agentTools = fs.readFileSync(path.join(root, 'agent-tools.js'), 'utf8');
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
assert(commands.has('llmWiki.configureAgentWikiMaintenance'), 'missing Agent Wiki maintenance grant command');
assert(entry.includes("registerCommand('llmWiki.configureAgentWikiMaintenance'"), 'maintenance grant command not wired in entry.js');
assert(entry.includes("config.update('agentWikiMaintenanceEnabled', action.value, vscode.ConfigurationTarget.Workspace)"), 'maintenance grant must be workspace-scoped');
assert(entry.includes('After you explicitly remember a source, its admitted bytes may be sent to exact gpt-5.6-luna'), 'maintenance grant must disclose external source exposure');
assert(entry.includes("{ modal: true }"), 'maintenance enable grant must be modal');
assert(commands.has('llmWiki.doctor'), 'missing Doctor command');
assert(entry.includes("'llmWiki.doctor'"), 'Doctor command not wired in entry.js');
assert(commands.has('llmWiki.experimentalDiscoverCopilotModels'), 'missing experimental LM discovery command');
assert(entry.includes("'llmWiki.experimentalDiscoverCopilotModels'"), 'LM discovery command not wired in entry.js');
assert.equal(commands.size, 17, '0.1.10 command surface count changed unexpectedly');

const tools = manifest.contributes.languageModelTools || [];
assert.equal(tools.length, 2, '0.1.10 must expose exactly two bounded Agent Wiki tools');
const toolNames = new Set(tools.map((row) => row.name));
assert(toolNames.has('llmWiki_searchMemory'), 'missing read-only Wiki memory tool');
assert(toolNames.has('llmWiki_rememberSource'), 'missing explicit source-admission tool');
assert(manifest.activationEvents.includes('onLanguageModelTool:llmWiki_searchMemory'), 'search tool must activate extension lazily');
assert(manifest.activationEvents.includes('onLanguageModelTool:llmWiki_rememberSource'), 'remember tool must activate extension lazily');
const searchTool = tools.find((row) => row.name === 'llmWiki_searchMemory');
const rememberTool = tools.find((row) => row.name === 'llmWiki_rememberSource');
assert.equal(searchTool.canBeReferencedInPrompt, true);
assert.equal(searchTool.toolReferenceName, 'wikiMemory');
assert.match(searchTool.modelDescription, /Raw evidence remains the factual\/provenance authority/);
assert.match(searchTool.modelDescription, /derived Agent Wiki notes are synthesis\/navigation aids only/i);
assert.equal(rememberTool.canBeReferencedInPrompt, true);
assert.equal(rememberTool.toolReferenceName, 'rememberWikiSource');
assert.match(rememberTool.modelDescription, /explicitly asks/i);
assert.match(rememberTool.modelDescription, /separately enabled the workspace Agent Wiki maintenance grant/i);
assert.match(rememberTool.modelDescription, /never infers Human Knowledge/i);
assert.match(rememberTool.modelDescription, /cannot perform correction, change, dispute, supersession, or deletion/i);

assert.equal(manifest.version, '0.1.10');
assert.equal(manifest.engines.vscode, '^1.95.0', 'stable Language Model Tool API requires the 1.95+ product floor');
assert.equal(manifest.main, './entry.js');
assert.equal(manifest.private, true);
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false, 'extension must not run in untrusted workspaces');
const configProps = manifest.contributes.configuration.properties;
assert.equal(configProps['llmWiki.maxAiCredits'].default, 30);
assert.equal(configProps['llmWiki.maxAiCredits'].minimum, 30, 'Copilot CLI guard must honor current minimum');
assert.equal(configProps['llmWiki.agentWikiMaintenanceEnabled'].default, false, 'model-backed Agent Wiki maintenance must be off by default');
assert.equal(configProps['llmWiki.agentWikiMaintenanceEnabled'].scope, 'resource', 'maintenance grant must be workspace/resource scoped');
assert.equal(configProps['llmWiki.agentWikiMaintenanceMaxAiCredits'].default, 30);
assert.equal(configProps['llmWiki.agentWikiMaintenanceMaxAiCredits'].minimum, 30);
assert.equal(configProps['llmWiki.agentWikiMaintenanceMaxAiCredits'].maximum, 100);
assert.equal(manifest.devDependencies['@vscode/vsce'], '3.9.2', 'VSIX packager version must remain pinned');
assert(manifest.scripts['package:vsix'].includes('bundle:core'), 'VSIX packaging must bundle the shared core first');
assert(manifest.scripts.check.includes('agent-tools.js'), 'static check must syntax-check Agent Wiki tools');
assert(manifest.scripts.check.includes('product-helpers.js'), 'static check must cover local navigation helper');

assert(entry.includes("require('./agent-tools')"), 'entry wrapper must load Agent Wiki tools');
assert(entry.includes('registerAgentTools(context);'), 'entry wrapper must register Agent Wiki tools on activation');
assert(entry.includes('Agent Wiki maintenance:'), 'Doctor must expose maintenance grant state without making a model call');
assert(agentTools.includes("vscode.lm.registerTool(SEARCH_TOOL"), 'read tool must use stable LM Tool registration');
assert(agentTools.includes("vscode.lm.registerTool(REMEMBER_TOOL"), 'remember tool must use stable LM Tool registration');
assert(agentTools.includes("['discover', query, '--top-k-per-topic', '3', '--json']"), 'read tool must use deterministic current-view raw discovery');
assert(agentTools.includes("runAgentWikiCli(this.context, folder, ['search'"), 'read tool must query derived Agent Wiki notes separately');
assert(agentTools.includes('RAW_MEMORY R'), 'raw evidence must have an explicit memory class');
assert(agentTools.includes('DERIVED_MEMORY D'), 'derived note must have a separate memory class');
assert(agentTools.includes('epistemic_status=canonical_raw_evidence'), 'raw evidence authority must be explicit');
assert(agentTools.includes('epistemic_status=derived_noncanonical_agent_wiki'), 'derived note status must be explicit');
assert(agentTools.includes('DERIVED_MEMORY is model-generated, noncanonical synthesis/navigation aid'), 'derived notes must never masquerade as evidence');
assert(agentTools.includes('authority=read_only'), 'memory tool result must state read-only authority');
assert(agentTools.includes('canonical_mutation=none'), 'memory tool result must state no canonical mutation');
assert(agentTools.includes("['ingest', target.filePath, '--topic', topic.id]"), 'remember must admit raw source before any maintenance');
assert(agentTools.includes('confirmationMessages'), 'source admission must have explicit tool confirmation context');
assert(agentTools.includes("configuration().get('agentWikiMaintenanceEnabled', false) === true"), 'maintenance must have an explicit default-off grant check');
assert(agentTools.includes("'--allow-model-call'"), 'maintenance invocation must explicitly opt into its bounded model call');
assert(agentTools.includes("const AGENT_WIKI_MODEL = 'gpt-5.6-luna'"), 'maintenance model must be exact and product-controlled');
assert(agentTools.includes('FAILED_AFTER_RAW_ADMISSION'), 'maintenance failure must not erase successful raw admission');
assert(agentTools.indexOf("['ingest', target.filePath, '--topic', topic.id]") < agentTools.indexOf("'build', receipt.sourceId"), 'raw admission must happen before model maintenance');
assert(agentTools.includes('human_authorship_persisted=no'), 'source admission/maintenance must not become Human Knowledge authorship');
assert(agentTools.includes('canonical_semantic_mutation=none'), 'source admission/maintenance must not silently perform epistemic mutation');
assert(!agentTools.includes("'source', 'correct'"), 'maintenance tool must not expose correction');
assert(!agentTools.includes("'source', 'change'"), 'maintenance tool must not expose change');
assert(!agentTools.includes("'source', 'dispute'"), 'maintenance tool must not expose dispute');
assert(!agentTools.includes("'source', 'supersede'"), 'maintenance tool must not expose supersession');
assert(!agentTools.includes('persist_inferred_human_commitment'), 'maintenance tools must not manufacture Human Knowledge authorship');

assert(extension.includes("'gpt-5.6-luna'"), 'Luna must remain the pinned explicit Ask dogfood model');
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
assert(!entry.includes('--allow-model-call'), 'entry wrapper must never authorize a model call directly');
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

console.log('VS-CODE-DOGFOOD-STATIC PASS version=0.1.10 commands=17 agentTools=2 ambientRead=raw-plus-derived-labeled explicitRemember=raw-first maintenance=opt-in-luna-source-note maintenanceDefault=off humanAuthorshipProtected=yes semanticMutationProtected=yes python39Compat=required citationBoundary=core-bundled doctorModelCalls=0 gitSafety=read-only bundledCore=generated compiledProvider=not-implemented');
