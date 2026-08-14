# ADR-0007 — Verify raw content identity before semantic use

Status: **Accepted**

Date: 2026-08-14

## Context

The project has treated raw evidence as the authority floor from the beginning. ADR-0003/0004 made raw bytes immutable/content-addressed and separated immutable content identity from evidence-revision identity. ADR-0006 added exact raw-span provenance pointers with explicit SHA/object checks.

A remaining inconsistency existed: ordinary core consumers such as retrieval and source-open used `store.read_text(Source)`, and that function decoded the raw file without recomputing its SHA. A raw object whose file still existed but whose bytes had been corrupted or modified could therefore reach normal semantic use even though its filename/source metadata claimed the original digest.

That violates the intended meaning of “content-addressed raw authority.”

## Decision

Raw evidence must be **content-verified before semantic use**, not merely content-addressed when written.

### 1. One verified byte boundary

`store.read_bytes_verified(Source)` is the general raw-read floor.

Before returning bytes it verifies:

- declared SHA-256 has canonical lowercase 64-hex form;
- `object_id == obj-<sha256>`;
- the raw filename matches `<sha256>.txt`;
- the file exists;
- SHA-256 of the actual bytes equals the declared digest.

Any failure stops the read.

`store.read_text(Source)` must use that boundary and then require valid UTF-8.

### 2. Source metadata is validated before constructing a raw path

When a source record is projected from history, malformed SHA metadata or an object-ID/SHA mismatch fails before the raw path is used.

This is both an integrity and path-identity boundary. A malformed manifest digest must not become a filesystem path component that semantic code attempts to follow.

### 3. Failure is fail-closed

Missing, corrupt, identity-inconsistent, or invalid-UTF-8 raw evidence is not replaced by:

- manifest metadata;
- a derived page;
- a current successor revision;
- a fuzzy match;
- cached answer text;
- a model repair.

Ordinary retrieval may therefore fail when any raw object it must inspect is corrupt. This is intentional: silently answering from unverified evidence would be a worse failure mode.

### 4. Historical evidence is held to the same integrity rule

Superseded historical source revisions remain readable, but only through the same content verification.

“Historical” does not mean “trusted without checking.”

### 5. Aggregate integrity audit is read-only

`verify_raw_integrity(root)` scans source-history records and verifies each unique well-formed content digest once.

It returns only aggregate fields:

- source-record count;
- unique-object count;
- verified-object count;
- missing-object count;
- corrupt-object count;
- invalid-UTF8-object count;
- invalid-source-record count;
- overall `ok`.

It exposes no source IDs, hashes, filenames, paths, content, origins, queries, or provenance labels.

It performs no repair, deletion, quarantine, successor selection, manifest rewrite, or provenance mutation.

Shared evidence revisions that point to identical immutable bytes count as one raw object for the audit; provenance multiplicity does not inflate integrity work.

### 6. SHA identity, not size metadata, is the authority check

`size_bytes` remains descriptive source metadata. V1 does not add it as a separate trust gate because byte SHA-256 already binds the full content and changing legacy size semantics would add little integrity value.

### 7. Exact provenance may remain stricter

ADR-0006 exact-provenance resolution already checks its own stored source/object/SHA snapshot in addition to the general read path.

That extra cross-check is retained. The new verified-read floor does not weaken or replace provenance-specific validation.

## Evidence for acceptance

Implementation issue: #47  
Implementation PR: #48

Pre-ADR implementation head `d44d528ce1afbf6e54bbd9d6501fee9bc3327a46`:

- Python unit tests: **84/84 PASS**;
- valid ASCII/Korean/emoji verified-read round trip: PASS;
- existing raw-byte tamper causes `read_text` and default search to fail closed: PASS;
- missing raw object fails closed: PASS;
- source object-ID mismatch fails before semantic use: PASS;
- malformed/path-like SHA fails before raw-path construction: PASS;
- self-consistent invalid UTF-8 bytes fail text decoding and are counted by audit: PASS;
- integrity audit deduplicates shared immutable objects and is read-only/privacy-minimal: PASS;
- superseded historical raw source remains verified/readable: PASS;
- exact provenance still resolves valid bytes and detects corruption: PASS;
- integrity audit leaves valid retrieval signature unchanged: PASS;
- E013/E015/privacy/provenance regressions: PASS;
- frozen E004/E014/E014-R1 validations: PASS;
- CLI smoke: PASS;
- VS Code development Extension Host: **4/4 PASS**;
- bundled Python core: PASS;
- packaged VSIX Extension Host: **4/4 PASS**;
- compiled provider remains disabled;
- model calls / AI credits: **0 / 0**.

## Consequences

### Positive

- “raw is authoritative” now implies “raw bytes were verified before semantic use.”
- Retrieval cannot silently use a modified file whose name/manifest still claims the old digest.
- Manifest SHA path traversal-like corruption is rejected before path construction.
- Integrity auditing can diagnose a workspace without leaking evidence identity/content and without mutating it.
- Historical citations retain the same trust floor as current evidence.

### Costs / limitations

- Every semantic raw read now hashes the object bytes. This adds deterministic I/O/CPU cost.
- V1 has no digest cache because a cache would need its own invalidation/trust model. Correctness is preferred over premature optimization.
- One corrupt object can stop a retrieval that attempts to inspect it rather than partially answering from the rest.
- The integrity audit reports counts, not which source needs repair. A future explicit diagnostic UX may need a protected local detail view, but that is not part of this ADR.

## Explicit non-goals

This decision does **not** add:

- automatic repair/quarantine;
- signed manifests or cryptographic event-log chaining;
- hostile-tamper resistance for the entire workspace;
- multi-writer locking/transactions;
- fsync/crash-consistency redesign;
- retrieval/ranking changes;
- model-based recovery;
- vector/graph storage;
- compiled-Wiki activation;
- new VS Code features.

Raw object verification and event-log integrity are distinct problems. Passing this boundary does not imply the append-only manifest itself is cryptographically tamper-evident.

## Follow-up boundary

Do not automatically build a signed log next.

Before adding another persistence mechanism, evaluate the remaining alpha-critical core gaps by severity and realistic failure likelihood. Event-log crash/tamper detection, mutation concurrency, provenance reattachment, and persistent compilation are separate decisions with different evidence requirements.
