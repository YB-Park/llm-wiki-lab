# E007 Harness

Status: implementation scaffold; no scored runs yet

## Why Copilot CLI

The target daily environment is VS Code + GitHub Copilot, but manual chat UI interaction is difficult to repeat and measure consistently.

E007 therefore uses **Copilot CLI as a controlled model adapter** while reserving native VS Code workflow/automation questions for later experiments such as E010.

Official references:

- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- https://docs.github.com/en/copilot/reference/ai-models/supported-models
- https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing

## Real execution environment

The intended execution environment is a managed corporate network.

Known constraints:

- VS Code + GitHub Copilot are the permitted AI/development surface.
- ChatGPT is not reachable from the corporate network.
- GitHub push is not available from the corporate network.
- Large raw experiment artifacts therefore cannot be handed back through ChatGPT or pushed directly from the execution environment.

The harness must support a **manual-transfer-safe compact handoff**. Raw prompts, responses, wiki states, and telemetry remain local. Only a few sanitized aggregate lines should need to leave the environment.

## Model policy

`--model` is required for scored runs. Do not use Copilot Auto because model routing would become an uncontrolled experimental variable.

**GPT-5.6 Luna is the current primary candidate, not yet a frozen decision.** The rationale is operational: wiki maintenance is likely to involve many drafting, consolidation, checking, and query calls, so a lightweight low-cost model that is sufficiently capable could materially change the cost/quality frontier.

As of 2026-08-12, GitHub's public pricing lists GPT-5.6 Luna default-tier input at **$0.20 / 1M tokens** (with separate cached-input, cache-write, and output prices). Pricing and enterprise effective cost can change; every scored run family should record the actual model/config and use the effective runtime billing/credit conditions rather than assuming this historical number remains current.

Do not mix model comparison into E007. Once a concrete Luna model string/config works in the actual corporate Copilot environment, freeze it for the run family. Cross-model replication can be a later experiment.

## Experimental isolation principles

A scored call should:

1. pin a concrete model with `--model` — never `auto`,
2. use `--no-ask-user`,
3. use `--no-custom-instructions` so repo/user instructions do not silently alter conditions,
4. exclude workspace/web/agent tools unless a condition explicitly tests them,
5. behave as a pure text-in/text-out semantic transformation,
6. store the exact prompt and raw response locally,
7. keep raw OpenTelemetry local,
8. preserve CLI version and requested model in run metadata,
9. expose only aggregate/sanitized handoff data outside the run directory.

## Why tools are excluded

E007 is testing knowledge-state maintenance policies, not agent tool skill.

If one condition can inspect arbitrary workspace files, web sources, persistent Copilot memory, MCP state, or shell state, experimental inputs are no longer controlled. All allowed source/wiki state is therefore placed directly in the prompt.

Tool-using and IDE-native automation behavior belongs in later experiments.

## Telemetry

Each isolated call writes OTel locally using:

```text
COPILOT_OTEL_FILE_EXPORTER_PATH=<call>/otel.jsonl
```

The fields of interest include requested/resolved model, input/output/cache tokens, turn count, Copilot cost, and AI units where exposed by the runtime.

Raw OTel must not be manually copied out by default because it can include pseudonymous/runtime metadata. The preflight and run summarizer extract only the small fields needed for experiment handoff.

## Files

- `validate_corpus.py` — deterministic corpus/rubric consistency checks
- `copilot_cli.py` — isolated non-interactive Copilot adapter
- `preflight_copilot.py` — unrelated non-scored micro-test; emits a 3-line handoff by default
- `run_e007.py` — Family N state machine for C0–C4
- `score_deterministic.py` — deterministic scoring used by eligible queries/regression gates
- `handoff_summary.py` — creates an 8-line sanitized summary for one completed run

## Restricted-network handoff workflow

### 1. Infrastructure preflight

Run with the concrete model string available in the corporate Copilot environment:

```bash
python3 experiments/E007-long-horizon-contamination/harness/preflight_copilot.py \
  --model '<concrete-model>'
```

Default output is intentionally tiny:

```text
PREFLIGHT-HANDOFF-v0
status=PASS requested=... resolved=... cli=... wall_s=...
otel=yes in=... out=... cost=... aiu=...
```

Only those lines need to be transferred manually. `--json` is available for sanitized diagnostics if the compact output is insufficient.

### 2. Completed E007 run

After a local run, generate:

```bash
python3 experiments/E007-long-horizon-contamination/harness/handoff_summary.py \
  --run-dir experiments/E007-long-horizon-contamination/runs/<run-id>
```

It writes `handoff.txt` and `handoff.json` inside the local run directory and prints approximately eight compact lines containing only:

- run/condition/model,
- deterministic pass count and failed query IDs,
- model-call/OTel counts,
- bounded repair activity,
- aggregate token/cost fields when available,
- a short fingerprint of run-config + summary.

The handoff is intentionally small enough to type manually if no digital transfer path is available.

## Before first scored run

1. Validate Corpus C v0 and harness CI.
2. Run the unrelated preflight in the **actual corporate environment**.
3. Confirm the concrete Luna model string (or reject Luna if unavailable/unsuitable).
4. Confirm that OTel fields are sufficient and that aggregation semantics are sane.
5. Freeze model/config and semantic evaluator mode.
6. Run one non-scored infrastructure/cost dry run only.
7. Choose repetition count without inspecting comparative C0–C4 quality.
8. Begin scored Family N runs.

## Security / contamination note

Corpus C is fictional. Do not point E007 at the user's real personal wiki or sensitive corporate material.

Realistic Corpus R requires a separate privacy/data-handling review before use.
