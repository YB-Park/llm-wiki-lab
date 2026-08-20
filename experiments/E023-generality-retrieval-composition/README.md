# E023 — Generality Retrieval / Composition Gate

Status: **G1a NOT EARNED / G1b NOT EARNED / G1c-R1 NOT EARNED / G1d NOT EARNED / EVIDENCE-BUDGET SIGNAL ACTIVE**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy cross-source semantic knowledge from heterogeneous admitted authority **at query time**, before introducing persistent entity/graph/ontology state?

E023 decomposes G1 into:

1. authority discovery;
2. evidence budgeting/selection;
3. semantic composition;
4. explicit terminal authority typing.

It is not an entity-system experiment.

## Guardrails

- Authority Core remains ontology-agnostic.
- `source-note-v0` is one `DERIVED_MEMORY` projection, not the Wiki ontology.
- Every load-bearing derived statement must resolve to admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`.
- Evaluator clauses are evaluation-only and must not become runtime canonical structure by default.
- G1 failure does not authorize G2 persistence.
- G2 success would not automatically authorize G3 identity/routing.

## Frozen sequence

### G1a — blind query planning / NOT EARNED

Run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero rerolls.

Exact BM25 top-5 and blind planner+RRF both produced **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**. Planner arm improvements: **0**.

Q001 introduced the core trust lesson: the answer confidently merged aliases without the explicit identity bridge.

> **Truth-by-luck is not trustworthy semantic recovery.**

### G1b — evidence-follow retrieval / NOT EARNED, targeted repair observed

Run `32217824760`, exact Luna, 12 calls, zero rerolls.

Evidence-aware follow-up recovered the missing Q001 bridge and moved the semantic verdict `CRITICAL_ERROR -> PASS`, but final recovery reached only **1/4** versus the preregistered `>=3/4` threshold.

This earned a targeted query-time repair signal, not broad policy.

### Prospective authority-sufficiency evaluator

A separated evaluation contract was frozen before later semantic answers. It distinguishes:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

It can express unique authority, alternatives, repeated-support minima, identity/attribution bridges, negative evidence, temporal correction, forbidden conflation, and load-bearing `HUMAN_KNOWLEDGE`.

This representation is **not** a product claim graph.

### G1c v0 — INVALID_EXECUTION

Run `32229563330` failed from a runner aggregation bug. No G1c verdict is taken from it and lost B outputs are not reconstructed or rerolled.

### G1c-R1 — free-form model selector / NOT EARNED

Run `32232116273`, source `5227ac2b3f93c4f807e388822bfff963d0041120`, exact Luna, 18/18 calls, zero rerolls.

| stage | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| exact initial top-5 | 4 | 1 | 1 |
| evidence-follow candidate pool | 4 | 2 | **0** |
| model selector final | 4 | 0 | **2** |

Candidate pools contained enough positive authority for **6/6**, but the model selector discarded recovered/load-bearing authority in AQ001 and AQ004.

This made **authority-preserving evidence selection/budgeting** the next G1 bottleneck.

### G1c-R1 zero-model RRF counterfactual — posthoc only

On the already-inspected AQ slice, deterministic RRF top-4 happened to yield **6/6 clean** contexts across a wide RRF-k sweep. Because the rule was selected after observing failures, it was not promotable. It only justified a new prospective test.

See `g1c-r1-selection-counterfactual-v0.md`.

### G1d — deterministic RRF top-4 / NOT EARNED

Preregistered on new separated `authority-sufficiency-v1` material: 23 anchors, 8 questions, 21 RAW + 2 HUMAN_KNOWLEDGE.

Frozen run:

- run `32322429563`;
- source `c74673a83744789f271fa54c43b20212160007a2`;
- exact `gpt-5.6-luna`;
- **24/24** calls;
- model selector calls **0**;
- rerolls **0**;
- workflow success;
- result SHA-256 `ef57c7a43c782694a0c42d428421b5d9a4bbb72b0a48b52a60c36edafa310bda`;
- result/adjudication: PR #184.

Arms:

- A: exact BM25 top-5 -> composer;
- D: same top-5 -> evidence-aware planner -> targeted BM25 -> deterministic RRF `k=60` -> top-4 -> composer.

Authority result:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A | 3 | 4 | 1 |
| D | 3 | 3 | 2 |

D improvements: **0**. D regressions: **1**. Promotion: **NOT_EARNED**.

Semantic result:

- A: **7 PASS / 1 CRITICAL_ERROR**;
- D: **5 PASS / 2 PARTIAL / 1 CRITICAL_ERROR**;
- D improvements: **0**;
- D regressions: **2**;
- D new critical errors: **0**.

#### Why deterministic RRF failed

The posthoc AQ result did not generalize. Repeated lexical agreement can reinforce a distractor:

- BQ002: same-name B004 remains above the load-bearing B003 identity bridge; B003 falls to fifth and is dropped;
- BQ007: unrelated same-name product B019 remains;
- BQ008: vendor local-admin capability B023 remains even though capability is not authorization policy.

RRF is deterministic, but determinism is not authority awareness.

#### BQ006 — semantic diagnosis succeeded, retrieval still failed

The D planner explicitly identifies Cedar's governing EU-only policy as missing. The authoritative B013 policy anchor ranks exact **6**, first follow-up **4**, and is absent on the second follow-up. Because candidate additions are top-3, B013 never becomes selectable.

Both A and D then give a definitive-looking compliance conclusion without the governing policy authority and are frozen `CRITICAL_ERROR`.

This extends the truth-by-luck lesson from identity to **policy/compliance**.

## Zero-model evidence-budget frontier

Posthoc, 0 model calls, merged via PR #185. Does not alter G1d verdict.

Exact BM25 frontier:

| budget | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| top-3 | 4 | 0 | 4 |
| top-4 | 2 | 2 | 4 |
| top-5 | 3 | 4 | 1 |
| **top-6** | **4** | **4** | **0** |
| top-7 | 4 | 4 | 0 |
| top-8 | 4 | 4 | 0 |

The sole exact top-5 positive-authority miss is BQ006, and B013 sits at rank 6. Exact top-6 is therefore positive-authority sufficient on **8/8** frozen questions.

The four A@5 risk contexts are all semantic PASS, so on this slice removing every distractor was not the critical semantic bottleneck. The critical error occurred where governing authority was absent.

This is a **budget signal**, not a `k=6` product decision.

## Current action

Stay inside **G1 Retrieval / Composition** and pause paid calls at this checkpoint.

Next research question:

> **Can a modest explicit query-time evidence budget recover load-bearing authority more reliably and cheaply than planner/selector complexity, without causing semantic conflation/noise failures?**

Before another paid comparison:

1. use a **new separated slice**;
2. freeze the evidence-budget rule before semantic answers exist;
3. prefer a character/token budget over a universal source-count constant when practical;
4. compare the strong exact-BM25 budget baseline against any more complex retrieval/planning path with the same composer;
5. score positive authority sufficiency, conflation risk, semantic correctness, unsupported claims, evidence size, and model calls separately;
6. do not semantically rerun AQxxx or BQxxx;
7. keep evaluator clauses offline;
8. keep G2/G3 and product runtime unchanged.

## Product relationship

Dogfood 0.1.16 remains unchanged. Natural installed dogfood continues in parallel because controlled corpora cannot establish ambient routing, interaction friction, long-horizon value, or whether the Agent naturally follows authority days or weeks later.
