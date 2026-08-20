# E023 — Generality Retrieval / Composition / Persistence Gate

Status: **G1 CLOSED FOR COMPARATOR / G2 FIXED-IDENTITY PERSISTENCE NOT EARNED AND PARKED / G3 NOT OPENED**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy cross-source semantic knowledge at query time before persistent semantic state, and—only after that path is strong—does persistence add enough repeated-use value to justify lifecycle risk?

E023 deliberately ordered:

1. G1 retrieval/composition;
2. G2 persistence;
3. G3 identity/routing.

It is not a universal entity-system experiment.

## Guardrails

- Authority Core remains ontology-agnostic.
- `source-note-v0` is one DERIVED projection, not the Wiki ontology.
- Every load-bearing derived statement must resolve to admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`.
- Evaluator clauses remain evaluation-only.
- Exact BM25 top-6 is a research comparator, not product policy.
- A G2 failure does not justify G3.

## G1 — exploratory mechanism search closed

Planner/selector/RRF complexity repeatedly failed to beat the simple path safely.

G1e established the strongest simple evidence-budget signal: exact BM25 top-6 removed two authority misses with zero semantic regressions, though its strict individual promotion threshold remained NOT_EARNED.

G1f then compared the frozen old composer to `composition_prompt_v1` on new separated material with byte-identical top-6 contexts:

| arm | PASS | PARTIAL | CRITICAL |
| --- | ---: | ---: | ---: |
| old composer | 7 | 1 | 0 |
| `composition_prompt_v1` | 7 | 1 | 0 |

The new prompt produced zero paired improvements, so it was NOT_EARNED.

G1 closure therefore carried forward only this narrow **research comparator**:

- exact whole-object BM25 top-6;
- frozen old `run_g1c.py` composer;
- planner / selector / RRF = 0.

This is not product default policy.

## G2 — first fixed-identity persistence candidate

PR #197 preregistered new separated repeated-use/lifecycle material. PR #198 froze the one-shot execution. Run `32353304896`; result PR #199.

G2 held subject identity and final composer fixed:

- **Q:** current terminal authority -> exact BM25 top-6 -> frozen composer;
- **P:** query-blind persisted DERIVED retrieval projection -> deterministic terminal-anchor selection -> same composer;
- projection text never entered answer context;
- stale snapshot mismatch required exact Q bypass.

Execution:

- exact `gpt-5.6-luna`;
- 29/29 semantic attempts;
- 5 projection build/rebuild calls;
- 12 Q answer calls + 12 P answer calls;
- zero rerolls;
- planner / selector / vector = 0.

### Semantic result

| arm | PASS | FAIL_RETRIEVAL | CRITICAL_ERROR |
| --- | ---: | ---: | ---: |
| Q | 9 | 1 | 2 |
| P | 8 | 1 | 3 |

P improvements vs Q: **2**.  
P regressions vs Q: **3**.  
P new critical errors: **3**.

Frozen promotion required >=10/12 P PASS, >=2 improvements, zero regressions, zero new criticals, both prospective authority opportunities repaired, zero other fresh authority regressions, and safe correction/staleness behavior.

> **`G2_PERSISTENCE_CANDIDATE_EARNED` = NOT_EARNED.**

Do not weaken the frozen rule.

## What G2 did earn

### Snapshot freshness guard

PQ007 and PQ011 detected stale projection snapshots and reproduced the exact Q terminal context.

PQ011—the primary 30 -> 90-day correction stale negative control—avoided stale/current inversion.

Reusable principle:

> **Any future persisted/rebuildable derived state should be bound to a deterministic source-authority snapshot and fail closed to current authority when stale.**

This is a safety mechanism signal, not a persistence-value promotion.

### Context efficiency

Across ten fresh-projection queries:

- Q terminal evidence chars: 10,282;
- P terminal evidence chars: 7,019;
- P/Q = **68.3%**.

The <=85% efficiency gate passed.

### One prospective recovery

PQ004 recovered the prospectively missing P004 broader portfolio evidence and moved Q `CRITICAL_ERROR` to P `PASS`.

## Why persistence remained unearned

The projection compiler preserved every terminal anchor. The later query-time retrieval stage over projection statements discarded load-bearing authority:

- PQ008: required P021 existed in rebuilt projection but was not selected;
- PQ009: governing P026 existed in projection entry rank 3 but top-2 selection omitted it -> P critical regression;
- PQ012: user-owned superseding P034 existed in projection entry rank 3 but top-2 selection omitted it -> P critical regression.

This repeats an E023 invariant:

> **A representation may preserve authority globally while a later selection bottleneck destroys it locally.**

Persistence can move the evidence-selection problem into another layer while adding build/rebuild and stale-state obligations.

PQ007 is a causal nuance: stale bypass gave P and Q identical terminal context/question/prompt. Q safely returned `FAIL_RETRIEVAL`; the independent P model call asserted unsupported repetition. Count the frozen regression, but do not attribute it to persistence selection.

## G2 closure

G2 is **PARKED**. G3 is **NOT_OPENED**.

Do not respond with same-slice projection top-k tuning. The required PQ008 anchor was much deeper in projection ranking, so a trivial top-3 posthoc tweak does not solve the prospective failure set.

Reopen persistence only if independent evidence makes it materially relevant, such as repeated installed use showing query-time reconstruction is too slow/costly/unreliable or users repeatedly need a durable derived view current raw/query-time behavior cannot serve.

Any reopened G2 experiment requires new separated material and fresh preregistration. PQ is diagnostic history, not a tuning set.

## Product relationship — current priority

Dogfood 0.1.16 remains unchanged. Natural installed use on Issue #141 is now the primary project-evidence track.

Observe naturally:

- ambient memory routing in ordinary Agent conversation;
- `wikiRead` provenance follow-through;
- recovery of useful reasoning days/weeks later;
- setup/permission/popup friction;
- whether hidden Luna maintenance usage becomes repeated enough to justify product-owned usage visibility;
- whether a dedicated navigation/history surface is actually missed.

Do not manufacture demand to justify Tree View, usage accounting, or architecture layers.

Issue #132 reliability work remains evidence-gated rather than a pretext for premature database/WAL architecture.

## Current posture

Paid E023 semantic calls pause.

Do not start:

- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns;
- product top-6 policy;
- product persistent semantic dossiers;
- graph/entity/KU storage;
- G3 automatic identity merge/split/routing;
- vector defaults;
- background semantic maintenance.

See:

- `g1-closure-decision-v0.md`
- `g2-results-v0.md`
- `g2-closure-decision-v0.md`
- `docs/14-generality-and-semantic-projections.md`
