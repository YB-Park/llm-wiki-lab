# E023 G1e — exact BM25 evidence-budget replication preregistration

Status: **PREREGISTRATION / ZERO-MODEL FIRST GATE / NO SEMANTIC EXECUTION AUTHORIZED BY THIS FILE**  
Tracking: Issue #160  
Predecessor evidence: G1d run `32322429563`; zero-model budget frontier PR #185

## Research question

E023 has now rejected both blind planning and two different final-selection mechanisms, while independently observing load-bearing authority immediately outside fixed top-5 cutoffs on more than one separated slice.

G1e asks the smallest remaining query-time question:

> **Does increasing the exact-BM25 evidence prefix from five to six whole authoritative objects reliably reduce missing load-bearing authority on new material, without creating enough additional context noise to harm semantic answers?**

This is a controlled **source-count budget replication**, not a product decision that `k=6` is correct.

## Why this is not a 6,000-character gate yet

The current product already has character boundaries, but they describe different operations:

- `wikiRead` / `agent_memory_cli read` defaults to **6,000 raw characters for one source** and hard-stops at 12,000;
- E014 retrieval calibration renders at most **320 context characters per retrieval hit**.

Neither is an existing **global multi-source answer-context budget**. Reusing `6000` as a total G1 evidence budget would therefore invent a new policy rather than test an existing one.

G1e stays at the abstraction directly implicated by the frozen E023 signal: a one-object rank-prefix increase. It records actual evidence characters for both arms. If this simple mechanism earns itself prospectively, a later product-facing gate may translate the result into a character/token budget rather than hard-code a source count.

## New separated slice

Directory: `authority-sufficiency-v2/`

The slice contains:

- **35 new anchors**;
- **8 new questions**;
- 32 `RAW_MEMORY` anchors;
- 3 load-bearing `HUMAN_KNOWLEDGE` anchors;
- no IDs or exact anchor text shared with v0/v1;
- no model answers or semantic verdicts.

Families:

- person identity / attribution;
- governing vendor/customer constraints;
- user-owned decision rationale;
- incident hypothesis / causal evidence / postmortem;
- non-person project rename identity;
- security-policy exceptions;
- explicit negative characterization evidence;
- repeated observations supporting a user-owned capacity decision.

This is a mechanism stress slice, not an estimate of natural workload frequencies. It intentionally contains both rank-boundary authority cases and already-sufficient contexts with plausible distractors so that a larger evidence prefix has both opportunity and risk.

## Frozen arms

### Arm A5 — current simple comparator

1. exact user question;
2. same E023 whole-object BM25 implementation;
3. select exact ranked top **5** anchors;
4. unchanged G1d/G1c composer over full selected evidence.

### Arm B6 — one-object evidence-budget increment

1. exact user question;
2. the **same exact BM25 ranking** as A5;
3. select exact ranked top **6** anchors;
4. the **same composer** as A5 over full selected evidence.

There is:

- no planner;
- no query rewrite;
- no RRF;
- no selector model;
- no authority-aware runtime rule;
- no evaluator-clause access during retrieval or composition.

The only causal difference is the fifth versus sixth ranked evidence object.

## Phase 0 — zero-model authority gate

Before any semantic execution, deterministically compute A5 and B6 contexts and score them with the already-frozen evaluation-only authority contract.

Semantic execution may be considered only if B6 satisfies **all**:

1. **0 `INSUFFICIENT_AUTHORITY`** contexts;
2. authority-status improvements versus A5 on at least **2 / 8** questions;
3. authority-status regressions versus A5 on **0 / 8** questions;
4. all anchor/question/contract separation and terminal-authority checks pass;
5. no model answer or semantic verdict exists anywhere in the v2 prospective package.

If Phase 0 fails, G1e stops with **0 semantic calls**. Do not weaken the rule.

Phase 0 is an authorization gate for a later semantic comparison, not final product promotion.

## Evidence-size measurement

For each question record, without using it to choose anchors:

- selected source count;
- total selected raw evidence text characters;
- B6/A5 raw evidence character ratio;
- identity of the newly included rank-6 anchor.

No evidence-character threshold is a promotion requirement in v0 because the repository has no pre-existing global multi-source character budget to inherit honestly.

## Phase 1 — semantic safety/value, only after a separate execution contract

If Phase 0 is frozen and passed, a separate execution-addendum PR may authorize:

- exact model `gpt-5.6-luna`;
- A5 composer: **8** calls;
- B6 composer: **8** calls;
- total semantic attempts: **16**;
- rerolls: **0**;
- planner calls: **0**;
- selector calls: **0**.

Use the same authority-preserving composer instructions for both arms. Only the selected context differs.

## Frozen final promotion rule

G1e evidence-budget promotion is **EARNED** only if Phase 0 passed and the later frozen semantic adjudication also satisfies all:

1. B6 semantic verdicts contain at least **7 / 8 PASS**;
2. B6 produces at least **1 semantic improvement** versus A5;
3. B6 produces **0 semantic regressions** versus A5;
4. B6 produces **0 new CRITICAL_ERROR** versus A5;
5. no B6 answer makes a load-bearing unsupported claim when its context is authority-incomplete;
6. exact 16-call Luna execution completes with zero rerolls.

Do not weaken these thresholds after execution.

Even an EARNED result would establish only a query-time evidence-budget mechanism signal. It would **not** make six sources a product default. Product translation would still need an explicit evidence-size/cost policy and natural dogfood evidence.

## Overfitting / freeze boundary

The A5→A6 hypothesis comes from already-frozen E023 evidence, so the old AQxxx/BQxxx slices are no longer valid promotion material.

For v2:

- all Cxxx anchors/questions/authority clauses are frozen before semantic execution;
- do not edit them to improve A5 or B6 after the zero-model gate is recorded;
- do not add Cxxx-specific rules to retrieval or composition;
- do not semantically rerun AQxxx/BQxxx;
- any material correction after semantic execution requires a new experiment identity.

## Product/architecture boundary

G1e remains inside G1 Retrieval / Composition.

It does **not** authorize:

- G2 persistence;
- graph/entity/KnowledgeUnit storage;
- automatic identity merge/split or routing;
- vector retrieval defaults;
- evaluator clauses as runtime canonical structure;
- a hard-coded top-6 product policy;
- Dogfood runtime changes.
