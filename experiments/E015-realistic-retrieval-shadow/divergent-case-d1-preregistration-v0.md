# E015-D1 — first real-user divergent-case quality check

Status: **PREREGISTERED BEFORE X1 MODEL SCORING**  
Date: 2026-08-15 KST

## Why this case exists

Assistant-as-user E010 exposed a repeated failure on the frozen question:

> E014-R1 passed. Why is `structural_expand_v1` still not the default, and what can E015 actually tell us?

Two independent W0-backed real `gpt-5.6-luna` answers overclaimed E015 as if it could establish comparative retrieval quality/default promotion.

We initially classified this as a semantic-model failure because `source show` proved that the cited E015 preregistration itself contains the explicit limitation:

> E015 is not a quality proof. The user continues to see W0 only, so shadow disagreement cannot tell us which mode is correct.

That diagnosis was too strong. Zero-model diagnostic run `31861868445` / artifact `9240822200` reconstructed the actual model context and showed:

- W0 ranked the correct E015 preregistration, but its single best paragraph snippet omitted both the divergence-description paragraph and the `not a quality proof` paragraph;
- increasing W0 top-k did not repair that within-object snippet loss;
- X1 on the same current topic/corpus produced context containing both decisive paragraphs;
- no model call was needed to observe this difference.

This is the first actual project-dogfood case matching the E014-R1 mechanism: **the correct object is retrieved but W0's context granularity omits a decisive neighboring/section statement that X1 preserves**.

## D1 question

Does X1 context repair this already-observed user failure in one real Luna answer?

## Frozen comparison boundary

- user question is unchanged;
- W0 negative outcome is already observed twice; do not spend another W0 model call;
- topic discovery remains the current W0/current-only product discovery path so this is not an all-X1 synthetic route;
- after the topic is selected, render the answer context with `structural_expand_v1` only;
- assert before the model call that X1 context contains both:
  - `E015 measures **how often the existing default W0 and candidate X1 actually diverge`;
  - `E015 is not a quality proof`;
- use the existing product citation-handle boundary and exact `gpt-5.6-luna`;
- exactly one model call, `--max-ai-credits=30`, no rerolls.

The runner excludes only its own D1 preregistration/runner/workflow/request files from ingestion so it reproduces the 299-file main corpus on which the zero-model W0/X1 diagnosis was made. No pre-existing project evidence is excluded.

## D1 GO

All must hold:

1. answer is returned normally through the product citation-handle boundary;
2. answer says E014-R1/X1 evidence does **not** justify default promotion by itself;
3. answer says E015 measures realistic W0/X1 **divergence / disagreement / prevalence**;
4. answer explicitly says E015 **cannot establish which mode is better / comparative quality / default promotion by itself**;
5. all materialized canonical source IDs resolve through `source show`;
6. exact response model is `gpt-5.6-luna` where observable;
7. final Alpha integrity remains clean.

## D1 FAIL

Any repeat of the W0 quality overclaim, missing/invalid citation, fail-closed model-output error, or missing required limitation fails D1.

## Interpretation

### If D1 passes

Conclude only:

- X1 repaired this **one observed realistic divergent case**;
- the E014 mechanism is no longer purely synthetic—it has appeared in real project dogfood;
- additional realistic divergent cases are justified if/when natural E015 telemetry surfaces them.

Do **not** conclude:

- X1 should become global default from one case;
- X1 is generally more accurate;
- E015 shadow disagreement itself proved quality.

A passed D1 may justify a narrowly scoped product hypothesis (for example, an opt-in/candidate route or later routing hypothesis) only after checking additional natural divergent cases.

### If D1 fails

Do not blame W0 context alone. Re-open the answer-semantic hypothesis and decide whether any verifier experiment is still justified.

## Cost discipline

- D1: exactly 1 Luna call;
- W0 control: 0 new calls (two real failures already exist);
- no company/private evidence;
- no canonical mutation;
- no automatic default promotion.
