# E016 — read-only verifier V1 preregistration

Status: **ABORTED BEFORE VERIFIER MODEL CALL — ROOT CAUSE CORRECTED**  
Date: 2026-08-15 KST

## Original question

V1 was preregistered to ask whether a separate read-only Luna verifier could catch the observed E015 answer overclaim, but only if the **actual retrieved model context first contained** the literal limitation:

> E015 is not a quality proof

That prerequisite was intentional: without it, the experiment would conflate retrieval/context failure with answer verification.

## What happened

Main run `31861598269` rebuilt the current full-repo Wiki and checked the prerequisite before `ask_copilot`.

The prerequisite failed:

`RuntimeError:prerequisite_context_missing_e015_quality_limit`

Therefore **zero verifier model calls were made**. No verifier ACCEPT/REJECT result exists.

## Why the prerequisite failed

Zero-model diagnostic `31861868445` / artifact `9240822200` reconstructed W0 retrieval/context and showed:

- the correct E015 preregistration object was retrieved;
- W0's single best-paragraph excerpt omitted the adjacent `diverge` / `not a quality proof` paragraphs;
- increasing W0 top-k did not repair that within-object excerpt loss;
- X1 context on the same corpus/topic/query included both decisive statements.

The prior semantic-failure premise was therefore corrected: the demonstrated problem was first **context granularity**, not a model contradicting a limitation present in its prompt.

## Subsequent evidence

E015-D1 preregistered one real-model check of the simpler explanation. W0 current-only discovery selected the topic; X1 rendered the answer context; the runner asserted both decisive E015 statements were present before calling Luna.

Run `31862013373` / artifact `9240865801`: **PASS**.

The real answer correctly said:

- E014-R1 does not justify default promotion by itself;
- E015 measures realistic W0/X1 divergence/prevalence;
- E015 is not a quality proof and cannot establish which mode is correct or promote X1 by itself.

All citations resolved and integrity was clean.

## Decision

V1 and its planned V2 controls are **not run further**. Do not spend verifier calls on a symptom already explained and repaired by a simpler retrieval/context mechanism.

Reopen a semantic verifier experiment only if a future real answer materially contradicts an explicit limitation that is demonstrably present in the exact model context. Such a future gate must be preregistered separately.
