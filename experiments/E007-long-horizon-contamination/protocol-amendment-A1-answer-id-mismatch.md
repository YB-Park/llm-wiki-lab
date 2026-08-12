# E007 Protocol Amendment A1 — Answer-ID mismatch handling

Date: 2026-08-13
Status: **active for Family N from seq=2 retry onward**

## Trigger

The frozen Family N block began after the full-harness rehearsal passed. Sequence 1 (`C0-r03`) completed. Sequence 2 (`C4-r03`) then aborted because an answer-batch response returned a query-ID set different from the requested set.

No comparative condition ranking or intermediate quality interpretation was used to design this amendment.

## Defect in v0 harness

`run_e007.answer_queries()` treated any answer-ID mismatch as a Python exception and aborted the entire run.

That behavior conflated two different things:

- infrastructure/transport failure that makes output unreadable, and
- a readable model output that violates the requested answer contract by omitting or adding query IDs.

The latter is itself observable model/system behavior and should be scored/recorded rather than making the experiment impossible to complete.

## A1 policy

For readable answer-batch JSON:

- preserve the exact raw response unchanged,
- record `expected_ids`, `actual_ids`, `missing_ids`, and `extra_ids` in a local `contract-violations/` sidecar,
- perform **no retry**,
- invent **no missing answer**,
- ignore extra IDs for requested-query scoring,
- allow the existing deterministic scorer to count a missing requested answer as a failure.

Malformed/unparseable JSON still fails loudly under the existing parser policy.

## Execution integrity

The failed `C4-r03` attempt must not be deleted. It is archived under `runs/_failed_attempts/` with `archive_incomplete_run.py`, then the same frozen sequence-2 run ID is retried using `run_family_n_amendment1.py`.

Sequence 1 is not rerun. Corpus C, source order, model, prompts, C0–C4 condition semantics, n=3 repetition count, run order, and scoring rubrics remain unchanged.

## Interpretation

Answer-contract violations are a reliability signal, not merely nuisance formatting. Final E007 analysis should report their frequency by condition/call type if they recur.

This amendment does **not** claim that production systems should silently accept arbitrary malformed structured output. It only separates parseable contract violations from process-level crashes so the experiment can measure them.
