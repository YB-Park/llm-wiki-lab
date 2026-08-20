# E023 — Generality Retrieval / Composition Gate

Status: **G1 QUERY-TIME BASELINE EARNED FOR G2 RESEARCH COMPARATOR / INDIVIDUAL G1 PROMOTIONS REMAIN AS FROZEN / G2 PREREG NEXT**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy cross-source semantic knowledge at query time before persistent semantic state, and—only after that path is strong—does persistence add enough repeated-use value to justify lifecycle risk?

E023 deliberately orders the work:

1. G1 retrieval/composition;
2. G2 persistence;
3. G3 identity/routing.

It is not a universal entity-system experiment.

## Guardrails

- Authority Core remains ontology-agnostic.
- `source-note-v0` is one DERIVED projection, not the Wiki ontology.
- Every load-bearing derived statement must resolve to admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`.
- Evaluator clauses remain evaluation-only.
- Exact BM25 top-6 is an experimental baseline, not product policy.
- G2 does not authorize G3.

## G1 sequence

### G1a / G1b

Blind planning did not beat the simple baseline. Evidence-follow produced one targeted repair but missed its broad gate.

Key lesson:

> **Truth-by-luck is not trustworthy semantic recovery.**

### G1c-R1

A model selector received authority-sufficient candidate pools on 6/6 but dropped load-bearing evidence. NOT_EARNED.

### G1d

Planner + deterministic RRF top-4 did not generalize; the simple exact-BM25 arm was stronger. NOT_EARNED.

A zero-model frontier then found consequential authority at exact rank 6.

### G1e — simple evidence-budget replication

New separated 35-anchor / 8-question slice.

Exact top-6 versus top-5:

- authority improvements 2, regressions 0;
- top-6 authority incomplete contexts 0;
- semantic improvements 2, regressions 0, new criticals 0;
- planner/selector calls 0.

Strict top-6 gate was still NOT_EARNED because B6 reached 6/8 PASS against a frozen >=7/8 threshold.

Nevertheless, exact BM25 + modestly larger evidence prefix became the strongest simple retrieval baseline.

### Composition contract v0

PR #191 froze a generic zero-model contract for:

- user-owned authority;
- direct vs attributed evidence;
- missing bridges;
- proposition-scoped insufficiency;
- negative characterization;
- temporal/correction state;
- terminal citations;
- conflation-risk restraint.

`composition_prompt_v1` was a prospective candidate, not a promoted composer.

### G1f — paired composition comparison

PR #193 preregistered new separated DQ material. PR #194 froze a one-shot execution. Run `32349241403`; result PR #195.

Both arms used exact `gpt-5.6-luna` and the exact same frozen top-6 context per question.

| arm | PASS | PARTIAL | CRITICAL |
| --- | ---: | ---: | ---: |
| O — frozen old composer | **7** | **1** | **0** |
| N — `composition_prompt_v1` | **7** | **1** | **0** |

N improvements: **0**. Regressions: **0**. New criticals: **0**.

Both arms passed:

- DQ003 deliberately authority-incomplete identity negative control;
- DQ004 proposition-scoped `could satisfy` case;
- DQ001/DQ007 user-owned decision cases;
- direct-vs-attributed, temporal/correction, repeated-support, and project-identity cases.

Both were PARTIAL only on DQ006 because neither used prospectively required D033 broader-serverless corroboration.

Frozen N promotion required >=1 paired improvement:

> **`composition_prompt_v1` candidate promotion is NOT_EARNED.**

Do not tune/rerun the DQ slice.

## G1 closure

The experiment family now distinguishes **mechanism promotion** from **baseline adequacy**.

Several individual mechanisms missed strict gates. But accumulated separated evidence supports this narrower architecture conclusion:

> **The simple query-time path is sufficiently strong and stable to serve as the fixed control for a G2 persistence-value experiment.**

Frozen G2 control:

- exact whole-object BM25 top-6;
- frozen old `run_g1c.py` composer;
- no planner, selector, or RRF.

This does not turn those choices into product defaults.

## Next: G2 fixed-identity persistence preregistration

G2 asks whether a rebuildable persistent semantic projection earns itself over the fixed G1 control under repeated use and lifecycle change.

First G2 design must:

- use new separated repeated-use/update material;
- supply subject identity prospectively;
- forbid automatic identity discovery/routing;
- include addition, correction/supersession, and stale-state hazards;
- keep persistent claims anchored to terminal authority;
- measure answer semantics, critical stale/unsupported claims, calls/cost, maintenance/rebuild work, and human intervention;
- include a stale-view negative control;
- keep prereg semantic calls at zero;
- require a separate execution contract.

No graph DB, universal Entity/Relation/KnowledgeUnit schema, vector default, or product runtime change is authorized.

## Product relationship

Dogfood 0.1.16 remains unchanged.

Natural installed use on Issue #141 remains the source for product-value evidence such as ambient recall, long-horizon usefulness, setup/notification friction, hidden usage visibility, and whether users actually miss dedicated navigation.

Issue #132 reliability work remains evidence-gated rather than a pretext for premature database/WAL architecture.
