# Lab Operating Model

This document governs how research, decisions, experiments, implementation, dogfood, and handoff state move through the repository.

The lab exists to produce a **working VS Code-first LLM Wiki**. Research rigor is a means to that end; it must not become an endless prerequisite chain after a usable decision is sufficiently supported.

## 1. Artifact roles

### `HANDOFF.md` — current continuation state

Purpose: let the next session/operator continue without reconstructing the project from history.

Rules:

- keep current state, in-flight work, immediate next actions, and important “do not accidentally do” boundaries;
- **replace/delete stale information** instead of appending a project diary;
- point to canonical evidence rather than copying experiment/ADR detail;
- if handoff disagrees with merged code or an accepted ADR, code/ADR wins and handoff is corrected immediately.

### `docs/02-design-questions.md` — current question register

Purpose: track unresolved or active architecture/product questions.

Rules:

- keep statuses current;
- `DECIDED` requires an accepted ADR;
- completed experiments may narrow a question without silently becoming policy;
- remove obsolete “current focus” language when the program moves on.

### `docs/03-experiment-plan.md` — current experiment map

Purpose: show active gates, completed evidence that constrains the architecture, parked families, and the current critical path.

Detailed protocols/results belong under `experiments/`, not repeated forever in the program map.

### `research/` — external evidence / prior art

Record sources, implementation observations, known limitations, failure modes, and our interpretation. Do not treat one system's design choice or an LLM summary as universal evidence.

### `experiments/` — reproducible evidence

State protocol/decision boundaries before interpreting results when practical. Preserve negative results. Keep synthetic mechanism evidence distinct from natural product/workload evidence.

### `decisions/` — accepted policy

Non-trivial architecture behavior should be justified by an ADR containing context, alternatives, evidence, trade-offs, failure modes, and re-evaluation triggers.

Do not rewrite an old ADR to make history look cleaner; supersede it with a later ADR when policy changes.

### `dogfood/` — current product/core implementation

- `dogfood/llm_wiki/`: editor-agnostic trustworthy substrate and CLI/testing surface;
- `dogfood/vscode/`: first-class VS Code product surface and installable VSIX.

The CLI is a substrate/fallback, not permission to leave important customer operations terminal-only forever.

## 2. Epistemic discipline

Use these labels mentally and in artifacts where useful:

- **Fact** — supported by a source or direct measured observation.
- **Observation** — seen in a test/experiment/real use; may not generalize.
- **Hypothesis** — proposed explanation or design expectation.
- **Interpretation** — reasoning about facts/observations.
- **Decision** — adopted policy in an ADR.
- **Open question** — intentionally unresolved.

A confident LLM sentence does not upgrade epistemic status.

## 3. Two different readiness concepts

Do not conflate them.

### Core readiness

Alpha Core readiness means the raw-first trust loop has enough integrity/provenance/history/retrieval/answer boundaries to be used safely for dogfood. `docs/09-alpha-core-readiness-gate.md` owns this definition.

### Customer readiness

Customer readiness means a real VS Code + Copilot user can actually live with the product: recover knowledge, navigate original sources, express corrections/disagreements, give feedback, survive operational mistakes, and use the real model path repeatedly without hidden assumptions.

E010 owns the current customer/product gate. Passing deterministic core CI is **not** sufficient for customer readiness.

## 4. Convergence rule

After Alpha Core Ready, **stop adding core infrastructure by default**.

Core work requires at least one of:

1. an observed dogfood/product blocker;
2. an E013/E015 preregistered boundary crossing;
3. a reproducible trust/data-loss failure in an existing Alpha invariant.

“Interesting”, “future-proof”, “modern architecture”, or “another team uses it” are not enough.

When a real product blocker exists, fix the **smallest layer that owns the problem**. A VS Code surface gap should not automatically become a new database/schema/retrieval subsystem.

## 5. Product dogfood discipline

Real use must not be replaced by synthetic activity once the question is about user behavior.

For E010/E013/E015:

- use the installable VSIX in actual VS Code work;
- preserve private/company-data boundaries;
- do not manufacture visits/updates/query classes to reach sample minima;
- capture friction and fixed-code feedback when practical;
- distinguish “the capability exists in core” from “a normal VS Code user can perform it”; 
- prefer repeated multi-session use over one impressive demo.

The repository itself is a valid self-hosting corpus, but self-repo success is only one realistic workload, not proof of universal customer value.

## 6. Model / Copilot cost discipline

Use model calls when the research/product question **is about model behavior**.

Examples that justify paid calls:

- actual answer usefulness/faithfulness;
- exact model/adapter behavior;
- compiled synthesis quality;
- a preregistered LLM-evaluated comparison where deterministic checks are insufficient.

Do **not** spend model calls to re-test deterministic storage, JSONL integrity, permissions, lexical ranking, or other questions that code/fault injection can answer directly.

Cost discipline does not mean under-testing a genuine model question. When a small paid experiment is necessary, run enough calls to answer the preregistered question rather than stopping early only to save credits.

The actual VS Code/Copilot Pro entitlement must be tested in a real user session; CI must not fake that evidence or silently substitute another model.

## 7. Change-risk tiers

### Low risk

- current-state doc refresh;
- research notes;
- recording measured outputs;
- tests that do not change product semantics.

### Medium risk

- product UX behavior;
- telemetry/event semantics;
- retrieval candidate behavior;
- experiment protocol changes before official scoring.

Use a short-lived branch/PR and relevant automated consumer tests.

### High risk

- canonical evidence/history semantics;
- destructive operations;
- source identity/provenance meaning;
- policy changes to accepted ADR behavior;
- changing frozen experiment inputs/scorers after results are visible.

Require explicit rationale, strong regression/fault tests, and an ADR or ADR amendment/supersession where policy changes.

## 8. Experiment lifecycle

Use the full controlled lifecycle when the decision benefits from it:

1. choose question;
2. write hypothesis/boundary;
3. freeze corpus/protocol/scorer enough for fairness;
4. run baseline/alternatives;
5. compute deterministic metrics;
6. add human/LLM evaluation only where justified;
7. record result and threats;
8. decide, narrow, kill, or generate a new question.

For **real dogfood** the lifecycle is lighter:

1. state what behavior/decision the natural data is meant to inform;
2. instrument privacy-minimal events before looking at them;
3. use the product normally;
4. wait for preregistered sufficiency rather than fabricating activity;
5. make the narrow decision supported by the observed distribution/failures.

## 9. Git / PR workflow

Prefer short-lived branches and PRs for consequential implementation, experiment, or product changes so diffs remain inspectable.

A normal completion unit is:

```text
problem/evidence
  -> narrow change
  -> tests / product check
  -> PR / decision record when needed
  -> HANDOFF current-state refresh
```

Do not leave a PR/issue body claiming a merge/result that did not actually occur. Current handoff must reflect merged state, not intent.

## 10. How LLMs participate

Good roles:

- research assistant;
- synthesis/comparison tool;
- code assistant;
- test-data generator;
- experimental subject;
- read-only answerer over retrieved evidence.

Bad roles:

- self-authenticating evidence source;
- invisible policy maker;
- automatic winner-selection for disputed evidence;
- justification for deleting provenance/history;
- substitute for a deterministic comparison that is cheaper and stronger.

## 11. Release posture

Until E010 customer gates have evidence, describe the product as **Alpha/dogfood**, not customer-ready.

A customer-ready candidate must at minimum demonstrate:

- Alpha trust/integrity remains green;
- useful self-hosting/realistic retrieval;
- unambiguous original-source navigation in realistic workspaces;
- first-class VS Code access to trust-sensitive update/correction/dispute behavior when needed;
- low-friction product feedback;
- a forgotten-topic/cross-topic recall story;
- a minimal backup/restore operating story for valuable local knowledge;
- real-session evidence for the actual Copilot/model path shipped;
- repeated multi-session usefulness rather than a one-shot demo.

A failed customer gate should generate the smallest product fix, **not a new open-ended architecture program**.
