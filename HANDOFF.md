# Current Handoff

Last updated: 2026-08-24 KST

This file is a **living continuation checkpoint**, not project history. Keep only current state, authority boundaries, active evidence questions, and next actions. Historical rationale belongs in merged commits, PRs, ADRs, experiments, or dedicated design documents. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, relevant current design docs, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

### Published baseline

- `main`: `8b981339aa896ad76c2b1d47244911626c5f78f5`
- validated/published dogfood: **0.1.21**
- product merge head: `abd93c57567afbeef960a86ccf0dc204adc3691f`
- versioned VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.21.vsix`
- stable convenience path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX bytes: `140151`
- SHA-256: `fa4d166abb6ac8331f06d729b3be2c0d91d660cf210e4cf33f2eda55d09d1fc2`
- validated GitHub Actions build: `32686519533`
- PR #217: **merged**
- public Beta: **not declared**

The published VSIX is the exact artifact emitted after the successful `VS Code Dogfood` run on `main`, including packaged-VSIX Extension Host execution. The versioned 0.1.21 path is immutable under the existing release rule.

### Active product work

The project is now in **installed UX vNext U0 dogfood**. Do not reopen the Authority Core merely because interaction quality still needs work.

U0 is shipped:

- one native LLM Wiki Activity Bar container;
- one native Tree View / Welcome View;
- persistent user-facing state for Project memory, AI summaries, AI-assisted memory answers, and Other project memories;
- registered external projects shown by display name only;
- existing safe configuration flows reachable from the relevant overview rows;
- sparse title actions for Agent Chat, health details, and refresh;
- first-install walkthrough reduced to installed -> setup -> Agent Chat;
- **no Webview, no canonical schema migration, no retrieval/model/grant widening**.

Design gate: `docs/product-ux-vnext.md`.

The product direction implements the existing intent in `docs/12-autonomy-ux-philosophy.md`: ordinary Agent chat is primary, automation is ambient but legible, review should not become an approval storm, and Doctor/manual commands are expert/fallback surfaces.

## PRODUCT / UX TARGET

Optimize for the user's small task model rather than exposing the system's internal authority model.

A normal user should be able to answer:

1. Is project memory on here?
2. What optional AI behavior is on?
3. Are other project memories available?
4. Did something I asked to remember become durable memory?
5. Is anything waiting for my judgment?
6. If something is wrong, what is the next safe action?

Default product language should prefer `Project memory`, `AI summaries`, `AI-assisted memory answers`, `Other project memories`, and later `Needs attention` / plain-language pending decisions.

Technical terms such as RAW/DERIVED enum labels, `current_store`, `library_store`, opaque store IDs, `scope_ref`, authority epochs, experiment tags, and calibration fields remain available where actually needed: tool contracts, provenance, diagnostics, tests, and expert inspection.

## AUTHORITY FLOOR — DO NOT WEAKEN FOR UX

The Alpha Core is ready under the convergence rule in `docs/09-alpha-core-readiness-gate.md`. New core work still requires a real dogfood/trust failure or an earned evidence boundary.

Non-negotiable current invariants:

- workspace use is explicit opt-in; disabling/re-enabling invalidates stale Query/Library workspace grants;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` = immutable admitted evidence / provenance authority;
- `DERIVED_MEMORY` = noncanonical, rebuildable navigation/synthesis aid;
- `HUMAN_KNOWLEDGE` = explicit user-owned project decision/belief/rationale;
- source admission, Human Knowledge authorship, and canonical lineage semantics remain human-gated;
- changed remembered files never silently become correction/change/dispute/supersession;
- authorization constrains external scope before retrieval/model exposure;
- external project memory remains explicitly registered, explicitly named, **read-only**, and separately granted per current workspace;
- wrong/unknown/ambiguous/revoked/unavailable external scope fails closed with no current/other-store fallback;
- terminal Wiki Brief refs terminate only on RAW/HUMAN_KNOWLEDGE;
- private filesystem roots stay out of normal Agent/model output;
- Query usage reservation remains conservative; uncertain/failed attempts are not silently refunded;
- no silent broad-RAW fallback.

See ADR-0002 and `docs/12-autonomy-ux-philosophy.md` for the product/core boundary. Do not duplicate epistemic/storage logic into the VS Code UI merely to make the interface convenient.

## CURRENT PRODUCT BOUNDARY

Still true unless a later evidence-backed change explicitly supersedes it:

- trusted **single-folder** workspace only; multi-root fails closed;
- each project keeps an independent Authority Core (`.wiki-lab` by default);
- ordinary `wikiMemory` / `wikiConsult` remain current-store-only;
- other-project memory is named-store-only, local routing/authorization state — not a merged/global knowledge store;
- external reads never authorize external writes, maintenance, source admission, Human Knowledge mutation, or lineage mutation;
- exact external scope is preserved through `wikiRead` follow-through;
- Query Plane remains read-only and exact composer model remains `gpt-5.6-luna`;
- existing-store portability is earned; sync, Remote-runtime support, and multi-writer behavior are not.

## UX VNEXT SEQUENCE

Do not build every desirable surface at once. Earn each slice in installed use.

### U0 — Product shell — SHIPPED / DOGFOOD ACTIVE

Published as **0.1.21**. Judge it through ordinary installed work, not screenshots or synthetic support counts alone.

Current evidence questions:

- can a fresh user set up memory without README/maintainer help?
- can they tell at a glance whether project memory and optional AI features are on?
- can they see and understand other-project memory availability without store IDs/paths?
- do they naturally return to Agent chat instead of treating LLM Wiki as a separate database app?
- can they find technical health/recovery only when needed?
- does the legacy status-bar entry still pull users toward a diagnostic-first mental model, or is the new Overview sufficient? Treat installed behavior as the deciding evidence.

### U1 — Safe action placement — NOT OPENED

Candidate: contextual `Remember in Project Memory`, but only after the existing `rememberWikiSource` admission contract is shared/reused. It must preserve dirty-editor refusal, explicit admission confirmation, same-file reuse/detection, pending-lineage creation, and optional maintenance behavior. Do **not** create a weaker parallel ingest path for discoverability.

### U2 — Pending decisions / activity — NOT OPENED

Candidate: plain-language semantic choices over the existing verified lineage mechanism plus bounded review/activity. Canonical relation enums stay unchanged internally.

### U3 — Other-project memory simplification — NOT OPENED

Candidate: project-folder-first registration, derived display name, aliases as advanced, and coherent sequencing of still-separate registration/access/query authorities.

### U4 — AI-assisted answer configuration — NOT OPENED

Candidate: meaningful bounded choices plus Custom instead of unexplained bare-number entry, while preserving explicit user selection and the exact stored numeric caps.

## NOT EARNED / PARKED

- library-wide ambient/union search;
- sync/Git/cloud replication and automatic remote discovery;
- validated Remote SSH / WSL / Dev Container / Codespaces product boundary;
- multi-writer semantic merge, distributed locks, or automatic conflict resolution;
- Personal/global writable store or cross-project writes;
- portable global identity, automatic person/alias routing, graph/entity/ontology infrastructure;
- vector-default retrieval or background cross-project maintenance;
- E024 L1 iterative Librarian;
- G2 Persistence: **NOT_EARNED; parked**;
- G3 Identity / Routing: **NOT_OPENED**;
- paid E023 semantic reruns remain paused absent explicit authorization/evidence.

## RELEASE / VALIDATION EVIDENCE

0.1.21 release gate is complete:

- PR head `111619735b0dac20de0ca28653111c7459a3814b`: VS Code Dogfood and E004/E010/E014/E023/E026 checks green;
- merged product head `abd93c57567afbeef960a86ccf0dc204adc3691f`;
- main `VS Code Dogfood` run `32686519533`: successful;
- packaged VSIX executed in Extension Host before artifact publication;
- release bot published versioned and `latest` VSIX paths at main `8b981339aa896ad76c2b1d47244911626c5f78f5`;
- release validation required **0 model calls** for U0 itself.

E020 remains a deterministic safety/product-contract gate, **not a human product-quality score**.

## FAST POINTERS

- UX vNext design gate: `docs/product-ux-vnext.md`
- autonomy/UX contract: `docs/12-autonomy-ux-philosophy.md`
- VS Code-first/editor-agnostic core: `decisions/ADR-0002-vscode-first-editor-agnostic-core.md`
- Alpha Core convergence rule: `docs/09-alpha-core-readiness-gate.md`
- U0 implementation/review: merged PR **#217**
- current published release metadata: `dogfood/releases/README.md`
- installed product guide: `dogfood/vscode/README.md`
- natural installed evidence: #141
- cross-workspace / named-store evidence: #202
- Query Plane: #204
- portability / future remote work: #213
- reliability: #132

## NEXT ACTION

1. **Install and dogfood 0.1.21 in ordinary Agent work now.** Collect task-level UX evidence; do not treat E020 counts or visual polish as sufficient evidence.
2. Fix U0-level interaction friction only when installed use makes it concrete. Keep those fixes in the adapter/product layer unless a genuine authority/trust failure proves otherwise.
3. Open U1 only after U0 installed use confirms the persistent product shell is useful. U1 source-admission discoverability must reuse the existing safe admission path.
4. Keep U2-U4 gated behind the preceding installed evidence rather than implementing the roadmap mechanically.
5. Keep broader core/retrieval/sync/reliability work parked unless independent evidence activates it.
