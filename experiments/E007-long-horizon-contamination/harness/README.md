# E007 Harness

Status: implementation scaffold; no scored runs yet

## Why Copilot CLI

The target daily environment is VS Code + GitHub Copilot, but manual chat UI interaction is difficult to repeat and measure consistently.

Current GitHub Copilot CLI supports programmatic non-interactive prompts, explicit model pinning, custom-instruction suppression, JSONL output, transcript export, and OpenTelemetry metrics including token usage and Copilot cost/AI units.

For the experiment we therefore use **Copilot CLI as a controlled model adapter**, while keeping VS Code UX for the later E010 usability trial.

Official references:

- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference

## Experimental isolation principles

A scored model call should:

1. pin a concrete model with `--model` — never `auto`,
2. use `--no-ask-user`,
3. use `--no-custom-instructions` so repo/user instruction files do not silently alter conditions,
4. deny read/write/shell/url/memory tools unless a condition explicitly tests tools,
5. run as a pure text-in/text-out transformation,
6. store the exact prompt and raw JSONL output,
7. export the session transcript,
8. enable OTel file export for token/cost/model metadata,
9. preserve CLI version and requested model in run metadata.

## Why tools are denied

E007 is testing knowledge-state maintenance policies, not agent tool skill.

If one condition can inspect arbitrary workspace files, web sources, persistent Copilot memory, or shell state, experimental inputs are no longer controlled.

The harness therefore places all allowed source/wiki state directly in the prompt and treats Copilot as the semantic transformation engine.

Tool-using/IDE-native behavior belongs in later experiments.

## Model policy

`--model` is required for scored runs.

Do not use Copilot Auto in E007 because Auto may route requests to different models according to task/system conditions. That is useful in normal work but introduces a confound in comparative experiments.

The chosen model must be available on the user's Copilot plan and should remain pinned for one run family.

A later experiment may explicitly compare models; E007 should not mix model choice with maintenance-policy choice.

## Telemetry

For scored runs set:

```text
COPILOT_OTEL_FILE_EXPORTER_PATH=<run>/otel.jsonl
```

The CLI's OTel spans can expose metadata including:

- requested/resolved model,
- input/output/cache tokens,
- turn count,
- Copilot cost,
- AI units,
- server duration,
- inference/tool call counts.

Prompt/response content capture should remain disabled because the prompt and raw CLI output are already stored explicitly by the harness.

## Files

- `validate_corpus.py` — deterministic corpus/rubric consistency checks
- `copilot_cli.py` — isolated non-interactive Copilot adapter
- future `run_e007.py` — state machine for waves/conditions
- future `score.py` — deterministic + semantic scoring aggregation

## Before first scored run

1. Run `python harness/validate_corpus.py`.
2. Confirm `copilot --version` and authentication locally.
3. Inspect available model strings with `copilot help` / model commands.
4. Pin one concrete model in experiment configuration.
5. Run one **non-scored infrastructure dry run** to validate JSONL/OTel parsing and estimate cost.
6. Freeze repetition count and condition prompts.

## Security / contamination note

The experiment corpus is fictional. Do not point the E007 harness at the user's real personal wiki or sensitive local files.

Realistic Corpus R will have a separate privacy and data-handling review before use.
