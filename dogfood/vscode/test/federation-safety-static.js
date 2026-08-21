'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const vscodeRoot = path.resolve(__dirname, '..');
const dogfoodRoot = path.resolve(vscodeRoot, '..');
const memoryRead = fs.readFileSync(path.join(vscodeRoot, 'memory-read-service.js'), 'utf8');
const queryPlane = fs.readFileSync(path.join(vscodeRoot, 'query-plane.js'), 'utf8');
const personalLibrary = fs.readFileSync(path.join(vscodeRoot, 'personal-wiki-library.js'), 'utf8');
const scopedRead = fs.readFileSync(path.join(vscodeRoot, 'scoped-read-tool.js'), 'utf8');
const agentTools = fs.readFileSync(path.join(vscodeRoot, 'agent-tools.js'), 'utf8');
const pythonRuntime = fs.readFileSync(path.join(vscodeRoot, 'python-runtime.js'), 'utf8');
const federationRead = fs.readFileSync(path.join(dogfoodRoot, 'llm_wiki', 'federation_read_cli.py'), 'utf8');

function must(label, condition) {
  assert.ok(condition, `FEDERATION-SAFETY ${label}`);
}
function mustNot(label, condition) {
  assert.ok(!condition, `FEDERATION-SAFETY ${label}`);
}

must('external-generic-runner-forbidden', memoryRead.includes("throw new Error('external_generic_python_runner_forbidden')"));
must('external-read-dedicated-module', memoryRead.includes("const FEDERATION_READ_MODULE = 'dogfood.llm_wiki.federation_read_cli'"));
must('external-read-auto-runtime-only', memoryRead.includes('resolveAutoPythonRuntime(folder)'));
must('external-read-isolated-python-flags', memoryRead.includes("args: ['-I', '-S', '-c', ISOLATED_MODULE_RUNNER"));
must('external-read-clears-pythonpath', memoryRead.includes('delete env.PYTHONPATH'));
must('external-read-clears-pythonhome', memoryRead.includes('delete env.PYTHONHOME'));
must('external-read-clears-pythonstartup', memoryRead.includes('delete env.PYTHONSTARTUP'));
must('external-read-clears-pythonuserbase', memoryRead.includes('delete env.PYTHONUSERBASE'));
must('trusted-core-bundled-first', memoryRead.includes("path.join(bundled, 'dogfood', 'llm_wiki', 'federation_read_cli.py')"));
must('external-handle-requires-continuity-witness', memoryRead.includes('library.AUTHORITY_ANCHOR_RE.test(String(handle.authorityAnchor'));
must('external-standing-grant-rechecked', memoryRead.includes('library.resolveStoreId(context, folder, wikiRoot(folder), store.storeId)'));
must('external-read-rechecks-js-continuity', memoryRead.includes('function revalidateExternalStore(context, folder, storeHandle)'));
must('external-read-passes-continuity-to-bridge', memoryRead.includes("['--root', store.root, '--expected-authority-anchor', store.authorityAnchor, bridgeCommand, ...args]"));
must('external-integrity-through-dispatch', memoryRead.includes("runReadOperation(context, folder, store, 'integrity')"));
must('external-query-evidence-through-dispatch', memoryRead.includes("runReadOperation(context, folder, store, 'relevant'"));
must('external-source-read-through-dispatch', memoryRead.includes("runReadOperation(context, folder, store, 'read'"));
must('external-hk-bracketed-by-revalidation', (memoryRead.match(/revalidateExternalStore\(context, folder, store\)/g) || []).length >= 2);

must('auto-python-runtime-is-distinct', pythonRuntime.includes('async function resolveAutoPythonRuntime(folder)'));
must('auto-python-runtime-does-not-read-config-in-function', /async function resolveAutoPythonRuntime\(folder\)[\s\S]*?for \(const candidate of autoPythonCandidates\(\)\)/.test(pythonRuntime));

must('external-composer-trusted', queryPlane.includes('trusted: expectedStoreHandle.isCurrentStore === false'));
must('external-composer-uses-trusted-invocation', queryPlane.includes('memoryRead.trustedPythonInvocation('));
must('named-store-resolves-before-reservation', queryPlane.indexOf('library.resolveNamedStore(this.context, folder') < queryPlane.indexOf('reserveQueryCall(this.context, folder, grant)'));
must('named-store-integrity-before-reservation', queryPlane.indexOf('memoryRead.assertStoreIntegrity(this.context, folder, storeHandle)') < queryPlane.indexOf('reserveQueryCall(this.context, folder, grant)'));
must('query-usage-lock-is-keyed', queryPlane.includes('const reservationLocks = new Map()') && queryPlane.includes('async function withReservationLock(key, operation)'));
must('query-reservation-is-serialized', /async function reserveQueryCall[\s\S]*?return withReservationLock\(key, async \(\) =>/.test(queryPlane));
must('query-reservation-rereads-state-under-lock', /return withReservationLock[\s\S]*?context\.workspaceState\.get\(key, \{\}\)/.test(queryPlane));
must('query-grant-binds-random-workspace-epoch', queryPlane.includes('workspaceActivation.workspaceEpoch(optIn)'));
must('pre-model-authorization-explicit', queryPlane.includes('function preModelAuthorization(context, folder, requestedStore, originalStoreHandle)'));
must('pre-model-query-grant-rechecked', /function preModelAuthorization[\s\S]*?const liveGrant = queryGrant\(context, folder\)/.test(queryPlane));
must('pre-model-named-store-rechecked', /function preModelAuthorization[\s\S]*?library\.resolveNamedStore\(context, folder/.test(queryPlane));
must('pre-model-reauthorization-before-composer', queryPlane.indexOf('const live = preModelAuthorization(') < queryPlane.lastIndexOf('const stdout = await runComposerStdin('));
must('final-model-authorization-explicit', queryPlane.includes('function finalModelAuthorization(context, folder, requestedStore, originalStoreHandle, expectedGrant)'));
must('final-model-grant-fingerprint-bound', queryPlane.includes('grantFingerprint(live.grant) !== grantFingerprint(expectedGrant)'));
must('composer-before-spawn-hook', queryPlane.includes("if (typeof options.beforeSpawn === 'function') options.beforeSpawn();"));
const beforeSpawnIndex = queryPlane.indexOf("if (typeof options.beforeSpawn === 'function') options.beforeSpawn();");
const spawnIndex = queryPlane.indexOf('const child = spawn(executable, fullArgs');
const trustedRuntimeIndex = queryPlane.indexOf('const invocation = await memoryRead.trustedPythonInvocation(');
const currentRuntimeIndex = queryPlane.indexOf('const runtime = await resolvePythonRuntime(folder)');
must('final-auth-after-runtime-preparation', beforeSpawnIndex > trustedRuntimeIndex && beforeSpawnIndex > currentRuntimeIndex);
must('final-auth-immediately-before-spawn', beforeSpawnIndex >= 0 && spawnIndex > beforeSpawnIndex && !queryPlane.slice(beforeSpawnIndex, spawnIndex).includes('await '));
must('invoke-supplies-final-authorization-hook', queryPlane.includes('beforeSpawn: () => finalModelAuthorization('));
must('revoked-query-stops-with-zero-model-result', queryPlane.includes("live.state === 'query_grant_revoked'") && queryPlane.includes('disabledResult()'));
must('revoked-library-stops-with-zero-model-result', queryPlane.includes("state: 'library_scope_revoked'") && queryPlane.includes('scopeBlockedResult(live.error)'));

must('catalog-v2', personalLibrary.includes('const CATALOG_VERSION = 2'));
must('catalog-authority-anchor', personalLibrary.includes('authorityAnchor'));
must('catalog-absent-is-empty', personalLibrary.includes('if (!raw) return emptyCatalog()'));
must('catalog-version-mismatch-fails-closed', personalLibrary.includes("raw.version !== CATALOG_VERSION") && personalLibrary.includes("throw new Error('library_catalog_corrupt')"));
must('manifest-authority-anchor-function', personalLibrary.includes('function manifestAuthorityAnchor(root)'));
must('authority-anchor-first-ingest', personalLibrary.includes("event.event !== 'ingest'"));
must('authority-continuity-rechecked-at-use', personalLibrary.includes('anchor !== row.authorityAnchor'));
must('authority-handle-recheck-exported', personalLibrary.includes('function verifyStoreHandle(handle)') && personalLibrary.includes('verifyStoreHandle,'));
must('identity-change-fails-closed', personalLibrary.includes("throw new Error('library_store_identity_changed')"));
must('catalog-duplicate-id-fails-closed', personalLibrary.includes('ids.has(storeId)'));
must('catalog-duplicate-root-fails-closed', personalLibrary.includes('roots.has(root)'));
must('registration-mints-new-id-for-new-authority', personalLibrary.includes('sameAuthority ? existing.storeId : `libstore-${crypto.randomUUID()}`'));
must('library-grant-binds-random-workspace-epoch', personalLibrary.includes("const storedEpoch = String(row.workspaceEpoch || '')") && personalLibrary.includes('workspaceEpoch: workspaceActivation.workspaceEpoch(optIn)'));
mustNot('library-grant-has-no-timestamp-auth-fallback', personalLibrary.includes('row.workspaceEnabledAt !== optIn.enabled_at'));

must('federation-bridge-requires-existing-store', federationRead.includes('def _require_initialized(root: Path)'));
mustNot('federation-bridge-never-initializes', federationRead.includes('ensure_workspace'));
must('federation-bridge-pure-discovery', federationRead.includes('discover_current(root, args.query'));
must('federation-bridge-verified-source-read', federationRead.includes('find_source(root, source_id'));
must('federation-bridge-verified-content-read', federationRead.includes('read_text(source)'));
must('federation-bridge-readonly-agent-state', federationRead.includes('def _read_agent_state_readonly(root: Path)'));
must('federation-bridge-requires-continuity-input', federationRead.includes('p.add_argument("--expected-authority-anchor", required=True)'));
must('federation-bridge-rechecks-continuity', federationRead.includes('def _require_authority_anchor(root: Path, expected: str)'));
must('federation-bridge-safe-identity-failure', federationRead.includes('FEDERATION-READ-STOP library_store_identity_changed'));
mustNot('federation-bridge-no-agent-state-writer', federationRead.includes('write_agent_state'));
mustNot('federation-bridge-no-ingest', federationRead.includes('ingest_file'));
mustNot('federation-bridge-no-lineage-mutation', federationRead.includes('supersede_source') || federationRead.includes('correct_source') || federationRead.includes('change_source'));

mustNot('write-tools-do-not-load-library-router', agentTools.includes("require('./personal-wiki-library')"));
mustNot('write-tools-have-no-library-store-input', agentTools.includes('library_store'));
must('scoped-read-remains-read-only-policy', scopedRead.includes('never authorizes source admission, Human Knowledge, lineage, maintenance, or configuration writes'));
must('scoped-read-no-cross-store-fallback', scopedRead.includes('Never retry a missing external source ID against the current store or another store'));
must('scoped-read-preserves-revocation-failures', scopedRead.includes("'library_access_disabled'") && scopedRead.includes("'library_store_identity_changed'") && scopedRead.includes("'library_store_not_registered'"));

console.log('F1-FEDERATION-SAFETY-STATIC PASS strictReadBridge=yes isolatedPython=yes trustedExternalComposer=yes registrationContinuity=yes strictLibraryEpoch=yes catalogFailClosed=yes serializedUsageCap=yes liveReauthorization=yes finalSpawnAuthorization=yes writeIsolation=yes');
