# LLM Wiki UX vNext — product-shell design gate

Status: **active product/UX implementation gate; core authority unchanged**  
Date: 2026-08-24 KST  
Baseline: published Dogfood **0.1.20** / `main` `22be8db1eb63840f94fb7731b3e7aad8fa47f418`

## Why this exists

Natural installed dogfood is now giving a strong product-level signal: the trustworthy core is substantially ahead of the user experience around it.

This gate deliberately does **not** derive a feature list from individual review wording. Users can reliably tell us whether the experience is satisfying or frustrating, but they should not have to reverse-engineer our authority model or prescribe the product architecture. The job here is to inspect the actual interaction model and remove avoidable cognitive/operational burden while preserving the earned trust boundaries.

The project already anticipated this transition:

- `docs/09-alpha-core-readiness-gate.md` declares the raw-first Alpha Core ready and explicitly keeps final UI/sidebar polish outside the core blocker set.
- `docs/12-autonomy-ux-philosophy.md` says Command Palette operations must not become the primary mental model, automation must remain legible, review must not become an approval storm, and Doctor/expert commands are fallback surfaces.
- `docs/13-luna-wiki-steward-hypothesis.md` keeps ordinary conversation as the primary loop and deterministic capability enforcement as the authority boundary.
- ADR-0002 requires a **VS Code-first product surface over an editor-agnostic core**, not a CLI/database UX exposed through VS Code.

The current extension has the right primary idea — ordinary Agent chat — but too little persistent product surface between the user and the underlying system. State, permission, other-project availability, health, and follow-through are mostly discoverable through commands, modals, README text, or diagnostic Output channels.

## External UX evidence used for this gate

This gate follows current VS Code extension UX guidance rather than inventing a parallel application shell:

- VS Code **Views** guidance recommends Tree Views for structured data, Welcome Views for empty/getting-started states, a minimal number of views, and avoiding custom Webviews unless necessary: <https://code.visualstudio.com/api/ux-guidelines/views>
- **Sidebar** guidance recommends one coherent container when an extension genuinely needs persistent related state and warns against excessive containers/views: <https://code.visualstudio.com/api/ux-guidelines/sidebars>
- **Notifications** guidance says to respect user attention and reserve modal dialogs for immediate user decisions rather than multi-step explanation: <https://code.visualstudio.com/api/ux-guidelines/notifications>
- **Walkthrough** guidance says onboarding should stay short and action-oriented: <https://code.visualstudio.com/api/ux-guidelines/walkthroughs>
- **Context menu** guidance says file actions belong near the file when contextually appropriate: <https://code.visualstudio.com/api/ux-guidelines/context-menus>
- **Webview** guidance explicitly discourages reimplementing native UI or using Webviews for wizards/settings when native surfaces are sufficient: <https://code.visualstudio.com/api/ux-guidelines/webviews>

The consequence is important: UX vNext starts with native VS Code primitives. A custom React/Webview dashboard is **not** the default solution.

## Product diagnosis

The main failure pattern is not “the UI needs prettier styling.” It is a mismatch between two mental models.

### The system model

The implementation correctly distinguishes, among other things:

- workspace opt-in and authority epoch;
- immutable RAW evidence, derived Agent Wiki material, and Human Knowledge;
- current-store Query Reasoning grant;
- Personal Wiki Library registration and separate workspace library grant;
- named-store-only external resolution;
- correction / change / dispute / supersede / independent lineage semantics;
- exact provenance and scope-qualified reads;
- local usage guards and model exposure boundaries.

These distinctions are valuable **inside the trust architecture**.

### The user model we should optimize for

The user has a much smaller set of goals:

1. Is project memory on and healthy here?
2. Can the Agent use what I saved?
3. What optional AI behavior is on?
4. Can this workspace use memory from another project?
5. Did the thing I asked to remember actually become durable memory?
6. Is anything waiting for my judgment?
7. If something is wrong, what is the next safe action?

UX vNext must translate from the first model to the second. We should **not make users learn our internal ontology merely to operate the product**.

## Design principles

### P1. User goals and state first; authority mechanics second

Default UI language should use concepts such as:

- Project memory
- Saved sources
- Your decisions / project knowledge
- AI summaries
- AI-assisted memory answers
- Other project memories
- Needs attention

Terms such as `current_store`, `library_store`, `scope_ref`, authority epoch, RAW/DERIVED enum names, store IDs, and grant fingerprints belong in technical details, model/tool contracts, tests, or diagnostics unless they are genuinely necessary for a user decision.

### P2. Preserve semantic choice, translate the vocabulary

Canonical lineage remains human-gated. The UI should ask what a change **means**, not ask the user to know our enum names.

Candidate wording:

- “The older version was wrong; this fixes it.” -> `correction`
- “The older version was true then; things changed later.” -> `change`
- “Both versions disagree and this is unresolved.” -> `dispute`
- “Use the newer version going forward.” -> `supersede`
- “These are separate pieces of evidence.” -> `independent`

The mapping is a UX responsibility. The core semantics remain unchanged.

### P3. Approve authority, not routine mechanics

Keep confirmation where it protects privacy, authorship, epistemic meaning, destructive state, or model spend. Do not add confirmation merely because an internal subsystem has multiple steps.

Separate grants may remain separate internally even when one user journey explains and sequences them coherently.

### P4. Ambient but inspectable

The primary experience remains ordinary Agent conversation. The product shell exists to answer “what state is this memory system in?” and “what needs my attention?” — not to force users into a separate database application.

### P5. Progressive disclosure

The default surface should show the smallest useful status. Expert/internal details remain available through `Check Setup and Health`, logs, provenance drill-down, and advanced commands.

### P6. Native VS Code before custom UI

Use a single native View container with one Tree View/Welcome View first. Use view title actions and contextual file actions where appropriate. Introduce Webviews only if a later interaction genuinely cannot be expressed accessibly with native controls.

### P7. Research instrumentation never becomes ordinary interaction tax

E013/E020-style tags, score fields, source IDs, experiment labels, and calibration controls may remain available for dogfood instrumentation and diagnostics, but they must not sit in the ordinary user path unless the user explicitly enters an expert/research surface.

## UX vNext information architecture

### Persistent LLM Wiki view

One LLM Wiki View Container in the Activity Bar / Primary Sidebar, with **one** primary view.

Setup/off state uses a concise Welcome View. Enabled state uses a shallow Tree View.

Initial enabled model:

```text
LLM Wiki

Project memory                     On
AI summaries                       Off
AI-assisted memory answers         Off
Other project memories             2 added · Ready
  Project Alpha                    Read only
  Project Beta                     Read only
```

This is intentionally not a dashboard. It is a small, persistent state and navigation surface.

View-title actions should remain sparse:

- Open Agent Chat
- Check Setup and Health
- Refresh

Do not turn tree rows into a button farm.

### Setup / empty state

The first useful product journey should be:

```text
Install extension
  -> Set Up Project Memory
  -> Open Agent Chat
```

AI summaries and other optional features should not appear as required-looking onboarding steps. They remain discoverable after the core loop works.

### Other project memories

Primary flow should ask the user to select a **project**, not an implementation directory.

Preferred flow:

```text
Manage Other Project Memories
  -> Add Project
  -> choose project folder
  -> detect .wiki-lab
  -> derive project name
  -> concise read-only disclosure
  -> register
  -> optionally allow this workspace to use explicitly named other-project memory
```

Selecting `.wiki-lab` directly remains an expert/custom-location fallback, not the primary mental model. Alias entry is advanced and should not be mandatory in the primary flow.

The underlying named-store-only resolution, registration continuity witness, read-only boundary, workspace grant, and no-fallback rules remain unchanged.

### AI-assisted memory answers

The grant remains explicit and revocable. The UI should not require unexplained bare-number entry when a bounded choice can communicate meaning better.

Candidate later slice:

- daily attempts: light / regular / frequent / custom;
- per-answer AI credit guard: bounded choices / custom;
- no default silently selected if the product contract requires the user to choose.

The stored grant remains the same typed numeric policy.

### Changed remembered file

The safe pending-lineage mechanism remains. The future UX should present verified old/new context plus plain-language meanings, then map the chosen meaning to the existing canonical relation.

Do **not** weaken the second verification immediately before mutation.

## First implementation slice — U0 Product Shell

This branch starts with the smallest structural change that can improve orientation without widening authority:

1. add one native `LLM Wiki` Activity Bar container and one Tree View;
2. show setup/off state through Welcome View;
3. show project-memory / optional-AI / other-project state with user-facing vocabulary;
4. show registered other-project names without exposing store IDs or paths;
5. provide sparse view-title actions for Agent Chat, health details, and refresh;
6. reduce first-install Walkthrough to installed -> setup -> Agent Chat;
7. keep all core schemas, canonical semantics, model tools, grant storage, query behavior, and write boundaries unchanged;
8. add static product-contract checks for the new native UI and ensure no Webview is introduced.

### U0 non-goals

U0 does **not** yet:

- change canonical memory semantics;
- auto-admit files;
- add ambient cross-project union search;
- change Query Plane retrieval/composition;
- add a Webview/dashboard;
- display source/Human Knowledge counts by parsing canonical files directly in UI code;
- create a new persistence layer;
- change model or budget policy;
- add a context-menu `Remember` action until it can reuse the same dirty-file and explicit-confirmation contract as `rememberWikiSource` without creating a weaker parallel write path.

The last point is deliberate. Discoverability must not come at the cost of a second, less-safe admission implementation.

## Acceptance criteria for U0

### Orientation

- A user can find a persistent LLM Wiki surface without knowing Command Palette commands.
- Before setup, the view tells the user exactly one primary next action.
- After setup, the user can tell at a glance whether project memory is on.
- Optional AI features are visibly optional state, not setup obligations.
- Registered other-project memories are visible by human-readable project name.

### Cognitive load

- The default Tree View contains no RAW/DERIVED enum names, scope refs, authority epochs, opaque store IDs, absolute paths, or experiment tags.
- No extra confirmation is introduced for read-only inspection.
- The first-install Walkthrough has three steps and does not make AI summaries look like setup work.

### Trust / authority

- Workspace explicit opt-in remains required.
- Model-backed Query Reasoning remains separately granted.
- Other-project registration and workspace access remain separately revocable.
- External stores remain read-only and named-store-only.
- Human Knowledge authorship and canonical lineage remain human-gated.
- Doctor remains zero-model / zero-state-change.
- No core schema migration.

### Platform fit

- Native Tree View + Welcome View; no Webview.
- One View Container and one View only.
- View title actions remain sparse.
- Existing normal Agent chat remains the primary task surface.

## Follow-on slices after U0 earns itself

Do not implement these merely because they are listed here. Re-check the installed U0 experience first.

### U1 — action placement and safe admission

- reuse/extract the existing `rememberWikiSource` admission path into a shared extension-layer operation;
- add `Remember in Project Memory` to appropriate Explorer/editor context menus;
- preserve dirty-editor refusal, explicit admission confirmation, same-file detection, pending-lineage creation, and maintenance behavior;
- show a compact durable-success state without notification spam.

### U2 — pending decisions and activity

- expose pending epistemic decisions in the LLM Wiki view;
- show plain-language relation choices backed by verified old/new excerpts;
- expose recent reversible derived maintenance/activity only if it is useful and bounded;
- keep canonical mutation pre-action and derived work mostly post-hoc/reviewable.

### U3 — other-project memory simplification

- project-folder-first registration;
- automatic human-readable name derivation;
- aliases only when needed/advanced;
- coherent sequencing of registration, workspace access, and AI-assisted-answer prerequisites without merging their underlying authorities.

### U4 — AI-assisted answer configuration

- replace unexplained numeric entry with bounded meaningful choices plus Custom;
- preserve explicit user selection and exact stored caps;
- show current state/usage in product language, with provider/billing caveats in details.

## Evidence gate for resuming broad dogfood

Do not judge UX vNext by whether reviewers like visual styling. Evaluate task-level outcomes:

1. Can a fresh user establish project memory without README/maintainer help?
2. Can they tell whether the system is ready and what optional features are on?
3. Can they return to ordinary Agent chat without believing a separate Wiki app must stay open?
4. Can they understand why an other-project question is unavailable and identify the next action?
5. Can they save a source and later recognize that it is durable memory?
6. When a remembered file changes, can they choose the correct semantic relationship from plain-language meanings without learning internal enum vocabulary?
7. Can they recover from setup/privacy/runtime failure without reading raw diagnostic output first?

Synthetic/static tests remain useful for authority regressions, but these are installed-human interaction questions. E020 itself correctly says its high supported count is not a product-quality score.

## Re-evaluation triggers

Revisit this gate if:

- native Views materially interfere with the intended Agent-first workflow;
- the Tree View cannot express required review/pending-decision interactions accessibly;
- repeated installed evidence shows users do not need or use a persistent memory state surface;
- the product needs a richer editor surface for actual Wiki-page reading/navigation rather than state management;
- implementing UX requires duplicating core epistemic logic in the extension.

If a richer Webview/editor surface is later justified, add it for a concrete unmet interaction — not because a custom dashboard is aesthetically attractive.
