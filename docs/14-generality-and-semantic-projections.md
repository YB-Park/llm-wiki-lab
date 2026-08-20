# Generality and semantic projections — working design gate

Status: **WORKING DESIGN GATE / G1 COMPARATOR EARNED / G2 PREREGISTRATION ALLOWED / NOT AN ADR OR PRODUCT STORAGE DECISION**  
Date: 2026-08-20 KST  
Tracking: Issue #160  
Experiment: E023

## Design target

LLM Wiki must be general at the capability/query boundary without prematurely forcing all knowledge into a universal storage ontology.

> **Capability generality before storage uniformity.**

Working thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. The Agent should reconstruct and use the right semantic view at the moment of need; persistence must earn itself separately.**

## Authority Core and projection boundary

The durable Authority Core remains ontology-agnostic. It owns:

- admitted evidence identity/integrity/provenance;
- current/history and explicit correction/change/dispute semantics;
- Human Knowledge authorship;
- privacy/permission boundaries;
- deterministic repairable storage invariants.

Semantic projections may be source notes, ephemeral cross-source dossiers, timelines, project summaries, or later persistent views if persistence earns itself.

Common projection properties:

- DERIVED;
- NONCANONICAL;
- terminal-authority resolvable;
- inspectable;
- reversible/rebuildable;
- unable to impersonate RAW evidence or Human Knowledge.

## Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. Persistence never makes DERIVED state terminal authority.

## Ordered architecture gates

1. **G1 Retrieval / Composition**
2. **G2 Persistence**
3. **G3 Identity / Routing**

G2 must hold a strong G1 path fixed. G3 remains closed until persistent semantic targets themselves earn value.

## G1 findings

### Truth-by-luck is a trust failure

Correct-looking identity or compliance conclusions are unsafe when the supplied authority lacks the required bridge.

Similarity and strong identifiers are evidence, not automatic truth.

### Planner/selector complexity did not earn itself

G1a, G1c-R1, and G1d showed that blind planning, free-form final selection, and deterministic RRF can fail to preserve governing/load-bearing authority.

Do not carry that complexity into later gates without new evidence.

### G1e strengthened a simple retrieval path

Prospective exact BM25 top-6 on separated material removed both top-5 authority misses with zero authority regression and no semantic regression/new critical error.

Strict G1e promotion remained NOT_EARNED at 6/8 PASS.

Therefore top-6 is a strong **research baseline**, not a product source-count policy.

### G1f tested composition with retrieval held identical

Run `32349241403` used paired byte-identical top-6 contexts.

O old composer: **7 PASS / 1 PARTIAL / 0 CRITICAL**.  
N `composition_prompt_v1`: **7 PASS / 1 PARTIAL / 0 CRITICAL**.

The new prompt produced zero paired improvements, so its promotion is NOT_EARNED.

But both arms safely handled the authority-incomplete identity negative control, proposition-scoped sufficiency, and user-owned authority on new separated material.

## G1 closure

The architecture gate now separates two questions:

1. Did every attempted G1 mechanism earn its individual promotion? **No.**
2. Is there now a strong enough simple G1 path to use as a controlled comparator for persistence value? **Yes.**

Frozen G2 research comparator:

> **exact whole-object BM25 top-6 + frozen old `run_g1c.py` composer**

No planner, selector, RRF, vector retrieval, or persistent semantic state is added to the control.

This is not a product runtime prescription.

## G2 — persistence-value gate now open for preregistration only

Immediate research question:

> **With authority, fixed identity scope, retrieval, and composition held constant, does a rebuildable persistent semantic projection improve repeated-use answer quality/cost/latency enough to justify lifecycle and stale-state risk?**

First G2 must use fixed, prospectively supplied subjects. Automatic identity discovery/routing is G3 and remains prohibited.

### G2 must test lifecycle cost, not only happy-path recall

Prospective material should include:

- repeated queries over the same cross-source subject;
- new authority arriving after the projection exists;
- correction/supersession;
- a stale-view hazard that could cause a load-bearing wrong answer;
- rebuild/repair behavior.

Measure separately:

- semantic PASS/critical error;
- unsupported or stale load-bearing claims;
- evidence/authority termination;
- model calls;
- maintenance/rebuild calls;
- latency/cost where observable;
- human intervention required to keep state trustworthy.

A persistent arm that saves calls but trusts stale authority fails.

### Persistence-arm constraints

The first G2 arm may add a simple rebuildable DERIVED projection. It must not require:

- graph database;
- universal Entity/Relation/KnowledgeUnit schema;
- automatic identity resolution;
- merge/split/routing;
- vector default;
- evaluator clauses as runtime canonical structure.

Any later product/storage policy still requires independent evidence and, where appropriate, an ADR.

## Product evidence remains natural

Dogfood 0.1.16 stays unchanged.

Issue #141 natural installed use remains necessary because controlled corpora cannot establish ambient routing value, long-horizon usefulness, interaction friction, hidden model-cost annoyance, or demand for dedicated navigation/history UI.

Issue #132 reliability edges remain evidence-gated. Do not adopt database/WAL architecture preemptively.

## Current action

1. merge/freeze the zero-model G1 closure;
2. create a fresh G2 fixed-identity persistence preregistration;
3. freeze new separated repeated-use/update material and lifecycle negative controls;
4. add zero-model validator/CI;
5. semantic calls remain zero until that preregistration is merged and a separate execution contract is reviewed.

Do not rerun AQ/BQ/CQ/DQ or retune the frozen G1 slices.
