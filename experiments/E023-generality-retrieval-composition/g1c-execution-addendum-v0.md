# E023 G1c execution addendum v0

Status before first G1c semantic call: **EXECUTION CONTRACT FROZEN / PR PATH ZERO MODEL / MAIN PUSH ONLY**.

This addendum implements the already-merged `g1c-preregistration-v0.md`. It may not change the causal question, six-question target set, authority-sufficiency evaluator, strict promotion rule, or non-conclusion boundaries.

## 1. Exact execution source

The executable contract is `run_g1c.py` plus `remote-lab/e023-g1c-request.json` and `.github/workflows/e023-generality-g1c.yml` as merged together.

The pull-request workflow path runs only zero-model preflight. The semantic `execute` job is gated to a push to `main` after this addendum merges.

## 2. Frozen request

```json
{
  "a_composer_calls": 6,
  "b_composer_calls": 6,
  "b_planner_calls": 6,
  "b_selector_calls": 6,
  "candidate_followup_top_k": 3,
  "final_anchor_limit": 5,
  "initial_top_k": 5,
  "max_ai_credits_per_call": 30,
  "max_followup_queries": 2,
  "max_model_call_attempts": 24,
  "model": "gpt-5.6-luna",
  "planner_snippet_chars": 320,
  "question_count": 6,
  "request_id": "e023-g1c-authority-sufficiency-evidence-follow-v0"
}
```

Any byte-level semantic change to this request stops the runner.

## 3. Arm A

For each `AQ001`–`AQ006`:

1. exact question;
2. the exact BM25 implementation frozen by `validate_g1c_prereg.py`;
3. exact top-5 must byte-for-byte match the preregistered IDs;
4. offline authority-sufficiency status is recorded but never shown to the model;
5. one composer call receives the five full authoritative anchors.

A uses exactly six semantic calls.

## 4. Arm B

For each question:

1. exact same top-5 initial context as A;
2. planner sees only question plus bounded candidate metadata/snippets and typed authority labels;
3. planner emits one non-empty missing/ambiguous relation plus 0–2 lexical follow-up queries;
4. follow-up queries use the same BM25, top-3 each;
5. selector sees only question, planner working state, and candidate metadata/snippets; it chooses 1–5 anchors;
6. offline evaluator records final authority status;
7. the same composer prompt/contract as A receives only the selected full anchors.

B uses exactly 18 semantic calls when every contract succeeds: six planner, six selector, six composer.

## 5. Model-facing information isolation

Planner, selector, and composer never receive:

- authority evaluator clauses;
- proposition IDs;
- expected statuses;
- reference contexts;
- required or forbidden anchor IDs;
- preregistered top-5 explanations;
- semantic gold/adjudication.

Anchor snippets/full text are explicitly labeled untrusted data.

Planner working state is explicitly not authority.

## 6. Typed authority contract

Model-facing metadata exposes only each candidate's actual `authority_type`.

- `RAW_MEMORY` = admitted external evidence.
- `HUMAN_KNOWLEDGE` = explicit user-owned project knowledge.
- `HUMAN_KNOWLEDGE` must not be presented as independently observed external evidence.
- no `DERIVED_MEMORY` is terminal authority in G1c.

The shared composer prompt requires this distinction in both arms.

## 7. Prompt/output contracts

Exact prompt bytes are frozen in `run_g1c.py`.

Planner output must be JSON with exactly:

- `missing_or_ambiguous_relation` — non-empty <=240 chars;
- `queries` — 0–2 unique non-empty strings <=160 chars, with no `Axxx` handles.

Selector output must be JSON with exactly:

- `selected_anchor_ids` — 1–5 unique candidate `Axxx` IDs.

Composer output must be JSON with exactly:

- `answer` — non-empty string;
- `cited_anchor_ids` — unique supplied IDs only;
- `insufficient_authority` — boolean.

Semantic contract failure is recorded; there are zero rerolls.

## 8. Call budget and model identity

- exact model: `gpt-5.6-luna`;
- max model-call attempts: 24;
- expected successful full execution: 24 attempts exactly;
- rerolls: 0;
- timeout and Copilot CLI hardened invocation reuse the already-shipped E023/0.1.16 transport path;
- model mismatch fails closed;
- per-call AI-credit ceiling parameter: 30;
- tokens/actual premium requests are recorded only if machine-readable upstream data exists; never infer them from call count.

## 9. Primary retrieval/selection verdict

`run_g1c.py` applies only the preregistered zero-model context rule:

- `EARNED_FOR_BROADER_G1_CONSIDERATION` only when all six B final contexts are `SUFFICIENT_CLEAN`, within the five-anchor budget, with valid planner/selector contracts;
- `TARGETED_SIGNAL_ONLY` only under the narrower preregistered improvement/no-clean-regression rule;
- otherwise `NOT_EARNED`.

Composer quality does not rewrite this retrieval/selection verdict.

## 10. Evidence capture

The authorized main-push run always uploads `remote-lab/out/e023-g1c/` and then commits immutable evidence under:

`experiments/E023-generality-retrieval-composition/evidence/g1c-run-<run_id>/`

The evidence directory contains:

- `result.json`;
- `run.json`;
- `result.sha256`.

Evidence-only commits do not match the paid workflow path, so capture cannot recursively execute G1c.

## 11. Post-run adjudication

Do not rerun answers. After immutable evidence exists:

1. inspect frozen A/B contexts and answers;
2. adjudicate PASS/PARTIAL/FAIL_RETRIEVAL/FAIL_COMPOSITION/CRITICAL_ERROR using the preregistered rules;
3. record the frozen retrieval/selection verdict separately from semantic quality;
4. update Issue #160 / HANDOFF only after result evidence is captured.

## 12. Non-conclusions

No G1c result directly authorizes G2 persistence, entity/graph/KnowledgeUnit storage, vector defaults, automatic identity merge/split, automatic routing, background semantic maintenance, or DERIVED state as terminal authority.
