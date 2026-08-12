# Corpus C v0 — Controlled Synthetic Knowledge Base

Status: **FROZEN DESIGN v0 before any E007 LLM run**
Date: 2026-08-12

## Purpose

Corpus C v0 is a deliberately synthetic and adversarial knowledge stream for E007.

It is not meant to look like a perfectly realistic personal vault. It is designed to make failure mechanically observable before we move to Realistic Corpus R.

All organizations, projects, people, benchmark values, and events in this corpus are fictional.

## Fixed size

- 6 waves: W0–W5
- 18 source documents: exactly 3 per wave
- 30 scored queries
- query classes: local/exact, global/synthesis, multi-hop, temporal, provenance, negative/uncertainty/delayed

No source/query/fact should be modified after the first scored model run. Any new failure case becomes Corpus C v1 or a holdout extension.

## Files

- `manifest.json` — wave and source manifest
- `sources.jsonl` — model-visible synthetic source documents
- `ground-truth.json` — evaluator-only fact/lifecycle truth
- `queries.json` — fixed scored queries and rubrics

## Model visibility

During wiki ingest/maintenance, the model may receive source documents and ordinary source metadata.

It must **not** receive:

- `ground-truth.json`,
- query rubrics,
- injected-fault metadata,
- labels such as "this is a correction trap" or "this is a delayed probe".

## Design features

The corpus contains:

1. **exact facts** — dates, numbers, flags, format strings,
2. **near-duplicate entities** — Aster vs Astra; Northstar Systems vs Northstar Research,
3. **temporal changes** — SQLite -> PostgreSQL, Orchid-2 -> Orchid-3, TTL 30 -> 10 minutes,
4. **correction** — a January latency value later shown to have been wrong rather than changed,
5. **unresolved disagreement** — partner and internal reports disagree on the same build/test latency,
6. **long-range dependency** — a later design decision depends on facts introduced in earlier waves,
7. **source-ownership trap** — similar benchmark numbers belong to different projects/sources,
8. **unsupported inference trap** — plausible benefit of a design change is never evidenced,
9. **delayed probes** — obscure W0 facts are not queried until after W5,
10. **structural evolution** — Aster becomes Aurora and later separates into Retrieval/Ingest components,
11. **distractors** — lexically similar but unrelated material.

## Knowledge-time rule

Evaluation distinguishes:

- what sources are available by a given wave,
- what those sources assert,
- what later sources correct or supersede.

A system is not penalized for failing to know future evidence. It **is** penalized after correction/supersession evidence becomes available if it continues to expose an invalid current state without uncertainty/history semantics appropriate to the query.

## Baseline use

The same source stream and query suite must be used by all E007 conditions.

For C0 raw/search control, no durable semantic wiki is built.
For C1–C4, the derived state may vary by condition, but the source-of-record corpus remains identical.
