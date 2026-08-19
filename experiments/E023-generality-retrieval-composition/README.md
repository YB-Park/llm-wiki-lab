# E023 — Generality Retrieval / Composition Gate

Status: **G1-C NOT EARNED / RESULT RECORDED**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy **cross-source semantic knowledge** from heterogeneous admitted evidence without first introducing persistent entity/graph/ontology state?

E023 is intentionally **not** an entity-system experiment. It tests simpler retrieval/composition explanations before semantic persistence.

## Core architecture guardrail

- The Trust / Authority Core remains knowledge-type agnostic.
- `source-note-v0` is one source-oriented **DERIVED projection**, not the ontology of LLM Wiki.
- A load-bearing derived statement must resolve to an authoritative anchor whose epistemic type remains explicit: admitted RAW evidence or explicit HUMAN_KNOWLEDGE. DERIVED state is never terminal authority.
- Semantic persistence is an optimization that must earn itself; it is not the default definition of knowledge.

## Three gates, in order

### G1 — Retrieval / Composition — **active**

Test whether authoritative evidence can be found and composed at query time without persistent semantic state.

The first G1 comparison is complete:

- **A:** exact-question BM25 top-5 → Luna composer;
- **C/G1a:** question-only Luna planner → 1–3 blind query rewrites → BM25 + RRF(k=60) → same top-5 evidence budget → same composer.

Frozen run `32215941344` used 30 exact-Luna calls with zero semantic rerolls.

Result:

- A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- C: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- C semantic improvements over A: **0**;
- C closed required-source recall@5 gaps: **0 / 4**;
- therefore **blind query expansion + consensus RRF is not earned**.

The critical Q001 failure is the most important evidence: both arms omitted the explicit identity bridge S004 but confidently merged `J.H. Park` with `Jihoon Park`. The answer happened to match frozen gold, but the supplied authority did not establish the merge.

See `results-v0.md` and `adjudication-v0.json`.

### G1b — next candidate, not yet authorized

Stay inside retrieval/composition. A separately preregistered follow-up may test **iterative evidence-follow retrieval**:

1. retrieve first candidates;
2. inspect bounded metadata/snippets;
3. identify a concrete missing/ambiguous relation;
4. issue targeted follow-up retrieval;
5. compose under the same bounded evidence budget;
6. require uncertainty for high-consequence identity/attribution when no explicit authoritative bridge was recovered.

Do zero-model counterfactual analysis of the frozen G1 artifact before authorizing more semantic calls.

### G2 — Persistence — future only if earned

Hold a strong retrieval/composition procedure fixed, then compare ephemeral synthesis with a fixed-identity persistent derived projection. G1a's failure does **not** authorize G2.

### G3 — Identity / Routing — last

Only if persistence itself demonstrates value may a later experiment test identity candidates, alias routing, merge/split, or bounded automatic target routing.

## Frozen corpus

18 normalized text sources / 10 cross-source questions / four families:

- identity / attribution / role-over-time;
- project decision rationale;
- incident timeline / hypothesis correction;
- vendor constraint conflict.

The person-heavy cases are stress tests, not a product proposal for people profiles. Binary PDF/DOCX/MSG extraction remains a separate provenance/adapter axis.

## Evidence

- preregistration merge: `17d1a2798357c2723c4776a7fa45ffc081124c9f`;
- execution-contract merge/source: `7315b858ed5ce764fa81ed131ee17f77c1ea11ae`;
- frozen run: `32215941344`;
- immutable captured result: `evidence/run-32215941344/result.json`;
- result SHA-256: `e578feb61454f124fce2294bf1a8e6ce396de213984cd889f760343f788c779a`;
- model calls: **30**;
- token totals: unknown — transport did not expose machine-readable totals in this runner;
- AI credits/premium requests: unknown — never infer from call count.

## Relationship to the product

Dogfood 0.1.16 remains unchanged. E023 adds no graph, entity store, vector default, background worker, new canonical schema, or product binary behavior.

Natural multi-session dogfood continues in parallel. E023 exists because developer-project dogfood strongly favors the current developer-shaped source-note projection and cannot be the only generality test.
