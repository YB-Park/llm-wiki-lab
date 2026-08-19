# E023 — Generality Retrieval / Composition Gate

Status: **G1a NOT EARNED / G1b NOT EARNED / AUTHORITY-SUFFICIENCY EVALUATION CONTRACT PROSPECTIVELY FROZEN**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy **cross-source semantic knowledge** from heterogeneous admitted authority without first introducing persistent entity/graph/ontology state?

E023 is intentionally **not** an entity-system experiment. It tests retrieval/composition explanations first and now freezes a better way to measure whether the required authority actually reached the composer.

## Core architecture guardrail

- The Authority Core remains knowledge-type agnostic.
- `source-note-v0` is one source-oriented **DERIVED projection**, not the ontology of LLM Wiki.
- Every load-bearing derived statement must resolve to explicit terminal authority: admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`.
- `DERIVED_MEMORY` may help retrieval/compilation/navigation but is not terminal authority.
- Semantic persistence is an optimization that must earn itself after a strong query-time path exists.

## Three gates, in order

1. **G1 Retrieval / Composition** — active.
2. **G2 Persistence** — future only if a strong G1 path still shows a persistence-shaped need.
3. **G3 Identity / Routing** — last, only if persistent semantic targets themselves earn value.

A G1 failure does not authorize G2. A G2 success would not automatically authorize G3.

## G1a — blind planned retrieval — complete / NOT EARNED

Frozen run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero semantic rerolls.

- **A:** exact-question BM25 top-5 -> composer.
- **C:** question-only planner -> 1–3 blind query rewrites -> BM25 + deterministic RRF -> same top-5 -> same composer.

Frozen semantic result:

- A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- C: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- C semantic improvements: **0**;
- promotion: **NOT_EARNED**.

Q001 was the key trust failure. Both arms omitted the explicit S004 identity bridge but confidently merged `J.H. Park` with `Jihoon Park`. The merge happened to match frozen gold, but the supplied authority did not establish it.

> **Truth-by-luck is not trustworthy semantic recovery.**

## G1b — evidence-follow retrieval — complete / frozen promotion NOT EARNED

Frozen run `32217824760`, exact `gpt-5.6-luna`, 12 calls, zero rerolls.

G1b used:

> exact-query top-5 -> inspect bounded evidence -> identify a missing/ambiguous relation -> targeted follow-up BM25 -> bounded selector -> unchanged G1a composer.

Frozen result:

- previously-missing source reached candidate pool: **2 / 4**;
- previously-missing source entered final context: **1 / 4**;
- semantic verdicts: **4 PASS**;
- Q001: **CRITICAL_ERROR -> PASS**;
- regressions: **0**;
- promotion: **NOT_EARNED** because the preregistered final-recovery threshold was >=3/4.

The targeted signal is still important: Q001 was repaired because evidence-follow retrieval recovered S004, selected the explicit identity bridge, and dropped the same-surname distractor while the composer prompt stayed unchanged.

## Evaluation finding — authority sufficiency is not flat source completeness

Posthoc zero-model analysis of already-frozen contexts found:

- G1a A flat required-source complete: **6/10**; load-bearing support complete: **9/10**;
- G1a C flat required-source complete: **6/10**; load-bearing support complete: **9/10**;
- G1b final contexts: **4/4 support-complete**;
- unique G1a support-incomplete question: **Q001**, exactly the frozen critical error;
- Q008: support-complete yet semantically PARTIAL, isolating a composition omission.

This does not rewrite any frozen verdict.

The better measurement question is:

> **Did the selected context contain enough typed authoritative support to establish every load-bearing proposition?**

## Prospective authority-sufficiency contract — zero-model / no paid run

`authority-sufficiency-preregistration-v0.md` and `authority-sufficiency-v0/` freeze a new separated evaluation slice before any new semantic answer is generated.

The package contains:

- 15 new typed authoritative anchors;
- 6 new questions;
- explicit `RAW_MEMORY` and load-bearing `HUMAN_KNOWLEDGE`;
- `all_of`, `any_of`, and `min_count` support clauses;
- unique support, alternatives, repeated-support minima, identity bridges, attribution, negative evidence, temporal correction, and forbidden conflation;
- 14 deterministic zero-model reference contexts;
- no model answers or semantic verdicts.

The evaluator distinguishes:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

Forbidden-conflation risk is deliberately not collapsed into missing positive authority.

Run:

```bash
python3 experiments/E023-generality-retrieval-composition/validate_authority_sufficiency.py
```

Expected first line:

```text
E023 authority-sufficiency prereg validation: PASS
```

This evaluation representation is **not** a product claim graph, semantic storage schema, or authorization for G2/G3.

## Current next decision

Paid retrieval tuning remains paused.

After this prospective evaluator contract is merged and validated, decide whether another **G1 retrieval/selection/composition** mechanism comparison deserves semantic calls. Any such run requires a separate frozen preregistration and execution contract.

Do not jump from G1a/G1b to persistent dossiers, graph/entity infrastructure, vector defaults, or automatic identity/routing.

## Relationship to the product

Dogfood 0.1.16 remains unchanged.

Natural installed dogfood continues in parallel because controlled corpora cannot establish long-horizon value, ambient routing behavior, popup/spend friction, or whether useful reasoning is recovered days or weeks later.
