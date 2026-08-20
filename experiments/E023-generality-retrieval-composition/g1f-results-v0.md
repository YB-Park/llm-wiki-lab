# E023 G1f — authority-preserving composition comparison result v0

Status: **COMPLETE / COMPOSITION CANDIDATE PROMOTION NOT EARNED / SIMPLE G1 PATH SAFETY REPLICATED**  
Run: `32349241403`  
Execution source: `eab8c9e4f5ebbe5f43b93a1558fd3f9cc295f772`  
Preregistration merge: `1e5a3f991d0c3b76552725933149702ff6e53d15`  
Evidence commit: `fdae1b5ce645d6951db0d6b703947405c3c3fa78`  
Exact model: `gpt-5.6-luna`  
Semantic calls: **16 / 16**  
Planner / selector / retrieval-model calls: **0 / 0 / 0**  
Rerolls: **0**  
Workflow conclusion: **success**  
Result SHA-256: `de65721f1e127f9dd2d24f1c1ef33dd1a42740fee6f755ef9cf411b476a0b45a`

## Frozen question

G1f tested one causal question on new separated material:

> **When the exact user question and exact selected authority context are held identical, does the frozen generic authority-preserving composer improve semantic behavior over the frozen old composer?**

The paired arms were:

- **O:** frozen `run_g1c.py::composer_prompt` with only the output-handle wording adapted from `Axxx` to `Dxxx`;
- **N:** frozen `composition_prompt_v1.py::composer_prompt_v1`.

Both arms received the same exact `gpt-5.6-luna`, the same question string, and the same preregistered exact-BM25 top-6 rendered context for every DQ pair.

Retrieval was not rerun per arm. There was no planner, selector, RRF, vector lookup, evaluator-aware runtime rule, or semantic reroll.

## Execution integrity

The one-shot run completed exactly as preregistered:

- 8 questions / 2 arms;
- 16/16 semantic attempts;
- zero rerolls;
- `context_identity_contract=true`;
- every O/N pair recorded the same preregistered context SHA-256;
- output contracts and in-context citation-handle validation passed for all 16 calls;
- the intentionally authority-incomplete DQ003 context remained incomplete in both arms.

Execution therefore reached `PENDING_FROZEN_ADJUDICATION` without a transport or parser failure.

## Frozen semantic result

| arm | PASS | PARTIAL | CRITICAL_ERROR |
| --- | ---: | ---: | ---: |
| O — old composer | **7** | **1** | **0** |
| N — composition contract v1 | **7** | **1** | **0** |

Paired comparison:

- N improvements vs O: **0**;
- N regressions vs O: **0**;
- N new critical errors: **0**.

The frozen promotion required at least one paired semantic improvement. Actual was zero:

> **G1f composition candidate promotion is NOT_EARNED. Do not weaken the frozen rule.**

The binding failure is:

`N_PAIRED_IMPROVEMENTS_0_LT_REQUIRED_1`

## Hard cases that both arms passed

### DQ003 — authority-incomplete identity negative control

The top-6 context intentionally omitted the explicit `J. Moreno -> Julia Moreno` identity bridge, which sat at exact BM25 rank 7.

Both O and N:

- correctly reported that J. Moreno approved the temporary exception from D013;
- refused to identify J. Moreno as Julia Moreno;
- surfaced the Julia/Julian ambiguity from supplied authority;
- set `insufficient_authority=true`.

This is important because the simple query-time path did not repeat the earlier E023 truth-by-luck identity failure even when the authoritative bridge was deliberately absent.

### DQ004 — proposition-scoped sufficiency

Both arms correctly answered that the EU-only archive option **could satisfy** the residency rule from D020 + D021 without demanding proof of a deployed configuration that the question did not ask for.

Both also preserved the authorization boundary:

- D022 customer policy governs emergency access;
- D023 vendor capability does not itself grant authorization.

The G1e `COMPOSITION_OVERCAUTIOUS_INSUFFICIENCY` failure did not recur here.

### DQ001 / DQ007 — user-owned authority

Both arms preserved user/project ownership of the load-bearing decisions:

- DQ001 kept the staged-rollout choice/rationale as a project-team decision and treated the rollback drill as supporting evidence;
- DQ007 kept the capacity change as the project team's recorded decision and independently established recurrence using D039 + D040.

The G1e `COMPOSITION_EPISTEMIC_TYPE_OMISSION` failure did not recur on these separated cases.

## The sole shared PARTIAL — DQ006

Both arms answered the user-facing proposition correctly:

- D032 directly says Rhea Kim's regulated-release signing requirement was narrow;
- D032 explicitly says it was **not** a general objection to serverless;
- both preserved that anti-generalization.

However, the prospective evaluator also required the answer to use D033 as evidence that broader serverless use remained approved. Neither arm cited D033.

Because that requirement was frozen before outputs existed, both answers are adjudicated `PARTIAL` with root cause:

`COMPOSITION_CORROBORATION_OMISSION`

Do not weaken the check post hoc simply because D032 is already sufficient for the narrow proposition.

## What G1f means

### What did not earn promotion

`composition_prompt_v1` did **not** demonstrate incremental semantic value over the frozen old composer on this new separated slice.

It therefore remains a research candidate, not a promoted/default composer.

Do not tune it on DQxxx and rerun the same material.

### What was nevertheless replicated

The old composer itself, on the same strong simple query-time baseline, produced:

- **7/8 PASS**;
- **0 critical errors**;
- safe authority insufficiency on the deliberate negative control;
- correct proposition-scoped sufficiency;
- preserved user-owned decision authority;
- correct direct-vs-attributed, temporal/correction, repeated-support, and project-identity behavior on the remaining cases.

The new composer produced the same profile.

That does not satisfy the paired G1f promotion hypothesis, but it is useful independent evidence that the existing simple query-time G1 path is materially safer on a new separated composition-stress slice than earlier E023 failures suggested.

## Project interpretation

Do **not** immediately launch another prompt-tuning or retrieval-tuning run.

The accumulated G1 evidence now supports a different next question:

> **Is the simple query-time G1 path strong enough, as a research baseline, to close G1 exploration and preregister a narrow G2 persistence comparison?**

That is a **zero-model G1 closure decision first**, not automatic authorization for persistence.

A G1 closure decision should synthesize:

- G1d evidence that planner/RRF complexity did not earn itself;
- G1e prospective evidence that a modest exact-BM25 prefix repaired two authority misses with no semantic regression;
- G1f evidence that the existing simple composer and the new generic composer both reached 7/8 with zero critical errors on separated composition-stress material;
- the fact that `composition_prompt_v1` itself did not outperform the old composer;
- natural Dogfood evidence from Issue #141, which remains the product-value track rather than a synthetic architecture benchmark.

G2 is not authorized by this result alone.

Only if that synthesis explicitly declares G1 strong enough should a **new preregistered G2 experiment** be designed. G2 must hold the query-time baseline fixed and test whether fixed-identity persistent semantic state adds enough repeated-use value to justify lifecycle, repair, stale-state, and human-intervention cost.

## Boundaries unchanged

This result does **not** authorize:

- `composition_prompt_v1` as a product/default composer;
- a hard-coded top-6 product default;
- same-slice AQ/BQ/CQ/DQ semantic reruns;
- persistent semantic dossiers without a separate G2 gate;
- graph DB / universal Entity/Relation/KnowledgeUnit storage;
- automatic identity merge/split/routing;
- vector retrieval defaults;
- evaluator clauses as runtime canonical structure;
- Dogfood runtime changes.

Dogfood 0.1.16 natural installed use continues in parallel. Do not manufacture long-horizon workload, >80k inputs, navigation demand, or hidden-usage complaints merely to produce evidence.
