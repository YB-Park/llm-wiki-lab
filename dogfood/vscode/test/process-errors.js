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

console.log('PROCESS-ERRORS-TEST PASS bounded=yes spoofResistant=yes rawDetailReflected=no');
