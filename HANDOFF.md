# Current Handoff

Last updated: 2026-08-19 KST

This file is the **continuation checkpoint only**. Keep historical evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally reads and maintains it inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

The normal product loop is ordinary VS Code Agent conversation. Users should not need to learn Wiki tool names or internal storage concepts.

## Current baseline — Dogfood 0.1.16

0.1.16 is released from main via PR #159.

Core authority remains unchanged:

> **Installed capability != workspace permission.**

- **Set Up Project Memory** is the explicit per-workspace opt-in. Before opt-in, Agent tool implementations are unavailable.
- **Check Setup and Health** is pure diagnostics: **0 model calls / 0 state changes**.
- **Disable for This Workspace** removes Agent availability while preserving Wiki data.
- New source bytes require a product-owned human confirmation before durable evidence admission.
- **RAW_MEMORY** remains immutable factual/provenance evidence.
- **DERIVED_MEMORY** remains noncanonical/rebuildable AI-maintained synthesis.
- **HUMAN_KNOWLEDGE** remains explicit user-confirmed decision/belief/rationale, not independent evidence.
- Changed remembered files remain pending until the human explicitly decides correction/change/dispute/supersede/independent semantics.
- AI summaries remain **OFF by default** until explicitly granted per workspace.

The five Agent tools still implement the model-facing contract, but normal users should not need to invoke or understand them directly.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Retrieval remains **W0 default / X1 shadow**. Customer readiness still depends on natural installed multi-session evidence; synthetic green tests do not substitute for real project use.

## 0.1.16 release UX baseline

### First-run and everyday UX

- Native VS Code Walkthrough explains four steps: local/user-controlled project memory -> explicit workspace setup -> optional AI summaries/Copilot setup -> normal Agent chat.
- Normal UI language uses **project memory**, **AI summaries**, **saved evidence**, and **confirmed project knowledge** instead of leading with implementation terminology.
- Default Command Palette surface is intentionally small: Set Up Project Memory, Check Setup and Health, Configure AI Summaries, Disable for This Workspace. Legacy/manual IDs remain available internally but hidden from the default Palette.
- Status bar represents workspace project-memory state, not filing topic, and disappears immediately when disabled.
- Multi-root workspaces fail closed in 0.1.16 instead of silently selecting the first folder. True multi-root semantics remain deferred.

### Install / prerequisite recovery

- Python is auto-discovered when no override is configured:
  - Windows: `python` -> `py` -> `python3`
  - macOS/Linux: `python3` -> `python`
- Setup, Agent tools, and advanced commands share the same Python resolver.
- Check Setup and Health distinguishes **Copilot CLI executable presence** from **actual model-call readiness**, which the zero-model diagnostic intentionally does not claim to verify.
- Copilot CLI capability probing remains authoritative over documentation/version assumptions. `compiled_provider=disabled` remains expected and unrelated to AI-summary maintenance.

### Notification / confirmation policy

Routine success notifications are quiet. Modal confirmation is reserved for genuine user decisions:

- enabling project memory for a workspace;
- admitting **new source bytes** as durable evidence;
- saving Human Knowledge;
- deciding changed-source lineage semantics;
- granting AI-summary evidence sending;
- the daily AI-summary spend checkpoint.

Do **not** remove these authority confirmations merely to reduce clicks without natural evidence that a safer equivalent exists.

One deliberate P2 reduction is shipped: repeating an explicit remember request for the **exact same current workspace-file bytes** is a no-op reuse. It produces no new RAW admission, no canonical append, reuses the same source ID, and does not show a second source-admission modal. Optional AI-summary reuse/maintenance still follows the existing workspace grant and spend guard.

### AI-summary soft guard

The positive `llmWiki.agentWikiMaintenanceDailyCallLimit` remains a **soft-guard threshold**, not a hard cap. Default `10` means the product asks at the threshold and offers:

- **Continue Today** — keep model-backed AI summaries running for the rest of that local day;
- **Pause AI Summaries Today** — stop further model-backed summaries for that local day/threshold without changing Wiki knowledge.

Closing the dialog is not silently interpreted as a day-long pause. `0` still explicitly disables new model-backed maintenance generation. RAW evidence remains preserved when optional derived maintenance is paused, declined, or fails.

### Error / support contract

- Maintenance failures return bounded causal fields to the conversational Agent, including `failure_code`, `stage`, and `model_call_attempted` where known.
- Arbitrary subprocess stderr/traceback is not passed directly to the Agent. Unknown process failures collapse to a bounded generic code; spoof/leak tests cover this boundary.
- User-facing failures explain what was preserved and provide a next action rather than exposing implementation traceback.
- Native VS Code **Issue Reporter** integration is available through `issue/reporter` / `vscode.openIssueReporter`.
- Attached diagnostic metadata is deliberately bounded: extension/VS Code version, platform, workspace mode, project-memory state, Python presence/source, Git privacy, AI-summary state, and Copilot executable presence. It must not include project evidence, prompts, source text, local paths, usernames, hostnames, or environment variables.

## Retained maintenance boundaries

### Copilot CLI compatibility

The 0.1.13 capability-aware adapter remains active. LLM Wiki probes the installed `copilot --help` with zero model calls, keeps the privacy boundary, and applies optional CLI flags only when the installed runtime advertises them. Runtime capability is the source of truth; do not treat a version range alone as sufficient compatibility proof.

### Source size

The 0.1.15 source-size policy remains active:

- <=40,000 characters: preferred single-pass range;
- 40,001–80,000: still one Luna maintenance pass, reported as `oversize_single_pass`;
- >80,000: RAW admission remains preserved, derived maintenance stops before model call with causal `SKIPPED_SOURCE_TOO_LARGE` metadata;
- never silently truncate.

Do not build chunk -> compile merely because the temporary ceiling exists. Add it only if natural >80k sources recur often enough to justify the complexity.

## Hidden maintenance usage is the leading UX follow-up

Internal Luna consumption is still not sufficiently visible to the user. Keep these quantities distinct:

- **maintenance model calls** — locally countable;
- **tokens** — exact only when the transport exposes machine-readable input/output/cache usage;
- **AI credits / premium requests** — never infer from calls or tokens; report only actual upstream values.

Do not rely on the conversational Agent to volunteer usage. A future product-owned usage surface should be lightweight and visible even when the main Agent omits it. Candidate shape: per-operation + daily cumulative calls/tokens where known, explicit `unknown` for upstream billing units not reported, and no fake conversion from calls to credits.

Do not switch transports solely to obtain a prettier counter without first validating reliability/privacy/compatibility implications.

## 0.1.16 validation / artifact

PR #159 final clean head: `be4390af82aa9ec5749b53fdc2fd2ad5032a55a1`.

Final PR VS Code Dogfood run `32204630675` passed:

- Python 3.9 bundled-core compatibility;
- **153 Python tests**;
- CLI smoke;
- E020 frozen zero-model contract;
- syntax/static release UX boundaries;
- bounded process-error spoof/leak tests;
- Windows/macOS/Linux Python runtime policy tests;
- dev Extension Host integration;
- exact-current-bytes no-op reuse runtime regression (same source ID, no manifest append);
- shared-core bundle verification;
- VSIX packaging;
- unpacked packaged VSIX Extension Host validation.

Merged source:

- PR #159 merge/source commit: `e9370663d4763ae0f29d67c572d45c5b80f6c120`
- validated main run: `32204779167`
- Actions artifact: `llm-wiki-dogfood-vsix` / id `9348765994`
- artifact ZIP digest: `sha256:deb64b2bfd5f689571ed92b3eeb94bcfae9266d612b9fbb573019049df229d25`
- publisher commit: `3366df98e33dabbe72d00d396c2ea1820e50d9a4`
- `dogfood/releases/llm-wiki-dogfood-0.1.16.vsix`
- `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX bytes: `102811`
- VSIX SHA-256: `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`
- Git blob for both repo VSIX paths: `025c90bba243e7594c8e2b621c28bd51e5b9acd3`

The main Actions artifact was independently downloaded and extracted. Its VSIX byte size, SHA-256, and `git hash-object` exactly match both in-repo release paths.

## NEXT — natural installed multi-session use

Observation log: **Issue #141**.

Do not manufacture workload simply to make the product look validated. Real-project dogfood will take time and that is expected.

During ordinary use, watch for:

1. **First-run clarity** — does the Walkthrough/setup path explain enough without forcing the user to learn internals?
2. **Popup fatigue** — do remaining authority modals occur only when the user perceives a real decision? In particular, confirm that exact-same-byte repeated remembers no longer show the source-admission modal.
3. **Soft-guard behavior** — does Continue Today / Pause AI Summaries Today feel understandable, and is the threshold useful at all?
4. **Agent routing** — can the main Agent naturally recover history without the user naming `#wikiMemory`, and does it follow load-bearing hits with verified source reads when needed?
5. **Causal failure reporting** — does the conversational Agent describe source-size/auth/model/CLI failures from actual bounded outcome fields rather than inventing causes?
6. **Usage uncertainty** — when internal Luna maintenance runs, how strongly does the lack of token/AI-credit visibility bother the user? This is the leading candidate for the next deliberate UX slice.
7. **Navigation need** — do users actually miss a dedicated Tree/View? 0.1.16 intentionally adds none; build one only if natural behavior shows a recurring need.
8. **Long-term value** — days/weeks later, does project memory recover reasoning that would otherwise have been lost?

## Do not start merely because it is available

- chunk compiler unless natural >80k sources recur;
- vector/graph/ontology infrastructure;
- background source watching;
- broad automatic contradiction resolution;
- permanent Tree View/activity UI without observed need;
- federation or X2 without recurring natural evidence;
- automatic concept routing from E021 alone;
- paid reruns of frozen E017/E018/E019/E021/E022 cases.

## Known non-blocking edges

- Issue #132: deletion detection for `agent-state.json` and relation/pending crash window.
- Human Knowledge file deletion is not independently detectable without an index.
- Relation append and pending-state resolution are not one cross-process transaction.
- Copilot CLI optional flags can change independently of public docs; runtime capability probing remains authoritative.
- 80k is a temporary product ceiling, not a claimed Luna technical limit.
- E013/E015 evidence must remain natural; do not manufacture workload/divergence.

## Fast pointers

- Installed/natural dogfood log: Issue #141
- Release UX audit: Issue #158 / `docs/13-vscode-release-ux-audit.md`
- 0.1.16 release UX: PR #159
- 0.1.15 source-size / causal outcomes: PR #156
- 0.1.14 maintenance soft guard: PR #154
- 0.1.13 Copilot CLI compatibility: PR #152
- 0.1.12 lifecycle/opt-in: PR #148
- Current validated VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- User guide: `dogfood/vscode/README.md`
- Reliability follow-up: Issue #132
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Backup/restore: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
