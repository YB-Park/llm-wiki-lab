# LLM Wiki for VS Code — 0.1.16 release candidate

LLM Wiki gives your coding Agent **durable project memory that you control**.

Install the extension, enable project memory for a trusted workspace, and keep using normal Agent chat. The Agent can look up saved project context when it is useful. Things that become official project memory—or change what earlier memory means—stay explicit and human-approved.

## Get started

1. Install the `.vsix` with **Extensions → … → Install from VSIX…**.
2. Open **one trusted local workspace folder**. Multi-root workspaces are intentionally not enabled in 0.1.16.
3. Follow the built-in **Get started with LLM Wiki** walkthrough, or run **LLM Wiki: Set Up Project Memory**.
4. If the project is a Git repository, keep the private memory directory out of Git. With the default `.wiki-lab/`, use `.git/info/exclude` for a local-only choice or `.gitignore` for a project-wide choice.
5. Continue in normal Agent chat.

Installing LLM Wiki gives VS Code the capability. **Setting up a workspace gives the Agent permission to use it there.** Existing `.wiki-lab` data alone never silently enables Agent access.

## What normal use feels like

You do not need to learn LLM Wiki tool names or operate a separate database UI.

A normal historical question can simply be:

> “왜 예전에 Redis를 안 쓰기로 했지?”

The Agent may search project memory, follow a relevant result back to verified saved evidence, and answer with the recovered context.

When you want to preserve something, say it naturally:

> “이 파일 프로젝트 기억에 저장해.”

or:

> “우리는 운영 복잡성 때문에 Redis를 아직 쓰지 않기로 결정했어. 이 결정 기억해.”

LLM Wiki keeps the final authority boundary explicit. Saving durable source evidence, saving your confirmed decision/rationale, and deciding whether a changed source is a correction/change/dispute/replacement all require product-owned confirmation.

## The four normal commands

The default Command Palette intentionally stays small:

- **LLM Wiki: Set Up Project Memory** — explicitly enable this workspace.
- **LLM Wiki: Check Setup and Health** — read-only diagnostics; zero model calls and zero state changes.
- **LLM Wiki: Configure AI Summaries** — optional Copilot-backed summaries; off by default.
- **LLM Wiki: Disable for This Workspace** — stop Agent access while keeping saved Wiki data on disk.

Advanced/manual dogfood commands remain registered for testing and explicit fallback workflows, but they are hidden from the default Command Palette.

## Project memory is local-first

The default private store is `.wiki-lab/` inside the workspace. Treat it as sensitive project data and keep it out of Git.

The directory can contain:

- immutable copies of explicitly saved source evidence;
- history describing corrections, changes over time, disputes, and replacements;
- your explicitly confirmed project knowledge and rationale;
- optional rebuildable AI summaries;
- local pending decisions and source-location metadata;
- the separate workspace opt-in marker controlling Agent-tool availability.

Back up the **whole directory as one private snapshot** rather than copying individual files. See `docs/11-local-backup-restore.md` for the longer operating note.

## Workspace permission boundary

LLM Wiki does not activate itself for every project after installation.

Before **Set Up Project Memory** succeeds:

- LLM Wiki Agent tools are hidden by the VS Code contribution condition;
- runtime tool implementations are not registered;
- no model call is made by setup or health checks.

Setup verifies the local store and Git privacy, then writes a separate local opt-in marker. **Disable for This Workspace** removes only that marker. Saved Wiki data remains intact and Agent tools are unregistered again immediately.

0.1.16 intentionally supports one workspace folder at a time. A multi-root workspace does not silently pick the first project and enable memory against it.

## Python runtime

The bundled local core requires Python 3.9+.

`llmWiki.pythonExecutable` defaults to an empty value, which means **auto-detect**:

- Windows: `python`, then `py`, then `python3`;
- macOS/Linux: `python3`, then `python`.

If you explicitly configure an executable, LLM Wiki respects that value rather than silently falling back to another runtime.

If Python cannot be started, setup stays disabled and offers a direct path to LLM Wiki settings instead of creating a partial workspace opt-in.

## AI summaries are optional

Local project memory works without GitHub Copilot CLI and without AI summaries.

**LLM Wiki: Configure AI Summaries** controls a separate workspace-scoped outbound-data grant and is **OFF by default**. When enabled, after you explicitly save a source and no unresolved history decision blocks it, that saved source may be sent to GitHub Copilot using exact `gpt-5.6-luna` to create or reuse a source-scoped summary.

AI summaries are navigation aids. They never replace saved source evidence and never become your confirmed project decision automatically.

If Copilot CLI is not ready:

1. [Install GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli).
2. Run `copilot login` and complete GitHub authentication.
3. Run **LLM Wiki: Check Setup and Health** again.

An organization or enterprise policy can disable Copilot CLI even when the executable exists. For that reason the zero-model health check distinguishes:

- **Copilot CLI executable: FOUND / NOT FOUND**;
- **AI-summary model-call readiness: NOT VERIFIED**.

The health command never makes a model call just to prove authentication or model access.

### AI-summary size and spend controls

The current dogfood policy uses a 40,000-character preferred single-pass target and a temporary 80,000-character hard ceiling. Sources from 40,001–80,000 characters may still use one summary pass; above 80,000 characters summary generation stops before a model call while the saved raw source remains intact.

Two settings provide visibility/control:

- `llmWiki.agentWikiMaintenanceMaxAiCredits` — preferred per-summary Copilot guard, default `30`, used only when the installed CLI advertises the corresponding flag;
- `llmWiki.agentWikiMaintenanceDailyCallLimit` — compatibility name for the daily soft-guard threshold, default `10`; `0` disables new model-backed summary generation. A positive threshold prompts once before continuing for the rest of that day and is not a hard billing cap.

A failed or declined summary step never rolls back source admission.

## Check Setup and Health

**LLM Wiki: Check Setup and Health** is a pure diagnostic command:

- **0 model calls**;
- **0 state changes**;
- no initialization;
- no repair;
- no source/prompt/evidence content printed.

The first section is user-oriented and reports:

- Project memory: ON / OFF / NOT SET UP;
- Local memory store;
- Python runtime;
- Git privacy;
- local data integrity;
- AI summaries;
- Copilot CLI executable presence;
- model-call readiness as explicitly unverified by the zero-model check;
- a concrete next action when known.

Technical details follow below. `compiled_provider=disabled` is expected and is **not used by AI summaries**.

## Errors and recovery

Release UX uses two bounded representations of failures.

For the user, LLM Wiki should say what failed, what was preserved, and what action to take next. Routine errors do not dump arbitrary tracebacks, local paths, source text, prompts, or secrets into notifications.

For the Agent, recoverable tool failures expose stable fields such as `failure_code`, `stage`, and `model_call_attempted` where they matter. Arbitrary subprocess stderr is not passed through as model-visible diagnosis material. Unknown subprocess detail collapses to a generic bounded failure code.

The process-error classifier only accepts a small allowlist of final exception codes and is covered by spoof/leak tests so source text cannot manufacture a false Copilot diagnosis.

## Confirmation policy

Modal dialogs are intentionally rare and reserved for boundaries where the user must make an immediate authority/privacy/spend decision:

- enable or disable project memory for this workspace;
- save a local file as durable project evidence;
- save your confirmed project knowledge/decision;
- resolve what changed saved revisions mean;
- turn on AI summaries;
- continue optional model-backed summaries after the daily soft-guard reminder.

Routine success, health output, search/read, topic filing, and ordinary diagnostics should not create repeated blocking dialogs.

Whether an explicit chat request like “remember this file” can eventually replace the second source-admission modal is deliberately **not** decided synthetically. That is an evidence-dependent dogfood question because it changes an authority boundary.

## Trust model — advanced

Normal users do not need these internal labels, but they define the product contract:

- **RAW_MEMORY** — immutable admitted source evidence; factual/provenance authority.
- **DERIVED_MEMORY** — AI-created summaries/navigation aids; noncanonical and rebuildable.
- **HUMAN_KNOWLEDGE** — a decision, belief, rationale, or user-approved synthesis explicitly confirmed for durable memory; it is not independent external evidence.

The user decides what is admitted as official durable knowledge and what semantic relationship changed evidence has. The Agent handles retrieval, organization, provenance following, and optional rebuildable summarization.

### Changed remembered files

LLM Wiki does not silently guess what a new revision means. The new bytes are preserved first, then optional summary work pauses while the relationship remains unresolved.

The user can explicitly choose:

- **correction** — the older revision was wrong;
- **change** — the older state may have been valid, and the newer state became valid later;
- **dispute** — both current revisions remain unresolved/conflicting;
- **supersede** — generic replacement without a stronger temporal/correction claim;
- **independent** — keep them unrelated.

Before recording the relation, LLM Wiki verifies both immutable revisions, checks their durable file/SHA binding, shows a bounded old/new changed-region preview, and revalidates immediately before the canonical mutation. A change requires a timezone-aware effective instant.

### Human Knowledge

A user decision/rationale becomes durable only after the full proposed statement is shown for confirmation. A later explicit change can supersede an older current Human Knowledge record while retaining history. Tentative inferred preferences are not silently persisted.

Malformed/tampered Human Knowledge and fork/cycle ambiguity fail closed. The stored integrity hash is a corruption check, not cryptographic tamper resistance.

## Agent tools — advanced

The normal Agent may choose these naturally while project memory is enabled:

- `#wikiMemory` / `llmWiki_searchMemory` — search current project memory; read-only.
- `#wikiRead` / `llmWiki_readSource` — read verified immutable source evidence; read-only and paginated.
- `#rememberWikiSource` / `llmWiki_rememberSource` — admit a local workspace file after product confirmation.
- `#rememberHumanKnowledge` / `llmWiki_rememberHumanKnowledge` — save the user's confirmed decision/rationale after product confirmation.
- `#resolveWikiLineage` / `llmWiki_resolveLineage` — record an explicitly chosen relationship between changed revisions.

Remembered raw/derived text is framed as untrusted quoted data and JSON-encoded at the Agent boundary. Search does not authorize writes. Load-bearing facts surfaced by a derived summary should be followed back to raw source evidence.

## Settings

- `llmWiki.pythonExecutable` — empty by default; auto-detect Python. Set only to override.
- `llmWiki.corePath` — advanced local core override; empty uses the bundled core in an installed VSIX.
- `llmWiki.workspaceDirectory` — private local project-memory directory; default `.wiki-lab`.
- `llmWiki.maxAiCredits` — advanced preferred guard for the legacy explicit Ask Luna path.
- `llmWiki.agentWikiMaintenanceEnabled` — optional AI summaries, workspace-scoped, default `false`.
- `llmWiki.agentWikiMaintenanceMaxAiCredits` — preferred per-summary guard, default `30`.
- `llmWiki.agentWikiMaintenanceDailyCallLimit` — daily soft-guard threshold, default `10`; `0` disables new summary generations.

## 0.1.16 validation gate

0.1.16 keeps the existing authority/retrieval contract and adds release-oriented VS Code UX hardening:

- native first-install Walkthrough;
- four-command normal Command Palette surface;
- user-facing terminology centered on project memory and AI summaries;
- actionable zero-model Setup & Health output;
- quiet routine success paths;
- workspace-state status bar rather than internal filing topic;
- immediate status/tool teardown on disable;
- explicit single-folder fail-closed behavior for multi-root workspaces;
- cross-platform Python auto-discovery unless explicitly overridden;
- bounded subprocess error classification with direct spoof/leak tests;
- user/Agent causal maintenance-failure reporting;
- packaged-VSIX checks for the release UX helpers and onboarding assets.

The frozen E020 synthetic contract remains **78 cases: 60 supported / 7 partial / 11 deferred**, with zero model calls. Python 3.9 compatibility, Python unit tests, E020, static boundaries, dev Extension Host, bundled core, VSIX packaging, and unpacked packaged Extension Host are all required before this candidate is considered mergeable.

## What still needs real dogfood

A polished release candidate still cannot replace real multi-session use. Natural dogfood should decide:

- whether the Agent searches memory at the right moments;
- whether it follows important memory hits to source evidence naturally;
- whether source-admission confirmation causes approval fatigue;
- whether “remember our decision” feels natural in conversation;
- whether old/new revision previews are understandable;
- whether optional AI-summary latency/spend is worth it;
- whether the daily soft guard is useful or annoying;
- whether users ever need a dedicated history/navigation view;
- whether returning days later actually recovers reasoning the user would otherwise have lost.

Do not add vectors/graphs, background watching, URL/PDF capture, cross-workspace federation, automatic concept routing, or a large custom navigation UI just because they are available ideas. Those remain evidence-gated product decisions.
