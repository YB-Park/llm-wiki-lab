# E023 G1c-R1 preregistration v0 — B-only recovery replication

Status before semantic generation: **PREREGISTERED RECOVERY / ZERO MODEL CALLS ON THIS PR / NO PAID RUN AUTHORIZED**.

G1c v0 run `32229563330` is frozen as `INVALID_EXECUTION`: the A arm completed, but a runner aggregation bug crashed after the first B planner/selector/composer sequence and before that B row was persisted. No complete B comparison exists and no G1c retrieval verdict is valid from v0.

R1 is a new evidence identity. It is not a reroll that replaces v0.

## 1. Frozen causal question

The causal question is unchanged from merged G1c preregistration:

> On the six prospectively separated authority-sufficiency questions, does the already-defined evidence-follow loop produce cleaner, authority-sufficient final contexts than exact-question BM25 top-5, without degrading questions whose baseline context is already clean?

R1 changes only execution recovery mechanics required to obtain the previously unobserved B arm.

## 2. What remains frozen byte-for-byte / semantically unchanged

R1 must reuse from G1c v0:

- `authority-sufficiency-v0/` anchors, questions, and evaluator contract;
- exact-question BM25 implementation and frozen A top-5 baseline;
- B initial top-5;
- planner prompt and JSON contract;
- 0–2 follow-up query limit;
- same BM25 top-3 per follow-up query;
- selector prompt and <=5 final-anchor contract;
- composer prompt and JSON contract;
- typed `RAW_MEMORY` versus `HUMAN_KNOWLEDGE` handling;
- evaluator isolation from all model-facing prompts;
- strict primary promotion: B `SUFFICIENT_CLEAN` on 6/6;
- `TARGETED_SIGNAL_ONLY` fallback rule;
- semantic adjudication categories and truth-by-luck rule.

No question-specific retrieval or prompt rule may be added after inspecting v0 A outputs.

## 3. R1 arm

R1 executes **B only** for `AQ001`–`AQ006`:

1. deterministic exact-question top-5;
2. planner call;
3. 0–2 deterministic BM25 follow-up queries;
4. selector call choosing 1–5 candidate anchors;
5. offline authority-sufficiency evaluation;
6. composer call from selected full authority.

The A comparison is the prospectively frozen deterministic authority baseline: 4 `SUFFICIENT_CLEAN`, 1 `SUFFICIENT_WITH_CONFLATION_RISK`, 1 `INSUFFICIENT_AUTHORITY`. A semantic model calls are not repeated.

## 4. Call budget

- exact model: `gpt-5.6-luna`;
- questions: 6;
- planner: 6 calls;
- selector: 6 calls;
- composer: 6 calls;
- **maximum and expected full execution: 18 semantic call attempts**;
- semantic rerolls inside R1: 0;
- per-call AI-credit ceiling parameter: 30;
- actual tokens/credits are recorded only if upstream exposes them; never infer from call count.

The lost v0 AQ001 B calls do not count toward the R1 budget because R1 is a separate replication identity. They remain permanently recorded as lost v0 evidence, not overwritten.

## 5. Persistence-before-aggregation requirement

R1 must be more failure-resilient than v0 without changing semantics:

- create result artifact before first call;
- after planner: append/update and persist the question row;
- after deterministic candidate retrieval: persist;
- after selector/final authority evaluation: persist;
- after composer: persist;
- do **not** compute aggregate promotion during a partial six-question loop;
- compute the aggregate retrieval verdict only after all six B rows are present;
- artifact upload/evidence capture runs even when execution exits nonzero.

This is an evidence-retention fix, not a retrieval mechanism change.

## 6. Frozen primary verdict

Using the already-frozen evaluator:

### `EARNED_FOR_BROADER_G1_CONSIDERATION`

Only if all six R1 B final contexts are `SUFFICIENT_CLEAN`, each contains <=5 anchors, and all planner/selector contracts are valid.

### `TARGETED_SIGNAL_ONLY`

Only if strict promotion fails but:

- R1 B clean count > frozen A baseline clean count 4;
- AQ003–AQ006 remain `SUFFICIENT_CLEAN`;
- none of AQ003–AQ006 gains forbidden-conflation risk;
- all planner/selector contracts are valid.

Otherwise `NOT_EARNED`.

Semantic composer quality is adjudicated separately and cannot rewrite this context-selection verdict.

## 7. Execution sequencing

This preregistration contains no paid runner or request.

Only after merge may a separate R1 execution addendum freeze:

- dedicated `run_g1c_r1.py`;
- dedicated remote request;
- dedicated main-push workflow;
- exact source SHA execution boundary.

The archived v0 workflow must be source-SHA locked so later runner/recovery changes cannot accidentally rerun the 24-call v0 experiment.

## 8. Non-conclusions

R1 cannot directly authorize G2 persistence, graph/entity/KnowledgeUnit storage, vector defaults, automatic identity merge/split, automatic semantic routing, background semantic maintenance, or DERIVED state as terminal authority.
