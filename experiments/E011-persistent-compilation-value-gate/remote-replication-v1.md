# E011 Stage 1A remote transport replication v1

Status: **replication protocol fixed before remote scored calls**

## Purpose

Replicate the frozen E011 Stage 1A semantic experiment on GitHub Actions using the same `gpt-5.6-luna`, corpus, conditions, prompts, retrieval, scoring, seeds, duplicate-prompt reuse, and analysis semantics while replacing the corporate Copilot CLI text stdout boundary with Copilot CLI JSONL programmatic output.

The original corporate run remains historical evidence and is never overwritten or rerun in place.

## What is unchanged

- generated documents/query fingerprints
- `R0`, `R1`, `C0`, `C1`
- BM25 and top-k
- compiler prompt
- answer prompt and contract
- model: `gpt-5.6-luna`
- build seed `20260814`
- answer seed `20260815`
- 24 logical builds
- 288 logical answer tasks with exact-prompt deduplication
- frozen quality metrics and topic-cluster analysis
- reuse regimes `N=1,3,10`

`validate_frozen_a1.py` must pass before the remote scored run. No semantic fixture is changed for this replication.

## Transport change under test

Copilot CLI is invoked on GitHub Actions with `--output-format=json --stream=off`. The experimental answer passed to the frozen E011 parser is only the final `assistant.message` event's `data.content` string. CLI event envelopes, UI decoration, session events, and usage events are not treated as model answer text.

The adapter requires:

- every non-empty CLI stdout line to be valid JSONL;
- exactly one usable final-answer content payload per call;
- event model `gpt-5.6-luna`;
- no tool requests;
- OTel metadata present with message-content capture disabled.

The frozen E011 answer parser then decides whether the extracted model content satisfies its answer JSON contract. No prefix stripping, smart-quote repair, comma repair, JSON5, or semantic repair is added by the remote transport adapter.

## Tool/security boundary

- synthetic/public experiment only; no corporate data;
- workflow token: `contents: read`, `copilot-requests: write` only;
- built-in MCP servers disabled;
- Copilot tools excluded;
- custom instructions disabled;
- remote session export disabled;
- OTel prompt/response content capture disabled.

## Cost discipline

The GitHub-hosted remote run has two independent guards:

1. `--max-ai-credits=30` per Copilot response;
2. repository-side cumulative estimated-credit guard of **700 AI credits** for the complete replication.

Estimated credits use the published GPT-5.6 Luna default-tier token rates and `1 AI credit = $0.01`: non-cached input $1/M, cache-read input $0.10/M, output $6/M. The runner stops before starting another call once completed-call estimated usage reaches the cumulative guard. Any partial artifacts are preserved.

The 700-credit ceiling is a safety ceiling, not a target. Do not spend credits merely because they are available.

## OTel correction

Prior local telemetry aggregation could count both the model `chat` span and parent `invoke_agent` span, duplicating the same usage. Remote v1 reads the single `invoke_agent` span for per-call token/cost accounting. Historical E011 quality outcomes are unaffected by this accounting correction; token-volume absolute totals from the earlier run should be treated cautiously.

## Preflight

Before scored corpus calls, one separate fictional remote preflight verifies JSONL extraction, Luna model identity, no tool use, and OTel. It is not part of E011 quality scoring.

## Interpretation

This is a replication after the first E011 outcome was observed, so it is not a fresh blinded discovery experiment. Its primary value is to separate transport/runtime effects from the frozen semantic Value Gate result. Any architecture conclusion still requires realistic/shadow-workload evidence.
