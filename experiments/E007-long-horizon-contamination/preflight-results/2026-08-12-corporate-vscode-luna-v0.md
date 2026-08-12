# Corporate VS Code Luna Preflight — 2026-08-12

Status: **PASS**

This record captures a manually transferred, sanitized result from the actual managed corporate VS Code + GitHub Copilot environment. No raw prompt/response or corporate data was transferred.

## Observed model identity

```text
name=GPT-5.6 Luna
id=gpt-5.6-luna
family=gpt-5.6-luna
version=gpt-5.6-luna
maxInputTokens=921793
```

## Synthetic preflight result

```text
VSCODE-PREFLIGHT-HANDOFF-v0
status=PASS name=GPT-5.6 Luna id=gpt-5.6-luna family=gpt-5.6-luna version=gpt-5.6-luna maxIn=921793
prompt_tokens=167 response_tokens=55 wall_s=5.31
mismatch=-
billing=not_exposed_by_vscode_lm_api
```

## What this establishes

- GPT-5.6 Luna is actually exposed in the target corporate VS Code/Copilot environment.
- The concrete model identifier visible through `vscode.lm` is `gpt-5.6-luna`.
- A user-initiated VS Code Language Model API request to Luna succeeds in that environment.
- The frozen synthetic temporal-change response contract passed in this one non-scored invocation.
- VS Code LM API token counting is usable for prompt/response accounting in this probe.
- Exact billing/cache telemetry is not exposed by this probe and remains unresolved.

## What this does NOT establish

- It does not freeze Luna as the E007 model yet.
- It does not establish that Copilot CLI accepts `gpt-5.6-luna` even if the current CLI documentation does not list it explicitly.
- It does not establish scored E007 quality.
- It does not establish billing/AI-unit/cache-read behavior.
- It is one infrastructure invocation, not a model-quality benchmark.

## Next evidence step

Try the exact model ID `gpt-5.6-luna` through the existing **non-scored Copilot CLI preflight**. If accepted, the CLI+OTel adapter remains preferred for E007 because it preserves the existing runner and may expose richer cost/cache telemetry. If rejected or unavailable, evaluate whether the E007 runner should be ported to the VS Code Language Model API.
