# ADR-0003 — Explicit topic-scoped source lineage over immutable raw evidence

Status: **Accepted**

Date: 2026-08-14

## Context

The dogfood core began with a deliberately small raw substrate:

- raw bytes are stored content-addressed by SHA-256;
- `source_id` is derived from the content hash;
- ingest events are append-only;
- topic-scoped BM25 retrieval reads all sources associated with a topic.

That was sufficient for early retrieval and E013 workload calibration, but it had a correctness gap: when evidence changed, the new bytes became another active source while the old bytes remained active. `--authoritative-update` could not solve this because it is intentionally an E013 maintenance-cycle marker, not a claim that one evidence object semantically replaces another.

A trustworthy Wiki substrate therefore needs a way to distinguish **immutable history** from the **current evidence view** without deleting old evidence or asking an LLM to infer temporal semantics.

There is an additional complication: source IDs are currently content-addressed. The exact same historical bytes can legitimately become current again after an intervening change (`A -> B -> A`). A static acyclic predecessor graph over content IDs would incorrectly treat that normal reversion as a cycle.

## Decision

### 1. Raw bytes remain immutable

Supersession never rewrites or deletes raw objects. Every historical content object remains addressable by its SHA-256-backed source ID.

### 2. Supersession is explicit and append-only

The manifest may contain an explicit topic-scoped event:

```text
supersede(predecessor_source_id, successor_source_id, topic_id)
```

The core does not infer this relationship from filenames, changed bytes, timestamps, semantic similarity, or an E013 authoritative-update boundary.

### 3. Current state is produced by event folding, not a permanent DAG

For a topic, the core folds ingest/supersede events in recorded order.

- a source's first ingest into the topic makes it current;
- a supersede event removes the predecessor from the current set and keeps the successor current;
- a plain later re-ingest of previously superseded bytes does **not** resurrect them;
- an explicit `ingest --supersedes <current-source>` may mark the successor ingest as a deliberate reactivation, allowing legitimate `A -> B -> A` reversion;
- replaying an old relation is idempotent only while its successor is still current; it cannot resurrect an already-superseded successor.

This makes the event log the temporal record and the current evidence set a materialized view of that log.

### 4. Supersession is topic-scoped in v1

The same content-addressed source can participate in multiple topics. A relation in topic A must not silently hide evidence in topic B.

Therefore v1 does not implement global supersession. Unscoped retrieval remains an all-evidence view and does not claim to represent current truth.

### 5. Current retrieval is the default for topic-scoped answering

Topic-scoped `search`, `context`, and `ask` use only the current evidence view by default.

Historical inspection is explicit (`--include-superseded`). Direct provenance lookup by source ID always remains able to open historical superseded content.

`ask` has no historical mode: model-backed answering receives current evidence only.

### 6. E013 update boundaries remain independent

`--authoritative-update` continues to mean only "start a new E013 maintenance cycle." It does not imply supersession.

A command may explicitly perform both operations, but the resulting calibration event and evidence-lineage event remain separate facts.

### 7. Failure containment is conservative

Lineage mutation validates that the predecessor is current and that a standalone successor is current. Self-reference and stale/conflicting operations fail closed.

For `ingest --supersedes`, validation happens before ingest. If the process fails after ingest but before the supersede event is durably appended, both candidate versions remain visible. The system prefers temporary ambiguity over accidentally hiding evidence.

## Rejected alternatives

### Overwrite/delete old raw evidence

Rejected because it destroys provenance and prevents historical reconstruction.

### Treat every authoritative update as supersession

Rejected because a maintenance-cycle boundary can contain additions, corrections, changed facts, or unrelated new evidence. It does not identify which evidence replaces which.

### Infer supersession from same filename or changed bytes

Rejected because rename/copy/mirror/disagreement cases make this unsafe, and filename identity is not semantic identity.

### Global supersession

Rejected for v1 because a source may still be valid in another topic.

### Static DAG over content-addressed source IDs

Rejected because legitimate recurrence of identical bytes (`A -> B -> A`) becomes a false cycle. Event folding represents recurrence without mutating history.

## Consequences

Positive:

- stale explicitly-replaced evidence no longer enters normal topic answers;
- old citations remain resolvable;
- reversion is explicit and auditable;
- E013 semantics remain unchanged;
- no model calls, graph database, verifier stack, or compiled Wiki layer are required.

Costs/limitations:

- the user/tool must explicitly identify supersession;
- unscoped retrieval cannot claim current-state semantics;
- current `source_id` still conflates content identity with evidence/source occurrence identity;
- identical content from two independent origins is not yet represented as two independent provenance records;
- correction vs change-over-time vs disagreement is still not modeled explicitly.

The last two limitations are deliberate follow-up work. In particular, a future core revision should evaluate separating immutable content-object identity from evidence/source occurrence identity before richer provenance weighting or corroboration logic is added.

## Relationship to experiments

This ADR does not claim that explicit supersession is the final temporal model. E003 remains the experiment for correction/change/disagreement/valid-time semantics.

It also does not authorize persistent compiled state. E013 remains the gate for whether durable compilation has a realistic high-reuse workload region.
