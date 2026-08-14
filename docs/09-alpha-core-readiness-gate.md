# Alpha Core Readiness Gate

Status: **ALPHA CORE READY — convergence rule active**

Date: 2026-08-14

## Alpha Core Ready declaration

The final planned Alpha infrastructure blocker is closed by ADR-0008 / #51 / #52.

The raw-first core is therefore **Alpha Core Ready**.

This is a readiness declaration for the trustworthy core loop, not a claim that the product, UI, retrieval policy, or persistent compiled Wiki is finished.

From this point forward, the convergence rule is active:

> **Stop adding core infrastructure by default.**

New core work must be justified by an actual dogfood failure, a preregistered realistic-evidence boundary crossing, or a reproducible data-loss/trust failure in an existing Alpha invariant.

## Why this document exists

The project must not trade rigor for schedule, but it also must not turn every interesting research question into a prerequisite for using an LLM Wiki.

This document defines the smallest **trustworthy raw-first Alpha core** and separates:

1. implementation blockers that had to be closed before calling the core Alpha-ready;
2. evidence gates that require real dogfood data and therefore run while Alpha is used;
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

### G. Canonical append-log torn-tail/crash containment — READY

Evidence:

- `manifest.jsonl` and `provenance.jsonl` share one strict canonical JSONL contract (ADR-0008);
- only newline-terminated JSON-object records are replayable;
- a non-empty final tail is detected as `torn_tail`, even if it is syntactically valid JSON;
- invalid UTF-8, invalid JSON, or non-object committed records are detected as `corrupt_prefix`;
- semantic replay fails closed on either class and performs no automatic repair/truncation;
- writers refuse to append onto a damaged log, use `O_APPEND`, terminate records with LF, and request `fsync`;
- read-only aggregate canonical-log audit exposes status/counts only;
- legacy blank-line/source replay remains compatible;
- PR #52 pre-documentation implementation head passed **94/94 Python tests**, CLI smoke, development VS Code Extension Host **4/4**, bundled core, packaged VSIX Extension Host **4/4**, and frozen E004/E014/E014-R1 validations;
- model calls / AI credits: **0 / 0**.

The implementation intentionally does not claim multi-writer transactions, hostile-tamper resistance, automatic recovery, or database-grade cross-file atomicity.

## Realistic evidence gates that run during Alpha, not before it

### E013 — revisit/update/query-mix calibration

Still required before enabling any durable compiled provider.

Alpha must be usable while these real workload observations accumulate. If reuse/update economics do not occur naturally, compiled state stays disabled.

### E015 — W0 vs structural-expand shadow calibration

Still required before changing default retrieval.

Alpha keeps W0 visible/default while X1 is measured in zero-extra-model-call shadow.

### Exact-provenance realistic burden

E004 demonstrated mechanism value but also large D1 rewrite/reattachment burden. The local provenance pointer should be exercised only where naturally useful; do not add a rebind/current-claim layer before dogfood shows a concrete need.

## Explicitly not Alpha blockers

Unless real dogfood exposes one as a blocker, the following must **not** trigger another prerequisite chain before Alpha use:

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

## Active convergence rule

Alpha Core Ready is now the baseline, not a reason to invent another infrastructure checklist.

Further core work requires at least one of:

1. an actual dogfood failure/blocker;
2. E013/E015 realistic evidence crossing a preregistered decision boundary;
3. a reproducible data-loss/trust failure in an existing Alpha invariant.

“Interesting architecture”, “might be useful later”, or “would make the Wiki more sophisticated” are not sufficient reasons.

Research may continue, but it must either test a concrete decision boundary or remain explicitly post-Alpha. This rule exists to ensure rigor converges into a usable LLM Wiki rather than becoming an endless prerequisite chain.
