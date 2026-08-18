# Current Handoff

Last updated: 2026-08-18 KST

This file is the **continuation checkpoint only**. Keep history/evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally reads and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine compilation/maintenance inside granted authority.**

## Current baseline — Dogfood 0.1.12

0.1.12 is on `main` via PR #148. The key lifecycle boundary is now:

> **Installed capability != workspace permission.**

- Installing the VSIX does **not** opt every project into LLM Wiki.
- Before explicit `LLM Wiki: Initialize Workspace`, Agent-mode selection is `when`-gated off and the five runtime tool implementations are not registered.
- `Doctor` is pure diagnostics: **0 model calls / 0 state changes**. It never initializes, repairs, or enables a workspace.
- `Initialize Workspace` is explicit opt-in: Git safety -> Python -> human confirmation -> Core init -> integrity -> local opt-in marker -> Agent runtime enabled.
- Existing `.wiki-lab` Core files alone do not imply opt-in; this covers stores created by older dogfood behavior.
- `Disable Workspace (Keep Data)` removes the opt-in marker and Agent runtime while preserving Wiki data.
- Incomplete/damaged existing stores fail closed; Init does not recreate missing canonical history over them.

Five Agent tools remain the product loop after opt-in:

1. `#wikiMemory` — search current Raw / Derived / Human Knowledge.
2. `#wikiRead` — bounded verified immutable raw read and provenance follow.
3. `#rememberWikiSource` — explicit human-confirmed local-file admission; never auto-saves dirty documents.
4. `#rememberHumanKnowledge` — explicit user-confirmed decision/belief/rationale; zero model calls; separate from raw evidence.
5. `#resolveWikiLineage` — human-gated correction/change/dispute/supersede/independent resolution for changed remembered files.

Authority classes remain separate: **RAW_MEMORY** factual/provenance authority; **DERIVED_MEMORY** rebuildable noncanonical synthesis; **HUMAN_KNOWLEDGE** user-confirmed belief/decision, not independent evidence.

E020 remains **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Retrieval remains **W0 default / X1 shadow**. Agent Wiki Luna maintenance remains **OFF by default**.

Customer readiness: **NOT READY YET** — installed multi-session P7 evidence is the blocker.

## 0.1.12 validation / artifact

PR #148 passed Python/E020/static plus dev and unpacked packaged Extension Host validation. The runtime lifecycle test proves a valid `wikiMemory` invocation rejects before Init, succeeds after Init, and rejects again after Disable.

VS Code nuance: `vscode.lm.tools` may enumerate contributed tool metadata even while `when=false`; that metadata list is not the product definition of Agent availability. The contract is `when`-gated Agent selection plus runtime implementation registration/unregistration. See `dogfood/vscode/test/WORKSPACE-ACTIVATION.md`.

Validated main artifact:

- source run: `32103419086`
- source head: `7508eff913226647eb558ed690e0da954673e183`
- `dogfood/releases/llm-wiki-dogfood-0.1.12.vsix`
- `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- bytes: `94341`
- SHA-256: `1a8cac3520ce55e0cca3ac79dd4447b01c8f146aece436bd87d35324e35d9504`
- Git blob: `728611a2aa35c7a55827d0963f905e6dfe2641da`

The Actions artifact bytes were independently extracted and matched the repo size, SHA-256, and Git blob exactly.

## NEXT — installed multi-session P7

**Start here if a session dies. Do not design another subsystem first.**

Observation log: **Issue #141**. Put natural P7 findings there; keep this handoff short.

First 0.1.12 installed observation:

1. Install `dogfood/releases/llm-wiki-dogfood-latest.vsix`.
2. Open a trusted real workspace that has not been explicitly opted into 0.1.12.
3. Optional but useful: run Doctor before Init. Expect `NOT_INITIALIZED`/`NOT_ENABLED` or existing-store + `NOT_ENABLED`; Doctor must make no state change and Agent tools remain unavailable.
4. Protect `.wiki-lab/` from Git (`.git/info/exclude` is the local-only Alpha choice).
5. Run `LLM Wiki: Initialize Workspace` and confirm opt-in.
6. Run Doctor: expect opt-in enabled / Agent tools available / realistic evidence READY when other checks pass.
7. Keep Luna maintenance **OFF** for the first natural routing observation.
8. Ask an ordinary prior-project question where remembered knowledge should help, **without naming `#wikiMemory`**. Observe whether Agent naturally uses memory and follows important claims with `wikiRead`.
9. Continue real remember/Human Knowledge/changed-file lineage flows across later sessions and record natural friction/failures in Issue #141.

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
- E013/E015 evidence must remain natural; do not manufacture workload/divergence.

## Fast pointers

- Installed P7 observation log: Issue #141
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
