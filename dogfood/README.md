# Dogfood v0 — raw/retrieval/provenance shell

This is the earliest usable surface of the project. It is intentionally architecture-neutral while the persistent-compilation evidence program is still running.

## What is real in v0

- immutable, content-addressed raw evidence copies;
- stable source IDs derived from SHA-256;
- append-only ingest history;
- deterministic local BM25 retrieval;
- optional explicit local topic scopes;
- provenance-preserving context rendering;
- an optional read-only Copilot answer adapter behind explicit opt-in;
- privacy-preserving E013 workload calibration with aggregate-only export;
- zero hidden model calls and zero automatic upload.

The durable/compiled knowledge layer is **disabled by default**. E013 realistic-workload evidence decides whether and where that layer earns even shadow/opt-in activation.

## Quick start

From the repository root:

```bash
python3 -m dogfood.llm_wiki.cli init
python3 -m dogfood.llm_wiki.cli ingest notes/a.md notes/b.md
python3 -m dogfood.llm_wiki.cli search "why did we choose the cache design"
python3 -m dogfood.llm_wiki.cli context "why did we choose the cache design"
python3 -m dogfood.llm_wiki.cli history
```

The default local workspace is `.wiki-lab/` and is git-ignored. Override it with `--root` on any command.

## E013 realistic workload calibration

Calibration is explicit. Activity is logged only when you supply a local topic. Topic labels remain in the local registry; telemetry events store only opaque topic IDs and never store raw query text, document text, answer text, filenames, source IDs, hashes, or environment metadata.

Create a topic and associate evidence:

```bash
python3 -m dogfood.llm_wiki.cli topic add "cache architecture"

python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  notes/cache-decision.md notes/cache-constraints.md
```

The first topic-associated ingest starts the baseline maintenance cycle. Ordinary later ingests add evidence but do not create fake update cycles. When the authoritative knowledge really changes, mark that explicitly:

```bash
python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  --authoritative-update \
  notes/cache-decision-v2.md
```

Tag query class when it is easy to do so:

```bash
python3 -m dogfood.llm_wiki.cli search \
  "what was the exact approved cache limit?" \
  --topic "cache architecture" \
  --class exact_provenance

python3 -m dogfood.llm_wiki.cli context \
  "why did we choose this cache design?" \
  --topic "cache architecture" \
  --class decision_history
```

Available explicit classes are `exact_provenance`, `synthesis`, `decision_history`, and `other`. Omitting `--class` records the event as unknown rather than guessing with a model.

`search -> context -> ask` within the same topic consultation does **not** count as three revisits. E013 sessionizes query-like activity into one topic visit while consecutive query events remain within 30 minutes. A gap greater than 30 minutes starts another visit. This rule was preregistered before workload collection.

If you open raw evidence through the CLI, that becomes a local provenance-follow event:

```bash
python3 -m dogfood.llm_wiki.cli source show src-0123456789abcdef \
  --topic "cache architecture"
```

Optional fixed-code feedback can also be logged without free text:

```bash
python3 -m dogfood.llm_wiki.cli feedback helpful \
  --topic "cache architecture" \
  --reason found_source
```

Generate the only artifact suitable for sharing back into the research conversation:

```bash
python3 -m dogfood.llm_wiki.cli calibration export
```

The sanitized export contains only aggregate counts, distributions, fractions, concentration measures, and a data-sufficiency status. It deliberately emits no topic IDs or labels, raw timestamps, queries, filenames, source IDs, hashes, paths, or document/answer content.

Until the preregistered minima are met (10 topics with query activity, 20 completed maintenance cycles, 30 sessionized visits), the exporter returns `INSUFFICIENT_CALIBRATION_DATA` regardless of attractive point estimates.

## Optional model-backed answer

`ask` is deliberately harder to invoke than `search` or `context`. It requires an explicit flag because the rendered evidence context is sent to the selected Copilot model.

```bash
python3 -m dogfood.llm_wiki.cli ask \
  "why did we choose the cache design" \
  --topic "cache architecture" \
  --class decision_history \
  --allow-model-call
```

Defaults:

- model: `gpt-5.6-luna`;
- per-call AI-credit cap: `30`;
- Copilot tools/MCPs disabled;
- final content extracted from JSONL programmatic transport;
- answer is printed only; it is never written into canonical state.

Do **not** use `--allow-model-call` for evidence you are not permitted to send to the model. In particular, this branch does not change the project's company-data boundary.

## Supported evidence

v0 accepts UTF-8 text files. Markdown, source code, JSON, YAML, CSV, and plain text work as long as they decode as UTF-8. PDF/OCR, web crawling, embeddings, graph stores, and cloud sync are deliberately out of scope for this first shell.

## Authority rule

Raw evidence is authoritative and immutable. Search results and rendered context are views over raw evidence. The optional model-backed answer is also only a view. No command in v0 mutates or promotes an LLM-derived statement into canonical state.

## Source identity

A source ID is `src-` plus the first 16 hexadecimal characters of the content SHA-256. Re-ingesting identical bytes reuses the same source ID and raw object, while still appending a new local ingest-history event. If a file changes, the changed bytes become a new source ID; the old object remains intact.

## Privacy boundary

Ingest, search, context, topic registry, workload telemetry, and history are local-only. The evidence manifest records the basename supplied during ingest, not an absolute path. E013 workload telemetry is a separate local event stream and intentionally does not contain filenames/source IDs/hashes/query text. Only the `ask --allow-model-call` path invokes Copilot, and it does so explicitly with the retrieved evidence context.

## Non-goals

This branch does not decide whether persistent compilation should exist. It does not contain a vector DB, graph DB, verifier stack, autonomous mutation, incremental consolidation, or polished UI. E013 workload collection is not permission to enable compiled state; it is evidence gathering for that decision.
