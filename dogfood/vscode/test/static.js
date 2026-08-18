'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const entry = fs.readFileSync(path.join(root, 'entry.js'), 'utf8');
const extension = fs.readFileSync(path.join(root, 'extension.js'), 'utf8');
const agentTools = fs.readFileSync(path.join(root, 'agent-tools.js'), 'utf8');
const workspaceActivation = fs.readFileSync(path.join(root, 'workspace-activation.js'), 'utf8');
const humanKnowledge = fs.readFileSync(path.join(root, 'human-knowledge.js'), 'utf8');
const productHelpers = fs.readFileSync(path.join(root, 'product-helpers.js'), 'utf8');
const gitSafety = fs.readFileSync(path.join(root, 'git-safety.js'), 'utf8');
const lmDiscovery = fs.readFileSync(path.join(root, 'lm-discovery.js'), 'utf8');
const bundler = fs.readFileSync(path.join(root, 'scripts', 'bundle-core.js'), 'utf8');

function must(label, condition) {
  assert.ok(condition, `STATIC-BOUNDARY ${label}`);
}
function mustNot(label, condition) {
  assert.ok(!condition, `STATIC-BOUNDARY ${label}`);
}

const commands = new Set((manifest.contributes.commands || []).map((row) => row.command));
for (const command of [
  'llmWiki.enableWorkspace', 'llmWiki.disableWorkspace', 'llmWiki.createTopic', 'llmWiki.selectTopic', 'llmWiki.newKnowledgeNote',
  'llmWiki.configureAgentWikiMaintenance', 'llmWiki.ingestActiveFile', 'llmWiki.ingestAuthoritativeUpdate',
  'llmWiki.search', 'llmWiki.discoverAcrossTopics', 'llmWiki.markCorrection', 'llmWiki.markChange',
  'llmWiki.markDispute', 'llmWiki.feedback', 'llmWiki.ask', 'llmWiki.calibration', 'llmWiki.doctor',
  'llmWiki.experimentalDiscoverCopilotModels',
]) must(`command:${command}`, commands.has(command));
assert.equal(commands.size, 18, 'STATIC-BOUNDARY command-count');
mustNot('internal-core-init-not-user-contributed', commands.has('llmWiki.init'));
must('startup-activation', manifest.activationEvents.includes('onStartupFinished'));
must('enable-activation', manifest.activationEvents.includes('onCommand:llmWiki.enableWorkspace'));
must('disable-activation', manifest.activationEvents.includes('onCommand:llmWiki.disableWorkspace'));

must('human-note-command', entry.includes("registerCommand('llmWiki.newKnowledgeNote'"));
must('human-note-boundary-text', entry.includes('Human-owned draft. Saving this file does not ingest, promote, or mutate LLM Wiki state.'));
mustNot('human-note-no-auto-ingest', entry.includes("executeCommand('llmWiki.ingestActiveFile')"));
mustNot('human-note-no-auto-model', entry.includes("executeCommand('llmWiki.ask')"));
must('maintenance-config-command', entry.includes("registerCommand('llmWiki.configureAgentWikiMaintenance'"));
must('maintenance-workspace-setting', entry.includes("config.update('agentWikiMaintenanceEnabled', action.value, vscode.ConfigurationTarget.Workspace)"));
must('maintenance-modal', entry.includes("{ modal: true }"));
must('doctor-zero-model', entry.includes("doctorOutput.appendLine('Model calls: 0')"));
must('doctor-zero-state-change', entry.includes("doctorOutput.appendLine('State changes: 0')"));
mustNot('doctor-does-not-init-command', entry.includes("executeCommand('llmWiki.init')"));
mustNot('doctor-does-not-run-init-core', /async function doctor[\s\S]*?runCoreCommand\(context, folder, \['init'\]\)/.test(entry));
mustNot('entry-never-authorizes-model', entry.includes('--allow-model-call'));

const tools = manifest.contributes.languageModelTools || [];
assert.equal(tools.length, 5, 'STATIC-BOUNDARY tool-count');
const toolNames = new Set(tools.map((row) => row.name));
for (const name of [
  'llmWiki_searchMemory', 'llmWiki_readSource', 'llmWiki_rememberSource',
  'llmWiki_rememberHumanKnowledge', 'llmWiki_resolveLineage',
]) must(`tool:${name}`, toolNames.has(name));
for (const name of toolNames) must(`activation:${name}`, manifest.activationEvents.includes(`onLanguageModelTool:${name}`));
for (const tool of tools) assert.equal(tool.when, 'llmWiki.workspaceEnabled && isWorkspaceTrusted', `STATIC-BOUNDARY tool-when:${tool.name}`);
assert.equal(tools.find((row) => row.name === 'llmWiki_searchMemory').toolReferenceName, 'wikiMemory', 'STATIC-BOUNDARY ref:wikiMemory');
assert.equal(tools.find((row) => row.name === 'llmWiki_readSource').toolReferenceName, 'wikiRead', 'STATIC-BOUNDARY ref:wikiRead');
assert.equal(tools.find((row) => row.name === 'llmWiki_rememberSource').toolReferenceName, 'rememberWikiSource', 'STATIC-BOUNDARY ref:rememberWikiSource');
assert.equal(tools.find((row) => row.name === 'llmWiki_rememberHumanKnowledge').toolReferenceName, 'rememberHumanKnowledge', 'STATIC-BOUNDARY ref:rememberHumanKnowledge');
assert.equal(tools.find((row) => row.name === 'llmWiki_resolveLineage').toolReferenceName, 'resolveWikiLineage', 'STATIC-BOUNDARY ref:resolveWikiLineage');
const hkSchema = tools.find((row) => row.name === 'llmWiki_rememberHumanKnowledge').inputSchema.properties;
assert.equal(hkSchema.statement.maxLength, 1800, 'STATIC-BOUNDARY hk-statement-bound');
assert.equal(hkSchema.reasoning.maxLength, 1600, 'STATIC-BOUNDARY hk-reasoning-bound');
assert.equal(hkSchema.sourceIds.maxItems, 12, 'STATIC-BOUNDARY hk-source-bound');
must('hk-supersedes-schema', Boolean(hkSchema.supersedesKnowledgeId));

assert.equal(manifest.version, '0.1.12', 'STATIC-BOUNDARY version');
assert.equal(manifest.engines.vscode, '^1.95.0', 'STATIC-BOUNDARY vscode-engine');
assert.equal(manifest.main, './entry.js', 'STATIC-BOUNDARY main-entry');
assert.equal(manifest.private, true, 'STATIC-BOUNDARY private-package');
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false, 'STATIC-BOUNDARY untrusted-workspace');
const configProps = manifest.contributes.configuration.properties;
assert.equal(configProps['llmWiki.agentWikiMaintenanceEnabled'].default, false, 'STATIC-BOUNDARY maintenance-default-off');
assert.equal(configProps['llmWiki.agentWikiMaintenanceMaxAiCredits'].minimum, 30, 'STATIC-BOUNDARY maintenance-credit-min');
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].default, 10, 'STATIC-BOUNDARY daily-limit-default');
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].minimum, 0, 'STATIC-BOUNDARY daily-limit-min');
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].maximum, 100, 'STATIC-BOUNDARY daily-limit-max');
must('check-includes-workspace-activation', manifest.scripts.check.includes('workspace-activation.js'));
must('check-runs-workspace-activation-test', manifest.scripts.check.includes('test/workspace-activation.js'));
must('check-includes-human-knowledge', manifest.scripts.check.includes('human-knowledge.js'));
assert.equal(manifest.devDependencies['@vscode/vsce'], '3.9.2', 'STATIC-BOUNDARY vsce-pin');

must('entry-load-agent-tools', entry.includes("require('./agent-tools')"));
must('entry-load-workspace-activation', entry.includes("require('./workspace-activation')"));
must('entry-register-agent-tools', entry.includes('registerAgentTools(context);'));
must('workspace-context-key', entry.includes("const WORKSPACE_ENABLED_CONTEXT = 'llmWiki.workspaceEnabled'"));
must('workspace-context-set', entry.includes("executeCommand('setContext', WORKSPACE_ENABLED_CONTEXT"));
must('explicit-enable-command', entry.includes("registerCommand('llmWiki.enableWorkspace'"));
must('explicit-disable-command', entry.includes("registerCommand('llmWiki.disableWorkspace'"));
must('initialize-git-gate', entry.includes("gitSafety === 'UNPROTECTED'"));
must('initialize-core-explicit-path', entry.includes("runCoreCommand(context, folder, ['init'])"));
must('initialize-integrity-before-opt-in', entry.indexOf("runCoreCommand(context, folder, ['init'])") < entry.indexOf('workspaceActivation.enableWorkspace(root)'));
must('disable-preserves-data-message', entry.includes('Stored Wiki data was preserved.'));
must('doctor-reports-opt-in', entry.includes('Workspace opt-in:'));
must('doctor-reports-tools', entry.includes('Agent tools:'));
must('agent-load-human-knowledge', agentTools.includes("require('./human-knowledge')"));
must('register-search-tool', agentTools.includes('vscode.lm.registerTool(SEARCH_TOOL'));
must('register-read-tool', agentTools.includes('vscode.lm.registerTool(READ_TOOL'));
must('register-remember-tool', agentTools.includes('vscode.lm.registerTool(REMEMBER_TOOL'));
must('register-hk-tool', agentTools.includes('vscode.lm.registerTool(HUMAN_KNOWLEDGE_TOOL'));
must('register-lineage-tool', agentTools.includes('vscode.lm.registerTool(RESOLVE_LINEAGE_TOOL'));

must('workspace-marker-format', workspaceActivation.includes("llm-wiki-workspace-opt-in-v1"));
must('workspace-marker-separate-from-core', workspaceActivation.includes("WORKSPACE_OPT_IN_FILE = 'workspace-opt-in.json'"));
must('workspace-enable-requires-core', workspaceActivation.includes('Cannot enable LLM Wiki Agent integration before the local Wiki store is initialized.'));
must('workspace-enabled-requires-marker-and-core', workspaceActivation.includes('return isCoreInitialized(root) && Boolean(readWorkspaceOptIn(root));'));
must('workspace-disable-only-unlinks-marker', workspaceActivation.includes('fs.unlinkSync(target)'));
mustNot('workspace-disable-does-not-remove-root', workspaceActivation.includes('rmSync(root'));

must('ambient-v4', agentTools.includes('LLM_WIKI_MEMORY_RESULT v4'));
must('ambient-discover-current', agentTools.includes("['discover', query, '--top-k-per-topic', '3', '--json']"));
must('verified-read-v2', agentTools.includes('LLM_WIKI_SOURCE_READ v2'));
must('verified-read-cli', agentTools.includes('runAgentMemoryCli(this.context, folder, args)'));
must('raw-memory-class', agentTools.includes('RAW_MEMORY R'));
must('derived-memory-class', agentTools.includes('DERIVED_MEMORY D'));
must('human-knowledge-class', agentTools.includes('HUMAN_KNOWLEDGE H'));
must('untrusted-raw-framing', agentTools.includes('UNTRUSTED_QUOTED_DATA_NOT_INSTRUCTIONS'));
must('json-data-encoding', agentTools.includes('data_encoding=json_string_fields'));
must('json-data-helper', agentTools.includes('function jsonData(value)'));
must('raw-snippet-json', agentTools.includes('snippet_json='));
must('raw-text-json', agentTools.includes('raw_text_json='));
must('derived-note-json', agentTools.includes('derived_note_markdown_json='));
must('metadata-name-json', agentTools.includes('name_json='));
mustNot('no-raw-begin-end-delimiter', agentTools.includes('BEGIN VERIFIED IMMUTABLE RAW EVIDENCE'));
must('read-pagination-policy', agentTools.includes('If has_more=yes'));
must('derived-follow-to-raw', agentTools.includes('For load-bearing factual claims surfaced by DERIVED_MEMORY, follow source_ids with wikiRead'));

must('product-owned-confirmation', agentTools.includes('explicitHumanConfirm('));
must('confirmation-test-only-bypass', agentTools.includes('context.extensionMode === vscode.ExtensionMode.Test'));
must('any-open-doc-dirty-check', agentTools.includes('dirtyOpenDocumentFor'));
must('dirty-check-text-documents', agentTools.includes('vscode.workspace.textDocuments.find'));
must('dirty-fail-message', agentTools.includes('LLM Wiki will not auto-save a dirty editor'));
mustNot('no-document-save-call', agentTools.includes('document.save()'));
mustNot('no-active-document-save-call', agentTools.includes('active.document.save()'));
must('remember-raw-ingest', agentTools.includes("['ingest', target.filePath, '--topic', topic.id]"));
must('remember-human-confirmed-authority', agentTools.includes('authority=human_confirmed_source_admission'));
must('remember-does-not-persist-hk', agentTools.includes('human_authorship_persisted=no'));

must('durable-agent-state-cli', agentTools.includes("runPythonModule(context, folder, 'dogfood.llm_wiki.agent_state_cli'"));
must('durable-source-locators', agentTools.includes('durableSourceLocators'));
must('legacy-locator-migration', agentTools.includes("'locator-set', row.source_id"));
must('durable-pending-list', agentTools.includes('openPendingLineageRows'));
must('durable-budget-reserve', agentTools.includes('reserveMaintenanceCall'));
must('daily-limit-skip', agentTools.includes('SKIPPED_DAILY_CALL_LIMIT'));
must('pending-lineage-skip', agentTools.includes('SKIPPED_PENDING_LINEAGE_DECISION'));
must('continuation-decision-output', agentTools.includes('continuation_decision_id='));
must('remaining-predecessors-output', agentTools.includes('remaining_predecessor_source_ids='));

must('lineage-enum', agentTools.includes("LINEAGE_RELATIONS = new Set(['correction', 'change', 'dispute', 'supersede', 'independent'])"));
must('lineage-modal', agentTools.includes('Confirm LLM Wiki lineage decision'));
must('lineage-verified-compare', agentTools.includes("'compare', predecessor, pending.successor_source_id"));
must('lineage-old-excerpt', agentTools.includes('comparison.old_excerpt'));
must('lineage-new-excerpt', agentTools.includes('comparison.new_excerpt'));
must('lineage-current-revalidation', agentTools.includes("comparison.older_status !== 'current' || comparison.newer_status !== 'current'"));
must('lineage-locator-sha-binding', agentTools.includes('olderLocator.sha256 !== comparison.older_sha256'));
assert.equal((agentTools.match(/verifiedLineageComparison\(this\.context, folder, pending, predecessor\)/g) || []).length, 2, 'STATIC-BOUNDARY lineage-compare-before-and-after-confirm');
must('lineage-correction', agentTools.includes("['source', 'correct'"));
must('lineage-change', agentTools.includes("['source', 'change'"));
must('lineage-dispute', agentTools.includes("['source', 'dispute'"));
must('lineage-supersede', agentTools.includes("['source', 'supersede'"));
must('change-effective-time-required', agentTools.includes("relation === 'change' && !effectiveAt"));
must('lineage-human-authority', agentTools.includes('authority=human_confirmed_epistemic_relation'));

must('hk-v1-format', humanKnowledge.includes("const FORMAT = 'llm-wiki-human-knowledge-v1'"));
must('hk-integrity-field', humanKnowledge.includes('integritySha256'));
must('hk-integrity-fail-closed', humanKnowledge.includes('Human Knowledge integrity failure'));
must('hk-supersedes', humanKnowledge.includes('supersedesKnowledgeId'));
must('hk-current-filter', humanKnowledge.includes('currentRows'));
must('hk-superseded-filter', humanKnowledge.includes('superseded.has(row.id)'));
must('hk-fork-fail-closed', humanKnowledge.includes('Human Knowledge lineage fork detected'));
must('hk-cycle-fail-closed', humanKnowledge.includes('Human Knowledge lineage cycle detected'));
must('hk-json-parse-fails-closed', humanKnowledge.includes('throw new Error(`Human Knowledge corruption detected (${name}): unreadable JSON.`)'));
mustNot('hk-no-empty-json-catch', humanKnowledge.includes('JSON.parse(fs.readFileSync(filePath, \'utf8\'));\n    } catch (_) {}'));
must('hk-modal', agentTools.includes('Save Human Knowledge?'));
must('hk-full-confirmation-text', agentTools.includes('full text below becomes user-confirmed memory'));
must('hk-supersedes-tool', agentTools.includes('supersedesKnowledgeId'));
must('hk-human-authority', agentTools.includes('authority=explicit_user_confirmation'));
must('hk-integrity-output', agentTools.includes('integrity_sha256='));
must('hk-no-raw-mutation', agentTools.includes('raw_evidence_mutation=none'));
must('hk-no-canonical-temporal-mutation', agentTools.includes('canonical_temporal_mutation=none'));

must('luna-exact-model', agentTools.includes("const AGENT_WIKI_MODEL = 'gpt-5.6-luna'"));
must('maintenance-default-config-read', agentTools.includes("configuration().get('agentWikiMaintenanceEnabled', false) === true"));
must('daily-call-setting', agentTools.includes('agentWikiMaintenanceDailyCallLimit'));
must('model-authorization-only-maintenance', agentTools.includes("'--allow-model-call'"));
const ingestIndex = agentTools.indexOf("['ingest', target.filePath, '--topic', topic.id]");
const maintenanceIndex = agentTools.indexOf('maintainSource(this.context, folder, receipt.sourceId');
must('raw-first-ordering-markers-exist', ingestIndex >= 0 && maintenanceIndex >= 0);
must('raw-first-ordering', ingestIndex < maintenanceIndex);
must('maintenance-failure-preserves-raw', agentTools.includes('FAILED_AFTER_RAW_ADMISSION'));

must('legacy-extension-luna-model', extension.includes("'gpt-5.6-luna'"));
must('legacy-extension-explicit-model-auth', extension.includes("'--allow-model-call'"));
must('legacy-extension-readonly-ask', extension.includes('Canonical mutation: none'));
must('source-navigation-scheme', extension.includes("const SOURCE_SCHEME = 'llm-wiki-source'"));
mustNot('no-shell-true', extension.includes('shell: true'));
mustNot('no-compiled-provider-mutation', extension.includes('compiled_provider ='));
must('workspace-relative-helper', productHelpers.includes('workspaceRelativePath'));
mustNot('helpers-dont-touch-manifest', productHelpers.includes('manifest.jsonl'));
must('experimental-exact-luna-discovery', lmDiscovery.includes("const REQUIRED_LUNA_ID = 'gpt-5.6-luna'"));
must('experimental-discovery-zero-generation', lmDiscovery.includes('generationCalls: 0'));
mustNot('experimental-discovery-no-generation', lmDiscovery.includes('sendRequest'));
must('git-safety-ignore-check', gitSafety.includes("['check-ignore', '-q', '--'"));
mustNot('git-safety-no-write', gitSafety.includes('writeFile'));
must('bundle-core-source', bundler.includes("path.join(dogfoodRoot, 'llm_wiki')"));
must('bundle-core-destination', bundler.includes("path.join(bundleRoot, 'dogfood')"));

console.log('VS-CODE-DOGFOOD-STATIC PASS version=0.1.12 agentTools=5 explicitWorkspaceOptIn=yes doctorPureDiagnostic=yes toolWhenGated=yes memoryV4=json-data verifiedReadV2=yes verifiedLineageDiff=yes durableAuthorityState=yes dirtyAnyOpenDocBlocked=yes humanKnowledgeV1=integrity+supersede+fork-cycle-failclosed dailyMaintenanceCap=yes python39Compat=required');
