# E023 G1f — composition comparison execution addendum v0

Status: **FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL**  
Preregistration: PR #193 -> `1e5a3f991d0c3b76552725933149702ff6e53d15`  
Tracking: Issue #160

## Purpose

G1f preregistered a composition-only paired comparison on new separated DQ material. This addendum freezes the semantic execution mechanics only after that preregistration has merged.

The causal question remains unchanged:

> When the user question and selected evidence context are identical, does the frozen authority-preserving composition contract improve epistemic-type preservation and proposition-scoped sufficiency over the frozen old composer?

No retrieval tuning, evaluator-aware runtime behavior, persistence, identity routing, or product policy is introduced here.

## Frozen execution

Exact execution:

- prereg merge base: `1e5a3f991d0c3b76552725933149702ff6e53d15`;
- exact model: `gpt-5.6-luna`;
- questions: `DQ001`–`DQ008` only;
- arm O: frozen `run_g1c.py::composer_prompt`, with only `Axxx` -> `Dxxx` output-ID wording adaptation;
- arm N: frozen `composition_prompt_v1.py::composer_prompt_v1`;
- O composer calls: **8**;
- N composer calls: **8**;
- exact/max semantic attempts: **16**;
- planner calls: **0**;
- selector calls: **0**;
- retrieval model calls: **0**;
- rerolls: **0**;
- max AI credits per call: **30**.

The model is held at Luna because G1f is intended to isolate the composer contract change from model-family change and preserve comparability with the immediately preceding G1 evidence.

## Frozen shared-context rule

`composition-comparison-v0/context-freeze.json` is the sole selected-context authority for execution.

For each DQ question the runner:

1. loads the preregistered selected six anchor IDs;
2. renders the full evidence context exactly once using the already-frozen evidence-object format;
3. verifies the preregistered context character count and SHA-256;
4. stores that one rendered context object in memory;
5. passes the same question string and same rendered context to O and N.

The execution runner does **not** call BM25, planner, selector, RRF, vector retrieval, evaluator clauses, or any arm-specific retrieval function.

If any context hash differs from the preregistered value, execution stops before the first model call.

## Frozen paired call ordering

Calls are interleaved by question and counterbalanced so one arm is not systematically earlier in the run:

| question | first | second |
| --- | --- | --- |
| DQ001 | O | N |
| DQ002 | N | O |
| DQ003 | O | N |
| DQ004 | N | O |
| DQ005 | O | N |
| DQ006 | N | O |
| DQ007 | O | N |
| DQ008 | N | O |

This yields exactly eight O calls and eight N calls. There is no randomization after execution starts.

## Failure discipline

`result.json` is persisted:

1. before the first semantic attempt;
2. after every scheduled call attempt;
3. after final execution-complete bookkeeping.

Every scheduled slot gets at most one model attempt. There are no hidden retries or rerolls after transport, parser, or output-contract failure.

The runner continues through the frozen schedule after an individual slot failure so failure handling cannot selectively change which later arm/question receives an attempt. A failed or malformed slot remains immutable execution evidence and prevents execution from being marked complete.

Raw model text is preserved alongside parsed output when transport succeeds, including when JSON/output-contract parsing fails. This synthetic experiment contains no private user source data.

`execution_complete=true` requires all of:

- exactly 16 attempted model calls;
- every scheduled O/N slot returns the frozen output shape;
- every citation is unique and within that question's supplied D-context;
- both arms record the preregistered context SHA for every question.

Incomplete execution cannot earn G1f.

## Runtime information boundary

The composer receives only:

- the exact user question;
- the six full supplied evidence objects and their authority/provenance fields;
- stable Dxxx evidence handles.

The runner does not load `g1f-evaluation-contract-v0.json` or `composition-comparison-v0/authority-contract.json` into either prompt path.

The model must not receive expected answers, expected insufficiency values, semantic verdicts, promotion thresholds, DQ-specific evaluator checks, or hidden reasoning requirements.

## One-shot merge boundary

The execution PR itself performs **0 semantic/model calls**.

Semantic execution is authorized only by a `push` to `main` that changes these execution-contract files **and** whose `github.event.before` equals the exact preregistration merge SHA:

`1e5a3f991d0c3b76552725933149702ff6e53d15`

Therefore the execution contract must be the next main change after PR #193. If main moves first, the semantic job must remain skipped; do not widen the condition. Rebase/re-freeze a fresh execution contract instead.

The execution workflow uploads raw result evidence and, even on incomplete execution, commits an immutable evidence directory containing:

- `result.json`;
- `result.sha256`;
- `source.json` with workflow run ID and execution source SHA.

The evidence commit itself does not touch execution workflow paths and must not trigger a second semantic run.

## Adjudication boundary

The runner does not self-adjudicate semantic PASS/PARTIAL/CRITICAL_ERROR and does not self-promote G1f.

A complete execution ends as `PENDING_FROZEN_ADJUDICATION`. A later result/adjudication change must apply the already-merged `g1f-evaluation-contract-v0.json` without changing its thresholds.

Frozen G1f candidate promotion still requires all preregistered conditions, including:

- N >= **7 / 8 PASS**;
- >= **1** paired semantic improvement vs O;
- **0** paired semantic regressions;
- **0** new N critical errors;
- DQ003 negative control PASS;
- DQ004 proposition-scoped sufficiency PASS;
- DQ001 and DQ007 user-owned-authority preservation PASS;
- every N load-bearing citation supported by the supplied context;
- proof of the same exact model and one byte-identical context per O/N pair.

Do not weaken the rule after outputs exist.

## Project boundary

Even if `G1F_COMPOSITION_CANDIDATE_EARNED` is earned:

- exact BM25 top-6 remains an experimental baseline, not a product default;
- G2 persistence is not automatically authorized;
- graph/entity/Relation/KnowledgeUnit storage is not authorized;
- automatic identity merge/split/routing is not authorized;
- vector retrieval defaults are not authorized;
- Dogfood runtime does not change in this execution contract.

After adjudication, the project should decide whether G1 as a whole is strong enough to justify any persistence gate. Natural installed dogfood on Issue #141 remains a parallel product-evidence track, and Issue #132 reliability edges remain evidence-gated rather than reasons to introduce a database/WAL architecture preemptively.
