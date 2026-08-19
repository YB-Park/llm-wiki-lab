# E023 — Generality Retrieval / Composition Gate

Status: **G1a NOT EARNED / G1b NOT EARNED / G1c-R1 FINAL SELECTION NOT EARNED / CANDIDATE RETRIEVAL SIGNAL OBSERVED**  
Tracking: Issue #160  
Product baseline: Dogfood 0.1.16

## Question

Can LLM Wiki recover trustworthy **cross-source semantic knowledge** from heterogeneous admitted authority without first introducing persistent entity/graph/ontology state?

E023 is intentionally not an entity-system experiment. It decomposes G1 into retrieval, evidence selection, and composition before any semantic persistence is considered.

## Core architecture guardrail

- The Authority Core remains knowledge-type agnostic.
- `source-note-v0` is one source-oriented `DERIVED_MEMORY` projection, not the Wiki ontology.
- Every load-bearing derived statement must resolve to explicit terminal authority: admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`.
- `DERIVED_MEMORY` may help retrieval/compilation/navigation but is not terminal authority.
- Semantic persistence is an optimization that must earn itself only after a strong query-time path exists.

## Three gates, in order

1. **G1 Retrieval / Composition** — active.
2. **G2 Persistence** — future only if a strong G1 path still shows a persistence-shaped need.
3. **G3 Identity / Routing** — last, only if persistent semantic targets themselves earn value.

A G1 failure does not authorize G2. A G2 success would not automatically authorize G3.

## G1a — blind planned retrieval — complete / NOT EARNED

Frozen run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero semantic rerolls.

- A: exact-question BM25 top-5 -> composer.
- C: question-only planner -> 1–3 blind query rewrites -> BM25 + deterministic RRF -> same top-5 -> same composer.

Frozen semantic result:

- A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- C: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- C semantic improvements: **0**;
- promotion: **NOT_EARNED**.

Q001 was the key trust failure. Both arms omitted the explicit S004 identity bridge but confidently merged `J.H. Park` with `Jihoon Park`. The merge happened to match frozen gold, but the supplied authority did not establish it.

> **Truth-by-luck is not trustworthy semantic recovery.**

## G1b — evidence-follow retrieval — complete / frozen promotion NOT EARNED

Frozen run `32217824760`, exact `gpt-5.6-luna`, 12 calls, zero rerolls.

G1b used:

> exact-query top-5 -> inspect bounded evidence -> identify a missing/ambiguous relation -> targeted follow-up BM25 -> bounded selector -> unchanged G1a composer.

Frozen result:

- previously-missing source reached candidate pool: **2 / 4**;
- previously-missing source entered final context: **1 / 4**;
- semantic verdicts: **4 PASS**;
- Q001: **CRITICAL_ERROR -> PASS**;
- regressions: **0**;
- promotion: **NOT_EARNED** because the preregistered final-recovery threshold was >=3/4.

The targeted signal was still important: evidence-follow retrieval recovered the explicit missing identity bridge and repaired a critical trust failure without persistent identity state or a special-case composer rule.

## Authority-sufficiency evaluation — prospectively frozen and exercised

G1b exposed that flat `required_sources` conflated uniquely load-bearing authority with redundant corroboration. The evaluation question became:

> **Did the selected context contain enough typed authoritative support to establish every load-bearing proposition?**

A separated prospective slice was frozen before G1c semantic execution:

- 15 new typed authoritative anchors;
- 6 new questions `AQ001`–`AQ006`;
- 14 `RAW_MEMORY` anchors and one load-bearing `HUMAN_KNOWLEDGE` anchor;
- `all_of`, `any_of`, and `min_count` support clauses;
- identity bridges, direct attribution, repeated support, negative evidence, temporal correction, and forbidden conflation;
- 14 deterministic zero-model reference contexts.

The evaluator distinguishes:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

This is evaluation-only structure. It is **not** a product claim graph, semantic storage schema, or authorization for G2/G3.

## G1c v0 — invalid execution, no experiment verdict

G1c reused the already-defined evidence-follow mechanism on all six prospective questions instead of inventing a retrieval trick after inspecting the new evaluator slice.

The original execution source `987ee7ec615f7eb869be59f14a1928a3811baeed` produced run `32229563330`, but a runner aggregation bug crashed after all six A composer calls and the first B planner/selector/composer sequence. The first B row had not yet been persisted.

Therefore:

- v0 is frozen as **`INVALID_EXECUTION`**;
- no G1c retrieval-selection verdict is taken from v0;
- the six A outputs are immutable auxiliary semantic baselines only;
- the lost first-B output is not reconstructed or silently rerolled.

See `g1c-v0-execution-failure-v0.md`.

## G1c-R1 — B-only recovery replication — complete / NOT EARNED

Frozen R1 evidence:

- run `32232116273`;
- execution source `5227ac2b3f93c4f807e388822bfff963d0041120`;
- exact `gpt-5.6-luna`;
- **18 / 18** semantic call attempts;
- semantic rerolls: **0**;
- execution complete: **true**;
- result SHA-256 `8f3e77163db92f7dff0b0a9aed5776c6dadd0eebfdb122fbfecf4313d0dae822`;
- frozen final-selection verdict: **NOT_EARNED**.

R1 did not rerun A. It executed a new B-only evidence identity with the same G1c BM25, planner, selector, composer, typed-authority boundary, and promotion rules.

### The important stage decomposition

| stage | clean | sufficient + conflation risk | insufficient |
|---|---:|---:|---:|
| exact-query initial top-5 | 4 | 1 | 1 |
| evidence-follow candidate pool | 4 | 2 | **0** |
| final selector output | 4 | 0 | **2** |

The candidate pools contained enough positive load-bearing authority for **6 / 6** questions.

That means G1c-R1 did **not** primarily fail because the evidence-follow retriever could not discover authority. It failed because the final selector sometimes discarded authority that had already been found.

### AQ001 — recovered bridge discarded

The exact context lacked A003, the explicit `M. Chen -> Maya Chen` identity bridge, and contained same-surname distractor A004.

The planner correctly identified the identity/disambiguation gap. Follow-up BM25 recovered A003 into the candidate pool. The selector removed A004 — but also removed A003. Final authority therefore returned to `INSUFFICIENT_AUTHORITY`, and the composer again confidently asserted `M. Chen == Maya Chen`.

This remains a `CRITICAL_ERROR` despite the guessed identity being true in the frozen material.

> **Truth-by-luck remains a trust failure even when the missing authority was found earlier in the same loop and then discarded.**

### AQ002 — selector improvement

The exact context was positive-authority complete but contained A004 as a dangerous distractor. The selector retained direct email A002, meeting evidence A001/A005, and identity bridge A003 while dropping A004.

Final context became `SUFFICIENT_CLEAN`, and the answer correctly preserved direct authorship versus meeting attribution.

### AQ004 — destructive over-compression

The exact context and candidate pool were already `SUFFICIENT_CLEAN` with A009/A010/A011 available for:

- the unconfirmed early memory-leak hypothesis;
- retry/rollback causal evidence;
- the final retry-amplification root cause and rejection of the memory-leak hypothesis.

The selector compressed the context to A011 alone. This converted a clean context into `INSUFFICIENT_AUTHORITY` and produced the only semantic regression versus the auxiliary A baseline.

This is direct evidence against unconstrained “smallest sufficient set” compression.

## Frozen semantic adjudication

The invalid-v0 A outputs are auxiliary only.

| question | A auxiliary | R1 B | diagnosis |
|---|---|---|---|
| AQ001 | CRITICAL_ERROR | **CRITICAL_ERROR** | missing identity bridge; R1 selector dropped recovered A003 |
| AQ002 | PASS | **PASS** | attribution/identity preserved and distractor removed |
| AQ003 | PARTIAL | **PARTIAL** | `HUMAN_KNOWLEDGE` terminal authority type not made explicit |
| AQ004 | PASS | **FAIL_RETRIEVAL** | selector over-compressed a clean context to A011 |
| AQ005 | PASS | **PASS** | timeline/correction authority preserved |
| AQ006 | PARTIAL | **PARTIAL** | context support-complete; composer overstates insufficiency |

Counts:

- A auxiliary: **3 PASS / 2 PARTIAL / 1 CRITICAL_ERROR**;
- R1 B: **2 PASS / 2 PARTIAL / 1 FAIL_RETRIEVAL / 1 CRITICAL_ERROR**;
- B semantic improvements: **0**;
- B semantic regressions: **1**;
- new critical errors: **0**.

### HUMAN_KNOWLEDGE lesson

AQ003 is substantively correct, but A007 is explicit user-owned `HUMAN_KNOWLEDGE`. The answer states the decision as an ordinary team fact instead of preserving that terminal epistemic type.

Authority correctness includes **what kind of authority a claim terminates in**, not only whether the words are factually compatible.

### Composition-sufficiency lesson

AQ006 has a `SUFFICIENT_CLEAN` final context under the prospective contract. The composer correctly says standard HelixCloud DR fails and the Canada-only option **could** satisfy the rule, then unnecessarily marks authority insufficient because a stronger guarantee is not separately documented.

That is a composition judgment error, not retrieval insufficiency.

## What G1c-R1 earns

The current final evidence-follow selection policy is **NOT_EARNED**.

It does earn a narrower, useful diagnosis:

1. evidence-aware follow-up retrieval can recover missing load-bearing authority;
2. R1 candidate pools were positive-authority complete on **6 / 6** questions;
3. **authority-preserving final selection is now the leading G1 bottleneck**;
4. composition behavior remains independently important for explicit `HUMAN_KNOWLEDGE` typing and correct sufficiency judgments;
5. no result supports jumping to persistent dossiers, entity/graph storage, vector defaults, or automatic identity/routing.

## Current next decision

**Paid semantic tuning is paused again.**

Before any G1d model call, use the frozen G1c-R1 candidate pools for zero-model selection/budget counterfactual analysis.

The next question is not “which retrieval query trick is better?” It is:

> **Can a simple, general, evaluator-independent selection/budget rule preserve recovered load-bearing authority and avoid destructive compression, without installing a product claim graph?**

Only after a concrete zero-model rule earns a comparison should another semantic execution be preregistered.

## Relationship to the product

Dogfood 0.1.16 remains unchanged.

Natural installed dogfood continues in parallel because controlled corpora cannot establish long-horizon value, ambient routing behavior, popup/spend friction, or whether useful reasoning is recovered days or weeks later.
