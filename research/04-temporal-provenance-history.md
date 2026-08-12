# Temporal Truth, Provenance, History, and Deletion — Research Batch C

Date: 2026-08-12
Status: research note, not policy
Related: Issue #9

## 1. Purpose

An LLM Wiki cannot safely treat knowledge as timeless text.

At least four different things can happen when a new source appears:

1. an earlier statement was **wrong** and is being corrected,
2. an earlier statement was **true then** but the world changed,
3. two sources **disagree** and no single truth is established,
4. the wiki's wording/organization changes while the underlying knowledge does not.

If these are represented by the same operation — "rewrite the page" — history, attribution, and trust can silently collapse.

This batch examines ideas from temporal databases, event sourcing, provenance standards, temporal agent memory, and claim-level source verification.

---

## 2. Bitemporal data — two clocks answer two different questions

Primary/authoritative references:

- Clifford & Isakowitz, *On the Semantics of Transaction Time and Valid Time in Bitemporal Databases* (1992): https://archive.nyu.edu/jspui/handle/2451/14356
- Shasha & Zhu, *SpyTime — a Performance Benchmark for Bitemporal Databases*: https://cs.nyu.edu/~shasha/spytime/spytime.html

A bitemporal model distinguishes:

- **valid time** — when a fact is effective/true in the modeled world,
- **transaction time** — when that fact/version is recorded as effective in the database.

For a personal wiki, a more intuitive vocabulary may eventually be:

```text
valid time      = when was this true?
recorded time   = when did my system learn/store this?
```

These are not always equal.

Example:

```text
2026-08-12: read a source stating that
"Project X used architecture A from Jan through May 2026."
```

Then:

```text
valid_from: 2026-01
valid_to:   2026-05
recorded_at: 2026-08-12
```

Without two clocks, the wiki may accidentally interpret a newly learned historical fact as a newly true fact.

### Personal-wiki implication

We should not immediately conclude that every note needs four temporal columns. The lesson is semantic:

> "When true?" and "When learned?" are distinct questions and may need distinct representation when temporal precision matters.

E003 should include delayed-discovery cases, not only sequential current-state updates.

---

## 3. Correction is not supersession

Consider two update chains.

### Case A — correction

```text
recorded at T1: CEO = Alice
later evidence: the T1 source was wrong; CEO was Bob all along
```

The system should be able to say:

- our earlier stored state was incorrect,
- reality did not change at the correction time.

### Case B — temporal change

```text
valid until T2: CEO = Alice
valid from T2: CEO = Bob
```

Both claims were valid in different intervals.

A single `updated_at` timestamp cannot distinguish these cases.

This distinction matters for personal beliefs too:

- "I used to prefer X, now I prefer Y" is temporal change,
- "I misremembered; I never preferred X" is correction.

Any future lifecycle model should preserve this semantic difference.

---

## 4. Event sourcing — current state can be a projection, not the only truth

Reference:

- Martin Fowler, *Event Sourcing*: https://martinfowler.com/eaaDev/EventSourcing.html

Event sourcing captures changes to application state as a sequence of events and reconstructs current or past state from that history.

The transferable idea for an LLM Wiki is not to adopt enterprise CQRS infrastructure. It is a separation of concerns:

```text
change / observation history
        |
        v
projection / materialized current view
        |
        v
"what do I currently know?"
```

This maps cleanly to our compiler model:

```text
raw observations / sources / corrections
               |
               v
         consolidation
               |
               v
        current wiki view
```

### Why this is attractive

A current synthesis can remain concise while historical changes stay recoverable elsewhere.

It also provides a conceptual answer to a recurring conflict:

- append-only history is useful for audit/reconstruction,
- current wiki prose should not become an unreadable changelog.

### Why this is dangerous if copied literally

Event sourcing assumes deterministic or sufficiently controlled projection logic. LLM consolidation is probabilistic and model-version-sensitive. Replaying the same history may not produce byte-identical or semantically identical current state.

Therefore, if we borrow the pattern, we likely need to preserve both:

- the durable inputs/change events,
- and important derived versions/diffs/checkpoints.

Do not assume "we can always regenerate the wiki later" unless reproducibility is demonstrated.

---

## 5. W3C PROV — provenance is richer than a citation URL

Primary standard:

- W3C PROV-O Recommendation: https://www.w3.org/TR/prov-o/
- W3C PROV Primer: https://www.w3.org/TR/prov-primer/

PROV models provenance around three core classes:

- **Entity** — something with fixed aspects,
- **Activity** — a process that uses/transforms/generates entities,
- **Agent** — something responsible for an activity/entity.

It also provides relations such as:

- `wasDerivedFrom`,
- `wasRevisionOf`,
- `hadPrimarySource`,
- `wasGeneratedBy`,
- `used`,
- attribution/responsibility relations.

### Important insight for our wiki

A source citation answers only:

> "What file/page is related to this statement?"

A richer provenance record can answer:

> "Was this quoted, summarized, inferred, revised, or generated from multiple sources? Which process/model/human produced this version?"

This is directly relevant to recursive contamination.

For example:

```text
raw source A
    |
    | primary source / used by
    v
consolidation activity
    |
    v
wiki version B
    |
    | revision
    v
wiki version C
```

If C later informs D, we can distinguish "D ultimately traces to A" from "D is merely repeating derived prose from C."

### Restraint

W3C PROV is a general interchange model and is much richer than a personal Markdown wiki needs. We should borrow semantics, not automatically adopt RDF/OWL or full provenance graphs.

A minimal subset may be enough:

```text
source_of_record
was_derived_from
was_revision_of
generated_by / model+prompt version (selectively)
reason_for_change
```

But even this should be cost-tested.

---

## 6. Version identity matters

The PROV primer explicitly treats revisions as new entities rather than pretending an evolving document has one timeless state.

This is useful for LLM-generated pages because provenance attached only to a pathname can become ambiguous:

```text
wiki/agent-memory.md
```

may mean different content on different dates.

Git already gives us content-addressed/versioned history. A future provenance design can likely exploit Git commit/blob identity rather than inventing a second version-control layer.

However, Git alone does not encode semantic relations such as:

- corrected because source was wrong,
- superseded because reality changed,
- rewritten only for organization,
- disputed because sources disagree.

So Git is likely necessary infrastructure but insufficient semantic metadata.

---

## 7. Source ownership is an independent factuality problem

Recent primary research:

- Alvarez et al., *ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents*: https://arxiv.org/abs/2606.18037

ProvenanceGuard focuses on **cross-source conflation**: a claim can be supported somewhere in pooled evidence while being attributed to the wrong source.

This matters in a wiki with multiple sources discussing similar facts.

Example:

```text
Source A: revenue = 100
Source B: headcount = 50
Wiki: "Source A reports revenue 100 and headcount 50."
```

Every fact may exist somewhere in retrieved context, yet the source ownership is wrong.

### Implication

"All claims are supported by the retrieved context" is weaker than:

> "Each claim is supported by the source it is attributed to."

For low-risk personal summaries this granularity may be excessive. For exact numbers, disputed claims, research conclusions, and decisions, it may be necessary.

E004 should therefore test not only citation presence but **claim-to-source correctness**.

---

## 8. Granular provenance can improve caution but also create cognitive burden

Recent study:

- Martin-Boyle et al., *PaperTrail: A Claim-Evidence Interface for Grounding Provenance in LLM-based Scholarly Q&A*: https://arxiv.org/abs/2602.21045

PaperTrail maps answer claims to evidence and exposes unsupported/omitted information. In a within-subject study with 26 researchers, the richer interface lowered participants' trust in LLM output, but the increased caution did not necessarily translate into changed behavior; verification remained cognitively burdensome.

### Important automation lesson

More provenance is not automatically more usable trust.

If every sentence in a personal wiki demands manual evidence inspection, the user may stop reviewing it.

Therefore provenance design must optimize two different properties:

1. **machine-auditable traceability**,
2. **human verification ergonomics**.

A likely direction is progressive disclosure:

```text
normal reading: concise synthesis
on uncertainty/high impact: claim-level evidence
on audit: full derivation/history
```

This remains a hypothesis.

---

## 9. Temporal graph memory is one implementation, not the semantic requirement

Primary source:

- Rasmussen et al., *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*: https://arxiv.org/abs/2501.13956

Zep/Graphiti represents evolving agent memory in a temporal knowledge graph and retains historical relationships as new information arrives.

The transferable lesson is that temporal relationships and invalidation can be explicit first-class structures.

The non-transferable assumption is that a graph database is required. A Markdown/Git system could encode similar semantics much more simply at personal scale.

Batch C therefore treats temporal graph memory as evidence for the **problem**, not as a selected solution.

---

## 10. Four histories we should not conflate

A mature personal Wiki may need to distinguish:

### H1 — Source history

What did the original source say, and which source version did we ingest?

### H2 — World/fact history

When was a statement true in the external/personal reality?

### H3 — Knowledge-state history

What did our wiki believe/represent at a given time?

### H4 — Artifact/edit history

How did the markdown/files change structurally?

Git handles H4 extremely well and can partially support H1/H3.

It does **not automatically solve H2**, and it does not explain the semantic relationship between versions.

This four-history distinction should be used when designing E003.

---

## 11. Deletion is not one operation

Our lifecycle vocabulary needs semantic precision before automation.

Candidate operations:

### Hard delete

Remove content/evidence/history from the active repository.

Appropriate when true erasure is required, but destructive and potentially incompatible with reconstruction.

### Archive

Retain content but exclude it from normal active retrieval.

Useful for low-value or obsolete material where history still matters.

### Supersede

Keep the old statement as historically meaningful but mark a newer state as current.

Appropriate for change over time.

### Correct / invalidate

Keep evidence that the old wiki state existed, but mark the old claim as erroneous rather than historically true.

### Tombstone

Retain a marker that something existed/was intentionally removed without keeping the original active content.

### Redirect

Replace an organizational identity/path while preserving navigation to the new canonical location.

### Remove from derived view

Delete a statement from current synthesis while leaving its raw source and historical edit record intact.

These operations have different effects on retrieval, provenance, privacy, and auditability. A single `/delete` automation would be dangerously underspecified.

---

## 12. A candidate semantic update model

Not a production schema — just a testable mental model.

For a knowledge statement/claim, distinguish:

```text
content
source(s)
recorded_at
valid_from / valid_to   (only where meaningful)
status:
  current
  superseded
  disputed
  invalidated
  archived
relation:
  derived_from
  revision_of
  supersedes
change_reason
```

Important: most ordinary wiki prose probably should **not** expose all fields inline. The experiment should determine which metadata is worth persisting and at what granularity.

---

## 13. Minimal temporal experiment matrix for E003

E003 should now include at least these update chains:

| Scenario | Old statement | New evidence | Correct semantic outcome |
|---|---|---|---|
| actual change | A true until T | B true from T | preserve A historically, B current |
| correction | A recorded | evidence shows A never true | invalidate A, do not invent a validity interval |
| late discovery | learn today that A was true last year | historical source | recorded time != valid time |
| disagreement | source A says X, B says Y | neither resolved | both evidence paths retained, current state disputed |
| refinement | X | X + precise detail | same core fact, revision/augmentation |
| reorganization | page moved/split | no semantic change | artifact history only; no fake fact change |
| personal preference change | prefer A | now prefer B | temporal personal state |
| decision reversal | chose A for reason R | later choose B | preserve both decision contexts/reasons |

Compare:

1. overwrite-latest,
2. append-only chronology,
3. status/supersession model,
4. two-clock validity + recording model for applicable claims.

Measure current answers, historical answers, false contradictions, lost history, metadata burden, token cost, and human comprehensibility.

---

## 14. Provenance experiment refinements for E004

Compare at least:

1. page-level source list,
2. section-level source mapping,
3. selective claim-level provenance for high-risk facts,
4. claim-level provenance everywhere.

Add tests for:

- correct fact attributed to wrong source,
- claim synthesized from multiple sources,
- raw source vs derived wiki source,
- page rewritten while citations remain stale,
- source version changes,
- exact number/date verification,
- human time needed to audit a claim.

The expected optimum may be **risk-adaptive provenance**, not maximum provenance.

---

## 15. Relationship to automation boundary

Temporal/provenance semantics directly influence what can be safely automated.

Potentially low-risk:

- attach recorded timestamp,
- preserve source identifier,
- create Git diff,
- update deterministic link/index metadata.

Potentially high-risk:

- decide that old claim is false vs merely superseded,
- infer validity intervals from vague prose,
- merge conflicting sources into one canonical statement,
- hard-delete source history,
- reassign claim provenance after synthesis.

This suggests automation authority should depend on **semantic consequence**, not just file operation type.

A one-line edit can be epistemically more dangerous than moving ten files.

---

## 16. Strongest conclusions from Batch C — hypotheses only

1. **Two clocks are conceptually necessary even if we do not store both for every fact.** "When true" and "when learned" are different.
2. **Current synthesis should probably be a projection over more durable evidence/change history, not the only retained state.**
3. **Git is necessary but semantically incomplete.** It tracks artifact versions, not why truth changed.
4. **Provenance must distinguish derivation and source ownership, not merely attach bibliography links.**
5. **Maximum provenance can create human verification fatigue.** Risk-adaptive/progressive disclosure deserves testing.
6. **Deletion must be decomposed into semantic operations before any autonomous delete workflow exists.**
7. **Correction, supersession, disagreement, and reorganization must be separate test cases.**

None are adopted policies.

---

## 17. Next dependency

The next research batch should examine **PKM, Wikipedia/information science, and knowledge organization**.

Why now: we have increasingly strong semantics for evidence and change, but still do not know the right human-readable knowledge unit, linking style, taxonomy depth, or maintenance ergonomics. PKM and collaborative encyclopedic systems have decades of practical experience with granularity, redirects, disambiguation, citation norms, stale pages, and editorial conflict.

## 18. Sources

- Clifford & Isakowitz, *On the Semantics of Transaction Time and Valid Time in Bitemporal Databases*: https://archive.nyu.edu/jspui/handle/2451/14356
- Shasha & Zhu, *SpyTime — a Performance Benchmark for Bitemporal Databases*: https://cs.nyu.edu/~shasha/spytime/spytime.html
- Martin Fowler, *Event Sourcing*: https://martinfowler.com/eaaDev/EventSourcing.html
- W3C, *PROV-O: The PROV Ontology*: https://www.w3.org/TR/prov-o/
- W3C, *PROV Model Primer*: https://www.w3.org/TR/prov-primer/
- Rasmussen et al., *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*: https://arxiv.org/abs/2501.13956
- Alvarez et al., *ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents*: https://arxiv.org/abs/2606.18037
- Martin-Boyle et al., *PaperTrail: A Claim-Evidence Interface for Grounding Provenance in LLM-based Scholarly Q&A*: https://arxiv.org/abs/2602.21045
