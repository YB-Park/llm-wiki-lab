# Initial Synthesis After Direct LLM Wiki Research

Date: 2026-08-12
Status: synthesis / hypotheses, not policy
Depends on: `research/01-direct-llm-wiki-landscape.md`

## 1. What changed after the first research batch

The original LLM Wiki idea sounds deceptively simple:

```text
raw sources -> LLM -> maintained wiki -> answers
```

The direct evidence suggests that a serious implementation is closer to:

```text
sources
  -> ingest / triage
  -> structured compilation
  -> grounding checks
  -> persistent derived knowledge
  -> retrieval / navigation
  -> downstream questions
  -> failure detection
  -> repair / reconsolidation
  -> schema evolution
  -> regression checks
  -> human review where risk warrants it
```

The central research problem is therefore not "how should the Markdown look?"

It is:

> How do we maintain a lossy, LLM-generated representation of growing knowledge so that it remains useful, auditable, repairable, economical, and trustworthy over time?

That framing should guide the rest of Phase 1.

---

## 2. Five distinct failure classes

Our initial threat model focused heavily on hallucination/contamination. The first batch suggests at least five separate failure classes that must not be collapsed into one "accuracy" metric.

### F1 — Fabrication

The wiki states something unsupported by authoritative source material.

Examples:

- invented number,
- incorrect date,
- source A says X but wiki says Y,
- derived interpretation silently presented as sourced fact.

Primary defenses to investigate:

- immutable/source-of-record layer,
- provenance,
- deterministic evidence checks for high-signal facts,
- source verification on high-risk queries.

### F2 — Omission / compilation loss

The wiki says nothing false, but discards information needed later.

WiCER makes this impossible to treat as a minor edge case. A beautiful summary can be a poor memory.

Primary defenses to investigate:

- coverage probes,
- query-derived regression tests,
- selective raw fallback,
- preservation rules for exact/conditional information,
- representation/granularity choices.

### F3 — Temporal corruption

The wiki contains facts that were true at one time but are incorrectly exposed as current, or a new state destroys historically valid knowledge.

Primary defenses to investigate:

- explicit supersession,
- validity metadata where warranted,
- current-state vs history separation,
- source/date-aware retrieval.

### F4 — Structural corruption

Knowledge still exists but organization makes it hard to retrieve or maintain.

Examples:

- duplicate entities,
- page too broad,
- fragmented concept,
- stale index,
- bad taxonomy,
- links that encode obsolete structure.

Primary defenses to investigate:

- split/merge experiments,
- alias resolution,
- schema evolution,
- structural lint,
- retrieval-failure feedback.

### F5 — Maintenance-induced regression

An edit fixes one page/query while degrading other queries or destroying useful context.

This is the knowledge-base analogue of a software regression.

Primary defenses to investigate:

- query regression suites,
- edit impact analysis,
- diff-based review,
- downstream utility evaluation,
- reversible edit history.

These five classes should eventually appear in our evaluation scorecard and test corpus.

---

## 3. The strongest convergence: treat wiki generation as compilation

Multiple systems independently point toward a compiler-like mental model.

A useful abstraction is:

```text
Concrete knowledge state
    raw sources / observations / conversations
                |
                v
        compiler / consolidator
                |
                v
      derived canonical artifacts
                |
        +-------+-------+
        |               |
        v               v
    navigation       human reading
        |
        v
      queries
        |
        v
 failures / counterexamples
        |
        v
 diagnostics / rule changes / recompilation
```

The compiler analogy is more than metaphor because it suggests mature engineering tools:

- invariants,
- deterministic checks,
- regression tests,
- versioned transformations,
- reproducible builds where practical,
- source maps / provenance,
- incremental recompilation,
- diagnostics rather than silent repair.

But we must also remember where the analogy breaks: an LLM compiler is probabilistic, semantic, and may change behavior across model versions. Reproducibility cannot be assumed.

---

## 4. The wiki should probably not be treated as the sole memory

A major early architectural temptation is:

> "Once source material is compiled into the wiki, just query the wiki."

The first batch argues against making this an invariant.

Reasons:

1. compilation can lose future-critical facts,
2. exact values and disputed claims may require direct evidence,
3. personal knowledge may need historical reconstruction,
4. a compiled page may be optimized for thematic understanding rather than exact lookup.

The more plausible hypothesis is layered memory:

```text
raw evidence
    ^
    | verification / detail fallback
    |
derived wiki <-> indices/search
    ^
    |
query/navigation agent
```

The wiki remains the preferred semantic navigation layer, but not necessarily the final authority for every answer.

This preserves the original compounding advantage without making compilation loss unrecoverable.

---

## 5. We should distinguish three kinds of "tests"

### 5.1 Structural lint

Deterministic or low-ambiguity checks:

- broken links,
- malformed metadata,
- missing index entries,
- duplicate IDs,
- impossible paths,
- source file existence.

These are cheap and suitable for aggressive automation.

### 5.2 Grounding tests

Does a claim have adequate support?

Examples:

- exact values exist in linked evidence,
- source attribution exists,
- derived-only citation chain is detected,
- disputed claims expose disagreement.

Some can be deterministic; others may require LLM/source entailment checks.

### 5.3 Behavioral regression tests

Can the knowledge system still answer what it should answer?

Examples:

- previously correct exact-fact questions,
- temporal questions,
- cross-source synthesis questions,
- questions associated with a prior user correction,
- adversarial contamination probes.

This third category is the biggest addition to our initial thinking. A page edit can pass formatting and grounding checks while degrading downstream usefulness.

---

## 6. "Error Book" should be generalized into durable failure learning

Natural-language Error Books appear directly in LLM-Wiki research, but the concept should not be constrained to a single markdown file.

A failure can mature through stages:

```text
one-off failure
   -> recorded example
   -> generalized rule candidate
   -> regression test
   -> deterministic lint/check if possible
   -> schema/process change if recurring
```

This is attractive because human corrections become durable system improvement rather than repeated prompt steering.

Risk: overgeneralization.

A rule learned from one correction can create new false positives. Therefore every promoted rule should preserve:

- motivating examples,
- scope,
- counterexamples if known,
- tests showing what behavior it is meant to prevent.

This should be investigated in E008.

---

## 7. Current truth and historical truth should be treated as different products

There is real tension between:

- concise, current, low-noise answers,
- preserving old beliefs, failed approaches, superseded facts, and reasoning history.

Trying to put both into the same prose page may create an unreadable archive.

A promising hypothesis is to separate surfaces:

```text
Current synthesis
    "What do I currently believe/know?"

History / audit trail
    "What changed, why, and what used to be believed?"

Raw evidence
    "What did the original sources actually say?"
```

Git alone is not necessarily enough. Git tells us textual history, but not automatically semantic reasons for the change or whether an old statement was wrong, superseded, or merely reorganized.

E003 should explicitly compare whether semantic lifecycle metadata adds value beyond Git history.

---

## 8. Schema should be allowed to evolve, but evolution is high risk

We now have evidence supporting both sides:

- stable types/folders make operations predictable,
- evolving corpora invalidate early taxonomy assumptions.

Therefore "dynamic schema" should not automatically imply autonomous restructuring.

A plausible staged model to test is:

```text
LLM detects structural pressure
       |
       v
proposes split/merge/rename + rationale
       |
       v
runs impact analysis / migration preview
       |
       v
human approves high-impact restructure
       |
       v
mechanical migration + redirects + tests
```

This connects schema evolution directly to the automation-boundary research axis.

---

## 9. Cost must be measured as lifecycle cost, not per-query cost

A compiled wiki can save repeated query-time synthesis but spend substantial resources during ingest and maintenance.

A fair comparison must include:

```text
Total cost over period =
    source acquisition / parsing
  + ingest compilation
  + reconsolidation
  + embedding/index maintenance if any
  + query retrieval
  + answer synthesis
  + lint/testing
  + failed automation repair
  + human review attention
```

This is especially important for VS Code/Copilot use. A workflow that silently burns large context windows to keep hundreds of pages "fresh" may be economically worse than occasional rediscovery.

We should eventually compare systems over a workload trace, not isolated operations.

Candidate metric:

> maintenance cost per unit of downstream rediscovery avoided.

This will be difficult to define but is closer to the actual purpose than tokens per ingest alone.

---

## 10. Decisions we should explicitly avoid making yet

The first batch is sufficient to say that the following would be premature:

1. Choosing `concept/entity/source` as the permanent page ontology.
2. Choosing atomic notes as the permanent knowledge unit.
3. Choosing a fixed folder hierarchy.
4. Enabling autonomous split/merge/delete.
5. Assuming every ingest should alter the wiki.
6. Assuming every query should run embeddings/vector search.
7. Assuming compiled pages are enough for exact factual answers.
8. Assuming Git history alone solves temporal semantics.
9. Choosing claim-level provenance everywhere before measuring its cost.
10. Optimizing for maximum automation.

These are all experiment/research questions.

---

## 11. What appears safe enough to use as research infrastructure

These are not final wiki policies; they are low-risk practices for the lab itself:

- keep source references for research claims,
- distinguish evidence from interpretation,
- keep ADRs for decisions,
- preserve failed experiments,
- version everything in Git,
- turn newly discovered failure modes into explicit design questions or experiment candidates,
- avoid destructive cleanup of research history.

The lab should model the epistemic behavior we want to study.

---

## 12. Updated Phase 1 research order

The direct LLM Wiki batch has reduced some uncertainty and exposed new dependencies. Recommended next order:

### Batch B — Agent memory and consolidation

Questions:

- How do long-term agent-memory systems decide what to write?
- How do they consolidate observations into semantic memory?
- How do they handle memory conflict, forgetting, decay, and retrieval?
- What evidence exists on long-horizon performance vs one-shot benchmarks?

Candidate systems:

- MemGPT / Letta,
- A-MEM,
- Zep / temporal knowledge graph memory,
- Mem0,
- Infini Memory,
- other recent memory-maintenance systems with reproducible evaluations.

### Batch C — Temporal knowledge and provenance

Questions:

- What models distinguish observation time from validity time?
- How do event sourcing / bitemporal systems preserve current and historical truth?
- What provenance granularity is maintainable?
- What does deletion mean in an auditable knowledge system?

### Batch D — PKM and information science

Questions:

- What did Zettelkasten / evergreen notes learn about note granularity?
- What does Wikipedia know about redirects, disambiguation, stale pages, citation quality, and editorial conflict?
- When does hierarchy help vs hurt discovery?

### Batch E — Docs-as-code / database / software-maintenance analogies

Questions:

- What can we borrow from ADRs, schema migration, materialized views, CI, regression testing, incremental builds, garbage collection, and dependency graphs?

### Batch F — IDE + automation boundary

Do after semantics are better constrained but before production workflow is frozen.

---

## 13. Highest-priority hypotheses entering Batch B

### H1 — Derived knowledge must never become an irreversible compression boundary

We should retain a path back to primary evidence.

### H2 — Maintenance should be triggered by evidence of value/risk, not simply by elapsed time or every ingest

Candidate triggers include contradiction, retrieval failure, structural pressure, and user correction.

### H3 — Query behavior should generate maintenance signals

If the system fails to find known information, that is a knowledge-organization failure worth recording.

### H4 — High-risk edits need semantic regression checks

Split/merge, supersession, large rewrites, and policy changes are obvious candidates.

### H5 — The best automation boundary will be risk- and reversibility-sensitive

Deterministic/reversible operations can likely be more autonomous than epistemically consequential ones.

These hypotheses remain open until evidence and experiments justify ADRs.
