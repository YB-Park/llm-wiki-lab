# E023 G1f — authority-preserving composition comparison preregistration

Status: **PREREGISTRATION / ZERO-MODEL ONLY / NO SEMANTIC EXECUTION AUTHORIZED BY THIS PR**  
Tracking: Issue #160  
Baseline: composition contract v0 from PR #191; handoff checkpoint from PR #192

## Research question

G1e established exact BM25 with a modestly larger evidence prefix as the current strong simple **experimental** retrieval baseline, but G1e did not earn strict promotion and did not make top-6 a product default. Its remaining B6 failures were composition-side.

G1f therefore asks one causal question:

> **When the user question and exact selected evidence context are held identical, does the frozen authority-preserving composition contract improve epistemic-type preservation and proposition-scoped sufficiency over the frozen old composer on new separated material?**

This preregistration changes composition only. It does not tune retrieval.

## Frozen prospective material

Directory: `composition-comparison-v0/`

The package contains:

- **49 new anchors** with IDs `D001`–`D049`;
- **8 new questions** with IDs `DQ001`–`DQ008`;
- 47 `RAW_MEMORY` anchors;
- 2 load-bearing `HUMAN_KNOWLEDGE` anchors;
- no AQ/BQ/CQ question reuse;
- no prior anchor IDs;
- no exact prior anchor/question text;
- no model answers, semantic verdicts, adjudication, or gold answer text.

Coverage is intentionally mechanism-oriented rather than frequency-estimating. It includes:

1. user-owned decision/rationale authority;
2. direct versus attributed evidence;
3. a missing identity bridge;
4. governing customer policy versus vendor capability;
5. proposition-scoped `could satisfy` sufficiency;
6. temporal hypothesis -> causal signal -> final assessment -> limited correction;
7. explicit negative characterization boundaries;
8. repeated support requiring two independent observations;
9. an explicit project rename bridge with a similarly named distractor.

## Frozen retrieval/context contract

For every `DQxxx` question:

1. use the exact question text;
2. use the existing `g1d_common.bm25_ranking` whole-object BM25 implementation;
3. select the exact ranked top **6** anchors;
4. render the selected anchors once in the existing full evidence-object shape;
5. compute one frozen context SHA-256;
6. feed that **same byte-identical question and context** to both composition arms.

There is no arm-specific retrieval, no planner, no query rewrite, no selector, no RRF, no vector search, and no evaluator-aware retrieval.

`composition-comparison-v0/context-freeze.json` is the single source of truth for selected IDs and context hashes. The future execution contract must consume one context object per question and pass that same object to O and N; it must not independently reconstruct or retrieve per arm.

Exact BM25 top-6 is used only because it is the current strong simple experimental baseline. **This preregistration does not authorize a top-6 product default.**

## Frozen composition arms

### O — old composer

Source: `run_g1c.py::composer_prompt` as frozen on current main.

The only permitted adapter in a later execution runner is replacing the output-ID wording `Axxx` with `Dxxx` so that the frozen output-format instruction matches the new anchor namespace. No semantic instruction may be added, removed, or rewritten.

### N — contract-v0 composer

Source: `composition_prompt_v1.py::composer_prompt_v1` as frozen by PR #191.

No DQ-specific rule, evaluator clause, expected answer, expected insufficiency bit, verdict, or promotion threshold may enter this prompt.

Both arms must see the exact same user question and exact same evidence context.

## Prospective authority-incomplete negative control

`DQ003` is deliberately frozen as an authority-incomplete control.

The corpus contains the explicit identity bridge `D019`, but exact BM25 ranks it **7th** for DQ003. The shared top-6 context therefore contains approval by abbreviated `J. Moreno` plus same-surname/full-name distractors, but it does **not** contain authority that bridges `J. Moreno -> Julia Moreno`.

The prospective expected context status is `INSUFFICIENT_AUTHORITY` because the user asks both whether J. Moreno approved the exception and whether J. Moreno is Julia Moreno.

A successful composer may answer the supported approval part, but must not synthesize the identity bridge and must set `insufficient_authority=true` for the requested answer as a whole.

Do not move D019 into top-6 after semantic outputs exist. Doing so would invalidate this experiment identity.

## Evaluation contract

File: `g1f-evaluation-contract-v0.json`

Evaluation is separate from runtime prompt information. The composer may not see this file.

Semantic adjudication is proposition-scoped:

- `PASS`: requested load-bearing propositions are supported or explicitly bounded as unsupported; required epistemic distinctions and citations are correct;
- `PARTIAL`: no load-bearing unsupported claim, but a non-critical preservation/calibration requirement is missed;
- `CRITICAL_ERROR`: unsupported load-bearing claim, synthesized required bridge, false sufficiency on authority-incomplete context, false direct authorship, or a citation claimed to support a relation it does not establish.

The evaluation contract prospectively fixes question-level checks for user-owned authority, direct/attributed semantics, missing bridge restraint, policy/capability, proposition scope, temporal correction, negative characterization, repeated support, explicit identity bridges, and citation support.

## Frozen G1f promotion rule

`G1F_COMPOSITION_CANDIDATE_EARNED` requires **all** of the following after a separately preregistered execution and adjudication:

1. N reaches at least **7 / 8 PASS**;
2. N produces at least **1 paired semantic improvement** versus O;
3. N produces **0 paired semantic regressions** versus O;
4. N produces **0 new CRITICAL_ERROR** versus O;
5. the prospective DQ003 authority-incomplete negative control is **PASS**;
6. the DQ004 proposition-scoped sufficiency case is **PASS**;
7. both DQ001 and DQ007 preserve load-bearing user-owned authority;
8. every N load-bearing citation is supported by the supplied frozen context;
9. the later execution record proves O/N used the same exact model and one byte-identical frozen context per question.

Do not weaken these thresholds after semantic outputs exist.

Even an earned result is only a G1 composition-candidate signal. It does not by itself authorize G2 or product translation.

## Zero-model validator / CI gate

`validate_g1f_prereg.py` and `.github/workflows/validate-e023-g1f-prereg.yml` must pass before review/merge.

The validator proves:

- 49/8 prospective material shape and allowed terminal authority types;
- exact ID and text separation from authority-sufficiency v0/v1/v2 and AQ/BQ/CQ questions;
- deterministic exact-BM25 top-6 selected IDs and frozen context SHA-256 values;
- a single context source per question, shared by O/N;
- DQ003 is the sole prospective authority-incomplete negative control and has `D019` at rank 7;
- all other frozen contexts are authority-sufficient;
- required coverage classes are present;
- the old composer, new composer, and contract-v0 source blobs remain frozen;
- neither composer prompt contains DQ/D material, project names, evaluator clauses, expected insufficiency values, semantic verdicts, or promotion thresholds;
- no model answer/adjudication exists in the new prospective package;
- `semantic_calls_authorized_on_this_pr=false`;
- no G1f runner, remote execution request, or semantic execution workflow exists on this prereg branch.

The validator itself performs **0 model calls**.

## Execution boundary

This PR does **not** design or authorize semantic execution.

Only after this preregistration is merged may a **fresh execution branch from the prereg merge SHA** freeze:

- the exact model;
- paired call ordering;
- exact call budget;
- zero-reroll/failure-safe policy;
- transport/request metadata;
- result capture;
- execution CI;
- adjudication procedure tied to this already-frozen evaluation contract.

Until then, semantic calls remain **0**.

Do not semantically rerun AQxxx, BQxxx, or CQxxx.

## Architecture/product boundary

G1f remains inside G1 Retrieval / Composition and does not authorize:

- exact BM25 top-6 as a product default;
- G2 persistence;
- graph/entity/Relation/KnowledgeUnit storage;
- automatic identity merge/split or routing;
- vector retrieval defaults;
- evaluator clauses as runtime canonical structure;
- Dogfood runtime changes.
