# E023 G1f — authority-preserving composition execution addendum v0

Status: **FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL**  
Preregistration: PR #192  
Frozen composition contract: PR #191 / `composition_prompt_v1.py`

## Frozen comparison

G1f holds retrieval and evidence bytes fixed and changes only composer instructions.

For each DQ001–DQ008:

1. exact E023 whole-object BM25;
2. exact top-6 evidence, frozen identically for both arms;
3. no planner, query rewrite, RRF, selector, or context reranking.

Arms:

- **O:** old G1c/G1d/G1e composer prompt;
- **N:** frozen `composition_prompt_v1.py` authority-preserving composer.

Exact execution:

- model: `gpt-5.6-luna`;
- O composer calls: **8**;
- N composer calls: **8**;
- total semantic attempts: **16**;
- planner calls: **0**;
- selector calls: **0**;
- rerolls: **0**.

Both arms receive the same evidence order, full evidence text, authority type, title, kind, date, and stable Dxxx handles. Neither receives evaluator clauses, expected answers, semantic verdicts, fixture labels, or promotion thresholds.

## Frozen context preflight

Before any semantic call the runner must re-establish the merged preregistration context gate:

- seven questions have positive-authority-sufficient exact top-6 contexts;
- DQ004 is `INSUFFICIENT_AUTHORITY` with only `identity_bridge` missing;
- D017 is outside DQ004 top-6;
- DQ004 still contains at least two repeated S. Lee requirement records.

Any mismatch stops before model execution.

## Failure discipline

Persist `result.json` before the first call and after every O/N composer attempt. No rerolls or hidden semantic retries are allowed after parser/model/contract failure. Partial outputs remain frozen execution evidence but cannot earn G1f.

## One-shot workflow boundary

The PR event runs zero-model preflight only. The semantic job is permitted only on the unique main squash commit whose message begins:

`Freeze E023 G1f execution contract`

The workflow path filter is limited to the G1f execution assets. Immediately after the run is captured, the result PR must replace this commit-message gate with the exact used execution SHA so later edits cannot rerun the experiment.

## Promotion boundary

The runner records `PENDING_FROZEN_ADJUDICATION` after a complete 16-call execution; it does not self-promote.

Final promotion remains exactly the preregistered rule:

- N >=7/8 PASS;
- >=2 semantic improvements vs O;
- 0 semantic regressions;
- 0 new critical errors;
- DQ004 N reports insufficiency and does not assert an unsupported full-name identity;
- prospectively sufficient N contexts are not marked insufficient unless adjudication finds an actually unsupported load-bearing part of the question;
- user-owned authority semantics are preserved on DQ001 and DQ008;
- exact 16 calls, zero rerolls.

Even an earned result would promote only the query-time composer-contract hypothesis. It would not authorize a product prompt rollout, top-6 product default, G2, or G3.
