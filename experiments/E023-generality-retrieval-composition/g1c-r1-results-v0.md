# E023 G1c-R1 results v0 — authority-sufficiency evidence-follow recovery

Status: **R1 EXECUTION COMPLETE / RETRIEVAL-SELECTION NOT EARNED / NO G2 OR G3 AUTHORIZATION**.

## Frozen evidence

- invalid predecessor: G1c v0 run `32229563330` / source `987ee7ec615f7eb869be59f14a1928a3811baeed`;
- R1 run: `32232116273`;
- R1 execution source: `5227ac2b3f93c4f807e388822bfff963d0041120`;
- exact model: `gpt-5.6-luna`;
- R1 semantic call attempts: **18 / 18**;
- R1 semantic rerolls: **0**;
- execution complete: **true**;
- result SHA-256: `8f3e77163db92f7dff0b0a9aed5776c6dadd0eebfdb122fbfecf4313d0dae822`;
- frozen retrieval-selection verdict: **NOT_EARNED**.

R1 is a separate B-only recovery identity. It does not overwrite or pretend to continue the three lost B calls from invalid v0.

## Why v0 is not the result

G1c v0 completed six A composer calls and the first B planner/selector/composer sequence, then crashed because aggregate verdict code indexed baseline-clean B questions before their rows existed. The first B row had not yet been persisted, so the artifact retained only A and a stale persisted call count of six. Control flow proves nine actual v0 call attempts, but the three B outputs are unrecoverable.

Therefore v0 remains `INVALID_EXECUTION`. Its six A outputs are used only as immutable auxiliary semantic baselines; they do not make v0 a completed A/B comparison.

## Primary authority-sufficiency result

The prospectively frozen A baseline was:

- `SUFFICIENT_CLEAN`: **4 / 6**;
- `SUFFICIENT_WITH_CONFLATION_RISK`: **1 / 6**;
- `INSUFFICIENT_AUTHORITY`: **1 / 6**.

R1 stage decomposition is more informative than the final count alone:

| stage | clean | sufficient + conflation risk | insufficient |
|---|---:|---:|---:|
| A / initial exact top-5 | 4 | 1 | 1 |
| R1 candidate pool after evidence-follow retrieval | 4 | 2 | **0** |
| R1 final selector output | 4 | 0 | **2** |

The candidate pools contained enough positive load-bearing authority for **6 / 6** questions. This is a real retrieval mechanism signal. The final selector then destroyed part of that gain.

### AQ001 — retrieval recovered the bridge; selector threw it away

Initial exact top-5 lacked A003, the explicit `M. Chen -> Maya Chen` identity bridge, and contained same-surname distractor A004.

The planner correctly identified the identity/disambiguation gap. Both targeted follow-up queries retrieved A003 at rank 3, so the candidate pool became positive-authority complete. But the selector chose only A002/A001/A005: it removed the distractor **and the required identity bridge**.

Final authority returned to `INSUFFICIENT_AUTHORITY`. The composer then confidently named Maya Chen anyway.

This is no longer primarily a discovery failure. It is an **authority-preserving selection failure followed by an epistemic composition failure**.

### AQ002 — selector genuinely improved the context

The exact top-5 was already positive-authority complete but contained A004 as a dangerous same-surname distractor.

The selector retained direct email A002, meeting evidence A001/A005, and identity bridge A003 while dropping A004. Final context became `SUFFICIENT_CLEAN`, and the composer correctly preserved direct authorship versus meeting attribution.

This is a real positive selector example.

### AQ004 — selector regressed an already-clean baseline

The exact top-5 and candidate pool were both `SUFFICIENT_CLEAN` with A009/A010/A011 available for the early unconfirmed hypothesis, retry/rollback causal signal, and final postmortem.

The selector compressed the context to A011 alone. That removed A009 and A010, so the final context became `INSUFFICIENT_AUTHORITY` even though retrieval had already supplied everything needed.

This is direct evidence against the current prompt goal of selecting the "smallest sufficient" set without an external authority-preservation guarantee.

## Frozen promotion verdict

The preregistered strict rule required all six B final contexts to be `SUFFICIENT_CLEAN`. Actual final count was **4 / 6**.

The preregistered targeted-signal fallback also fails because:

- clean count did not increase above the A baseline of four;
- AQ004 regressed from clean to insufficient.

Therefore:

> **G1c-R1 evidence-follow final-selection policy is NOT_EARNED.**

Do not weaken this rule after seeing the result.

## Semantic adjudication

The invalid-v0 A outputs are auxiliary only. Frozen manual adjudication:

| question | A auxiliary | R1 B | main reason |
|---|---|---|---|
| AQ001 | CRITICAL_ERROR | **CRITICAL_ERROR** | unsupported identity merge; R1 selector dropped recovered A003 bridge |
| AQ002 | PASS | **PASS** | direct authorship / meeting attribution / identity preserved |
| AQ003 | PARTIAL | **PARTIAL** | HUMAN_KNOWLEDGE decision authority not made explicit in answer |
| AQ004 | PASS | **FAIL_RETRIEVAL** | R1 selector over-compressed clean context to A011 |
| AQ005 | PASS | **PASS** | temporal correction and causal timeline preserved |
| AQ006 | PARTIAL | **PARTIAL** | support-complete context, but composer overstates insufficiency for Canada-only option |

Counts:

- A auxiliary: **3 PASS / 2 PARTIAL / 0 FAIL_RETRIEVAL / 0 FAIL_COMPOSITION / 1 CRITICAL_ERROR**;
- R1 B: **2 PASS / 2 PARTIAL / 1 FAIL_RETRIEVAL / 0 FAIL_COMPOSITION / 1 CRITICAL_ERROR**;
- R1 semantic improvements vs auxiliary A: **0**;
- R1 semantic regressions: **1**;
- new critical errors: **0**.

### Trust lesson: AQ001 remains critical

The AQ001 answer again truthfully guessed the intended person but lacked the explicit identity bridge in final context. This remains `CRITICAL_ERROR`.

The important new diagnosis is that A003 had already been recovered into the candidate pool. The failure is now localized after retrieval.

> **Truth-by-luck is still not trustworthy recovery, even when the missing authority was found earlier in the same loop and then discarded.**

### HUMAN_KNOWLEDGE lesson: AQ003

A007 is explicit user-owned `HUMAN_KNOWLEDGE`. Both A and B answers state the decision/rationale correctly, but neither makes the epistemic type explicit. The answer reads like an ordinary externally observed team fact.

This is `PARTIAL`, not because the decision is wrong, but because a load-bearing derived claim should preserve whether its terminal authority is user-owned knowledge versus admitted external RAW evidence.

### Composition lesson: AQ006

A013+A014 are support-complete under the prospective contract. They establish Maple's Canada-only scope, encryption non-waiver, standard US-backup behavior, and existence of a non-default Canada-only DR option.

Both A and B correctly say the standard configuration fails and the Canada-only option **could** satisfy the rule, then unnecessarily mark the authority insufficient because the option is not separately guaranteed to keep every copy in Canada. That stronger guarantee is not part of the frozen proposition.

This is a composition sufficiency error, not a retrieval failure.

## What G1c-R1 actually earns

It does **not** earn the current final evidence-follow policy.

It does earn a narrower architectural diagnosis:

1. **evidence-aware follow-up retrieval can recover missing load-bearing authority** — AQ001 A003 reached the candidate pool;
2. the candidate-generation stage achieved positive authority completeness on **6 / 6** questions;
3. **unconstrained semantic compression is now the leading G1 failure surface** — it discarded authority in AQ001 and AQ004;
4. context sufficiency and composer epistemic behavior remain separable — AQ006 and AQ003 fail semantically despite clean authority contexts;
5. none of this is evidence for persistent semantic dossiers, entities, graphs, or automatic identity routing.

## Immediate next step

Pause paid semantic tuning again.

Before any G1d model run, use the frozen G1c-R1 candidate pools for **zero-model selection/budget counterfactual analysis**. The next question is not "which retrieval query trick is better?" It is:

> **Can a simple, general, evaluator-independent selection/budget rule preserve recovered load-bearing authority and avoid destructive compression, without installing a product claim graph?**

Candidate work should compare non-destructive evidence-budget policies against the frozen stage transitions before authorizing another model call.

Separately, future composition work must preserve `HUMAN_KNOWLEDGE` epistemic type and avoid declaring sufficient authority insufficient.

G2 persistence and G3 identity/routing remain unearned.
