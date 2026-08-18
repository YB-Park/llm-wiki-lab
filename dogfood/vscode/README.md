# LLM Wiki Dogfood 0.1.12 — VS Code-first Alpha

LLM Wiki is a local, user-owned knowledge system that lets a VS Code Agent search, read, and maintain persistent project memory without giving the model silent authority over raw evidence or the user's own beliefs/decisions.

The simplest mental model is:

- **RAW_MEMORY** — immutable admitted source evidence; factual/provenance authority.
- **DERIVED_MEMORY** — LLM-maintained Agent Wiki synthesis; useful, noncanonical, rebuildable.
- **HUMAN_KNOWLEDGE** — a decision/belief/rationale the user explicitly confirmed for durable memory; not independent external evidence.

## Install / first run

1. Install the `.vsix` from VS Code Extensions → `...` → **Install from VSIX...**.
2. Open a **trusted local workspace**.
3. Protect the configured Wiki directory from that Git repository. With the default `.wiki-lab/`, a local-only Alpha choice is adding `.wiki-lab/` to `.git/info/exclude`; a project-wide choice is `.gitignore`.
4. Run `LLM Wiki: Initialize Workspace` and confirm the explicit workspace opt-in.
5. Optionally run `LLM Wiki: Doctor (Zero Model Calls)` to inspect readiness. Doctor never initializes, repairs, or enables the workspace.
6. Use your normal VS Code Agent conversation. The five Agent tools are available only while this workspace is explicitly enabled.

Initialization refuses to enable Agent integration while the Wiki directory is Git-`UNPROTECTED`, when the configured Python executable is unavailable, or when post-init integrity does not pass.

Python defaults to `python3`. Dogfood 0.1.12 retains explicit Python 3.9 compatibility testing for the bundled core.

## Workspace activation boundary

Installing the extension gives VS Code the LLM Wiki capability; it does **not** opt every project into LLM Wiki.

- Before explicit initialization, all five LLM Wiki Agent tools are hidden from Agent mode by a VS Code `when` condition.
- `LLM Wiki: Initialize Workspace` creates/verifies the local store, then records a separate local opt-in marker at `.wiki-lab/workspace-opt-in.json` (or the equivalent configured Wiki root).
- Existing Core files alone do not imply opt-in. This intentionally covers stores that older dogfood builds may have created through Doctor or write flows.
- `LLM Wiki: Disable Workspace (Keep Data)` removes only the opt-in marker. The Wiki store and remembered data remain intact, while the Agent tools become unavailable again.
- Reopening an enabled workspace restores tool availability from the local marker with zero model calls.

The product boundary is therefore: **installed capability ≠ workspace permission**.

## The five Agent tools

You normally do not need to operate the Wiki through Command Palette commands after initialization. The selected VS Code Agent model can call these tools when appropriate, and you can also reference them explicitly by `#` name while dogfooding.

### `#wikiMemory` — search persistent memory

Agent tool: `llmWiki_searchMemory`.

Use when prior project knowledge, evidence, rationale, decisions, or history may help.

What happens:

1. LLM Wiki performs local deterministic current-view retrieval. **The tool itself makes zero model calls.**
2. It can return separately labeled `RAW_MEMORY`, `DERIVED_MEMORY`, and `HUMAN_KNOWLEDGE`.
3. Untrusted remembered text and text metadata are returned in JSON-string `*_json` fields. They are data, never Agent instructions.
4. No Wiki mutation is authorized by a search result.

A normal user question might be:

> “왜 예전에 Redis를 안 쓰기로 했지?”

The Agent may use `wikiMemory` to recover relevant prior memory before answering.

### `#wikiRead` — follow a memory hit into verified evidence

Agent tool: `llmWiki_readSource`.

`wikiMemory` intentionally returns bounded search snippets. When a factual claim needs deeper provenance, `wikiRead` reads the immutable admitted source by canonical `source_id`.

It exposes:

- source SHA/name;
- current/superseded/contested status when a topic ID is supplied;
- bounded raw text with `startChar` / `maxChars` pagination;
- the source-scoped Agent Wiki note, if one exists, clearly labeled as derived/noncanonical.

Raw evidence remains the factual authority. If `has_more=yes` and the answer depends on omitted text, the Agent can continue with `next_start_char`.

### `#rememberWikiSource` — “이 파일 기억해”

Agent tool: `llmWiki_rememberSource`.

Use only when the user explicitly asks to remember/save/capture/add a **local workspace file**.

What happens:

1. The product shows its own human confirmation modal. This is separate from generic Agent tool approval.
2. If the file is currently dirty in any open editor, LLM Wiki **does not auto-save it**. Save it yourself and ask again.
3. After confirmation, the exact file bytes are admitted first as immutable raw evidence.
4. Filing uses the selected topic when available; otherwise deterministic **Agent Inbox** avoids extra ceremony.
5. If Agent Wiki maintenance is disabled, the flow stops with zero maintenance model calls.
6. If maintenance is enabled and there is no unresolved lineage ambiguity, Luna may create/reuse a derived source note.

Raw admission always happens before optional derived maintenance. A maintenance failure does not erase admitted raw evidence.

#### If the same remembered file changed

0.1.12 does **not** silently assume what the new revision means.

The new raw bytes are preserved, but Agent Wiki maintenance pauses and LLM Wiki creates a **pending lineage decision**. The Agent should ask whether the newer revision is:

- a **correction** — the older revision was wrong;
- a **change** — the older revision may have been valid then and the newer state became valid later;
- an unresolved **dispute**;
- a generic **supersede**;
- intentionally **independent**.

Then `#resolveWikiLineage` handles the human-confirmed answer.

### `#resolveWikiLineage` — decide what changed revisions mean

Agent tool: `llmWiki_resolveLineage`.

Use only after `rememberWikiSource` returns a `pending_decision_id` and the user explicitly chooses the semantic relationship.

Before recording anything, LLM Wiki:

1. verifies the older/newer immutable raw revisions;
2. verifies both are still current for the pending decision;
3. checks their durable workspace-file locator/SHA binding;
4. shows a bounded **OLDER / NEWER changed-region preview** in the confirmation modal;
5. after confirmation, rechecks the source state immediately before any canonical relation is recorded.

`change` requires a timezone-aware effective instant. If multiple old current revisions are involved, deciding one does not silently resolve the others; remaining ambiguity stays pending.

This is where the human is intentionally in the loop because the difference between “wrong,” “changed later,” and “still disputed” is an epistemic commitment, not filing work.

### `#rememberHumanKnowledge` — “우리는 이렇게 결정했어. 기억해”

Agent tool: `llmWiki_rememberHumanKnowledge`.

Use only when the user explicitly asks to durably remember their **own** decision, belief, rationale, or user-approved synthesis.

Example:

> “우리는 운영 복잡성 때문에 Redis를 아직 쓰지 않기로 결정했어. 기억해.”

What happens:

1. The Agent proposes a bounded statement/reasoning record.
2. LLM Wiki shows the **full durable text** to the user for confirmation.
3. On confirmation it is stored as `HUMAN_KNOWLEDGE` with **zero model calls** by the Wiki write path.
4. It is never promoted to raw external evidence or a canonical temporal source relation.
5. A later explicit change can create a new Human Knowledge record that supersedes the old current one.

Tentative/inferred beliefs must not be silently persisted. “Redis 좀 귀찮은 것 같아. 아직 결정은 안 했어.” may justify reading relevant memory, but not durable Human Knowledge.

Malformed/tampered Human Knowledge and fork/cycle ambiguity fail closed. The local integrity hash is a corruption check, **not** cryptographic tamper resistance.

## Agent Wiki maintenance with Luna

`LLM Wiki: Configure Agent Wiki Maintenance` controls a workspace-scoped standing grant. It is **OFF by default**.

When enabled, after explicit source admission and only when no pending lineage decision blocks the source, admitted source bytes may be sent to exact `gpt-5.6-luna` to create/reuse a source-scoped derived note under:

- `.wiki-lab/agent-wiki/source-notes/<source_id>.json`
- `.wiki-lab/agent-wiki/source-notes/<source_id>.md`

The artifact is labeled:

> **AGENT WIKI — NONCANONICAL / REBUILDABLE**

The maintenance path cannot perform correction/change/dispute/supersession/delete and cannot infer Human Knowledge. Generated notes are never re-ingested as raw evidence.

The same current source + policy reuses the existing note with **zero new model calls**.

Two separate spend guards exist:

- `llmWiki.agentWikiMaintenanceMaxAiCredits` — Copilot CLI per-call ceiling, default/minimum `30` because of the current CLI contract;
- `llmWiki.agentWikiMaintenanceDailyCallLimit` — durable per-workspace local-day call reservation cap, default `10`, range `0–100`; `0` disables new maintenance generations even if the grant is enabled.

The daily count is stored inside `.wiki-lab/agent-state.json` before a generation. An uncertain transport outcome is not automatically refunded.

## What `.wiki-lab/` contains

The whole configured Wiki directory is one private backup boundary. It may contain:

- immutable raw evidence;
- canonical manifest/provenance/temporal history;
- topics and local calibration state;
- noncanonical Agent Wiki source notes;
- user-confirmed Human Knowledge;
- `agent-state.json` with pending lineage decisions, source locators, and maintenance call reservations;
- the local workspace opt-in marker controlling Agent-tool availability.

Do not commit the Wiki directory. Treat backups as equally sensitive as the source material.

### Minimal Alpha backup / restore

Stop Wiki writes (closing the workspace is the simplest Alpha procedure) and copy the **entire Wiki directory as one snapshot** to an approved private location. Do not copy only `raw/` or only `manifest.jsonl`.

After restore, run `LLM Wiki: Doctor (Zero Model Calls)` before resuming work. If Doctor reports missing/torn/corrupt canonical history or missing raw evidence, stop rather than manually reconstructing history. A restored Core store without a valid workspace opt-in marker remains disabled until the user runs `LLM Wiki: Initialize Workspace` explicitly.

This is not live transactional backup or cloud sync. The longer operating note is `docs/11-local-backup-restore.md`.

## Doctor

`LLM Wiki: Doctor (Zero Model Calls)` is a **pure diagnostic** command. It can be run before or after workspace initialization and makes no state changes.

It:

- reports whether the local Wiki store is initialized;
- reports whether this workspace has explicit Agent-tool opt-in;
- checks the configured Python executable;
- confirms `compiled_provider=disabled` when a store exists;
- audits raw/canonical integrity without repairing it;
- classifies Git raw-store safety as `NOT_GIT`, `PROTECTED`, or `UNPROTECTED`;
- reports Copilot CLI availability;
- reports whether Agent Wiki maintenance is enabled;
- makes **zero model calls** and **zero state changes**.

Doctor never initializes the store, writes the opt-in marker, repairs history, or changes Git configuration. On an uninitialized workspace it reports `Workspace store: NOT_INITIALIZED`, `Workspace opt-in: NOT_ENABLED`, and `Agent tools: HIDDEN`.

Doctor does not print evidence, prompts, answers, usernames, hostnames, or environment variables.

## Ask Luna (legacy explicit read-only path)

`LLM Wiki: Ask Luna (Read-only)` remains available as an explicit topic-scoped diagnostic/dogfood path. It is not the primary 0.1.12 agent-first UX.

It requires a modal evidence-send confirmation, uses exact `gpt-5.6-luna`, sends the transformed prompt over stdin rather than process argv, validates transient citation handles, and never writes the answer into canonical Wiki state.

## Command Palette surface

The 18 user-facing commands remain available as initialization/manual/diagnostic/fallback controls:

- `LLM Wiki: Initialize Workspace`
- `LLM Wiki: Disable Workspace (Keep Data)`
- `LLM Wiki: Doctor (Zero Model Calls)`
- `LLM Wiki: Create Topic`
- `LLM Wiki: Select Topic`
- `LLM Wiki: New Human Knowledge Note`
- `LLM Wiki: Configure Agent Wiki Maintenance`
- `LLM Wiki: Ingest Active File`
- `LLM Wiki: Ingest Active File as Authoritative Update`
- `LLM Wiki: Search Topic`
- `LLM Wiki: Global Search Current Evidence Across Topics`
- `LLM Wiki: Record Correction`
- `LLM Wiki: Change Source Over Time`
- `LLM Wiki: Record Unresolved Dispute`
- `LLM Wiki: Record Feedback`
- `LLM Wiki: Ask Luna (Read-only)`
- `LLM Wiki: Show Calibration Summary`
- `LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)`

Initialization/disable/Doctor define the workspace lifecycle. After initialization, the Command Palette is not the intended primary product loop; ordinary Agent conversation is.

## Runtime prerequisites

For local raw/search/provenance and zero-model Agent tools:

- trusted VS Code workspace;
- explicit `LLM Wiki: Initialize Workspace` opt-in for that workspace;
- protected Wiki directory when it lives inside a Git repository;
- VS Code `1.95+`;
- Python, default `python3` (`llmWiki.pythonExecutable` can override it).

For model-backed Luna maintenance / explicit Ask Luna:

- GitHub Copilot CLI installed and authenticated;
- permitted evidence for the configured workspace grant.

The normal VS Code Agent tools also require an authenticated Agent-capable VS Code session for the user's selected main model.

## Settings

- `llmWiki.pythonExecutable`: default `python3`.
- `llmWiki.corePath`: empty means bundled core in an installed VSIX / repository core during extension development.
- `llmWiki.workspaceDirectory`: default `.wiki-lab`.
- `llmWiki.maxAiCredits`: default `30`, explicit Ask Luna per-call guard.
- `llmWiki.agentWikiMaintenanceEnabled`: default `false`, workspace-scoped standing grant.
- `llmWiki.agentWikiMaintenanceMaxAiCredits`: default `30`, maintenance per-call CLI guard.
- `llmWiki.agentWikiMaintenanceDailyCallLimit`: default `10`; `0` disables new maintenance generations.

## 0.1.12 validation status

0.1.12 keeps the existing deterministic/adversarial authority contract and adds explicit workspace activation boundaries around the same five Agent tools.

**E020** contains **78** frozen representative authority/UX cases:

- 60 supported by concrete current product mechanisms;
- 7 partial and still requiring installed/model/process evidence;
- 11 deliberately deferred because they require new authority/parser/product decisions;
- model calls: 0.

Dev and **unpacked packaged VSIX Extension Host** tests exercise the actual five-tool surface, including dirty-file fail-closed, verified raw read, pending revision lineage, Human Knowledge lifecycle, newline metadata structural injection, stale/tampered lineage binding, and Human Knowledge fork handling. 0.1.12 additionally statically locks tool `when` gating and tests that the separate opt-in marker is required and that disabling Agent integration preserves the Core store.

**E021** is the separate cross-source concept-compounding experiment. It recorded narrow positive evidence that exact Luna can maintain one fixed-identity derived concept page across a deliberately relevant A→A+B→A+B+C source sequence while retaining raw provenance. It does **not** earn automatic concept discovery/routing/dedup/update triggers, and its result record documents a retained execution-provenance limitation. Do not rerun it merely to strengthen the record.

**E022** used exactly **two** real main-model generations (`gpt-5.4`, `claude-sonnet-4.6`) against the malicious exact v4 memory serialization. Both recovered the legitimate fact `42`, treated embedded policy/mutation/delete-looking strings as data, and requested/claimed no Wiki mutation. Rerolls: 0. Run `31993541811`, artifact `9276094144`. This is a useful translation smoke, **not a universal prompt-injection guarantee**.
