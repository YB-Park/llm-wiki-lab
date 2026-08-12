# Research

This directory contains prior-art research and evidence that informs design questions.

## Planned tracks

```text
research/
  llm-wiki/
  agent-memory/
  retrieval/
  temporal-knowledge/
  provenance/
  pkm/
  data-systems/
  docs-as-code/
  information-science/
```

Directories should be created as actual notes are added; the tree above is a roadmap, not a taxonomy decision for the future personal wiki.

## Note standard

A substantial system/paper/practice note should cover:

- source and review date,
- problem addressed,
- architecture/method,
- evaluation/evidence,
- observed strengths,
- limitations and failure modes,
- relevant project design questions,
- candidate experiments,
- our interpretation and uncertainty.

## Evidence rules

1. Prefer primary sources for technical mechanisms and benchmark claims.
2. Clearly mark anecdotal operating experience as anecdotal.
3. Do not flatten conflicting evidence into a single conclusion.
4. A source can motivate an experiment without proving that its design is correct for our workload.
5. Research notes do not create project policy; accepted ADRs do.

## Synthesis artifacts

The first pass should eventually produce:

- a direct LLM Wiki implementation landscape,
- an adjacent-system landscape,
- a cross-system comparison matrix using the dimensions in `docs/01-research-map.md`,
- a failure-mode catalog,
- a list of architecture hypotheses worth testing.
