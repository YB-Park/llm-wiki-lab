# Current Handoff

Last updated: 2026-08-18 KST

This file is the **continuation checkpoint only**. Keep history/evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally reads and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine compilation/maintenance inside granted authority.**

## Current baseline — Dogfood 0.1.14

0.1.14 is on `main` via PR #154. The lifecycle boundary remains:

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

## 0.1.13 Copilot CLI compatibility boundary retained

P7 installed dogfood exposed a real external-runtime compatibility failure after updating Copilot CLI to `1.0.80`: the installed CLI no longer advertised `--max-ai-credits` or `--no-remote-export`, while 0.1.12 hardcoded both. A simple Luna call worked, but maintenance exited `1` after RAW admission.

The fix retained in 0.1.14 is:

- probe the **installed** `copilot --help` with zero model calls before model-backed maintenance;
- keep `--no-remote` required;
- pass optional flags such as `--no-remote-export` and `--max-ai-credits` only when that binary advertises them;
- translate recognized Copilot failures into bounded maintenance statuses instead of reflecting arbitrary stderr.

`compiled_provider=disabled` remains **EXPECTED / healthy** for the current Core and is unrelated to Agent Wiki Luna maintenance.

## 0.1.14 maintenance soft guard

Natural P7 use showed the previous default daily hard cap of `10` model-backed Agent Wiki maintenance calls was too blunt for ordinary batch maintenance.

0.1.14 changes the positive daily threshold into a **soft guard**:

- `llmWiki.agentWikiMaintenanceDailyCallLimit` keeps its setting name for compatibility and defaults to `10`;
- positive values are advisory thresholds, **not hard caps**;
- before the first new model-backed call after the threshold has already been reached, VS Code asks whether to `Continue Today`;
- after approval, maintenance can continue for the rest of that local day without the durable counter hard-blocking further calls;
- declining skips only optional derived Agent Wiki maintenance; RAW evidence was already admitted and remains preserved;
- `0` intentionally retains its prior meaning: disable new model-backed maintenance generations;
- same-source note `REUSED` remains zero-model and is resolved before the soft guard;
- `.wiki-lab/agent-state.json` durably records model-call reservations before external calls but no longer enforces a positive product cap;
- the soft-guard acknowledgement is VS Code workspace UI state, not epistemic/canonical Wiki state.

The guard is provisional dogfood UX. Installed evidence should determine whether the threshold should move, become less prominent, or disappear.

## Hidden maintenance usage is the next UX question

The user can now let maintenance continue, but internal Luna consumption is still not sufficiently visible.

Keep these quantities distinct:

- **maintenance model calls** — locally countable now;
- **tokens** — input/output/cache usage only when the Copilot transport exposes reliable machine-readable usage;
- **AI credits / premium requests** — never infer from token or call count; report only when GitHub exposes the actual value.

Do not rely only on the conversational Agent to volunteer usage. A likely next P7 slice is product-owned maintenance usage visibility: short per-tool operation + cumulative counters, plus a lightweight VS Code surface such as status bar/hover. Exact token metering should be investigated against current Copilot CLI/ACP usage output before changing transport. Unknown values must stay explicitly unknown.

## 0.1.14 validation / artifact

PR #154 validation passed after one infrastructure-only retry: the first dev Extension Host attempt failed while `@vscode/test` was resolving/downloading VS Code with `ETIMEDOUT`; no extension test had begun. The rerun passed.

Validated main run `32118652040` passed:

- Python 3.9 bundled-core compatibility;
- **150 Python tests**;
- CLI smoke;
- E020 frozen zero-model contract;
- VS Code syntax/static boundary checks;
- dev Extension Host integration;
- shared-core bundle verification;
- VSIX packaging;
- unpacked packaged VSIX Extension Host validation.

Validated main artifact:

- source run: `32118652040`
- source head: `5ce0b49bb009b8a13632ced2352ef767c26db68f`
- publisher commit: `16bf631c734b6680b5befa24202aac9e4d6b8f44`
- Actions artifact: `llm-wiki-dogfood-vsix` / id `9317704330`
- artifact ZIP digest: `sha256:bf38434792905cf2f6dfc8b03d70abf9bf3b33223c6bd77ba548b3a87901273e`
- `dogfood/releases/llm-wiki-dogfood-0.1.14.vsix`
- `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX bytes: `97090`
- VSIX SHA-256: `7ddce126b8877957928acd901ab1b762d2a9a5673201b6bce32a7426a419216c`
- Git blob for both repo VSIX paths: `d8314da1cd4e3a2d3e2befdb21166e2ada557fe2`

The Actions artifact was independently downloaded and extracted. Its VSIX size, SHA-256, and `git hash-object` exactly match both in-repo release paths.

## NEXT — resume installed multi-session P7

**Start here if a session dies. Do not design another subsystem first.**

Observation log: **Issue #141**. Put natural P7 findings there; keep this handoff short.

Immediate next run:

1. Install `dogfood/releases/llm-wiki-dogfood-latest.vsix` (0.1.14) over the prior dogfood build.
2. Reopen the same trusted workspace and preserve the existing local Wiki/opt-in.
3. Keep `LLM Wiki: Configure Agent Wiki Maintenance` enabled if testing maintenance.
4. Continue a natural multi-file remember/maintenance task past the configured default threshold of `10` new model-backed calls.
5. Confirm the threshold no longer becomes a hard stop. At the boundary, the product should explain that RAW is already saved and offer `Continue Today`; after approval, later maintenance calls that day should continue.
6. Observe whether this checkpoint is actually useful or merely annoying. Record that natural reaction in Issue #141.
7. Separately observe whether the lack of visible internal maintenance token/AI-credit usage creates uncertainty. This is the leading next UX slice; do not guess usage values.
8. Continue normal cross-session recall without naming `#wikiMemory` and watch ambient routing / `wikiRead` follow-through.

The next product slice must remain grounded in installed evidence. Current leading candidate: **maintenance usage visibility**, not another memory subsystem.

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
- Copilot CLI optional flags can change independently of public docs; runtime capability probing is the compatibility boundary for the observed optional flags.
- Positive maintenance soft-guard acknowledgement lives in VS Code workspace state; loss of that UI state may cause another prompt but does not affect Wiki knowledge.
- E013/E015 evidence must remain natural; do not manufacture workload/divergence.

## Fast pointers

- Installed P7 observation log: Issue #141
- 0.1.14 maintenance soft guard: PR #154
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
