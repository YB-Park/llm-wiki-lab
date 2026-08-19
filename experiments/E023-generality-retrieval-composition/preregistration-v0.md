# E023 preregistration v0 — Generality Retrieval / Composition Gate G1

Status before semantic generation: **PREREGISTERED / ZERO MODEL CALLS**.

## 1. Frozen question

For heterogeneous admitted evidence, does bounded **query-time retrieval planning + ephemeral cross-source composition** materially improve trustworthy semantic recovery over a simple raw-retrieval answer path, without persistent semantic identity or semantic state?

This experiment separates three questions that must not be collapsed:

1. can required evidence be found and composed at query time? — G1 / E023;
2. does semantic synthesis need to persist across queries/updates? — G2, only if later earned;
3. does automatic identity/routing add value safely? — G3, last.

## 2. Non-authorizations

E023 does **not** authorize or implement:

- Entity/Relation/KnowledgeUnit core schemas;
- graph DB, RDF/OWL, universal ontology;
- vector retrieval as a default;
- persistent person profiles or automatic profiling;
- automatic identity merge/split or alias resolution;
- automatic concept routing from E021;
- binary PDF/DOCX/MSG ingestion;
- background semantic maintenance;
- canonical mutation from model inference;
- DERIVED artifacts becoming authority.

`source-note-v0` remains a product experiment/projection. E023 does not promote or delete it.

## 3. Authority invariant

Every load-bearing claim in an answer or future derived projection must be traceable to an **authoritative anchor whose epistemic type remains explicit**:

- admitted `RAW_MEMORY`; or
- explicit `HUMAN_KNOWLEDGE` for user-owned decisions/beliefs/rationale.

`DERIVED_MEMORY` may assist navigation or compilation but is not terminal evidence merely because it persists.

The frozen E023 corpus uses normalized synthetic RAW evidence only; the invariant is stated more generally so this experiment does not accidentally redefine Human Knowledge as second-class.

## 4. Frozen corpus

Files:

- `corpus/sources.jsonl`
- `corpus/questions.json`
- `corpus/manifest.json`

Exactly **18 sources / 10 questions / 4 families**:

| family | sources | semantic stress |
|---|---:|---|
| identity_attribution | 6 | aliases, same-surname distractor, direct vs attributed speech, role change, unsupported characterization |
| decision_rationale | 4 | proposal vs decision, rationale, later evidence that does not automatically reverse a decision |
| incident_temporal | 4 | early hypothesis, later root cause, downstream symptom, timeline correction |
| vendor_constraint | 4 | repeated constraint, meeting uncertainty, direct clarification, vendor default that conflicts with requirement |

The corpus is synthetic and normalized text. The person scenario is one semantic family among four, not the target ontology.

## 5. Phase 0 — deterministic preflight — required before paid calls

Run:

```bash
python3 experiments/E023-generality-retrieval-composition/validate_corpus.py
```

Required:

- exact frozen IDs and counts;
- source/question hashes match manifest;
- all required/forbidden references resolve;
- no question references the same source as both required and forbidden;
- deterministic production-shaped BM25 rank report is emitted;
- `model_calls=0`.

The lexical report is **diagnostic, not a semantic gate**. A required source below top-k identifies a retrieval challenge. It does not prove that persistent semantic state is needed.

## 6. Primary comparison after main freeze

Use exact `gpt-5.6-luna`. Semantic rerolls: **0**.

### A — simple raw-retrieval baseline

For each frozen question:

1. submit the exact user question to the frozen deterministic raw retrieval procedure;
2. select a fixed top-k evidence context under the run protocol frozen before execution;
3. make **one** Luna answer call;
4. no persistent semantic state; no source-note input unless a later separately preregistered diagnostic says otherwise.

Maximum: **10 model calls** for 10 questions.

### C — planned query-time composition

For each frozen question:

1. one Luna **planner** call produces a bounded set of search queries/subquestions under a frozen machine-readable contract;
2. deterministic retrieval runs for those queries;
3. a deterministic union/dedup/budget step constructs raw evidence context;
4. one Luna **composer** call answers from that raw evidence;
5. the temporary plan/dossier is discarded after the question.

Maximum: **20 model calls** for 10 questions.

Total primary A+C ceiling: **30 semantic model calls**. Infrastructure failures are recorded; they do not receive semantic rerolls. The execution runner must fail closed if exact Luna is unavailable.

The final top-k/context budgets, planner query-count bound, prompts, and output schemas must be frozen on `main` in an execution addendum **before** the first semantic call. This preregistration deliberately does not tune them after seeing paid answers.

## 7. Why current source Agent Notes are not the primary B arm yet

The advisory review identified a concrete concern that `source-note-v0` forces developer-shaped fields (`operational_rules`, `boundaries`) onto heterogeneous sources. Generating 18 notes before we establish the raw/query-time baseline would mix two questions:

- whether cross-source semantic composition is valuable;
- whether this specific source-note projection is a good heterogeneous representation.

Therefore E023 G1 first isolates A vs C. A later zero-/bounded-call **B diagnostic** may compare current source-note behavior only after its own protocol is frozen. It cannot be used to infer persistence value.

## 8. Frozen semantic failure classes

Each answer is evaluated separately for:

- answer correctness;
- required evidence recall in supplied context;
- provenance resolvability;
- wrong-person/wrong-subject attribution;
- false merge / false split when applicable;
- direct-authored vs meeting-attributed distinction;
- temporal ordering/current-vs-earlier correctness;
- unsupported characterization / epistemic upgrade;
- disagreement/constraint preservation;
- insufficient-answer behavior when context lacks load-bearing evidence.

### Critical errors

The following are critical regardless of generic answer quality:

- conflating Park Jieun (S005) with Park Jihoon/Jihoon Park/J.H. Park;
- presenting meeting-note attribution as a direct-authored statement;
- turning an explicitly superseded early incident hypothesis into the final root cause;
- inventing a broad personality/technology stance such as `risk-averse` or `anti-cloud` from the narrow DPA evidence;
- claiming a derived conclusion is sourced when its required authoritative evidence is absent.

## 9. Retrieval vs composition diagnosis

For every failed semantic answer, classify first:

### RETRIEVAL_FAILURE
At least one load-bearing required source/region was absent from the supplied composer context.

Consequence: improve/evaluate retrieval or planning. **Do not infer persistence.**

### COMPOSITION_FAILURE
The load-bearing evidence was present, but the answer still made a factual, attribution, temporal, or epistemic error.

Consequence: query-time composition/reasoning needs work. **Do not infer persistence.**

### SUFFICIENT_CAUTION
The context genuinely does not establish the answer and the model says so rather than fabricating.

Consequence: answer may be incomplete as a user outcome but is not hallucination; trace retrieval separately.

Persistence is not a G1 failure label.

## 10. Promotion logic frozen before results

The gate is directional, not a license to optimize thresholds after the run.

- If C yields **fewer than 2 net question-level improvements over A**, with no clearer recovery of required evidence, planned query-time complexity is not earned by this corpus.
- If C yields **at least 2 net question-level improvements over A** and introduces **zero new critical errors**, query-time planning/composition earns continued product/research consideration.
- Any new critical error in C blocks a positive G1 promotion regardless of aggregate gains until that failure class is understood.
- If C improves evidence recall but answers still fail with evidence present, the result is composition-limited, not persistence evidence.
- If A and C both fail because evidence retrieval misses required sources, the result is retrieval-limited, not persistence evidence.
- **No E023 G1 outcome directly authorizes G2 persistent semantic state.** G2 requires a separate preregistration motivated by repeated reconstruction cost, inconsistency, latency, or retrieval fragility after a strong ephemeral procedure exists.

“Question-level improvement” must be decided by the frozen evaluator rubric/exact answer checks before execution; it cannot mean merely a longer or more fluent answer.

## 11. Cost reporting

Record separately:

- planner calls;
- answer/composer calls;
- total model calls;
- tokens only when machine-readable transport data exists;
- AI credits/premium requests only when upstream reports them.

Never infer credits from calls or tokens.

## 12. Relationship to real dogfood

Natural installed P7/Issue #141 continues in parallel and may take days or weeks. E023 is a controlled **architecture-discrimination** experiment, not a substitute for product habitability evidence.

E023 is justified now because developer-project dogfood strongly favors the current developer-shaped source-note schema and can therefore hide a generality failure by workload selection.

## 13. Decision boundary

A PASS for G1 can earn only this conclusion:

> bounded query-time retrieval planning and ephemeral cross-source composition are worth further use/testing without persistent semantic state.

A FAIL can earn only a failure diagnosis. It cannot by itself authorize entity persistence, graphs, vectors, automatic routing, or a new ontology.
