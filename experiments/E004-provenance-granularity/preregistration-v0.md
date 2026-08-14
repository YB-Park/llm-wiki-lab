# E004 — Minimum provenance granularity gate v0

Status: **preregistered before corpus scoring**

Date: 2026-08-14

Issue: #43

## 1. Decision question

What is the minimum provenance granularity that materially improves auditability and claim-to-source ownership over strong raw/structural baselines without imposing maintenance cost large enough to justify a persistent claim graph prematurely?

E004-v0 isolates provenance representation. It does **not** test LLM generation quality or automatic claim extraction.

## 2. Null / kill hypothesis

> Structural provenance plus cheap deterministic audit-time localization is sufficient for the important controlled workload; universal exact claim-to-span provenance does not produce a large, repeatable audit/source-ownership advantage that justifies its precision burden.

If this null survives, do not build a universal claim-level provenance system or claim graph from E004-v0.

## 3. Experimental unit and dependence

Primary experimental unit: **topic**.

Frozen target:

- 24 topics;
- 6 immutable raw source revisions per topic at W0;
- 3 derived sections per topic;
- 4 derived claims per section;
- 12 claims/topic;
- 288 claim rows total before condition expansion;
- every provenance condition is paired on the same topic, source bytes, derived claims, fault state, and waves.

Claims/atoms inside a topic are dependent diagnostics and are **not** treated as independent samples.

This is a large-effect controlled mechanism/falsification experiment. n=24 topics is not intended to resolve small policy differences.

## 4. Conditions

### P0 — page/object bibliography + cheap audit-time localization

The derived page exposes a set of raw source-revision IDs, with no per-section or per-claim ownership.

To avoid a strawman, the deterministic auditor may perform **within-cited-source lexical localization** at audit time using the frozen E014-style tokenizer/BM25 over structural units. This is a cheap baseline, not a model call.

P0 therefore measures whether persistent fine provenance beats keeping coarse sources and locating evidence only when verification is requested.

### P1 — structural ownership

Each derived section maps to one or more raw source-revision structural units. Every claim in the section inherits that same evidence region set.

No claim receives a minimal exact evidence span.

### P2 — exact claim-to-span everywhere

Every derived claim atom maps to one or more exact character spans in immutable raw source revisions.

Exact spans always retain their raw source-revision ID. They are navigation/ownership metadata, not new authority.

### P3 — selective precision

Every claim inherits P1 structural provenance.

Only fixture-predeclared `risk=high` claims additionally receive P2 exact spans. `risk` is synthetic corpus metadata fixed before scoring. E004-v0 does **not** infer risk from text or use an LLM/heuristic classifier.

## 5. Important representation boundary

The benchmark may use stable topic/section/claim/atom IDs internally to pair conditions and score maintenance waves. These IDs are **experiment oracle machinery**, not an accepted product claim schema and not evidence that the production Wiki needs a global claim graph.

## 6. Fresh corpus and balancing

Corpus generation must be deterministic from a frozen seed that has not been used by earlier experiments.

Each topic contains 12 claims: 6 high-risk and 6 low-risk. Fault/workload family is rotated across topic indices so that each family appears in both risk classes across the corpus. Risk must not be equivalent to “this row contains a fault.”

Required claim/fault families:

1. **clean** — valid claim with correct raw ownership;
2. **wrong_value** — exact number/date/status value in derived claim is changed while provenance remains from the pre-fault claim;
3. **wrong_source** — the asserted fact exists elsewhere in pooled raw evidence but not in the source ownership claimed by the provenance state;
4. **derived_only** — provenance path terminates at a derived artifact rather than a raw source of record;
5. **within_source_conflict** — one raw source contains competing passages for the same subject/predicate; audit must not silently treat one precise passage as global consensus;
6. **multi_source_misownership** — a composite claim contains multiple atoms whose correct support belongs to different raw sources, with at least one atom assigned to the wrong source in the injected state.

Each topic must include every family at least once. Exact family counts and risk cross-tab are frozen before scoring.

## 7. Two maintenance/rewrite waves

### W0 — initial provenance state

All conditions are constructed from the same immutable W0 raw source revisions and derived artifact.

### W1 — raw source revision wave

A deterministic subset of source revisions is superseded by new immutable revisions covering at least:

- support preserved but text/structure shifted;
- a factual correction;
- a conflict added or resolved.

Historical W0 source IDs/spans must remain resolvable. For a **current derived view**, compute the minimal metadata edits required to point policy metadata at the correct W1 current raw revision/locator.

This is an **oracle lower bound on maintenance work**: no automatic updater is being evaluated.

### D1 — derived page rewrite/reorder wave

The derived page is reordered/reformatted without changing the intended semantic claim atoms except where the frozen fault injection says otherwise.

Benchmark-stable IDs are available to compute the theoretical minimum reattachment/update work. This is an optimistic lower bound for precise provenance; it does not prove stable product claim IDs are free or desirable.

## 8. Deterministic audit protocol

No LLM judge.

The corpus contains hidden fact/span ownership metadata used only by the scorer. Human-readable synthetic source text itself must not contain explicit `GOLD`, `FAULT`, or condition labels.

The auditor classifies each claim as one of:

- `verified`;
- `invalid_or_unsupported`;
- `contested`;
- `unresolved_budget`.

Gold outcomes are frozen by the generator.

### Bounded audit budget

Primary audit budget: **1,200 source characters per claim**.

Sensitivity budgets, reported but not gate-changing: **600** and **2,400** characters.

Inspection is hierarchical and deterministic:

- P0: use claim text/atoms only to rank structural units inside the page-level cited raw sources; inspect ranked units in deterministic score/source/locator order until the character budget is exhausted.
- P1: inspect mapped structural units in deterministic source/locator order until budget exhausted.
- P2: inspect exact atom span(s) first, then expand to their containing structural unit(s) while budget remains. This prevents an exact citation from hiding a competing passage in the same structural unit.
- P3: high-risk claims use the P2 order; low-risk claims use P1.

No condition may search uncited sources during primary audit. A pooled-evidence oracle is used only to score source-ownership faults, not to rescue a condition.

## 9. Source ownership metric

For each claim atom, provenance is `ownership_exact` only if the condition can uniquely identify the raw source revision(s) that actually support that atom.

A page/section source set containing the correct source plus unrelated plausible sources is **ambiguous**, not exact ownership.

A fact existing somewhere in pooled context does not count as support for a different cited source.

## 10. Primary measures

Computed per claim, aggregated to topic before primary paired analysis:

- bounded audit outcome accuracy at 1,200 chars;
- critical-fault detection rate;
- exact source-ownership rate;
- ownership ambiguity/error rate;
- clean false-accusation rate;
- within-source conflict detection rate;
- derived-only provenance acceptance rate;
- exact provenance reversibility to immutable raw bytes;
- inspected source characters;
- structural units / source revisions visited;
- serialized provenance metadata bytes;
- W1 oracle-minimum provenance update actions;
- D1 oracle-minimum provenance reattachment/update actions;
- broken/stale provenance after W1/D1 before repair.

Report all claim/fault/risk strata descriptively. Primary uncertainty is topic-level only.

## 11. Critical audit set

For Gate A, `critical` includes:

- wrong_value;
- wrong_source;
- derived_only;
- within_source_conflict;
- multi_source_misownership.

Clean rows are used for false-accusation control.

## 12. Statistics

Paired topic-level bootstrap:

- 20,000 resamples;
- seed `20260831`;
- resample 24 topics with replacement;
- preserve all claims/conditions within sampled topic clusters;
- report point difference and percentile 95% CI.

No claim-level confidence interval may be presented as primary evidence.

No multiple-comparison-adjusted discovery claims are planned. The frozen gates below are conjunctive and primary; other slices are diagnostics.

## 13. Gate A — does precise claim-to-span provenance deserve to exist as a capability?

All checks required:

1. P2 − P1 critical bounded-audit accuracy **>= +0.15**;
2. its topic-bootstrap 95% CI lower bound **> 0**;
3. P2 − P1 exact source-ownership rate **>= +0.20**;
4. its topic-bootstrap 95% CI lower bound **> 0**;
5. P2 mean inspected characters on critical claims **<= 0.65 × P1**;
6. P2 clean false-accusation rate is no worse than P1 by more than **+0.02**;
7. P2 within-source conflict detection is no worse than P1 by more than **−0.05**;
8. P2 exact raw-span reversibility = **100%**;
9. P2 derived-only acceptance = **0%**;
10. no condition mutates raw evidence, E003 temporal relations, or default retrieval as part of scoring.

If any check fails: `DOES_NOT_SURVIVE_E004_PRECISE_GATE`.

A Gate A pass authorizes only a local exact-provenance capability/shadow prototype, not universal product adoption.

## 14. Gate B — does selective precision deserve preference over universal precision?

Evaluate only as an architecture signal if Gate A passes. All checks required:

1. P3 high-risk bounded-audit accuracy >= P2 high-risk accuracy − **0.03**;
2. P3 high-risk exact ownership >= P2 high-risk exact ownership − **0.03**;
3. P3 high-risk conflict detection >= P2 high-risk conflict detection − **0.03**;
4. P3 total serialized provenance metadata bytes <= **0.75 × P2**;
5. P3 W1 oracle-minimum update actions <= **0.80 × P2**;
6. P3 clean false-accusation rate <= P2 + **0.02**;
7. every P3 exact span on its precise subset is raw-reversible = **100%**;
8. P3 derived-only acceptance = **0%**.

If all pass: `SELECTIVE_PRECISION_SURVIVES_E004_V0`.

If any fail: do not claim risk-adaptive provenance wins. P3 low-risk quality is always reported so the selective policy cannot hide failures outside its high-risk subset.

## 15. P0/P1 role and Pareto reporting

P0 and P1 are not strawmen.

Report a four-condition frontier over:

- audit accuracy;
- ownership exactness;
- inspected characters;
- metadata bytes;
- W1 update actions.

Cost never excuses materially worse critical audit quality.

## 16. Freeze protocol

Before the first held-out score:

1. create corpus generator;
2. create provenance-condition constructor/auditor;
3. create scorer/analysis;
4. use only a separate non-held-out fixture for development tests;
5. generate canonical held-out corpus and record corpus SHA-256;
6. record SHA-256 for generator, condition/auditor implementation, and scorer;
7. run a prescore validator that checks shape/family/risk balance, source/span reversibility, no raw gold/fault-label leakage, W0/W1/D1 structure, and workflow inability to score;
8. freeze a pre-run manifest;
9. only then enable a single official held-out score workflow.

After scoring, no threshold, budget, prevalence, condition logic, corpus, or scorer edits are allowed to reinterpret v0. Bugs found after score require an explicit amendment or fresh replication depending semantic impact.

## 17. Leakage / cheap baselines

Because this is a deterministic representation experiment rather than model reasoning, lexical surface leakage is not a classifier shortcut in the E009A sense. Still:

- raw human-readable text must not contain condition/fault/gold labels;
- condition constructors cannot read hidden gold outcome labels to choose provenance granularity;
- P3 may read only the frozen `risk` field, not fault family/outcome;
- P0 audit localization may use claim terms but not hidden support spans/owners.

The pooled-evidence gold oracle is scorer-only.

## 18. Architecture interpretation ceiling

Even if Gate A and Gate B pass, E004-v0 does **not** authorize:

- a global claim registry/graph;
- automatic claim extraction;
- automatic risk classification;
- LLM provenance assignment or repair;
- derived-to-derived evidence as authority;
- RDF/OWL/full W3C PROV storage;
- graph/vector database;
- persistent compiled-Wiki activation.

The strongest allowed conclusion is that a particular **local provenance granularity capability** deserves realistic/shadow evaluation.

## 19. Cost / model boundary

Model calls: **0**.

AI credits: **0**.

Any later Luna-based answer-quality or human-verification study must be separately preregistered and cannot retroactively change E004-v0.

## 20. Product convergence rule

Passing must enable a concrete next implementation; failing must eliminate one.

- Gate A fail → do not implement universal exact claim-to-span provenance; retain object/structural provenance and move on.
- Gate A pass → implement the smallest local precise-provenance record needed for shadow/realistic audit.
- Gate B pass → selective precision becomes the candidate policy for realistic testing, but risk labeling remains explicit/manual until separately justified.
- Gate B fail → do not claim selective/risk-adaptive provenance is preferred.
