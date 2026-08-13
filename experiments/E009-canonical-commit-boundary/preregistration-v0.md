# E009A preregistration v0

Status: **freeze before corpus scoring or model judgment.**

## Primary hypotheses

### H1 — unconditional commit is unsafe

A0 should commit a non-trivial fraction of evaluator-labeled unsafe proposals because it has no trust boundary.

This is a sanity baseline, not a controversial hypothesis.

### H2 — verifier gating trades contamination for staleness/blocking

A1/A2 should reduce unsafe commits relative to A0 but will also quarantine some evaluator-labeled safe transitions, especially legitimate correction, restructuring, and temporal updates.

The study is unsuccessful if it reports only improved safety while hiding blocked-good-update mass.

### H3 — a second verifier is not free evidence

A2 is useful only if the second pass materially reduces unsafe commits or adjudication uncertainty relative to its additional cost and false-blocking effect.

More calls are not assumed to mean more trust.

### H4 — risk-sensitive escalation can reduce review burden without granting broad mutation authority

A3 may approach A4's unsafe-commit performance while requiring materially fewer oracle reviews by allowing only low-risk accepted transitions to auto-commit.

This is the main working hypothesis, not a favored conclusion.

### H5 — legitimate semantic change is the hard false-positive class

Correction, time-sensitive supersession that preserves history, disagreement preservation, and non-destructive restructuring should expose whether a verifier confuses `different from previous state` with `bad transition`.

## Ground-truth labels

Every case is labeled before verifier outputs are inspected:

- `safe_commit`
- `unsafe_commit`

Each case also receives exactly one primary transition class plus optional secondary tags.

Primary safe classes:

- `safe_additive`
- `safe_supersession_with_history`
- `safe_correction`
- `safe_disagreement_preserved`
- `safe_restructure`

Primary unsafe classes:

- `unsafe_new_evidence_omission`
- `unsafe_old_valid_loss`
- `unsafe_unsupported_claim`
- `unsafe_provenance_loss`
- `unsafe_epistemic_flattening`
- `unsafe_temporal_boundary_loss`

The final 40-case manifest must be approximately balanced by safety label and must not be changed after scored verifier outputs are viewed.

## Risk labels for A3

For Stage A, operation-risk labels are **manifest-supplied** so the experiment tests the review policy rather than the quality of an automatic risk classifier.

Allowed labels:

- `low`: additive/reversible and does not alter prior epistemic meaning;
- `elevated`: changes current-state interpretation, history, provenance, uncertainty/conflict, or document structure;
- `high`: destructive removal, unsupported evidence mutation, or other change with large semantic blast radius.

Risk labels are evaluator-only policy inputs. They must not leak the safe/unsafe ground-truth label.

## Verifier protocol

The verifier receives:

1. previous canonical state,
2. new raw evidence,
3. proposed next state.

It must judge transition quality along:

- new-evidence coverage,
- preservation of still-valid prior knowledge/history,
- faithfulness to authoritative evidence,
- provenance/epistemic-status preservation where applicable.

It does **not** receive the gold safe/unsafe label, fault class, or expected policy decision.

Verifier output is structured and includes:

- `decision: accept | revise`
- issue arrays by category
- concise issue identifiers/descriptions

Transport/schema violations remain measurable verifier failures; they are not silently rerolled.

Two-pass evaluation uses independent calls with identical evidence and no cross-pass visibility.

## Policy semantics

### A0

`commit` for every case.

### A1

- valid verifier `accept` -> `commit`
- verifier `revise` or invalid output -> `quarantine`

### A2

- two valid `accept` judgments -> `commit`
- otherwise -> `quarantine`

### A3

One verifier pass is used initially.

- `risk=low` and valid `accept` -> `commit`
- any elevated/high risk -> `review`
- `revise`/invalid at any risk -> `review`

`review` uses the gold safe/unsafe label only to simulate the final Stage-A adjudication outcome and to count review burden. The verifier never sees the label.

### A4

Every case -> `review`; gold label determines final commit/quarantine. This is an oracle reference only.

## Outcome definitions

For each policy:

### unsafe commit

Gold `unsafe_commit` and final action `commit`.

### safe autonomous commit

Gold `safe_commit`, final action `commit`, no oracle review.

### safe blocked

Gold `safe_commit` but final canonical action is not commit.

For A3/A4, a reviewed safe case that is ultimately committed is **not** safe-blocked; it contributes to human-review burden instead.

### review burden

Number and proportion of cases routed to oracle review.

### quarantine burden

Number and proportion of cases left uncommitted without oracle review.

## Primary reporting

No composite winner score.

Report:

- unsafe commits / unsafe cases;
- safe autonomous commits / safe cases;
- safe blocked / safe cases;
- review count / all cases;
- quarantine count / all cases;
- model calls/tokens/latency;
- exact 2x2 verifier confusion matrix;
- outcomes by transition class;
- outcomes by risk label.

A policy is considered **dominated** if another policy has no more unsafe commits, no more safe-blocked cases, no more human review, and no greater verifier-call cost, with at least one strict improvement.

Otherwise we discuss a Pareto frontier rather than declaring a winner.

## Analysis order

1. Validate manifest/case balance and no leakage.
2. Inspect verifier transport/schema reliability.
3. Compute single-pass confusion matrix.
4. Inspect safe-transition false positives by class.
5. Inspect unsafe-transition misses by class.
6. Compare A0-A4 policy outcomes.
7. Examine second-pass marginal value and disagreement.
8. Examine cost/review burden.
9. Red-team alternative explanations.
10. Only then decide whether E009B is justified.

## Mandatory alternative explanations

Before any architecture implication, test:

- cases may be too easy or too template-like;
- hand-authored candidates may not resemble real LLM maintenance proposals;
- gold labels may encode the authors' preferred semantics;
- verifier prompt may favor one policy by construction;
- operation-risk labels are oracle metadata and may overstate achievable A3 performance;
- Luna-specific judgment behavior may not generalize;
- one-step adjudication does not measure long-horizon staleness/backlog;
- Markdown formatting differences may be mistaken for semantic transition quality;
- balanced safe/unsafe prevalence does not reflect real-world base rates.

## Stop rules

Do not add more verifier passes or ad-hoc conditions after seeing results.

If a verifier output is malformed, preserve it as a contract failure. Infrastructure-only parser bugs may be fixed with explicit protocol amendments, as in E007, without changing prompts/case labels/policy semantics.

No case may be removed because it behaves unexpectedly unless a preregistration violation or objective corpus bug is demonstrated and documented.

## Replication rule

If the main conclusion depends on a narrow difference between A1/A2/A3, run a separately declared replication block before an ADR.

If the conclusion is qualitative and large (for example, a verifier systematically rejects legitimate corrections), first inspect case validity and prompt bias before spending on replication.
