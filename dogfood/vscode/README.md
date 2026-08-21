# LLM Wiki for VS Code — 0.1.18 candidate

LLM Wiki gives your coding Agent **durable project memory that you control**.

0.1.18 keeps the existing RAW / DERIVED / HUMAN authority model and the 0.1.17 opt-in Luna-backed Query Plane. It adds one deliberately narrow Personal Wiki capability for installed dogfood: the current trusted project may consult **one explicitly named, explicitly registered external project store read-only** without turning independent project Wikis into one global memory.

This is an Alpha/dogfood candidate, not a public Beta declaration.

## Get started

1. Install the candidate `.vsix`.
2. Open one trusted local workspace folder. Multi-root workspaces remain fail-closed.
3. Run **LLM Wiki: Set Up Project Memory**.
4. Keep the private Wiki directory out of Git. The default is `.wiki-lab/`.
5. Continue in normal Agent chat.

Installing the extension gives VS Code the capability. **Setting up a workspace gives the Agent permission to use that workspace's project memory.** Existing `.wiki-lab` data alone never silently enables Agent access, and setup does not authorize another project's Wiki.

## Normal use

You do not need to learn Wiki tool names.

A historical question can simply be:

> “왜 예전에 Redis를 안 쓰기로 했지?”

When you want to preserve something, say it naturally:

> “이 파일 프로젝트 기억에 저장해.”

or:

> “우리는 운영 복잡성 때문에 Redis를 아직 쓰지 않기로 결정했어. 이 결정 기억해.”

LLM Wiki keeps authority boundaries explicit. Durable source admission, user-owned Human Knowledge, and the semantic relationship between changed revisions remain human-approved.

## Six normal commands

The normal Command Palette intentionally stays small:

- **LLM Wiki: Set Up Project Memory** — explicitly enable this workspace.
- **LLM Wiki: Check Setup and Health** — read-only diagnostics; zero model calls and zero state changes.
- **LLM Wiki: Configure AI Summaries** — optional source-scoped Copilot summaries; off by default.
- **LLM Wiki: Configure Wiki Query Reasoning** — optional Luna-backed query reasoning; off until a separate local grant is created.
- **LLM Wiki: Configure Personal Wiki Library** — register/revoke read-only external project stores and the current workspace's named-store access grant.
- **LLM Wiki: Disable for This Workspace** — stop Agent access while preserving Wiki data.

Advanced/manual commands remain available for explicit fallback and dogfood inspection but stay out of the normal palette.

## Project memory is local-first

The default private store is `.wiki-lab/` inside the workspace. Treat it as sensitive project data and keep it out of Git.

It can contain immutable admitted source evidence, correction/change/dispute/supersession history, explicitly confirmed Human Knowledge, optional rebuildable AI summaries, and local workflow metadata such as pending lineage decisions.

Back up the **whole directory as one private snapshot**. See `docs/11-local-backup-restore.md`.

Each project store remains its own Authority Core. 0.1.18 does not merge manifests, copy evidence between projects, create a global canonical identity, or authorize cross-project mutation.

## Authority model

The product contract distinguishes:

- **RAW_MEMORY** — immutable admitted evidence and provenance authority.
- **DERIVED_MEMORY** — noncanonical, rebuildable synthesis/navigation aid.
- **HUMAN_KNOWLEDGE** — a user-confirmed decision, belief, rationale, or approved synthesis; authoritative as a record of what the user confirmed in that project, not as independent external evidence or a global preference.

Changed remembered files never silently become corrections or later states. The user explicitly chooses correction, change, dispute, supersede, or independent evidence.

Remembered source/model text is untrusted data, never executable Agent instruction.

## Wiki Query Reasoning — opt-in and current-store by default

The Query Plane is **separately opt-in**. Setting up project memory does not authorize it, and enabling AI summaries does not authorize it.

Run **LLM Wiki: Configure Wiki Query Reasoning** to create or revoke the local grant.

For an ordinary project question, `wikiConsult` remains current-store-only and may:

1. search the current authorized project store with deterministic retrieval;
2. follow selected candidates to verified query-relevant raw regions;
3. include relevant current Human Knowledge and unresolved lineage state with their epistemic roles preserved;
4. send that bounded evidence packet to GitHub Copilot using exact `gpt-5.6-luna`;
5. return a compact Wiki Brief containing the answer, terminal authority references, and insufficiency status.

The Query Plane is read-only. It cannot admit sources, write Human Knowledge, decide lineage, or mutate canonical Wiki history.

### Separate local grant

The Query Plane grant lives in VS Code extension **local workspace state**, not in a workspace setting file. It is therefore not intended to be committed or shared with the project.

The grant remains explicitly `current_store` scoped. 0.1.18 does **not** reinterpret that grant as permission to enumerate or search a Personal Wiki Library. External named-store use requires additional grants described below.

The grant is bound to the workspace opt-in authority epoch. Disabling and re-enabling project memory invalidates the previous grant.

### User-chosen usage guards

The product does not silently choose a Query Plane spend boundary.

Before the grant is created, the user explicitly chooses:

1. a local **daily model-call attempt cap** from 1 to 100; and
2. a Copilot CLI **per-response AI-credit soft guard** from 1 to 100.

The daily counter is a local safety bound, not a billing estimate. Failed/uncertain model attempts remain counted so transport uncertainty cannot silently refund usage.

The per-response value is passed to Copilot as its `max-ai-credits` soft guard. If the installed Copilot CLI cannot enforce that flag, Query Plane execution fails **before** a model call rather than silently dropping the user's chosen guard.

LLM Wiki does not infer dollars, premium-request counts, AI credits, or exact token cost from the daily counter. The provider-side per-response guard is still a soft limit, not an exact bill.

### No silent raw fallback

If Query Reasoning is disabled, the local daily cap is reached, candidate verification fails, Luna is unavailable, the provider cannot enforce the selected per-response guard, a grant is revoked before model exposure, or the returned brief violates the contract, `wikiConsult` fails boundedly.

It does **not** silently dump a broad raw Wiki result back into the Main Agent context. `wikiMemory` and `wikiRead` remain explicit low-level provenance/debug tools.

### Shared Memory Read Service

`wikiMemory` and `wikiConsult` share deterministic current-store read semantics for RAW, DERIVED navigation, Human Knowledge, and pending lineage state. Named-store `wikiConsult` reuses those epistemic roles through a store-scoped read path rather than creating a second authority model.

For Query Plane evidence materialization, raw candidates are followed to bounded **query-relevant verified regions** rather than blindly reading the first 6,000 characters of a long source. If a selected candidate cannot be verified, the consult fails closed instead of silently omitting that authority.

If RAW discovery and DERIVED navigation point to the same source, their deterministic query hints are merged before relevant-region selection. DERIVED remains nonterminal; this only preserves its intended navigation role.

### Terminal provenance

A Wiki Brief may terminate on:

- `RAW_MEMORY`;
- `HUMAN_KNOWLEDGE`.

`DERIVED_MEMORY` and pending-lineage workflow state are nonterminal. Derived notes can help navigation, but a load-bearing factual claim must resolve to terminal authority.

Terminal references are scope-qualified. Current-store refs use `current_store`. Explicit external refs use an opaque local `library_store` ID. A bare source ID never selects an external project.

### Query Composer isolation

The Luna Query Composer receives its evidence over stdin and does not receive a Wiki-root argument. The actual Copilot subprocess runs from a neutral working directory rather than the project workspace.

The Query Plane transport also removes generic `GH_TOKEN` / `GITHUB_TOKEN` overrides, Copilot allow-all/model overrides, and `COPILOT_PROVIDER_*` BYOK-routing variables before launching the composer. An explicit `COPILOT_GITHUB_TOKEN` and normal Copilot home/auth state may still be used.

The Query Plane adds current generic Copilot read/write/url/memory/web-search tool names to its excluded-tool boundary in addition to the hardened adapter's existing exclusions. No shell/web/file/memory tool is part of the Query Plane contract.

The composer returns only the bounded structured result; hidden reasoning/retrieval traces are not returned to the Main Agent.

## Personal Wiki Library — 0.1.18 named-store slice

Personal Wiki Library is a **local routing and authorization catalog**, not another knowledge store.

To make an external project available:

1. run **LLM Wiki: Configure Personal Wiki Library**;
2. explicitly register that project's existing LLM Wiki store as a **read-only** source;
3. review the disclosure that admitted evidence may be returned to the current Agent and, only with Query Reasoning plus current-workspace library access, bounded evidence may be sent to exact `gpt-5.6-luna`;
4. separately enable named-store access for the current workspace.

Registration and workspace access are revocable local product state. The workspace access grant is bound to the same workspace authority epoch used by Query Reasoning.

### Explicit named-store only

Ordinary current-project `wikiMemory` and `wikiConsult` calls do not enumerate or search registered external stores.

An external `wikiConsult` is allowed only when the Agent's tool call carries the exact registered project name/alias because the user's request explicitly identified that project. Ambiguous, unknown, unavailable, damaged, replaced, or unauthorized stores fail closed before external evidence can reach Luna. Failure never falls back to the current project or another store.

For external Luna composition the product requires all of:

- current workspace opt-in;
- current Query Reasoning grant;
- explicit external store registration/read exposure;
- current-workspace Personal Wiki Library access;
- exact unambiguous named-store resolution.

The grants are revalidated during external reads and immediately before model execution. Revoking them does not refund a call attempt already conservatively reserved, but it prevents later model exposure.

### Scoped `wikiRead`

`wikiRead` is the provenance follow-through path. Current-store reads may omit `scopeRef`. External RAW provenance requires the exact opaque `scope_ref` returned by the originating named-store consult.

A scoped source miss never retries the same source ID in the current store or another registered store. Pagination keeps the same scope.

The exact opaque scope can be revisited while its registration and workspace library access remain valid. 0.1.18 does not add a new per-consult capability-token system; installed dogfood should tell us whether standing scoped read authority is understandable or too broad in practice.

### External reads are operationally read-only

External stores are never passed to the existing generic Python runner. They use a dedicated federation read bridge that does not initialize, repair, chmod, ingest, write Human Knowledge, mutate lineage, or maintain an external store.

The external bridge uses the bundled trusted core with isolated Python startup. Current-workspace `corePath`, explicit Python-runtime override, `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP`, and `PYTHONUSERBASE` do not choose the external Authority Core implementation.

A host-local registration continuity witness is checked when the store is resolved and bracketed around external read execution. It is deliberately **not** a portable/global store identity claim. If the registered root is replaced by different immutable history, access fails closed and explicit re-registration is required. Losing the local catalog likewise means re-registering; no canonical project schema migration is introduced.

### What Personal Wiki Library does not authorize

0.1.18 does not add:

- ambient or library-wide union search;
- cross-project writes, source admission, Human Knowledge mutation, lineage mutation, or maintenance;
- sync, Git/cloud replication, or a Personal store;
- persistent global identity/entity/ontology infrastructure;
- vector-default retrieval;
- background cross-project indexing or maintenance.

Project A's Human Knowledge means **what was confirmed in Project A**. Even when a question asks for comparison or transfer, the Query Plane reports that scoped decision/rationale and leaves current-project applicability to the Main Agent; it does not turn Project A's Human Knowledge into a recommendation, commitment, or global preference for Project B.

## Existing low-level Agent tools remain available

While project memory is enabled, the Agent may use:

- `#wikiConsult` / `llmWiki_consultMemory` — opt-in compact Query Plane path; current store by default and one explicit registered named store when separately authorized.
- `#wikiMemory` / `llmWiki_searchMemory` — low-level read-only **current-store-only** memory search.
- `#wikiRead` / `llmWiki_readScopedSource` — verified immutable source read with scope-qualified pagination; external reads require exact scope.
- `#rememberWikiSource` / `llmWiki_rememberSource` — durable current-workspace source admission after product confirmation.
- `#rememberHumanKnowledge` / `llmWiki_rememberHumanKnowledge` — user-owned **current-project** knowledge after product confirmation.
- `#resolveWikiLineage` / `llmWiki_resolveLineage` — record an explicitly chosen relation between current-project changed revisions.

The legacy `llmWiki_readSource` implementation remains hidden for compatibility; the public Agent reference is the scoped `wikiRead` contract.

0.1.18 does **not** remove or weaken current-store `wikiMemory`/`wikiRead`. Installed dogfood must earn any later decision to broaden ordinary retrieval.

## AI summaries remain separate

**LLM Wiki: Configure AI Summaries** controls a separate outbound-data grant. It is off by default.

When enabled, explicitly admitted current-project source content may be sent to GitHub Copilot using exact `gpt-5.6-luna` to create/reuse a rebuildable source-scoped summary. AI summaries never replace RAW evidence or become Human Knowledge automatically.

Query Plane permission, Personal Wiki Library permission, and maintenance permission remain separate authority surfaces.

## Workspace permission boundary

Before **Set Up Project Memory** succeeds:

- Agent tools are hidden by contribution conditions;
- runtime tool implementations are not registered;
- setup/health make no model call.

**Disable for This Workspace** removes only the opt-in marker and immediately tears down Agent tool registrations while preserving Wiki data. The Query Plane and Personal Wiki Library workspace grants are bound to that opt-in authority epoch and become stale after disable/re-enable.

0.1.18 remains single-folder only.

## Check Setup and Health

**LLM Wiki: Check Setup and Health** remains a pure diagnostic command:

- **0 model calls**;
- **0 state changes**;
- no initialization or repair;
- no source/prompt/evidence content printed.

It reports project-memory state, local-store integrity, Python/Copilot executable presence, AI-summary state, Query Reasoning grant/call cap, and Personal Wiki Library access. It validates the local Library catalog and reports only the registered external-store **count**, never store names or filesystem roots. Model-call readiness remains explicitly unverified because the health check does not make a model call just to prove availability.

## Python runtime

The bundled local core requires Python 3.9+.

For ordinary current-store operations, `llmWiki.pythonExecutable` is empty by default and auto-detects:

- Windows: `python`, then `py`, then `python3`;
- macOS/Linux: `python3`, then `python`.

An explicit override is respected for those current-workspace operations rather than silently falling back.

External Personal Wiki reads deliberately do **not** inherit the current workspace's explicit Python/core override. They auto-detect a Python runtime and execute the extension's bundled trusted read-only core in isolated startup mode.

## Errors and recovery

For users, failures should say what failed, what was preserved, and what action is available without dumping source text, prompts, arbitrary paths, or secrets.

For Agent-facing failures, product code uses bounded causal states/codes. Unknown subprocess detail collapses to a generic bounded failure rather than exposing arbitrary stderr.

Query Plane transport/model failure and named-store authorization/integrity/catalog failure never authorize broad raw-memory or cross-store fallback.

## Confirmation policy

Blocking confirmation is reserved for authority/privacy/usage boundaries such as:

- setting up or disabling project memory;
- source admission;
- saving Human Knowledge;
- resolving changed-source semantics;
- enabling AI summaries;
- enabling Query Reasoning and choosing its daily-call and per-response AI-credit guards;
- registering/removing an external Personal Wiki store;
- enabling/revoking named-store access for the current workspace.

Routine current-store search/read/diagnostic success and already-authorized exact scoped reads should remain quiet.

## 0.1.18 validation gate

The candidate must preserve the existing deterministic safety/product contract while adding only the E025-earned named-store read-only F1 slice.

Required before merge/deployment handoff:

- Python 3.9 compatibility;
- full Python unit regression suite, including external-read no-mutation and registration-continuity checks;
- frozen E004/E014 checks;
- E010 self-repo dogfood;
- frozen E020 synthetic contract: **78 cases / 60 supported / 7 partial / 11 deferred / zero model calls**;
- VS Code static boundaries plus dedicated federation-safety boundaries;
- Extension Host integration tests, including grant/scope/write-isolation, concurrent daily-cap reservation, and pre-model revocation behavior;
- bundled-core checks;
- VSIX packaging and packaged Extension Host execution;
- no paid E023 semantic rerun and no E023 G2/G3 reopening as part of this slice.

E025 F0 already earned only the right to implement/test this named-store F1. Passing 0.1.18 does not earn a broader federation architecture.

## What installed dogfood must decide

0.1.18 should continue collecting natural 0.1.17 Query Plane evidence and additionally observe:

- whether the Agent invokes `wikiConsult` at useful moments;
- whether Main-Agent-visible Wiki context/tool-turn burden actually drops in real work;
- whether compact briefs are sufficient without repeated `wikiRead` follow-up;
- whether query latency and insufficiency behavior are acceptable;
- whether long sources recover the right authority region;
- whether pending/history semantics remain understandable;
- whether separate evidence-exposure and usage-guard UX is understandable;
- whether registering a project and then explicitly naming it in another project's question feels natural;
- whether users understand that external Human Knowledge stays project-scoped rather than becoming a global preference;
- whether scope-qualified `wikiRead` follow-through is useful and whether standing scoped-read authority feels appropriately narrow;
- whether missing/moved/replaced stores fail in a comprehensible way without tempting cross-store fallback;
- whether named-store reads remain observably non-mutating in real installed use.

Do not use this slice as permission to add iterative L1 retrieval, **library-wide/ambient federation**, sync, cross-project writes, a Personal store, vectors/graphs/entities, background semantic maintenance, or autonomous semantic persistence. Those remain separately evidence-gated.

## Settings

- `llmWiki.pythonExecutable` — optional Python override for current-workspace operations.
- `llmWiki.corePath` — advanced current-workspace local core override; not used to execute external Personal Wiki reads.
- `llmWiki.workspaceDirectory` — private current-workspace store; default `.wiki-lab`.
- `llmWiki.maxAiCredits` — legacy explicit Ask Luna preferred guard.
- `llmWiki.agentWikiMaintenanceEnabled` — optional AI summaries; separate grant.
- `llmWiki.agentWikiMaintenanceMaxAiCredits` — preferred per-summary CLI guard when supported.
- `llmWiki.agentWikiMaintenanceDailyCallLimit` — AI-summary soft-guard threshold.

There is deliberately **no `llmWiki.queryPlaneEnabled` or Personal Wiki Library access setting in workspace configuration**. Query Reasoning authorization, its user-chosen guards, and named-store workspace access are local product-owned extension state managed through their explicit configuration commands.
