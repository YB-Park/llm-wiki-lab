# LLM Wiki Dogfood 0.1.11 — VS Code-first Alpha

LLM Wiki is a local, user-owned knowledge system that lets a VS Code Agent search, read, and maintain persistent project memory without giving the model silent authority over raw evidence or the user's own beliefs/decisions.

The simplest mental model is:

- **RAW_MEMORY** — immutable admitted source evidence; factual/provenance authority.
- **DERIVED_MEMORY** — LLM-maintained Agent Wiki synthesis; useful, noncanonical, rebuildable.
- **HUMAN_KNOWLEDGE** — a decision/belief/rationale the user explicitly confirmed for durable memory; not independent external evidence.

## Install / first run

1. Install the `.vsix` from VS Code Extensions → `...` → **Install from VSIX...**.
2. Open a **trusted local workspace**.
3. Run `LLM Wiki: Doctor (Zero Model Calls)`.
4. If Doctor reports `Git raw-store safety: UNPROTECTED` or realistic dogfood `BLOCKED`, do not ingest sensitive evidence until `.wiki-lab/` is protected from that Git repository.
5. Use your normal VS Code Agent conversation. The extension contributes the Agent tools described below.

Python defaults to `python3`. Dogfood 0.1.11 retains explicit Python 3.9 compatibility testing for the bundled core.

## The five Agent tools

You normally do not need to operate the Wiki through Command Palette commands. The selected VS Code Agent model can call these tools when appropriate, and you can also reference them explicitly by `#` name while dogfooding.

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

0.1.11 does **not** silently assume what the new revision means.

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
- `agent-state.json` with pending lineage decisions, source locators, and maintenance call reservations.

Do not commit the Wiki directory. Treat backups as equally sensitive as the source material.

### Minimal Alpha backup / restore

Stop Wiki writes (closing the workspace is the simplest Alpha procedure) and copy the **entire Wiki directory as one snapshot** to an approved private location. Do not copy only `raw/` or only `manifest.jsonl`.

After restore, run `LLM Wiki: Doctor (Zero Model Calls)` before resuming work. If Doctor reports missing/torn/corrupt canonical history or missing raw evidence, stop rather than manually reconstructing history.

This is not live transactional backup or cloud sync. The longer operating note is `docs/11-local-backup-restore.md`.

## Doctor

`LLM Wiki: Doctor (Zero Model Calls)`:

- checks the configured Python executable;
- invokes the real initialization boundary;
- confirms `compiled_provider=disabled`;
- audits raw/canonical integrity without repairing it;
- classifies Git raw-store safety as `NOT_GIT`, `PROTECTED`, or `UNPROTECTED`;
- reports Copilot CLI availability;
- reports whether Agent Wiki maintenance is enabled;
- makes **zero model calls**.

Doctor does not print evidence, prompts, answers, usernames, hostnames, or environment variables.

## Ask Luna (legacy explicit read-only path)

`LLM Wiki: Ask Luna (Read-only)` remains available as an explicit topic-scoped diagnostic/dogfood path. It is not the primary 0.1.11 agent-first UX.

It requires a modal evidence-send confirmation, uses exact `gpt-5.6-luna`, sends the transformed prompt over stdin rather than process argv, validates transient citation handles, and never writes the answer into canonical Wiki state.

## Command Palette surface

The 17 commands remain available as manual/diagnostic/fallback controls:

- `LLM Wiki: Doctor (Zero Model Calls)`
- `LLM Wiki: Initialize Workspace`
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

The Command Palette is no longer the intended primary product loop; ordinary Agent conversation is.

## Runtime prerequisites

For local raw/search/provenance and zero-model Agent tools:

- trusted VS Code workspace;
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

## 0.1.11 validation status

Before 0.1.11 human dogfood, the project ran deterministic/adversarial synthetic passes rather than asking the user to discover every obvious gap manually.

**E020** contains **78** frozen representative authority/UX cases:

- 60 supported by concrete current product mechanisms;
- 7 partial and still requiring installed/model/process evidence;
- 11 deliberately deferred because they require new authority/parser/product decisions;
- model calls: 0.

Dev and **unpacked packaged VSIX Extension Host** tests exercise the actual five-tool surface, including dirty-file fail-closed, verified raw read, pending revision lineage, Human Knowledge lifecycle, newline metadata structural injection, stale/tampered lineage binding, and Human Knowledge fork handling.

**E021** is the separate cross-source concept-compounding experiment. It recorded narrow positive evidence that exact Luna can maintain one fixed-identity derived concept page across a deliberately relevant A→A+B→A+B+C source sequence while retaining raw provenance. It does **not** earn automatic concept discovery/routing/dedup/update triggers, and its result record documents a retained execution-provenance limitation. Do not rerun it merely to strengthen the record.

**E022** used exactly **two** real main-model generations (`gpt-5.4`, `claude-sonnet-4.6`) against the malicious exact v4 memory serialization. Both recovered the legitimate fact `42`, treated embedded policy/mutation/delete-looking strings as data, and requested/claimed no Wiki mutation. Rerolls: 0. Run `31993541811`, artifact `9276094144`. This is a useful translation smoke, **not a universal prompt-injection guarantee**.

## What still needs human dogfood

This is an **Alpha**, not customer-ready software. Synthetic testing cannot tell us:

- whether the main Agent invokes `wikiMemory` often enough or too often;
- whether it naturally follows important hits with `wikiRead`;
- whether admission/lineage confirmations cause approval fatigue;
- whether “remember my decision” feels natural in conversation;
- whether the old/new lineage preview is understandable to a normal user;
- whether Luna maintenance latency/spend feels worth it;
- whether RAW vs DERIVED vs HUMAN_KNOWLEDGE distinctions stay understandable rather than leaking implementation complexity;
- whether returning days later actually recovers reasoning the user would otherwise have lost.

Those are the next product questions. Do not add vectors/graphs, background watching, URL/PDF capture, cross-workspace federation, automatic concept routing, or a large visual navigation system merely because they are available ideas.

Known non-blocking reliability follow-up #132 tracks deletion detection for `agent-state.json` and the relation/pending-state crash window. Do not claim those edges are already atomic/detectable.

Compiled knowledge remains disabled as a trusted/default provider. W0 remains the default retrieval path and X1 remains non-default/shadow pending more natural quality evidence.
