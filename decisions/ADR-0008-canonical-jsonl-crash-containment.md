# ADR-0008 — Contain canonical JSONL torn tails and durable-prefix corruption

Status: **Accepted**

Date: 2026-08-14

## Context

The raw-first Alpha core already had immutable evidence, explicit current/history lineage, temporal/dispute semantics, deterministic retrieval, exact provenance, verified raw-byte reads, and a read-only answer boundary.

The final planned infrastructure gap was physical failure containment for the two canonical append logs:

- `manifest.jsonl`, which carries source/current-history/temporal events;
- `provenance.jsonl`, which carries optional exact raw-span bindings.

The previous readers treated line-oriented JSON as semantic input but did not define what a partially written final append meant. The previous writers also did not request a durability flush after each event. A crash at the wrong point could therefore leave an ambiguous final record boundary.

The project does not need a database, WAL subsystem, signed log, or consensus protocol merely to contain this failure class.

## Decision

Adopt one small shared canonical JSONL contract for both logs.

### 1. Newline is the durable record boundary

A semantic record is replayable only when all of the following are true:

- its bytes occur inside the newline-terminated durable prefix;
- the record bytes decode as UTF-8;
- the decoded line parses as JSON;
- the parsed value is a JSON object.

Any non-empty bytes after the final LF are classified as a **torn tail**, even if those bytes happen to form syntactically valid JSON.

This deliberately avoids guessing whether a process died after payload bytes were written but before the record boundary was committed.

Blank newline-terminated lines remain ignored for compatibility with legacy logs whose readers already ignored blank lines.

### 2. Durable-prefix corruption is distinct from a torn tail

A newline-terminated record inside the durable prefix is corrupt if it is:

- invalid UTF-8;
- invalid JSON;
- valid JSON but not an object.

If durable-prefix corruption and a torn tail coexist, the status is `corrupt_prefix`. A corrupt committed prefix is the more fundamental replay failure.

### 3. Semantic replay fails closed

`manifest.jsonl` and `provenance.jsonl` semantic readers use the shared strict reader.

They reject:

- a torn tail;
- durable-prefix corruption.

They do not:

- truncate a tail;
- repair JSON;
- invent an event;
- skip a corrupt committed record and continue;
- follow a successor as a substitute;
- ask a model to reconstruct missing state.

The aggregate scanner may report how many valid durable records preceded/occurred around damage, but semantic code never treats that diagnostic count as permission to replay a damaged log.

### 4. One append primitive is shared by both canonical logs

Canonical event append uses one helper that:

- serializes one JSON object deterministically;
- appends a terminating LF;
- opens with `O_APPEND`;
- loops until all encoded bytes are written;
- calls `fsync` before closing;
- refuses to append when the existing log already has a torn tail or corrupt durable prefix.

The reader contract is still the primary containment mechanism. `fsync` reduces exposure but does not create a claim that arbitrary filesystems or multi-writer races provide stronger transactional guarantees than they actually do.

### 5. Aggregate integrity audit is privacy-minimal and read-only

`audit_canonical_logs(root)` reports only status/count fields for the two canonical logs, including:

- durable record count;
- ignored blank-record count;
- torn-tail byte count;
- corrupt durable-record count;
- invalid UTF-8 / invalid JSON / non-object counts;
- per-log status and aggregate `ok`.

It exposes no source IDs, object IDs, hashes, filenames, paths, topic IDs, origin IDs, labels, queries, answer text, or evidence content.

It performs no repair or mutation.

### 6. Existing semantic layers are unchanged

This decision changes the physical append/replay boundary only.

It does not alter:

- source/evidence identity;
- topic-scoped current/history projection;
- correction/change/dispute semantics;
- retrieval ranking or X1 shadow status;
- exact-provenance identity rules;
- E013/E015 telemetry semantics;
- answer behavior;
- compiled-provider state.

## Evidence for acceptance

Implementation issue: #51  
Implementation PR: #52

Pre-ADR implementation head `08efcd070d3d311c17c1a2a730f9588c5643b328` and PR CI run `31807220370`:

- Python unit tests: **94/94 PASS**;
- manifest torn-tail detection/fail-closed replay: PASS;
- complete valid JSON without final newline classified as torn tail: PASS;
- durable-prefix invalid JSON detection: PASS;
- durable-prefix invalid UTF-8 detection: PASS;
- durable-prefix non-object JSON detection: PASS;
- simultaneous prefix corruption + tail prioritization: PASS;
- append refusal on damaged logs: PASS;
- newline termination + `fsync` path: PASS;
- exact-provenance torn-tail and prefix-corruption handling: PASS;
- legacy blank-line/source replay compatibility: PASS;
- aggregate audit privacy boundary: PASS;
- CLI smoke: PASS;
- VS Code development Extension Host: **4/4 PASS**;
- bundled Python core: PASS;
- packaged VSIX Extension Host: **4/4 PASS**;
- frozen E004 prescore validation: PASS (`31807220368`);
- frozen E014 result validation: PASS (`31807220428`);
- frozen E014-R1 prescore validation: PASS (`31807220399`);
- E014-R1 freeze-hash validation: PASS (`31807220363`);
- compiled provider remains disabled;
- model calls / AI credits: **0 / 0**.

## Consequences

### Positive

- A partially written final canonical event can no longer be silently replayed.
- A damaged durable prefix is distinguishable from an incomplete final append.
- Both canonical logs now obey one failure contract rather than two subtly different readers/writers.
- Diagnostic inspection can remain privacy-minimal and mutation-free.
- The failure class is contained without introducing a database or repair subsystem.

### Costs / limitations

- A torn tail blocks semantic replay until an explicit future recovery procedure is chosen; v1 intentionally provides no automatic repair command.
- `fsync` is requested for the file descriptor, but this ADR does not claim full filesystem/power-loss transactional semantics across directory metadata, raw-object writes, or multiple files.
- There is no multi-process/multi-writer locking or compare-and-swap protocol. Concurrent writers remain outside the Alpha contract.
- There is no cryptographic event chaining or hostile-tamper resistance.
- A newline is part of the canonical durability format. A JSON payload without its terminating newline is not replayed as a committed event.

## Explicit non-goals

This decision does **not** add:

- SQLite/Postgres or another database;
- a general WAL/transaction manager;
- signed/hash-chained event logs;
- multi-writer concurrency control;
- automatic truncation or repair;
- backup/restore orchestration;
- model-based event recovery;
- retrieval promotion;
- vector/graph storage;
- compiled-Wiki activation;
- new VS Code UX.

## Follow-up boundary

This closes the final planned Alpha infrastructure blocker.

Per `docs/09-alpha-core-readiness-gate.md`, after this decision is merged the project must **stop adding core infrastructure by default**. Further core work requires an actual dogfood failure, a preregistered E013/E015 realistic-evidence boundary crossing, or a reproducible data-loss/trust failure in an existing Alpha invariant.
