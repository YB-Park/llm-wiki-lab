# E007 Protocol Amendment A2 — Malformed Answer Items

Date: 2026-08-13
Status: active for the remainder of the frozen Family N primary block

## Trigger

After the frozen primary block had started, sequence 4 (`C4-r02`) aborted because an `answers[]` item emitted by the model did not contain a non-empty `query_id`.

This occurred after A1 had already changed batch-level answer-ID mismatch from a process-fatal exception into a recorded reliability failure.

## Problem

The original strict parser treated any malformed item inside `answers[]` as an infrastructure exception, aborting the entire run before the existing scorer could count the corresponding requested query as missing/failed.

That behavior conflated two distinct failure classes:

- experiment infrastructure failure, and
- model output-contract/reliability failure.

For the research objective, a malformed answer item is evidence about system reliability and should remain measurable rather than terminating the process.

## A2 policy

Each `answers[]` item is validated independently.

- Valid items are preserved without semantic editing.
- Invalid items are skipped and recorded with their array index and validation reason.
- Duplicate query IDs keep the first valid item; later duplicates are recorded as violations.
- No retry is performed.
- No missing query ID is inferred from position or question order.
- No malformed answer is repaired.
- No missing answer is invented.
- Extra valid query IDs are not scored.
- Any requested query left without a valid answer is handled by the already-existing scorer as `missing answer object` and therefore fails.

A2 therefore changes only failure containment/observability, not semantic scoring criteria.

## Scope control

A2 does **not** change:

- Corpus C,
- any source or query,
- C0–C4 prompts,
- condition semantics,
- model/runtime,
- n=3 repetition count,
- frozen run order,
- deterministic scoring rules,
- semantic scoring rubric,
- retry budget (still zero for answer-contract failures).

The incomplete `C4-r02` attempt must be archived rather than deleted before restarting the same frozen sequence 4 run.

## Evaluation compatibility

Post-hoc semantic evaluation must use the same A2 valid-item parsing rule when loading primary responses. Missing semantic query answers remain missing and must not be reconstructed from malformed items.

## Interpretation

A1+A2 expose a broader operational lesson without yet promoting it to architecture policy:

> LLM structured-output failures should be separated into deterministic transport/schema violations and semantic correctness failures. A malformed sub-item should not necessarily crash an entire long-running maintenance process, but containment must never silently repair or hide the failure.
