# Advisory review follow-up: generality and semantic-structure decision gate

> This is a **traceability / decision-gate follow-up**, not an implementation ticket and not a new critical-path item.

An advisory architecture review was performed against repository snapshot `341c9fffbb32607681fe93add82f9fcfb6e9d555` and published as:

- `research/advisory-reviews/2026-08-19-generality-semantic-architecture-review.md`
- review artifact commit: `cfd66ad97d3506bab9d5b65307ebb2a6ab22e795`

Full pinned review:
https://github.com/YB-Park/llm-wiki-lab/blob/cfd66ad97d3506bab9d5b65307ebb2a6ab22e795/research/advisory-reviews/2026-08-19-generality-semantic-architecture-review.md

## Why preserve this separately

The motivating example involved several meeting records plus email history with recurring people, aliases, roles, attribution, and temporal changes. That example is intentionally a **stress case for general cross-source semantic memory**.

It must **not** be interpreted as a proposal to turn LLM Wiki into a people directory, CRM, contact manager, phone book, or person-profile product. The same question applies to projects, products, contracts, incidents, concepts, decisions, customers, policies, and other cross-source knowledge subjects.

## Main review outcome

The review identified a real concern that the current derived Agent Wiki is source-note/document-centric relative to the broader product philosophy.

An initial candidate response was a persistent Knowledge IR / Entity layer. After adversarial re-review, that recommendation was deliberately weakened:

> Do not promote a universal Knowledge IR/entity/graph architecture from this review alone.

Preferred current hypothesis:

> **Stable admitted-evidence core + optional rebuildable semantic projections + strong raw fallback. Semantic persistence must be earned by demonstrated value.**

The user-facing capability to recover cross-source knowledge does not necessarily require a permanent entity/page/node. Query-time semantic compilation may be sufficient for some workloads.

## Questions this issue preserves

- Is current `source-note-v0` materially too document-centric on heterogeneous non-developer sources?
- Can raw retrieval + source notes + query-time synthesis recover cross-source semantic knowledge reliably enough without persistent semantic identity?
- When, if ever, does a fixed-target persistent semantic projection materially outperform query-time synthesis after lifecycle cost is included?
- If persistence is useful, can identity remain user-confirmed/fixed rather than automatically resolved?
- What failure class would actually justify alias/entity routing, semantic indexes, vectors, or graph-like structure?
- How should binary/source-container formats such as PDF/DOCX/MSG preserve original artifact identity separately from normalized/extracted text?

## Candidate future Generality Gate

Only when natural use makes this question active, compare in order:

1. **A — Raw + current retrieval**
2. **B — Raw + current source Agent Notes**
3. **C — Query-time semantic dossier/view; no persistent semantic state**
4. **D — Fixed-identity persistent dossier/view**
5. **E — Automatic identity/routing**

Do not start with E. Separate the value of cross-source synthesis, persistence, and automatic identity so one success does not silently authorize the next layer of complexity.

The evaluation should distinguish answer correctness, evidence recall/provenance, false merge/split, attribution error, temporal error, unsupported characterization, compilation loss, retrieval failure, maintenance cost, human intervention, and repair/rebuild cost.

## This issue does not authorize

- graph DB / RDF / OWL / universal ontology;
- permanent Entity/Relation core schema;
- universal KnowledgeUnit storage;
- automatic people profiling;
- automatic entity merge/split;
- automatic concept routing from E021;
- vector retrieval default changes;
- binary-ingestion and semantic-architecture changes bundled together;
- background semantic maintenance;
- autonomous canonical mutation;
- derived artifacts becoming evidence.

## Relationship to current priority

The reviewed HANDOFF explicitly says not to start vector/graph/ontology infrastructure or automatic concept routing from E021 and keeps installed P7 evidence as the immediate path.

This issue should remain a **parked design/research trace** unless natural dogfood or another preregistered gate makes the generality problem concrete enough to activate.

## Acceptable future outcomes

Any of the following are legitimate outcomes of this issue:

- close as `not planned` because raw/query-time behavior is sufficient;
- keep as a research question without product work;
- create a narrow preregistered Generality Gate experiment;
- promote one small derived projection after evidence;
- eventually write an ADR if a durable semantic architecture actually earns adoption.

The advisory review itself is not evidence that any of those later steps must happen.
