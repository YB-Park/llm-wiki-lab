# Dogfood v0 — raw/retrieval/provenance shell

This is the earliest usable surface of the project. It is intentionally architecture-neutral while the persistent-compilation evidence program is still running.

## What is real in v0

- immutable, content-addressed raw evidence copies;
- stable source IDs derived from SHA-256;
- append-only ingest history;
- deterministic local BM25 retrieval;
- provenance-preserving context rendering;
- an optional read-only Copilot answer adapter behind explicit opt-in;
- zero hidden model calls and zero automatic upload.

The durable/compiled knowledge layer is **disabled by default**. E012 and later realistic-workload evidence decide whether and where that layer earns activation.

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

## Optional model-backed answer

`ask` is deliberately harder to invoke than `search` or `context`. It requires an explicit flag because the rendered evidence context is sent to the selected Copilot model.

```bash
python3 -m dogfood.llm_wiki.cli ask \
  "why did we choose the cache design" \
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

Ingest, search, context, and history are local-only. The store records the basename supplied during ingest, not an absolute path. Only the `ask --allow-model-call` path invokes Copilot, and it does so explicitly with the retrieved evidence context.

## Non-goals

This branch does not decide whether persistent compilation should exist. It does not contain a vector DB, graph DB, verifier stack, autonomous mutation, incremental consolidation, or polished UI.
