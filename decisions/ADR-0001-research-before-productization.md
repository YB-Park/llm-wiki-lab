# ADR-0001: Research Before Productization

**Status:** Accepted  
**Date:** 2026-08-12

## Context

The LLM Wiki concept is structurally simple but operationally dangerous.

A personal knowledge base that allows an LLM to continuously synthesize, rewrite, classify, merge, and delete knowledge can accumulate subtle errors that become progressively harder to detect. Early architectural choices about provenance, temporal updates, document granularity, schema, and maintenance may also become expensive to reverse after a large corpus is created.

The project could immediately build a VS Code + GitHub Copilot prototype. Doing so would provide fast feedback, but it would also risk treating the prototype's accidental design choices as default policy before their consequences are understood.

## Decision drivers

- Long-horizon contamination is a central risk.
- Destructive lifecycle choices may be difficult to reverse.
- Multiple adjacent research fields already contain relevant mechanisms and failure lessons.
- Many important design choices are experimentally testable.
- The intended system should remain inspectable and repairable over years, not merely impressive in a short demo.

## Alternatives considered

### A. Build first and iterate informally

Advantages:

- fastest path to something usable,
- immediate UX feedback,
- low upfront analysis cost.

Risks:

- accidental architecture becomes entrenched,
- generated corpus may become polluted before evaluation exists,
- changes are judged by subjective feel rather than controlled comparison.

### B. Fully design the architecture before any implementation

Advantages:

- rigorous conceptual treatment,
- fewer accidental early choices.

Risks:

- analysis paralysis,
- architecture by analogy rather than evidence,
- lack of real workflow feedback.

### C. Research-first, experiment-driven staged prototyping

Conduct structured prior-art research, define failure modes and evaluation methods, run targeted experiments on high-risk design questions, then build increasingly realistic prototypes.

## Decision

Adopt **Alternative C: research-first, experiment-driven staged prototyping**.

The project will progress through:

```text
problem framing
  -> landscape research
  -> failure model
  -> evaluation design
  -> targeted experiments
  -> ADRs
  -> minimal prototype
  -> real-use observations
  -> revised experiments/ADRs
```

Research is not a gate requiring all questions to be solved before coding. Small prototypes and scripts are encouraged when they answer a specific question. What is deferred is **premature production policy**, not experimentation.

## Consequences

### Benefits

- Major policies have explicit rationale.
- Competing alternatives remain visible.
- Negative results can prevent expensive mistakes.
- Future changes can trace back to the assumptions they invalidate.
- The repository becomes a record of how the system was designed, not only what was eventually built.

### Costs

- Slower path to a polished personal wiki.
- More documentation overhead.
- Some research questions will remain ambiguous despite effort.
- Controlled experiments may not fully predict long-term personal usage.

### Risks / failure modes

- Research can expand without bound.
- Experiments can optimize synthetic benchmarks rather than real usefulness.
- Documentation itself can become stale.
- Excessive caution can delay real-world learning.

## Mitigations

- Prioritize questions by irreversibility and contamination risk.
- Pair controlled corpora with realistic usage trials.
- Use explicit milestones rather than waiting for complete theoretical certainty.
- Treat the eventual prototype as another experiment, not as the end of research.

## Re-evaluation triggers

Revisit this decision if:

- research activity no longer changes design choices,
- experimental overhead exceeds the value of evidence produced,
- the major high-risk questions have converged enough that continued delay provides little benefit,
- a minimal prototype is required to answer the remaining questions.

## Related documents

- `docs/00-project-charter.md`
- `docs/01-research-map.md`
- `docs/02-design-questions.md`
- `docs/03-experiment-plan.md`
