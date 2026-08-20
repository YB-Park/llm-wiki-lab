# E023 G2 — fixed-identity persistence execution addendum v0

Status: **FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL**  
Preregistration: PR #197 -> `080ac3d91d011be3ec16111bdc24eda9905f3d9c`  
Tracking: Issue #160

## Purpose

G2 tests one narrow persistence-value hypothesis after G1 closure:

> **With fixed subject identity, terminal authority, answer composer, and the query-time comparator held constant, does a rebuildable persisted DERIVED retrieval projection improve repeated-use semantic quality/evidence efficiency enough to justify maintenance and stale-state risk?**

This addendum freezes execution mechanics only. It does not authorize product persistence or G3 identity/routing.

## Frozen execution

- prereg merge base: `080ac3d91d011be3ec16111bdc24eda9905f3d9c`;
- exact model: `gpt-5.6-luna`;
- query pairs: **12**;
- Q composer calls: **12**;
- P composer calls: **12**;
- projection build/rebuild calls: **5**;
- exact/max semantic attempts: **29**;
- planner calls: **0**;
- selector calls: **0**;
- vector calls: **0**;
- rerolls: **0**;
- max AI credits per call: **30**.

The frozen final answer composer in both arms is `run_g1c.py::composer_prompt`, with only `Axxx` -> `Pxxx` handle wording adaptation.

## Arm Q

For every query event:

1. use the prospectively supplied subject/state;
2. recompute the current active terminal-authority snapshot and verify its preregistered SHA;
3. recompute subject-scoped exact BM25;
4. require exact agreement with `persistence-comparison-v0/control-contexts.json` top-6 IDs and context SHA;
5. answer once with the frozen old composer.

A Q mismatch stops the run before using that corrupted context and prevents execution completion.

## Projection build/rebuild

At each of the five frozen lifecycle build events:

1. render **all current terminal authority** for the already fixed subject;
2. verify the lifecycle snapshot SHA;
3. make exactly one `projection_prompt_v0` model call;
4. preserve raw model text;
5. parse exactly one projection contract.

Parsed projection requirements:

- JSON exactly `{ "entries": [...] }`;
- 4–12 entries;
- sequential `E01`, `E02`, ... IDs;
- each entry has exactly `entry_id`, `statement`, `anchor_ids`;
- statement is non-empty and <=320 characters;
- 1–4 unique supplied Pxxx anchor IDs per entry;
- every supplied current terminal anchor is referenced by at least one entry.

No compiler retry or reroll is allowed.

A failed compiler slot is retained as execution evidence. The corresponding projection becomes unavailable and later P queries fail closed to Q retrieval, but the overall experiment cannot be marked complete/earned.

## Persistent retrieval and authority boundary

The persisted projection is `DERIVED / NONCANONICAL` retrieval state only.

For a fresh projection:

1. BM25 ranks projection **statement** text against the user query;
2. top 2 positive projection entries are taken;
3. their terminal Pxxx handles are de-duplicated in entry order;
4. the same current raw-authority BM25 ranking fills until at least 4 terminal anchors are selected;
5. final terminal anchor count is capped at 6;
6. zero positive projection scores falls back exactly to Q top-6.

The final composer sees **only full terminal authority objects**. Projection statements are never composer context, citations, or terminal authority.

## Freshness / stale-state guard

Before each P query, recompute the complete current subject snapshot SHA.

If it differs from the stored projection source snapshot:

> **STALE_PROJECTION_BYPASS**

Then:

- do not rank or inspect projection statements;
- select exactly the Q top-6 terminal anchors;
- record the stale/current snapshot hashes;
- answer using the same terminal context as Q.

This is prospectively required at PQ007 and PQ011.

PQ011 is the primary stale negative control: the S0 projection can contain the old 30-day Keystone state while S1 terminal authority makes 90 days current. Any use of that stale projection for retrieval or a stale/current inversion is disqualifying.

## Frozen lifecycle and call order

Lifecycle order remains exactly the merged preregistration order:

1. Iris S0 projection build;
2. PQ001–PQ004;
3. Juniper S0 build;
4. PQ005–PQ006;
5. Juniper S0->S1 authority mutation;
6. PQ007 stale bypass;
7. Juniper S1 rebuild;
8. PQ008;
9. Keystone S0 build;
10. PQ009–PQ010;
11. Keystone S0->S1 correction/supersession mutation;
12. PQ011 stale bypass;
13. Keystone S1 rebuild;
14. PQ012.

Q/P composer ordering is counterbalanced by question: odd PQ numbers use Q then P; even PQ numbers use P then Q.

There is no randomization after execution starts.

## Failure discipline

`result.json` is persisted before the first model call and after every model-call attempt.

Each scheduled projection or composer slot receives at most one model attempt. No hidden retries/rerolls occur after transport, parse, or output-contract failure.

The runner continues through the frozen lifecycle after individual model-slot failure when doing so is deterministic and safe, so failures cannot selectively remove later scheduled comparisons. All failures remain immutable evidence and prevent `execution_complete=true`.

Raw model text is preserved whenever transport succeeds, including malformed JSON/output cases.

`execution_complete=true` requires all:

- exactly 29 model attempts;
- all five projection build/rebuild contracts valid;
- all 24 composer contracts valid;
- every Q context matches the preregistered frozen control;
- PQ007 and PQ011 record exact `STALE_PROJECTION_BYPASS` with P selected anchors identical to Q;
- no projection statement enters any composer input;
- exact model is preserved by transport.

Complete execution ends only as `PENDING_FROZEN_ADJUDICATION`.

## Runtime information boundary

Projection compiler receives only:

- fixed subject ID;
- all current terminal authority objects for that subject snapshot.

It receives no user question, future query, evaluation clause, expected status, expected answer, opportunity ID, stale-control label, promotion criterion, or adjudication.

Final composer receives only:

- user question;
- selected full terminal authority objects.

The runner may compute zero-model evaluator status for evidence capture, but neither compiler nor composer prompt may receive evaluator clauses/statuses.

## One-shot merge boundary

The execution PR itself performs **0 semantic/model calls**.

Semantic execution is authorized only on a `push` to `main` changing this execution contract whose `github.event.before` equals the exact preregistration merge SHA:

`080ac3d91d011be3ec16111bdc24eda9905f3d9c`

Therefore this execution contract must be the next main change after PR #197. If main moves first, semantic execution must skip fail-closed; create a fresh execution contract from the new main instead of widening the condition.

The execution workflow uploads the raw result and commits an immutable evidence directory:

- `result.json`;
- `result.sha256`;
- `source.json`.

The evidence commit does not retrigger semantic execution.

## Frozen adjudication boundary

The runner does not self-promote G2.

A later result PR must apply the already-merged `g2-evaluation-contract-v0.json` exactly, including:

- fresh context improvements on **both PQ004 and PQ008**;
- zero fresh authority regressions elsewhere;
- exact stale bypass at PQ007/PQ011;
- PQ011 no stale/current inversion/critical error;
- PQ012 PASS;
- P >= **10/12 PASS**;
- >= **2 paired semantic improvements**;
- 0 semantic regressions;
- 0 new critical errors;
- 0 stale/unsupported load-bearing claims;
- terminal citation support;
- fresh-query P raw evidence chars <= **85%** of Q;
- exactly 5 compiler calls and no query-time compiler call.

Do not weaken thresholds after outputs exist.

## Project boundary

Even an earned G2 research result does not automatically authorize:

- Dogfood persistent semantic state;
- graph/entity/KnowledgeUnit storage;
- automatic identity merge/split/routing;
- vector defaults;
- product top-6 policy;
- G3.

Natural installed product evidence on Issue #141 continues independently.
