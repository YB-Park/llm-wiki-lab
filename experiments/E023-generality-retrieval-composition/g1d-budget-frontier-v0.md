# E023 G1d — zero-model evidence-budget frontier

Status: **POSTHOC / ZERO MODEL / NON-PRIMARY / DOES NOT CHANGE G1d VERDICT**  
Frozen run: `32322429563`  
Frozen G1d promotion: `NOT_EARNED`

## Question

After G1d rejected deterministic RRF top-4, is the remaining positive-authority miss better explained by the retrieval mechanism or by the fixed top-5 evidence cutoff itself?

This analysis performs **zero model calls**. It re-scores only already-frozen exact BM25 rankings and G1d evidence with the prospectively frozen authority-sufficiency contract.

## Exact-query evidence-budget frontier

Authority status for exact BM25:

| Budget | Clean | Conflation risk | Insufficient |
| --- | ---: | ---: | ---: |
| top-3 | 4 | 0 | 4 |
| top-4 | 2 | 2 | 4 |
| top-5 | 3 | 4 | 1 |
| **top-6** | **4** | **4** | **0** |
| top-7 | 4 | 4 | 0 |
| top-8 | 4 | 4 | 0 |

The only A@5 positive-authority miss is BQ006. Its uniquely load-bearing governing-policy anchor `B013` sits at **exact BM25 rank 6**.

Adding that one next-ranked object makes BQ006 `SUFFICIENT_CLEAN`; therefore exact BM25 top-6 is positive-authority sufficient on **8/8** frozen G1d questions.

This says nothing yet about semantic answer quality at top-6. The BQxxx slice is now inspected and must not be semantically rerun for promotion.

## Why G1d did not recover B013

The D planner correctly states that Cedar's authoritative EU-only rule is missing and asks a targeted query for that rule.

But `B013` ranks:

- exact query: **6**;
- first targeted follow-up: **4**;
- second targeted follow-up: absent from the scored ranking.

G1d admitted only the top-3 follow-up hits into the candidate pool, so `B013` never became selectable. The planner's semantic diagnosis was directionally correct, but the lexical retrieval/candidate cutoff still excluded the authority.

## Distractor lesson

The four A@5 `SUFFICIENT_WITH_CONFLATION_RISK` questions are BQ001, BQ002, BQ007, and BQ008.

All four A semantic answers are frozen `PASS`: the composer had explicit load-bearing positive authority and did not conflate the same-name/product/capability distractor.

This does **not** prove distractors are harmless. It does show that on the frozen G1d slice, forcing every context from `RISK` to `CLEAN` was not the primary semantic bottleneck. The actual critical semantic failure was BQ006, where governing authority was absent.

The evidence therefore shifts priority from “perfectly clean the context” toward **“do not omit the governing/load-bearing authority.”**

## Cross-experiment recurrence

This is not the first rank-boundary signal in E023.

Earlier G1a zero-model analysis found that several flat-source misses sat immediately outside a fixed top-5 cutoff; G1b then showed that targeted retrieval could repair one consequential bridge but did not broadly earn promotion.

G1d now provides a new, separately frozen example where the only exact top-5 positive-authority insufficiency is resolved at rank 6, while a more expensive planner + fixed candidate cutoff + RRF path fails to recover it.

The recurrence does **not** prove that `top-6` is a universal product constant. It does justify testing **evidence budget before retrieval complexity** as the next simple competitor.

## Current hypothesis

The next prospective G1 comparison should not start from another selector trick.

A simpler candidate is:

> **exact BM25 + a slightly larger explicit evidence budget (preferably character/token bounded rather than a permanent source-count constant) + the same authority-preserving composer**

The research question is whether a modest evidence-budget increase recovers load-bearing authority more reliably and cheaply than planner/selector machinery, without increasing semantic conflation or context-noise errors.

A valid paid comparison requires a **new separated slice** and a preregistered budget rule before semantic answers are generated. Do not rerun BQxxx.

## What this does not authorize

- no retroactive G1d promotion;
- no same-slice semantic top-6 run;
- no claim that six sources is the product default;
- no G2 persistence;
- no graph/entity/KnowledgeUnit storage;
- no automatic identity/routing;
- no vector default;
- no evaluator clauses in runtime;
- no Dogfood runtime change.

Run:

```bash
python3 experiments/E023-generality-retrieval-composition/analyze_g1d_budget_frontier.py
```

Expected first line:

```text
E023 G1d zero-model evidence-budget frontier: PASS
```
