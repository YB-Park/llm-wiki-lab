# E007 Harness

Status: **ready for the first scored Family N block after one non-scored full-harness rehearsal**

## Research boundary

E007 is testing knowledge-state maintenance policies, not Copilot skill or model ranking.

GPT-5.6 Luna and Copilot CLI are frozen **experimental equipment** for the first block so that policy differences are easier to interpret. Production model/provider decisions belong later.

The project-level objective remains to find the minimum architecture and operating discipline that lets useful understanding compound faster than error and maintenance debt.

## Why Copilot CLI

The target daily environment is VS Code + GitHub Copilot, but manual chat UI interaction is difficult to repeat and measure consistently.

E007 therefore uses **Copilot CLI as a controlled text-in/text-out adapter** while reserving native VS Code workflow/automation questions for later experiments such as E010.

## Real execution environment

The intended execution environment is a managed corporate network.

Known constraints:

- VS Code + GitHub Copilot are the permitted AI/development surface.
- ChatGPT is not reachable from the corporate network.
- GitHub push is not available from the corporate network.
- Raw experiment artifacts therefore remain local.
- Only compact sanitized handoff text should need to leave the environment.

## Frozen first-block profile

See `../execution-profile-v0.md`, `../repetition-plan-v0.md`, and `../run-plan-v0.json`.

- adapter: non-interactive Copilot CLI
- model: `gpt-5.6-luna`
- observed target CLI: `GitHub Copilot CLI 1.0.35`
- OTel: enabled, message-content capture disabled
- model auto-routing: forbidden
- repo/user custom instructions: disabled
- workspace/web/shell/memory-style tools: excluded from scored calls
- repetitions: 3 per condition, 15 total runs in frozen interleaved order

Do not intentionally update the CLI, switch models, reorder runs, or tune prompts mid-block.

## Experimental isolation principles

A scored call should:

1. pin a concrete model — never `auto`,
2. disable user interaction/custom instructions,
3. exclude workspace/web/agent tools unless a condition explicitly tests them,
4. behave as a pure text-in/text-out semantic transformation,
5. store exact prompt and raw response locally,
6. keep raw OTel local,
7. preserve CLI version and requested/resolved model metadata,
8. expose only aggregate/sanitized handoff data outside the run directory.

## Telemetry and cost

Each isolated call writes OTel locally. The harness also records explicit prompt/response payload sizes.

Keep these concepts separate:

- explicit experiment payload size,
- observed adapter input/output/cache tokens,
- model-call count,
- logical cost category (`maintenance_update`, `transition_verify`, `transition_repair`, `regression_probe`, `regression_repair`, `primary_answer`),
- opaque Copilot cost/AIU fields unless their semantics are verified.

Do not convert opaque cost/AIU telemetry to dollars by assumption.

## Key files

- `validate_corpus.py` — deterministic corpus/rubric consistency checks
- `copilot_cli.py` — isolated non-interactive Copilot adapter
- `preflight_copilot.py` — unrelated micro model/OTel preflight
- `full_harness_preflight.py` — unrelated Zephyr end-to-end rehearsal; **does not use Corpus C**
- `run_e007.py` — Family N C0–C4 state machine
- `run_family_n.py` — executes the frozen 15-run plan and resumes safely
- `score_deterministic.py` — deterministic query/regression scoring
- `structural_metrics.py` — Wiki/raw ratio, growth, churn, provenance-description metrics
- `cost_metrics.py` — logical cost ledger by call category
- `handoff_summary.py` — compact sanitized summary for one run
- `evaluate_semantic.py` — blinded two-pass semantic evaluation for one run
- `evaluate_family.py` — resumable semantic evaluation wrapper for the frozen family
- `summarize_family.py` — compact cross-run family handoff

## Execution workflow

### 0. Non-scored full-harness rehearsal — run once

This is the final infrastructure check before scored execution. It uses an unrelated fictional Zephyr micro-world and exercises update, verify, repair, regression-repair, answer JSON, and OTel contracts.

```bash
python3 experiments/E007-long-horizon-contamination/harness/full_harness_preflight.py
```

Expected compact output begins with:

```text
FULL-HARNESS-PREFLIGHT-v0
status=PASS ...
calls=7 otel=7/7
...
corpus_c=NOT_USED quality_result=NONE
```

The rehearsal may expose infrastructure bugs only. It must not be used to tune E007 conditions, prompts, repetition count, or expected outcome.

### 1. Execute the frozen primary block

```bash
python3 experiments/E007-long-horizon-contamination/harness/run_family_n.py
```

The runner follows `run-plan-v0.json`, never silently rerolls incomplete runs, and writes raw artifacts under ignored local `runs/` directories.

For operational chunking without changing order, `--limit N` may be used. Re-running the command skips completed runs and continues the frozen sequence.

### 2. Run frozen post-hoc semantic evaluation

After all 15 primary runs complete:

```bash
python3 experiments/E007-long-horizon-contamination/harness/evaluate_family.py
```

Semantic evaluation is analysis-only and never feeds back into C0–C4 maintenance.

### 3. Produce the compact family handoff

```bash
python3 experiments/E007-long-horizon-contamination/harness/summarize_family.py
```

This prints the small sanitized cross-condition summary that can be manually transferred outside the restricted network. Raw prompts, Wiki states, answers, and OTel remain local.

## Interpretation rules

Do not reduce E007 to one accuracy leaderboard.

Before any headline conclusion inspect jointly:

- deterministic and semantic correctness,
- omission/unsupported/temporal/provenance failures,
- Wiki/raw compression ratio,
- rewrite churn,
- verifier/repair intervention yield,
- regression false positives and repair-induced damage,
- post-hoc state integrity,
- lifecycle cost by category,
- stochastic variation across repetitions.

A safeguard that wins only by copying most raw text, rewriting everything, or spending unlimited inference is a trade-off, not an unconditional success.

See `../pre-scoring-red-team-review-v0.md` and `../analysis-protocol-v0.md`.

## Security / contamination note

Corpus C and the rehearsal micro-world are fictional.

Do not point E007 at a real personal Wiki or sensitive corporate material. Realistic Corpus R requires a separate privacy/data-handling review before use.
