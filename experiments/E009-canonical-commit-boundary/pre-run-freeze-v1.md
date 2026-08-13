# E009A pre-run freeze v1

Status: **FROZEN before any scored Corpus T verifier judgment.**

This document closes the E009A pre-scoring design/red-team phase. After this point, scored outputs may be observed, but the semantic experiment definition is not changed in response to results.

## Project objective

> Find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

E009A asks one narrow question inside that objective:

> What evidence threshold should authorize canonical mutation, and when should a transition instead be quarantined or escalated to review?

It does not choose the final wiki representation, consolidation algorithm, retrieval stack, model, or IDE workflow.

## Scored-output status at freeze

- Corpus T scored verifier calls observed: **0**
- Corpus T semantic outcomes inspected: **0**
- Policy outcome table observed: **0**

The only model work performed before this freeze belongs to earlier E007 experiments. E009A's one-call non-scored preflight has not yet been run at this freeze point.

## Frozen corpus

- corpus: `T-v1`
- 40 cases
- 20 paired scenario groups
- 20 `safe_commit`
- 20 `unsafe_commit`
- each pair shares previous state, new evidence, and risk tier
- each pair contains one safe and one unsafe candidate
- cases SHA-256: `6690fdfcd610a61743b18e2a37060aa262c9e6bd235880795cc444c4f7c16767`

Risk-tier composition is paired/balanced by label:

- low: 8 cases = 4 safe + 4 unsafe
- elevated: 26 cases = 13 safe + 13 unsafe
- high: 6 cases = 3 safe + 3 unsafe

### T-v0 rejection

T-v0 was rejected before scoring because a trivial candidate-byte threshold could classify the gold label with best one-dimensional accuracy 0.925 and the safe candidate was longer in 20/20 pairs.

This was a corpus-design failure, not a model result.

T-v1 rebalanced surface form without changing the intended semantic fault taxonomy. Frozen T-v1 audit:

- candidate-byte best one-dimensional threshold accuracy: 0.700
- line-count best one-dimensional threshold accuracy: 0.600
- source-mention best one-dimensional threshold accuracy: 0.600
- safe candidate longer: 10/20 pairs
- unsafe candidate longer: 10/20 pairs

We do **not** continue editing T-v1 to chase a 0.500 post-hoc surface statistic. The obvious near-deterministic shortcut was removed; further tuning to the audit itself would risk a different form of benchmark overfit.

## Frozen verifier interface

The verifier receives only:

1. previous canonical state;
2. new authoritative evidence;
3. proposed next canonical state.

It does not receive case ID, scenario group, gold label, risk tier, transition class, rationale, or expected policy action.

The verifier evaluates:

- new-evidence coverage;
- preservation of still-valid/historical knowledge;
- faithfulness;
- provenance where material;
- temporal and epistemic semantics.

Large rewrites are not inherently failures. Corrections and supersessions may legitimately replace prior wording when history/meaning is represented correctly.

Structured output is frozen to `accept | revise` plus issue arrays. Malformed output is recorded as an invalid judgment and is **not semantically rerolled**.

## Frozen judgment plan

- model: `gpt-5.6-luna`
- plan: `run-plan-v1.json`
- 80 total verifier calls
- exactly two separate calls per case
- fixed interleaved sequence 1..80
- pass-1 and pass-2 have identical semantic inputs and no cross-pass visibility

Two calls to the same model are empirical repeatability/consensus evidence, not statistically independent experts.

## Frozen policy semantics

### A0 — unconditional commit

Every candidate commits.

### A1 — one-pass gate

Every case uses pass 1.

- valid accept -> commit
- revise/invalid -> automatic quarantine

Counterfactual verifier calls: 40.

### A2 — two-pass consensus

Every case uses both passes.

- two valid accepts -> commit
- otherwise -> automatic quarantine

Counterfactual verifier calls: 80.

### A3 — risk-sensitive tiered evidence

Risk is manifest-supplied and hidden from the verifier.

- low: one verifier; accept -> autonomous commit, otherwise oracle review
- elevated: two verifiers; both accept -> autonomous commit, otherwise oracle review
- high: direct oracle review

Given frozen T-v1 risk counts, counterfactual verifier calls are 60 before any model outcome is known: 8 low calls + 52 elevated calls + 0 high calls.

A3 tests the potential of risk-sensitive adjudication **assuming risk classification is correct**. It does not establish how to classify risk in production.

### A4 — review all oracle reference

Every case receives simulated oracle review. This is an upper-bound adjudication reference, not a model of real human accuracy or UX.

## Frozen primary outcomes

No weighted winner score.

Report separately:

- unsafe commits / unsafe cases;
- safe autonomous commits / safe cases;
- safe blocked / safe cases;
- review burden;
- automatic quarantine/final rejection burden;
- verifier invalid-contract rate;
- pass disagreement;
- calls, adapter-level tokens, wall time;
- outcomes by transition class and risk tier.

Interpretation is Pareto-oriented. Safety purchased entirely through blocked good updates, review volume, or inference cost is not free.

## Infrastructure boundary

The following may be fixed after freeze **only if they do not alter case semantics, verifier prompt semantics, policy semantics, or scored judgments**:

- parser/runtime crash;
- CLI compatibility;
- telemetry collection bug;
- safe-report formatting bug;
- resume/archive mechanics.

Any such change requires an explicit amendment and preserved raw local evidence.

A malformed but successfully returned verifier judgment is **not** an infrastructure error and may not be retried merely to obtain a clean judgment.

Infrastructure failure may retry the exact same frozen planned call only after the incomplete attempt is preserved with `archive_incomplete_call_v1.py`.

## Security boundary

Raw prompts/responses, telemetry, local paths, usernames/hostnames, and environment screenshots remain local. Successful external handoff contains synthetic aggregate metrics only and is transferred only when organizational policy permits it.

If organizational policy prohibits even sanitized transfer, the experiment remains useful locally and no external artifact is required.

## Mandatory limitations retained before seeing results

Even a strong result cannot by itself establish production policy because:

- the cases are hand-authored and fictional;
- gold labels may still encode author assumptions;
- T-v1 may still contain subtle benchmark cues despite the surface audit;
- safe/unsafe prevalence is deliberately 50/50, not a production base rate;
- risk labels are oracle metadata;
- same-model passes are correlated;
- one-step adjudication omits quarantine backlog/staleness dynamics;
- oracle review does not estimate actual human error, latency, fatigue, or UX;
- frozen candidates do not measure real proposal-generation quality;
- Markdown transition semantics do not settle the final representation question;
- Luna-specific behavior requires replication if a narrow result becomes architecture-critical.

## What is forbidden after this freeze

Do not change because a scored result is surprising:

- case wording or gold labels;
- case inclusion/exclusion;
- risk labels;
- verifier prompt;
- number of verifier passes;
- A0-A4 action semantics;
- primary outcome definitions;
- call order;
- model inside the primary block.

Do not add an A5 after seeing the frontier.

## Execution gate

1. CI must be green.
2. Run the one-call synthetic `preflight.py`; it must report valid structured judgment + OTel and does not use Corpus T.
3. Only then run `run_stage_a_v1.py` through all 80 planned calls.
4. Do not interpret partial judgments.
5. Analyze only after the complete safe handoff exists.

## Exit

The pre-scoring phase is closed. The next information we need is empirical data, not another architecture opinion.
