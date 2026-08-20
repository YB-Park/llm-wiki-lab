# E023 G1e — semantic execution addendum v0

Status: **FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL**  
Preregistration + passed Phase 0: PR #187 -> `c674f93728db7d4fe0d8b84328feca34b87fd655`

## Frozen semantic comparison

Phase 0 prospectively established on the separated v2 slice:

- A5 exact BM25 top-5: 2 clean / 4 risk / 2 insufficient;
- B6 exact BM25 top-6: 3 clean / 5 risk / 0 insufficient;
- B6 authority improvements: 2;
- B6 authority regressions: 0;
- model calls used for Phase 0: 0.

Phase 1 tests semantic safety/value only.

Exact execution:

- model: `gpt-5.6-luna`;
- questions: CQ001–CQ008 only;
- A5: exact BM25 top-5 -> unchanged authority-preserving composer;
- B6: the same exact BM25 ranking top-6 -> the same composer;
- planner calls: **0**;
- selector calls: **0**;
- A5 composer calls: **8**;
- B6 composer calls: **8**;
- exact/max semantic attempts: **16**;
- rerolls: **0**.

The G1c/G1d composer semantic instructions are reused. The only mechanical syntax adaptation is the frozen evidence handle from `Axxx` to `Cxxx`.

## Frozen evidence contexts

The runner must assert the exact deterministic A5 and B6 prefixes produced by the already-merged v2 Phase 0 corpus before a model call is attempted.

Retrieval, ranking, context membership, authority status, and evidence-character counts are zero-model deterministic inputs. The model receives no evaluator clause, expected status, expected answer, semantic verdict, or promotion threshold.

## Failure discipline

Persist `result.json`:

1. before the first semantic call;
2. after each A5 composer attempt;
3. after each B6 composer attempt;
4. after final execution-complete bookkeeping.

No rerolls or hidden model retries are allowed after a parser/model/contract failure. Partial outputs remain execution evidence but cannot earn G1e.

## One-shot workflow boundary

This execution PR is based exactly on Phase-0 merge `c674f93728db7d4fe0d8b84328feca34b87fd655`.

The PR event runs zero-model preflight only. Semantic execution is permitted only on a `main` push whose `github.event.before` equals that exact Phase-0 merge. If main moves before merge, do not widen the trigger; refresh the execution contract from the new base instead.

The workflow uploads immutable raw result evidence and commits its SHA-256/source identity even if execution fails. Final completed run metadata and semantic adjudication belong in a later result PR.

## Promotion boundary

The runner does not self-promote G1e semantically. It records `PENDING_FROZEN_ADJUDICATION` after a complete 16-call run.

Final promotion remains the preregistered rule:

- B6 >=7/8 PASS;
- >=1 semantic improvement vs A5;
- 0 semantic regressions;
- 0 new critical errors;
- no load-bearing unsupported B6 claim;
- exact 16 calls, zero rerolls.

Even an earned G1e result would be a query-time evidence-budget mechanism signal, **not** a hard-coded top-6 product policy and not authorization for G2/G3.
