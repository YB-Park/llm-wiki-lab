# E018 preregistration addendum v2 — model-family JSONL parser and no-reroll resume

Status: **infrastructure correction after 2 completed generations, before any scored matrix completion**  
Date: 2026-08-15 KST

The corrected-credit run completed two C1 baseline generations before the harness stopped:

1. `gpt-5.4` C1 completed and parsed successfully.
2. `claude-sonnet-4.6` C1 completed successfully, but the harness rejected its JSONL because it required `assistant.message.data.phase == "final_answer"`.

Current Copilot CLI output showed a model-family transport difference:

- GPT-5.4 terminal `assistant.message` included `phase: "final_answer"`.
- Claude Sonnet 4.6 emitted exactly one terminal content-bearing `assistant.message` with matching model/tool metadata but no `phase` field.

Claude's actual policy JSON was valid and matched the frozen C1 expectation. This is a harness/parser failure, not a semantic model failure.

## No-reroll correction

The two completed C1 baseline generations are preserved in `phase1-seed-run-31888767216.json`, with exact parsed decisions/replies and SHA-256 hashes of the original raw JSONL artifact files.

They will **not be called again**.

The resume runner:

- re-scores those two seeded decisions with the original frozen scorer;
- accepts either one explicit `phase=final_answer` message or, when no explicit phase exists, exactly one content-bearing terminal `assistant.message` with no tool request;
- executes only the remaining **22** Phase-1 calls;
- combines 2 seeded + 22 new = the original frozen 24-call matrix;
- preserves every original case, expected label, model, prompt policy, scoring rule, trigger, and no-reroll constraint.

This addendum changes transport parsing/resume mechanics only. It does not respond to or alter a model-quality outcome.
