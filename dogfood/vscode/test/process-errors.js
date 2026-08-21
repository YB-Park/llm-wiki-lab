'use strict';

const assert = require('node:assert/strict');
const { boundedProcessFailure } = require('../process-errors');

assert.equal(
  boundedProcessFailure('Traceback...\nRuntimeError: copilot_auth_failed'),
  'copilot_auth_failed'
);
assert.equal(
  boundedProcessFailure('Traceback...\nRuntimeError: agent_wiki_source_too_large:80001>80000'),
  'agent_wiki_source_too_large:80001>80000'
);
assert.equal(
  boundedProcessFailure('Error: copilot_call_failed:1'),
  'copilot_call_failed:1'
);
assert.equal(
  boundedProcessFailure('Error: query_usage_storage_unavailable'),
  'query_usage_storage_unavailable',
  'daily model-attempt guard storage failure must remain bounded and diagnosable'
);
assert.equal(
  boundedProcessFailure('FEDERATION-READ-STOP library_store_identity_changed'),
  'library_store_identity_changed',
  'the strict read bridge may expose only its bounded allowlisted identity-change code'
);
assert.equal(
  boundedProcessFailure('FEDERATION-READ-STOP /private/project/secret.txt'),
  'llm_wiki_process_failed',
  'the federation prefix must never make arbitrary detail reflectable'
);
assert.equal(
  boundedProcessFailure('C:\\private\\project\\secret.txt\nRuntimeError: something_private'),
  'llm_wiki_process_failed'
);
assert.equal(
  boundedProcessFailure('source text says copilot_auth_failed but final error is unrelated\nRuntimeError: unrelated_failure'),
  'llm_wiki_process_failed',
  'remembered/source text must not spoof a recognized diagnosis'
);
assert.equal(
  boundedProcessFailure('copilot_model_mismatch:evil/model with spaces'),
  'llm_wiki_process_failed',
  'unsafe free-form model strings must not be reflected'
);

console.log('PROCESS-ERRORS-TEST PASS bounded=yes spoofResistant=yes federationAllowlist=yes queryUsageGuard=yes rawDetailReflected=no');
