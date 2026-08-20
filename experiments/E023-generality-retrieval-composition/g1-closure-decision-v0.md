# E023 G1 closure decision v0

Status: **G1 QUERY-TIME BASELINE EARNED FOR G2 RESEARCH COMPARATOR / NOT A PRODUCT POLICY / ZERO-MODEL ARCHITECTURE DECISION**  
Tracking: Issue #160  
Evidence through: G1f result PR #195 / run `32349241403`

## Decision

E023 closes the exploratory **G1 Retrieval / Composition mechanism-search loop** at this checkpoint.

The research comparator carried forward into any G2 persistence experiment is:

> **exact whole-object BM25 top-6 + the frozen old composer from `run_g1c.py`**

This is a controlled-experiment baseline only. It is **not** a Dogfood runtime change and **not** a product default for `k=6`.

`composition_prompt_v1` is not promoted. G1f found no paired semantic improvement over the old composer, so using it as the G2 comparator would silently promote a mechanism that missed its frozen gate.

## Why G1 is strong enough for a G2 comparator

This is an architecture synthesis of already-frozen evidence, not a new semantic experiment and not a claim that every G1 strict promotion was earned.

### Complexity did not earn itself

- G1a blind planner + RRF did not improve the exact-BM25 baseline.
- G1b evidence-follow produced a targeted identity repair but missed its broad gate.
- G1c-R1 found sufficient candidate authority, then a model selector dropped load-bearing evidence.
- G1d deterministic RRF top-4 did not generalize and produced worse authority sufficiency than the simple arm.

Therefore G2 should not carry planner/selector/RRF complexity forward merely because it exists.

### The simple evidence-budget path strengthened prospectively

G1e used new separated material and showed exact BM25 top-6 versus top-5:

- removed both authority-incomplete contexts;
- produced 2 authority improvements and 0 regressions;
- produced 2 semantic improvements, 0 semantic regressions, and 0 new critical errors;
- required 0 planner and 0 selector calls.

G1e strict promotion remained NOT_EARNED at 6/8 PASS, so top-6 is not product policy.

### Composition safety replicated on another separated slice

G1f held the exact question and exact top-6 context byte-identical between composers on new DQ material.

Both the old composer and `composition_prompt_v1` produced:

- **7 PASS / 1 PARTIAL / 0 CRITICAL_ERROR**;
- safe insufficiency on the deliberately authority-incomplete DQ003 negative control;
- correct proposition-scoped sufficiency on DQ004;
- preserved user-owned decision authority on DQ001 and DQ007;
- no synthesized identity bridge.

The new composer produced **0 paired improvements**, so its candidate promotion is NOT_EARNED. But the old/simple path itself replicated a high-safety profile without adding semantic retrieval machinery.

## Meaning of “earned”

The earned statement is deliberately narrow:

> **G1 now has a sufficiently strong, simple, frozen query-time path to serve as the control/comparator for a persistence-value experiment.**

It does **not** mean:

- exact BM25 top-6 is a product default;
- the old composer is a universal production composer;
- G1 has zero remaining errors;
- persistent semantic state has earned itself;
- graph/entity/KU storage has earned itself;
- automatic identity routing has earned itself.

A new naturally observed query-time critical failure can reopen G1.

## G2 research gate now allowed

This decision authorizes **G2 preregistration/design work only**.

The next research question is:

> **Holding authority, identity scope, retrieval, and composition fixed, does a rebuildable persistent semantic projection improve repeated-use answer quality/cost/latency enough to justify lifecycle and stale-state risk over query-time synthesis alone?**

The first G2 comparison should use **fixed, prospectively supplied identities/subjects**. It must not test automatic subject discovery, entity resolution, merge/split, or routing; those remain G3.

### Frozen G2 design constraints

A G2 preregistration should require:

1. a new separated repeated-use/update corpus;
2. the G1 control arm fixed to exact BM25 top-6 + frozen old composer;
3. the persistence arm to add only a rebuildable `DERIVED_MEMORY`-like semantic projection whose load-bearing claims resolve to terminal `RAW_MEMORY` or `HUMAN_KNOWLEDGE`;
4. no graph database or universal Entity/Relation/KnowledgeUnit schema;
5. fixed identity/subject assignment supplied prospectively rather than inferred automatically;
6. lifecycle cases including source addition, correction/supersession, and a stale-view hazard;
7. explicit measurement of answer semantics, critical unsupported/stale claims, model calls, evidence bytes/tokens where observable, rebuild/maintenance calls, and human-intervention burden;
8. at least one negative control where persistence would be harmful if stale authority were trusted;
9. zero semantic calls in the preregistration PR;
10. a separate execution contract merged before any paid/semantic execution.

A persistence arm that improves latency/call count but introduces a stale load-bearing claim must fail.

## Product track remains separate

Dogfood 0.1.16 remains the product baseline.

Issue #141 natural installed dogfood continues to answer product questions controlled experiments cannot:

- whether ambient memory recall is useful days/weeks later;
- whether setup/notification friction returns;
- whether hidden Luna usage becomes a repeated user problem;
- whether dedicated navigation/history UI is actually missed.

Do not manufacture workload or UI demand.

Issue #132 reliability follow-ups remain evidence-gated. Do not introduce DB/WAL architecture preemptively just to solve hypothetical crash windows.

## What not to do next

- no AQ/BQ/CQ/DQ semantic reruns;
- no further prompt tuning on DQ material;
- no new planner/selector/RRF tuning without a new failure signal;
- no product top-6 default;
- no persistent semantic implementation before G2 preregistration;
- no graph/entity/KU schema;
- no vector default;
- no automatic identity merge/split/routing;
- no broad background semantic watcher;
- no product UI expansion without natural evidence.

## Next core

Create a **fresh G2 fixed-identity persistence preregistration** from the merge of this closure decision.

The preregistration must be zero-model first and must not authorize semantic execution on the same PR.
