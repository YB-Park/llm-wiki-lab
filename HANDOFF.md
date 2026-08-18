# Current Handoff

Last updated: 2026-08-18 KST

This file is the **continuation checkpoint only**. Keep history/evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally reads and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine compilation/maintenance inside granted authority.**

## Current baseline — Dogfood 0.1.13

0.1.13 is on `main` via PR #152. The existing lifecycle boundary remains:

> **Installed capability != workspace permission.**

- Installing the VSIX does **not** opt every project into LLM Wiki.
- Before explicit `LLM Wiki: Initialize Workspace`, Agent-mode selection is `when`-gated off and the five runtime tool implementations are not registered.
- `Doctor` is pure diagnostics: **0 model calls / 0 state changes**. It never initializes, repairs, or enables a workspace.
- `Initialize Workspace` is explicit opt-in: Git safety -> Python -> human confirmation -> Core init -> integrity -> local opt-in marker -> Agent runtime enabled.
- `Disable Workspace (Keep Data)` removes the opt-in marker and Agent runtime while preserving Wiki data.

Five Agent tools remain the normal product loop after opt-in:

1. `#wikiMemory` — search current Raw / Derived / Human Knowledge.
2. `#wikiRead` — bounded verified immutable raw read and provenance follow.
3. `#rememberWikiSource` — explicit human-confirmed local-file admission; never auto-saves dirty documents.
4. `#rememberHumanKnowledge` — explicit user-confirmed decision/belief/rationale; zero model calls; separate from raw evidence.
5. `#resolveWikiLineage` — human-gated correction/change/dispute/supersede/independent resolution for changed remembered files.

Authority classes remain separate: **RAW_MEMORY** factual/provenance authority; **DERIVED_MEMORY** rebuildable noncanonical synthesis; **HUMAN_KNOWLEDGE** user-confirmed belief/decision, not independent evidence.

E020 remains **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Retrieval remains **W0 default / X1 shadow**. Agent Wiki Luna maintenance remains **OFF by default** until explicitly granted per workspace.

Customer readiness: **NOT READY YET** — installed multi-session P7 evidence is still the blocker.

## 0.1.13 Copilot CLI compatibility boundary

P7 installed dogfood exposed a real external-runtime compatibility failure after updating Copilot CLI to `1.0.80`:

- a simple `copilot -p ... --model gpt-5.6-luna` call succeeded;
- the installed `copilot --help` no longer advertised `--max-ai-credits` or `--no-remote-export`;
- 0.1.12 hardcoded both flags, so Agent Wiki maintenance exited `1` after RAW admission;
- the opaque `FAILED_AFTER_RAW_ADMISSION` result caused the main Agent to incorrectly guess that `compiled_provider=disabled` was the cause.

0.1.13 fixes that boundary:

- before a maintenance model call, LLM Wiki probes the **installed** `copilot --help` with zero model calls;
- `--no-remote` remains required;
- optional flags such as `--no-remote-export` and `--max-ai-credits` are passed only when that installed binary advertises them;
- the durable per-workspace daily maintenance-call reservation remains enforced independently of optional CLI credit-flag support;
- recognized Copilot failures are translated into bounded maintenance statuses such as CLI argument/auth/model/output-contract failures instead of reflecting arbitrary stderr or collapsing everything into one opaque failure.

`compiled_provider=disabled` remains **EXPECTED / healthy** for the current Core and is unrelated to Agent Wiki Luna maintenance.

## 0.1.13 validation / artifact

PR #152 final branch validation passed Python 3.9 compatibility, **150 Python tests**, E020, static checks, dev Extension Host, VSIX packaging, and unpacked packaged Extension Host validation. A first packaged test run exposed CI workspace-state leakage from the preceding dev Extension Host; the workflow now removes the previous `.wiki-lab` before the packaged fresh-workspace test.

Validated main artifact:

- source run: `32112387118`
- source head: `683633bc2771550f0093cccc9f82bb63dfedd503`
- publisher commit: `f95a9163a341c48dba7381de2fb5d8d71569b0ac`
- Actions artifact: `llm-wiki-dogfood-vsix` / id `9315393587`
- artifact ZIP digest: `sha256:59e75d74f4b428c595ea66b3b76aaef1822b18c28f3e10270310bc3e92c2dc15`
- `dogfood/releases/llm-wiki-dogfood-0.1.13.vsix`
- `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX bytes: `96012`
- VSIX SHA-256: `ee085db51ad84e2b927008aff50c572b73fad5b24b27cf0594c749a3e3967c20`
- Git blob for both repo VSIX paths: `0de0371ef746b26135f44fe8104e5ea41cf47786`

The Actions artifact was independently downloaded and extracted. Its VSIX size, SHA-256, and `git hash-object` exactly match both in-repo release paths.

## NEXT — resume installed multi-session P7

**Start here if a session dies. Do not design another subsystem first.**

Observation log: **Issue #141**. Put natural P7 findings there; keep this handoff short.

Immediate next run:

1. Install `dogfood/releases/llm-wiki-dogfood-latest.vsix` (0.1.13) over the prior dogfood build.
2. Open the trusted target workspace. Existing local Wiki data / opt-in may remain; do not recreate or delete it merely for this retry.
3. Optionally run Doctor. `Compiled provider: disabled` is expected. Confirm local Wiki readiness and Copilot CLI presence.
4. Ensure `LLM Wiki: Configure Agent Wiki Maintenance` is **ENABLED** for this workspace.
5. Retry one small, non-sensitive current source that was already admitted (remember the file again if needed) so Agent Wiki source-note maintenance runs.
6. Expect derived maintenance to return `CREATED` or `REUSED`. If it fails, the 0.1.13 status should identify the failure class rather than inviting a `compiled_provider` guess.
7. Once a derived note exists, start a fresh normal Agent chat/session and ask an ordinary historical project question **without naming `#wikiMemory`**. Observe ambient routing and whether important derived claims are followed with `wikiRead`.
8. Continue across later sessions and record only natural friction/failures in Issue #141.

The next product slice must come from repeated installed evidence, not another speculative subsystem.

## Experiment closeouts

- **E021 concept compounding:** narrow PASS with exact `gpt-5.6-luna`, 3 calls, 0 semantic rerolls, but retained Actions execute-job provenance limitation. Do not rerun or promote automatic concept routing from it.
- **E022 v4 translation smoke:** exact GPT-5.4 + Claude Sonnet 4.6, 2 generations, 0 rerolls, both PASS on the frozen malicious serialization boundary. This is not a universal prompt-injection guarantee. Do not rerun just to strengthen the record.

## Do not start yet

- vector/graph/ontology infrastructure;
- background source watching;
- broad automatic contradiction resolution;
- full Tree View/activity system without observed need;
- federation or X2 without recurring natural evidence;
- automatic concept routing from E021 alone;
- paid reruns of frozen E017/E018/E019/E021/E022 cases.

## Known non-blocking edges

- Issue #132: deletion detection for `agent-state.json` and relation/pending crash window.
- Human Knowledge file deletion is not independently detectable without an index.
- Relation append and pending-state resolution are not one cross-process transaction.
- Copilot CLI optional flags can change independently of public docs; runtime capability probing is now the compatibility boundary for the two observed optional flags.
- E013/E015 evidence must remain natural; do not manufacture workload/divergence.

## Fast pointers

- Installed P7 observation log: Issue #141
- 0.1.13 Copilot CLI compatibility: PR #152
- 0.1.12 lifecycle/opt-in: PR #148
- VSIX publisher guidance: PR #149
- Agent-tool availability contract note: PR #150 / `dogfood/vscode/test/WORKSPACE-ACTIVATION.md`
- Current validated VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- User guide: `dogfood/vscode/README.md`
- E020: `experiments/E020-synthetic-agent-ux/README.md`
- E021: Issue #131 / historical PR #133 / `experiments/E021-concept-compounding/results-v0.md`
- E022: Issue #135 / PR #136 / `experiments/E022-v4-translation-smoke/results-v0.md`
- Reliability follow-up: Issue #132
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Backup/restore: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
