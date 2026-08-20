# E024 Q1 freeze correction v2

Status: **PROSPECTIVELY FROZEN / ZERO SEMANTIC MODEL CALLS BEFORE THIS CORRECTION**

## Why v2 exists

The first Q1 execution attempt on PR #206 failed before Copilot CLI installation and before any Luna semantic call.

Two preregistration bookkeeping defects were exposed by fail-closed CI:

1. the hand-built per-file SHA-256 manifest did not match the exact Git bytes written to the branch;
2. `context-freeze.json` contained precomputed context hashes/character counts produced before the final renderer bytes were fixed, while the selected memory IDs themselves still matched the deterministic BM25 ranking.

The failed runs therefore provide **no semantic evidence** for or against the Query Plane hypothesis.

## v2 correction principle

Do not repair the experiment by editing observed semantic outputs. There are none.

Instead, simplify the freeze boundary:

- Git commit identity is the authoritative freeze for corpus, questions, renderer, prompts, parser, request, evaluation thresholds, and workflows.
- The execution signal must be the only path changed after the frozen parent commit.
- `context-freeze.json:selected_ids` remains the prospective deterministic retrieval freeze.
- Legacy `context_sha256` and `context_chars` fields from v0 are historical diagnostics only and are not used by v2.
- Actual rendered context SHA-256 and character count are recomputed from the frozen source rows plus frozen renderer and recorded in the immutable v2 result.
- M and Q receive the exact same rendered context bytes for each pair.
- The original Q0 promotion thresholds are unchanged.

## What is unchanged

- 29 memory objects.
- 9 questions.
- exact BM25 top-6 selected IDs.
- required terminal-authority IDs.
- M/Q paired design.
- exact `gpt-5.6-luna`.
- 18 attempts, zero rerolls.
- planner calls = 0.
- selector calls = 0.
- retrieval-model calls = 0.
- answer max = 900 characters.
- Query Plane brief max = 2200 characters.
- median external-context ratio <= 0.35.
- maximum external-context ratio <= 0.50.
- Q semantic >=8/9 PASS, 0 CRITICAL, no paired regression.

## Invalid/no-run execution history

The following are execution-infrastructure history only and must never be adjudicated as semantic trials:

- connector-authored signal commit `e135d3679af6b2d974eb63d7908b527c19d394f9`: no Actions checks, zero semantic calls;
- PR-triggered Q1 run `32378526834`: failed in source-lock validation before Copilot installation, zero semantic calls;
- PR-triggered zero-model run `32378526759`: failed in prereg diagnostic validation, zero semantic calls.

## Interpretation boundary

v2 changes only experiment source-lock mechanics. It does not change the product hypothesis, corpus semantics, prompts, evaluation thresholds, or runtime product code.
