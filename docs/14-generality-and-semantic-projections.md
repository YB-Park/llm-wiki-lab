# Generality and semantic projections — working design gate

Status: **WORKING DESIGN GATE / NOT AN ADR / NOT A STORAGE DECISION**  
Date: 2026-08-19 KST  
Tracking: Issue #160  
Experiment: E023

## Why this exists

LLM Wiki must not accidentally define “Wiki” as a collection of developer-shaped source summaries merely because that was the smallest useful Agent Wiki slice.

At the same time, “more general” must not become an excuse to install a universal Entity/Relation/KnowledgeUnit schema, graph database, vector default, or automatic identity machinery before the workload demonstrates a need.

The design target is **capability generality before storage uniformity**.

## Working product thesis

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. The product succeeds when the Agent can reconstruct and use the right semantic view at the moment of need; it does not require every useful view to exist as a permanent node/page/schema.**

## Layer 1 — Authority Core

The durable core remains semantic-ontology agnostic. It owns:

- admitted RAW evidence and immutable identity/integrity;
- provenance and local source navigation;
- current/history and explicit correction/change/dispute semantics;
- Human Knowledge authorship and explicit user epistemic commitments;
- privacy/permission boundaries;
- deterministic repairable storage invariants.

The Authority Core should not need to know whether a future semantic view is a person, project, incident, concept, decision, policy, vendor, timeline, or something not yet designed.

## Layer 2 — Semantic projections

A semantic projection is a task/retrieval/maintenance aid built from authoritative anchors. Examples may include:

- `source-note-v0`;
- an ephemeral cross-source dossier for one question;
- a concept synthesis;
- a decision-history view;
- a timeline;
- a project summary;
- a fixed-target persistent dossier;
- a semantic retrieval index.

These projections do **not** need one shared permanent ontology in Alpha.

Common safety properties should be stronger than common schema:

- DERIVED;
- NONCANONICAL;
- authority-anchor resolvable;
- inspectable;
- reversible or rebuildable;
- unable to silently impersonate RAW evidence or Human Knowledge.

## Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Valid terminal anchors include admitted `RAW_MEMORY` and explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may be useful working/navigation/compilation state, but persistence does not make it terminal authority.

E023 G1c-R1 adds a concrete refinement: **finding an authoritative anchor is not enough if a later selection/compression stage discards it before composition**. The end-to-end G1 path must preserve load-bearing authority through retrieval, selection, and answer composition.

## `source-note-v0` boundary

The current Agent Wiki source note is useful but narrow:

- one source per note;
- developer-friendly summary / operational rules / boundaries / open questions;
- source-scoped retrieval.

Treat it as **one derived projection under product test**.

Do not infer that every heterogeneous source should fit that schema, that source is the permanent semantic unit, that source notes must mediate every query, or that adding universal fields to the note schema equals generality.

## Persistence is earned, not assumed

Persistent semantic state adds lifecycle obligations: refresh timing, compilation loss, stale state, repair/rebuild, migration, retrieval dominance, maintenance spend, and possibly identity merge/split risk.

Therefore persistence is an optimization to earn when a strong ephemeral approach is measurably insufficient because of repeated cost, inconsistency, latency, retrieval fragility, or downstream quality.

Use this order:

1. **G1 Retrieval / Composition** — can authoritative material be found, preserved, and combined at query time?
2. **G2 Persistence** — with retrieval held strong and fixed, does durable projection materially improve repeated use after lifecycle cost?
3. **G3 Identity / Routing** — only if persistent targets are already valuable, does automatic subject discovery/routing earn itself safely?

A G1 failure is not evidence for G2. A G2 success is not evidence for G3.

## Semantic subject identity

Identity ambiguity is broader than people: projects, products, incidents, policies, decisions, vendors, concepts, and evolving topics can all have aliases or changing names.

Strong identifiers are **identity evidence**, not universal identity truth. Weak signals such as name similarity or role proximity remain derived hypotheses unless an authoritative adapter or human supplies stronger semantics.

Resolve ambiguity when consequence requires it rather than forcing every mention into a durable merge/split decision during ingest.

E023 now contains two versions of the same trust lesson:

- G1a Q001 omitted an explicit identity bridge and Luna confidently merged aliases anyway;
- G1c-R1 AQ001 **retrieved** the explicit bridge into the candidate pool, but the selector discarded it and Luna again confidently merged the identity from the insufficient final context.

> **Truth-by-luck is not trustworthy semantic recovery.**

The second case is especially important: a persistent identity store is not implied when the bridge was already available in ephemeral retrieval. The immediate failure is authority-preserving selection and consequence-sensitive composition.

## Query-time synthesis is a first-class architecture option

An LLM-facing Wiki differs from a human-only wiki: a useful semantic page may be assembled on demand and discarded.

The baseline competitor for persistent semantic infrastructure is therefore:

> authoritative evidence + strong retrieval/planning + authority-preserving selection + enough context + capable LLM

If that baseline reliably answers cross-source questions, not persisting a dossier is a positive architecture result, not a missing feature.

## E023 G1a — blind planning NOT EARNED

Frozen run `32215941344`, exact Luna, 30 calls, zero rerolls.

- A exact BM25 top-5: 8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR.
- C question-only planner -> BM25 -> RRF top-5: 8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR.
- C improvements: 0.
- promotion: **NOT_EARNED**.

Blind query expansion did not outperform the simple lexical floor.

## E023 G1b — evidence-follow final policy NOT EARNED, targeted repair observed

Frozen run `32217824760`, exact Luna, 12 calls, zero rerolls.

G1b used initial exact top-5 -> bounded evidence inspection -> missing/ambiguous relation -> targeted BM25 -> selector <=5 -> unchanged composer.

Frozen result:

- candidate recovery of previously missing source: 2/4;
- final-context recovery: 1/4;
- semantic answers: 4 PASS;
- Q001 improved CRITICAL_ERROR -> PASS;
- promotion: **NOT_EARNED** under the preregistered >=3/4 final recovery rule.

This established a targeted signal that evidence-aware follow-up can repair missing-authority failures without persistent semantic identity.

## Authority sufficiency is not flat source completeness

G1b exposed that flat `required_sources` lists were too coarse. A posthoc support-clause hypothesis separated uniquely load-bearing authority, alternatives, repeated-support minima, and forbidden conflation.

Against frozen G1a/G1b contexts:

- G1a A flat complete 6/10; support complete 9/10;
- G1a C flat complete 6/10; support complete 9/10;
- G1b final contexts support complete 4/4;
- Q001 was the unique support-incomplete G1a case and the frozen critical error;
- Q008 was support-complete but semantically PARTIAL, isolating composition omission.

The evaluator question became:

> **Did the selected context contain enough typed authoritative support to establish every load-bearing proposition?**

A prospective evaluation-only contract was then frozen on separated material before G1c semantic execution:

- 15 new anchors;
- 6 questions;
- 14 `RAW_MEMORY` + one load-bearing `HUMAN_KNOWLEDGE`;
- `all_of`, `any_of`, `min_count` support clauses;
- identity/attribution bridges, negative evidence, temporal correction, repeated support, forbidden conflation;
- statuses `INSUFFICIENT_AUTHORITY`, `SUFFICIENT_CLEAN`, `SUFFICIENT_WITH_CONFLATION_RISK`.

> **A richer evaluator is not evidence for a richer canonical storage schema.**

Do not expose evaluator clauses as runtime product facts merely because they are useful for controlled diagnosis.

## E023 G1c v0 — invalid execution

G1c reused the already-defined evidence-follow mechanism instead of designing a new retrieval trick after seeing the prospective evaluator slice.

Run `32229563330`, source `987ee7ec615f7eb869be59f14a1928a3811baeed`, is frozen as **INVALID_EXECUTION**. A runner aggregation bug occurred after six A composer calls and the first B planner/selector/composer sequence, before the B row was persisted.

No retrieval-selection conclusion is taken from v0. The six A outputs are auxiliary semantic baselines only; lost B outputs are not reconstructed or treated as rerolls.

## E023 G1c-R1 — candidate retrieval signal, final selection NOT EARNED

R1 is a separately preregistered B-only recovery identity with unchanged retrieval/selection/composition semantics and improved evidence persistence.

Frozen run:

- run `32232116273`;
- source `5227ac2b3f93c4f807e388822bfff963d0041120`;
- exact Luna;
- 18/18 calls;
- zero rerolls;
- result SHA-256 `8f3e77163db92f7dff0b0a9aed5776c6dadd0eebfdb122fbfecf4313d0dae822`;
- execution complete;
- retrieval-selection promotion: **NOT_EARNED**.

### Stage decomposition

| stage | clean | sufficient + conflation risk | insufficient |
|---|---:|---:|---:|
| exact initial top-5 | 4 | 1 | 1 |
| evidence-follow candidate pool | 4 | 2 | **0** |
| final selector | 4 | 0 | **2** |

The candidate pool was positive-authority complete on **6/6** questions. That is a genuine retrieval-stage signal.

The final selector then caused two authority losses:

- **AQ001:** targeted retrieval recovered the explicit A003 `M. Chen -> Maya Chen` bridge. The selector removed the same-surname distractor A004 but also removed A003, returning the final context to insufficient. The composer then repeated an unsupported identity merge: CRITICAL_ERROR.
- **AQ004:** initial/candidate context was already clean with explicit early hypothesis, retry/rollback signal, and final cause. The selector compressed to final postmortem A011 alone, producing an insufficient final context and semantic `FAIL_RETRIEVAL`.

AQ002 is the counterexample where selection worked: the selector removed the distractor while preserving direct authorship, meeting attribution, and the identity bridge, yielding a clean PASS.

The preregistered strict rule required 6/6 clean final contexts. Actual was 4/6. The targeted-signal fallback also failed because clean count did not exceed the baseline and AQ004 regressed.

Therefore:

> **The current evidence-follow final-selection policy is NOT_EARNED.**

## What the G1c-R1 result changes

The leading controlled G1 diagnosis is now more specific:

> **Candidate retrieval can find the needed authority; unconstrained semantic compression/selection can throw it away.**

This is not evidence that a persistent semantic page, entity graph, or identity cache is required. The missing AQ001 bridge was already present in the ephemeral candidate pool.

A query-time architecture must therefore treat **authority preservation through selection** as a first-class safety property, not merely retrieval recall followed by arbitrary summarizing selection.

This does not imply that the evaluator's claim clauses should become runtime product nodes. The next design challenge is to find simple, general selection/budget behavior that preserves authority without installing evaluator-shaped ontology into the product.

## Separate composition findings

G1c-R1 also separates two composition-policy failures from selection:

### `HUMAN_KNOWLEDGE` epistemic type

AQ003's context is clean and the decision/rationale are substantively correct. The load-bearing decision anchor is explicit user-owned `HUMAN_KNOWLEDGE`, but the answer states it like an ordinary externally observed team fact.

The authoritative-anchor invariant includes terminal **type**, not only supporting text. Future composition policy must preserve that distinction when it matters to the claim.

### Overcautious sufficiency

AQ006's final context is clean under the prospective contract. The answer correctly says standard HelixCloud DR fails and the Canada-only option could satisfy the rule, then unnecessarily declares authority insufficient by demanding a stronger guarantee than the frozen proposition requires.

This is a composition sufficiency judgment error, not a retrieval failure.

## Evaluation discipline

Generality cannot be reduced to one answer score. Keep separate:

- authority sufficiency in initial context;
- candidate-generation sufficiency;
- final-selection sufficiency;
- conflation risk;
- semantic correctness;
- provenance resolution;
- wrong-subject attribution / false merge;
- direct-vs-indirect attribution;
- terminal authority type (`RAW_MEMORY` vs `HUMAN_KNOWLEDGE`);
- temporal correctness;
- unsupported characterization / epistemic upgrade;
- composition omission or overcautious insufficiency when authority was present;
- model calls/tokens/known billing units;
- human intervention and repair cost.

When an answer fails, locate the first stage where load-bearing authority was lost or mishandled before proposing persistent semantic structure.

## Separate axis — source-container ingestion

PDF/DOCX/MSG/EML support is a distinct provenance/adapter problem. Future adapters may need original immutable artifact identity, normalized rendition, extractor/version metadata, and structural locators.

Do not combine binary extraction quality with the semantic-generality gate.

## Current evidence summary

- E017 showed useful raw-first multi-source temporal synthesis and showed context construction can mimic a memory-architecture failure.
- E021 showed fixed-target persistent concept compounding can work, but not that persistence is necessary or discovery/routing is solved.
- E023 G1a rejected blind query expansion/RRF as a promoted mechanism.
- E023 G1b showed evidence-aware follow-up can repair a concrete missing-authority failure but did not earn broad promotion.
- The prospective authority-sufficiency evaluator separated missing authority, conflation risk, and composition failure on held-out material.
- G1c-R1 showed candidate retrieval can achieve positive authority completeness on 6/6, while final semantic selection can regress authority.
- Natural installed dogfood remains necessary because controlled corpora cannot establish long-horizon product value.

## Current action

Stay inside **G1 Retrieval / Composition** and pause paid semantic calls again.

Before any G1d semantic run:

1. use only frozen G1c-R1 rankings/candidate pools for **zero-model selection/budget counterfactual analysis**;
2. compare simple non-destructive evidence-budget policies;
3. require that a candidate rule preserve the recovered AQ001 identity bridge and avoid the AQ004 clean-context regression **without consulting evaluator clauses at runtime**;
4. keep the prospective authority evaluator evaluation-only;
5. separately track composition policy for explicit `HUMAN_KNOWLEDGE` typing and correct sufficiency judgment;
6. only if a concrete general selection/budget rule earns a comparison should another semantic execution be preregistered;
7. keep Dogfood 0.1.16 runtime unchanged while natural installed use continues.

The immediate research question is:

> **Can a simple, general, evaluator-independent evidence-budget/selection rule preserve recovered load-bearing authority without destructive compression?**

Do **not** move to persistent semantic dossiers, graph/entity infrastructure, universal KnowledgeUnit schema, or automatic identity/routing from G1c-R1.

Any durable semantic architecture still requires its own evidence gate and, if promoted to policy, an ADR.
