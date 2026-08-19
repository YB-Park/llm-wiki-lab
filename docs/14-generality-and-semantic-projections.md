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

1. **G1 Retrieval / Composition** — can authoritative material be found and combined at query time?
2. **G2 Persistence** — with retrieval held strong and fixed, does durable projection materially improve repeated use after lifecycle cost?
3. **G3 Identity / Routing** — only if persistent targets are already valuable, does automatic subject discovery/routing earn itself safely?

A G1 failure is not evidence for G2. A G2 success is not evidence for G3.

## Semantic subject identity

Identity ambiguity is broader than people: projects, products, incidents, policies, decisions, vendors, concepts, and evolving topics can all have aliases or changing names.

Strong identifiers are **identity evidence**, not universal identity truth. Weak signals such as name similarity or role proximity remain derived hypotheses unless an authoritative adapter or human supplies stronger semantics.

Resolve ambiguity when consequence requires it rather than forcing every mention into a durable merge/split decision during ingest.

E023 made this concrete: when an explicit identity bridge was omitted from context, Luna confidently merged aliases anyway. The merge happened to match frozen gold, but the context did not establish it.

> **Truth-by-luck is not trustworthy semantic recovery.**

## Query-time synthesis is a first-class architecture option

An LLM-facing Wiki differs from a human-only wiki: a useful semantic page may be assembled on demand and discarded.

The baseline competitor for persistent semantic infrastructure is therefore:

> authoritative evidence + strong retrieval/planning + enough context + capable LLM

If that baseline reliably answers cross-source questions, not persisting a dossier is a positive architecture result, not a missing feature.

## E023 G1a result

Frozen run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero rerolls.

A = exact query BM25 top-5 + composer.

C = question-only Luna query planner + BM25 + deterministic RRF + same top-5 + same composer.

Frozen semantic result:

- A: 8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR
- C: 8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR
- C improvements: 0
- C promotion: **NOT_EARNED**

The critical Q001 failure was an unsupported identity merge because the explicit S004 alias bridge was missing from final context.

Posthoc ranking-only analysis showed all four C missing sources at fused rank 6, so G1a did not prove query-time synthesis was useless. It proved only that **blind question-only expansion + consensus RRF + fixed top-5 did not outperform the strong baseline**.

## E023 G1b result

Frozen run `32217824760`, exact `gpt-5.6-luna`, 12 calls, zero rerolls.

G1b targeted only Q001/Q002/Q004/Q010 using a prospectively frozen retrieval condition. It used:

initial exact-query top-5 -> bounded evidence inspection -> missing/ambiguous relation -> 0–2 targeted BM25 queries -> temporary candidate pool -> selector choosing at most five sources -> unchanged G1a composer.

No persistent semantic state and no identity-specific composer rule were added.

Frozen result:

- candidate-pool recovery of previously missing source: 2/4;
- final-context recovery: 1/4;
- semantic verdicts: 4 PASS;
- Q001 improved CRITICAL_ERROR -> PASS;
- regressions: 0;
- new critical errors: 0;
- frozen promotion: **NOT_EARNED** because the preregistered recovery threshold was >=3/4.

The important positive signal is Q001: evidence-aware follow-up retrieval explicitly searched the missing identity relation, recovered S004 at rank 1, selected it, dropped the same-surname distractor, and the unchanged composer then answered with supported identity authority.

This earns a **targeted mechanism signal**, not a broad product policy.

## New evaluation lesson — authority sufficiency is not flat source completeness

G1b exposed that the original E023 flat `required_sources` lists were too coarse. Several listed sources were redundant corroboration rather than uniquely load-bearing authority.

A posthoc, zero-model, non-primary support-clause hypothesis was added only to explain already-frozen outcomes. It does not alter G1a/G1b promotion verdicts.

Against frozen contexts:

- G1a A flat complete: 6/10; support-clause complete: **9/10**;
- G1a C flat complete: 6/10; support-clause complete: **9/10**;
- G1b final contexts: **4/4 support-complete**;
- unique support-incomplete G1a question: **Q001**, exactly the frozen critical error;
- Q008 is support-complete but semantically PARTIAL, cleanly separating composition omission from retrieval insufficiency.

The better evaluation question is:

> **Did the context contain enough authoritative support to establish every load-bearing proposition in the expected answer?**

An evaluation-only authority contract may need:

- uniquely required authority;
- one-of alternative support;
- a minimum count for repeated observations;
- explicit negative evidence;
- required identity/attribution bridges;
- forbidden-conflation checks.

This structure belongs to the evaluator unless product evidence later earns a corresponding runtime representation.

> **A richer evaluator is not evidence for a richer canonical storage schema.**

## Evaluation discipline

Generality cannot be reduced to one answer score. Separate:

- authority sufficiency in context;
- lexical/retrieval ranking;
- answer correctness;
- provenance resolution;
- wrong-subject attribution and false merge/split;
- direct-vs-indirect attribution;
- temporal correctness;
- unsupported characterization / epistemic upgrade;
- disagreement preservation;
- composition omission when authority was present;
- model calls/tokens/known billing units;
- human intervention and repair cost.

When an answer fails, determine whether load-bearing authority was absent (**retrieval/selection failure**) or present but mishandled (**composition failure**) before proposing persistent semantic structure.

## Separate axis — source-container ingestion

PDF/DOCX/MSG/EML support is a distinct provenance/adapter problem. Future adapters may need original immutable artifact identity, normalized rendition, extractor/version metadata, and structural locators.

Do not combine binary extraction quality with the semantic-generality gate.

## Current evidence summary

- E017 showed useful raw-first multi-source temporal synthesis and also showed context construction can mimic a memory-architecture failure.
- E021 showed fixed-target persistent concept compounding can work, but did not show that persistence is necessary or that discovery/routing is solved.
- E023 G1a rejected blind query expansion/RRF as a promoted mechanism.
- E023 G1b showed evidence-aware follow-up retrieval can repair a concrete missing-authority failure, but did not pass its frozen broad promotion rule.
- E023's posthoc support analysis indicates the next bottleneck is **measurement of load-bearing authority sufficiency**, not product schema design.
- Natural installed dogfood remains necessary because controlled corpora cannot establish long-horizon product value.

## Current action

Stay inside **G1 Retrieval / Composition**, but pause paid retrieval tuning.

Before any new semantic run:

1. prospectively define an **evaluation-only authority-sufficiency contract** on held-out or clearly separated material;
2. freeze load-bearing unique support, alternatives, repeated-support minima, negative evidence, identity/attribution bridges, and forbidden conflation before seeing answers;
3. validate the evaluator with zero model calls;
4. only then decide whether another G1 mechanism comparison deserves paid calls;
5. keep Dogfood 0.1.16 runtime unchanged while natural installed use continues.

Do **not** move to persistent semantic dossiers, graph/entity infrastructure, universal KnowledgeUnit schema, or automatic identity/routing from E023 G1a/G1b.

Any durable semantic architecture still requires its own evidence gate and, if promoted to policy, an ADR.
