'use strict';

const EXACT_SAFE_CODES = new Set([
  'agent_wiki_model_call_not_authorized',
  'agent_wiki_source_not_current',
  'agent_wiki_source_changed_during_generation',
  'copilot_cli_not_found',
  'copilot_cli_argument_error',
  'copilot_auth_failed',
  'copilot_model_unavailable',
  'copilot_jsonl_invalid',
  'copilot_tool_request_present',
  'copilot_source_citation_missing',
]);

const SAFE_PATTERNS = [
  /^agent_wiki_source_too_large:\d+>\d+$/,
  /^agent_wiki_[a-z0-9_]+_invalid$/,
  /^copilot_call_failed:\d+$/,
  /^copilot_model_mismatch:[A-Za-z0-9_.-]+$/,
  /^copilot_final_message_count:\d+$/,
  /^copilot_raw_source_citation_forbidden:[A-Za-z0-9_.:-]+$/,
  /^copilot_unknown_citation_handle:[A-Za-z0-9_.:-]+$/,
];

function normalizedExceptionCandidate(line) {
  const trimmed = String(line || '').trim();
  if (!trimmed) return '';
  return trimmed
    .replace(/^(?:RuntimeError|ValueError|Error):\s*/, '')
    .trim();
}

function boundedProcessFailure(detail) {
  const lines = String(detail || '')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const candidate = normalizedExceptionCandidate(lines[index]);
    if (EXACT_SAFE_CODES.has(candidate)) return candidate;
    if (SAFE_PATTERNS.some((pattern) => pattern.test(candidate))) return candidate;
  }
  return 'llm_wiki_process_failed';
}

module.exports = {
  boundedProcessFailure,
  normalizedExceptionCandidate,
};
