# E009A policy red-team amendment v1

Status: **pre-scoring policy correction; no scored verifier judgment had been generated.**

## Trigger

The original A3 policy routed every elevated/high-risk transition directly to oracle review and allowed autonomous commit only for low-risk accepted transitions.

On review, this design was too weak as a risk-sensitive automation experiment:

- it could appear safe largely by delegating most cases to review;
- the verifier call on a case already predetermined for review would not affect action;
- it did not test the more general hypothesis that higher epistemic/destructive risk may require **stronger evidence**, rather than always requiring a person.

## Revised A3 — tiered evidence escalation

Risk is evaluated before model calls.

- **low risk**: one valid `accept` verifier judgment -> autonomous `commit`; otherwise -> oracle `review`;
- **elevated risk**: two valid independent `accept` judgments -> autonomous `commit`; otherwise -> oracle `review`;
- **high risk**: direct oracle `review`; verifier calls are not required by the counterfactual policy.

Reviewed cases use the frozen gold label only to simulate Stage-A adjudication, exactly as before.

## Why this is better isolated

The revised A3 creates a meaningful ladder:

- A0: no evidence gate;
- A1: one verifier for all;
- A2: two-verifier consensus for all;
- A3: evidence strength rises with operation risk, with human review reserved for high-risk or failed gates;
- A4: human review for all.

This lets the experiment ask whether **selective evidence and selective review** can occupy a useful Pareto region rather than merely comparing automation with near-review-all.

## Cost semantics

Although the research block generates two blinded verifier judgments for every case so A1/A2/A3 can be replayed on identical evidence, A3's counterfactual deployment cost includes only calls the policy would need:

- pass 1 for low-risk cases;
- pass 1 + pass 2 for elevated-risk cases;
- no verifier calls for high-risk cases routed directly to review.

## Frozen elements unchanged

This amendment does not change:

- safe/unsafe gold labels;
- candidate text;
- previous state or evidence;
- verifier prompt;
- A0, A1, A2, or A4;
- two-pass call generation plan;
- primary outcome definitions;
- model/runtime profile.

## Limitation

A3 still receives oracle operation-risk labels in Stage A. A positive result therefore shows only the potential value of risk-sensitive adjudication **assuming risk is classified correctly**. It does not solve automatic risk classification.
