# E023 — Generality Retrieval / Composition Gate

Status: **G1 PREREGISTERED / ZERO-MODEL FOUNDATION**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy **cross-source semantic knowledge** from heterogeneous admitted evidence without first introducing persistent entity/graph/ontology state?

E023 is intentionally **not** an entity-system experiment. It tests the simpler explanation first: perhaps the missing capability is retrieval planning and query-time composition rather than a new persistent semantic store.

## Core architecture guardrail

- The Trust / Authority Core remains knowledge-type agnostic.
- `source-note-v0` is one source-oriented **DERIVED projection**, not the ontology of LLM Wiki.
- A load-bearing derived statement must resolve to an authoritative anchor whose epistemic type remains explicit: admitted RAW evidence or explicit HUMAN_KNOWLEDGE. DERIVED state is never terminal authority.
- Semantic persistence is an optimization that must earn itself; it is not the default definition of knowledge.

## Three gates, in order

### G1 — Retrieval / Composition — **E023**

Compare a simple raw-retrieval answer path with bounded planned multi-query retrieval plus **ephemeral** cross-source composition. No persistent semantic state is created.

### G2 — Persistence — future only if G1 earns it

Hold the strongest G1 retrieval/composition procedure fixed, then compare ephemeral synthesis with a fixed-identity persistent derived projection. This separates persistence value from retrieval quality and identity resolution.

### G3 — Identity / Routing — last

Only if persistence itself earns value may a later experiment test identity candidates, alias routing, merge/split, or bounded automatic target routing.

**Do not infer G2 or G3 from a G1 failure.** A failed answer with missing required evidence is first a retrieval failure, not evidence that persistence is required.

## Frozen G1 corpus

The controlled corpus contains **18 normalized text sources** and **10 cross-source questions** across four families:

- identity / attribution / role-over-time;
- project decision rationale;
- incident timeline / hypothesis correction;
- vendor constraint conflict.

The person-heavy cases are stress tests, not a product proposal for people profiles. Binary PDF/DOCX/MSG extraction is deliberately excluded so parser quality cannot confound the semantic result.

## Current phase

Before any paid model generation, `validate_corpus.py`:

1. validates frozen IDs, family counts, source/question hashes, and ground-truth references;
2. runs a deterministic BM25 diagnostic using the production tokenization/BM25 constants;
3. reports required-source ranks, recall@5, and distractor presence for each exact user question;
4. makes **zero model calls** and does not declare semantic PASS/FAIL from lexical rank alone.

Paid A/C execution must not begin until the preregistration is merged to `main` and the zero-model preflight is clean.

## Relationship to the product

Dogfood 0.1.16 remains the installed product baseline. E023 adds no graph, entity store, vector default, background worker, new canonical schema, or product binary behavior.

Natural multi-session dogfood continues in parallel. E023 exists because the current dogfood corpus is developer-document-heavy and therefore can systematically under-detect `source-note-v0` generality problems.
