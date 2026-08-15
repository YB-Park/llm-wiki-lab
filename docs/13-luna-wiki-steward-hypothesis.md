# Luna Wiki Steward — working control-plane hypothesis

Status: **working hypothesis, not an accepted ADR and not an implementation decision**  
Date: 2026-08-15 KST  
Tracking: Issue #110

## Why this hypothesis exists

Real installed-use discussion exposed a stronger requirement than simply making Wiki tools available to the user's main LLM:

> Wiki-relevant judgment may need to happen *inside the user's normal LLM loop*, and that judgment should be controlled by the LLM Wiki product rather than delegated to whichever main model the user happened to select.

If the main model alone decides whether to consult, remember, rewrite, or escalate Wiki state, memory behavior changes with model/provider/prompt and the product cannot reliably enforce its own autonomy contract.

The candidate response is a dedicated **Wiki Steward**: a product-controlled model/agent role, initially pinned to `gpt-5.6-luna`, that governs Wiki memory decisions while the user's chosen main model remains responsible for the user's actual coding/research answer.

This is not a conclusion that Luna must permanently be the model. The architectural hypothesis is **separate memory governance from the main answering model**. Luna is the current concrete candidate because it is cheap, fast, available in Copilot, and already validated in this project.

## Current official Luna cost fact

As of 2026-08-15, GitHub's official Copilot pricing page lists GPT-5.6 Luna (default context, <=200K input tokens) at:

- input: **$0.20 / 1M tokens**;
- cached input: **$0.02 / 1M tokens**;
- cache write: **$0.25 / 1M tokens**;
- output: **$1.20 / 1M tokens**.

GitHub classifies Luna as a lightweight model for quick, cost-efficient smaller/repetitive tasks.

Do not reinterpret `$0.20` as a flat per-call price. The product-relevant point is that a deliberately small, structured policy call can be cheap enough to consider on ordinary interaction paths. Keep the controller context small; do not feed it the whole repository or long conversation merely because Luna supports long context.

Pricing is mutable external product data. Re-verify before release decisions, but keep this 2026-08-15 fact in the design record because it materially motivated the hypothesis.

## Key distinction: main model vs memory governor

Candidate roles:

### Main LLM

- whatever model the user chooses for the actual task;
- writes the user-facing answer/code;
- may use Wiki context supplied through the governed path;
- should not receive unrestricted canonical memory-mutation authority;
- should not be trusted to remember to invoke Wiki tools merely because prompts ask it to.

### Wiki Steward

- product-selected and policy-versioned;
- sees only the minimum prompt/candidate/state required for memory judgment;
- emits structured, auditable decisions;
- can run a maintenance loop when derived Wiki work is actually needed;
- has capabilities constrained by code, not only by prompt text;
- cannot silently promote generated text into raw evidence or human belief.

The product invariant is:

> **The user's main LLM may change. The Wiki's memory policy should remain stable, testable, and owned by LLM Wiki.**

## Do not make Luna a single yes/no gate

A naive design would ask Luna on each turn: `Should I search the Wiki? yes/no`.

That is dangerous because a single model false negative can hide memory that actually exists.

The existing deterministic local retrieval core is cheap, private, and inspectable. Prefer a recall-first pipeline:

1. user submits a prompt;
2. local deterministic discovery/search produces bounded candidate memory, or determines that no candidate exists;
3. Wiki Steward judges the **meaning and action** around those candidates;
4. only the selected/provenance-preserving context is exposed to the main LLM;
5. deterministic capability enforcement executes any allowed memory action.

Therefore Luna is not the search engine. It is the **memory policy / interpretation layer** above deterministic candidate generation.

This also means not every user turn necessarily needs a paid call. If there is no Wiki state, no candidate, no explicit memory intent, and no relevant lifecycle event, deterministic code may skip the Steward. The important requirement is that every *ambiguous Wiki-relevant decision* passes through the governed policy path rather than being left to the main model's whim.

## Two Luna roles, not one giant agent

The same model can serve two different execution shapes.

### A. Turn Policy Judge — small structured call

Purpose: answer narrow questions such as:

- Are these retrieved candidates relevant to the current user intent?
- Is the user explicitly asking to remember something?
- Is this an explicit human commitment or only an inferred belief?
- Is this ordinary derived maintenance, a possible conflict, or no-op?
- Which bounded Wiki context should the main model receive?

Expected output should be typed and small, for example conceptually:

```json
{
  "read": ["candidate-1", "candidate-3"],
  "intent": "query|remember_source|explicit_human_commitment|maintenance|possible_conflict|none",
  "action": "inject_context|enqueue_derived_maintenance|create_authorized_human_note|raise_pending_decision|none",
  "confidence": "high|medium|low"
}
```

This phase should ideally have **no general-purpose mutation tools**. It classifies and plans; deterministic code validates the output.

### B. Derived Wiki Maintenance Agent — tool-using loop only when needed

Triggered after an admitted source, an explicit authorized human-memory event, or another allowed maintenance event.

It may:

- read admitted evidence;
- read existing Agent Wiki pages;
- create/update derived pages;
- add links;
- surface tensions;
- produce provenance-linked diffs.

Its write capability is limited to the **derived Agent Wiki** and explicitly authorized human-note path. Canonical correction/change/dispute/destructive operations remain outside this capability set unless a human-approved deterministic operation is invoked.

This separation keeps ordinary turn decisions cheap and makes tool-using autonomy occur only when the product gets real value from it.

## Candidate per-turn control flow

```text
User prompt
    |
    v
Local deterministic candidate discovery
    |
    v
Luna Turn Policy Judge  <--- LLM Wiki-owned policy/prompt/schema
    |
    +--> bounded Wiki context --------------------+
    |                                             |
    +--> memory intent / pending action            v
                                            User-selected Main LLM
                                                    |
                                                    v
                                               User answer
                                                    |
                                                    v
                                   Post-turn/event memory handling
                                                    |
                             +----------------------+------------------+
                             |                      |                  |
                           no-op            Luna maintenance     Pending human
                                                 agent             decision
                             |                      |                  |
                             +----------------------+------------------+
                                                    |
                                                    v
                                    Derived Agent Wiki / audited state
```

The exact pre/post-turn integration mechanism is still open.

## Why tool-only integration may be insufficient

VS Code Language Model Tools and MCP tools can be invoked automatically by the main agent, but in the normal tool model **the main model decides which tool to call**.

That is useful for capabilities, but it may not satisfy the stronger product requirement:

> a Wiki-policy judgment must occur even when the main model would not independently choose to invoke a Wiki tool.

Therefore transport evaluation must ask not only `Can the main model call Wiki?`, but:

> **Can LLM Wiki enforce a product-controlled memory-policy phase independently of main-model discretion?**

Current VS Code also exposes agent lifecycle hooks (`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, etc.) that execute deterministic code at specific points, custom agents/subagents with model selection, Chat Participants that own the end-to-end interaction, and direct Language Model API calls. These make the stronger design technically plausible, but none is accepted yet.

Hooks are currently Preview and the documented `UserPromptSubmit` output does not itself provide the same arbitrary per-prompt context-injection surface as `SessionStart`/tool hooks. Do not prematurely declare hooks the final solution.

Candidate harnesses to evaluate later:

- a top-level LLM Wiki custom agent plus hidden Luna Steward subagent and enforcement/audit hooks;
- a Chat Participant or extension-owned orchestrator that directly performs Steward -> main-model sequencing;
- a hybrid where hooks enforce lifecycle policy while extension/MCP tools provide Wiki reads and maintenance capabilities;
- eventually an MCP/portable surface for non-VS-Code agents, while preserving the same core policy protocol.

## Capability architecture matters more than prompt wording

The Steward is still an LLM and can be wrong. The core must constrain what a wrong judgment can do.

Candidate hard boundaries:

- local deterministic retrieval can return candidates, but does not grant write authority;
- Turn Policy Judge outputs only validated typed decisions;
- main model has read-oriented Wiki capabilities by default;
- derived maintenance agent can write only derived/rebuildable Agent Wiki artifacts;
- explicit user `remember` intent may authorize source admission or a human-authored commitment, but the executor records the user-authorship boundary;
- inferred human belief is proposal-only;
- canonical correction/change/dispute/supersession is proposal-only until human arbitration;
- raw/provenance/history deletion is never model-auto-approved;
- model answers never become raw evidence merely because another model later cited them;
- activity/provenance/cost/model/policy-version metadata remain inspectable.

This is **capability security for epistemic state**: prompts guide behavior; code determines what actions are possible.

## Explicit user intent outranks model preference

The Steward should not become a bureaucrat that vetoes clear user intent.

Examples:

- `Remember this file.` -> the user has decided admission. Steward may classify/file/compile; it should not independently decide the file is unworthy of memory.
- `Remember that we decided X because Y.` -> direct user authorship/intent is present. The system may persist a human-owned commitment without a redundant second confirmation, while preserving the user's actual statement and provenance.
- inferred `The user probably believes X.` -> no direct authorship; proposal only.

The model governs ambiguous memory mechanics and meaning. It does not supersede explicit human authority.

## Query write-back must avoid self-contamination

A useful query may create reusable synthesis. The Steward may decide that the Agent Wiki should be updated, but the maintenance agent must synthesize from **underlying admitted evidence / explicit human statements**, not from the main model answer as if that answer were evidence.

The main answer can be a *signal that a synthesis is useful*. It is not the source of truth.

This rule prevents recursive model-on-model contamination while still allowing knowledge to compound through use.

## Privacy, latency, and cost are first-class constraints

A dedicated Steward means some user prompts and Wiki snippets may be sent to Luna in addition to the main model. That is a second model exposure and must be covered by explicit standing workspace/session permission.

The product should make the scope legible:

- `Wiki memory: on/off`;
- model used for Wiki policy (`gpt-5.6-luna` initially);
- which workspace/source classes are eligible;
- daily/session maintenance budget;
- compact usage/activity view.

Latency should be measured because a pre-response policy call can affect every useful turn. Keep policy inputs bounded and structured. Run local retrieval in parallel where possible. Skip the model call when deterministic state proves there is no Wiki-relevant decision.

Do not optimize away the Steward before testing its value, but do not assume cheap tokens make added latency/free external exposure irrelevant.

## Failure modes to test before committing

1. **False negative memory use** — relevant Wiki exists but Steward withholds it.
2. **False positive memory use** — irrelevant/stale memory pollutes main-model context.
3. **Unauthorized persistence** — inferred human belief is stored as a human commitment.
4. **Epistemic overreach** — Steward silently labels correction/change/dispute.
5. **Recursive contamination** — generated answers become evidence for later generated answers.
6. **Main-model bypass** — user-selected agent writes Wiki state outside the governed capability path.
7. **Prompt injection through evidence** — admitted source text manipulates Steward policy/tool behavior.
8. **Controller drift** — Luna/model updates change memory decisions; version prompts and keep regression fixtures.
9. **Latency tax** — the system becomes annoying despite cheap tokens.
10. **Surprise spend/exposure** — background or per-turn calls exceed the user's standing grant.
11. **Controller outage** — Wiki becomes unusable if Luna is unavailable; define fail-open/read-only vs fail-closed/write behavior separately.

A likely safe degradation rule is:

- **reads/query:** fall back to deterministic local Wiki retrieval with clear degraded-mode labeling if Steward is unavailable;
- **writes/epistemic actions:** fail closed or queue, because missing policy judgment should not create persistent state.

This is a hypothesis and should be tested.

## What would make this architecture worth it?

The separate Steward earns its complexity only if it produces a better user experience than simply telling the main agent to use Wiki tools:

- memory use becomes consistent across different main models;
- users stop manually remembering when/how to invoke Wiki;
- relevant past knowledge appears without approval storms;
- human commitments and canonical semantics remain protected;
- model/cost behavior stays predictable enough for ambient use;
- the policy can be regression-tested independently from answer quality.

If those benefits do not appear, remove the extra model layer rather than defending it architecturally.

## Immediate design consequence

Do **not** implement `wiki_search` MCP/tool first and call agent integration solved.

Before implementation, define one smallest controlled experiment comparing:

- **main-model-discretion baseline:** main agent is merely given Wiki tools/instructions;
- **dedicated Steward candidate:** deterministic local candidate retrieval + Luna policy judgment + constrained execution.

Use realistic multi-turn prompts where memory should be used, should not be used, explicit `remember` intent appears, inferred beliefs appear, and conflicts occur.

Measure at minimum:

- relevant-memory recall / false negatives;
- irrelevant-memory injection;
- correct autonomy class;
- protected-operation violations;
- added latency;
- actual tokens / AI-credit cost;
- whether behavior remains stable across two or more different main models.

This experiment can decide whether the extra Steward layer is real product value rather than attractive architecture.