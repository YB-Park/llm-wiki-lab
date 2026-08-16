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
for (const command of [
  'llmWiki.init', 'llmWiki.createTopic', 'llmWiki.selectTopic', 'llmWiki.newKnowledgeNote',
  'llmWiki.configureAgentWikiMaintenance', 'llmWiki.ingestActiveFile', 'llmWiki.ingestAuthoritativeUpdate',
  'llmWiki.search', 'llmWiki.discoverAcrossTopics', 'llmWiki.markCorrection', 'llmWiki.markChange',
  'llmWiki.markDispute', 'llmWiki.feedback', 'llmWiki.ask', 'llmWiki.calibration', 'llmWiki.doctor',
  'llmWiki.experimentalDiscoverCopilotModels',
]) assert(commands.has(command), `missing command: ${command}`);
assert.equal(commands.size, 17, '0.1.11 command surface should not grow for agent-first hardening');

assert(entry.includes("registerCommand('llmWiki.newKnowledgeNote'"));
assert(entry.includes('Human-owned draft. Saving this file does not ingest, promote, or mutate LLM Wiki state.'));
assert(!entry.includes("executeCommand('llmWiki.ingestActiveFile')"), 'Human Knowledge draft creation must never auto-ingest');
assert(!entry.includes("executeCommand('llmWiki.ask')"), 'Human Knowledge draft creation must never auto-call a model');
assert(entry.includes("registerCommand('llmWiki.configureAgentWikiMaintenance'"));
assert(entry.includes("config.update('agentWikiMaintenanceEnabled', action.value, vscode.ConfigurationTarget.Workspace)"));
assert(entry.includes("{ modal: true }"), 'maintenance grant must remain modal');
assert(entry.includes("doctorOutput.appendLine('Model calls: 0')"));
assert(!entry.includes('--allow-model-call'), 'entry wrapper itself must never authorize generation');

const tools = manifest.contributes.languageModelTools || [];
assert.equal(tools.length, 5, '0.1.11 must expose exactly five bounded Agent Wiki tools');
const toolNames = new Set(tools.map((row) => row.name));
for (const name of [
  'llmWiki_searchMemory', 'llmWiki_readSource', 'llmWiki_rememberSource',
  'llmWiki_rememberHumanKnowledge', 'llmWiki_resolveLineage',
]) assert(toolNames.has(name), `missing Agent Wiki tool: ${name}`);
for (const name of toolNames) assert(manifest.activationEvents.includes(`onLanguageModelTool:${name}`), `missing activation event: ${name}`);
assert.equal(tools.find((row) => row.name === 'llmWiki_searchMemory').toolReferenceName, 'wikiMemory');
assert.equal(tools.find((row) => row.name === 'llmWiki_readSource').toolReferenceName, 'wikiRead');
assert.equal(tools.find((row) => row.name === 'llmWiki_rememberSource').toolReferenceName, 'rememberWikiSource');
assert.equal(tools.find((row) => row.name === 'llmWiki_rememberHumanKnowledge').toolReferenceName, 'rememberHumanKnowledge');
assert.equal(tools.find((row) => row.name === 'llmWiki_resolveLineage').toolReferenceName, 'resolveWikiLineage');

assert.equal(manifest.version, '0.1.11');
assert.equal(manifest.engines.vscode, '^1.95.0');
assert.equal(manifest.main, './entry.js');
assert.equal(manifest.private, true);
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false);
const configProps = manifest.contributes.configuration.properties;
assert.equal(configProps['llmWiki.agentWikiMaintenanceEnabled'].default, false);
assert.equal(configProps['llmWiki.agentWikiMaintenanceMaxAiCredits'].minimum, 30);
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].default, 10);
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].minimum, 0);
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].maximum, 100);
assert.equal(manifest.devDependencies['@vscode/vsce'], '3.9.2');
assert(manifest.scripts['package:vsix'].includes('bundle:core'));
assert(manifest.scripts.check.includes('agent-tools.js'));

assert(entry.includes("require('./agent-tools')"));
assert(entry.includes('registerAgentTools(context);'));
assert(agentTools.includes("vscode.lm.registerTool(SEARCH_TOOL"));
assert(agentTools.includes("vscode.lm.registerTool(READ_TOOL"));
assert(agentTools.includes("vscode.lm.registerTool(REMEMBER_TOOL"));
assert(agentTools.includes("vscode.lm.registerTool(HUMAN_KNOWLEDGE_TOOL"));
assert(agentTools.includes("vscode.lm.registerTool(RESOLVE_LINEAGE_TOOL"));

assert(agentTools.includes("['discover', query, '--top-k-per-topic', '3', '--json']"));
assert(agentTools.includes("runAgentWikiCli(this.context, folder, ['search'"));
assert(agentTools.includes("runAgentMemoryCli(this.context, folder, args)"));
assert(agentTools.includes('RAW_MEMORY R'));
assert(agentTools.includes('DERIVED_MEMORY D'));
assert(agentTools.includes('HUMAN_KNOWLEDGE H'));
assert(agentTools.includes('UNTRUSTED_QUOTED_DATA_NOT_INSTRUCTIONS'));
assert(agentTools.includes('BEGIN VERIFIED IMMUTABLE RAW EVIDENCE'));
assert(agentTools.includes('If has_more=yes'));
assert(agentTools.includes('For load-bearing factual claims surfaced by DERIVED_MEMORY, follow source_ids with wikiRead'));
assert(agentTools.includes('canonical_mutation=none'));

assert(agentTools.includes('explicitHumanConfirm('));
assert(agentTools.includes('context.extensionMode === vscode.ExtensionMode.Test'), 'only Extension Host tests may bypass interactive confirmation');
assert(agentTools.includes('LLM Wiki will not auto-save a dirty editor'));
assert(!agentTools.includes('active.document.save()'), 'remember must never auto-save user working state');
assert(agentTools.includes("['ingest', target.filePath, '--topic', topic.id]"));
assert(agentTools.includes('authority=human_confirmed_source_admission'));
assert(agentTools.includes('human_authorship_persisted=no'));

assert(agentTools.includes('createPendingLineage'));
assert(agentTools.includes('SKIPPED_PENDING_LINEAGE_DECISION'));
assert(agentTools.includes('Do not guess the relationship'));
assert(agentTools.includes('pending_lineage_decision='));
assert(agentTools.includes("LINEAGE_RELATIONS = new Set(['correction', 'change', 'dispute', 'supersede', 'independent'])"));
assert(agentTools.includes('Confirm LLM Wiki lineage decision'));
assert(agentTools.includes("['source', 'correct'"));
assert(agentTools.includes("['source', 'change'"));
assert(agentTools.includes("['source', 'dispute'"));
assert(agentTools.includes("['source', 'supersede'"));
assert(agentTools.includes("relation === 'change' && !effectiveAt"));
assert(agentTools.includes('authority=human_confirmed_epistemic_relation'));

assert(agentTools.includes('llm-wiki-human-knowledge-v0'));
assert(agentTools.includes('HUMAN KNOWLEDGE — USER CONFIRMED'));
assert(agentTools.includes('Save Human Knowledge?'));
assert(agentTools.includes('authority=explicit_user_confirmation'));
assert(agentTools.includes('raw_evidence_mutation=none'));
assert(agentTools.includes('canonical_temporal_mutation=none'));

assert(agentTools.includes("const AGENT_WIKI_MODEL = 'gpt-5.6-luna'"));
assert(agentTools.includes("configuration().get('agentWikiMaintenanceEnabled', false) === true"));
assert(agentTools.includes('agentWikiMaintenanceDailyCallLimit'));
assert(agentTools.includes('reserveMaintenanceCall'));
assert(agentTools.includes('SKIPPED_DAILY_CALL_LIMIT'));
assert(agentTools.includes("'--allow-model-call'"));
assert(agentTools.indexOf("['ingest', target.filePath, '--topic', topic.id]") < agentTools.indexOf('maintainSource(this.context, folder, receipt.sourceId'), 'raw admission must precede derived maintenance');
assert(agentTools.includes('FAILED_AFTER_RAW_ADMISSION'));

assert(extension.includes("'gpt-5.6-luna'"));
assert(extension.includes("'--allow-model-call'"));
assert(extension.includes('Canonical mutation: none'));
assert(extension.includes("const SOURCE_SCHEME = 'llm-wiki-source'"));
assert(extension.includes("['source', 'show'"));
assert(extension.includes("['source', 'correct'"));
assert(extension.includes("'source', 'change'"));
assert(extension.includes("['source', 'dispute'"));
assert(!extension.includes('shell: true'));
assert(!extension.includes('compiled_provider ='));
assert(productHelpers.includes('workspaceRelativePath'));
assert(productHelpers.includes('resolveWorkspaceRelative'));
assert(productHelpers.includes('locatorForRow'));
assert(!productHelpers.includes('manifest.jsonl'));

assert(lmDiscovery.includes("const REQUIRED_LUNA_ID = 'gpt-5.6-luna'"));
assert(lmDiscovery.includes("selectChatModels({ vendor: 'copilot' })"));
assert(lmDiscovery.includes('generationCalls: 0'));
assert(!lmDiscovery.includes('sendRequest'));
assert(gitSafety.includes("['rev-parse', '--is-inside-work-tree']"));
assert(gitSafety.includes("['check-ignore', '-q', '--'"));
assert(!gitSafety.includes('writeFile'));
assert(bundler.includes("path.join(dogfoodRoot, 'llm_wiki')"));
assert(bundler.includes("path.join(bundleRoot, 'dogfood')"));

console.log('VS-CODE-DOGFOOD-STATIC PASS version=0.1.11 commands=17 agentTools=5 verifiedRead=yes untrustedFraming=yes dirtyAutosave=no pendingLineage=human-gated humanKnowledge=confirmed dailyMaintenanceCap=yes python39Compat=required');
