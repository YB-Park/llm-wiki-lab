# E018 preregistration addendum v1 — Copilot CLI credit guard floor

Status: **infrastructure correction before any E018 model generation**  
Date: 2026-08-15 KST

The first main-branch Phase-1 attempt stopped before model generation on its very first command because the current Copilot CLI rejects `--max-ai-credits` values below 30:

`Invalid value for --max-ai-credits: "3". Use at least 30 AI credits.`

The runner's attempted-call counter reported 1, but the CLI rejected the command during argument validation; no model response was produced and no E018 case was scored.

## Correction

- `max_ai_credits_policy`: 3 -> **30**
- `max_ai_credits_answer`: 6 -> **30**

This is a CLI safety-guard floor, **not a planned spend of 30 credits per call**. Actual usage remains whatever the bounded prompt/response consumes; usage is reported only if the CLI emits trustworthy telemetry.

No case, expected decision, prompt policy, model, scoring rule, Phase-1 trigger, Phase-2 case, or no-reroll rule changes.

The corrected workflow uses a small v1 adapter around the frozen Phase-1 runner so the original pre-scoring runner remains inspectable.
