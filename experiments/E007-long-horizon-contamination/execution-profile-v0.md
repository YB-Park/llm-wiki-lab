# E007 Execution Profile v0

Status: **frozen for the first Family N scored run block; not an architecture decision**
Date: 2026-08-12

## Purpose

Freeze execution variables that are not the subject of E007 so that maintenance-policy differences are easier to interpret.

This profile is intentionally boring. GPT-5.6 Luna and Copilot CLI are experimental equipment, not the object of the research.

## Primary execution engine

- provider surface: GitHub Copilot
- adapter: non-interactive GitHub Copilot CLI via `harness/copilot_cli.py`
- requested model: `gpt-5.6-luna`
- required resolved model: `gpt-5.6-luna`
- observed corporate CLI at preflight: `GitHub Copilot CLI 1.0.35`
- OpenTelemetry: enabled, message-content capture disabled
- model auto-routing: forbidden
- repo/user custom instructions: disabled for scored calls
- workspace/web/shell/memory-style tools: excluded from scored calls

## Evidence

Two independent target-environment probes succeeded:

1. VS Code Language Model API exposed and invoked `GPT-5.6 Luna` with id/family/version `gpt-5.6-luna`.
2. Corporate Copilot CLI accepted `gpt-5.6-luna`, resolved to the same model, and emitted OTel telemetry.

See `preflight-results/`.

## Run-block stability rule

Do not intentionally update the Copilot CLI, switch models, or change the adapter in the middle of the first scored Family N block.

If any of the following changes unexpectedly, record it and begin a new execution block rather than mixing results silently:

- resolved model,
- CLI version,
- material CLI feature behavior,
- OTel accounting behavior,
- organization policy that changes available model/runtime behavior.

A later replication on another model or adapter is desirable, but it is a **replication**, not part of the first causal comparison.

## Cost-accounting caution

OTel token totals are adapter-level observations. They may include system/agent runtime context beyond the explicit experiment prompt.

Therefore later analysis should distinguish at least:

- explicit experiment payload size,
- observed adapter input/output tokens,
- number of model calls,
- opaque Copilot cost/AIU telemetry unless its semantics are verified.

Do not convert opaque `github.copilot.cost` or `github.copilot.aiu` values into dollars by assumption.

## Not frozen here

The following remain separate methodological choices:

- semantic evaluator model/mode,
- repetition count,
- any later independent-model replication,
- production Wiki model routing.

Choosing Luna here does **not** imply that a future personal Wiki must use Luna, Copilot CLI, or even GitHub Copilot.
