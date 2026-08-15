# LLM Wiki autonomy and UX philosophy — working product contract

Status: **working design gate, not an accepted ADR and not an implementation choice**  
Date: 2026-08-15 KST  
Tracking: Issue #110

## Why this exists

Installed 0.1.8 dogfood exposed a product-level ambiguity that the trust/retrieval work did not answer:

> What should the LLM do by itself, what should require human intent or approval, and what should never be silently delegated?

The current Alpha proves trustworthy evidence storage, provenance, temporal semantics, deterministic retrieval, and grounded model use. But its command-driven interaction can feel like a human-operated evidence database with an `Ask Luna` button. That is not yet the intended LLM Wiki experience.

This document deliberately precedes MCP, VS Code Language Model Tools, Chat Participants, background workers, or any other transport choice. Platform capabilities are implementation mechanics. The product contract must come first.

## Central thesis

> **The user controls admission and epistemic commitment. The LLM controls compilation and maintenance inside the authority it has been granted.**

Or more concretely:

- The human decides **what deserves to enter memory**.
- The LLM decides **how admitted material is filed, linked, synthesized, retrieved, and maintained**.
- The human decides **what counts as the user's own belief/decision and how conflicting evidence should be interpreted**.
- The LLM may detect, explain, and propose those high-consequence judgments, but should not silently impersonate the human or rewrite source meaning.

This is not “manual versus autonomous.” It is **delegation by class of action**.

## User initiation is not the same as per-step approval

A user may initiate a high-level intent once:

- “Remember this document.”
- “Use my Wiki while we work.”
- “Keep the derived Wiki up to date for this workspace.”
- “Remember that we decided X because Y.”

The product should not then force the user to approve every search, page selection, cross-link, summary rewrite, or derived-page update.

Likewise, true autonomy does not require a daemon that acts without any user relationship. A useful LLM Wiki can be event-driven: after a source is admitted or a user grants a standing scope, the LLM can perform the maintenance loop without micro-management.

The UX goal is:

> **Approve intent and authority, not routine mechanics.**

## Three ownership layers

### 1. Raw evidence and canonical history — human-admitted, trust substrate

Properties:

- immutable raw evidence;
- provenance and revision identity;
- correction / change / dispute semantics;
- fail-closed integrity;
- no silent model-authored reinterpretation of source history.

Default authority:

- **Read:** LLM may read within a granted workspace/session scope.
- **Admission:** human-directed by default. The user chooses a file/source/folder or explicitly says “remember this.”
- **Mechanical ingest after admission:** may be automatic.
- **Correction / change / dispute / destructive deletion:** model may propose; human arbitrates by default.

Why: source admission and semantic history determine what the system is allowed to remember as evidence. They are not mere filing operations.

### 2. Human Knowledge Notes — human-owned commitments

Purpose:

- what I currently believe;
- what I decided;
- why I decided it;
- open questions or hypotheses explicitly owned by the user.

Default authority:

- If the user explicitly says “remember that we decided X because Y,” that high-level instruction can itself be authorization to create/update a human-owned note.
- If the LLM merely **infers** that the user believes or decided something, it should propose a note/edit rather than silently asserting it on the user's behalf.
- The model should not silently overwrite a human note because new evidence appears. It may surface a conflict and propose a revision.

The important boundary is authorship, not file format.

### 3. Agent Wiki — LLM-owned derived knowledge

This is the missing Karpathy-style layer we now need to dogfood.

Properties:

- persistent Markdown or equivalent inspectable artifact;
- created and maintained by the LLM;
- summarizes and links admitted evidence;
- records entities, concepts, relationships, comparisons, unresolved tensions, and reusable synthesis;
- every load-bearing claim remains traceable to canonical evidence;
- changes are diffable/logged;
- the entire layer is **derived, noncanonical, reversible, and rebuildable**.

Default authority:

- after the user grants a maintenance scope and model/budget permission, the LLM should be able to update this layer **without per-page confirmation**;
- a bad Agent Wiki edit must be recoverable by inspecting/reverting/rebuilding from raw evidence and history;
- Agent Wiki text must never silently become raw evidence or a human belief merely because a model wrote it.

This is where meaningful autonomy belongs first.

## Important correction to earlier “compiled Wiki” framing

Two different ideas were partially conflated:

1. **Persistent compiled provider as a trusted/default query substrate.**  
   E013 still governs whether this deserves promotion based on realistic reuse/cost/update evidence.

2. **Persistent Agent Wiki as an LLM-owned derived product artifact.**  
   This is the central product hypothesis of an LLM Wiki and does not need to masquerade as canonical truth or default retrieval infrastructure in order to be dogfooded.

Therefore:

> The E013 gate remains valid for trusted/default compiled-provider promotion, but it must **not** be interpreted as a ban on building and testing a derived, provenance-linked Agent Wiki.

## Autonomy matrix — working default

| Operation | Default autonomy | Why |
|---|---|---|
| Search/read already-admitted Wiki/evidence | Automatic after scoped trust grant | Reversible read; routine agent memory use |
| Choose which retrieved pages/regions to inspect | Automatic | Pure mechanics |
| Create/update cross-links and summaries in Agent Wiki | Automatic after maintenance opt-in | Derived/rebuildable layer is exactly what the LLM owns |
| Recompile Agent Wiki after an explicitly admitted source | Automatic within budget | User already approved admission; filing is agent work |
| Send evidence to an external model | Standing explicit workspace/session permission | Privacy boundary |
| Spend paid model credits | Standing explicit budget/cap, visible usage | Cost boundary; no surprise background spend |
| Admit a new raw source | Human-directed by default | Determines memory boundary/privacy |
| Auto-watch a folder/source class for admission | Explicit standing opt-in | Broader memory/privacy scope |
| Label correction/change/dispute/supersession | Human confirmation by default | Epistemic meaning, not filing |
| Write an explicit user-stated decision to a Human Note | May follow direct user instruction without a second click | User already supplied authorship and intent |
| Infer a user belief/decision and persist it | Proposal only | Avoid impersonating user beliefs |
| Delete raw/provenance/history | Explicit human action | Destructive/irreversible trust loss |
| Delete/rebuild Agent Wiki | May be automated if clearly derived and recoverable | Derived layer, but activity must remain inspectable |

This table is a design hypothesis to test, not a frozen security policy.

## Primary UX philosophy

The intended product should **not** make Command Palette operations the main mental model.

### Primary surface: ordinary agent conversation

The user should be able to talk to their normal coding/research agent:

- “Why did we decide not to promote X1?”
- “What did I learn about forkserver?”
- “Remember this design review.”
- “We decided to keep timeout at 15 seconds because of retry budget.”

The agent should decide when to consult the Wiki and use it as persistent memory within granted permissions.

The user should not need to remember topic names or manually run `Search` before every useful answer.

### Ambient but legible

Automatic does **not** mean invisible.

A good answer should make it obvious, without ceremony, that Wiki memory was used:

- `Used LLM Wiki` indicator;
- navigable citations/provenance;
- optional expansion showing which pages/evidence were read;
- no hidden claim that the model “remembered” something outside inspectable state.

### Review surface, not approval storm

Derived maintenance should produce a compact activity surface:

- “3 Agent Wiki pages updated from source X”;
- diff/revert/source links;
- model/cost metadata when relevant;
- health/integrity state;
- **Pending decisions** for items that require human epistemic judgment.

The review surface is mostly post-hoc for reversible derived work and pre-action for high-consequence semantics.

### Manual commands remain valuable

Commands remain as:

- explicit fallback;
- diagnostics;
- trust-sensitive operations;
- deterministic testing surfaces;
- expert escape hatches.

But a user should not need to think like a storage-engine operator to benefit from the Wiki.

## Candidate end-to-end loops

### A. Source admission and compilation

1. User explicitly chooses a source or says “remember this.”
2. Raw bytes/provenance are captured under existing trust rules.
3. Within granted model/budget scope, the LLM automatically updates affected Agent Wiki pages, links, summaries, and index.
4. Activity view reports what changed and why.
5. If the new source appears to contradict prior evidence, ordinary derived pages may record the tension, but canonical correction/change/dispute waits for human judgment.

### B. Ordinary query

1. User asks their normal agent a question; no special `Ask Wiki` ritual required.
2. Agent autonomously reads/searches Wiki within trust scope.
3. Answer states that Wiki memory was used and provides provenance.
4. If the query produces reusable synthesis, the agent may update Agent Wiki **from the underlying admitted evidence**, not by treating its own answer text as new evidence.

This last invariant is critical to avoid recursive self-contamination.

### C. Human decision

1. User says: “We decided X because Y. Remember that.”
2. This is explicit authorship/intent, so the system may create/update a Human Knowledge Note without a redundant second confirmation.
3. Evidence can be linked automatically.
4. Later contradictory evidence does not silently rewrite the human decision; it surfaces a pending review or suggested revision.

### D. Conflict

1. Agent notices two admitted sources disagree.
2. It may update the **derived Agent Wiki** to say that there is a tension/uncertainty, with citations.
3. It must not silently choose canonical `correction`, `change over time`, or `unresolved dispute` semantics.
4. A compact Pending Decision asks the user only when that semantic distinction matters.

## Permissions should be scoped, not binary

The product should prefer standing grants such as:

- **session:** use Wiki reads automatically in this chat;
- **workspace:** use admitted Wiki evidence with Copilot in this workspace;
- **maintenance:** keep Agent Wiki updated after explicit source admission;
- **source watch:** automatically admit files only from a specifically granted source/folder class;
- **budget:** maximum calls/credits per maintenance event/day/session;
- **never-auto:** canonical epistemic mutation, destructive provenance loss, inferred human belief.

The exact VS Code permission API may not map perfectly to these concepts. If so, our extension must preserve the product contract rather than flattening it into the platform's coarse permission switch.

## What Language Model Tools / MCP do and do not decide

Current VS Code agent tools can be selected automatically from a user's ordinary prompt, and VS Code exposes permission levels from per-tool approvals to high-autonomy modes. That means an agent-facing implementation is feasible.

However:

- Language Model Tool vs MCP is **not yet the design decision**;
- tool auto-approval is not equivalent to our epistemic authority model;
- a platform-wide “Always Allow” may be too broad for some Wiki mutations;
- a background maintenance loop may require a different transport from conversational reads.

Choose transport only after the autonomy contract and minimal product loop are clear.

## UI we should probably build toward, not yet commit to

Likely primary components:

1. **Agent integration** — automatic read/search during normal conversation.
2. **Remember This** — high-level source admission intent, not a multi-command ingest ceremony.
3. **Agent Wiki view** — actual LLM-maintained pages users can read/navigate.
4. **Activity / review** — compact history, diffs, provenance, cost, revert.
5. **Pending decisions** — only high-consequence human judgments.
6. **Human Notes** — explicit user reasoning/decisions, with LLM assistance but protected authorship.
7. **Doctor / expert commands** — operational fallback, not primary product UX.

Do not build all seven at once. The first end-to-end slice should prove the ownership/autonomy contract with the smallest possible surface.

## Smallest representative product slice to design next

Before implementation, specify one loop that feels like the real product:

> User says “remember this source” -> source is admitted -> LLM autonomously updates a small derived Agent Wiki -> later the user asks an ordinary Copilot question -> agent autonomously reads the Wiki and cites it -> any detected epistemic conflict is surfaced as a pending human decision, not silently resolved.

If we cannot make this loop feel coherent, choosing MCP or Language Model Tools will not save the product.

## Open questions

1. What is the default source-admission boundary: explicit item only, selected folder, or configurable source classes?
2. Should derived maintenance happen immediately after explicit ingest, opportunistically during agent sessions, or also via background/event queues?
3. What model/budget policy makes automatic maintenance useful without surprise spend?
4. How do we write query-derived reusable synthesis back without letting generated answers become circular evidence?
5. What is the smallest activity/review UI that provides trust without turning every derived edit into approval fatigue?
6. Which operations must be technically ineligible for auto-approval, not merely discouraged by prompt text?
7. How should a human explicitly delegate more autonomy if they want a closer “LLM owns the Wiki” Karpathy experience?

## Immediate consequence for P7

0.1.8 remains useful for core/runtime dogfood, but **the existing command-driven loop is no longer sufficient evidence for the intended product UX**.

Do not spend weeks evaluating whether users enjoy manually operating `Create Topic -> Ingest -> Search -> Ask Luna` as if that were the final LLM Wiki.

Before representative long-run P7, settle this contract and implement the smallest agent-maintained Wiki loop. Then dogfood the real thing.