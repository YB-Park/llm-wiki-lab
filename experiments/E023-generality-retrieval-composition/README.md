# E023 — Generality Retrieval / Composition Gate

Status: **G1a/G1b/G1c-R1/G1d/G1e STRICT PROMOTIONS NOT EARNED / SIMPLE EVIDENCE-BUDGET SIGNAL STRENGTHENED / COMPOSITION BOTTLENECK ACTIVE**  
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
- Evaluator clauses are evaluation-only and do not become runtime canonical structure by default.
- G1 failure does not authorize G2 persistence.
- G2 success would not automatically authorize G3 identity/routing.

## Frozen evidence sequence

### G1a — blind query planning / NOT EARNED

Run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero rerolls. Exact BM25 top-5 and blind planner+RRF both produced **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**; planner improvements 0.

Q001 introduced the core trust lesson:

> **Truth-by-luck is not trustworthy semantic recovery.**

### G1b — evidence-follow / NOT EARNED, targeted repair

Run `32217824760`, exact Luna, 12 calls, zero rerolls. Evidence-aware follow-up repaired Q001 `CRITICAL_ERROR -> PASS`, but the preregistered broad recovery threshold was missed.

### Prospective authority-sufficiency evaluator

The evaluation-only contract distinguishes `INSUFFICIENT_AUTHORITY`, `SUFFICIENT_CLEAN`, and `SUFFICIENT_WITH_CONFLATION_RISK` and can express unique support, alternatives, repeated-support minima, identity/attribution bridges, negative evidence, temporal correction, forbidden conflation, and terminal `HUMAN_KNOWLEDGE`.

This representation is **not** a product claim graph.

### G1c-R1 — free-form model selector / NOT EARNED

Run `32232116273`, exact Luna, 18/18 calls, zero rerolls. Evidence-follow candidate pools reached sufficient positive authority on **6/6**, but the model selector dropped load-bearing evidence and produced two insufficient finals.

### G1d — deterministic RRF top-4 / NOT EARNED

Run `32322429563`, exact Luna, 24/24 calls, zero rerolls.

- exact BM25 A: **3 clean / 4 risk / 1 insufficient**;
- planner + targeted BM25 + deterministic RRF D: **3 clean / 3 risk / 2 insufficient**;
- D authority improvements 0, regressions 1;
- semantic A **7 PASS / 1 CRITICAL**;
- semantic D **5 PASS / 2 PARTIAL / 1 CRITICAL**.

RRF did not generalize from a posthoc prior slice. Repeated lexical consensus can amplify same-name/product/capability distractors. Planner diagnosis can also correctly identify a missing authority class while lexical candidate cutoffs still fail to retrieve the authoritative object.

### G1d zero-model evidence-budget frontier

PR #185 found that the sole exact top-5 positive-authority miss had its governing policy at exact rank 6. Exact top-6 was therefore positive-authority sufficient on 8/8 frozen G1d questions, while the top-5 risk cases were all semantic PASS.

This justified a new prospective simple-budget replication. It did not establish `k=6` as policy.

## G1e — prospective exact top-5 vs top-6 replication

G1e used new separated `authority-sufficiency-v2` material: **35 anchors / 8 questions / 32 RAW_MEMORY / 3 HUMAN_KNOWLEDGE**.

There was no planner, query rewrite, RRF, or selector model. The only causal difference was the exact ranked evidence prefix.

### Phase 0 — zero model / PASSED

PR #187:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A5 exact top-5 | 2 | 4 | 2 |
| B6 same ranking top-6 | 3 | 5 | **0** |

B6 authority improvements: **2**; regressions: **0**.

The sixth object supplied:

- CQ001 explicit `R. Singh -> Rina Singh` identity authority;
- CQ008 the second independent monthly-close observation needed for the word “repeated”.

### Phase 1 — semantic result / strict promotion NOT EARNED

Run `32324460519`, source `505740b74776fc7b7988e9c168c9c9d0ed2067fa`, exact Luna, **16/16** composer calls, planner 0, selector 0, zero rerolls.

Result SHA-256: `865d89ad8c8b219493823bd21413196f658a9ffa2fdd3ed2948bb34b20f16727`.

Frozen semantic adjudication:

- A5: **5 PASS / 1 PARTIAL / 1 FAIL_RETRIEVAL / 1 CRITICAL_ERROR**;
- B6: **6 PASS / 2 PARTIAL / 0 FAIL / 0 CRITICAL_ERROR**;
- B6 improvements: **2**;
- B6 regressions: **0**;
- B6 new critical errors: **0**.

The frozen rule required >=7/8 B6 PASS. Actual is 6/8:

> **G1e strict promotion is NOT_EARNED. Do not weaken the rule.**

### What the budget increase genuinely repaired

**CQ001:** A5 lacked the identity bridge and still asserted Rina Singh = R. Singh, a `CRITICAL_ERROR`. B6 adds rank-6 C003 and moves to `PASS`.

**CQ008:** A5 had only one independent monthly-close observation and correctly surfaced retrieval insufficiency. B6 adds rank-6 C033 and completes the repeated-observation authority.

Across all eight questions the extra evidence caused **0 semantic regressions and 0 new critical errors** with no planner/selector calls.

This is the strongest prospective evidence-budget signal in E023 so far. It makes exact BM25 + modestly larger evidence prefix the current **strong simple retrieval baseline**. It does not make six sources a product default.

## Current binding failures are composition-side

B6 has **zero authority-incomplete contexts**, but two semantic partials remain:

1. **CQ002 — overcautious insufficiency:** the context is sufficient for the proposition asked and the prose is substantively correct, but the structured answer declares insufficiency because it silently demands a stronger guarantee.
2. **CQ008 — epistemic-type omission:** the context contains complete repeated-observation evidence plus the user-owned C034 capacity decision, but the answer presents that decision as an ordinary fact instead of preserving its `HUMAN_KNOWLEDGE` status in natural language.

These are recurring E023 composition classes.

## Current action

Paid calls pause. Do not rerun AQxxx/BQxxx/CQxxx.

Next research question:

> **Can a generic composer contract preserve terminal epistemic type and calibrate insufficiency to the actual load-bearing proposition, without exposing internal storage jargon or importing evaluator/domain schemas into runtime?**

Next deliberate work:

1. keep B6-like simple evidence budgeting as the strong retrieval baseline; do not retune retrieval simultaneously;
2. prospectively define generic composition rules for user-owned authority, direct-vs-attributed evidence, missing bridges, proposition-scoped insufficiency, temporal corrections, and explicit negative evidence;
3. validate those rules with zero-model/adversarial fixtures first;
4. only then run a new separated semantic comparison with retrieval held fixed;
5. measure PASS/critical errors, epistemic-type preservation, insufficiency calibration, citations, and model calls separately;
6. keep evaluator clauses offline and product runtime unchanged.

## Product relationship

Dogfood 0.1.16 remains unchanged. Natural installed dogfood continues in parallel because controlled corpora cannot establish ambient routing, interaction friction, long-horizon value, or whether the Agent naturally follows authority days or weeks later.
