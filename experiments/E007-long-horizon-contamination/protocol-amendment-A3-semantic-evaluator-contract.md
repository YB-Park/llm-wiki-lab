# E007 Protocol Amendment A3 — Semantic Evaluator Contract Containment

Date: 2026-08-13
Status: **post-primary evaluation infrastructure amendment**

## Trigger

The frozen 15-run Family N primary block completed. During post-hoc semantic evaluation, the evaluator aborted on C4-r03 with:

```text
Q006: unsupported_claim must be boolean
```

The primary run artifacts are complete and unchanged. This amendment applies only to the post-hoc semantic evaluator contract boundary.

## Problem

The v0 evaluator treated any malformed field in one evaluator item as a fatal error for the entire evaluation pass. That conflates a structured-output contract failure with the semantic quality being evaluated.

## A3 policy

For evaluator output only:

1. Native JSON booleans remain canonical.
2. The exact case-insensitive strings `"true"` and `"false"` may be normalized to booleans. This is deterministic schema normalization, not semantic inference.
3. Other malformed or ambiguous values (`0`, `1`, `"yes"`, `null`, missing fields, invalid correctness, malformed rationale arrays, duplicate/missing query IDs) are **not guessed or repaired**.
4. An invalid evaluator item is recorded as an evaluator-contract violation and excluded from automatic semantic aggregation for that pass/query.
5. Any query with fewer than two valid evaluator passes is automatically placed in the human-audit set and must not contribute to the headline semantic mean or consensus-flag counts.
6. Raw evaluator responses are preserved. No evaluator call is silently retried merely to obtain a cleaner schema.
7. If a failed call already produced a raw response, A3 must attempt to parse that existing response before issuing any new model call.

## What A3 does not change

- Corpus C
- primary C0–C4 runs
- primary prompts or maintenance state
- deterministic scoring
- n=3 repetitions or run order
- semantic rubric or evaluator prompt
- candidate answers

A3 changes only how malformed evaluator output is contained and reported.

## Interpretation

Evaluator contract violations are evaluation-system reliability evidence, not candidate-Wiki errors. They must be reported separately from semantic correctness.
