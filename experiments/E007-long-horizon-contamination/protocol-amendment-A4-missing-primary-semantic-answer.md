# E007 protocol amendment A4 — missing primary semantic answers

## Trigger

After the frozen primary Family N block completed, A3 semantic evaluation stopped on `C4-r02 / W01` because primary query `Q006` was absent. `Q006` is a `global_synthesis` query, so it is in semantic-evaluation scope.

The primary omission is already an observed model/contract failure. Re-running the primary answer or inventing a placeholder answer would change the observed result. Aborting the whole semantic evaluation also hides usable evidence from unrelated queries.

## A4 policy

For post-hoc semantic evaluation only:

1. Parse existing primary responses with A2 containment.
2. Preserve every valid primary answer exactly as emitted.
3. If a semantic query has no valid primary answer, do **not** call the semantic judge for that query.
4. Record the query as `primary_answer_missing` and `automatic_semantic_result=invalid_or_incomplete`.
5. Require human audit for that query.
6. Do not synthesize an answer, infer a query ID, retry the primary call, or assign semantic correctness/flags by guess.
7. Existing evaluator `response.txt` artifacts are reused; no reroll is allowed merely because parsing/evaluation infrastructure changed.

This amendment does not change the frozen primary block, prompts, corpus, run order, or deterministic scoring. It only prevents an already-observed primary omission from aborting post-hoc semantic evaluation.
