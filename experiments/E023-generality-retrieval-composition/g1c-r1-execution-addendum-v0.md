# E023 G1c-R1 execution addendum v0

Status before first R1 semantic call: **EXECUTION CONTRACT FROZEN / PR PATH ZERO MODEL / MAIN PUSH ONLY**.

This addendum implements the already-merged `g1c-r1-preregistration-v0.md`. R1 is a new B-only recovery replication after G1c v0 run `32229563330` was frozen as `INVALID_EXECUTION`.

## 1. Scope

R1 executes only the evidence-follow B arm for `AQ001`–`AQ006`. It does not rerun A. The comparison baseline remains the prospectively frozen deterministic A authority status: 4 `SUFFICIENT_CLEAN`, 1 `SUFFICIENT_WITH_CONFLATION_RISK`, 1 `INSUFFICIENT_AUTHORITY`.

## 2. Frozen request

```json
{
  "b_composer_calls": 6,
  "b_planner_calls": 6,
  "b_selector_calls": 6,
  "candidate_followup_top_k": 3,
  "final_anchor_limit": 5,
  "initial_top_k": 5,
  "max_ai_credits_per_call": 30,
  "max_followup_queries": 2,
  "max_model_call_attempts": 18,
  "model": "gpt-5.6-luna",
  "planner_snippet_chars": 320,
  "question_count": 6,
  "request_id": "e023-g1c-r1-b-only-recovery-v0"
}
```

Any semantic change to the request stops the runner.

## 3. Semantic mechanism is unchanged

`run_g1c_r1.py` directly reuses the frozen G1c v0 implementation for:

- exact BM25 ranking;
- bounded candidate view;
- planner prompt and parser;
- follow-up candidate-pool construction;
- selector prompt and parser;
- full authority context rendering;
- composer prompt and parser;
- typed `RAW_MEMORY` / `HUMAN_KNOWLEDGE` semantics;
- offline authority-sufficiency evaluation.

No evaluator clause, expected status, required/forbidden anchor ID, reference context, or semantic gold is shown to planner, selector, or composer.

## 4. R1 loop

For each of six questions:

1. deterministically reconstruct and assert the frozen exact-question top-5;
2. persist the initial row before any model call;
3. one planner call; persist receipt/output/call count;
4. deterministic 0–2 follow-up BM25 queries and candidate pool; persist;
5. one selector call choosing 1–5 anchors; persist selected IDs, final authority status, receipt, and call count;
6. one composer call using the unchanged G1c composer contract; persist output/receipt/call count.

There are zero semantic rerolls. A failed stage is recorded and never retried within R1.

## 5. Persistence-before-aggregation fix

The v0 defect was evidence lifecycle, not retrieval semantics. R1 therefore freezes these implementation-only corrections:

- result artifact exists before the first semantic call;
- every question row is appended before its planner call;
- every model stage is saved immediately after completion or failure;
- aggregate promotion is never computed during a partial six-question loop;
- aggregate promotion is computed only after the loop has attempted all six questions;
- artifact upload/evidence capture uses `if: always()` and accepts incomplete results as evidence rather than rejecting them before capture.

## 6. Budget and identity

- exact model: `gpt-5.6-luna`;
- planner calls: 6;
- selector calls: 6;
- composer calls: 6;
- maximum/expected full R1 semantic attempts: **18**;
- rerolls: **0**;
- per-call AI-credit ceiling parameter: 30;
- actual tokens/credits remain unknown unless machine-readable upstream data is exposed.

The nine v0 calls remain separate immutable v0 history and are not counted as R1 calls.

## 7. Retrieval-selection verdict

The preregistered rule is unchanged:

- `EARNED_FOR_BROADER_G1_CONSIDERATION`: all six B final contexts are `SUFFICIENT_CLEAN`, each <=5 anchors, planner/selector contracts valid;
- `TARGETED_SIGNAL_ONLY`: strict promotion fails, but B clean count >4, AQ003–AQ006 remain clean with no forbidden risk, planner/selector contracts valid;
- otherwise `NOT_EARNED`.

If a complete six-question B context set does not exist, the aggregate verdict remains `NOT_EXECUTED` and `execution_complete=false`.

Composer quality is adjudicated separately after immutable evidence capture and cannot rewrite the context-selection verdict.

## 8. GitHub execution boundary

The pull-request event runs only zero-model preflight. The semantic `execute` job exists only for the separately merged `main` push that introduces this execution contract. The subsequent result/closeout PR must source-lock or disable the R1 workflow before any other R1-path main change.

Evidence is captured under:

`experiments/E023-generality-retrieval-composition/evidence/g1c-r1-run-<run_id>/`

Evidence-only commits do not match the paid workflow paths.

## 9. Non-conclusions

No R1 outcome directly authorizes G2 persistence, Entity/Relation/KnowledgeUnit storage, graph/vector defaults, automatic identity merge/split, automatic routing, background semantic maintenance, or DERIVED state as terminal authority.
