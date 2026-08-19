# E023 G1c v0 execution failure record

Status: **INVALID_EXECUTION / NO G1c RETRIEVAL VERDICT / DO NOT ADJUDICATE AS A COMPLETED COMPARISON**.

Frozen execution source: `987ee7ec615f7eb869be59f14a1928a3811baeed`  
Run: `32229563330`  
Exact model: `gpt-5.6-luna`

## What happened

The G1c runner completed all six A-arm composer calls, then entered the B evidence-follow loop. After the first B question had completed its planner/selector/composer path, the runner called `retrieval_verdict(result)` before persisting that B row. The verdict helper assumed all baseline-clean B questions already existed and indexed `AQ004`, raising `KeyError('AQ004')` during the first incremental B iteration.

The workflow therefore failed before a complete B arm existed. The raw artifact contains:

- all six frozen A contexts and composer outputs;
- `B: []` because the first B row was not saved before the crashing verdict call;
- persisted `model_call_attempts: 6`, which is stale because the result file was last saved before entering B.

Control flow plus the failure location establish that the first B planner, selector, and composer calls had completed before the exception. Therefore **nine semantic call attempts occurred in v0: six A + three first-question B calls**. The three B outputs are not recoverable from the persisted artifact and must not be reconstructed or guessed.

## Why this is not a G1c result

The preregistered primary comparison requires final B authority status across all six questions. No complete B evidence exists. Therefore:

- `retrieval_selection_verdict = NOT_EXECUTED` is the only valid experiment-level interpretation;
- no `EARNED`, `TARGETED_SIGNAL_ONLY`, or `NOT_EARNED` semantic/retrieval conclusion may be drawn from v0;
- the A outputs may remain immutable auxiliary evidence but do not authorize any architecture change;
- the lost first-B output must not be silently rerolled and treated as if it were the original run.

## Recovery discipline

A recovery replication may be separately preregistered because the failure is an implementation/evidence-persistence defect, not an observed B outcome.

The recovery must:

1. keep the G1c corpus, evaluator, B planner/selector/composer prompts, BM25 mechanics, top-k limits, and promotion rules unchanged;
2. **not rerun A**;
3. run a new B-only evidence identity across all six questions;
4. treat that B-only execution as `G1c-R1`, not continuation of v0;
5. use a maximum of 18 semantic calls (6 planner + 6 selector + 6 composer), zero rerolls inside R1;
6. persist each B stage before any aggregate verdict computation so a later failure cannot erase completed evidence;
7. compute the aggregate verdict only after all six B rows exist;
8. retain v0 and R1 as separate immutable evidence.

No recovery outcome directly authorizes G2 persistence, entity/graph storage, automatic identity/routing, or product runtime changes.
