# Copilot Instructions — LLM Wiki Lab

This repository is a research lab for designing a trustworthy personal LLM Wiki.

## Primary rule

Do not silently turn hypotheses, examples, or LLM suggestions into project policy.

A policy is considered adopted only when it is recorded in an accepted ADR under `decisions/`.

## Product interaction target

The **primary product target is VS Code**. Product-facing work should assume that the first-class user experience will live in VS Code alongside Git/GitHub, GitHub Copilot, and local Markdown/code files.

This is **VS Code-first, not VS Code-only**:

- keep storage, retrieval, provenance, evaluation, and maintenance semantics editor-agnostic where practical;
- treat CLI/Python commands as substrate, tests, automation hooks, and fallback surfaces rather than the intended long-term primary UX;
- prefer VS Code commands, source navigation, editor context, panels/views, and Copilot-assisted workflows for dogfood interaction work;
- do not duplicate or weaken epistemic rules inside the extension layer;
- do not introduce VS Code-specific architecture into the trustworthy core unless evidence requires it.

When there is a tension between a convenient CLI-only implementation and a reasonably small VS Code-first interaction surface, preserve the reusable core and add the VS Code adapter rather than declaring the CLI to be the finished product.

## Epistemic discipline

When creating or editing research/design documents, distinguish:

- **Fact** — supported by an external source or direct measured observation.
- **Observation** — seen in a specific implementation, experiment, or usage session.
- **Hypothesis** — plausible but unverified.
- **Interpretation** — reasoning derived from facts or observations.
- **Decision** — adopted through an ADR.
- **Open question** — intentionally unresolved.

Do not present LLM-generated text as evidence merely because it sounds plausible.

## Research work

When adding research notes:

1. preserve enough source information to verify important claims later,
2. separate what the source says from our interpretation,
3. record limitations and conflicting evidence,
4. map findings to relevant design questions,
5. prefer primary sources for technical claims when practical.

Do not infer that a popular implementation choice is necessarily optimal for this project.

## Experiments

When modifying an experiment:

- preserve the hypothesis, protocol, corpus version, prompts, and raw outputs needed for reproducibility when feasible,
- distinguish measured results from interpretation,
- do not rewrite historical results to match a newer hypothesis,
- record failures and ambiguous results,
- avoid changing evaluation criteria after seeing results without explicitly documenting the change.

## Decisions

For consequential architecture or policy choices, propose or update an ADR containing:

- context,
- alternatives,
- evidence,
- decision,
- benefits and costs,
- known failure modes,
- re-evaluation triggers.

Do not edit an old accepted ADR to hide that a decision changed. Prefer a new ADR that supersedes it.

## Risk-sensitive editing

Be especially conservative with operations that:

- delete evidence or experiment outputs,
- alter source-of-record material,
- merge/split/rename established structures,
- change shared metrics,
- change provenance semantics,
- change temporal/contradiction semantics.

Prefer reversible changes and explicit migration notes.

## Writing style

- Be precise and skeptical rather than promotional.
- State uncertainty explicitly.
- Prefer concrete failure examples over vague warnings.
- Avoid unnecessary framework complexity unless it answers a documented problem.
- Keep terminology stable; if terminology changes, document the migration.

## Current project phase

The project is in research plus architecture-neutral dogfood phase.

Do not prematurely create the final production wiki folder structure, ontology, retrieval database, graph layer, or autonomous maintenance workflow unless the task is explicitly an experiment intended to evaluate one of those choices.

It is acceptable to build a VS Code-first dogfood shell over architecture-neutral raw/retrieval/provenance primitives, provided it does not silently promote a persistent compiled layer or canonical LLM-derived state before the evidence gates support that move.

Read these before consequential changes:

- `docs/00-project-charter.md`
- `docs/02-design-questions.md`
- `docs/03-experiment-plan.md`
- relevant ADRs under `decisions/`
