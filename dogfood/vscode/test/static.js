'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
const entry = fs.readFileSync(path.join(ROOT, 'entry.js'), 'utf8');
const extension = fs.readFileSync(path.join(ROOT, 'extension.js'), 'utf8');
const agent = fs.readFileSync(path.join(ROOT, 'agent-tools.js'), 'utf8');
const human = fs.readFileSync(path.join(ROOT, 'human-knowledge.js'), 'utf8');
const query = fs.readFileSync(path.join(ROOT, 'query-plane.js'), 'utf8');
const usageLedger = fs.readFileSync(path.join(ROOT, 'query-usage-ledger.js'), 'utf8');
const memoryRead = fs.readFileSync(path.join(ROOT, 'memory-read-service.js'), 'utf8');
const library = fs.readFileSync(path.join(ROOT, 'personal-wiki-library.js'), 'utf8');
const libraryUi = fs.readFileSync(path.join(ROOT, 'personal-wiki-library-ui.js'), 'utf8');
const scopedRead = fs.readFileSync(path.join(ROOT, 'scoped-read-tool.js'), 'utf8');
const runtime = fs.readFileSync(path.join(ROOT, 'python-runtime.js'), 'utf8');
const runtimePolicy = fs.readFileSync(path.join(ROOT, 'python-runtime-policy.js'), 'utf8');

function must(name, condition) {
  assert.ok(condition, `STATIC-BOUNDARY ${name}`);
}

function mustNot(name, condition) {
  assert.ok(!condition, `STATIC-BOUNDARY ${name}`);
}

// Installation / trust / lifecycle boundaries.
must('activation-startup', manifest.activationEvents.includes('onStartupFinished'));
must('activation-workspace-enable', manifest.activationEvents.includes('onCommand:llmWiki.enableWorkspace'));
must('activation-workspace-disable', manifest.activationEvents.includes('onCommand:llmWiki.disableWorkspace'));
must('activation-query-config', manifest.activationEvents.includes('onCommand:llmWiki.configureQueryPlane'));
must('activation-library-config', manifest.activationEvents.includes('onCommand:llmWiki.configurePersonalWikiLibrary'));
must('activation-scoped-read', manifest.activationEvents.includes('onLanguageModelTool:llmWiki_readScopedSource'));
must('trusted-workspace-required', manifest.capabilities.untrustedWorkspaces.supported === false);
must('entry-checks-workspace-opt-in', entry.includes('workspaceActivation.isWorkspaceEnabled'));
must('disable-tears-down-tools', entry.includes('unregisterAgentTools'));
must('single-folder-boundary', entry.includes('one workspace folder at a time'));

// Command palette remains intentionally bounded.
const palette = manifest.contributes.menus.commandPalette || [];
const visibleNormal = palette.filter((row) => row.when !== 'false').map((row) => row.command).sort();
assert.deepEqual(visibleNormal, [
  'llmWiki.configureAgentWikiMaintenance',
  'llmWiki.configurePersonalWikiLibrary',
  'llmWiki.configureQueryPlane',
  'llmWiki.disableWorkspace',
  'llmWiki.doctor',
  'llmWiki.enableWorkspace',
].sort(), 'STATIC-BOUNDARY normal-command-palette');

// Explicit human-owned authority transitions must remain product-owned.
must('remember-source-human-confirm', agent.includes('explicitHumanConfirm('));
must('remember-source-raw-first', agent.includes("['ingest', target.filePath, '--topic', topic.id]"));
must('dirty-editor-fail-closed', agent.includes('will not auto-save a dirty editor'));
must('pending-lineage', agent.includes('SKIPPED_PENDING_LINEAGE_DECISION'));
must('human-knowledge-confirm', agent.includes('Save this as your confirmed project knowledge?'));
must('human-knowledge-format', human.includes('llm-wiki-human-knowledge-v1'));
must('verified-lineage-comparison', agent.includes('verifiedLineageComparison'));
must('lineage-revalidation-count', agent.match(/verifiedLineageComparison\(this\.context, folder, pending, predecessor\)/g)?.length === 2);

// Query Plane stays separate, bounded, read-only, and opt-in.
must('query-exact-luna', query.includes("const QUERY_MODEL = 'gpt-5.6-luna'"));
must('query-current-store-grant', query.includes("scope: 'current_store'"));
must('query-local-grant-key', query.includes('llmWiki.queryPlaneGrant.v1'));
must('query-usage-ledger', query.includes('usageLedger.reserveUsage'));
must('query-pre-model-authorization', query.includes('preModelAuthorization'));
must('query-final-model-authorization', query.includes('finalModelAuthorization'));
must('query-before-spawn', query.includes('beforeSpawn'));
must('usage-ledger-exclusive-slot', usageLedger.includes("fs.openSync(target, 'wx', 0o600)"));
must('usage-ledger-global-storage', usageLedger.includes('globalStorageUri'));
mustNot('query-write-admission', query.includes('rememberSource'));
mustNot('query-write-human', query.includes('rememberHumanKnowledge'));

// Named-store federation remains exact, local-catalog scoped, and read-only.
must('library-store-prefix', library.includes("const STORE_ID_PREFIX = 'libstore-'"));
must('library-authority-anchor', library.includes('authorityAnchor'));
must('library-workspace-epoch', library.includes('workspaceEpoch'));
must('library-read-only-disclosure', libraryUi.includes('read-only'));
must('external-read-service', memoryRead.includes('runFederationRead'));
must('external-bridge-isolated', memoryRead.includes('federation_read_cli'));
must('scoped-read-no-fallback', scopedRead.includes('scopeRef'));
mustNot('library-write-route', library.includes('rememberSource'));
mustNot('library-human-write-route', library.includes('rememberHumanKnowledge'));

// Python runtime separation for external read path remains visible.
must('auto-runtime-export', runtime.includes('resolveAutoPythonRuntime'));
must('runtime-policy-isolated', runtimePolicy.includes('isolatedPythonEnv'));

// Tool manifest boundaries.
const tools = manifest.contributes.languageModelTools;
for (const tool of tools) {
  must(`user-description:${tool.name}`, typeof tool.userDescription === 'string' && tool.userDescription.trim().length > 0);
}
assert.equal(tools.find((row) => row.name === 'llmWiki_searchMemory').toolReferenceName, 'wikiMemory', 'STATIC-BOUNDARY ref:wikiMemory');
assert.equal(tools.find((row) => row.name === 'llmWiki_consultMemory').toolReferenceName, 'wikiConsult', 'STATIC-BOUNDARY ref:wikiConsult');
assert.equal(tools.find((row) => row.name === 'llmWiki_readScopedSource').toolReferenceName, 'wikiRead', 'STATIC-BOUNDARY ref:wikiRead');
assert.equal(tools.find((row) => row.name === 'llmWiki_readSource').canBeReferencedInPrompt, false, 'STATIC-BOUNDARY legacy-read-hidden');
mustNot('legacy-read-no-public-ref', Object.prototype.hasOwnProperty.call(tools.find((row) => row.name === 'llmWiki_readSource'), 'toolReferenceName'));
assert.equal(tools.find((row) => row.name === 'llmWiki_rememberSource').toolReferenceName, 'rememberWikiSource', 'STATIC-BOUNDARY ref:rememberWikiSource');
assert.equal(tools.find((row) => row.name === 'llmWiki_rememberHumanKnowledge').toolReferenceName, 'rememberHumanKnowledge', 'STATIC-BOUNDARY ref:rememberHumanKnowledge');
assert.equal(tools.find((row) => row.name === 'llmWiki_resolveLineage').toolReferenceName, 'resolveWikiLineage', 'STATIC-BOUNDARY ref:resolveWikiLineage');
const hkSchema = tools.find((row) => row.name === 'llmWiki_rememberHumanKnowledge').inputSchema.properties;
assert.equal(hkSchema.statement.maxLength, 1800, 'STATIC-BOUNDARY hk-statement-bound');
assert.equal(hkSchema.reasoning.maxLength, 1600, 'STATIC-BOUNDARY hk-reasoning-bound');
assert.equal(hkSchema.sourceIds.maxItems, 12, 'STATIC-BOUNDARY hk-source-bound');
must('hk-supersedes-schema', Boolean(hkSchema.supersedesKnowledgeId));
const consultSchema = tools.find((row) => row.name === 'llmWiki_consultMemory').inputSchema.properties;
assert.equal(consultSchema.query.maxLength, 2000, 'STATIC-BOUNDARY query-question-bound');
assert.equal(consultSchema.store.maxLength, 120, 'STATIC-BOUNDARY query-named-store-bound');
const scopedReadSchema = tools.find((row) => row.name === 'llmWiki_readScopedSource').inputSchema.properties;
must('scoped-read-scope-ref', Boolean(scopedReadSchema.scopeRef));
assert.deepEqual(scopedReadSchema.scopeRef.properties.kind.enum, ['current_store', 'library_store'], 'STATIC-BOUNDARY scoped-read-scope-kinds');

assert.equal(manifest.version, '0.1.19', 'STATIC-BOUNDARY version');
assert.equal(manifest.engines.vscode, '^1.95.0', 'STATIC-BOUNDARY vscode-engine');
assert.equal(manifest.main, './entry.js', 'STATIC-BOUNDARY main-entry');
assert.equal(manifest.private, true, 'STATIC-BOUNDARY private-package');
assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false, 'STATIC-BOUNDARY untrusted-workspace');
const configProps = manifest.contributes.configuration.properties;
assert.equal(configProps['llmWiki.pythonExecutable'].default, '', 'STATIC-BOUNDARY python-auto-default');
must('python-auto-setting-description', configProps['llmWiki.pythonExecutable'].description.includes('auto-detect'));
assert.equal(configProps['llmWiki.agentWikiMaintenanceEnabled'].default, false, 'STATIC-BOUNDARY maintenance-default-off');
assert.equal(configProps['llmWiki.agentWikiMaintenanceMaxAiCredits'].minimum, 30, 'STATIC-BOUNDARY maintenance-credit-min');
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].default, 10, 'STATIC-BOUNDARY daily-soft-guard-default');
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].minimum, 0, 'STATIC-BOUNDARY daily-soft-guard-min');
assert.equal(configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].maximum, 100, 'STATIC-BOUNDARY daily-soft-guard-max');
must('daily-soft-guard-description', configProps['llmWiki.agentWikiMaintenanceDailyCallLimit'].description.includes('soft-guard threshold'));
mustNot('query-grant-not-workspace-setting', Object.prototype.hasOwnProperty.call(configProps, 'llmWiki.queryPlaneEnabled'));
mustNot('library-grant-not-workspace-setting', Object.prototype.hasOwnProperty.call(configProps, 'llmWiki.personalWikiLibraryAccess'));
must('check-includes-workspace-activation', manifest.scripts.check.includes('workspace-activation.js'));
must('check-runs-workspace-activation-test', manifest.scripts.check.includes('test/workspace-activation.js'));
must('check-includes-human-knowledge', manifest.scripts.check.includes('human-knowledge.js'));

console.log('STATIC-BOUNDARY PASS');
