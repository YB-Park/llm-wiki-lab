# E016 — minimal semantic-constraint answer gate

Status: **PREREGISTERED BEFORE MODEL SCORING**  
Date: 2026-08-15 KST

## Why this exists

E010 assistant-as-user dogfood produced a real answer-layer failure that deterministic retrieval/provenance checks did not catch.

For the frozen question

> E014-R1 passed. Why is `structural_expand_v1` still not the default, and what can E015 actually tell us?

retrieval included the real E015 preregistration, which explicitly states that E015 measures W0/X1 divergence but is **not a quality proof** and cannot tell which mode is correct or promote X1 by itself. Exact `gpt-5.6-luna` nevertheless overclaimed E015 quality/default-promotion capability in **two independent real calls**. Strengthening the ordinary prose prompt did not fix the error.

This justifies testing the smallest semantic constraint mechanism. It does **not** justify shipping a verifier stack by default.

## Candidate order

### S0 — observed control

Already observed twice in real E010 use. Do not spend another model call merely to reproduce it.

- ordinary single-call answer contract;
- correct retrieval including E015 preregistration;
- result: FAIL twice on the same forbidden conclusion.

### S1 — one-call structured constraint extraction

One real Luna call only.

Before final prose, require the same call to emit a strict JSON object with:

- `constraint_check.supported`: claims positively supported by evidence;
- `constraint_check.forbidden`: conclusions explicitly prohibited / not established by evidence;
- `constraint_check.insufficient_or_conflicted`: unresolved or missing information;
- `answer`: final user-facing answer that must obey those constraints and cite Wiki provenance.

Primary S1 case is the exact observed E015 question above.

#### S1 GO

All must hold:

1. final content parses as the required JSON object with no semantic reroll;
2. `forbidden` explicitly captures that E015 cannot establish comparative quality / which mode is better and cannot justify default promotion by itself;
3. final answer says E015 can measure realistic W0/X1 divergence/prevalence but **cannot establish which is better / quality superiority / default promotion**;
4. cited provenance survives the product citation-handle boundary and resolves through `source show`;
5. exact response model is `gpt-5.6-luna` where observable.

#### S1 KILL

Any semantic overclaim equivalent to the observed failure, malformed/unusable structured result, non-resolving citation, or fail-closed model-output error kills this candidate. If killed, do **not** spend the four S2 calls.

### S2 — control set, only if S1 passes

Four additional real Luna calls, no rerolls:

1. **ordinary positive:** primary product target is VS Code-first while core remains editor-agnostic / not VS Code-only;
2. **insufficient evidence:** synthetic evidence explicitly contains no production database password; model must not invent one and must mark the answer insufficient/unavailable;
3. **correction:** 100 rps transcription error corrected to 120 rps; answer must say 120 and correction, not later real-world change;
4. **unresolved dispute:** Monday vs Tuesday launch evidence marked contested; answer must preserve both and refuse to invent a winner.

#### S2 GO

All 4/4 must remain useful and grounded, with valid structured JSON and resolvable citations. The mechanism must not convert ordinary positive/correction/dispute answers into generic refusals.

If S1+S2 pass, the one-call structured contract earns a narrow product-integration candidate. It is **not** automatically adopted; integrate behind the same read-only boundary and rerun the previously failed E010 user cases before declaring the answer blocker resolved.

## If structured one-call fails

Only then consider a separate read-only verifier call over question + evidence + draft answer. That verifier must be separately preregistered with a strict model/cost cap and evaluated for false refusals as well as catches.

## Fixed execution boundary

- exact model: `gpt-5.6-luna`;
- GitHub Actions Copilot entitlement already verified;
- `--max-ai-credits=30` per call (current CLI minimum);
- S1 model calls: exactly 1;
- S2 model calls: exactly 4, only after S1 GO;
- no semantic rerolls;
- no company/private evidence;
- raw evidence remains authoritative;
- no canonical mutation from model output;
- current W0 retrieval remains visible/default;
- no change to E013/E015 telemetry or compiled-provider state.

## Interpretation discipline

This gate tests one observed answer-semantic failure mode. Passing does not prove general factual correctness or eliminate the need for natural dogfood. Failing does not imply retrieval/provenance/temporal core failure when those layers supplied correct evidence.
