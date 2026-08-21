# LLM Wiki for VS Code — 0.1.17 candidate

LLM Wiki gives your coding Agent **durable project memory that you control**.

0.1.17 keeps the 0.1.16 authority model and adds an **opt-in Luna-backed Wiki Query Plane** for installed dogfood. The Query Plane is intended to keep broad Wiki retrieval/composition work out of the Main Agent context while returning a compact, provenance-backed Wiki Brief.

This is an Alpha/dogfood candidate, not a public Beta declaration.

## Get started

1. Install the candidate `.vsix`.
2. Open one trusted local workspace folder. Multi-root workspaces remain fail-closed.
3. Run **LLM Wiki: Set Up Project Memory**.
4. Keep the private Wiki directory out of Git. The default is `.wiki-lab/`.
5. Continue in normal Agent chat.

Installing the extension gives VS Code the capability. **Setting up a workspace gives the Agent permission to use project memory there.** Existing `.wiki-lab` data alone never silently enables Agent access.

## Normal use

You do not need to learn Wiki tool names.

A historical question can simply be:

> “왜 예전에 Redis를 안 쓰기로 했지?”

When you want to preserve something, say it naturally:

> “이 파일 프로젝트 기억에 저장해.”

or:

> “우리는 운영 복잡성 때문에 Redis를 아직 쓰지 않기로 결정했어. 이 결정 기억해.”

LLM Wiki keeps authority boundaries explicit. Durable source admission, user-owned Human Knowledge, and the semantic relationship between changed revisions remain human-approved.

## Five normal commands

The normal Command Palette intentionally stays small:

- **LLM Wiki: Set Up Project Memory** — explicitly enable this workspace.
- **LLM Wiki: Check Setup and Health** — read-only diagnostics; zero model calls and zero state changes.
- **LLM Wiki: Configure AI Summaries** — optional source-scoped Copilot summaries; off by default.
- **LLM Wiki: Configure Wiki Query Reasoning** — optional Luna-backed query reasoning; off until a separate local grant is created.
- **LLM Wiki: Disable for This Workspace** — stop Agent access while preserving Wiki data.

Advanced/manual commands remain available for explicit fallback and dogfood inspection but stay out of the normal palette.

## Project memory is local-first

The default private store is `.wiki-lab/` inside the workspace. Treat it as sensitive project data and keep it out of Git.

It can contain immutable admitted source evidence, correction/change/dispute/supersession history, explicitly confirmed Human Knowledge, optional rebuildable AI summaries, and local workflow metadata such as pending lineage decisions.

Back up the **whole directory as one private snapshot**. See `docs/11-local-backup-restore.md`.

## Authority model

The product contract distinguishes:

- **RAW_MEMORY** — immutable admitted evidence and provenance authority.
- **DERIVED_MEMORY** — noncanonical, rebuildable synthesis/navigation aid.
- **HUMAN_KNOWLEDGE** — a user-confirmed decision, belief, rationale, or approved synthesis; authoritative as a record of what the user confirmed, not as independent external evidence.

Changed remembered files never silently become corrections or later states. The user explicitly chooses correction, change, dispute, supersede, or independent evidence.

Remembered source/model text is untrusted data, never executable Agent instruction.

## Wiki Query Reasoning — 0.1.17 opt-in slice

The Query Plane is **separately opt-in**. Setting up project memory does not authorize it, and enabling AI summaries does not authorize it.

Run **LLM Wiki: Configure Wiki Query Reasoning** to create or revoke the local grant.

When enabled, an ordinary `wikiConsult` call may:

1. search the current authorized project store with deterministic retrieval;
2. follow selected candidates to verified query-relevant raw regions;
3. include relevant current Human Knowledge and unresolved lineage state with their epistemic roles preserved;
4. send that bounded evidence packet to GitHub Copilot using exact `gpt-5.6-luna`;
5. return a compact Wiki Brief containing the answer, terminal authority references, and insufficiency status.

The Query Plane is read-only. It cannot admit sources, write Human Knowledge, decide lineage, or mutate canonical Wiki history.

### Separate local grant

The Query Plane grant lives in VS Code extension **local workspace state**, not in a workspace setting file. It is therefore not intended to be committed or shared with the project.

The grant is versioned and records the provider/model/current-store exposure boundary plus two user-chosen usage guards.

### User-chosen usage guards

The product does not silently choose a Query Plane spend boundary.

Before the grant is created, the user explicitly chooses:

1. a local **daily model-call attempt cap** from 1 to 100; and
2. a Copilot CLI **per-response AI-credit soft guard** from 1 to 100.

The daily counter is a local safety bound, not a billing estimate. Failed/uncertain model attempts remain counted so transport uncertainty cannot silently refund usage.

The per-response value is passed to Copilot as its `max-ai-credits` soft guard. If the installed Copilot CLI cannot enforce that flag, Query Plane execution fails **before** a model call rather than silently dropping the user's chosen guard.

LLM Wiki does not infer dollars, premium-request counts, AI credits, or exact token cost from the daily counter. The provider-side per-response guard is still a soft limit, not an exact bill.

### No silent raw fallback

If Query Reasoning is disabled, the local daily cap is reached, candidate verification fails, Luna is unavailable, the provider cannot enforce the selected per-response guard, or the returned brief violates the contract, `wikiConsult` fails boundedly.

It does **not** silently dump a broad raw Wiki result back into the Main Agent context. `wikiMemory` and `wikiRead` remain explicit low-level provenance/debug tools.

### Shared Memory Read Service

`wikiMemory` and `wikiConsult` use the same deterministic candidate-collection service for current RAW, DERIVED navigation, Human Knowledge, and pending lineage state. This prevents the two read paths from evolving different authority semantics.

For Query Plane evidence materialization, raw candidates are followed to bounded **query-relevant verified regions** rather than blindly reading the first 6,000 characters of a long source. If a selected candidate cannot be verified, the consult fails closed instead of silently omitting that authority.

If RAW discovery and DERIVED navigation point to the same source, their deterministic query hints are merged before relevant-region selection. DERIVED remains nonterminal; this only preserves its intended navigation role.

### Terminal provenance

A Wiki Brief may terminate on:

- `RAW_MEMORY`;
- `HUMAN_KNOWLEDGE`.

`DERIVED_MEMORY` and pending-lineage workflow state are nonterminal. Derived notes can help navigation, but a load-bearing factual claim must resolve to terminal authority.

Terminal references are scope-qualified. 0.1.17 only authorizes the current store, but the reference shape is intentionally compatible with a future explicitly authorized multi-store/federation layer without changing the Main-Agent `wikiConsult` contract.

### Query Composer isolation

The Luna Query Composer receives its evidence over stdin and does not receive a Wiki-root argument. The actual Copilot subprocess runs from a neutral temporary working directory rather than the project workspace.

The Query Plane transport also removes generic `GH_TOKEN` / `GITHUB_TOKEN` overrides, Copilot allow-all/model overrides, and `COPILOT_PROVIDER_*` BYOK-routing variables before launching the composer. An explicit `COPILOT_GITHUB_TOKEN` and normal Copilot home/auth state may still be used.

The Query Plane adds current generic Copilot read/write/url/memory/web-search tool names to its excluded-tool boundary in addition to the hardened adapter's existing exclusions. No shell/web/file/memory tool is part of the Query Plane contract.

The composer returns only the bounded structured result; hidden reasoning/retrieval traces are not returned to the Main Agent.

## Existing low-level Agent tools remain available

While project memory is enabled, the Agent may use:

- `#wikiConsult` / `llmWiki_consultMemory` — opt-in compact Query Plane path.
- `#wikiMemory` / `llmWiki_searchMemory` — low-level read-only memory search.
- `#wikiRead` / `llmWiki_readSource` — verified immutable source read with pagination.
- `#rememberWikiSource` / `llmWiki_rememberSource` — durable local source admission after product confirmation.
- `#rememberHumanKnowledge` / `llmWiki_rememberHumanKnowledge` — user-owned project knowledge after product confirmation.
- `#resolveWikiLineage` / `llmWiki_resolveLineage` — record an explicitly chosen relation between changed revisions.

0.1.17 does **not** remove or weaken `wikiMemory`/`wikiRead`. Installed dogfood must earn any later decision to make `wikiConsult` the ordinary default path.

## AI summaries remain separate

**LLM Wiki: Configure AI Summaries** controls a separate outbound-data grant. It is off by default.

When enabled, explicitly admitted source content may be sent to GitHub Copilot using exact `gpt-5.6-luna` to create/reuse a rebuildable source-scoped summary. AI summaries never replace RAW evidence or become Human Knowledge automatically.

Query Plane permission and usage accounting remain separate from maintenance permission and maintenance usage.

## Workspace permission boundary

Before **Set Up Project Memory** succeeds:

- Agent tools are hidden by contribution conditions;
- runtime tool implementations are not registered;
- setup/health make no model call.

**Disable for This Workspace** removes only the opt-in marker and immediately tears down Agent tool registrations while preserving Wiki data. The Query Plane tool shares this same lifecycle; a separate query grant cannot keep the tool alive in a disabled workspace.

0.1.17 remains single-folder only.

## Check Setup and Health

**LLM Wiki: Check Setup and Health** remains a pure diagnostic command:

- **0 model calls**;
- **0 state changes**;
- no initialization or repair;
- no source/prompt/evidence content printed.

It reports project-memory state, local-store integrity, Python/Copilot executable presence, AI-summary state, and whether Query Reasoning is granted plus its daily call cap. Model-call readiness remains explicitly unverified because the health check does not make a model call just to prove availability.

## Python runtime

The bundled local core requires Python 3.9+.

`llmWiki.pythonExecutable` is empty by default and auto-detects:

- Windows: `python`, then `py`, then `python3`;
- macOS/Linux: `python3`, then `python`.

An explicit override is respected rather than silently falling back.

## Errors and recovery

For users, failures should say what failed, what was preserved, and what action is available without dumping source text, prompts, arbitrary paths, or secrets.

For Agent-facing failures, product code uses bounded causal states/codes. Unknown subprocess detail collapses to a generic bounded failure rather than exposing arbitrary stderr.

Query Plane transport/model failure never authorizes broad raw-memory fallback.

## Confirmation policy

Blocking confirmation is reserved for authority/privacy/usage boundaries such as:

- setting up or disabling project memory;
- source admission;
- saving Human Knowledge;
- resolving changed-source semantics;
- enabling AI summaries;
- enabling Query Reasoning and choosing its daily-call and per-response AI-credit guards.

Routine search/read/diagnostic success should remain quiet.

## 0.1.17 validation gate

The candidate must preserve the existing deterministic safety/product contract while adding the opt-in Query Plane slice.

Required before peer-review/merge handoff:

- Python 3.9 compatibility;
- full Python unit regression suite;
- frozen E004/E014 checks;
- E010 self-repo dogfood;
- E023 G2 closure validator;
- frozen E020 synthetic contract: **78 cases / 60 supported / 7 partial / 11 deferred / zero model calls**;
- VS Code static boundaries;
- Extension Host integration tests;
- bundled-core checks;
- VSIX packaging and packaged Extension Host execution;
- no new paid semantic benchmark as part of this PR.

The E024 semantic experiment that earned L0 is already merged separately; this product PR should not re-tune against that material.

## What installed dogfood must decide

0.1.17 should collect natural evidence about:

- whether the Agent invokes `wikiConsult` at useful moments;
- whether Main-Agent-visible Wiki context/tool-turn burden actually drops in real work;
- whether compact briefs are sufficient without repeated `wikiRead` follow-up;
- whether query latency is acceptable;
- whether insufficiency is correctly conservative rather than annoying;
- whether long sources recover the right authority region;
- whether pending/history semantics remain understandable;
- whether the separate evidence-exposure and usage-guard UX is understandable;
- whether a deterministic bounded packet without Luna could provide enough value as a competing hypothesis.

Do not use this slice as permission to add iterative L1 retrieval, cross-workspace federation, vectors/graphs/entities, background semantic maintenance, or autonomous semantic persistence. Those remain separately evidence-gated.

## Settings

- `llmWiki.pythonExecutable` — optional Python override.
- `llmWiki.corePath` — advanced local core override.
- `llmWiki.workspaceDirectory` — private local store; default `.wiki-lab`.
- `llmWiki.maxAiCredits` — legacy explicit Ask Luna preferred guard.
- `llmWiki.agentWikiMaintenanceEnabled` — optional AI summaries; separate grant.
- `llmWiki.agentWikiMaintenanceMaxAiCredits` — preferred per-summary CLI guard when supported.
- `llmWiki.agentWikiMaintenanceDailyCallLimit` — AI-summary soft-guard threshold.

There is deliberately **no `llmWiki.queryPlaneEnabled` or Query Plane spend setting in workspace configuration**. Query Reasoning authorization and its user-chosen guards are local product-owned extension state managed through **Configure Wiki Query Reasoning**.
