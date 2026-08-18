# Current Handoff

Last updated: 2026-08-18 KST

This file is the **continuation checkpoint only**. Keep history/evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally reads and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine compilation/maintenance inside granted authority.**

## Current baseline — Dogfood 0.1.15

0.1.15 is on `main` via PR #156. The existing lifecycle/authority boundary remains unchanged:

> **Installed capability != workspace permission.**

- `LLM Wiki: Initialize Workspace` is explicit workspace opt-in; before it, the five Agent tool implementations are unavailable.
- `Doctor` is pure diagnostics: **0 model calls / 0 state changes**.
- `Disable Workspace (Keep Data)` removes Agent availability while preserving Wiki data.
- **RAW_MEMORY** is immutable factual/provenance evidence.
- **DERIVED_MEMORY** is noncanonical/rebuildable Agent Wiki synthesis.
- **HUMAN_KNOWLEDGE** is explicit user-confirmed belief/decision/rationale, not independent evidence.
- Changed remembered files remain pending until the human explicitly decides correction/change/dispute/supersede/independent semantics.
- Agent Wiki Luna maintenance remains **OFF by default** until explicitly granted per workspace.

Five Agent tools remain the normal loop: `#wikiMemory`, `#wikiRead`, `#rememberWikiSource`, `#rememberHumanKnowledge`, `#resolveWikiLineage`.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Retrieval remains **W0 default / X1 shadow**. Customer readiness is still **NOT READY YET**; installed multi-session P7 evidence remains the blocker.

## Retained maintenance boundaries

### Copilot CLI compatibility

The 0.1.13 compatibility fix remains active: LLM Wiki probes the installed `copilot --help` with zero model calls, requires the privacy-critical `--no-remote` boundary, applies optional flags only when that installed CLI advertises them, and converts recognized Copilot failures into bounded statuses. `compiled_provider=disabled` remains expected/healthy and is unrelated to Agent Wiki maintenance.

### Daily maintenance soft guard

The 0.1.14 behavior remains active: the positive `llmWiki.agentWikiMaintenanceDailyCallLimit` value is a **soft-guard threshold**, not a hard cap. Default `10` means the product asks once whether to `Continue Today`; approval permits further calls that local day. `0` still explicitly disables new model-backed maintenance. RAW admission is preserved if derived maintenance is declined or fails.

## 0.1.15 source-size / causal-outcome fix

Natural P7 dogfood repeatedly hit `agent_wiki_source_too_large:40491>40000`. The main conversational Agent could not see that causal failure and guessed that the maintenance soft guard had not been approved.

0.1.15 changes this boundary without adding a chunking subsystem:

- **40,000 characters is now a preferred single-pass target, not a hard failure cliff.**
- Current sources from **40,001 through 80,000 characters** are still sent to exact Luna in one maintenance pass and report `source_size_mode=oversize_single_pass`.
- Above the temporary **80,000-character ceiling**, RAW admission remains preserved but derived maintenance ends before any model call with `SKIPPED_SOURCE_TOO_LARGE`.
- The causal over-ceiling status returned to the main Agent includes bounded safe facts: `failure_code=SOURCE_TOO_LARGE`, `stage=preflight`, `model_call_attempted=no`, observed/preferred/ceiling character counts, and `soft_guard_prompted=no`.
- LLM Wiki never silently truncates a source.
- Chunk -> compile remains deferred until **natural >80k sources recur**; do not build it merely because the temporary ceiling exists.

This fixes the recurring observability failure: the main Agent should no longer need to guess whether a source-size preflight failure was caused by the soft guard, compiled provider, auth, or another unrelated state.

## Hidden maintenance usage remains the next UX question

Internal Luna consumption is still not sufficiently visible. Keep these quantities distinct:

- **maintenance model calls** — locally countable now;
- **tokens** — only exact when the transport exposes machine-readable input/output/cache usage;
- **AI credits / premium requests** — never infer from calls or tokens; report only actual upstream values.

Do not rely only on the conversational Agent to volunteer usage. The leading subsequent slice remains **product-owned maintenance usage visibility** (per-operation + cumulative counters and a lightweight VS Code surface), but first collect the 0.1.15 natural retry evidence below.

## 0.1.15 validation / artifact

PR #156 and the final main build passed the full dogfood gate. Main run `32125890602` passed:

- Python 3.9 bundled-core compatibility;
- **153 Python tests**;
- CLI smoke;
- E020 frozen zero-model contract;
- VS Code syntax/static boundary checks;
- dev Extension Host integration;
- shared-core bundle verification;
- VSIX packaging;
- unpacked packaged VSIX Extension Host validation.

New source-size tests prove:

- a **40,491-character** source crosses the old cliff and performs one single-pass model generation;
- an **80,001-character** source is classified causally before any model call and explicitly reports that the soft guard was not prompted.

Validated artifact:

- source head: `701feb5dd5c5694c8a03b54af1d181845d3c7cb7`
- main run: `32125890602`
- publisher commit: `2713a696a3cc55d44bb33a66616436069d7f727e`
- Actions artifact: `llm-wiki-dogfood-vsix` / id `9320351015`
- artifact ZIP digest: `sha256:8098c1cf5e58fff50df0448826b51b117184364d9a516b47af9b46c6355a51c2`
- `dogfood/releases/llm-wiki-dogfood-0.1.15.vsix`
- `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX bytes: `98393`
- VSIX SHA-256: `d6ee323e1cf2b3641c172e0cef64891f833e1dc5be7663a25858eace1cc34733`
- Git blob for both repo VSIX paths: `3cdcbc9f32513d9d9dc1daa386f27136bcb1f511`

The Actions artifact was independently downloaded and extracted. Its VSIX byte size, SHA-256, and `git hash-object` exactly match both in-repo release paths.

## NEXT — resume installed multi-session P7

**Start here if a session dies. Do not design another subsystem first.**

Observation log: **Issue #141**.

Immediate natural retry:

1. Install `dogfood/releases/llm-wiki-dogfood-latest.vsix` (0.1.15) over the current dogfood build.
2. Reopen the same trusted/opted-in workspace and keep existing Wiki data.
3. Keep Agent Wiki Maintenance enabled.
4. Retry the **real source around 40,491 characters that previously failed at the old 40k cliff**. Do not edit or shrink it merely for the test.
5. Expected maintenance result: `CREATED` (or `REUSED` if a valid note already exists); when generation occurs above 40k, the status should include `source_size_mode=oversize_single_pass` and the source-size metadata.
6. Observe the conversational Agent's explanation. It should no longer claim that the soft guard was unapproved merely because source size was involved.
7. Do **not** manufacture an >80k file. If a natural one appears, confirm that RAW is preserved and the Agent receives the explicit `SKIPPED_SOURCE_TOO_LARGE ... soft_guard_prompted=no` causal status; log that occurrence.
8. After this retry, resume normal cross-session recall without naming `#wikiMemory`; continue observing ambient routing and `wikiRead` follow-through.
9. Keep noting whether invisible maintenance token/AI-credit usage creates uncertainty. That remains the leading next UX candidate after this source-size retry.

## Do not start yet

- chunk compiler unless natural >80k sources recur;
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
- Copilot CLI optional flags can change independently of public docs; runtime capability probing remains authoritative.
- Positive maintenance soft-guard acknowledgement lives in VS Code workspace state; loss may cause another prompt but does not affect Wiki knowledge.
- 80k is a temporary dogfood ceiling, not a claimed Luna technical limit.
- E013/E015 evidence must remain natural; do not manufacture workload/divergence.

## Fast pointers

- Installed P7 observation log: Issue #141
- 0.1.15 source-size / causal outcomes: PR #156
- 0.1.14 maintenance soft guard: PR #154
- 0.1.13 Copilot CLI compatibility: PR #152
- 0.1.12 lifecycle/opt-in: PR #148
- Current validated VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- User guide: `dogfood/vscode/README.md`
- E020: `experiments/E020-synthetic-agent-ux/README.md`
- Reliability follow-up: Issue #132
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Backup/restore: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
