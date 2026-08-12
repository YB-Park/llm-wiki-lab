# Software and Database Maintenance Patterns — Research Batch E

Date: 2026-08-12
Status: research note, not policy
Related: Issue #11

## 1. Purpose

Earlier batches suggest that an LLM Wiki is a continuously maintained derived knowledge system rather than a folder of summaries.

Software engineering and databases have mature concepts for similar operational problems:

- derived state becoming stale,
- expensive recomputation,
- dependency-aware updates,
- preserving versions,
- testing transformations before accepting them,
- migrating structure without breaking references,
- and recording why important decisions were made.

This batch extracts those patterns without assuming we need a database server or complex build system.

---

## 2. Materialized views — the strongest operational analogy so far

Primary reference:

- PostgreSQL materialized views: https://www.postgresql.org/docs/current/rules-materializedviews.html
- PostgreSQL `REFRESH MATERIALIZED VIEW`: https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html

A materialized view stores the result of a derivation/query so reads are cheap, while the underlying definition/source remains separate. When source data changes, the stored view can become stale and needs refresh.

This maps surprisingly well to the LLM Wiki:

```text
authoritative evidence / observations
               |
               | semantic derivation
               v
        materialized knowledge view
               |
               v
         cheap human/agent reads
```

### Key consequence

If the wiki is a materialized view, then "wiki freshness" is not binary. A view can be:

- current enough for a query,
- known stale,
- partially affected by new evidence,
- expensive to refresh relative to its expected value.

This reframes maintenance from:

> "Always keep every page perfectly up to date"

into:

> "Refresh derived knowledge when the expected benefit/risk justifies recomputation."

That connects directly to E002, Issue #8, and the automation/token-cost research axis.

### Important difference

Database views have deterministic definitions. Our semantic compiler is probabilistic and context-sensitive. Therefore a wiki refresh can introduce regression even when the inputs are unchanged or only slightly changed.

Unlike a SQL materialized view, **refresh itself must be tested**.

---

## 3. Full refresh vs incremental maintenance

A naive LLM Wiki can do this:

```text
new source
  -> reread all related sources
  -> rewrite whole topic
  -> update all summaries/links
```

That is analogous to full recomputation.

At larger scale, a more economical approach may track dependencies:

```text
source S changed/added
      |
      v
which claims/pages depend on S?
      |
      v
mark only affected artifacts dirty
      |
      v
recompute/verify selectively
```

### Why provenance and cost are linked

Provenance is usually discussed as trust metadata. But dependency-aware maintenance gives it a second purpose:

> provenance tells us what might need rebuilding when evidence changes.

If a page has no machine-readable relationship to its evidence, the safest maintenance action may require expensive global search/reasoning.

This creates a real trade-off for E004:

- more provenance metadata costs more to create,
- but it may reduce future recomputation scope.

The correct cost calculation must therefore be lifecycle-wide.

---

## 4. "Dirty" state may be better than automatic refresh

Build/database systems commonly distinguish source change from completed recomputation.

A personal wiki could use an analogous intermediate state:

```text
new source arrives
      -> affected page identified
      -> page marked needs_reconsolidation
      -> old page remains readable
      -> refresh occurs when triggered/approved
```

This is important because LLM maintenance is expensive and uncertain.

It also aligns with Wikipedia-style maintenance tags from Batch D: **detecting work and executing work are different operations.**

Potential triggers later to test:

- user opens/queries the affected topic,
- contradiction detected,
- enough observations accumulate,
- explicit maintenance command,
- high-impact decision depends on it,
- low-cost background opportunity exists.

Do not adopt any trigger yet.

---

## 5. Dependency graphs do not require a graph database

A common architecture mistake would be:

> "We need dependency relationships, therefore we need Neo4j/GraphRAG."

Not necessarily.

At personal scale, dependencies might be represented by simple metadata/index files:

```text
page A <- source 1, source 3
page B <- source 2
summary C <- page A, page B
```

or generated deterministically by scanning source references.

The graph is a **logical relationship**, not a storage-engine requirement.

This principle should apply throughout the project: specify semantics first, choose infrastructure later.

---

## 6. Git gives artifact identity and cheap rollback

Primary reference:

- *Pro Git*, Git Objects: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

Git is fundamentally content-addressable: stored content receives an identity based on its contents. Commits/trees/blobs give us stable version references and history essentially for free because the system already lives in a repository.

For our wiki this provides:

- versioned raw/source snapshots where stored locally,
- exact identity of derived document versions,
- diffs before human acceptance,
- rollback after a harmful maintenance operation,
- reproducible references to "which page version did this decision use?"

### What Git does not give

Git cannot tell us by itself:

- whether a removed sentence was intentionally superseded or accidentally dropped,
- whether two files contain the same semantic claim,
- which source actually supports a claim,
- whether a rewrite degraded question answering,
- whether a commit changed world-state semantics or only formatting.

Therefore Git should be treated as the **artifact history substrate**, not the complete knowledge model.

---

## 7. Knowledge maintenance should resemble CI more than silent autosave

Software systems do not generally trust an arbitrary transformation merely because it produced syntactically valid files. Changes can pass through checks before being accepted.

Our Batch A–C findings suggest a potential wiki maintenance pipeline:

```text
proposed semantic edit
       |
       +-- structural lint
       +-- provenance/grounding checks
       +-- transition verification
       +-- targeted regression queries
       +-- cost/risk gate
       |
       v
accept / request review / reject
```

### Deterministic-first principle

Checks that do not require an LLM should preferably remain deterministic:

- broken links,
- source existence,
- duplicate IDs,
- redirect loops,
- malformed timestamps/status values,
- changed file scope,
- exact literal checks where appropriate.

Use expensive probabilistic verification only for genuinely semantic questions.

This directly supports the user's automation-cost concern.

---

## 8. High-impact wiki edits resemble migrations

Operations such as:

- split,
- merge,
- rename,
- re-parent,
- change canonical page identity,
- change metadata/schema,

can affect many dependent artifacts.

Treating them as ordinary free-form edits is risky.

A migration-like workflow may eventually be:

```text
proposal
  -> affected-artifact discovery
  -> dry-run / preview
  -> redirects or compatibility mapping
  -> transformation
  -> structural checks
  -> semantic regression suite
  -> commit with rationale
```

This is particularly suitable for VS Code because the proposed change can be inspected as an ordinary Git diff.

### Automation boundary implication

The LLM might safely *propose* a migration much earlier than it can safely *execute and finalize* one autonomously.

This supports separating `suggest` from `mutate` as distinct capabilities.

---

## 9. Architecture Decision Records — decisions are durable knowledge of a special kind

References:

- ADR organization: https://adr.github.io/
- AWS ADR process: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html
- UK Government ADR Framework: https://www.gov.uk/government/publications/architectural-decision-record-framework

ADRs capture a significant decision along with its context and consequences. The Nygard-style structure is intentionally compact: status, context, decision, consequences.

Our lab already uses ADRs because they solve a problem that ordinary wiki prose does not:

> preserving **why** a choice was made at a particular time.

### Why decisions should not be ordinary mutable wiki facts

A decision can later be superseded without having been "wrong."

Example:

```text
ADR-0007: Use source-file-level provenance for MVP
reason: claim-level cost too high under E004

later:
ADR-0015: Adopt selective claim-level provenance for high-risk claims
reason: experiment shows acceptable overhead
```

Rewriting ADR-0007 to contain today's answer would destroy the historical reasoning.

This is the same semantic distinction Batch C found between current state and history.

### Documentation overhead matters

Recent empirical work comparing ADR templates reports a trade-off between concise/easy-to-adopt formats and more detailed structured formats. This is consistent with our broader principle: a documentation policy that is theoretically complete but too expensive to maintain will fail operationally.

Our current lightweight ADR approach is therefore reasonable research infrastructure, but we should still keep individual ADRs small.

---

## 10. The build-system analogy: invalidation may matter more than generation

In generated systems, one of the hardest questions is not "how do I build this artifact?" but:

> "What became invalid when this input changed?"

For an LLM Wiki, that question is even harder because dependencies can be semantic rather than explicit.

Example:

```text
Source S changes a benchmark result.

Directly affected:
  benchmark-page.md

Potentially affected:
  model-comparison.md
  decision-use-model-x.md
  overview.md
```

A future maintenance system may need multiple dependency levels:

- explicit citation dependency,
- explicit summary/parent dependency,
- explicit decision dependency,
- semantic/search-discovered possible dependency.

The last category is uncertain and expensive. It may be suitable for periodic audit rather than automatic cascade rewrite.

---

## 11. Canonical state vs generated presentation

Database and build analogies reinforce a distinction surfaced in Batch D.

Some artifacts can be canonical; others can be derived presentations.

Possible future model:

```text
Evidence / observations        <- authoritative inputs
Claim/topic knowledge state    <- canonical derived semantic state?
Overview/index/excerpts         <- generated materialized presentations
Query answers                   <- ephemeral projections
```

But this introduces a major open question:

> What is the smallest canonical derived state we actually need to persist?

If we persist too little, every query becomes expensive recomputation.
If we persist too much, consistency/maintenance cost explodes.

This is central to E001, E002, E006, and Issue #8.

---

## 12. A proposed three-tier verification model for experiments

Not policy. A useful experimental framework:

### Tier A — deterministic integrity

Cheap, always runnable:

- syntax/schema,
- broken links,
- source/redirect existence,
- IDs/aliases,
- allowed status transitions,
- exact literal checks,
- dependency bookkeeping.

### Tier B — semantic transition safety

LLM-assisted/selective:

- coverage,
- preservation,
- faithfulness,
- contradiction classification,
- temporal semantic correctness.

### Tier C — downstream behavioral regression

Query/probe based:

- known answerable questions still work,
- exact facts preserved,
- historical queries still work,
- unrelated areas did not degrade,
- prior user-corrected failures do not recur.

A high-impact change might require A+B+C; a low-risk metadata fix might require only A.

This creates a concrete bridge between risk-tiered automation and token efficiency.

---

## 13. Refresh policy as an economic decision

Materialized-view thinking suggests a useful future decision function.

A refresh is attractive when:

```text
expected cost of stale knowledge / query-time rediscovery
>
expected refresh cost + regression risk + review cost
```

We cannot measure this exactly, but the framing is valuable.

It prevents two extremes:

- never consolidate anything,
- continuously spend tokens perfecting pages nobody queries.

Potential observable proxies:

- query frequency for topic,
- number/value of pending observations,
- contradiction severity,
- downstream decision dependency,
- age of current synthesis,
- historical retrieval failures,
- estimated token cost.

These can later inform Issue #8 and the IDE automation study.

---

## 14. Phase 1 architectural patterns now visible across fields

After Batches A–E, several patterns recur independently:

### P1 — Source-of-record / derived-view separation

Appears in LLM Wiki implementations, provenance standards, event sourcing, materialized views, and Wikipedia source discipline.

### P2 — Capture / consolidate separation

Appears in agent memory systems, database refresh concepts, and practical ingest triage.

### P3 — Progressive disclosure

Appears in Wiki summary style, agentic retrieval, memory tiers, raw fallback, and hierarchical navigation.

### P4 — Preserve recoverability

Appears in immutable raw, Git, event history, temporal memory, redirects, and append-oriented failure history.

### P5 — Test transformations

Appears in WiCER probes, TRUSTMEM transition verification, WikiLoop regression guards, CI analogy, and Wikipedia verification/maintenance mechanisms.

### P6 — Selective maintenance

Appears in LeanMem, materialized-view refresh economics, maintenance tags, and risk-tiered automation.

### P7 — Structure evolves

Appears in WikiKV, Zettelkasten, Wikipedia split/merge/redirect, and schema migration practices.

### P8 — Uncertainty is a legitimate state

Appears in disputed/ambiguous/citation-needed states, contradiction handling, and human-review gates.

The fact that these patterns arise from different domains increases their value as experiment hypotheses, but convergence still does not make them automatic production policy.

---

## 15. What we should test first after the research landscape

The research now suggests a tighter experiment sequence than the original list.

### Experiment Group 1 — Can derived knowledge be trusted at all?

- long-horizon contamination (E007),
- blind compilation loss / diagnostic repair (Issue #3),
- transition verification (Issue #7).

### Experiment Group 2 — What should be persisted and maintained?

- knowledge unit / representation × retrieval (E001 + E006),
- immediate vs staged/selective consolidation (E002 + Issue #8),
- provenance granularity/source ownership (E004).

### Experiment Group 3 — Can it survive change?

- temporal semantics (E003),
- split/merge/schema migration (E005 + Issue #5),
- downstream regression of edits (Issue #4).

### Experiment Group 4 — Can a human actually live with it?

- risk-tier review (E009),
- VS Code/Copilot workflow and lifecycle token cost (E010 + automation-boundary study).

This sequence reduces the risk of optimizing UX for an unreliable semantic core.

---

## 16. Strongest conclusions from Batch E — hypotheses only

1. **The materialized-view model is currently our strongest operational mental model for the wiki.**
2. **Provenance may pay for itself partly by enabling dependency-aware selective maintenance, not only by increasing trust.**
3. **A changed input should be able to mark knowledge dirty without forcing immediate LLM rewrite.**
4. **Semantic maintenance should be deterministic-first and risk-tiered.**
5. **High-impact structural edits should behave like migrations with preview, compatibility, tests, and rollback.**
6. **Git is an excellent artifact-history substrate but not a semantic truth model.**
7. **Current knowledge, historical decisions, and generated presentation should not all share the same mutation semantics.**
8. **The right refresh policy is an economic/risk optimization problem, not merely a freshness schedule.**

No architecture decision is adopted by these conclusions.

## 17. Sources

- PostgreSQL, Materialized Views: https://www.postgresql.org/docs/current/rules-materializedviews.html
- PostgreSQL, REFRESH MATERIALIZED VIEW: https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html
- *Pro Git*, Git Objects: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
- ADR organization/resources: https://adr.github.io/
- AWS Prescriptive Guidance, ADR process: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html
- UK Government, Architectural Decision Record Framework: https://www.gov.uk/government/publications/architectural-decision-record-framework
- Nogueira et al., *One Size Fits All? An Empirical Comparison of ADR Templates regarding Comprehension, Usability, and Ease of Adoption*: https://arxiv.org/abs/2604.27333
