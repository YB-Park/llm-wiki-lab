# E012 pre-run freeze v0

Status: **FROZEN BEFORE SCORED E012 MODEL CALLS**

At this freeze point, E012 has made zero model calls. Only deterministic generation, red-team review, compiler-leak checks, source/signal validation, hash-seed determinism checks, code compilation, and runner/analysis self-tests have run.

## Research purpose

Test whether the selective high-reuse compilation region found by E011 survives authoritative updates once full-rebuild maintenance cost and stale/current semantics are included.

A negative result is valid. E012 is allowed to narrow or kill full-rebuild durable compilation without adding a more sophisticated maintenance algorithm.

## Frozen corpus and queries

- 12 fictional topic clusters inherited from E011 large-scale topics;
- W0: 32 documents/topic;
- W1: 34 documents/topic after authoritative supersession + decision review;
- W2: 36 documents/topic after correction + decision supersession/history;
- final unique documents: 432;
- wave-specific queries: 108;
- query classes: current exact/provenance, current synthesis, decision/history.

Fingerprints:

- documents SHA-256: `faa7986fb0644b240857f907f6158b71763aa2a5393c0fe55836b0f918e73b4f`
- queries SHA-256: `f5702e42b94c4d857a3c99c54af48413879602ac9d42036cc1e018257f3b5e89`

The query fingerprint was checked in separate Python processes under different `PYTHONHASHSEED` values after a prescore nondeterministic set-iteration defect was found and fixed. Both seeds produce the same document/query fingerprints.

## Frozen conditions

- `R1`: complete raw topic evidence available through the current wave;
- `C0`: one query-independent compiled note rebuilt from all raw topic evidence available through the current wave; no raw evidence supplied during answering.

C0 is always rebuilt from authoritative raw evidence. There is no recursive compiled-state mutation, incremental patching, verifier/repair layer, or fallback retrieval in E012.

## Frozen prompts and model

- model: `gpt-5.6-luna` only;
- E011 generic compiler prompt reused unchanged;
- E011 shared answer prompt/contract reused unchanged;
- compiler never receives future questions or answer keys;
- GitHub Actions Copilot JSONL transport extracts only the final `assistant.message.data.content` payload;
- no post-result serialization repair and no semantic rerolls.

## Frozen call plan

- build order seed: `20260818`;
- answer order seed: `20260819`;
- 36 compilation builds = 12 topics x 3 waves;
- 216 logical answer tasks = 12 topics x 3 waves x 3 query classes x 2 conditions;
- one separate fictional preflight may run before scored corpus calls;
- exact duplicate prompts, if any, reuse one actual model response rather than rerolling.

## Frozen quality outcomes

Report separately:

- strict answer pass;
- required signal coverage;
- required source-ID coverage;
- answer-contract invalid count;
- deterministic stale-current substitution count;
- compiled-state signal/provenance preservation;
- stale compiled-state count;
- invented source IDs;
- compiled/raw byte ratio.

No weighted winner score and no LLM-as-judge primary metric.

## Frozen maintenance economics

Primary axis: **revisits per update**.

Reuse regimes:

- `N=1`
- `N=3`
- `N=6`
- `N=10`
- `N=20`

The N regimes are replayed analytically from measured build/query costs. Identical queries are not physically repeated N times.

Report aggregate and per-topic finite break-even only when raw query cost exceeds compiled query cost. A token break-even cannot be called a value win when C0 quality is materially worse than R1.

## Frozen statistics

- independent cluster: topic (`n=12`);
- wave, condition, and query class are paired within topic;
- headline C0-R1 quality differences use topic-cluster paired bootstrap;
- bootstrap seed: `20260820`;
- bootstrap draws: `20000`;
- wave/class cells are secondary diagnostics;
- 108 rows/condition are not treated as 108 independent samples.

## Frozen budget

- per-call Copilot AI-credit cap: 30;
- cumulative estimated E012 guard: 400 AI credits;
- the guard is an infrastructure stop, not a target or adaptive sample-size rule;
- no topic/wave/query may be dropped to save credits after scoring starts.

## Stop / narrow rule

If C0 loses meaningful quality after updates, do not repair the benchmark or introduce a better compiler inside E012.

If C0 quality remains comparable but full-rebuild break-even exceeds a plausible revisit/update range, narrow durable compilation rather than adding maintenance machinery by default.

If a plausible region survives, the next evidence requirement is realistic/shadow calibration of actual revisit/update distributions before detailed representation or autonomous maintenance work.

## No-change rule after scoring starts

Do not change based on E012 outputs:

- corpus generator or update semantics;
- ground truth, required/forbidden signals, or query wording;
- R1/C0 condition definitions;
- compiler or answer prompts;
- model;
- build/answer seeds;
- scoring semantics;
- stale-current definition;
- N=1/3/6/10/20 regimes;
- bootstrap unit/seed/draw count;
- primary C0-R1 interpretation rule;
- budget by reducing the scientific sample.

Infrastructure-only defects may receive explicit amendments that preserve all completed artifacts. New semantic ideas become later experiments.

## Evidence grade

E012 can produce controlled maintenance-mechanism/economics evidence only. It cannot establish realistic usage frequency, human utility, production safety, or cross-model generality.
