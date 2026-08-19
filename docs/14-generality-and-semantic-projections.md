# Generality and semantic projections — working design gate

Status: **WORKING DESIGN GATE / NOT AN ADR / NOT A STORAGE DECISION**  
Date: 2026-08-19 KST  
Tracking: Issue #160  
Experiment: E023

## Why this exists

LLM Wiki must not accidentally define “Wiki” as a collection of developer-shaped source summaries merely because that was the smallest useful Agent Wiki slice.

At the same time, “more general” must not become an excuse to install a universal Entity/Relation/KnowledgeUnit schema, graph database, vector default, or automatic identity machinery before the workload demonstrates a need.

The design target is therefore **capability generality before storage uniformity**.

## Working product thesis

> **LLM Wiki is a trustworthy authority core plus task-appropriate semantic views. The product succeeds when the Agent can reconstruct and use the right semantic view at the moment of need; it does not require every useful view to exist as a permanent node/page/schema.**

## Layer 1 — Authority Core

The core remains deliberately semantic-ontology agnostic.

It owns durable trust facts such as:

- admitted RAW evidence and immutable identity/integrity;
- provenance and local source navigation;
- current/history and explicit correction/change/dispute semantics;
- Human Knowledge authorship and explicit user epistemic commitments;
- privacy/permission boundaries;
- deterministic repairable storage invariants.

The Authority Core should not need to understand whether a future semantic view represents a person, project, incident, concept, decision, policy, vendor, timeline, or something not yet designed.

## Layer 2 — Semantic projections

A semantic projection is a task/retrieval/maintenance aid built from authoritative anchors.

Examples may include:

- `source-note-v0`;
- an ephemeral cross-source dossier assembled for one question;
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
- provenance/authority-anchor resolvable;
- inspectable;
- reversible or rebuildable;
- unable to silently impersonate RAW evidence or Human Knowledge.

## Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Valid terminal anchors include:

- admitted `RAW_MEMORY` for source/evidence claims;
- explicit `HUMAN_KNOWLEDGE` for user-owned decisions, beliefs, rationale, or hypotheses.

`DERIVED_MEMORY` can be working state or a navigation/compilation aid, but persistence does not make it terminal authority.

This formulation intentionally avoids the narrower claim that all durable synthesis must bottom out only in external/raw evidence; the product already has a distinct human-authorship authority class.

## `source-note-v0` boundary

The current Agent Wiki source note is useful but narrow:

- one source per note;
- developer-friendly fields such as operational rules and boundaries;
- source-scoped retrieval.

Treat it as **one derived projection under product test**.

Do not silently infer:

- that every heterogeneous source should fit that schema;
- that a source is the permanent semantic unit of the Wiki;
- that source notes must mediate every future query;
- that adding more fields to the source-note schema is the path to generality.

## Persistence is earned, not assumed

Persistent semantic state adds lifecycle obligations: refresh timing, compilation loss, stale state, repair/rebuild, migration, retrieval dominance, maintenance spend, and possibly identity merge/split risk.

Therefore persistence is an optimization to earn when a strong ephemeral approach is measurably insufficient because of repeated cost, inconsistency, latency, retrieval fragility, or downstream quality.

A useful staged order is:

1. **Retrieval / Composition** — can authoritative material be found and combined at query time?
2. **Persistence** — with retrieval held strong and fixed, does a durable projection materially improve repeated use after lifecycle cost?
3. **Identity / Routing** — only if persistent targets are already valuable, does automatic subject discovery/routing earn itself safely?

A failure at step 1 is not evidence for step 2. Success at step 2 is not evidence for step 3.

## Semantic subject identity

If identity work is ever activated, avoid narrowing the architecture to “people.” Identity ambiguity also exists for projects, products, incidents, policies, decisions, vendors, concepts, and evolving topics.

Strong identifiers such as an email address or external contact ID are **identity evidence**, not universal identity truth. Weak signals such as name similarity or role proximity remain derived hypotheses unless the source adapter or human supplies stronger semantics.

Resolve ambiguity when consequence requires it rather than forcing every mention into a durable merge/split decision during ingest.

E023 G1 makes this boundary concrete: when an explicit identity bridge was omitted from context, Luna confidently merged two aliases anyway. The final merge happened to match frozen gold, but the context did not establish it. **Truth-by-luck is not trustworthy semantic recovery.**

## Query-time synthesis is a first-class architecture option

An LLM-facing Wiki differs from a human-only wiki: a useful semantic page may be assembled on demand and discarded.

The baseline competitor for persistent semantic infrastructure is therefore increasingly:

> authoritative evidence + strong retrieval/planning + enough context + capable LLM

If that baseline reliably answers cross-source questions, not persisting a dossier is a positive architecture result, not a missing feature.

E023 G1 also narrows what “strong retrieval/planning” means. A question-only planner that emits several blind query rewrites and combines them with consensus RRF is **not automatically stronger** than a simple exact-query baseline. Retrieval planning should be judged by whether it brings missing load-bearing authority into bounded context, not by whether it produces more queries.

## Evaluation discipline

Generality cannot be reduced to one answer score. Separate at least:

- evidence retrieval/recall;
- answer correctness;
- provenance resolution;
- wrong-subject attribution and false merge/split;
- direct-vs-indirect attribution;
- temporal/current-vs-earlier correctness;
- unsupported characterization / epistemic upgrade;
- disagreement preservation;
- compilation loss for persistent updates;
- model calls/tokens/known billing units;
- human intervention;
- repair/rebuild cost.

When an answer fails, first determine whether the required evidence was absent from context (**retrieval failure**) or present but mishandled (**composition failure**) before proposing persistent semantic structure.

Some failures are joint: E023 Q001 was **retrieval-rooted** because the explicit identity bridge was absent, but also **epistemic/compositional** because the model should have surfaced uncertainty instead of converting circumstantial similarity into a supported identity claim.

## Separate axis: source-container ingestion

PDF/DOCX/MSG/EML support is a distinct provenance/adapter problem. Future source adapters may need original immutable artifact identity, normalized rendition, extractor/version metadata, and structural locators.

Do not combine binary extraction quality with the first semantic-generality experiment. E023 uses frozen normalized text.

## Current evidence

- E017 already showed useful raw-first multi-source temporal synthesis for NASA material.
- E017 also showed a CPython failure where the correct long source was retrieved but the decisive region was omitted from context: evidence that retrieval/context construction can mimic a “memory architecture” failure.
- E021 showed fixed-target persistent cross-source concept compounding can work with Luna, but did not test discovery, routing, identity, or whether persistence is necessary.
- Natural P7 dogfood remains essential, but its developer-project source mix is favorable to the current developer-shaped source-note projection and therefore cannot be the only generality test.
- **E023 G1 frozen run `32215941344`:** simple A and planned C both scored 8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR. C added 10 planner calls but produced 0 semantic improvements and closed 0/4 required-source recall@5 gaps. The critical Q001 failure was an unsupported identity merge with the explicit alias bridge absent from both contexts.

## Current action

Stay inside **G1 Retrieval / Composition**.

The first planned-query mechanism is not earned as a default. Do **not** interpret that result as evidence for G2 persistence.

Before any more semantic calls:

1. analyze the frozen G1 artifact with zero-model counterfactual selection/fusion checks;
2. if the remaining failure is worth another controlled gate, preregister a narrower **iterative evidence-follow** path: initial retrieval → inspect bounded hits/snippets → identify the specific missing relation → targeted follow-up retrieval → same bounded final context;
3. add consequence-sensitive answer behavior: when a load-bearing identity/attribution relation lacks an explicit authoritative bridge, surface uncertainty rather than silently merging;
4. keep 0.1.16 product behavior unchanged until controlled evidence and natural dogfood jointly justify a product slice.

Do not move to persistent semantic dossiers, graph/entity infrastructure, or automatic identity/routing from E023 G1.

Any durable semantic architecture still requires its own evidence gate and, if promoted to policy, an ADR.
