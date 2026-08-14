# Alpha Core Readiness Gate

Status: **active convergence rule**

Date: 2026-08-14

## Why this document exists

The project must not trade rigor for schedule, but it also must not turn every interesting research question into a prerequisite for using an LLM Wiki.

This document defines the smallest **trustworthy raw-first Alpha core** and separates:

1. implementation blockers that must be closed before calling the core Alpha-ready;
2. evidence gates that require real dogfood data and therefore must run while Alpha is used;
3. post-Alpha research that is explicitly forbidden from delaying Alpha absent a newly observed blocker.

The Alpha definition is architecture-neutral. A persistent compiled provider is **not required** to call the raw-first core Alpha-ready; compiled state remains disabled until realistic reuse evidence earns activation.

## Alpha Core definition

Alpha Core means the system can safely support this loop:

```text
immutable raw evidence
    -> verified evidence identity/current-history
    -> deterministic retrieval
    -> provenance-preserving context
    -> read-only LLM answer
    -> exact source navigation/audit
```

while preserving enough temporal/history information that later updates do not silently rewrite what earlier evidence said.

It does **not** mean the final UI is stable, all automation exists, or persistent synthesis has been justified.

## Required Alpha invariants

### A. Raw authority and content integrity — READY

Evidence:

- immutable content-addressed raw objects;
- content/evidence identity separation (ADR-0004);
- verified raw-byte reads before semantic use (ADR-0007);
- read-only aggregate raw-integrity audit;
- corruption/missing/invalid identity fails closed.

### B. Evidence revision identity and current/history — READY

Evidence:

- opaque evidence revision IDs;
- optional explicit origin identity;
- append-only topic-scoped current/history lineage;
- A -> B -> A recurrence without rewriting raw history (ADR-0003/0004).

### C. Minimum temporal/epistemic semantics — READY

Evidence:

- explicit generic replacement;
- correction;
- change with separate effective/recorded instants;
- unresolved current-revision dispute with no hidden winner;
- contest metadata reaches answer boundary without changing retrieval ranking (ADR-0005 / E003 20/20).

### D. Retrieval floor with exact provenance — READY

Evidence:

- default object-level BM25 remains stable;
- E014-R1 confirmed structural rank-then-expand as a lower-cost candidate;
- X1 remains shadow/non-default pending realistic E015 evidence;
- identical immutable bytes are one lexical object regardless of provenance multiplicity;
- returned context preserves raw source revision IDs.

Alpha does not require promoting X1 over W0.

### E. Local precise provenance capability — READY

Evidence:

- E004 Gate A passed;
- optional exact `[source revision, character span]` pointer exists;
- deterministic raw-byte reversibility;
- historical pointer does not auto-follow a successor;
- no claim graph / automatic provenance inference (ADR-0006).

Alpha does not require collecting exact provenance universally.

### F. Read-only answer boundary — READY

Evidence:

- explicit model opt-in;
- raw evidence is authoritative;
- no canonical mutation from answer generation;
- identical-byte source multiplicity is not treated as corroboration;
- unresolved dispute cannot be silently collapsed into consensus.

### G. Canonical append-log torn-tail/crash containment — **LAST IMPLEMENTATION BLOCKER**

Current risk:

- `manifest.jsonl` is the canonical source/current-history/temporal event log;
- `provenance.jsonl` is an append-only exact-pointer log;
- current writers/readers do not yet define a tested contract for a process/power failure that leaves a partially written final JSONL record.

Alpha requires a minimal failure-containment floor:

- deterministic detection of incomplete/corrupt log records;
- no silent acceptance of a partial event;
- no automatic semantic repair or invented event;
- safe distinction between a torn **final append** and corruption inside the durable prefix;
- read-only aggregate integrity status suitable for Doctor later;
- valid legacy/current logs must replay identically;
- no signed-log, consensus, database, or transaction framework unless this minimal path fails.

This is the final planned infrastructure blocker before declaring **Alpha Core Ready**.

## Realistic evidence gates that run during Alpha, not before it

### E013 — revisit/update/query-mix calibration

Still required before enabling any durable compiled provider.

Alpha must be usable while these real workload observations accumulate. If reuse/update economics do not occur naturally, compiled state stays disabled.

### E015 — W0 vs structural-expand shadow calibration

Still required before changing default retrieval.

Alpha may keep W0 visible/default while X1 is measured in zero-extra-model-call shadow.

### Exact-provenance realistic burden

E004 demonstrated mechanism value but also large D1 rewrite/reattachment burden. The local provenance pointer should be exercised only where naturally useful; do not add a rebind/current-claim layer before dogfood shows a concrete need.

## Explicitly not Alpha blockers

Unless real dogfood exposes one as a blocker, the following must **not** delay Alpha:

- global claim graph;
- vector database / embeddings;
- graph database / RDF / OWL;
- full bitemporal/as-of engine;
- future scheduled temporal transitions;
- automatic contradiction/relation detection;
- LLM provenance repair;
- verifier/regression stack for compiled Wiki edits;
- taxonomy split/merge automation;
- schema evolution machinery;
- persistent synthesis maintenance classes;
- autonomous canonical mutation;
- VS Code design polish / sidebar / final UX;
- VS Code-native LM API replacement for the already-working Copilot CLI adapter.

## Persistent compiled Wiki boundary

Persistent compilation is a **data-gated Alpha evolution**, not an infrastructure prerequisite.

E011/E012 established a credible controlled mechanism/economic region, especially around repeated synthesis/decision understanding and reuse >= roughly three revisits per authoritative update in the frozen maintenance benchmark.

That does not authorize default activation.

Promotion still requires E013 realistic evidence that such a high-reuse region occurs materially in natural use. Exact/provenance-heavy workloads remain raw-first/raw-backed even if compilation later activates elsewhere.

## Convergence rule after blocker G

Once canonical append-log torn-tail/crash containment is green and merged:

> **Declare Alpha Core Ready and stop adding core infrastructure by default.**

After that point, new core work must be justified by one of:

1. an actual dogfood failure/blocker;
2. E013/E015 realistic evidence crossing a preregistered decision boundary;
3. a reproducible data-loss/trust failure in an existing Alpha invariant.

“Interesting architecture”, “might be useful later”, or “would make the Wiki more sophisticated” are not sufficient reasons.

This rule is intentionally stronger than the normal research backlog. It exists to ensure rigor converges into a usable LLM Wiki rather than becoming an endless prerequisite chain.
