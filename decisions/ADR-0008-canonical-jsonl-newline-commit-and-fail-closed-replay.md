# ADR-0008 — Canonical JSONL records commit at newline and replay fails closed

Status: **Accepted**

Date: 2026-08-14

## Context

The Alpha Core authority floor now includes:

- immutable, content-verified raw evidence (ADR-0003/0004/0007);
- append-only topic source/current-history and temporal/dispute events (ADR-0005);
- append-only exact raw-span provenance pointers (ADR-0006).

Two canonical metadata logs are JSONL files:

- `manifest.jsonl` — evidence revision observations, current/history lineage, correction/change/dispute events;
- `provenance.jsonl` — local exact raw-span pointer records.

A process or power failure during append can leave a final record only partially written. Without an explicit persistence contract, a reader might accidentally accept a partial tail, ignore corruption, or append new authority state on top of damaged history.

The project does not need a signed ledger or database to contain this failure. It needs a small, deterministic definition of what counts as a committed JSONL record and how damaged logs are handled.

## Decision

### 1. Newline termination is the commit marker

A canonical record is committed only when the complete UTF-8 JSON object is followed by its terminating newline.

Therefore:

- a non-empty final fragment without a newline is `torn_tail`;
- this remains true even when that final fragment happens to parse as valid JSON;
- a reader must not infer that a syntactically complete but non-newline-terminated final value was durably committed.

This is a deliberately simple local append contract, not a distributed commit protocol.

### 2. Durable-prefix corruption is distinct from a torn final append

Every newline-terminated record in the durable prefix must be:

- valid UTF-8;
- valid JSON;
- a JSON object.

An invalid UTF-8 line, invalid JSON line, non-object value, or blank complete line is classified as `corrupt_record` rather than `torn_tail`.

The distinction matters operationally:

- `torn_tail` is consistent with an interrupted final append;
- `corrupt_record` means a supposedly committed prefix record is invalid.

Neither classification is automatically repaired.

### 3. Semantic replay fails closed

The integrity inspector may count valid complete records before damage for diagnostics.

Semantic readers do **not** replay that prefix as a fallback when the log is torn or corrupt.

If either condition exists:

- `store.history()` fails;
- source/current-history/temporal projections fail;
- exact provenance history/resolution fails for a damaged provenance log;
- mutation paths that first read canonical state fail before adding new semantic state.

The core does not guess what the interrupted/corrupt event meant.

### 4. All canonical writers use one append boundary

Source/lineage, temporal/dispute, and exact-provenance canonical writers use the shared `eventlog.append_jsonl_record` helper.

Before append it verifies that the existing log is not torn/corrupt.

A successful append:

1. serializes exactly one JSON object;
2. appends exactly one terminating newline;
3. calls `fsync` on the completed file append before returning success.

A short/failed write may leave a torn tail. The writer does not attempt rollback or truncation; subsequent strict replay detects the state.

### 5. Aggregate log integrity audit is read-only and privacy-minimal

`verify_canonical_log_integrity(root)` reports only aggregate status for manifest and provenance logs:

- valid complete-record count;
- torn-tail boolean;
- corrupt-record count;
- overall `ok`.

It exposes no event body, source/provenance ID, hash, path, filename, local label, query, content, or user data.

The audit never changes log bytes.

### 6. Non-authoritative telemetry is outside this migration

E013/E015 local telemetry logs are observational measurement apparatus, not canonical knowledge authority.

This ADR therefore does not require migrating their persistence semantics. Their privacy/failure-containment contracts remain separate.

## Evidence for acceptance

Implementation issue: #49  
Implementation PR: #50

The shared boundary is implemented in `dogfood/llm_wiki/eventlog.py` and used by:

- `store.history` / manifest writes;
- E003 temporal/dispute manifest writes;
- exact-provenance history / writes.

Deterministic tests cover:

- newline-terminated append and `fsync` invocation;
- valid newline-terminated legacy manifest replay;
- torn manifest tail with valid prefix diagnostic but fail-closed semantic replay;
- syntactically valid final JSON without newline still treated as uncommitted/torn;
- interior invalid JSON, invalid UTF-8, and non-object records classified as corruption;
- append refusal on torn/corrupt existing logs without changing bytes;
- source ingest and correction/dispute refusal on torn manifest;
- exact-provenance history/resolve/new bind refusal on torn/corrupt provenance log;
- privacy-minimal read-only aggregate integrity audit;
- integration of source, temporal/dispute, and provenance mutation paths through committed newline-terminated logs.

On fresh PR head `acb3f3f03a1193fc462fc239fe36dd1a69ab7e34`, all substantive consumer steps were green before this ADR commit:

- Python unit tests: PASS;
- CLI smoke: PASS;
- VS Code static/safety checks: PASS;
- development Extension Host: PASS;
- bundled Python core: PASS;
- packaged VSIX Extension Host: PASS;
- frozen E004/E014/E014-R1 validations: PASS;
- compiled provider remains disabled;
- model calls / AI credits: **0 / 0**.

A prior run also completed every substantive step and then remained unusually long in GitHub Actions checkout post-job cleanup. A fresh run was used to independently reconfirm the consumer steps rather than treating runner-cleanup state as product evidence.

## Consequences

### Positive

- An interrupted final append cannot be silently mistaken for committed authority state.
- Committed-prefix corruption cannot be mislabeled as an ordinary torn tail.
- The core will not append new canonical events on top of already detected damage.
- Source, temporal, and provenance logs now share one persistence contract instead of subtly different ad hoc JSONL behavior.
- The minimum Alpha persistence failure mode is explicit without adopting a database.

### Costs / limitations

- Semantic use stops on any canonical log damage instead of using a valid prefix opportunistically.
- `fsync` adds local write latency.
- The integrity report intentionally does not identify the damaged record; detailed recovery tooling would require a separately protected local diagnostic path.
- This contract assumes a single logical writer at a time. It does not make concurrent appends transactional.

## Explicit non-goals

This decision does **not** provide:

- automatic log repair or tail truncation;
- rollback after a failed append;
- signed/hash-chained/tamper-evident event history;
- hostile-tamper resistance;
- multi-writer locking or serializable transactions;
- event sequence consensus;
- database migration;
- filesystem/directory fsync protocol for arbitrary crash models;
- retrieval/model/UI changes;
- vector/graph storage;
- compiled-Wiki activation.

A newline + file `fsync` boundary is the minimum local crash-containment rule required for Alpha; it is not claimed to solve every storage-system failure model.

## Convergence consequence

This closes blocker G in `docs/09-alpha-core-readiness-gate.md`.

With A–G now implemented and regression-tested, the raw-first **Alpha Core is ready**.

Per the project convergence rule, new core infrastructure is no longer added by default. Further core work must be driven by:

1. an observed dogfood failure/blocker;
2. E013/E015 realistic evidence crossing a preregistered decision boundary; or
3. a reproducible trust/data-loss failure in an existing Alpha invariant.

Interesting architecture by itself is no longer sufficient justification.
