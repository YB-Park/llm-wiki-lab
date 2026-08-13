# E009A — Canonical Commit Boundary

Status: **T-v1 preregistered and frozen; no scored run yet.**

This is a focused activation of the existing E009 human-review/automation-boundary research axis after E007 exposed a more precise problem: semantic proposal quality and canonical mutation authority must be separated.

## Project-level objective

> Find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

E009A does not attempt to choose the full wiki representation, retrieval stack, model, IDE integration, or consolidation algorithm.

## Research question

When a proposed knowledge-state transition may be wrong, incomplete, over-conservative, or merely unusual, **what decision boundary should control mutation of canonical knowledge?**

The central trade-off is not only `catch bad edits`. A policy can also fail by blocking good updates until the wiki becomes stale, by consuming too many verifier calls, or by creating excessive human-review burden.

## Stage A: controlled transition adjudication

Proposal generation is **not** part of the variable under test. Corpus T-v1 contains 40 fixed fictional transition cases in 20 paired scenarios: one evaluator-labeled safe candidate and one unsafe candidate share the same previous state, new evidence, and risk label.

The corpus was red-teamed before scoring. T-v0 was rejected because candidate length alone predicted the label at 92.5% and the safe candidate was longer in all 20 pairs. T-v1 rebalanced those surface cues and is now frozen by SHA-256 in `corpus/manifest.json`.

Verifier-visible fields are only:

- previous canonical state;
- new authoritative evidence;
- proposed next canonical state.

Gold label, risk label, fault class, scenario identity, and rationale remain hidden from the verifier.

## Policy conditions

All policies are replayed over the same frozen two-pass judgment set. No automatic repair is performed in Stage A, so proposal quality is not confounded with adjudication quality.

### A0 — unconditional commit

Always commit the proposed next state.

Purpose: no-gate safety baseline / maximum autonomy.

### A1 — single-verifier gate

One blinded verifier judges every transition.

- valid `accept` -> commit
- `revise` or invalid verifier output -> quarantine

### A2 — two-pass consensus gate

Two separate blinded calls to the same pinned model judge every transition.

- both valid `accept` -> commit
- otherwise -> quarantine

The two calls measure empirical repeatability; they are not treated as statistically independent experts.

### A3 — risk-sensitive tiered evidence

A manifest-supplied operation-risk label is used only by the policy simulator; the verifier never sees it. Automatic risk-classifier quality is outside Stage A.

- **low risk** -> one verifier pass; valid `accept` may commit autonomously, otherwise oracle review
- **elevated risk** -> two verifier passes; two valid accepts may commit autonomously, otherwise oracle review
- **high risk** -> direct oracle review; no verifier call is needed by the counterfactual A3 deployment

This policy tests whether stronger evidence can be required as semantic/destructive risk rises without routing every non-trivial update directly to a person.

### A4 — review all

Every proposal receives simulated oracle review.

This is an adjudication upper bound and review-burden reference, not a claim that real humans are perfect and not a production recommendation.

## Primary outcomes

Report a Pareto frontier rather than one weighted winner score:

- unsafe commits / unsafe cases;
- safe autonomous commits / safe cases;
- safe blocked / safe cases;
- oracle review burden;
- quarantine/final rejection burden;
- verifier invalid/contract-failure rate;
- model calls, adapter-level input/output tokens, and wall time;
- outcomes by transition class and risk tier.

Unsafe commit and blocked-good-update are intentionally separate. Safety bought entirely by staleness, review burden, or inference cost is not treated as free.

## Frozen design artifacts

- `preregistration-v0.md`
- `pre-scoring-red-team-review-v0.md`
- `corpus-red-team-amendment-v1.md`
- `policy-red-team-amendment-v1.md`
- `corpus/manifest.json` / Corpus T-v1
- `run-plan-v1.json` / 80 interleaved calls
- `prompts/transition-verifier.md`

After `pre-run-freeze-v1.md` is recorded, semantic case text, gold labels, verifier prompt, and A0-A4 policy semantics are not changed based on scored outcomes. Infrastructure-only defects may be handled only through explicit amendments that preserve scored semantics and raw evidence.

## Explicit non-goals

Stage A does **not** answer:

- whether quarantine/rollback is sustainable over many waves;
- how pending evidence should be reincorporated;
- whether staging/selective consolidation is the final maintenance algorithm;
- whether Markdown pages or structured claims are the final representation;
- how operation risk should be classified automatically;
- whether behavioral answer failures should trigger state repair;
- whether Luna's judgment behavior generalizes to other models;
- real human-review accuracy/latency/UX;
- final VS Code/Copilot workflow.

## Follow-up trigger

Open E009B sequential commit/backlog study only if Stage A identifies a non-oracle boundary worth carrying forward. E009B would measure staleness, pending backlog, delayed reconsideration, and review batching over time.

A separate behavioral-alarm authorization study remains justified if `answer failure -> canonical mutation` is still unresolved after transition adjudication.

## Experimental equipment

The first block uses GPT-5.6 Luna because it is available in the actual managed environment and cheap enough for repeated controlled judgments. The model is experimental equipment, not an architecture decision.

If an architecture-relevant conclusion depends on a narrow verifier-behavior difference, replication with a second model is required before an ADR.

## Reporting/security boundary

Raw prompts, model responses, OTel, local paths, usernames/hostnames, and environment screenshots remain local. The normal successful runner emits a compact synthetic aggregate handoff only. External transfer occurs only if organizational policy permits it; see `docs/06-security-and-handoff-boundary.md`.

## Decision discipline

No production policy is adopted from E009A alone. Any eventual automation/commit policy requires an ADR with evidence, trade-offs, expected failure modes, operational cost, and reversal conditions.
