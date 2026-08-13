# E009A — Canonical Commit Boundary

Status: **preregistered design phase; no scored run yet.**

This is a focused activation of the existing E009 human-review/automation-boundary research axis after E007 exposed a more precise problem: semantic proposal quality and canonical mutation authority must be separated.

## Project-level objective

> Find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

E009A does not attempt to choose the full wiki representation, retrieval stack, model, IDE integration, or consolidation algorithm.

## Research question

When a proposed knowledge-state transition may be wrong, incomplete, over-conservative, or merely unusual, **what decision boundary should control mutation of canonical knowledge?**

We want to distinguish:

- safe autonomous commit,
- quarantine/pending review,
- retention of the previous canonical state,
- explicit human review.

The central trade-off is not only `catch bad edits`. A policy can also fail by blocking good updates until the wiki becomes stale.

## Why this experiment is next

E007 produced four observations that make this question urgent:

1. provenance can be lost in canonical state under generic recursive rewriting;
2. some failed answers occur even when canonical state remains correct enough;
3. transition verification can remain unresolved while the state is still committed;
4. a noisy or over-strict behavioral probe can trigger canonical mutation.

Therefore `more verification` is not yet a sufficient design answer. We need to study **decision semantics after verification**.

## Stage A only: controlled transition adjudication

The first scored block is deliberately one-step and controlled.

Proposal generation is **not** part of the variable under test. Each case provides a frozen previous state, new evidence, proposed next state, operation/risk metadata, and evaluator-only ground truth indicating whether the proposal is safe to commit.

This isolates the commit/adjudication policy from stochastic proposal-generation quality.

### Planned case balance

Target: 40 fixed cases, balanced 20 safe / 20 unsafe before the first scored run.

Safe cases should include:

- additive exact information,
- legitimate current-state supersession while preserving history,
- correction of an earlier erroneous measurement,
- preservation of unresolved disagreement,
- legitimate restructure/rename that changes prose without semantic loss.

Unsafe cases should include:

- omission of important new evidence,
- deletion of still-valid historical/qualifying information,
- unsupported factual synthesis,
- provenance/evidence-identity loss,
- conflict/uncertainty flattening,
- temporal boundary loss or incorrect overwrite.

The exact case manifest is frozen before any scored model judgment is inspected.

## Policy conditions

Stage A compares decision policies over the **same frozen proposal cases**.

### A0 — unconditional commit

Always commit the proposed next state.

Purpose: lower-bound safety / upper-bound automation.

### A1 — single-verifier gate

One blinded verifier judges the transition.

- `accept` -> commit
- `revise` or invalid verifier output -> quarantine

No automatic repair is performed in Stage A. This isolates decision quality from repair quality.

### A2 — two-pass consensus gate

Two independent blinded verifier passes evaluate the same frozen transition.

- both `accept` -> commit
- any `revise`, invalid output, or disagreement -> quarantine

Purpose: measure whether extra model work meaningfully reduces unsafe commits or mostly increases false blocking/cost.

### A3 — risk-sensitive escalation

A deterministic operation-risk label is supplied by the case manifest for this first controlled study; classifier quality is explicitly outside scope.

- low-risk + verifier `accept` -> autonomous commit
- destructive/temporal/provenance/conflict-sensitive operations -> simulated human review regardless of accept
- any verifier `revise`/invalid -> simulated human review

Human review is represented by evaluator-only ground truth in Stage A and is an **oracle upper-bound for adjudication**, not a claim that real humans are perfect.

Purpose: test whether risk-sensitive review can approach oracle safety with materially lower review burden than reviewing everything.

### A4 — review all

Every proposal receives simulated oracle review.

Purpose: upper-bound decision quality / upper-bound review burden. This is not a production recommendation.

## Primary outcomes

Report a Pareto frontier, not a single weighted score.

For every policy:

- **unsafe commit rate**: unsafe proposals committed;
- **safe auto-commit rate**: safe proposals committed without human review;
- **safe blocked/quarantined rate**: good updates prevented from becoming canonical;
- **review rate**: proportion requiring human review;
- **quarantine rate**;
- verifier invalid/contract-failure rate;
- model calls, input/output tokens, wall time;
- results by fault/operation class.

Unsafe commit and blocked-good-update are intentionally reported separately. We will not hide the trade-off inside an arbitrary loss weight.

## Secondary diagnostics

- verifier agreement/disagreement by case class;
- false positives on legitimate restructure/rename;
- provenance-loss detection;
- temporal/correction/change distinction;
- conflict/uncertainty preservation;
- whether the second verifier adds useful information conditional on the first pass;
- marginal safety improvement per extra verifier call.

## Explicit non-goals

Stage A does **not** answer:

- whether quarantine is better than rollback over many waves;
- how pending evidence should be reincorporated;
- whether a staging buffer should exist;
- whether Markdown pages or structured claims are the final representation;
- how to classify risk automatically;
- whether behavioral answer failures should trigger state repair;
- whether a particular model generalizes across providers;
- IDE review UX.

Those become follow-ups only if Stage A identifies a useful boundary.

## Follow-up triggers

### Open E009B sequential commit/backlog study if

one or more non-oracle policies materially reduce unsafe commits while retaining enough safe updates to justify studying long-horizon staleness/backlog behavior.

E009B would compare `quarantine`, `retain previous state`, delayed reconsideration, and review batching over a sequential stream.

### Open behavioral-alarm authorization study if

transition adjudication looks tractable but E007's `answer failure -> canonical mutation` risk remains unresolved.

That study must include known `state-good / answer-bad` and `state-bad / answer-bad` cases and compare direct repair against state diagnosis before mutation.

### Stop/redirect if

verifier-based policies are dominated by simple review or exhibit unacceptable false-blocking across legitimate safe transitions. In that case we should not add more verifier sophistication merely to preserve an attractive automation story.

## Experimental equipment

The first block may use GPT-5.6 Luna because it is available in the actual managed environment and cheap enough for repeated controlled judgments. The model is experimental equipment, not an architecture decision.

If a headline result depends strongly on verifier behavior, replication with a second model is required before promoting the result to an architecture-level policy.

## Reporting/security boundary

Raw model responses, local paths, telemetry, and environment metadata remain local to the execution environment.

The harness should emit a minimal structured safe handoff containing only synthetic case IDs, aggregate counts, and normalized metrics. External transfer occurs only if permitted by organizational policy.

## Decision discipline

No production policy is adopted from E009A alone. Any eventual automation/commit policy still requires an ADR with evidence, trade-offs, expected failure modes, and reversal conditions.
