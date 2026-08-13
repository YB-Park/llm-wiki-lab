# Research Axis: IDE Integration and Automation Boundary

## Status

**Partially activated after E007.**

The full IDE/workflow question remains future research, but the narrower **canonical mutation authority** sub-axis is now active through E009A.

This document exists so that architecture work does not accidentally harden around an implicit automation philosophy before we study it deliberately.

## Why activation changed

E007 produced direct evidence that the automation boundary is no longer merely a UX concern:

- some answer failures occurred while canonical state remained correct enough;
- some provenance failures were genuine state-level maintenance loss;
- repaired transitions were sometimes committed while the verifier still returned `revise`;
- a measurement-suspect behavioral probe could trigger canonical state mutation;
- recursive rewrite/repair paths could produce large state growth and operational complexity.

Therefore the immediate research question is now:

> What evidence is sufficient to authorize a canonical knowledge mutation, and when should the system instead quarantine, retain prior state, or escalate to review?

This narrower question is tested in `experiments/E009-canonical-commit-boundary/`.

The broader IDE integration surface, background scheduling, prompt-command UX, and final Copilot workflow remain unfrozen.

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
- Experiment/reporting workflows must not depend on copying large transcripts outward or pushing raw run artifacts directly from the execution environment.
- Raw prompts, responses, telemetry, environment metadata, and sensitive artifacts should remain local.
- Any compact handoff must be transferred only when organizational policy permits it; see `docs/06-security-and-handoff-boundary.md`.
- GPT-5.6 Luna is experimental equipment, not an adopted model policy.

A relevant adjacent design reference is the user's `over-the-luna` project. Principles such as **parallelize thinking; serialize mutation**, bounded evidence-triggered recovery, compact context handoffs, and visible human escalation remain useful hypotheses, not imported policy.

## Integration surface — still reserved

- How should the wiki appear inside an IDE: ordinary files, prompt commands, custom agents, background hooks, MCP/tools, or a hybrid?
- Which interactions should happen automatically from normal work, and which should require an explicit wiki action?
- How much context switching or ceremony is acceptable before users stop maintaining the wiki?

Do not freeze these before core semantics and mutation authority are better understood.

## Automation boundary — active research

Questions now under active study include:

- Which semantic proposals are safe to commit autonomously?
- Which operations should be quarantined or proposed as diffs?
- Which operations need explicit review?
- Should the boundary depend on reversibility, epistemic risk, provenance impact, and destructive scope rather than operation name alone?
- When should the system intentionally do nothing instead of attempting an uncertain update?
- Can a failed query ever authorize canonical repair without separate state-level evidence?

A useful conceptual separation is:

```text
observe / retrieve
      ↓
semantic proposal
      ↓
validation + diagnostics
      ↓
commit decision
   ↙    ↓      ↘
commit quarantine review
```

This is an experimental framing, not adopted architecture.

## Cost and efficiency

- What token/model-call budget is reasonable for ingest, consolidation, retrieval, verification, and maintenance?
- Can wiki maintenance consume more resources than the knowledge is worth?
- Should expensive consolidation happen immediately, opportunistically, periodically, or only when failures justify it?
- What work can be deterministic before invoking an LLM?
- What is the marginal benefit of additional verifier/model work per token/call/latency unit?

Useful metrics include:

- tokens per useful ingest,
- tokens per successful answer,
- maintenance tokens per source over time,
- human review actions per meaningful update,
- avoided rediscovery work,
- correction cost after an autonomous mistake,
- ratio of wiki-maintenance cost to demonstrated downstream value.

## Human control and attention

- What deserves interruption versus silent background preparation?
- Should low-risk proposals be batched into review sessions?
- How should uncertainty be surfaced without approval fatigue?
- Can Git diff/review become the primary human-control surface?
- How do we make autonomous behavior legible enough that the user understands why canonical knowledge changed?

## Working hypothesis — deliberately uncommitted

The optimal system is unlikely to maximize automation.

A stronger candidate objective is:

> **Automate reversible, mechanical, and verifiable work aggressively; separate semantic proposal from canonical mutation authority; escalate operations whose epistemic or destructive risk cannot be verified cheaply.**

This is still a hypothesis. E009A is designed to attack it rather than ratify it.

## Relationship to other research questions

This axis intersects with:

- human review and risk tiers (E009),
- long-horizon contamination (E007),
- consolidation policy (E002),
- provenance (E004),
- temporal semantics (E003),
- VS Code/Copilot usability (E010),
- operational cost evaluation.

## Timing

Canonical mutation authority is active now because E007 made it a blocking trust question.

Full daily IDE workflow, background automation, and UX remain deferred until the core semantic/commit rules survive controlled experiments.
