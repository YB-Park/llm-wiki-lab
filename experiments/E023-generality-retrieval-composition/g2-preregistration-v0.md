# E023 G2 — fixed-identity persistence-value preregistration v0

Status: **PREREGISTRATION / ZERO-MODEL FIRST / NO SEMANTIC EXECUTION AUTHORIZED BY THIS FILE**  
Tracking: Issue #160  
G1 closure base: `f7be9e810a0105a9cdfa1b50bc8d2b8e24c60a9b`

## Research question

G1 is now closed as an exploratory mechanism-search loop with one deliberately narrow earned statement:

> **exact whole-object BM25 top-6 + the frozen old `run_g1c.py` composer is strong enough to serve as the controlled query-time comparator for G2 research.**

That is not a product top-6 policy.

G2 asks:

> **With subject identity, terminal authority, answer composer, and the strong query-time baseline held fixed, does a rebuildable persistent semantic retrieval projection improve repeated-use semantic quality and evidence efficiency enough to justify maintenance and stale-state risk?**

This is a persistence-value experiment, not an entity-system experiment.

## New separated material

Directory: `persistence-comparison-v0/`

Prospective package:

- **36 new terminal anchors**;
- **12 paired query events**;
- **3 fixed subjects**: `iris`, `juniper`, `keystone`;
- 32 `RAW_MEMORY` anchors;
- 4 `HUMAN_KNOWLEDGE` anchors;
- no AQ/BQ/CQ/DQ IDs or reused anchor text;
- no model projection;
- no model answer;
- no semantic adjudication.

The material is a repeated-use/lifecycle mechanism stress slice, not an estimate of natural workload frequencies.

Fixed subject scope is supplied prospectively to **both** arms. No model discovers, merges, splits, or routes subject identity.

## Frozen lifecycle

### Iris — stable reuse

Iris has one S0 authority snapshot and four query events. Its persisted projection is built once and then reused without maintenance.

This tests whether a subject projection can provide repeated-use value without being rebuilt for every question.

### Juniper — new authority addition

Juniper starts at S0 and a projection is built.

After PQ005/PQ006, S1 adds four new admitted authority objects including P021, a second independent month-close observation.

PQ007 runs **after the authority mutation but before projection rebuild**. The persisted projection is therefore stale by construction and must be deterministically bypassed.

The projection is then rebuilt from the complete S1 terminal authority before PQ008.

P021 is prospectively frozen outside the Q exact-BM25 top-6 at **rank 8** for PQ007/PQ008. PQ008 is therefore one persistence retrieval-opportunity case after rebuild.

### Keystone — correction/supersession stale hazard

Keystone starts with a current 30-day retention policy/decision and an S0 projection.

S1 adds:

- P033 — customer policy addendum making 90 days current and the old policy historical;
- P034 — user-owned superseding project decision changing 30 -> 90 days;
- P035/P036 implementation/correction evidence.

PQ011 runs after S1 arrives but before projection rebuild.

A stale S0 projection could incorrectly preserve the old 30-day state as current. PQ011 is the **primary stale-projection negative control**.

The P arm must detect source-snapshot mismatch, bypass the stale projection, and use the exact Q control retrieval. It must not consult stale projection text for selection or answering.

After rebuild, PQ012 tests the corrected current state.

## Arm Q — frozen G1 query-time comparator

For each query:

1. use the prospectively supplied fixed subject;
2. select the current active terminal authority snapshot for that subject/state;
3. run the existing exact whole-object BM25 implementation;
4. select exact top **6** terminal authority objects;
5. answer with the frozen old `run_g1c.py::composer_prompt` with Pxxx handle wording only;
6. no planner, selector, RRF, vector retrieval, persistent state, or evaluator access.

Q is the control, not a product default.

## Arm P — rebuildable persistent semantic retrieval projection

P uses the same fixed subject, same current terminal authority, same final old composer, and same maximum six terminal anchors.

The only added mechanism is a persisted **DERIVED / NONCANONICAL retrieval projection**.

### Projection build/rebuild

At each frozen build/rebuild event:

1. compute a deterministic SHA-256 over the full current terminal-authority snapshot for that fixed subject;
2. make one model call using frozen `projection_prompt_v0.py`;
3. the compiler sees the fixed subject ID plus **all current terminal authority objects for that subject**;
4. the compiler sees **no user query**, no future question, no evaluator clause, no expected answer, and no promotion threshold;
5. store the parsed projection with the source-snapshot SHA.

The projection contains retrieval entries only:

```json
{
  "entries": [
    {
      "entry_id": "E01",
      "statement": "...",
      "anchor_ids": ["P001", "P002"]
    }
  ]
}
```

It is not terminal authority. Its text is never a valid final citation.

Every supplied terminal anchor must be referenced by at least one projection entry so the compiler cannot silently specialize the projection to an unknown future query.

### Freshness guard

Before every P query:

- recompute the current subject-authority snapshot SHA;
- compare it to the stored projection snapshot SHA.

If they differ:

> **STALE_PROJECTION_BYPASS**

The projection must not be used at all. P must select the exact same top-6 terminal anchors as Q for that query.

No query-time model call is allowed to repair or refresh a stale projection. Rebuild happens only at the prospectively frozen lifecycle event.

### Fresh projection retrieval

If the snapshot matches:

1. run deterministic BM25 over projection `statement` text using the user question;
2. take the top **2** positive-scoring projection entries;
3. collect their terminal `anchor_ids` in projection-entry order, de-duplicated;
4. if fewer than **4** terminal anchors were selected, fill from the same exact raw-authority BM25 ranking until four are present;
5. cap final selected terminal authority at **6**;
6. if no projection entry has a positive score, fall back exactly to Q top-6;
7. render only the selected **terminal authority objects** to the frozen old composer.

Projection statements themselves never enter the final composer context.

This preserves the authoritative-anchor invariant while allowing persistent semantic state to affect retrieval/navigation only.

## Prospective zero-model Q frontier

The prereg validator freezes the Q control contexts before any projection exists.

Expected control status:

| status | count |
| --- | ---: |
| `SUFFICIENT_CLEAN` | 3 |
| `SUFFICIENT_WITH_CONFLATION_RISK` | 6 |
| `INSUFFICIENT_AUTHORITY` | 3 |

The three Q incomplete contexts are frozen:

- **PQ004** — P004 broader portfolio evidence is exact rank **12** and outside top-6;
- **PQ007** — P021 second month-close observation is exact rank **8**; this query is also a stale-gap event, so P must bypass and cannot improve it;
- **PQ008** — P021 remains exact rank **8**, but the projection has been rebuilt and gets a fair opportunity to recover it.

The two prospectively designated **fresh persistence opportunities** are therefore PQ004 and PQ008.

Full current terminal authority is sufficient for all 12 questions. These are retrieval-context misses, not absent-world-authority cases.

## Planned semantic call budget — frozen now, not authorized now

A later separate execution contract may authorize exactly:

- Q composer: **12** calls;
- P composer: **12** calls;
- P projection build/rebuild: **5** calls;
- total semantic attempts: **29**;
- planner: **0**;
- selector: **0**;
- vector: **0**;
- rerolls: **0**;
- candidate exact model: `gpt-5.6-luna`.

The five projection calls are:

- Iris S0 initial build;
- Juniper S0 initial build;
- Juniper S1 rebuild;
- Keystone S0 initial build;
- Keystone S1 rebuild.

No projection compiler call occurs inside a query event.

This PR authorizes **0 semantic calls**.

## Frozen evaluation dimensions

Keep separate:

- Q/P selected-context authority sufficiency;
- semantic PASS/PARTIAL/FAIL_RETRIEVAL/CRITICAL_ERROR;
- stale-projection guard behavior;
- stale or unsupported load-bearing claims;
- terminal citation validity;
- user-owned authority preservation;
- correction/supersession semantics;
- selected terminal evidence characters;
- projection build/rebuild model calls;
- answer model calls;
- manual repair/human-intervention events.

The experiment does not claim model-call savings by construction: P spends five maintenance calls. Persistence must earn that overhead through semantic improvements and evidence-context efficiency without stale-state regressions.

## Frozen promotion rule

`G2_PERSISTENCE_CANDIDATE_EARNED` requires **all**:

1. exact 29 semantic attempts on one exact frozen model with zero rerolls;
2. fresh P selected contexts improve authority status versus Q on **both PQ004 and PQ008**;
3. fresh P selected contexts cause **0 authority-status regressions** on every other fresh-projection query;
4. PQ007 and PQ011 stale guards bypass projection and reproduce the exact Q selected terminal anchors;
5. PQ011 primary stale negative control produces **no stale/current inversion and no CRITICAL_ERROR**;
6. PQ012 post-rebuild correction/supersession verdict is **PASS**;
7. P semantic verdicts contain at least **10 / 12 PASS**;
8. P produces at least **2 paired semantic improvements** versus Q;
9. P produces **0 paired semantic regressions** versus Q;
10. P produces **0 new CRITICAL_ERROR** versus Q;
11. P produces **0 stale or unsupported load-bearing claims**;
12. every P load-bearing citation terminates in supplied terminal authority;
13. across the **10 fresh-projection queries** (excluding stale-gap PQ007/PQ011), total P selected raw terminal-evidence characters are at most **85%** of Q on the same queries;
14. projection build/rebuild calls are exactly **5**, with no query-time compiler call.

Do not weaken any threshold after model projection or answer outputs exist.

Even an earned result would be a **G2 research signal only**. It would not make persistence a Dogfood default and would not authorize G3.

## Runtime/evaluator separation

Projection compiler and final composer must not receive:

- evaluation clauses;
- expected Q/P statuses;
- expected answers;
- semantic verdicts;
- opportunity IDs;
- stale-negative-control labels;
- promotion thresholds;
- future questions.

Final composer receives terminal authority only.

## Product / architecture boundary

This preregistration does **not** authorize:

- G2 semantic execution on this PR;
- persistent semantic state in Dogfood runtime;
- graph database;
- universal Entity/Relation/KnowledgeUnit schema;
- automatic identity discovery/merge/split/routing;
- vector retrieval default;
- product top-6 default;
- evaluator clauses as runtime canonical structure;
- background semantic watching.

Dogfood 0.1.16 natural installed evidence continues independently on Issue #141.

## Next step

If this preregistration merges with all zero-model checks green, create a **fresh G2 execution-contract branch from that merge SHA**.

Only that later contract may freeze/authorize the exact 29-call run.
