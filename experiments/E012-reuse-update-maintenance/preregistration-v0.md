# E012 reuse-to-update maintenance gate — preregistration v0

Status: **design fixed before model scoring**

## Research question

E011 showed that a query-independent compiled topic state (`C0`) can match full raw-topic context (`R1`) on a static synthetic workload and can amortize its build cost after enough topic revisits.

E012 asks the next falsification question:

> When authoritative knowledge changes, at what revisits-per-update ratio, if any, does full-rebuild durable compilation remain non-dominated versus reading the complete raw topic at query time?

This is a maintenance-economics gate, not a representation or patch-algorithm contest.

## Conditions

Only two conditions survive into this gate:

- `R1`: all authoritative raw topic documents available through the current wave;
- `C0`: one generic query-independent durable synthesis rebuilt from all authoritative raw topic documents available through the current wave, with no raw documents supplied at query time.

C0 is rebuilt from raw evidence at every wave. It is **not** recursively updated from its previous compiled state. This deliberately isolates maintenance economics from recursive-contamination and incremental-patching design choices.

## Topics and waves

Use the same 12 fictional E011 topic identities and 32-document large-scale W0 corpus as a dependency.

For every topic:

- `W0`: original 32-document E011 large topic;
- `W1`: add an authoritative supersession that changes the current exact value and one named constraint, plus a decision review that reaffirms the current choice under current constraint names;
- `W2`: add an authoritative correction that replaces the W1 exact value while preserving the W1 constraint change, plus a decision supersession that changes the current selected option and explicitly preserves the previous decision as history.

Final topic size is 36 documents. Old evidence remains present; new documents state their temporal/epistemic relationship to older evidence explicitly.

## Queries

Three queries per topic per wave:

1. `current_exact`: recover the current exact value and authoritative source;
2. `current_synthesis`: recover all four current named constraints;
3. `decision_history`: recover the current decision and its current rationale; at W2 also recover the superseded prior choice.

The compiler never sees questions or answer keys.

## Model and prompts

- model: `gpt-5.6-luna` only;
- reuse the frozen E011 generic compiler prompt unchanged;
- reuse the frozen E011 shared answer prompt/contract unchanged;
- GitHub Actions Copilot CLI JSONL transport;
- no semantic rerolls;
- built-in MCPs and tools disabled;
- OTel message-content capture disabled.

## Experimental unit and size

- independent cluster: topic (`n=12`);
- wave, condition, and query class are paired within topic;
- 3 waves x 3 queries x 2 conditions = 18 logical answer tasks/topic;
- 216 logical answer tasks total;
- 36 compilation builds total.

The sample is a controlled pilot designed to detect a large maintenance/economic crossover, not to establish a small production effect.

## Primary quality outcomes

Report separately:

- strict answer pass;
- required answer-signal coverage;
- required source-ID coverage;
- answer-contract invalid count;
- current-vs-historical confusion count where deterministically inferable from required/forbidden signals.

No weighted winner score and no LLM-as-judge primary metric.

A cost break-even is never called a value win if C0 quality is materially worse than R1.

## Compiled-state diagnostics

At every wave report:

- current required-signal preservation;
- required provenance preservation;
- stale-current signal retention where an older value/choice is presented as current;
- invented source IDs;
- compiled-state bytes / raw-context bytes.

State fidelity remains separate from answer behavior.

## Lifecycle economics

The primary economic axis is **revisits per update**.

For a fixed revisit count `N` per wave:

- R1 lifecycle query cost = `N × sum(raw query-bundle cost per wave)`;
- C0 lifecycle cost = `sum(rebuild cost per wave) + N × sum(compiled query-bundle cost per wave)`.

Freeze reuse-per-update regimes:

- `N=1`
- `N=3`
- `N=6`
- `N=10`
- `N=20`

Also report the finite break-even `N` where one exists, both aggregate and by topic.

Token-volume accounting uses one OTel `invoke_agent` span per call and the same published Luna price estimator used by the remote lab. Token estimates are operational proxies, not human-value scores.

## Statistical interpretation

Use topic-cluster paired bootstrap for headline C0-R1 quality differences. Report point estimates and 95% bootstrap intervals. Wave/class cells are secondary diagnostics, not independent samples.

## Kill / narrow rule

- If C0 loses meaningful quality after updates, do not compensate by adding a more complex maintenance algorithm inside E012.
- If C0 quality remains comparable but break-even revisits-per-update moves beyond a plausible workload range, narrow durable compilation rather than optimizing it by default.
- If a plausible region survives, the next evidence requirement is realistic/shadow calibration of actual revisit/update distributions before detailed representation or autonomous maintenance work.

## Budget guard

Expected model-call order of magnitude is similar to E011 remote Stage 1A. Set:

- per-call max AI credits: 30;
- total estimated AI-credit guard: 400.

The guard is a ceiling, not a target. Deterministic generation, validation, scoring, bootstrap, and lifecycle replay use zero model calls.

## Interpretation limits

Even a positive E012 result remains controlled synthetic benchmark evidence. It does not establish realistic revisit frequency, human navigation value, production safety, or cross-model generality.
