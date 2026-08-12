# E007 VS Code-native Luna preflight

Status: **non-scored execution probe only**

This tiny extension exists because the actual target environment is VS Code + GitHub Copilot and GPT-5.6 Luna may be available there even when the Copilot CLI model catalog lags or differs.

It is **not** the production LLM Wiki architecture and it does not replace the Python E007 harness yet.

## What it checks

Two user-initiated commands are contributed:

- `LLM Wiki Lab: List Copilot Models`
- `LLM Wiki Lab: Run Luna Preflight`

The model-list command enumerates the `vendor: copilot` models currently exposed through VS Code's Language Model API and prints only model metadata.

The Luna preflight:

1. searches the actual VS Code Copilot model catalog for a model whose metadata contains `luna`,
2. sends the same fictional Zephyr micro-prompt used by the CLI preflight,
3. validates a fixed JSON response contract,
4. counts prompt/response tokens with the selected model's tokenizer,
5. prints a small handoff suitable for manual transfer.

No workspace, repository, or corporate content is included in the model request.

## Why a user command

VS Code's Language Model API requires user consent for extension access to Copilot models. Model selection/request must therefore originate from a user action. This probe intentionally runs only from explicit commands.

## Running from source

Open **this `vscode-preflight` directory as the VS Code workspace** in the corporate environment, then press `F5` to launch an Extension Development Host.

In the new VS Code window:

1. open Command Palette,
2. run `LLM Wiki Lab: List Copilot Models` if you want to inspect availability,
3. run `LLM Wiki Lab: Run Luna Preflight`,
4. approve the VS Code Copilot model-access consent prompt if shown,
5. copy/type only the short `VSCODE-PREFLIGHT-HANDOFF-v0` block back to the lab conversation.

No `npm install` is required; the probe uses only the built-in VS Code extension API.

## Expected handoff

```text
VSCODE-PREFLIGHT-HANDOFF-v0
status=PASS name=... id=... family=... version=... maxIn=...
prompt_tokens=... response_tokens=... wall_s=...
mismatch=-
billing=not_exposed_by_vscode_lm_api
```

If Luna is not exposed to the Language Model API, the output says `status=NO_LUNA_MODEL`.

## Measurement limitation

The VS Code Language Model API exposes model-specific token counting, but this probe does not receive Copilot's actual cache/billing/AI-credit telemetry. Therefore:

- CLI + OTel remains preferable if Luna becomes usable through Copilot CLI,
- VS Code-native execution can still measure supplied prompt/output token volume and comparative quality,
- any conversion from those token counts to cost is an estimate and must be labeled as such,
- cache effects must not be silently treated as known.

If this probe succeeds while CLI Luna fails, the next lab decision is whether to port the E007 state machine to a small VS Code experiment runner or accept a different execution/model compromise. That decision requires its own documented rationale; this preflight does not make it automatically.
