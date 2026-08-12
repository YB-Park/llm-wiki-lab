# Corporate Copilot CLI Luna Preflight — 2026-08-12

Status: **PASS — non-scored infrastructure evidence**

This is a sanitized record manually transferred from the actual managed corporate development environment. It contains no E007 scored outcome and no corporate source content.

## Observed result

```text
PREFLIGHT-HANDOFF-v0
status=PASS
requested=gpt-5.6-luna
resolved=gpt-5.6-luna
cli=GitHub Copilot CLI 1.0.35
wall_s=13.62
otel=yes
input_tokens=5801
output_tokens=90
cost=1
aiu=155810000
```

## What this establishes

- The exact model identifier discovered through VS Code, `gpt-5.6-luna`, is also accepted by the corporate Copilot CLI.
- The requested model resolves to the same model identifier rather than being silently routed elsewhere.
- The non-interactive CLI path can complete the synthetic response contract.
- OpenTelemetry export is available in the real execution environment.
- Token-related telemetry is present.

This is enough to treat Copilot CLI + pinned Luna as a viable E007 execution adapter.

## What this does **not** establish

- `github.copilot.cost=1` is **not interpreted as one dollar**.
- `github.copilot.aiu=155810000` is retained as an opaque telemetry value until its semantics are independently verified.
- The 5,801 input-token telemetry value should not be interpreted as the user prompt size alone. The earlier VS Code LM API probe counted the synthetic user message at 167 prompt tokens, while the CLI telemetry reports a much larger input total. This difference may include CLI/system/agent context, different accounting boundaries, tokenizer differences, or other runtime overhead. Absolute adapter-level token counts and model-payload size must therefore be reported separately where possible.
- This preflight says nothing about which E007 condition is better.

## Experimental implication

Stop treating model access as an active research question for E007 Family N. Pin the execution environment and return attention to the Wiki-maintenance hypotheses.

If the CLI version or resolved model changes during a scored run block, record the change and start a new execution block rather than silently mixing environments.
