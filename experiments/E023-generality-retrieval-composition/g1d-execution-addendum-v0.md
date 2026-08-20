# E023 G1d — execution addendum v0

Status: **FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL**  
Preregistration: `g1d-preregistration-v0.md` merged at `b0042a87cf871070b334a6c5bef79f390b5a6434`

## Exact execution

- model: `gpt-5.6-luna`;
- questions: BQ001–BQ008 only;
- A: exact-question BM25 top-5 -> composer;
- D: exact top-5 -> evidence-aware planner -> up to two targeted BM25 queries -> candidate union -> deterministic RRF `k=60` -> top-4 -> composer;
- model selector calls: **0**;
- A composer calls: **8**;
- D planner calls: **8**;
- D composer calls: **8**;
- exact/max semantic attempts: **24**;
- rerolls: **0**.

The G1c planner and composer **semantic instructions** are reused. The only prompt/parser adaptation is mechanical anchor-handle syntax from the prior `Axxx` slice to this slice's frozen `Bxxx` identifiers. No new identity, policy, project, or domain-specific semantic rule is added.

## Deterministic selection

The selection implementation is the already-merged `g1d_common.py`:

- candidate membership comes only from initial top-5 plus follow-up top-3 retrieval hits;
- RRF uses exact-query and all planner follow-up rankings;
- `k=60`;
- final budget `4`;
- tie break: higher fused score -> better initial exact-query rank -> lexicographically smaller anchor ID;
- authority clauses, expected answers, semantic verdicts, and forbidden-conflation labels are unavailable to selection.

## Failure discipline

The runner must persist `result.json`:

1. before any semantic call;
2. after every A composer attempt;
3. after every D planner attempt;
4. after deterministic candidate/RRF selection;
5. after every D composer attempt;
6. after final aggregate selection verdict.

No reroll or hidden retry is allowed after a contract/parser/model failure. Partial evidence remains valid execution evidence but does not earn the gate.

## One-shot workflow boundary

This execution PR is based exactly on `main@b0042a87cf871070b334a6c5bef79f390b5a6434`.

The PR event runs **zero-model preflight only**. The semantic execute job is allowed only on a `main` push whose `github.event.before` equals that exact preregistration commit. This makes the first merge from the frozen preregistration base the only eligible execution transition. If `main` moves before merge, the contract must be refreshed rather than silently widening the trigger.

The workflow captures immutable `result.json` evidence and its SHA-256. Final completed workflow metadata may be added in the closeout/result PR after the run finishes; do not rerun merely to improve metadata.

## Interpretation boundary

Even an `EARNED_PENDING_SEMANTIC_SAFETY` retrieval-selection result does not itself promote G1d. Frozen semantic adjudication must still confirm no new critical error and no load-bearing unsupported claim.

No outcome authorizes G2 persistence, entity/graph/KnowledgeUnit storage, vector defaults, automatic identity/routing, or Dogfood runtime changes.
