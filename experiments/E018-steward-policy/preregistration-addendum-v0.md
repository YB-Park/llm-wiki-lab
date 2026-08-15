# E018 preregistration addendum v0 — phase separation

Status: **frozen before any E018 model call**  
Date: 2026-08-15 KST

This addendum changes **execution plumbing only**, not the cases, expected decisions, models, phase-1 thresholds, phase-2 case IDs, answer checks, or decision interpretation frozen in `preregistration-v0.md`.

## Change

The initial merged workflow executes **Phase 1 only**: the 24-call policy matrix.

The phase-1 runner computes and records the already-preregistered `phase2_eligible` boolean. It does not automatically spend the reserved phase-2 calls.

If and only if `phase2_eligible=true`, a separate follow-up will run the already-frozen consequence check:

- cases: `C1-relevant-read`, `C6-conflict-pending-decision`;
- main models: `gpt-5.4`, `claude-sonnet-4.6`;
- maximum additional calls: 4;
- no rerolls;
- answer checks exactly as written in `preregistration-v0.md`.

## Why this is safer

Separating the workflows prevents a phase-2 transport bug or implementation detail from contaminating the 24-call policy result and guarantees that a Steward hypothesis that fails Phase 1 cannot spend additional calls automatically.

This addendum was created before model scoring and therefore does not respond to model outcomes.
