# Lab Operating Model

This document governs how research, decisions, experiments, and implementation changes should move through the repository.

It governs the **lab**, not the future production wiki. Production-wiki behavior must be decided separately through ADRs.

## 1. Artifact types

### Research notes

Location: `research/`

Purpose: record external evidence, implementation observations, paper notes, prior art, and comparisons.

Rules:

- distinguish source claims from our interpretation,
- include links/citations sufficient to re-check important claims,
- record limitations and uncertainty,
- avoid converting one implementation's choice into a universal recommendation.

### Design questions

Location: `docs/02-design-questions.md`

Purpose: canonical register of unresolved architecture/policy questions.

Rules:

- important ambiguity should become an explicit question,
- questions are not resolved by prose consensus,
- resolved questions point to an ADR.

### Experiments

Location: `experiments/`

Purpose: produce reproducible evidence about competing designs.

Rules:

- state hypothesis and protocol before interpreting results,
- preserve raw outputs when feasible,
- record model/tool versions and relevant prompts,
- keep measured result separate from interpretation,
- record failed experiments as well as successful ones.

### Decisions

Location: `decisions/`

Purpose: make policy adoption explicit and reversible.

An ADR must include alternatives, evidence, trade-offs, failure modes, and re-evaluation conditions.

### Implementation

Future location: to be decided.

Implementation should reference the ADRs that justify non-trivial behavior.

## 2. Epistemic discipline

Use these concepts consistently:

- **Fact** — supported by a source or direct measured observation.
- **Observation** — something seen in an experiment or real use; may not generalize.
- **Hypothesis** — proposed explanation or design expectation.
- **Interpretation** — our reasoning about facts/observations.
- **Decision** — an adopted policy recorded in an ADR.
- **Open question** — intentionally unresolved.

A confident LLM sentence does not change epistemic status.

## 3. Change-risk tiers

For the lab repository itself:

### Low risk

- adding research notes,
- adding references,
- recording experiment outputs,
- adding open questions.

These can usually be additive changes.

### Medium risk

- changing experiment protocols after runs exist,
- changing definitions or shared metrics,
- restructuring research taxonomy.

These should include rationale and preserve migration/history.

### High risk

- deleting experiment evidence,
- rewriting historical results,
- changing an ADR without recording supersession,
- removing an important rejected alternative from history.

Prefer superseding artifacts over rewriting history.

## 4. ADR lifecycle

Recommended states:

- Proposed
- Accepted
- Superseded
- Rejected
- Deprecated

A later ADR should supersede an earlier one instead of editing history to make the earlier decision appear different from what it was.

## 5. Experiment lifecycle

1. Question selected.
2. Hypothesis written.
3. Corpus and evaluation criteria frozen enough for comparison.
4. Baseline run.
5. Alternative runs.
6. Deterministic metrics computed.
7. Human/LLM qualitative evaluation where needed.
8. Analysis written.
9. Threats to validity documented.
10. Result either informs an ADR or generates new questions.

Negative or ambiguous results are valid outcomes.

## 6. Research-note template

Each substantial note should answer:

```text
System / paper / practice:
Source:
Date reviewed:

Problem addressed:
Architecture / method:
Evidence / evaluation:
What appears to work:
Known limitations:
Failure modes:
Relevant design questions:
Ideas worth testing:
Our interpretation:
Confidence / open uncertainty:
```

## 7. Decision template

```text
# ADR-XXXX: Title

Status:
Date:

## Context

## Decision drivers

## Alternatives considered

## Evidence

## Decision

## Consequences

### Benefits
### Costs
### Risks / failure modes

## Re-evaluation triggers

## Related experiments / research
```

## 8. Experiment template

```text
# E###: Title

Status:
Question:
Hypothesis:

## Variables
## Corpus
## Protocol
## Metrics
## Expected failure modes
## Runs
## Results
## Interpretation
## Threats to validity
## Follow-up
```

## 9. Git workflow

During the early research phase, small additive research/doc changes may land directly on `main` when appropriate.

As implementation and experiments become consequential, prefer short-lived branches and PRs so that:

- experiment changes are reviewable,
- policy changes are explicit,
- diffs act as a knowledge-maintenance audit trail.

Do not use commit history as the only place where a major decision is explained; use an ADR.

## 10. How Copilot/LLMs should participate

LLMs are useful as:

- research assistants,
- comparison/synthesis tools,
- experimental subjects,
- test-data generators,
- code assistants,
- candidate maintainers.

They must not be treated as:

- self-authenticating sources,
- invisible policy makers,
- justification for deleting provenance,
- substitutes for controlled comparison when a decision is experimentally testable.

## 11. Stop conditions before production prototype

Do not lock in a production schema until we can at least explain our current position on:

- source/derived separation,
- provenance,
- temporal update semantics,
- contradiction semantics,
- knowledge granularity,
- split/merge/rename lifecycle,
- deletion/archival,
- retrieval escalation,
- evaluation methodology,
- human-review boundaries.

We do not need perfect answers, but we need explicit, inspectable answers and known uncertainties.
