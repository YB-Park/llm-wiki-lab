# VS Code Release UX Audit

Status: release-readiness baseline after Dogfood 0.1.15  
Tracking: Issue #158  
Natural installed evidence: Issue #141

## Product experience north star

A normal user should understand LLM Wiki as **project memory for their coding Agent that they control**.

The intended loop is:

1. Install LLM Wiki.
2. Explicitly enable project memory for one trusted workspace.
3. Keep using normal Agent conversation.
4. Search/read happens quietly when useful.
5. Creating durable knowledge or changing what saved history means remains explicit.
6. Optional AI summaries are a separate outbound-data grant and are off by default.

Users should not have to learn `RAW_MEMORY`, `DERIVED_MEMORY`, topic IDs, source IDs, tool names, `compiled_provider`, E-series experiments, or the maintenance implementation in order to use the product successfully. Those concepts can remain in diagnostics, protocol contracts, and advanced documentation where they protect correctness.

## Release review by journey

### Install / first open — needs redesign

Current dogfood assumes the README and Command Palette will teach the product. That is not sufficient for a public VS Code extension.

Release direction:

- use one native VS Code Walkthrough that opens on install;
- explain local-first memory and the workspace opt-in boundary first;
- make AI summaries clearly optional;
- finish by returning the user to normal Agent chat;
- do not build a custom onboarding webview or setup dashboard.

### Workspace setup — conceptually strong, copy/actionability weak

The explicit workspace boundary is a product strength and remains unchanged. The current setup errors are too implementation-oriented.

A setup failure must answer:

1. What is blocking setup?
2. Is existing memory safe?
3. What should the user do next?

Important examples:

- Git privacy: explain that the private memory directory could be committed, then give the local-only `.git/info/exclude` and project-wide `.gitignore` choices.
- Python: say which executable was checked and provide a direct Settings action.
- Damaged/incomplete store: never overwrite history; direct the user to Setup & Health / restore guidance.

### First successful use — reduce ceremony

Routine success notifications do not teach anything after the first use. A completed command, chat tool result, updated contextual status, or opened document is usually sufficient feedback.

Do not show routine success toasts for:

- selecting an internal filing topic;
- ordinary source ingestion;
- successful project-memory setup;
- opening a Human Knowledge draft;
- ordinary enable/disable completion after the user already confirmed the action.

### Everyday use — Agent chat stays primary

Normal users should not operate LLM Wiki as a database.

The Agent may search and read saved memory naturally. The extension's public Command Palette is for lifecycle/configuration, not the daily memory loop.

### Consent / confirmation — keep only authority boundaries

Modal dialogs block the editor and must be rare. Every remaining modal needs a documented reason.

| Situation | Release treatment | Why |
|---|---|---|
| Enable project memory for a workspace | Modal | Explicit workspace permission boundary |
| Disable project memory | Modal | Changes Agent availability, while preserving data |
| Save a file as durable project evidence | Modal for now | Durable admission authority; revisit only with natural evidence |
| Save confirmed Human Knowledge | Modal | User authorship/epistemic commitment |
| Resolve correction/change/dispute/supersession meaning | Modal | Changes canonical interpretation of history |
| Enable AI summaries | Modal | Standing outbound-data/model-use permission |
| Daily AI-summary soft guard | Modal for now | Spend/continuation checkpoint; provisional dogfood UX |
| Doctor / Setup & Health result | No modal | Diagnostic output requires no immediate decision |
| Routine success | No modal | Does not require attention |
| Recoverable error | Notification with action | User needs a next step, not a blocking dialog |

The file-admission confirmation is intentionally **not** removed in this audit. A future P2 experiment may test whether an explicit chat request such as “remember this file” can safely serve as the admission confirmation, or whether a remembered workspace consent is understandable. That decision requires natural usage evidence because it changes an authority boundary.

### Errors and recovery — release blocking

An error is not useful merely because it contains a traceback.

LLM Wiki needs two bounded representations of the same failure:

#### Human result

- one short explanation in user language;
- what was preserved or changed;
- a concrete next action when known;
- `Show Details` / Setup & Health for safe diagnostic context;
- no arbitrary stderr, prompt, source text, secret, or local path in the notification.

#### Agent result

Stable machine-readable fields when applicable:

- `status`
- `failure_code`
- `stage`
- `state_changed=yes|no|partial`
- `model_call_attempted=yes|no|unknown`
- `retryable=yes|no|unknown`
- `recommended_action=<bounded enum/string>`

The Agent must not receive arbitrary stderr and then invent a diagnosis. Natural P7 already produced two examples of this defect class: a Copilot CLI compatibility error and a source-size preflight error were both misdiagnosed because causal detail was not available at the Agent boundary.

### Diagnostics — rename and restructure

`Doctor` is a useful engineering term but not the best primary release command. The public command should be **Check Setup and Health**.

The diagnostic contract remains strict:

- 0 model calls;
- 0 state changes;
- no repair;
- no initialization;
- no evidence/prompt/source contents.

The first section should be user-oriented:

- Project memory: ON / OFF / NOT SET UP
- Local memory store: READY / NEEDS ATTENTION
- Python runtime: FOUND / MISSING
- Git privacy: PASS / NEEDS ATTENTION
- Local data integrity: PASS / NEEDS ATTENTION
- AI summaries: ON / OFF
- Copilot CLI executable: FOUND / NOT FOUND
- AI-summary model-call readiness: NOT VERIFIED by zero-model diagnostic
- Next action

Technical details can follow below. `compiled_provider=disabled` belongs only there and must be labeled expected / unrelated to AI summaries.

### Command Palette — reduce the public surface

Dogfood exposes 18 commands, many of which are test/advanced/manual-authority surfaces. A release user should see a small lifecycle surface:

1. **Set Up Project Memory**
2. **Check Setup and Health**
3. **Configure AI Summaries**
4. **Disable for This Workspace**

Advanced commands remain registered for tests, explicit workflows, and future contextual UI, but should not make the default Command Palette look like an internal console.

### Status bar — show user state, not filing internals

The current selected topic is an internal organization concept. It should not be the primary persistent status.

If the status item remains, it should be short and workspace-level:

- `LLM Wiki` when project memory is enabled;
- click -> Setup & Health;
- tooltip explains that project memory is on;
- warning/error emphasis only for truly blocking states.

A permanent Tree View or Activity Bar container is not justified yet. Add one only if natural dogfood repeatedly shows a navigation need that normal Agent conversation and native VS Code surfaces cannot solve.

## User language dictionary

Use these translations in normal UI:

| Internal / engineering term | Normal user UI |
|---|---|
| Agent Wiki maintenance | AI summaries |
| Agent Wiki note | AI summary |
| RAW_MEMORY | saved project evidence / saved source |
| DERIVED_MEMORY | AI summary |
| HUMAN_KNOWLEDGE | your confirmed project knowledge / decision |
| Initialize Workspace | Set Up Project Memory |
| Doctor | Check Setup and Health |
| workspace opt-in | project memory on/off for this workspace |
| topic | hide unless the user explicitly manages filing |
| source ID / object ID | hide unless provenance/advanced diagnostics needs it |
| compiled provider | technical diagnostics only |
| LM spike / E013 / calibration experiment names | advanced/development UI only |

Do not weaken internal protocol terminology where precise labels are needed for the Agent's authority contract.

## AI summaries / Copilot setup

Local project memory must remain useful without Copilot CLI.

The UI should distinguish:

1. **Local memory readiness** — Python + local store + Git privacy + integrity + workspace opt-in.
2. **Copilot CLI executable presence** — a zero-model capability check.
3. **Authentication / organization policy / model-call readiness** — not proven merely by `copilot --version`.
4. **AI summaries enabled** — the user's standing outbound-data grant.

The zero-model Setup & Health command must never claim model-call readiness it did not test.

## Release gate

Before calling the VS Code experience release-ready:

- native first-install Walkthrough is packaged and validated;
- a new user can reach local project-memory READY without reading architecture docs;
- optional Copilot setup is clearly optional and independently diagnosable;
- default Command Palette contains only the primary lifecycle/configuration surface;
- normal UI does not leak development vocabulary unnecessarily;
- routine operations do not create repeated success notifications;
- every modal maps to a documented authority/privacy/spend boundary;
- every failure has a bounded human explanation and a causal Agent result where Agent recovery matters;
- arbitrary stderr/source/local secrets do not flow to Agent or notifications;
- Setup & Health distinguishes executable presence from model-call readiness and remains zero-model / zero-state-change;
- status bar, if present, reflects workspace memory state rather than selected filing topic;
- RAW / DERIVED / HUMAN_KNOWLEDGE authority semantics and explicit workspace opt-in remain unchanged.

## Evidence-dependent follow-ups (do not guess yet)

Natural multi-session dogfood should decide:

- whether explicit chat intent can replace the second source-admission modal;
- whether a workspace-scoped remembered source-admission choice is understandable and safe;
- whether the daily AI-summary soft guard is useful, annoying, or unnecessary;
- whether token / premium-request / AI-credit usage can be surfaced accurately enough to improve trust;
- whether users ever need a dedicated history/navigation View.

## 0.1.16 P1/P2 release decisions

- Native VS Code Issue Reporter integration is included through `issue/reporter`; only bounded environment/readiness metadata is attached, never project evidence, prompts, source text, local paths, usernames, hostnames, or environment variables.
- New source bytes still require the product-owned source-admission confirmation. Explicit Agent chat intent alone is not treated as sufficient authority for a new durable evidence mutation in 0.1.16.
- Repeating an explicit remember request for the exact same current workspace file bytes is a no-op reuse: no new RAW admission, no canonical history append, and no second source-admission modal. Optional AI-summary reuse/maintenance still follows the existing workspace grant and spend guard.
- The daily AI-summary guard remains a soft guard. Users can choose `Continue Today` or `Pause AI Summaries Today`; an explicit pause is remembered only for that local day/threshold and does not alter Wiki knowledge.
- No dedicated Tree/View is added for 0.1.16. Normal Agent conversation remains primary; a permanent navigation UI remains evidence-gated.
- No separate global progress notification is added. Agent tool invocations already have contextual progress, and setup is kept synchronous/short; a new progress surface should require measured latency evidence.
