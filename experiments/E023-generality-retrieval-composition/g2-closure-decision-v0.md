# E023 G2 closure decision v0

Status: **ZERO-MODEL ARCHITECTURE CHECKPOINT / G2 PERSISTENCE NOT EARNED / G3 NOT OPENED**  
Date: 2026-08-20 KST  
Tracking: Issue #160  
Result: PR #199 / run `32353304896`

## Decision

The first fixed-identity persistence-value candidate is **NOT_EARNED** and G2 is parked at this checkpoint.

Do not start G3 identity/routing.

Do not translate the G2 candidate into Dogfood persistent semantic state.

Do not tune projection top-k or rerun PQ material semantically.

The current architecture remains:

> **Stable Authority Core + strong query-time retrieval/composition + optional rebuildable derived projections only when a specific projection earns value.**

The accumulated evidence does not justify a universal persistent semantic layer.

## Evidence entering closure

G1 closed with a deliberately narrow research comparator:

- exact whole-object BM25 top-6;
- frozen old `run_g1c.py` composer;
- no planner / selector / RRF.

That comparator is research-only, not product top-6 policy.

G2 then froze fixed subject identity and compared:

- Q: current terminal authority -> exact BM25 top-6 -> frozen composer;
- P: query-blind persisted DERIVED projection -> deterministic terminal-anchor selection -> same composer;
- projection text never final answer context or terminal authority;
- stale snapshot mismatch -> exact Q bypass.

Frozen execution completed with 29/29 exact Luna attempts and zero rerolls.

## What G2 earned

### 1. Snapshot freshness guard is credible

PQ007 and PQ011 both detected stale projection snapshots and reproduced the exact Q selected terminal anchors/context.

PQ011, the primary correction/supersession stale negative control, preserved the new 90-day policy and superseding project decision without reviving the old 30-day state.

This earns a reusable engineering principle:

> **Any future persisted/rebuildable derived projection should be bound to a deterministic source-authority snapshot and fail closed to current authority when stale.**

This is a safety mechanism signal, not evidence that semantic persistence itself should exist.

### 2. Persistent projection can reduce answer-context size

Across ten fresh queries:

- P terminal evidence chars: 7,019;
- Q terminal evidence chars: 10,282;
- P/Q: 68.3%.

The frozen <=85% efficiency criterion passed.

### 3. One prospective retrieval miss was repaired

PQ004 recovered P004 broader portfolio evidence and moved Q `CRITICAL_ERROR` to P `PASS`.

This proves a persistent semantic retrieval view can sometimes expose authority that lexical whole-object retrieval misses.

## Why G2 is still not earned

The projection compiler itself preserved all terminal anchors, but the later projection-retrieval stage discarded load-bearing authority.

- PQ008: required second close observation P021 existed in the rebuilt projection but was not selected; the prospective authority opportunity failed.
- PQ009: governing policy P026 existed in projection entry E02 but ranked third; frozen top-2 retrieval omitted it and P regressed to `CRITICAL_ERROR`.
- PQ012: user-owned superseding decision P034 existed in projection entry E08 but ranked third; frozen top-2 retrieval omitted it and P regressed to `CRITICAL_ERROR`.

P semantic result:

- 8 PASS;
- 1 FAIL_RETRIEVAL;
- 3 CRITICAL_ERROR;
- paired improvements 2;
- paired regressions 3;
- new critical errors 3.

The candidate therefore fails multiple independent frozen requirements.

PQ007 additionally showed model-call variance on an identical stale-bypass prompt: Q safely returned `FAIL_RETRIEVAL`, while the separate P call asserted unsupported repetition. This is not causally attributable to persistence selection, but the frozen paired gate correctly does not erase the observed regression after the fact.

## Architecture interpretation

G2 reproduces a broader E023 lesson:

> **Preserving authority in a global representation is not enough. Any later selection bottleneck can discard the authority that makes an answer trustworthy.**

G1c showed this with a model selector over candidate evidence. G2 shows the same shape with deterministic lexical retrieval over persistent projection statements.

Persistence therefore does not solve semantic selection by itself; it can move the selection problem into another layer while adding build/rebuild and stale-state obligations.

The positive context-efficiency result is not sufficient to justify that new failure surface.

## What is parked

Until independent evidence reopens the question, do not start:

- another paid G2 persistence run;
- same-slice PQ top-k tuning;
- persistent dossier/entity/project pages as a default semantic layer;
- graph DB / universal Entity/Relation/KnowledgeUnit storage;
- automatic identity discovery, merge/split, or routing;
- vector retrieval defaults justified by this G2 result;
- background semantic maintenance;
- product persistence based on E023.

G3 remains **NOT_OPENED** because G2 persistent semantic targets did not earn value.

## Reopen condition

G2 may be reopened only if at least one independent signal makes persistence materially relevant, for example:

1. natural installed dogfood repeatedly shows that query-time reconstruction is too costly, slow, or unreliable for genuinely repeated semantic views;
2. users repeatedly need a durable derived view that cannot be served adequately by current raw/query-time behavior;
3. a new prospective persistence mechanism is justified by evidence independent of the PQ slice.

Any reopened G2 experiment must use new separated material and a fresh preregistration. The PQ slice is diagnostic history, not a tuning set.

## Product priority after closure

Dogfood 0.1.16 natural installed use on Issue #141 returns to the primary product-evidence position.

Observe, without manufacturing demand:

- ambient recall and `wikiRead` follow-through in ordinary Agent conversation;
- useful recovery of decisions/reasoning days or weeks later;
- remaining setup/permission/popup friction;
- whether hidden Luna maintenance usage becomes repeated enough to justify product-owned call/token visibility;
- whether a dedicated navigation/history surface is actually missed.

Do not build usage accounting, Tree View, navigation, or new maintenance machinery merely because it is technically available.

Issue #132 reliability edges remain evidence-gated. Narrowly fix them only if installed use/recovery tests make them material.

## Current research posture

Paid E023 semantic calls pause.

The default next action is **not another research architecture experiment**. It is continued natural product use and evidence collection.

If natural evidence later reopens G2, return here and start from a new separated preregistration rather than modifying frozen G2 outcomes.
