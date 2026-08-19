# E023 posthoc zero-model selection analysis v0

Status: **EXPLORATORY / ZERO MODEL CALLS / NOT A PREREGISTERED SEMANTIC RESULT**

This analysis uses only the already-frozen run `32215941344`. It does not rerun Luna, change the primary G1 verdict, or authorize a new product policy.

## Why inspect the selection frontier

The primary G1 result showed the same four required-source recall@5 gaps in A and C:

- Q001 missing S004;
- Q002 missing S003;
- Q004 missing S008;
- Q010 missing S003.

The semantic C arm therefore earned **0 question-level improvements** and remains `NOT_EARNED`.

However, the full RRF rankings show that every missing C source landed at exactly **fused rank 6**.

## Deterministic counterfactual

`analyze_selection_counterfactual.py` recomputes required-source coverage from the frozen rankings only.

| selection | questions with complete required-source coverage |
|---|---:|
| A top-5 | 6 / 10 |
| A top-6 | 7 / 10 |
| C top-5 | 6 / 10 |
| C top-6 | **10 / 10** |

No semantic answer was generated for top-6. Therefore this says only:

> the blind planner/RRF produced latent retrieval signal that the frozen top-5 cutoff discarded.

It does **not** say that top-6 would have improved final answer quality.

## Gap details

- **Q001 / identity bridge S004:** A rank 7 → C fused rank 6. One planned alias/identity query individually ranked S004 at 3.
- **Q002 / repeated meeting evidence S003:** A rank 6 → C fused rank 6.
- **Q004 / Operations rationale S008:** A rank 8 → C fused rank 6. One planned query individually ranked S008 at 5.
- **Q010 / repeated meeting evidence S003:** A rank 8 → C fused rank 6.

The primary semantic failure Q001 therefore sits at a particularly useful boundary: the missing authoritative identity bridge was close enough to be discoverable without persistence, but it was excluded by the fixed selection budget and the composer then overclaimed rather than expressing uncertainty.

## Interpretation

This strengthens the decision **not** to move to G2 persistence.

Before adding semantic state, the project should understand three simpler controls:

1. **Evidence budget:** source-count top-k is a crude proxy; real sources vary enormously in size. Future gates should use an explicit character/token evidence budget rather than assume `5 vs 6 sources` generalizes.
2. **Selection policy:** consensus RRF can suppress a source that is highly ranked by one diagnostically useful query. A future selector may need diversity/coverage or consequence-aware evidence selection rather than pure consensus.
3. **Iterative evidence-follow:** a planner that has inspected initial hits can ask for the missing relation directly. This is more representative of an Agent search loop than blind pre-retrieval query expansion.

For identity/attribution questions, composition policy also needs a consequence-sensitive rule:

> if an identity merge is load-bearing and no explicit authoritative bridge is in context, report ambiguity or retrieve more evidence instead of silently merging.

## Non-conclusion

Do not change G1's frozen promotion result. C remains **NOT_EARNED** under its preregistered equal top-5 budget.

This posthoc analysis is hypothesis generation for a separately preregistered G1b, not a retroactive rescue of C.
