# LLM Wiki for VS Code — 0.1.21 UX vNext U0 candidate

LLM Wiki gives your coding Agent **durable project memory that you control**.

The currently published dogfood release remains **0.1.20**. This branch prepares **0.1.21**, the first UX vNext product-shell slice. It does not widen memory authority, migrate the canonical store schema, change retrieval defaults, or add a new model policy. Existing 0.1.18+ `.wiki-lab` stores remain compatible.

The design gate for this work is [`../../docs/14-product-ux-vnext.md`](../../docs/14-product-ux-vnext.md).

## What changes in U0

0.1.21 adds a small **native LLM Wiki sidebar overview** so users no longer have to remember Command Palette commands or read diagnostic Output just to understand product state.

The overview intentionally stays shallow:

- **Project memory** — whether this workspace is enabled.
- **AI summaries** — optional derived summaries; off by default.
- **AI-assisted memory answers** — the separate read-only Query Reasoning grant.
- **Other project memories** — registered project names and whether this workspace is ready to consult them.

The sidebar uses one native VS Code Tree View plus Welcome View. It does **not** use a custom Webview/dashboard, expose store IDs or filesystem roots, or parse canonical memory files into a second UI-owned model.

Ordinary work still happens in **normal Agent chat**. The sidebar is for orientation, state, and follow-through.

## Get started

1. Install the candidate `.vsix`.
2. Open and trust one local workspace folder. Multi-root workspaces remain fail-closed.
3. Open the **LLM Wiki** sidebar or the VS Code Getting Started checklist.
4. Choose **Set Up Project Memory**. Setup is local and makes no model call.
5. Keep the private Wiki directory out of Git. The default is `.wiki-lab/`.
6. Continue in normal Agent chat.

AI summaries and AI-assisted memory answers are optional. They are **not** setup requirements.

Installing the extension gives VS Code the capability. **Setting up a workspace gives the Agent permission to use that workspace's project memory.** Existing `.wiki-lab` data alone never silently enables Agent access, and setup does not authorize another project's Wiki.

## Normal use

You do not need to learn Wiki tool names.

A historical question can simply be:

> “왜 예전에 Redis를 안 쓰기로 했지?”

When you want to preserve something, say it naturally:

> “이 파일 프로젝트 기억에 저장해.”

or:

> “우리는 운영 복잡성 때문에 Redis를 아직 쓰지 않기로 결정했어. 이 결정 기억해.”

LLM Wiki keeps authority boundaries explicit. Durable source admission, user-owned project knowledge, and the semantic relationship between changed revisions remain human-approved.

## Product surface

### LLM Wiki sidebar

The sidebar is the default state surface, not a second application.

When project memory is off, its Welcome View gives one primary next action: **Set Up Project Memory**.

When project memory is on, the overview shows the small set of state that normally matters. Registered other-project memories are displayed by their human-readable project names and remain read-only.

View-title actions stay intentionally sparse:

- **Open Agent Chat**
- **Check Setup and Health**
- **Refresh LLM Wiki**

### Command Palette

The normal Command Palette remains a fallback/configuration surface:

- **LLM Wiki: Set Up Project Memory**
- **LLM Wiki: Check Setup and Health**
- **LLM Wiki: Configure AI Summaries**
- **LLM Wiki: Configure AI-assisted Memory Answers**
- **LLM Wiki: Manage Other Project Memories**
- **LLM Wiki: Disable for This Workspace**

Advanced/manual commands remain available for deterministic fallback and dogfood inspection but stay out of the normal palette.

## Project memory is local-first

The default private store is `.wiki-lab/` inside the workspace. Treat it as sensitive project data and keep it out of Git.

It can contain immutable admitted source evidence, correction/change/dispute/supersession history, explicitly confirmed Human Knowledge, optional rebuildable AI summaries, and local workflow metadata such as pending lineage decisions.

Back up the **whole directory as one private snapshot**. See [`../../docs/11-local-backup-restore.md`](../../docs/11-local-backup-restore.md).

Each project store remains its own Authority Core. U0 does not merge manifests, copy evidence between projects, create a global canonical identity, or authorize cross-project mutation.

### Existing-store portability

E026 S0-A proves a bounded compatibility property with **zero model calls**: representative 0.1.18 store state survives relocation to another absolute root with RAW identity, topics/temporal history, exact provenance, Human Knowledge, workflow state, and derived notes intact. Host-local workspace opt-in is deliberately not transported; the destination establishes a fresh authority epoch.

This portability result does **not** authorize Git/SSH sync, automatic merge/rebase, live network-share semantics, distributed locks, or concurrent multi-machine writers. Git-style line-ending mutation of content-addressed RAW bytes is corruption and fails closed.

## Authority model — unchanged in U0

The core contract still distinguishes:

- **RAW_MEMORY** — immutable admitted evidence and provenance authority.
- **DERIVED_MEMORY** — noncanonical, rebuildable synthesis/navigation aid.
- **HUMAN_KNOWLEDGE** — a user-confirmed decision, belief, rationale, or approved synthesis; authoritative as a record of what the user confirmed in that project, not as independent external evidence or a global preference.

These enum-style names are primarily **technical/authority vocabulary**. The ordinary product surface uses user-facing language and reserves the internal terms for provenance, diagnostics, tool contracts, and expert inspection.

Changed remembered files never silently become corrections or later states. The user still explicitly decides what the relationship means. U0 does not alter the existing verified, human-gated lineage path.

Remembered source/model text is untrusted data, never executable Agent instruction.

## AI-assisted memory answers — separately opt-in

The existing Query Plane remains **separately opt-in** and read-only. Setting up project memory does not authorize it, and enabling AI summaries does not authorize it.

Run **LLM Wiki: Configure AI-assisted Memory Answers** to create or revoke the local grant. Internally this remains the same bounded Query Reasoning contract introduced before U0.

For an ordinary project question, `wikiConsult` remains current-store-only and may:

1. search the current authorized project store with deterministic retrieval;
2. follow selected candidates to verified query-relevant raw regions;
3. include relevant current Human Knowledge and unresolved lineage state with their epistemic roles preserved;
4. send that bounded evidence packet to GitHub Copilot using exact `gpt-5.6-luna`;
5. return a compact Wiki Brief containing the answer, terminal authority references, and insufficiency status.

The Query Plane cannot admit sources, write Human Knowledge, decide lineage, or mutate canonical Wiki history.

### Separate local grant and usage guards

The Query Plane grant lives in VS Code extension local workspace state, not in a project setting file. It remains `current_store` scoped and is bound to the workspace opt-in authority epoch.

Before creating the grant, the user still explicitly chooses:

1. a local daily model-call attempt cap from 1 to 100; and
2. a Copilot CLI per-response AI-credit soft guard from 1 to 100.

U0 only improves orientation around whether this feature is on. A later UX slice may improve how these numeric choices are presented without changing the stored limits or silently choosing a spend boundary for the user.

### No silent raw fallback

If AI-assisted memory answers are disabled, the daily cap is reached, candidate verification fails, Luna is unavailable, the provider cannot enforce the selected guard, a grant is revoked, or the returned brief violates the contract, `wikiConsult` fails boundedly.

It does **not** silently dump broad raw Wiki context into the Main Agent. `wikiMemory` and `wikiRead` remain explicit lower-level provenance/debug paths.

## Other project memories — named-store read-only boundary

The feature previously surfaced as **Personal Wiki Library** is still the same local routing/authorization catalog internally. U0 changes only the user-facing label in normal UI to **Other project memories**.

Current authority remains deliberately narrow:

- another project must be explicitly registered;
- the registration is read-only;
- this workspace needs a separate named-store access grant;
- AI-assisted consultation additionally needs the Query Reasoning grant;
- the user must explicitly identify the other project by an exact registered name/alias;
- unknown, ambiguous, moved, damaged, replaced, or unauthorized stores fail closed;
- failure never falls back to the current project or another store;
- external reads never authorize external mutation.

The U0 sidebar lists only registered **display names**. It does not expose opaque store IDs, authority anchors, or filesystem roots.

### Scoped provenance follow-through

`wikiRead` remains the provenance follow-through path. Current-store reads may omit `scopeRef`; external RAW provenance requires the exact opaque scope returned by the originating named-store consultation.

A scoped source miss never retries the same source ID in the current store or another registered store. Pagination keeps the same scope.

## Existing Agent tools remain available

While project memory is enabled, the Agent may use:

- `#wikiConsult` / `llmWiki_consultMemory` — opt-in compact Query Plane path; current store by default and one explicitly named registered store when separately authorized.
- `#wikiMemory` / `llmWiki_searchMemory` — low-level read-only current-store memory search.
- `#wikiRead` / `llmWiki_readScopedSource` — verified immutable source read with scope-qualified pagination.
- `#rememberWikiSource` / `llmWiki_rememberSource` — durable current-workspace source admission after product confirmation.
- `#rememberHumanKnowledge` / `llmWiki_rememberHumanKnowledge` — user-owned current-project knowledge after product confirmation.
- `#resolveWikiLineage` / `llmWiki_resolveLineage` — record an explicitly chosen relation between changed current-project revisions.

The legacy `llmWiki_readSource` implementation remains hidden for compatibility.

## AI summaries remain separate

**LLM Wiki: Configure AI Summaries** controls a separate outbound-data grant. It is off by default.

When enabled, explicitly admitted current-project source content may be sent to GitHub Copilot using exact `gpt-5.6-luna` to create/reuse a rebuildable source-scoped summary. AI summaries never replace RAW evidence or become Human Knowledge automatically.

Query Plane permission, other-project memory permission, and maintenance permission remain separate authority surfaces even when later UX work sequences them more coherently.

## Workspace permission boundary

Before **Set Up Project Memory** succeeds:

- Agent tools are hidden by contribution conditions;
- runtime tool implementations are not registered;
- setup/health make no model call.

**Disable for This Workspace** removes only the opt-in marker and immediately tears down Agent tool registrations while preserving Wiki data. Query and other-project workspace grants are bound to that opt-in epoch and become stale after disable/re-enable.

0.1.21 remains single-folder only.

## Check Setup and Health

**LLM Wiki: Check Setup and Health** remains the technical diagnostic surface:

- **0 model calls**;
- **0 state changes**;
- no initialization or repair;
- no source/prompt/evidence content printed.

It reports project-memory state, local-store integrity, Python/Copilot executable presence, AI-summary state, Query Reasoning grant/call cap, and external-library access. The new sidebar does not replace these deeper checks; it keeps routine orientation out of diagnostic Output.

## Python runtime

The bundled local core requires Python 3.9+.

For ordinary current-store operations, `llmWiki.pythonExecutable` is empty by default and auto-detects:

- Windows: `python`, then `py`, then `python3`;
- macOS/Linux: `python3`, then `python`.

An explicit override is respected for current-workspace operations rather than silently falling back.

External project reads deliberately do **not** inherit the current workspace's explicit Python/core override. They use the extension's bundled trusted read-only core under the existing isolated execution boundary.

## Errors and recovery

For users, failures should say what failed, what was preserved, and what safe action is available without dumping source text, prompts, arbitrary paths, or secrets.

For Agent-facing failures, product code uses bounded causal states/codes. Unknown subprocess detail collapses to a generic bounded failure rather than exposing arbitrary stderr.

Query Plane transport/model failure and named-store authorization/integrity/catalog failure never authorize broad raw-memory or cross-store fallback.

## Confirmation policy

Blocking confirmation remains reserved for authority/privacy/usage boundaries such as:

- setting up or disabling project memory;
- source admission;
- saving Human Knowledge;
- resolving changed-source semantics;
- enabling AI summaries;
- enabling AI-assisted memory answers and choosing usage guards;
- registering/removing an external project store;
- enabling/revoking named-store access for the current workspace.

Routine read-only inspection of the new overview adds no approval step.

## U0 validation gate

Before U0 can merge/publish, it must preserve the existing deterministic safety/product contract and add only a native product shell on top.

Required:

- package/JavaScript syntax checks;
- existing deterministic Node/static checks;
- existing Python/core regression checks relevant to the published baseline;
- Extension Host integration tests;
- bundled-core checks;
- VSIX packaging and packaged Extension Host execution;
- static assertions for one native View Container / one Tree View / Welcome View / no Webview;
- unchanged explicit workspace opt-in, Query grant, named-store read-only, Human Knowledge authorship, pending-lineage verification, no-silent-fallback, and Doctor purity boundaries;
- **0 model calls required for the U0 validation itself**.

Passing U0 does not earn sync, distributed/multi-writer semantics, ambient/library-wide federation, cross-project writes, a Personal store, vectors/graphs/entities, autonomous canonical persistence, or any new memory authority.

## What installed U0 dogfood must decide

Do not score U0 primarily on visual styling. Observe whether a user can:

- establish project memory without reading this README;
- tell at a glance whether project memory is on;
- understand that AI summaries and AI-assisted memory answers are optional;
- see which other project memories are registered without learning store IDs/paths;
- return naturally to Agent chat rather than treating LLM Wiki as a separate database app;
- find technical health details when something is wrong;
- understand the next safe action without reading raw diagnostic output first.

Broader UX work is gated behind this first installed product-shell experience. See `docs/14-product-ux-vnext.md` for the planned U1–U4 sequence.

## Settings

- `llmWiki.pythonExecutable` — optional Python override for current-workspace operations.
- `llmWiki.corePath` — advanced current-workspace local core override; not used to execute external project reads.
- `llmWiki.workspaceDirectory` — private current-workspace store; default `.wiki-lab`.
- `llmWiki.maxAiCredits` — legacy explicit Ask Luna preferred guard.
- `llmWiki.agentWikiMaintenanceEnabled` — optional AI summaries; separate grant.
- `llmWiki.agentWikiMaintenanceMaxAiCredits` — preferred per-summary CLI guard when supported.
- `llmWiki.agentWikiMaintenanceDailyCallLimit` — AI-summary soft-guard threshold.

There is deliberately **no `llmWiki.queryPlaneEnabled` or other-project access setting in workspace configuration**. Those grants remain local product-owned extension state managed through explicit product actions.
