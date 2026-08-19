# E023 G1c preregistration v0 — prospective authority-sufficiency evidence-follow comparison

Status before semantic generation: **PREREGISTERED CANDIDATE / ZERO MODEL CALLS ON THIS PR / NO PAID RUN AUTHORIZED**.

The authority-sufficiency evaluator is prospectively frozen on a separated six-question slice. G1a and G1b remain frozen `NOT_EARNED` under their original promotion rules. G1b nevertheless produced one concrete trust repair by retrieving an explicit identity bridge. G1c tests whether that already-defined evidence-follow mechanism generalizes on the new slice when measured by load-bearing authority rather than flat source-list completeness.

This is still **G1 Retrieval / Composition**. It does not test or authorize persistence, entities, graphs, vectors, durable identity, or automatic routing.

## 1. Frozen causal question

> On the six prospectively separated authority-sufficiency questions, does the already-defined evidence-follow loop produce cleaner, authority-sufficient final contexts than exact-question BM25 top-5, without degrading questions whose baseline context is already clean?

This is not a search for a new retrieval trick. The candidate structure is inherited from G1b because inventing a mechanism after inspecting this slice would overfit the evaluator.

## 2. Frozen material

Use only `authority-sufficiency-v0/`:

- 15 typed terminal-authority anchors;
- 6 questions: `AQ001`–`AQ006`;
- 14 `RAW_MEMORY` anchors and 1 `HUMAN_KNOWLEDGE` anchor;
- the already-frozen evaluation-only authority contract;
- no model answers exist before G1c execution.

All six questions are targets. No subset is selected from semantic outcomes.

## 3. Zero-model baseline frozen before calls

Production-shaped exact-question BM25 top-5 produces:

| question | exact top-5 | authority status |
|---|---|---|
| AQ001 | A005 A002 A001 A006 A004 | `INSUFFICIENT_AUTHORITY` |
| AQ002 | A005 A002 A004 A001 A003 | `SUFFICIENT_WITH_CONFLATION_RISK` |
| AQ003 | A007 A008 A006 A004 A013 | `SUFFICIENT_CLEAN` |
| AQ004 | A009 A011 A010 A012 A014 | `SUFFICIENT_CLEAN` |
| AQ005 | A012 A009 A010 A011 A005 | `SUFFICIENT_CLEAN` |
| AQ006 | A014 A015 A013 A003 A007 | `SUFFICIENT_CLEAN` |

Baseline counts: **4 clean / 1 sufficient-with-risk / 1 insufficient**.

AQ001 lacks the explicit `M. Chen -> Maya Chen` bridge A003 and also contains same-surname distractor A004. AQ002 has all positive authority but contains A004. These facts are evaluator measurements only and must never be shown to planner, selector, or composer.

## 4. Arms

### A — exact BM25 baseline

For every question:

1. exact user question;
2. same object-level BM25 formula/tokenization used in E023 G1;
3. top-5 full authoritative anchors;
4. one exact-Luna composer call.

No planner or selector.

### B — evidence-follow

Reuse the G1b structure without question-specific rules:

1. same exact-question BM25 top-5 as A;
2. one planner call sees only question + bounded metadata/snippets for those five hits;
3. planner states a missing/ambiguous relation and emits 0–2 targeted lexical queries;
4. same BM25 retrieves top-3 per follow-up query into a temporary pool;
5. one selector call sees question + bounded candidate metadata/snippets + planner working state and chooses at most five anchors;
6. same composer prompt/contract as A answers from the selected full anchors.

Temporary planner/selector state is discarded and is never authority.

## 5. Typed authority boundary

Every anchor shown to the composer carries `authority_type`.

- `RAW_MEMORY` is admitted external evidence.
- `HUMAN_KNOWLEDGE` is explicit user-owned project knowledge.
- Neither planner nor selector may manufacture authority.
- No `DERIVED_MEMORY` is terminal authority in this gate.
- Model-facing prompts do not expose evaluator clauses, proposition IDs, required anchor IDs, forbidden anchor IDs, reference contexts, or expected statuses.

The composer must preserve the epistemic type. In AQ003, A007 may support the user-owned decision/rationale but must not be misrepresented as independently observed external evidence.

## 6. Frozen budgets

A later execution addendum may freeze implementation details but may not exceed or change:

- model: exact `gpt-5.6-luna`;
- questions: 6;
- A composer calls: 6;
- B planner calls: 6;
- B selector calls: 6;
- B composer calls: 6;
- maximum semantic model-call attempts: **24**;
- semantic rerolls: **0**;
- initial top-k: 5;
- final full-authority limit: 5;
- follow-up queries: 0–2;
- follow-up BM25 top-k per query: 3;
- planner/selector snippet cap: 320 characters per candidate;
- per-call AI-credit ceiling parameter: 30, while actual credits/premium requests remain unknown unless upstream reports them.

## 7. Primary zero-model outcome — authority sufficiency

The frozen evaluator classifies A and B final contexts as:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

Primary G1c retrieval/selection verdict:

### `EARNED_FOR_BROADER_G1_CONSIDERATION`

Only if all are true:

1. B final contexts are `SUFFICIENT_CLEAN` for **6/6** questions;
2. every B final context contains at most five anchors;
3. planner and selector contracts are valid on all six questions;
4. all execution calls respect the frozen budget with zero rerolls.

This deliberately requires repairing both observed baseline trust defects while preserving all four already-clean cases.

### `TARGETED_SIGNAL_ONLY`

If the strict promotion rule fails, record this narrower signal only if:

1. B increases the `SUFFICIENT_CLEAN` count above the frozen baseline of 4;
2. none of AQ003–AQ006 degrades from `SUFFICIENT_CLEAN`;
3. B introduces no new forbidden-conflation risk on a previously clean question;
4. all executed contracts remain valid.

`TARGETED_SIGNAL_ONLY` is not promotion.

### `NOT_EARNED`

Otherwise.

## 8. Semantic adjudication is separate from retrieval promotion

Both A and B generate answers only after context selection. Adjudicate each frozen output once, with no rerolls:

- `PASS`;
- `PARTIAL`;
- `FAIL_RETRIEVAL`;
- `FAIL_COMPOSITION`;
- `CRITICAL_ERROR`.

Use the frozen question `load_bearing_propositions` plus authority type.

Key rules:

- context insufficient + safe uncertainty => `FAIL_RETRIEVAL`, not a hallucination;
- context sufficient + omitted implication => `PARTIAL` or `FAIL_COMPOSITION`;
- confident identity merge without an authoritative bridge, wrong-subject conflation, fabricated direct authorship, or treating `HUMAN_KNOWLEDGE` as independent external evidence may be `CRITICAL_ERROR`;
- truth-by-luck does not pass.

The primary retrieval/selection promotion above is not rewritten by composition quality. If B earns clean authority contexts but composition fails, the next diagnosis is composition policy—not G2 persistence.

For product-like follow-up consideration, additionally require **zero new B critical errors**.

## 9. Explicit non-conclusions

No G1c outcome directly authorizes:

- G2 persistent dossiers or semantic caches;
- Entity/Relation/KnowledgeUnit schemas;
- graph storage;
- vector defaults;
- automatic identity merge/split;
- automatic semantic routing;
- background semantic maintenance;
- derived artifacts becoming terminal authority.

Even strict G1c promotion only earns broader/natural validation of bounded evidence-follow behavior.

## 10. Execution discipline

This preregistration PR contains no paid runner or execution request.

Only after it is merged to `main` may a separate execution-addendum PR freeze exact prompts, schemas, runner, request bytes, GitHub workflow, evidence capture, and the 24-call ceiling. The PR path must remain zero-model; only the separately authorized `main` push may execute semantic calls.
