# Generality and semantic projections — working design gate

Status: **WORKING DESIGN GATE / NOT AN ADR / NOT A STORAGE DECISION**  
Date: 2026-08-20 KST  
Tracking: Issue #160  
Experiment: E023

## Design target

LLM Wiki must not accidentally define “Wiki” as developer-shaped source summaries just because that was the smallest useful Agent Wiki slice. But “generality” must also not become an excuse to install a universal Entity/Relation/KnowledgeUnit schema, graph database, vector default, or automatic identity machinery before the workload earns it.

> **Capability generality before storage uniformity.**

Working thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. The Agent should reconstruct and use the right semantic view at the moment of need; every useful view does not need to exist as a permanent node/page/schema.**

## Layer 1 — Authority Core

The durable core remains semantic-ontology agnostic. It owns:

- admitted RAW evidence and immutable identity/integrity;
- provenance and local source navigation;
- current/history and explicit correction/change/dispute semantics;
- Human Knowledge authorship and explicit user epistemic commitments;
- privacy/permission boundaries;
- deterministic repairable storage invariants.

The core should not need to know whether a future semantic view is a person, project, incident, concept, decision, policy, vendor, timeline, or something not yet designed.

## Layer 2 — semantic projections

A semantic projection is a task/retrieval/maintenance aid built from authoritative anchors. It may be ephemeral or persistent **if persistence later earns itself**.

Examples include `source-note-v0`, an ephemeral cross-source dossier, concept synthesis, decision history, timeline, project summary, fixed-target dossier, or retrieval index.

Common safety properties matter more than one common schema:

- DERIVED;
- NONCANONICAL;
- authority-anchor resolvable;
- inspectable;
- reversible/rebuildable;
- unable to silently impersonate RAW evidence or Human Knowledge.

## Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal anchors may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may help retrieval/compilation/navigation, but persistence never makes it terminal authority by itself.

E023 adds an end-to-end refinement:

> **Finding authority is not enough. Retrieval, evidence budgeting/selection, and composition must preserve the authority needed for every load-bearing claim.**

## Persistence remains earned

Persistent semantic state adds refresh, staleness, repair/rebuild, migration, retrieval dominance, maintenance spend, and identity lifecycle obligations.

Use this order:

1. **G1 Retrieval / Composition** — can authority be found, budgeted, preserved, and composed at query time?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval strong/fixed and test repeated-use benefit after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent targets themselves earn value, test subject discovery/alias routing/merge-split automation.

A G1 failure is not evidence for G2. A G2 success is not evidence for G3.

## Semantic identity is an authority problem before it is a storage problem

Identity ambiguity applies to people, projects, products, incidents, policies, decisions, vendors, concepts, and evolving names.

Strong identifiers are identity evidence, not universal identity truth. Name similarity remains a derived hypothesis unless authoritative evidence or a human supplies stronger semantics.

E023 repeatedly demonstrates the rule:

- G1a Q001 omitted an identity bridge and Luna confidently merged aliases anyway;
- G1c-R1 AQ001 recovered the bridge into the candidate pool, then the model selector discarded it and Luna again confidently merged from insufficient authority;
- G1d BQ002 deterministic RRF placed a same-name distractor above the explicit identity bridge and dropped the bridge, but the composer safely expressed uncertainty instead of forcing the merge.

> **Truth-by-luck is not trustworthy semantic recovery.**

None of these cases implies a persistent identity graph is required. They first demand consequence-sensitive authority recovery and composition.

## Query-time synthesis remains the baseline competitor

The baseline competitor for persistent semantic infrastructure is:

> authoritative evidence + sufficiently strong retrieval + explicit evidence budget + authority-preserving composition

If that reliably answers cross-source questions, not persisting a dossier is a positive architecture result.

## E023 evidence sequence

### G1a — blind planning NOT EARNED

Run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero rerolls.

Exact BM25 top-5 and blind planner+RRF both produced **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**. Planner improvements: **0**.

### G1b — evidence-follow NOT EARNED, targeted repair signal

Run `32217824760`, exact Luna, 12 calls, zero rerolls.

Evidence-aware follow-up repaired Q001 by recovering the explicit identity bridge, but broad final-source recovery reached only `1/4` against the preregistered `>=3/4` threshold.

Targeted mechanism signal earned; broad policy not earned.

### Authority-sufficiency evaluator

Flat source completeness was too coarse, so E023 froze an evaluation-only contract that can express unique support, alternatives, repeated support, identity/attribution bridges, negative evidence, temporal correction, Human Knowledge, and forbidden conflation.

It distinguishes `INSUFFICIENT_AUTHORITY`, `SUFFICIENT_CLEAN`, and `SUFFICIENT_WITH_CONFLATION_RISK`.

> **A richer evaluator is not evidence for a richer canonical storage schema.**

### G1c-R1 — free-form final selector NOT EARNED

Run `32232116273`, exact Luna, 18 calls, zero rerolls.

| stage | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| initial top-5 | 4 | 1 | 1 |
| evidence-follow candidates | 4 | 2 | **0** |
| model selector final | 4 | 0 | **2** |

Candidate generation reached positive-authority sufficiency on **6/6**, but the model selector discarded recovered/load-bearing evidence in AQ001 and AQ004. This rejected unconstrained semantic compression as an authority-preserving evidence policy.

### Posthoc RRF top-4 signal — not promotable

On the already-inspected AQ slice, evaluator-blind deterministic RRF top-4 happened to produce **6/6 clean** contexts across a wide RRF-k sweep. Because the mechanism was chosen after seeing failures, it only justified a new prospective test.

### G1d — deterministic RRF top-4 NOT EARNED

G1d prospectively froze a new 23-anchor / 8-question slice and removed the model selector.

Run `32322429563`, source `c74673a83744789f271fa54c43b20212160007a2`, exact Luna, 24/24 calls, zero rerolls.

- A = exact BM25 top-5 -> composer;
- D = same top-5 -> evidence-aware planner -> targeted BM25 -> RRF `k=60` -> top-4 -> composer;
- D selector model calls = 0.

Authority result:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A | 3 | 4 | 1 |
| D | 3 | 3 | 2 |

D authority improvements: **0**; regressions: **1**. Selection promotion: **NOT_EARNED**.

Semantic result:

- A: **7 PASS / 1 CRITICAL_ERROR**;
- D: **5 PASS / 2 PARTIAL / 1 CRITICAL_ERROR**;
- D improvements: **0**;
- D regressions: **2**;
- D new critical errors: **0**.

#### Deterministic does not mean authority-aware

The posthoc RRF signal failed to generalize. RRF repeatedly rewards lexical agreement, including dangerous distractors:

- BQ002: same-name B004 outranks and displaces load-bearing B003 identity authority;
- BQ007: unrelated same-name product B019 survives;
- BQ008: vendor local-admin capability B023 survives despite not being customer authorization policy.

Fixed RRF removes free-form model compression but does not solve semantic discrimination.

#### Planner diagnosis can be right while retrieval remains wrong

BQ006's planner explicitly identifies Cedar's governing EU-only rule as missing. Yet policy anchor B013 ranks exact **6**, first follow-up **4**, and is absent from the second follow-up. The top-3 candidate cutoff therefore excludes it.

Both A and D then produce a definitive compliance-looking conclusion without the governing policy anchor. Both are `CRITICAL_ERROR`.

This extends the truth-by-luck class from identity to policy/compliance.

## Evidence-budget frontier — current strongest zero-model signal

PR #185 analyzes the frozen G1d rankings with **0 model calls**.

Exact BM25:

| budget | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| top-3 | 4 | 0 | 4 |
| top-4 | 2 | 2 | 4 |
| top-5 | 3 | 4 | 1 |
| **top-6** | **4** | **4** | **0** |
| top-7 | 4 | 4 | 0 |
| top-8 | 4 | 4 | 0 |

The sole A@5 positive-authority miss is BQ006; its governing policy B013 is exact rank 6. Therefore exact top-6 contains sufficient positive authority on **8/8** frozen questions.

The four A@5 risk contexts are all frozen semantic PASS, so on this slice perfect distractor elimination was not the critical semantic bottleneck. The critical failure was omission of governing authority.

This result does **not** establish `k=6` as policy. It establishes a stronger design priority:

> **Test evidence budget before adding more retrieval/planning/selector complexity.**

Earlier E023 work also observed consequential authority immediately outside fixed top-5 cutoffs. G1d reproduces the rank-boundary problem on separately frozen material.

## Evaluation discipline

Keep separate:

- positive authority sufficiency;
- conflation risk;
- exact/follow-up rank position;
- candidate-generation cutoff;
- final evidence budget;
- semantic correctness;
- unsupported claims / epistemic upgrades;
- direct-vs-attributed authorship;
- terminal authority type (`RAW_MEMORY` vs `HUMAN_KNOWLEDGE`);
- temporal/correction correctness;
- evidence size and model-call cost.

A context can be sufficient but risky; a risky context can still yield a correct answer; a clean context can still be composed badly. Do not collapse those failure surfaces into one score.

## Current action

Stay inside **G1 Retrieval / Composition**. Paid calls are paused at this checkpoint.

Immediate research question:

> **Can a modest explicit query-time evidence budget recover load-bearing authority more reliably and cheaply than planner/selector complexity, without causing semantic conflation or context-noise errors?**

Before another paid comparison:

1. freeze a **new separated slice** before semantic answers exist;
2. freeze the evidence-budget rule prospectively;
3. prefer a character/token budget over a universal source-count constant when practical;
4. compare a strong exact-BM25 budget baseline against any more complex retrieval/planning mechanism using the same composer;
5. score authority sufficiency, risk, semantic correctness, unsupported claims, evidence size, and model calls separately;
6. do not semantically rerun AQxxx/BQxxx;
7. keep evaluator clauses offline;
8. keep Dogfood 0.1.16 runtime unchanged while natural installed use continues.

Do **not** move from G1d failure to persistent semantic dossiers, graph/entity infrastructure, a universal KnowledgeUnit schema, vector defaults, or automatic identity/routing.

Any durable semantic architecture still requires its own evidence gate and, if promoted to policy, an ADR.
