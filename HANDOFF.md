# Current Handoff

Last updated: 2026-08-24 KST

This file is a **living continuation checkpoint**, not project history. Keep current state, authority boundaries, active evidence questions, and next actions only. Historical rationale belongs in merged commits, PRs, ADRs, experiments, or dedicated design documents. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, relevant current design docs, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

### Published baseline

- validated/published dogfood: **0.1.22**
- product merge head: `0e727d77a070c2babdfaaad923be01c8a14c0098`
- published release commit: `d5c4de6ecfd003acf97edd42035a0037d9a3fa4c`
- versioned VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.22.vsix`
- stable convenience path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX bytes: `145985`
- VSIX SHA-256: `54715451477769cfa1aad8ed85c163e6f648bd6ab612ddbb180f62efdc0f6a02`
- validated main build: GitHub Actions `32688939217`
- PR #220: **merged**
- public Beta: **not declared**

The published VSIX is the exact artifact emitted only after the successful `VS Code Dogfood` run on `main`, including unpacked packaged-VSIX Extension Host execution. The versioned 0.1.22 path is immutable under the existing release rule.

### Active product work

The **UX/UI convergence phase** remains active, but implementation is paused at a real installed-evidence boundary: **dogfood 0.1.22 before opening another broad UX slice**.

0.1.21 established product orientation but was visibly insufficient: an Activity Bar icon plus a few state rows did not materially simplify the user's work. That installed evidence activated the action-oriented changes now shipped in 0.1.22.

0.1.22 is the first release that should be judged for task-level UX improvement rather than merely “can I find LLM Wiki?”

Shipped interaction changes:

- Overview leads with **Ask Agent with project memory**, **Remember active file**, and **Review saved-file changes**;
- Explorer/editor context menu exposes **Remember in Project Memory**;
- contextual Remember reuses the registered guarded `llmWiki_rememberSource` tool rather than a parallel ingest path;
- changed remembered files can be reviewed through plain-language meanings that map to the existing canonical lineage relations;
- Other Project Memories is project-folder-first: choose project -> detect `.wiki-lab` -> derive name -> read-only registration -> optional workspace access;
- aliases are no longer mandatory in the primary other-project flow;
- AI-assisted memory answers expose explicit **Light / Regular / Frequent / Custom** choices instead of unexplained bare-number setup; no preset is silently selected;
- ordinary questions remain Agent-first;
- no Webview/dashboard, no core schema migration, no retrieval/model/federation widening.

Design gate: `docs/product-ux-vnext.md`.

## PRODUCT / UX TARGET

Optimize for user goals/actions while keeping the authority model inspectable but mostly behind the adapter layer.

A normal user should be able to:

1. see whether project memory is ready;
2. ask Agent normally without learning LLM Wiki tool names;
3. remember the file they are looking at from the file/sidebar context;
4. understand that a changed remembered file needs judgment and describe what the change **means** without learning enum names;
5. add another project's memory by choosing the project, not an implementation directory;
6. understand/enable optional AI behavior without inventing numeric policy from scratch;
7. recover through a clear next action, with technical diagnostics available only when needed.

Default UI language should prefer `Project memory`, `Remember`, `Review saved-file changes`, `AI summaries`, `AI-assisted memory answers`, `Other project memories`, and `Needs attention`.

Technical terms such as RAW/DERIVED enum labels, `current_store`, `library_store`, opaque store IDs, `scope_ref`, authority epochs, experiment tags, and calibration fields remain where actually necessary: tool contracts, provenance, diagnostics, tests, and expert inspection.

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

Adapter UI may sequence or translate existing operations. Do not duplicate epistemic/storage authority into a second implementation merely for convenience.

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

### U0 — Product shell — SHIPPED IN 0.1.21

Earned but insufficient by itself. Persistent orientation/state is useful infrastructure, not the satisfaction-level UX change.

### U1 — Safe action placement — SHIPPED IN 0.1.22

Contextual Remember is implemented through the existing guarded remember tool. Real Extension Host integration executed the command end-to-end and observed canonical raw admission before release.

### U2 — Plain-language pending decision review — BOUNDED SLICE SHIPPED IN 0.1.22

Only the meaning-selection UX is shipped. Existing relation enums, verified old/new evidence, final confirmation, immediate pre-mutation revalidation, and canonical mutation remain unchanged.

A broader activity/diff/revert dashboard is **not earned/opened**.

### U3 — Other-project setup simplification — SHIPPED IN 0.1.22

Project-folder-first registration and derived display name are shipped. Registration, workspace access, Query grant, read-only isolation, named-store-only resolution, and no-fallback rules remain distinct underneath.

### U4 — AI-assisted answer configuration — BOUNDED SLICE SHIPPED IN 0.1.22

Meaningful explicit usage presets plus Custom are shipped. No preset is silently selected. Stored authorization remains a bounded numeric current-store grant and is accepted only when it passes the existing Query Plane validator.

## 0.1.22 INSTALLED DOGFOOD QUESTIONS

Do not ask whether the sidebar “looks better.” Observe task completion and friction.

Highest-priority checks:

- Can a user looking at a file discover **Remember in Project Memory** without instruction?
- Does contextual Remember feel like one coherent confirmation, or does invoking the Language Model Tool API create redundant/generic confirmation before the product-owned source-admission confirmation? If duplicate confirmation appears in real installed use, refactor Agent Tool + UI to a shared guarded extension operation rather than weakening/removing the product confirmation.
- After changing a remembered file, does **Review saved-file changes** make the old/new meaning decision understandable without exposing `correction/change/dispute/supersede/independent` as required vocabulary?
- Before modifying the lineage-review UX again, add an Extension Host product-flow test that drives the Review command through a real pending decision; current release verification combines product-action static checks with the already-strong existing lineage tool/core verification.
- Can another project be added by selecting its project root without needing to know `.wiki-lab`, store IDs, or aliases?
- Is the distinction between “project added”, “workspace may use added projects”, and “AI-assisted answers enabled” understandable without forcing the user to learn the internal grant model?
- Do Light / Regular / Frequent / Custom make AI-assisted memory-answer limits understandable enough, or do users still need cost/usage context?
- Does the legacy status-bar click -> Doctor behavior still teach a diagnostic-first mental model now that the actionable Overview exists? Change it only if installed evidence confirms the inconsistency is noticeable.
- Do users naturally return to Agent Chat for ordinary work rather than operate LLM Wiki as a separate database application?

## RELEASE / VALIDATION EVIDENCE

0.1.22 release gate is complete:

- PR #220 final head passed VS Code Dogfood plus E004/E010/E014/E023/E026 validation;
- contextual Remember is statically forbidden from direct CLI ingest/canonical lineage mutation and must reuse registered guarded tools;
- normal Extension Host integration executed the contextual Remember command through the actual registered tool and verified canonical RAW admission;
- Python 3.9 bundled-core and full Python/core regressions remained green;
- E020 frozen 78-case contract remained unchanged except release metadata;
- `main` product head `0e727d77a070c2babdfaaad923be01c8a14c0098` passed fresh `VS Code Dogfood` run `32688939217`;
- that main run completed VSIX packaging and unpacked packaged-VSIX Extension Host execution before artifact publication;
- release bot published exact versioned/latest bytes at `d5c4de6ecfd003acf97edd42035a0037d9a3fa4c`;
- release validation itself required no model calls.

E020 remains a deterministic safety/product-contract gate, **not a human product-quality score**.

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

## FAST POINTERS

- current release metadata: `dogfood/releases/README.md`
- action-oriented UX implementation: merged PR **#220**
- U0 product shell: merged PR **#217**
- UX design gate: `docs/product-ux-vnext.md`
- autonomy/UX contract: `docs/12-autonomy-ux-philosophy.md`
- VS Code-first/editor-agnostic core: `decisions/ADR-0002-vscode-first-editor-agnostic-core.md`
- Alpha Core convergence rule: `docs/09-alpha-core-readiness-gate.md`
- installed product guide: `dogfood/vscode/README.md`
- natural installed evidence: #141
- cross-workspace / named-store evidence: #202
- Query Plane: #204
- portability / future remote work: #213
- reliability: #132

## NEXT ACTION

1. **Install and dogfood 0.1.22 now**, specifically through the task flows above.
2. Treat redundant confirmation, confusing lineage wording, other-project setup confusion, or AI-limit confusion as product-adapter evidence first; do not reopen the Authority Core by default.
3. Add a real pending-lineage Review-command Extension Host flow test before the next change that touches that interaction.
4. Open the next UX slice only from installed evidence; do not mechanically continue a roadmap because 0.1.22 shipped.
5. Keep broader core/retrieval/sync/reliability work parked unless independent evidence activates it.
