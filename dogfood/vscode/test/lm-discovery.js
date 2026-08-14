'use strict';

const assert = require('node:assert/strict');
const {
  REQUIRED_LUNA_ID,
  summarizeModels,
  discoverCopilotModels,
} = require('../lm-discovery');

async function main() {
  const exactId = summarizeModels([
    { id: REQUIRED_LUNA_ID, family: 'gpt-5.6', version: '1', name: 'Luna', vendor: 'copilot', maxInputTokens: 200000 },
  ]);
  assert.equal(exactId.selectionStatus, 'OK');
  assert.equal(exactId.exactLuna.idMatches, 1);
  assert.equal(exactId.exactLuna.familyMatches, 0);
  assert.equal(exactId.exactLuna.exactMetadataSignal, true);

  const exactFamily = summarizeModels([
    { id: 'provider-specific-id', family: REQUIRED_LUNA_ID, version: '1', name: 'Luna', vendor: 'copilot' },
  ]);
  assert.equal(exactFamily.exactLuna.idMatches, 0);
  assert.equal(exactFamily.exactLuna.familyMatches, 1);
  assert.equal(exactFamily.exactLuna.exactMetadataSignal, true);

  const fuzzyOnly = summarizeModels([
    { id: 'gpt-5.6-preview', family: 'gpt-5.6', version: '1', name: 'GPT 5.6 Luna Preview', vendor: 'copilot' },
  ]);
  assert.equal(fuzzyOnly.exactLuna.idMatches, 0);
  assert.equal(fuzzyOnly.exactLuna.familyMatches, 0);
  assert.equal(fuzzyOnly.exactLuna.exactMetadataSignal, false);

  let selectorCalls = 0;
  const fakeApi = {
    lm: {
      selectChatModels: async (selector) => {
        selectorCalls += 1;
        assert.deepEqual(selector, { vendor: 'copilot' });
        return [{ id: 'some-model', family: 'other', vendor: 'copilot' }];
      },
    },
  };
  const discovered = await discoverCopilotModels(fakeApi);
  assert.equal(selectorCalls, 1);
  assert.equal(discovered.apiAvailable, true);
  assert.equal(discovered.selectionStatus, 'OK');
  assert.equal(discovered.generationCalls, 0);
  assert.equal(discovered.exactLuna.exactMetadataSignal, false);

  const unavailable = await discoverCopilotModels({ lm: undefined });
  assert.equal(unavailable.apiAvailable, false);
  assert.equal(unavailable.selectionStatus, 'API_UNAVAILABLE');
  assert.equal(unavailable.generationCalls, 0);
  assert.equal(unavailable.modelCount, 0);

  const failed = await discoverCopilotModels({
    lm: {
      selectChatModels: async () => {
        throw new Error('synthetic selector failure that must not be surfaced');
      },
    },
  });
  assert.equal(failed.apiAvailable, true);
  assert.equal(failed.selectionStatus, 'ERROR');
  assert.equal(failed.generationCalls, 0);
  assert.equal(failed.modelCount, 0);
  assert.deepEqual(Object.keys(failed).includes('error'), false);

  console.log('LM-DISCOVERY-TEST PASS exactId=yes exactFamily=yes fuzzyFallback=no selectorFailure=contained generationCalls=0');
}

main().catch((error) => {
  console.error(`LM-DISCOVERY-TEST FAIL type=${error && error.name ? error.name : 'Error'}`);
  process.exitCode = 1;
});
