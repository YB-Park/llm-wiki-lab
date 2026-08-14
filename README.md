# LLM Wiki Lab

A research-first lab for building and validating a trustworthy personal LLM Wiki.

The product target is a **VS Code-first LLM Wiki**. This repository contains the research, experiments, decisions, core implementation, and dogfood surfaces used to get there; it is not the user's personal wiki data.

For the latest continuation state and next actions, start with [`HANDOFF.md`](HANDOFF.md).

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

We treat these as research and systems-engineering problems rather than prompt-writing problems, while keeping the working LLM Wiki—not the research program itself—as the end goal.

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

The complementary convergence rule is equally important: once the evidence is sufficient for a usable path, build and dogfood it rather than turning every interesting question into another prerequisite.

## Repository map

- [`HANDOFF.md`](HANDOFF.md) — current continuation state, in-flight work, and next actions
- [`docs/00-project-charter.md`](docs/00-project-charter.md) — mission, scope, risks, success criteria
- [`docs/01-research-map.md`](docs/01-research-map.md) — research landscape and comparison framework
- [`docs/02-design-questions.md`](docs/02-design-questions.md) — design-question register
- [`docs/03-experiment-plan.md`](docs/03-experiment-plan.md) — experimental program and metrics
- [`docs/04-operating-model.md`](docs/04-operating-model.md) — how this lab itself is run
- [`docs/09-alpha-core-readiness-gate.md`](docs/09-alpha-core-readiness-gate.md) — Alpha Core invariants and convergence rule
- [`dogfood/`](dogfood/) — usable raw-first core and VS Code dogfood surface
- [`research/`](research/) — notes on papers, implementations, and adjacent systems
- [`experiments/`](experiments/) — reproducible experiments and results
- [`decisions/`](decisions/) — Architecture Decision Records (ADRs)

## Current program

The raw-first **Alpha Core is ready** under the convergence rule. The core now preserves immutable/verified raw evidence, explicit evidence revision and current/history semantics, minimum temporal/dispute semantics, deterministic provenance-preserving retrieval, optional exact raw-span provenance, and a read-only answer boundary.

The project is intentionally moving away from open-ended core infrastructure work and toward **real VS Code dogfood use**:

- E013 measures realistic revisit/update/query mix before any durable compiled provider is enabled.
- E015 measures W0 versus the E014-R1 structural-expand candidate in non-visible shadow before any retrieval-default change.
- `whole_object_v0` remains the visible/default retrieval path.
- persistent compiled state remains disabled pending realistic evidence.
- VS Code UI work has already reached a useful early shape and is deliberately deferred until real use exposes repeated friction or preference.

See [`HANDOFF.md`](HANDOFF.md) for the exact current in-flight item and immediate next steps.

## Status labels used in documents

- **Fact** — supported by a cited source or direct observation.
- **Hypothesis** — plausible but unverified.
- **Decision** — explicitly adopted in an ADR.
- **Experiment result** — produced by a reproducible experiment in this repository.
- **Open question** — unresolved and should not silently become policy.

The distinction is important: LLM-generated prose is not automatically evidence.
