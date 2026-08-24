# Current Handoff

Last updated: 2026-08-24 KST

This file is a **living continuation checkpoint**, not project history. Keep only current state, authority boundaries, active evidence questions, and next actions. Historical rationale belongs in merged commits, PRs, ADRs, experiments, or dedicated design documents. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, relevant current design docs, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

### Published baseline

- published release commit: `8b981339aa896ad76c2b1d47244911626c5f78f5`
- validated/published dogfood: **0.1.21**
- product merge head: `abd93c57567afbeef960a86ccf0dc204adc3691f`
- versioned VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.21.vsix`
- stable convenience path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX SHA-256: `fa4d166abb6ac8331f06d729b3be2c0d91d660cf210e4cf33f2eda55d09d1fc2`
- validated main build: GitHub Actions `32686519533`
- public Beta: **not declared**

0.1.21 is the validated U0 product-shell release. It added persistent orientation/state but did **not** materially simplify the user's core tasks enough to re-run broad satisfaction dogfood.

### Active product work

The **UX/UI convergence phase** remains active.

Installed 0.1.21 evidence was decisive: the sidebar icon/overview solved product discoverability and basic state visibility, but the enabled experience was still mostly a handful of status rows pointing back to old commands. That is structural progress, not a sufficient user-experience change. Do not mistake technical dogfood readiness for satisfaction-level UX readiness.

Active implementation:

- branch: `agent/ux-vnext-actionable`
- draft PR: **#220 — UX vNext: make project memory actionable**
- candidate version: **0.1.22**
- design gate: `docs/product-ux-vnext.md`
- merge/release gate: full `VS Code Dogfood` must pass through normal Extension Host, VSIX packaging, and unpacked packaged-VSIX Extension Host execution.

0.1.22 candidate scope:

- make the native Overview action-oriented: **Ask Agent**, **Remember active file**, **Review saved-file changes**;
- add Explorer/editor context action **Remember in Project Memory**;
- reuse the already-registered guarded `llmWiki_rememberSource` path instead of creating a second ingest/write path;
- translate lineage enums into plain-language meaning choices, then reuse the existing verified/human-confirmed `llmWiki_resolveLineage` path;
- simplify Other Project Memories to **choose project folder -> detect `.wiki-lab` -> derive name -> read-only registration -> optional workspace access**; aliases are no longer mandatory in the primary flow;
- replace unexplained Query Reasoning numeric setup with explicit **Light / Regular / Frequent / Custom** choices while preserving the same typed numeric grant and validating it through the existing Query Plane contract;
- keep ordinary questions in Agent Chat and keep Doctor as technical recovery/details.

No custom Webview/dashboard is being added.

## PRODUCT / UX TARGET

Optimize for user goals and actions, not the internal authority model.

A normal user should be able to:

1. see whether project memory is ready;
2. ask Agent normally without learning tool names;
3. remember the file they are looking at from its natural context;
4. understand that a changed remembered file needs judgment and describe the change's **meaning** without learning relation enum names;
5. add another project's memory by choosing the project, not an implementation directory;
6. understand/enable optional AI behavior without inventing numeric policy from scratch;
7. recover through a clear next action, with raw diagnostics available only when needed.

Default UI language should prefer `Project memory`, `Remember`, `Review saved-file changes`, `AI summaries`, `AI-assisted memory answers`, `Other project memories`, and `Needs attention`.

Technical terms such as RAW/DERIVED enum labels, `current_store`, `library_store`, opaque store IDs, `scope_ref`, authority epochs, experiment tags, and calibration fields remain where actually needed: tool contracts, provenance, diagnostics, tests, and expert inspection.

## AUTHORITY FLOOR — DO NOT WEAKEN FOR UX

The Alpha Core remains ready under `docs/09-alpha-core-readiness-gate.md`. New core work still requires a real dogfood/trust failure or an earned evidence boundary.

Non-negotiable current invariants:

- workspace use is explicit opt-in; disabling/re-enabling invalidates stale Query/Library workspace grants;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` = immutable admitted evidence / provenance authority;
- `DERIVED_MEMORY` = noncanonical, rebuildable navigation/synthesis aid;
- `HUMAN_KNOWLEDGE` = explicit user-owned project decision/belief/rationale;
- source admission, Human Knowledge authorship, and canonical lineage semantics remain human-gated;
- dirty remembered files are never auto-saved;
- changed remembered files never silently become correction/change/dispute/supersession;
- lineage evidence/currentness/locator binding remains verified before confirmation and again immediately before canonical mutation;
- authorization constrains external scope before retrieval/model exposure;
- external project memory remains explicitly registered, explicitly named, **read-only**, and separately granted per current workspace;
- wrong/unknown/ambiguous/revoked/unavailable external scope fails closed with no current/other-store fallback;
- terminal Wiki Brief refs terminate only on RAW/HUMAN_KNOWLEDGE;
- private filesystem roots stay out of normal Agent/model output;
- Query usage reservation remains conservative; uncertain/failed attempts are not silently refunded;
- no silent broad-RAW fallback.

Do not duplicate epistemic/storage logic into the VS Code UI merely for convenience. Adapter UI may sequence or translate existing operations, but the authoritative implementation stays in the established guarded paths.

## CURRENT PRODUCT BOUNDARY

Still true unless later evidence explicitly supersedes it:

- trusted **single-folder** workspace only; multi-root fails closed;
- each project keeps an independent Authority Core (`.wiki-lab` by default);
- ordinary `wikiMemory` / `wikiConsult` remain current-store-only;
- other-project memory is named-store-only local routing/authorization state, not a merged/global knowledge store;
- external reads never authorize external writes, maintenance, source admission, Human Knowledge mutation, or lineage mutation;
- exact external scope is preserved through `wikiRead` follow-through;
- Query Plane remains read-only and exact composer model remains `gpt-5.6-luna`;
- existing-store portability is earned; sync, Remote-runtime support, and multi-writer behavior are not.

## UX VNEXT STATE

### U0 — Product shell — SHIPPED AS 0.1.21

Earned: persistent native orientation/state surface, concise setup state, human-readable project names, Agent-first mental model.

Installed evidence: **necessary but insufficient**. It made LLM Wiki easier to find, but did not reduce enough task-level friction by itself.

### U1 — Safe action placement — ACTIVE IN #220

Contextual Remember is now allowed because the UI can invoke the existing guarded remember tool rather than implementing a weaker parallel ingest path. Release only if real Extension Host testing proves that bridge end to end.

### U2 — Plain-language pending decision review — BOUNDED SLICE ACTIVE IN #220

Only the meaning-selection UX is active. Existing relation enums, verified old/new evidence, final confirmation, immediate pre-mutation revalidation, and canonical mutation stay unchanged.

A broader activity/revert dashboard is **not** opened.

### U3 — Other-project setup simplification — ACTIVE IN #220

Project-folder-first registration and derived display name are active. Registration, workspace access, Query grant, read-only isolation, named-store-only resolution, and no-fallback rules remain separate underneath.

### U4 — AI-assisted answer configuration — ACTIVE IN #220

Meaningful explicit usage presets plus Custom are active. No preset is silently selected. Stored authorization remains the same bounded numeric current-store grant and must pass the existing Query Plane validator.

## NOT EARNED / PARKED

- library-wide ambient/union search;
- sync/Git/cloud replication and automatic remote discovery;
- validated Remote SSH / WSL / Dev Container / Codespaces product boundary;
- multi-writer semantic merge, distributed locks, or automatic conflict resolution;
- Personal/global writable store or cross-project writes;
- portable global identity, automatic person/alias routing, graph/entity/ontology infrastructure;
- vector-default retrieval or background cross-project maintenance;
- broad activity/diff/revert dashboard without installed evidence;
- E024 L1 iterative Librarian;
- G2 Persistence: **NOT_EARNED; parked**;
- G3 Identity / Routing: **NOT_OPENED**;
- paid E023 semantic reruns remain paused absent explicit authorization/evidence.

## VALIDATION GATE FOR 0.1.22

Do not merge/publish #220 merely because the UI looks more useful.

Required:

- Python 3.9 bundled-core compatibility green;
- full Python/core regressions green;
- E020 frozen 78-case authority/product contract remains unchanged except candidate release metadata;
- static boundary checks prove the contextual action does not implement CLI ingest/canonical relation mutation directly;
- normal Extension Host test must execute `Remember in Project Memory` through the actual registered guarded remember operation and observe canonical raw admission;
- F1 named-store safety, Query Plane usage/revocation, Human Knowledge integrity, lineage revalidation and other existing authority gates stay green;
- installable VSIX must contain/load the new product adapter files;
- unpacked packaged VSIX must pass Extension Host execution;
- after merge, `main` must independently repeat the release gate before the release bot publishes immutable 0.1.22 bytes.

E020 remains a deterministic safety/product-contract gate, **not a human product-quality score**.

## FAST POINTERS

- active actionable UX: PR **#220** / `agent/ux-vnext-actionable`
- UX design gate: `docs/product-ux-vnext.md`
- autonomy/UX contract: `docs/12-autonomy-ux-philosophy.md`
- VS Code-first/editor-agnostic core: `decisions/ADR-0002-vscode-first-editor-agnostic-core.md`
- Alpha Core convergence rule: `docs/09-alpha-core-readiness-gate.md`
- U0 implementation: merged PR **#217**
- current published release metadata: `dogfood/releases/README.md`
- installed product guide: `dogfood/vscode/README.md`
- natural installed evidence: #141
- cross-workspace / named-store evidence: #202
- Query Plane: #204
- portability / future remote work: #213
- reliability: #132

## NEXT ACTION

1. Finish **#220 / 0.1.22** validation; fix failures without weakening the authority floor or deleting meaningful gates.
2. Review the final diff for duplicate authority logic and accidental manifest/tool-contract widening.
3. If PR + packaged VSIX gates are green, merge #220 and require a fresh successful `main` VS Code Dogfood run before publication.
4. Publish 0.1.22 only through the existing immutable validated-artifact workflow, then update this handoff to the exact released build/artifact and switch the active track to installed action-oriented UX dogfood.
5. Use installed task completion/friction—not screenshots or synthetic counts—to decide the next UX slice.
