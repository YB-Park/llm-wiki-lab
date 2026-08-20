# E023 G1c-R1 — zero-model selection counterfactual

Status: **POSTHOC / ZERO MODEL / NON-PRIMARY / DOES NOT CHANGE FROZEN R1 VERDICT**  
Source run: `32232116273`  
Frozen R1 verdict: `NOT_EARNED`

## Question

After G1c-R1 showed that the evidence-follow candidate pool contained sufficient positive load-bearing authority for all six questions but the final model selector reduced two questions to insufficient contexts, is there a simple evaluator-blind deterministic selection rule that preserves the recovered authority better?

This analysis uses only already-frozen retrieval rankings, candidate membership, and the already-frozen prospective authority-sufficiency evaluator. It performs **zero model calls** and does not rerun or rewrite any semantic answer.

## Boundary

The selection policy must not inspect:

- authority-sufficiency clauses;
- expected answers;
- frozen semantic verdicts;
- forbidden-conflation labels;
- anchor IDs as hand-written special cases.

The evaluator is used **after selection only** to score the resulting context.

This is therefore a posthoc mechanism diagnostic, not a promoted runtime policy.

## Policies compared

Reference conditions:

1. initial exact-query top-5;
2. the frozen Luna final selector from G1c-R1;
3. the complete frozen candidate pool.

Counterfactual policy:

> Fuse the exact-query ranking and the two frozen evidence-follow rankings with deterministic Reciprocal Rank Fusion, restrict to the already-frozen candidate pool, then take a fixed evidence budget.

No LLM selector is used.

We test budgets 3, 4, and 5 and sweep RRF `k` over `1, 5, 10, 20, 40, 60, 100, 200, 1000`.

## Result

The important frozen-context result is:

- initial top-5: **4 clean / 1 conflation-risk / 1 insufficient**;
- frozen model selector: **4 clean / 0 risk / 2 insufficient**;
- candidate pools: **0 insufficient**;
- deterministic RRF top-4: **6 clean / 0 risk / 0 insufficient**.

The top-4 result remains 6/6 `SUFFICIENT_CLEAN` for every tested RRF `k` value.

Mechanistically:

- AQ001: RRF top-4 preserves recovered identity bridge `A003` and excludes same-name distractor `A004`;
- AQ002: it preserves the direct-author / attribution / identity set while excluding `A004`;
- AQ004: it retains the early hypothesis, retry signal, and final postmortem instead of over-compressing to the postmortem alone;
- the other three questions remain authority-sufficient.

Budget matters. Top-3 becomes insufficient on at least one question; top-5 retains conflation risk on at least one question. The frozen slice therefore contains a real **selection/evidence-budget frontier**, not simply a monotonic “more sources is safer” relationship.

## Interpretation

The strongest controlled signal is now narrower than “use smarter retrieval”:

> **Evidence-follow discovery can recover the needed authority, but final selection must preserve load-bearing relations and manage distractor exposure. A simple rank-fusion budget can outperform a free-form model selector on this frozen slice.**

This does **not** establish RRF top-4 as a product rule. It was selected after inspecting the frozen R1 failure, and the current six-question slice is no longer held out for mechanism choice.

The correct next experiment, if pursued, is a prospectively frozen **new separated slice** where the deterministic selection policy is fixed before any semantic answers or outcome inspection.

A useful next G1 candidate is:

> exact-query BM25 -> evidence-aware planner -> targeted BM25 -> deterministic multi-query RRF -> fixed evidence budget -> composer

This candidate removes the model selector call entirely. It should be tested against a strong exact-query baseline on new material, with authority sufficiency and semantic answer quality scored separately.

## What this does not authorize

- no semantic rerun on the current authority-sufficiency-v0 slice;
- no retroactive change to G1c-R1 `NOT_EARNED`;
- no G2 persistence;
- no graph/entity/KnowledgeUnit storage;
- no automatic identity merge/split;
- no vector default;
- no product runtime change.

Run:

```bash
python3 experiments/E023-generality-retrieval-composition/analyze_g1c_r1_selection_counterfactual.py
```

Expected first line:

```text
E023 G1c-R1 zero-model selection counterfactual: PASS
```
