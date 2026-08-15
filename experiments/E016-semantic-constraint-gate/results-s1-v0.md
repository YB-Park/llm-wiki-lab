# E016 structured semantic constraint gate — S1 result

Status: **FAIL / S2 NOT RUN**  
Date: 2026-08-15 KST

Workflow: `31861379614`  
Artifact: `9240675307`  
Main commit: `7a369058028c493d1e013b4e3515e1c2728b8d1a`

The first main attempt (`31861311808`) made **zero model calls** because the runner lacked repository-root `PYTHONPATH`; PR #90 fixed only that execution plumbing. The scored S1 run below is the first actual model call under the preregistered structured contract.

## Frozen case

Question:

> E014-R1 passed. Why is `structural_expand_v1` still not the default, and what can E015 actually tell us?

Context retrieval selected the `experiments and evidence` topic. The retrieved/cited evidence included the actual E015 preregistration, whose opening states:

- E015 measures how often W0/X1 diverge during natural dogfood use;
- E015 is **not a quality proof**;
- because the user sees W0 only, shadow disagreement cannot tell us which mode is correct.

## Structured one-call result

Luna returned valid structured JSON and a resolvable citation, but the semantic gate failed.

The final answer said:

> E015 can therefore provide evidence about real-use frequency **and quality** only if its actual design and results measure those questions.

It also said:

> The supplied evidence does not include E015's protocol, results, or threshold...

Both statements are incompatible with the supplied context: the actual E015 preregistration was present and explicitly prohibited treating E015 as a quality proof.

The model's own structured fields also claimed `E015-specific evidence is absent`, despite citing the E015 preregistration itself.

Automatic S1 checks failed on:

- `forbidden_quality_captured = false`;
- `answer_says_divergence = false`.

Citation resolution and exact model checks passed.

## Decision

Per preregistration, **do not run S2's four control calls**. The hypothesis that a single Luna call can reliably repair this observed failure merely by extracting `supported / forbidden / insufficient` before writing its answer is rejected for this case.

The next candidate, if pursued, must be a separately preregistered **read-only verifier call** over evidence + a frozen failing draft. It must first catch this one observed failure in a single verifier call before any false-refusal controls are paid for.
