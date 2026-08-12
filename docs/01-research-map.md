# Research Map

This document defines the landscape we will study before selecting a production architecture.

The goal is not to collect references indiscriminately. Every system, paper, or practice should be examined through the same design questions so that ideas can be compared rather than merely summarized.

## 1. Common comparison frame

For every relevant system, record how it handles:

1. **Ingest** — what enters the system and what is rejected?
2. **Representation** — documents, claims, notes, graph nodes, events, summaries, etc.
3. **Organization** — hierarchy, tags, links, schema, dynamic taxonomy.
4. **Consolidation** — when observations become durable knowledge.
5. **Update** — how new evidence changes existing knowledge.
6. **Contradiction** — overwrite, coexistence, temporal supersession, dispute.
7. **Lifecycle** — split, merge, rename, archive, forgetting, deletion.
8. **Provenance** — how derived statements trace back to evidence.
9. **Retrieval** — search, graph traversal, agentic navigation, summaries, exact lookup.
10. **Evaluation** — how correctness, usefulness, and maintenance cost are measured.
11. **Human role** — approval points, correction loops, review burden.
12. **Failure handling** — diagnostics, repair, rollback, error memory.

## 2. Track A — Direct LLM Wiki implementations

Study implementations explicitly inspired by the LLM Wiki concept.

Questions:

- Which parts of the concept survived real use?
- Which features were removed because they created maintenance cost?
- What failure modes appear only after weeks or months?
- How do implementations distinguish raw material from synthesized pages?
- Do they use linting, review queues, error books, or provenance checks?
- How do they handle page growth, split/merge, and taxonomy drift?

Deliverable: `research/llm-wiki/landscape.md`

## 3. Track B — Agent memory

Candidate families include memory managers, long-term agent memory, reflective memory, episodic/semantic memory, and self-evolving memory.

Questions:

- What is the memory unit?
- Is memory append-only, rewritten, consolidated, or forgotten?
- How is old memory reconciled with new observations?
- Does retrieval use summaries, semantic search, graph structure, or an agent loop?
- What temporal assumptions are made?
- How is memory corruption detected?

Relevant concepts to investigate:

- episodic vs semantic memory,
- consolidation,
- reflection,
- forgetting,
- memory routing,
- retrieval policy learning,
- memory editing.

Deliverable: `research/agent-memory/landscape.md`

## 4. Track C — RAG, hierarchical retrieval, and GraphRAG

We care less about benchmark leadership and more about retrieval architecture.

Questions:

- When are flat chunks sufficient?
- When do summaries or hierarchy help?
- When do graph links improve multi-hop retrieval?
- What information gets lost by summarization?
- How does retrieval escalate from broad context to exact source evidence?
- How expensive is maintenance when the corpus changes?

Deliverable: `research/retrieval/landscape.md`

## 5. Track D — Temporal knowledge and changing facts

This track addresses the difference between "incorrect" and "formerly correct."

Relevant fields:

- temporal knowledge graphs,
- bitemporal databases,
- event sourcing,
- slowly changing dimensions,
- validity intervals,
- supersession semantics.

Questions:

- Should knowledge have `observed_at`, `valid_from`, and `valid_to`?
- Which statements should be current-state only?
- Which need full history?
- How should personal preference changes differ from objective fact changes?
- How should conflicting sources be represented when no single truth is established?

Deliverable: `research/temporal-knowledge/landscape.md`

## 6. Track E — Provenance and epistemic status

Relevant fields:

- data lineage,
- scientific citation practice,
- evidence graphs,
- claim verification,
- reproducible research.

Questions:

- What is the minimum viable provenance unit: source file, section, span, quote, claim?
- Which statements require exact provenance?
- How expensive is fine-grained citation maintenance?
- Can provenance be checked automatically?
- How should personal inference be distinguished from source assertion?

Deliverable: `research/provenance/landscape.md`

## 7. Track F — Personal knowledge management

Relevant traditions:

- Zettelkasten,
- evergreen notes,
- atomic notes,
- progressive summarization,
- maps of content,
- personal wikis.

Questions:

- What makes a note a useful long-lived unit?
- How much hierarchy is healthy?
- What causes link gardens to become noise?
- When should a note be split or merged?
- How does a person's understanding evolve without losing history?

We should treat PKM practices as human-tested heuristics, not automatically as LLM-optimal architecture.

Deliverable: `research/pkm/landscape.md`

## 8. Track G — Database and information-system design

Relevant concepts:

- append-only logs,
- event sourcing,
- materialized views,
- normalization/denormalization,
- schema migration,
- garbage collection,
- indexes,
- transactions,
- consistency models.

Working analogy to test:

```text
raw observations / sources ~= source-of-record log
wiki pages                 ~= materialized views
consolidation              ~= view maintenance / compilation
schema                     ~= data model
lint                       ~= integrity constraints
Git                        ~= version history / rollback mechanism
```

This analogy is useful only if it improves concrete design decisions; it should not become architecture by metaphor alone.

Deliverable: `research/data-systems/landscape.md`

## 9. Track H — Software documentation and docs-as-code

Relevant practices:

- ADRs,
- documentation linting,
- broken-link checking,
- review workflows,
- CI validation,
- deprecation and migration policy,
- code ownership,
- changelogs.

Questions:

- Which wiki changes should require explicit review?
- Can destructive knowledge operations be treated like schema migrations?
- What can be automatically linted before a wiki change is accepted?
- What should Git history preserve vs explicit change logs?

Deliverable: `research/docs-as-code/landscape.md`

## 10. Track I — Wikipedia / information science / ontology maintenance

Relevant topics:

- disambiguation,
- redirects,
- notability,
- category systems,
- citation policy,
- stale-page maintenance,
- ontology evolution,
- entity resolution.

Questions:

- What problems recur in any long-lived knowledge corpus regardless of LLMs?
- Which editorial mechanisms can be simplified for a single-person wiki?
- How are rename/merge/split decisions made safely?

Deliverable: `research/information-science/landscape.md`

## 11. Cross-cutting synthesis

After the first landscape pass, produce a matrix with systems as rows and the 12 common comparison dimensions as columns.

The purpose of synthesis is to identify recurring architectural patterns such as:

- immutable source + mutable synthesis,
- staged observations + periodic consolidation,
- hierarchical navigation + exact retrieval fallback,
- temporal supersession instead of destructive overwrite,
- error books / learned maintenance rules,
- risk-sensitive human review,
- automatic structural linting,
- schema evolution through explicit migrations.

No pattern should become policy merely because it appears frequently. It becomes a candidate for experiment.
