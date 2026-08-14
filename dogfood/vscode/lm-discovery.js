'use strict';

const REQUIRED_LUNA_ID = 'gpt-5.6-luna';

function text(value) {
  return value === undefined || value === null ? '' : String(value);
}

function finiteNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : null;
}

function emptyReport(apiAvailable, selectionStatus) {
  return {
    schema: 'llm-wiki-lm-discovery-v0',
    generationCalls: 0,
    requestedVendor: 'copilot',
    requiredModel: REQUIRED_LUNA_ID,
    apiAvailable,
    selectionStatus,
    modelCount: 0,
    exactLuna: { idMatches: 0, familyMatches: 0, exactMetadataSignal: false },
    models: [],
  };
}

function sanitizeModel(model) {
  return {
    id: text(model && model.id),
    family: text(model && model.family),
    version: text(model && model.version),
    name: text(model && model.name),
    vendor: text(model && model.vendor),
    maxInputTokens: finiteNumber(model && model.maxInputTokens),
  };
}

function summarizeModels(models) {
  const rows = (models || [])
    .map(sanitizeModel)
    .sort((a, b) => `${a.id}\u0000${a.family}\u0000${a.version}`.localeCompare(`${b.id}\u0000${b.family}\u0000${b.version}`));

  const exactIdMatches = rows.filter((row) => row.id === REQUIRED_LUNA_ID).length;
  const exactFamilyMatches = rows.filter((row) => row.family === REQUIRED_LUNA_ID).length;

  return {
    schema: 'llm-wiki-lm-discovery-v0',
    generationCalls: 0,
    requestedVendor: 'copilot',
    requiredModel: REQUIRED_LUNA_ID,
    selectionStatus: 'OK',
    modelCount: rows.length,
    exactLuna: {
      idMatches: exactIdMatches,
      familyMatches: exactFamilyMatches,
      exactMetadataSignal: exactIdMatches > 0 || exactFamilyMatches > 0,
    },
    models: rows,
  };
}

async function discoverCopilotModels(vscodeApi) {
  const api = vscodeApi || require('vscode');
  if (!api.lm || typeof api.lm.selectChatModels !== 'function') {
    return emptyReport(false, 'API_UNAVAILABLE');
  }

  try {
    const models = await api.lm.selectChatModels({ vendor: 'copilot' });
    return { apiAvailable: true, ...summarizeModels(models) };
  } catch (_) {
    return emptyReport(true, 'ERROR');
  }
}

module.exports = {
  REQUIRED_LUNA_ID,
  sanitizeModel,
  summarizeModels,
  discoverCopilotModels,
};
