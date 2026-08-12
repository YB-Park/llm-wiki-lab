# E007 Family N Repetition Plan v0

Status: **frozen before first scored run**
Date: 2026-08-12

## Primary screening block

Run exactly **3 independent repetitions per condition** for C0–C4.

Total primary runs: **15**.

This is a screening/trust-gate block, not a high-powered statistical benchmark. Three repetitions are enough to expose gross stochastic instability without turning the first experiment into an unnecessarily large campaign.

## No optional-stopping pooling

Do not silently add a fourth or fifth repetition because an early result is surprising, close, or inconvenient and then pool it into the original block.

If more repetitions are justified after the n=3 block, create a separately named **replication block** with its own frozen plan. Report primary and replication blocks separately before any combined analysis.

This prevents sample-size expansion from becoming an unconscious way to chase a preferred conclusion.

## Frozen execution order

The 15 runs are interleaved rather than executing all runs of one condition together.

The order was generated before scored outcomes using the fixed seed label:

`E007-C-v0-2026-08-12`

Frozen order:

1. `C0-r03`
2. `C4-r03`
3. `C2-r01`
4. `C4-r02`
5. `C1-r01`
6. `C3-r03`
7. `C2-r02`
8. `C1-r02`
9. `C3-r02`
10. `C1-r03`
11. `C0-r02`
12. `C3-r01`
13. `C4-r01`
14. `C2-r03`
15. `C0-r01`

The unusual ordering is intentional. Do not reorder based on observed quality.

## Runtime drift rule

The primary block uses `execution-profile-v0.md`.

If a material runtime change occurs mid-block — for example resolved model changes or the Copilot CLI version changes materially — stop and record the boundary rather than silently treating all 15 runs as identical-runtime repetitions.

Infrastructure retries caused by a clear tool/process failure are allowed, but the failed attempt must remain observable in local logs and must not be confused with a semantic reroll.

## Semantic evaluation

Each completed run is evaluated according to `evaluator-profile-v0.md` after the original run output is frozen.

Evaluator calls are post-hoc analysis cost and are not included in C0–C4 maintenance lifecycle cost.

## After the primary block

Decide the next experiment based on failure structure, not only condition ranking.

Possible outcomes include:

- enough separation to justify a targeted ablation,
- high variance requiring a replication block,
- no useful separation, implying the proposed safeguard may be ceremony under this workload,
- a safeguard introducing new failure modes that deserve a dedicated automation-policy experiment.
