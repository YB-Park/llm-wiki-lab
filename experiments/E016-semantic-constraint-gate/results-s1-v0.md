# E016 structured semantic constraint gate — S1 result

Status: **OBSERVED FAIL / SEMANTIC HYPOTHESIS NOT VALIDLY TESTED**  
Date: 2026-08-15 KST

Workflow: `31861379614`  
Artifact: `9240675307`  
Main commit: `7a369058028c493d1e013b4e3515e1c2728b8d1a`

The first main attempt (`31861311808`) made zero model calls because the runner lacked repository-root `PYTHONPATH`; PR #90 fixed only that execution plumbing. The scored S1 run made one real `gpt-5.6-luna` call.

## Frozen case

Question:

> E014-R1 passed. Why is `structural_expand_v1` still not the default, and what can E015 actually tell us?

The S1 answer overclaimed E015 quality capability and failed the preregistered automatic checks. At the time, this was interpreted as evidence that a one-call structured `supported / forbidden / insufficient` self-check could not preserve an explicit negative constraint.

## Post-hoc diagnosis correction

That interpretation was too strong.

Zero-model diagnostic run `31861868445` / artifact `9240822200` later reconstructed the **exact W0 rendered context** on the current full-repo Wiki and showed:

- W0 did retrieve the correct E015 preregistration object;
- W0's best-paragraph snippet included the preceding purpose paragraph;
- the decisive adjacent paragraphs `E015 measures ... diverge` and `E015 is not a quality proof` were **not included in the model context**;
- later `source show` exposed the full source, which had caused the evaluator to incorrectly infer that Luna had seen those omitted statements;
- X1 context on the same corpus/topic/query did include both statements.

Therefore S1 did **not** validly test the intended semantic hypothesis: the model was asked to extract/preserve a limitation that its supplied W0 context omitted.

Preserve the observed S1 output as real answer evidence, but do not cite it as proof that structured self-checking fails when the negative constraint is actually present.

## Follow-up outcome

Verifier V1 explicitly required the literal `E015 is not a quality proof` in context before any model call. Run `31861598269` stopped at that prerequisite, so **zero verifier model calls** occurred.

E015-D1 then tested the simpler root-cause hypothesis. With the same frozen question and W0 topic discovery but X1 answer context, one real Luna call (`31862013373`, artifact `9240865801`) PASSed the required divergence-only/no-quality-proof/no-default-promotion answer with resolvable provenance and clean integrity.

## Decision

E016 is stopped. The observed failure is adequately explained first by context granularity, and the existing X1 mechanism repaired the one realistic case. Do not add or continue a verifier experiment unless a future real answer contradicts a material limitation that is demonstrably present in the exact model prompt/context.
