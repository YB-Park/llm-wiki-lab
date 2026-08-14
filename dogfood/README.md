# Dogfood v0 — raw/retrieval/provenance shell

This is the earliest usable core surface of the project. It remains intentionally architecture-neutral while the persistent-compilation evidence program is still running.

## What is real in v0

- immutable, SHA-256 content-addressed raw evidence objects;
- opaque evidence/source revision IDs that are separate from byte identity;
- optional caller-asserted opaque origin IDs;
- append-only ingest and explicit supersession history;
- topic-scoped current-vs-historical evidence views;
- deterministic local BM25 retrieval over unique content objects;
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

The default local workspace is `.wiki-lab/` and is git-ignored in this repository. Override it with `--root` on any command.

## Evidence identity

The core deliberately separates three ideas:

```text
content object
  exact immutable bytes
  object_id = obj-<full SHA-256>

source revision
  one evidence/provenance revision that can be cited and superseded
  source_id = opaque src-... identifier

origin (optional)
  caller-asserted logical source identity
  origin_id = opaque non-sensitive token
```

Identical bytes are stored only once as a raw content object. They can still have multiple source records when the caller explicitly knows they came from different origins.

For example, two independently tracked origins can point to the same bytes:

```bash
python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  --origin-id design-doc \
  notes/shared-text.md

python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  --origin-id approval-record \
  notes/same-bytes.md
```

That produces two provenance records but one raw object. The core **does not** interpret two source IDs as two independent votes. Copying/echoing is still possible, and provenance multiplicity is not a reliability weight.

`--origin-id` is optional and must be a caller-asserted opaque ASCII token. Do not put a path, username, hostname, URL with sensitive parameters, or other secret metadata in it. The core does not infer origins from filenames, paths, text similarity, or an LLM.

When no origin is supplied, repeated identical current evidence is idempotent rather than manufacturing apparent corroboration.

Existing pre-v2 local stores remain readable. Legacy content-derived source IDs are resolved in place; new writes use opaque source revision IDs. There is no destructive migration of old citations.

## Current evidence and history

Raw objects are never overwritten or deleted by supersession. Instead, topic-scoped current state is an event-folded view over append-only ingest/supersede history.

If one source revision explicitly replaces another:

```bash
python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  --origin-id cache-decision \
  --supersedes src-OLD \
  notes/cache-decision-v2.md
```

Normal topic `search`, `context`, and `ask` then exclude the predecessor. Historical inspection remains explicit:

```bash
python3 -m dogfood.llm_wiki.cli search \
  "old cache limit" \
  --topic "cache architecture" \
  --include-superseded
```

Direct provenance remains resolvable even after supersession:

```bash
python3 -m dogfood.llm_wiki.cli source show src-OLD \
  --topic "cache architecture"
```

Supersession is never inferred from a changed filename, changed bytes, an LLM judgment, or an E013 maintenance-cycle marker. If the same origin changes bytes without explicit supersession, the core preserves both as current ambiguity until the relation is made explicit.

A deliberate `A -> B -> A` reversion creates a **new source revision** for the second A occurrence while reusing A's existing raw content object. Thus temporal evidence identity does not collapse merely because bytes repeat.

## Retrieval semantics

BM25 relevance is computed over unique current content objects, not over the number of provenance records. If two source revisions point to identical bytes:

- the text is scored once;
- it consumes one top-k slot;
- all active source IDs remain attached to the hit for provenance;
- the extra source record does not inflate document frequency, lexical relevance, or corroboration weight.

Rendered model context explicitly tells the model that multiple source IDs under one evidence object are identical bytes and must not be counted as independent corroboration.

This is still a deliberately cheap lexical baseline. Embeddings, vector stores, graph retrieval, and learned reranking have not earned inclusion merely because they are available.

## E013 realistic workload calibration

Calibration is explicit. Activity is logged only when you supply a local topic. Topic labels remain in the local registry; telemetry events store only opaque topic IDs and never store raw query text, document text, answer text, filenames, source IDs, object IDs, hashes, origin IDs, or environment metadata.

Create a topic and associate evidence:

```bash
python3 -m dogfood.llm_wiki.cli topic add "cache architecture"

python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  notes/cache-decision.md notes/cache-constraints.md
```

The first topic-associated ingest starts the baseline maintenance cycle. Ordinary later ingests add evidence but do not create fake update cycles. When the authoritative knowledge really changes, mark that E013 boundary explicitly:

```bash
python3 -m dogfood.llm_wiki.cli ingest \
  --topic "cache architecture" \
  --authoritative-update \
  notes/cache-decision-v2.md
```

`--authoritative-update` and `--supersedes` are independent facts. The former starts an E013 maintenance cycle; the latter changes the topic's evidence-lineage/current-view semantics. A command may use both, but neither implies the other.

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

If you open raw evidence through the CLI, that becomes a local provenance-follow event. Optional fixed-code feedback can also be logged without free text.

Generate the only artifact suitable for sharing back into the research conversation:

```bash
python3 -m dogfood.llm_wiki.cli calibration export
```

The sanitized export contains only aggregate counts, distributions, fractions, concentration measures, and a data-sufficiency status. It deliberately emits no topic IDs or labels, raw timestamps, queries, filenames, source IDs, object IDs, hashes, origin IDs, paths, or document/answer content.

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

Do **not** use `--allow-model-call` for evidence you are not permitted to send to the model. This core work does not change the project's company-data boundary.

## Supported evidence

v0 accepts UTF-8 text files. Markdown, source code, JSON, YAML, CSV, and plain text work as long as they decode as UTF-8. PDF/OCR, web crawling, embeddings, graph stores, and cloud sync are deliberately out of scope for this shell.

## Authority rule

Raw evidence is authoritative and immutable. Search results, current/history projections, and rendered context are views over raw evidence. The optional model-backed answer is also only a view. No command here promotes an LLM-derived statement into canonical state.

## Privacy boundary

Ingest, search, context, topic registry, workload telemetry, lineage, and history are local-only. The evidence manifest records the basename supplied during ingest, not an absolute path. E013 workload telemetry is a separate local event stream and intentionally contains no filenames/source IDs/object IDs/hashes/origin IDs/query text. Only `ask --allow-model-call` invokes Copilot, and it does so explicitly with retrieved evidence context.

## Non-goals

This work does not decide whether persistent compilation should exist. It does not contain a vector DB, graph DB, verifier stack, autonomous mutation, provenance trust scoring, claim-level corroboration logic, incremental consolidation, or polished UI. E013 workload collection is not permission to enable compiled state; it is evidence gathering for that decision.
