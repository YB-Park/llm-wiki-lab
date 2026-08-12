# Future Research Axis: IDE Integration and Automation Boundary

## Status

**Reserved future research topic — not an active implementation decision.**

This document exists so that architecture work does not accidentally harden around an implicit automation philosophy before we study it deliberately.

## Why this matters

The success of a personal LLM Wiki may depend as much on **where we draw the automation boundary** as on knowledge representation or retrieval quality.

A system can fail even with good wiki semantics if it:

- consumes excessive tokens or model calls merely to maintain itself,
- interrupts normal IDE work too often,
- performs high-impact edits without enough human awareness,
- requires so much review that the user bypasses the workflow,
- automates low-value maintenance while leaving high-value judgment to unreliable heuristics,
- or creates a second workflow that competes with the user's actual development environment.

The target environment is currently VS Code + GitHub Copilot, but the questions should remain general enough to compare other IDE/agent environments later.

## Known real-environment constraints

These are deployment inputs, not architecture decisions:

- The intended day-to-day environment is a managed corporate network using VS Code + GitHub Copilot.
- ChatGPT is unavailable from that corporate network.
- Direct GitHub push from that corporate network is unavailable.
- Therefore experiment/reporting workflows must not depend on copying large transcripts to ChatGPT or pushing run artifacts directly from the execution environment.
- A practical experiment harness should be able to emit a **small sanitized handoff summary** that can be manually transferred when necessary; raw prompts, responses, telemetry, and sensitive artifacts should remain local.
- GPT-5.6 Luna is a **candidate**, not an adopted policy, for high-volume wiki maintenance because a lightweight/low-cost model may be sufficient for drafting, organization, consolidation, and routine verification. Actual model choice must be tested for quality and measured using the effective pricing/credit conditions of the real corporate Copilot environment at experiment time.

A relevant adjacent design reference is the user's `over-the-luna` project. Its principles such as **parallelize thinking; serialize mutation**, bounded evidence-triggered recovery, compact context handoffs, and visible human escalation are useful hypotheses for future Wiki automation experiments, but are not imported as policy here.

## Questions to investigate deeply later

### Integration surface

- How should the wiki appear inside an IDE: ordinary files, prompt commands, custom agents, background hooks, MCP/tools, or a hybrid?
- Which interactions should happen automatically from normal work, and which should require an explicit wiki action?
- How much context switching or ceremony is acceptable before users stop maintaining the wiki?

### Automation boundary

- Which operations are safe to perform autonomously?
- Which operations should be proposed as diffs for review?
- Which operations must always require explicit user approval?
- Should the boundary depend on reversibility and epistemic risk rather than operation type alone?
- When should the system intentionally do nothing instead of attempting an uncertain update?

Potential spectrum to test:

```text
observe -> suggest -> draft -> edit -> restructure -> delete
 low autonomy risk                         high autonomy risk
```

Do **not** adopt this spectrum as policy yet; it is only a useful experimental framing.

### Cost and efficiency

- What token/model-call budget is reasonable for ingest, consolidation, retrieval, and maintenance?
- Can wiki maintenance consume more resources than the knowledge is worth?
- Should expensive consolidation happen immediately, opportunistically, periodically, or only when retrieval failures justify it?
- How much derived material should be reread on every operation?
- What work can be handled deterministically with filesystem search, Git, lint, metadata, or local code before invoking an LLM?
- What is the marginal benefit of additional LLM work per token/call/latency unit?

A useful future metric family may include:

- tokens per useful ingest,
- tokens per successful answer,
- maintenance tokens per source over time,
- human review actions per meaningful update,
- avoided rediscovery work,
- correction cost after an autonomous mistake,
- ratio of wiki-maintenance cost to demonstrated downstream value.

### Human control and attention

- What deserves interruption versus silent background preparation?
- Should the system batch low-risk proposals into review sessions?
- How should uncertainty be surfaced without producing approval fatigue?
- Can Git diff/review serve as the primary human-control boundary?
- How do we make autonomous behavior legible enough that the user can understand *why* the wiki changed?

## Working hypothesis — deliberately uncommitted

The optimal system is unlikely to maximize automation.

A better objective may be to **automate reversible, mechanical, and verifiable work aggressively while keeping irreversible, semantic, or epistemically consequential decisions visible to the user**.

This is only a hypothesis. It must be tested against actual workflow friction, error rates, token/model cost, and user behavior before becoming policy.

## Relationship to existing research questions

This topic intersects with:

- human review and risk tiers,
- long-horizon contamination,
- consolidation policy,
- provenance and auditability,
- VS Code/Copilot UX,
- operational cost evaluation.

When this axis becomes active, it should produce dedicated experiments comparing different automation levels under the **same corpus and daily-work scenarios**, rather than being decided from intuition alone.

## Timing

Do not let this topic disrupt the current evidence-landscape phase.

Revisit it once core knowledge semantics are better understood, but **before** we freeze the daily IDE workflow, Copilot instructions, automatic maintenance triggers, or background/agent architecture.
