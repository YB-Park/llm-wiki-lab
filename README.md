# LLM Wiki Lab

A research-first lab for designing a trustworthy personal LLM Wiki.

This repository is intentionally **not** the personal wiki itself. It is the place where we investigate, test, document, and justify the architecture and operating policies that a future personal LLM Wiki will use.

## Why this exists

An LLM Wiki looks deceptively simple: collect sources, let an LLM synthesize them into documents, and retrieve those documents later.

The hard problem is everything that follows:

- What deserves to become durable knowledge?
- What is the right unit of knowledge?
- How should documents be classified, split, merged, or renamed?
- How should contradictions and temporal changes be represented?
- How do we prevent LLM-generated text from recursively contaminating the knowledge base?
- When should information be updated, superseded, archived, or deleted?
- How should provenance be preserved?
- How should retrieval traverse summaries, detail, and primary sources?
- How do we know the system is actually getting better rather than merely getting larger?

We will treat these as research and systems-engineering problems rather than prompt-writing problems.

## Core principle

> Do not promote an attractive idea into a permanent policy before we can explain its failure modes and, where practical, test it.

The working progression is:

```text
question
  -> hypothesis
  -> prior art / evidence
  -> experiment
  -> decision (ADR)
  -> implementation
  -> observation
  -> revision
```

## Repository map

- [`docs/00-project-charter.md`](docs/00-project-charter.md) — mission, scope, risks, success criteria
- [`docs/01-research-map.md`](docs/01-research-map.md) — research landscape and comparison framework
- [`docs/02-design-questions.md`](docs/02-design-questions.md) — open design-question register
- [`docs/03-experiment-plan.md`](docs/03-experiment-plan.md) — experimental program and metrics
- [`docs/04-operating-model.md`](docs/04-operating-model.md) — how this lab itself will be run
- [`research/`](research/) — notes on papers, implementations, and adjacent systems
- [`experiments/`](experiments/) — reproducible experiments and results
- [`decisions/`](decisions/) — Architecture Decision Records (ADRs)

## Current phase

**Phase 0 — Problem framing and research design**

We are deliberately postponing the production wiki schema, Copilot prompts, retrieval stack, and automation until the major design questions have been mapped and the first baseline experiments are defined.

## Near-term milestones

1. Build a landscape of real LLM Wiki implementations and relevant adjacent systems.
2. Define failure modes and evaluation criteria before optimizing architecture.
3. Construct a small controlled corpus and benchmark question set.
4. Compare alternative representations, update strategies, and retrieval strategies.
5. Record design choices as ADRs with evidence and explicit reversal conditions.
6. Only then build the first VS Code + GitHub Copilot prototype.

## Status labels used in documents

- **Fact** — supported by a cited source or direct observation.
- **Hypothesis** — plausible but unverified.
- **Decision** — explicitly adopted in an ADR.
- **Experiment result** — produced by a reproducible experiment in this repository.
- **Open question** — unresolved and should not silently become policy.

The distinction is important: LLM-generated prose is not automatically evidence.
