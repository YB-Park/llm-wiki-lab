'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const entry = fs.readFileSync(path.join(root, 'entry.js'), 'utf8');
const extension = fs.readFileSync(path.join(root, 'extension.js'), 'utf8');
const productView = fs.readFileSync(path.join(root, 'product-view.js'), 'utf8');
const agentTools = fs.readFileSync(path.join(root, 'agent-tools.js'), 'utf8');
const queryPlane = fs.readFileSync(path.join(root, 'query-plane.js'), 'utf8');
const memoryRead = fs.readFileSync(path.join(root, 'memory-read-service.js'), 'utf8');
const personalLibrary = fs.readFileSync(path.join(root, 'personal-wiki-library.js'), 'utf8');
const personalLibraryUi = fs.readFileSync(path.join(root, 'personal-wiki-library-ui.js'), 'utf8');
const scopedRead = fs.readFileSync(path.join(root, 'scoped-read-tool.js'), 'utf8');
const workspaceActivation = fs.readFileSync(path.join(root, 'workspace-activation.js'), 'utf8');
const humanKnowledge = fs.readFileSync(path.join(root, 'human-knowledge.js'), 'utf8');
const productHelpers = fs.readFileSync(path.join(root, 'product-helpers.js'), 'utf8');
const processErrors = fs.readFileSync(path.join(root, 'process-errors.js'), 'utf8');
const pythonRuntime = fs.readFileSync(path.join(root, 'python-runtime.js'), 'utf8');
const pythonRuntimePolicy = fs.readFileSync(path.join(root, 'python-runtime-policy.js'), 'utf8');
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
  'llmWiki.enableWorkspace', 'llmWiki.disableWorkspace', 'llmWiki.openAgentChat', 'llmWiki.refreshOverview',
  'llmWiki.createTopic', 'llmWiki.selectTopic', 'llmWiki.newKnowledgeNote',
  'llmWiki.configureAgentWikiMaintenance', 'llmWiki.configureQueryPlane', 'llmWiki.configurePersonalWikiLibrary',
  'llmWiki.ingestActiveFile', 'llmWiki.ingestAuthoritativeUpdate', 'llmWiki.search', 'llmWiki.discoverAcrossTopics',
  'llmWiki.markCorrection', 'llmWiki.markChange', 'llmWiki.markDispute', 'llmWiki.feedback', 'llmWiki.ask',
  'llmWiki.calibration', 'llmWiki.doctor', 'llmWiki.reportIssue', 'llmWiki.experimentalDiscoverCopilotModels',
]) must(`command:${command}`, commands.has(command));
assert.equal(commands.size, 23, 'STATIC-BOUNDARY command-count');
mustNot('internal-core-init-not-user-contributed', commands.has('llmWiki.init'));
must('startup-activation', manifest.activationEvents.includes('onStartupFinished'));
must('overview-view-activation', manifest.activationEvents.includes('onView:llmWiki.overview'));
must('enable-activation', manifest.activationEvents.includes('onCommand:llmWiki.enableWorkspace'));
must('disable-activation', manifest.activationEvents.includes('onCommand:llmWiki.disableWorkspace'));
must('query-config-activation', manifest.activationEvents.includes('onCommand:llmWiki.configureQueryPlane'));
must('library-config-activation', manifest.activationEvents.includes('onCommand:llmWiki.configurePersonalWikiLibrary'));

assert.equal(manifest.displayName, 'LLM Wiki', 'STATIC-BOUNDARY release-display-name');
const paletteRows = manifest.contributes.menus.commandPalette || [];
const visiblePalette = new Set(paletteRows.filter((row) => row.when !== 'false').map((row) => row.command));
assert.deepEqual(visiblePalette, new Set([
  'llmWiki.enableWorkspace', 'llmWiki.disableWorkspace', 'llmWiki.configureAgentWikiMaintenance',
  'llmWiki.configureQueryPlane', 'llmWiki.configurePersonalWikiLibrary', 'llmWiki.doctor',
]), 'STATIC-BOUNDARY release-command-palette');

const viewContainers = manifest.contributes.viewsContainers && manifest.contributes.viewsContainers.activitybar || [];
assert.equal(viewContainers.length, 1, 'STATIC-BOUNDARY ux-single-view-container');
assert.equal(viewContainers[0].id, 'llmWiki', 'STATIC-BOUNDARY ux-view-container-id');
const wikiViews = manifest.contributes.views && manifest.contributes.views.llmWiki || [];
assert.equal(wikiViews.length, 1, 'STATIC-BOUNDARY ux-single-view');
assert.equal(wikiViews[0].id, 'llmWiki.overview', 'STATIC-BOUNDARY ux-overview-view-id');
must('ux-native-tree-view-no-webview', !manifest.contributes.webviews && !manifest.contributes.webviewViews);
const welcomeRows = manifest.contributes.viewsWelcome || [];
must('ux-setup-welcome-primary-action', welcomeRows.some((row) => row.view === 'llmWiki.overview' && row.contents.includes('[Set Up Project Memory](command:llmWiki.enableWorkspace)')));
must('ux-welcome-ai-optional', welcomeRows.some((row) => row.contents.includes('AI features stay optional')));
const titleActions = manifest.contributes.menus['view/title'] || [];
assert.deepEqual(new Set(titleActions.map((row) => row.command)), new Set(['llmWiki.openAgentChat', 'llmWiki.doctor', 'llmWiki.refreshOverview']), 'STATIC-BOUNDARY ux-sparse-title-actions');

const walkthroughs = manifest.contributes.walkthroughs || [];
assert.equal(walkthroughs.length, 1, 'STATIC-BOUNDARY walkthrough-count');
assert.equal(walkthroughs[0].steps.length, 3, 'STATIC-BOUNDARY walkthrough-step-count');
must('walkthrough-setup-command', walkthroughs[0].steps.some((row) => (row.completionEvents || []).includes('onCommand:llmWiki.enableWorkspace')));
must('walkthrough-host-surface-disclosure', walkthroughs[0].description.includes("VS Code's Getting Started page"));
must('walkthrough-sidebar-orientation', walkthroughs[0].description.includes('sidebar overview'));
const walkthroughFirst = walkthroughs[0].steps.find((row) => row.id === 'llmWiki.gettingStarted.localFirst');
const walkthroughAi = walkthroughs[0].steps.find((row) => row.id === 'llmWiki.gettingStarted.aiSummaries');
const walkthroughChat = walkthroughs[0].steps.find((row) => row.id === 'llmWiki.gettingStarted.chat');
must('walkthrough-installed-disclosure', walkthroughFirst && walkthroughFirst.title === 'LLM Wiki is installed' && walkthroughFirst.description.includes('Installing the extension is complete'));
must('walkthrough-ai-summary-removed-from-setup', !walkthroughAi);
must('walkthrough-chat-primary-cta', walkthroughChat && walkthroughChat.description.includes('(command:workbench.action.chat.open)'));
must('walkthrough-chat-completion', walkthroughChat && (walkthroughChat.completionEvents || []).includes('onCommand:workbench.action.chat.open'));
must('walkthrough-no-separate-app', walkthroughChat && walkthroughChat.description.includes('do not need to operate a separate Wiki app'));

must('human-note-command', entry.includes("registerCommand('llmWiki.newKnowledgeNote'"));
must('human-note-boundary-text', entry.includes('Human-owned draft. Saving this file does not ingest, promote, or mutate LLM Wiki state.'));
mustNot('human-note-no-auto-ingest', entry.includes("executeCommand('llmWiki.ingestActiveFile')"));
mustNot('human-note-no-auto-model', entry.includes("executeCommand('llmWiki.ask')"));
must('maintenance-config-command', entry.includes("registerCommand('llmWiki.configureAgentWikiMaintenance'"));
must('maintenance-workspace-setting', entry.includes("config.update('agentWikiMaintenanceEnabled', true, vscode.ConfigurationTarget.Workspace)") && entry.includes("config.update('agentWikiMaintenanceEnabled', false, vscode.ConfigurationTarget.Workspace)"));
must('maintenance-modal', entry.includes('modal: true'));
must('query-config-command', entry.includes('registerQueryPlaneCommand(context);'));
must('doctor-zero-model', entry.includes("doctorOutput.appendLine('Model calls: 0')"));
must('doctor-zero-state-change', entry.includes("doctorOutput.appendLine('State changes: 0')"));
must('doctor-user-setup-heading', entry.includes('LLM Wiki — Setup & Health'));
must('doctor-copilot-executable-only', entry.includes('Copilot CLI executable:'));
must('doctor-model-readiness-unverified', entry.includes('AI-summary/query model-call readiness: NOT VERIFIED'));
must('doctor-query-grant-visible', entry.includes('Wiki query reasoning:'));
must('doctor-query-cap-visible', entry.includes('Wiki query daily call cap:'));
must('issue-reporter-command', entry.includes("registerCommand('llmWiki.reportIssue'"));
must('issue-reporter-native', entry.includes("executeCommand('vscode.openIssueReporter'"));
must('issue-reporter-bounded', entry.includes('No project evidence, prompts, source text, local paths, usernames, hostnames, or environment variables are included.'));
const issueReporterRows = manifest.contributes.menus['issue/reporter'] || [];
assert.deepEqual(issueReporterRows.map((row) => row.command), ['llmWiki.reportIssue'], 'STATIC-BOUNDARY native-issue-reporter');
must('doctor-compiled-provider-explained', entry.includes('disabled (expected; not used by AI summaries)'));
must('doctor-python-selected-runtime', entry.includes('Python runtime: ${pythonReady ? `FOUND (${runtime.executable}, ${runtime.source})`'));
mustNot('doctor-does-not-init-command', entry.includes("executeCommand('llmWiki.init')"));
mustNot('doctor-does-not-run-init-core', /async function doctor[\s\S]*?runCoreCommand\(context, folder, \['init'\]\)/.test(entry));
mustNot('entry-never-authorizes-model', entry.includes('--allow-model-call'));

const tools = manifest.contributes.languageModelTools || [];
assert.equal(tools.length, 7, 'STATIC-BOUNDARY tool-count');
const toolNames = new Set(tools.map((row) => row.name));
for (const name of [
  'llmWiki_searchMemory', 'llmWiki_consultMemory', 'llmWiki_readSource', 'llmWiki_readScopedSource',
  'llmWiki_rememberSource', 'llmWiki_rememberHumanKnowledge', 'llmWiki_resolveLineage',
]) must(`tool:${name}`, toolNames.has(name));
for (const name of toolNames) must(`activation:${name}`, manifest.activationEvents.includes(`onLanguageModelTool:${name}`));
for (const tool of tools) {
  const expectedWhen = tool.name === 'llmWiki_readSource' ? 'false' : 'llmWiki.workspaceEnabled && isWorkspaceTrusted';
  assert.equal(tool.when, expectedWhen, `STATIC-BOUNDARY tool-when:${tool.name}`);
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

assert.equal(manifest.version, '0.1.21', 'STATIC-BOUNDARY version');
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
must('check-includes-product-view', manifest.scripts.check.includes('product-view.js'));
must('check-includes-workspace-activation', manifest.scripts.check.includes('workspace-activation.js'));
must('check-runs-workspace-activation-test', manifest.scripts.check.includes('test/workspace-activation.js'));
must('check-includes-human-knowledge', manifest.scripts.check.includes('human-knowledge.js'));
must('check-includes-query-plane', manifest.scripts.check.includes('query-plane.js'));
must('check-includes-memory-read-service', manifest.scripts.check.includes('memory-read-service.js'));
must('check-includes-personal-library', manifest.scripts.check.includes('personal-wiki-library.js'));
must('check-includes-personal-library-ui', manifest.scripts.check.includes('personal-wiki-library-ui.js'));
must('check-includes-scoped-read', manifest.scripts.check.includes('scoped-read-tool.js'));
must('check-runs-personal-library-test', manifest.scripts.check.includes('test/personal-wiki-library.js'));
must('check-runs-process-errors-test', manifest.scripts.check.includes('test/process-errors.js'));
must('check-runs-python-policy-test', manifest.scripts.check.includes('test/python-runtime-policy.js'));
assert.equal(manifest.devDependencies['@vscode/vsce'], '3.9.2', 'STATIC-BOUNDARY vsce-pin');

must('entry-load-agent-tools', entry.includes("require('./agent-tools')"));
must('entry-load-query-plane', entry.includes("require('./query-plane')"));
must('entry-load-product-view', entry.includes("require('./product-view')"));
must('entry-load-workspace-activation', entry.includes("require('./workspace-activation')"));
must('entry-load-python-runtime', entry.includes("require('./python-runtime')"));
must('entry-register-product-view-before-runtime', entry.indexOf('registerProductView(context);') < entry.indexOf('await refreshWorkspaceRuntimeAvailability(context);'));
must('entry-register-agent-tools', entry.includes('registerAgentTools(context);'));
must('entry-register-query-tool-same-lifecycle', entry.includes('registerQueryPlaneTool(context);'));
must('entry-agent-tool-count-six-disposables', entry.includes('const AGENT_TOOL_COUNT = 6'));
must('workspace-context-key', entry.includes("const WORKSPACE_ENABLED_CONTEXT = 'llmWiki.workspaceEnabled'"));
must('workspace-context-set', entry.includes("executeCommand('setContext', WORKSPACE_ENABLED_CONTEXT"));
must('overview-refresh-follows-workspace-context', entry.includes("executeCommand('llmWiki.refreshOverview')"));
must('explicit-enable-command', entry.includes("registerCommand('llmWiki.enableWorkspace'"));
must('explicit-disable-command', entry.includes("registerCommand('llmWiki.disableWorkspace'"));
must('initialize-git-gate', entry.includes("gitSafety === 'UNPROTECTED'"));
must('initialize-core-explicit-path', entry.includes("runCoreCommand(context, folder, ['init'])"));
must('initialize-integrity-before-opt-in', entry.indexOf("runCoreCommand(context, folder, ['init'])") < entry.indexOf('workspaceActivation.enableWorkspace(root)'));
must('disable-preserves-data-message', entry.includes('Stored Wiki data was preserved.'));
must('doctor-reports-opt-in', entry.includes('Workspace opt-in:'));
must('doctor-reports-tools', entry.includes('Agent tools:'));
must('single-folder-runtime-gate', entry.includes('folders.length === 1 && workspaceActivation.isWorkspaceEnabled'));
must('status-lifecycle-sync', entry.includes('base.setStatusVisible(enabled)'));

must('product-view-native-tree', productView.includes('vscode.window.createTreeView(VIEW_ID'));
must('product-view-no-webview', !productView.includes('createWebview') && !productView.includes('Webview'));
must('product-view-user-vocabulary', productView.includes("node('Project memory'") && productView.includes("node('AI-assisted memory answers'") && productView.includes("node('Other project memories'"));
must('product-view-other-project-names', productView.includes('store.displayName'));
mustNot('product-view-no-store-id-display', productView.includes('store.storeId'));
mustNot('product-view-no-root-display', productView.includes('store.root'));
mustNot('product-view-no-authority-epoch', productView.includes('authority epoch'));
must('product-view-refresh-on-visible', productView.includes('tree.onDidChangeVisibility'));
must('product-view-workspace-eligible-context', productView.includes("const WORKSPACE_ELIGIBLE_CONTEXT = 'llmWiki.workspaceEligible'"));

must('query-local-grant-workspace-state', queryPlane.includes('context.workspaceState.get(grantKey(folder))') && queryPlane.includes('context.workspaceState.update(grantKey(folder), grant)'));
mustNot('query-grant-no-configuration-update', queryPlane.includes("config.update('queryPlaneEnabled'"));
must('query-grant-versioned', queryPlane.includes('const GRANT_VERSION = 1'));
must('query-current-store-grant-remains-narrow', queryPlane.includes("row.scope !== 'current_store'"));
must('query-exposure-explicit', queryPlane.includes("evidenceExposure: 'retrieved_admitted_memory_only'"));
must('query-user-chosen-cap', queryPlane.includes('Query reasoning daily call cap') && queryPlane.includes('dailyCallLimit'));
must('query-library-resolve-before-reserve', queryPlane.indexOf('library.resolveNamedStore(this.context, folder') < queryPlane.indexOf('reserveQueryCall(this.context, folder, grant)'));
must('query-reserve-before-composer', queryPlane.indexOf('reserveQueryCall(this.context, folder, grant)') < queryPlane.indexOf('runComposerStdin('));
must('query-no-raw-fallback', queryPlane.includes('Do not automatically fall back'));
must('query-scope-blocked-no-model', queryPlane.includes('state=library_scope_blocked') && queryPlane.includes('model_calls=0') && queryPlane.includes('fallback=none'));
must('query-result-scope-validation', queryPlane.includes('query_plane_result_scope_mismatch'));
must('query-exact-luna', queryPlane.includes("const MODEL = 'gpt-5.6-luna'"));
must('query-uses-memory-read-service', queryPlane.includes("require('./memory-read-service')") && queryPlane.includes('memoryRead.collectQueryEvidence'));
must('query-composer-no-root-arg', queryPlane.includes("['-m', 'dogfood.llm_wiki.query_plane_cli', ...args]"));
must('query-scope-qualified-brief', queryPlane.includes('scope-qualified refs'));
must('query-register-library-command', queryPlane.includes('libraryUi.registerPersonalWikiLibraryCommand(context)'));
must('query-composite-lifecycle', queryPlane.includes('queryDisposable.dispose()') && queryPlane.includes('readDisposable.dispose()'));

must('memory-profile-versioned', memoryRead.includes("id: 'current-store-l0-v1'"));
must('memory-named-profile-versioned', memoryRead.includes("id: 'named-store-l0-v1'"));
must('memory-current-discovery', memoryRead.includes("['discover', query, '--top-k-per-topic', '3', '--json']"));
must('memory-derived-navigation', memoryRead.includes("'dogfood.llm_wiki.agent_wiki_cli'"));
must('memory-human-knowledge', memoryRead.includes('humanKnowledge.search'));
must('memory-pending-lineage', memoryRead.includes("['pending-list']"));
must('memory-relevant-region-read', memoryRead.includes("'relevant', target.sourceId"));
must('memory-verification-failclosed', memoryRead.includes('query_plane_candidate_verification_failed'));
mustNot('memory-no-silent-candidate-omit', memoryRead.includes('Omit it;'));
must('memory-current-store-handle', memoryRead.includes("scopeRef: { kind: 'current_store' }"));
must('memory-library-store-handle', memoryRead.includes("scopeRef: { kind: 'library_store', store_id: scopeRef.store_id }"));
must('memory-root-only-from-store-handle', memoryRead.includes("const store = normalizeStoreHandle(folder, options.storeHandle)"));
must('memory-preserves-hk-support', memoryRead.includes('supporting_source_ids'));

must('library-global-catalog-state', personalLibrary.includes('context.globalState.get(CATALOG_KEY)') && personalLibrary.includes('context.globalState.update(CATALOG_KEY'));
must('library-workspace-grant-state', personalLibrary.includes('context.workspaceState.get(grantKey(folder))') && personalLibrary.includes('context.workspaceState.update(grantKey(folder)'));
must('library-grant-epoch-bound', personalLibrary.includes("const storedEpoch = String(row.workspaceEpoch || '')") && personalLibrary.includes('storedEpoch !== workspaceActivation.workspaceEpoch(optIn)'));
mustNot('library-grant-no-timestamp-auth-fallback', personalLibrary.includes('row.workspaceEnabledAt !== optIn.enabled_at'));
must('library-random-opaque-id', personalLibrary.includes('crypto.randomUUID()'));
must('library-current-store-rejected', personalLibrary.includes('library_store_is_current_store'));
must('library-ambiguity-failclosed', personalLibrary.includes('library_store_ambiguous'));
must('library-no-union-search-api', !personalLibrary.includes('searchAll') && !personalLibrary.includes('unionSearch'));
must('library-ui-explicit-readonly-disclosure', personalLibraryUi.includes('Register Read-only Store') && personalLibraryUi.includes('does not authorize writes, sync, ambient library search'));
must('library-ui-named-only-disclosure', personalLibraryUi.includes('no ambient library search'));

must('scoped-read-resolve-by-opaque-id', scopedRead.includes('library.resolveStoreId(context, folder'));
must('scoped-read-v3', scopedRead.includes('LLM_WIKI_SOURCE_READ v3'));
must('scoped-read-no-fallback', scopedRead.includes('library_store_source_not_found') && scopedRead.includes('Never retry a missing external source ID against the current store or another store'));
must('scoped-read-no-write-authority', scopedRead.includes('never authorizes source admission, Human Knowledge, lineage, maintenance, or configuration writes'));
mustNot('scoped-read-no-user-root-input', scopedRead.includes('input.root'));

must('agent-load-human-knowledge', agentTools.includes("require('./human-knowledge')"));
must('agent-load-process-errors', agentTools.includes("require('./process-errors')"));
must('agent-load-python-runtime', agentTools.includes("require('./python-runtime')"));
must('agent-load-memory-read-service', agentTools.includes("require('./memory-read-service')"));
must('agent-shared-memory-service', agentTools.includes('memoryRead.collectMemoryRows'));
must('agent-single-folder-failclosed', agentTools.includes('currently supports one workspace folder at a time'));
must('register-search-tool', agentTools.includes('vscode.lm.registerTool(SEARCH_TOOL'));
must('register-read-tool', agentTools.includes('vscode.lm.registerTool(READ_TOOL'));
must('register-remember-tool', agentTools.includes('vscode.lm.registerTool(REMEMBER_TOOL'));
must('register-hk-tool', agentTools.includes('vscode.lm.registerTool(HUMAN_KNOWLEDGE_TOOL'));
must('register-lineage-tool', agentTools.includes('vscode.lm.registerTool(RESOLVE_LINEAGE_TOOL'));
must('same-bytes-reuse-before-confirm', agentTools.indexOf('findExactCurrentRememberedSource') < agentTools.indexOf("'Save this file to project memory?'"));
must('same-bytes-reuse-result', agentTools.includes('raw_admission=reused_existing') && agentTools.includes('authority=existing_source_reuse'));
must('soft-guard-pause-today', agentTools.includes('Pause AI Summaries Today') && agentTools.includes('SKIPPED_SOFT_GUARD_PAUSED'));

must('workspace-marker-format', workspaceActivation.includes("llm-wiki-workspace-opt-in-v1"));
must('workspace-marker-separate-from-core', workspaceActivation.includes("WORKSPACE_OPT_IN_FILE = 'workspace-opt-in.json'"));
must('workspace-enable-requires-core', workspaceActivation.includes('Cannot enable LLM Wiki Agent integration before the local Wiki store is initialized.'));
must('workspace-enabled-requires-marker-and-core', workspaceActivation.includes('return isCoreInitialized(root) && Boolean(readWorkspaceOptIn(root));'));
must('workspace-disable-only-unlinks-marker', workspaceActivation.includes('fs.unlinkSync(target)'));
mustNot('workspace-disable-does-not-remove-root', workspaceActivation.includes('rmSync(root'));

must('ambient-v4', agentTools.includes('LLM_WIKI_MEMORY_RESULT v4'));
must('ambient-discover-current', memoryRead.includes("['discover', query, '--top-k-per-topic', '3', '--json']"));
must('verified-read-v2-compat', agentTools.includes('LLM_WIKI_SOURCE_READ v2'));
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
must('confirmation-uses-detail', agentTools.includes('showWarningMessage(title, { modal: true, detail }, button)'));
must('strict-bounded-process-failure', processErrors.includes('function boundedProcessFailure(detail)'));
must('strict-process-last-line-walk', processErrors.includes('for (let index = lines.length - 1; index >= 0; index -= 1)'));
must('strict-process-anchored-pattern', processErrors.includes('/^copilot_call_failed:\\d+$/'));
must('bounded-process-unknown', processErrors.includes("return 'llm_wiki_process_failed'"));
must('library-bounded-failure-codes', processErrors.includes("'library_store_ambiguous'") && processErrors.includes("'library_store_source_not_found'"));
must('maintenance-causal-failure-code', agentTools.includes('maintenance_failure_code='));
must('maintenance-causal-stage', agentTools.includes('maintenance_stage='));
must('maintenance-causal-model-attempt', agentTools.includes('maintenance_model_call_attempted='));
must('any-open-doc-dirty-check', agentTools.includes('dirtyOpenDocumentFor'));
must('dirty-check-text-documents', agentTools.includes('vscode.workspace.textDocuments.find'));
must('dirty-fail-message', agentTools.includes('LLM Wiki will not auto-save a dirty editor'));
mustNot('no-document-save-call', agentTools.includes('document.save()'));
mustNot('no-active-document-save-call', agentTools.includes('active.document.save()'));
must('remember-raw-ingest', agentTools.includes("['ingest', target.filePath, '--topic', topic.id]"));
must('remember-human-confirmed-authority', agentTools.includes('authority=human_confirmed_source_admission'));
must('remember-does-not-persist-hk', agentTools.includes('human_authorship_persisted=no'));

must('python-policy-win32', pythonRuntimePolicy.includes("['python', 'py', 'python3']"));
must('python-policy-unix', pythonRuntimePolicy.includes("['python3', 'python']"));
must('python-explicit-override', pythonRuntime.includes("source: 'configured'"));
must('python-auto-source', pythonRuntime.includes("source: 'auto'"));
must('python-no-setting-mutation', !pythonRuntime.includes('.update('));

must('durable-agent-state-cli', agentTools.includes("runPythonModule(context, folder, 'dogfood.llm_wiki.agent_state_cli'"));
must('durable-source-locators', agentTools.includes('durableSourceLocators'));
must('legacy-locator-migration', agentTools.includes("'locator-set', row.source_id"));
must('durable-pending-list', agentTools.includes('openPendingLineageRows'));
must('durable-budget-reserve', agentTools.includes('reserveMaintenanceCall'));
must('zero-limit-still-disables', agentTools.includes("status: 'SKIPPED_DAILY_CALL_LIMIT'"));
must('soft-guard-function', agentTools.includes('confirmMaintenanceSoftGuard'));
must('soft-guard-modal', agentTools.includes('Continue Today'));
must('soft-guard-explains-not-hard-cap', agentTools.includes('soft guard, not a hard cap'));
must('soft-guard-decline-status', agentTools.includes('SKIPPED_SOFT_GUARD_DECLINED'));
must('soft-guard-tool-output', agentTools.includes('maintenance_daily_limit_mode='));
mustNot('reservation-does-not-pass-hard-limit', agentTools.includes("'usage-reserve', '--day', localDayKey(), '--limit'"));
must('pending-lineage-skip', agentTools.includes('SKIPPED_PENDING_LINEAGE_DECISION'));
must('continuation-decision-output', agentTools.includes('continuation_decision_id='));
must('remaining-predecessors-output', agentTools.includes('remaining_predecessor_source_ids='));

must('lineage-enum', agentTools.includes("LINEAGE_RELATIONS = new Set(['correction', 'change', 'dispute', 'supersede', 'independent'])"));
must('lineage-modal', agentTools.includes('Confirm what this saved file change means?'));
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
must('hk-modal', agentTools.includes('Save this as your confirmed project knowledge?'));
must('hk-full-confirmation-text', agentTools.includes('will be remembered as something you explicitly confirmed'));
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

must('release-status-bar', extension.includes("status.text = '$(book) LLM Wiki'"));
must('release-status-health-action', extension.includes("status.command = 'llmWiki.doctor'"));
must('release-status-visibility-hook', extension.includes('function setStatusVisible(enabled)'));
must('release-status-deactivate-hide', extension.includes('if (status) status.hide()'));
mustNot('release-status-no-topic', extension.includes('Wiki: no topic'));
mustNot('routine-topic-success-toast', extension.includes('LLM Wiki topic selected:'));
mustNot('routine-ingest-success-toast', extension.includes('LLM Wiki ingested ${path.basename'));
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

console.log('VS-CODE-DOGFOOD-STATIC PASS version=0.1.21 agentToolDisposables=6 contributedTools=7 uxVNextU0=native-single-view+welcome+agent-first explicitWorkspaceOptIn=yes queryPlaneL0=optin-local-grant+daily-cap+no-raw-fallback namedStoreF1=explicit-grants+pre-retrieval-scope+scoped-provenance+write-isolation relevantRegionRead=yes doctorPureDiagnostic=yes memoryV4=yes verifiedReadV3=yes durableAuthorityState=yes humanKnowledgeV1=yes maintenanceSoftGuard=yes singleFolderFailClosed=yes');