# Generality and semantic projections — working design gate

Status: **WORKING DESIGN GATE / G1 QUERY-TIME COMPARATOR RETAINED / G2 PERSISTENCE NOT EARNED AND PARKED / G3 NOT OPENED / NOT AN ADR**  
Date: 2026-08-20 KST  
Tracking: Issue #160  
Experiment: E023

## Design target

LLM Wiki must be general at the capability/query boundary without prematurely forcing all knowledge into a universal storage ontology.

> **Capability generality before storage uniformity.**

Current working thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Query-time reconstruction is the default architecture posture; persistent semantic state must earn itself separately and has not yet done so.**

## Authority Core and projection boundary

The durable Authority Core remains ontology-agnostic. It owns admitted evidence identity/integrity/provenance, current/history and explicit correction/change/dispute semantics, Human Knowledge authorship, privacy/permission boundaries, and deterministic repairable storage invariants.

Semantic projections may be source notes, ephemeral cross-source dossiers, timelines, project summaries, or later persistent views only if a specific projection earns value.

Common projection properties remain:

- DERIVED;
- NONCANONICAL;
- terminal-authority resolvable;
- inspectable;
- reversible/rebuildable;
- unable to impersonate RAW evidence or Human Knowledge.

## Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. Persistence never makes DERIVED state terminal authority.

## Ordered architecture gates — current state

1. **G1 Retrieval / Composition — exploratory mechanism search closed.**
2. **G2 Persistence — first fixed-identity candidate NOT_EARNED; parked.**
3. **G3 Identity / Routing — not opened.**

A G2 failure is not evidence for G3.

## G1 findings retained

### Truth-by-luck is a trust failure

Correct-looking identity/compliance/recurrence conclusions are unsafe when the supplied authority lacks the required bridge or independent support.

Similarity and strong identifiers are evidence, not automatic truth.

### Planner/selector complexity did not earn itself

Blind planning, free-form final selection, and deterministic RRF repeatedly failed to preserve governing/load-bearing authority.

G1 therefore closed with a narrow research comparator:

> **exact whole-object BM25 top-6 + frozen old `run_g1c.py` composer**

No planner, selector, or RRF.

This is not a product runtime prescription.

### Composition candidate did not add incremental value

G1f on new separated material produced 7 PASS / 1 PARTIAL / 0 critical in both the old composer and `composition_prompt_v1` arms, with zero paired improvement.

`composition_prompt_v1` is therefore NOT_EARNED and the DQ slice is frozen against tuning.

## G2 result — persistence value not earned

G2 used new separated fixed-subject lifecycle material and held final composition constant.

- Q = current terminal authority -> exact BM25 top-6 -> frozen composer.
- P = query-blind persisted DERIVED retrieval projection -> deterministic terminal-anchor selection -> same composer.
- projection text never entered final composer context.
- stale projection snapshot mismatch required exact Q bypass.

Run `32353304896`, exact `gpt-5.6-luna`, 29/29 attempts, zero rerolls.

Semantic result:

| arm | PASS | FAIL_RETRIEVAL | CRITICAL_ERROR |
| --- | ---: | ---: | ---: |
| Q | 9 | 1 | 2 |
| P | 8 | 1 | 3 |

P paired improvements: 2.  
P paired regressions: 3.  
P new critical errors: 3.

Fresh selected terminal evidence chars fell from 10,282 Q to 7,019 P (**68.3%**), but semantic safety requirements failed.

> **`G2_PERSISTENCE_CANDIDATE_EARNED` = NOT_EARNED.**

## What G2 taught us

### Snapshot-bound fail-closed derived state is valuable

PQ007/PQ011 correctly detected stale projection snapshots and reproduced exact current-authority Q contexts.

PQ011 avoided the prospectively frozen 30 -> 90-day stale/current inversion.

Reusable safety principle:

> **If future persisted/rebuildable derived state exists, bind it to a deterministic terminal-authority snapshot and bypass it when stale.**

This safety rule is independent of whether persistent semantic state ultimately earns value.

### Persistence can improve context efficiency and occasional retrieval

PQ004 recovered one prospectively missing authority anchor and P used substantially fewer terminal evidence characters overall.

These are real positive mechanism signals.

### But persistence reintroduced destructive selection risk

Every model-built projection referenced every terminal anchor, so the compiler did not globally lose evidence.

The later query-time projection retrieval still discarded load-bearing authority:

- PQ008 failed to select required P021 despite its presence in the rebuilt projection;
- PQ009 omitted governing P026 and regressed critically;
- PQ012 omitted user-owned superseding P034 and regressed critically.

The architecture lesson is broader than one top-k value:

> **Global semantic preservation does not guarantee local trustworthy selection.**

A persistent layer can move the same selection problem seen in G1 into a new representation while adding maintenance and stale-state obligations.

## Why G3 remains closed

G3 would test automatic discovery/routing/merge-split of persistent semantic targets.

The first G2 test did not establish that persistent semantic targets themselves provide net value. Therefore there is no evidence basis for automatic identity infrastructure.

Do not introduce:

- graph DB / universal Entity/Relation/KnowledgeUnit schema;
- automatic identity merge/split/routing;
- vector defaults justified by G2;
- persistent dossiers as a product default;
- background semantic maintenance.

## Reopen rule for persistence

G2 remains parked unless independent evidence makes persistent derived state materially relevant.

Suitable reopen signals include repeated natural installed use showing that query-time semantic reconstruction is too slow, costly, or unreliable, or repeated demand for a durable derived view that current raw/query-time behavior cannot serve.

A future G2 experiment must use new separated material and fresh preregistration. Do not tune or rerun PQ material semantically.

## Product evidence now leads

Dogfood 0.1.16 remains unchanged. Issue #141 natural installed use is the primary project-evidence track.

Controlled E023 results cannot establish:

- ambient Agent tool routing;
- long-horizon memory usefulness;
- real interaction/popup friction;
- whether hidden Luna usage is repeatedly confusing;
- whether dedicated navigation/history UI is actually wanted.

Let repeated installed friction choose the next product slice.

If hidden maintenance spend becomes repeated friction, preserve the distinction between local model-call count, token usage, and actual AI-credit/premium-request usage; do not infer one from another.

Issue #132 reliability edges remain evidence-gated. Do not adopt database/WAL architecture preemptively.

## Current action

- paid E023 semantic calls pause;
- G2 persistence remains parked;
- G3 remains closed;
- continue natural installed Dogfood evidence on #141;
- reopen architecture only from independent evidence, not because more mechanisms are available.
