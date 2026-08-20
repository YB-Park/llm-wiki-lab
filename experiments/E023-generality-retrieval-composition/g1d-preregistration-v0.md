# E023 G1d — deterministic authority-preserving selection preregistration

Status: **PREREGISTRATION / ZERO MODEL / NO SEMANTIC EXECUTION AUTHORIZED BY THIS FILE**  
Tracking: Issue #160  
Predecessor evidence: G1c-R1 run `32232116273`; zero-model selection counterfactual PR #181

## Research question

Can the useful part of evidence-follow retrieval generalize when the free-form model selector is removed and replaced with a simple deterministic evidence budget that is fixed before outcomes on new material?

The causal question is deliberately narrow:

> **Given the same evidence-aware planner and lexical retrieval family, does deterministic multi-query rank fusion preserve load-bearing authority more reliably than exact-query top-5 while avoiding the destructive compression observed in G1c-R1?**

This is still G1 Retrieval / Composition. It does not test or authorize persistence, graph/entity storage, automatic identity routing, or a product runtime change.

## Why G1d exists

Frozen G1c-R1 established three facts on the first prospective authority-sufficiency slice:

1. evidence-follow candidate pools contained sufficient positive load-bearing authority for **6/6** questions;
2. the model selector then reduced AQ001 and AQ004 to insufficient final contexts;
3. a posthoc **zero-model** counterfactual found that evaluator-blind RRF top-4 produced **6/6 SUFFICIENT_CLEAN** contexts across RRF `k` values from 1 through 1000, while top-3 underfilled and top-5 retained conflation risk.

That signal was discovered after observing the frozen slice, so it cannot be promoted on that slice. G1d therefore uses a new separated corpus and freezes the mechanism before any semantic answers are generated.

## New separated evaluation slice

Directory: `authority-sufficiency-v1/`

The slice contains **23 new authoritative anchors** and **8 new questions**. It shares no anchor IDs or exact anchor text with `authority-sufficiency-v0`.

Families:

- person identity / direct-vs-attributed authorship;
- user-owned decision rationale;
- incident hypothesis / causal signal / postmortem / temporal correction;
- vendor geographic constraint and negative evidence;
- non-person project rename / stable project identity;
- narrow security-policy exception and audit scope.

Terminal authority is explicitly typed as `RAW_MEMORY` or `HUMAN_KNOWLEDGE`. The evaluator remains evaluation-only and is not a product claim graph.

## Frozen arms

### Arm A — strong simple baseline

1. exact user question;
2. same object-level BM25 family as prior E023 work;
3. select top **5** anchors;
4. unchanged G1c composer over full selected evidence.

No planner and no selector model call.

### Arm D — evidence-follow + deterministic selection

1. same exact-question BM25 top-5 as A;
2. unchanged G1c evidence-aware planner inspects only bounded metadata/snippets from those initial hits;
3. planner states the missing/ambiguous relation and returns **0–2** targeted queries;
4. same BM25 retrieves top **3** per follow-up query;
5. candidate pool is the union of initial top-5 and follow-up top-3 hits;
6. fuse the exact-query ranking plus all follow-up rankings using deterministic Reciprocal Rank Fusion with **k=60**;
7. restrict fused ranking to the candidate pool;
8. choose exactly the top **4** anchors as the final evidence budget;
9. unchanged G1c composer answers from those full evidence objects.

There is **no model selector** in D.

Tie-break order is frozen as:

1. higher RRF score;
2. better rank in the initial exact-query ranking;
3. lexicographically smaller anchor ID.

The selector receives no authority-sufficiency clauses, expected answers, semantic verdicts, forbidden-conflation labels, or hand-written anchor-specific rules.

## Frozen model and call budget

Exact model: `gpt-5.6-luna`.

For 8 questions:

- A composer: **8** calls;
- D planner: **8** calls;
- D composer: **8** calls;
- D model selector: **0** calls;
- total semantic call attempts: **24**;
- rerolls: **0**.

A later execution contract must fail closed if the exact model or exact call budget differs.

## Evaluation order

The prospective authority-sufficiency contract is primary for retrieval/selection diagnosis. Semantic adjudication is separate.

For each question record:

- A selected anchors and authority status;
- D initial retrieval, planner queries, follow-up rankings, candidate pool, RRF trace, final anchors, authority status;
- composer answer, citations, insufficiency flag, model receipt;
- model-call count and unavailable billing/token fields without inference.

Authority status order for comparison:

`INSUFFICIENT_AUTHORITY < SUFFICIENT_WITH_CONFLATION_RISK < SUFFICIENT_CLEAN`.

## Frozen promotion rule

G1d selection promotion is **EARNED** only if all of the following hold:

1. D final contexts contain **0 INSUFFICIENT_AUTHORITY** cases;
2. D final contexts are `SUFFICIENT_CLEAN` on at least **7/8** questions;
3. D improves authority status versus A on at least **2/8** questions;
4. D regresses authority status versus A on **0/8** questions;
5. all 24 planned semantic call attempts complete with zero rerolls and exact `gpt-5.6-luna`.

Semantic safety is then adjudicated separately. A selection promotion is blocked if D introduces any new `CRITICAL_ERROR` relative to A or if a D answer makes a load-bearing unsupported claim despite its recorded final authority status.

Do **not** weaken these thresholds after execution.

A NOT_EARNED result does not authorize G2. An EARNED result would establish only that this **query-time retrieval/selection mechanism** deserves broader G1/product consideration; it still would not authorize persistence or automatic identity infrastructure.

## Overfitting boundary

The mechanism was chosen from the frozen v0 counterfactual, but all BQxxx material and authority clauses are frozen before semantic execution.

After this preregistration merges:

- do not edit BQxxx anchors/questions/clauses to help G1d;
- do not inspect model answers before the execution identity is frozen;
- do not rerun the old AQxxx slice semantically;
- any corpus/contract correction after execution requires a new experiment identity.

## Execution boundary

This preregistration contains no remote request, no paid runner, and no workflow with `copilot-requests: write`.

A separate execution-addendum PR is required. Its PR event must run zero-model preflight only; only its merged main source SHA may authorize the 24-call execution.
