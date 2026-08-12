# E007 Condition Protocol v0

Status: frozen orchestration design before first scored run
Date: 2026-08-12

This file specifies **how calls are sequenced**, not just what individual prompts say.

## Common rules

- One concrete Copilot model is pinned for an entire run family.
- The same pinned model is used for maintenance, verifier, repair, and answer-generation calls. Scoring is separate.
- All conditions receive sources in the same wave order.
- C1–C4 maintain one derived Markdown artifact.
- No condition receives future sources, future questions, or evaluator ground truth.
- Query batches include only questions whose `ask_after_wave <= current wave` according to the rules below.
- Raw source text is immutable.

## C0 — raw full-context control

Corpus C v0 fits comfortably enough to use the strongest simple control.

For every scheduled query batch:

1. concatenate all raw sources available through the current wave,
2. render `answer-batch.md`,
3. call the pinned model once,
4. score answers.

C0 maintains no derived wiki and performs no maintenance calls.

This changes the earlier shorthand "raw/search" into a precise **raw full-context baseline for C-v0**. Search-based baselines belong in E006.

## C1 — naive compiled wiki

For each wave W:

1. render `C1-update.md` with the previous derived wiki and the new source wave,
2. call the pinned model once,
3. accept the returned Markdown directly as the next wiki state,
4. run the scheduled primary query batch against the derived wiki only.

No raw sources are supplied to query answering.

No verifier or repair call is performed.

## C2 — source-grounded compiled wiki

For each wave W:

1. render `C2-update.md` with previous wiki, new wave, and **all raw sources available through W**,
2. call the pinned model once,
3. accept the returned Markdown directly as the next wiki state,
4. run the scheduled primary query batch against the derived wiki only.

C2 therefore pays the context cost of source re-grounding during maintenance but does not pay a separate verifier cost.

## C3 — transition verification + one repair opportunity

For each wave W:

1. create a candidate wiki using the same `C2-update.md` call as C2,
2. render `C3-verify.md` using previous wiki, new wave, candidate wiki, and all available raw sources,
3. call the verifier once,
4. if decision is `accept`, candidate becomes next state,
5. if decision is `revise`:
   - render `C3-repair.md`,
   - call one repair pass,
   - run `C3-verify.md` **one final time** on the repaired result,
   - accept the repaired result as next state even if residual issues remain, but record the final verifier report as unresolved.
6. run the scheduled primary query batch against the accepted derived wiki only.

Why accept after one repair instead of looping until clean?

- unbounded repair loops make cost incomparable,
- a verifier can itself be wrong,
- real autonomous maintenance needs a bounded budget,
- residual issues are useful experimental evidence.

No hidden/manual repair is allowed.

## C4 — transition verification + behavioral regression repair

C4 first performs the complete C3 process and obtains a provisional next wiki.

Then:

1. collect all **previously passing regression-eligible queries** from earlier waves,
2. answer those queries from the provisional derived wiki only,
3. score them with the deterministic regression scorer,
4. if no previously passing query regresses, accept the provisional wiki,
5. if regressions occur:
   - render `C4-regression-repair.md` with only the regression failures plus all available raw sources,
   - call exactly one regression-repair pass,
   - rerun the regression batch once,
   - accept the repaired wiki regardless of residual failures and record those failures.
6. run the current wave's scheduled primary query batch against the final derived wiki.

### Regression-eligible query classes

For v0, regression gating uses only queries for which deterministic scoring is sufficiently reliable:

- `local_exact`,
- `temporal`,
- `provenance`,
- `negative_uncertainty_delayed` where a deterministic expectation is defined.

`global_synthesis` and `multi_hop` are measured but do not gate C4 edits in v0 because an LLM-as-judge gate would add another major probabilistic variable.

## Primary query schedule

A query is first run when `ask_after_wave == current wave`.

C1–C4 primary answers use only the derived wiki artifact.
C0 uses all raw sources available through the wave.

Previously answered queries are not automatically rerun in C1–C3 except in separate analysis. C4 reruns only the regression-eligible subset as part of its maintenance policy.

This lets us attribute C4's additional token cost explicitly to regression protection.

## Natural-error and injected-error run families

E007 has two families.

### Family N — natural behavior

No artificial faults are inserted. Measure naturally occurring fabrication, omission, preservation failure, temporal error, attribution error, and regression.

### Family I — controlled fault injection

Start from the same protocol but inject exactly one predefined fault class at a fixed state boundary. Run fault classes separately rather than stacking all faults into one run.

Injection placement and deterministic mutation functions must be frozen in a separate file **before Family I scored runs**.

Family N should run first because its behavior is easier to interpret and gives a cost estimate without deliberately damaging state.

## Stochastic repetition

The number of repetitions per condition is not set here yet.

Procedure:

1. validate infrastructure,
2. run one explicitly non-scored dry run solely to verify parsing/telemetry and estimate cost,
3. choose repetition count based on budget/variance considerations **without inspecting comparative quality conclusions**,
4. record the chosen count in run configuration before scored runs begin.

## Protocol version rule

Once a scored run uses v0, any semantic change to this file or prompt files creates v1. Existing v0 results remain preserved and are never silently relabeled as having used the new protocol.
