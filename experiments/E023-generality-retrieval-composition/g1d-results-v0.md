# E023 G1d — deterministic selection result v0

Status: **COMPLETE / SELECTION PROMOTION NOT EARNED**  
Run: `32322429563`  
Execution source: `c74673a83744789f271fa54c43b20212160007a2`  
Exact model: `gpt-5.6-luna`  
Semantic calls: **24 / 24**  
Rerolls: **0**  
Result SHA-256: `ef57c7a43c782694a0c42d428421b5d9a4bbb72b0a48b52a60c36edafa310bda`

## Frozen question

G1d tested whether the useful evidence-follow signal from G1c-R1 would generalize once the free-form model selector was removed and replaced with a deterministic, evaluator-blind evidence budget:

- **A:** exact-question BM25 top-5 -> composer;
- **D:** same initial top-5 -> unchanged evidence-aware planner -> 0–2 targeted BM25 queries -> candidate union -> RRF `k=60` -> fixed top-4 -> composer;
- D selector model calls: **0**.

The corpus and authority contract were prospectively frozen on a new 23-anchor / 8-question slice before this semantic run.

## Execution

The one-shot main workflow completed successfully.

- `execution_complete=true`;
- `model_call_attempts=24`;
- all A composer contracts completed;
- all D planner/composer contracts completed;
- deterministic RRF selection completed for all eight questions;
- no semantic reroll was performed.

The run is valid. Its negative result is therefore an experiment result, not an infrastructure failure.

## Frozen authority-selection result

Exact BM25 A:

- **3 SUFFICIENT_CLEAN**;
- **4 SUFFICIENT_WITH_CONFLATION_RISK**;
- **1 INSUFFICIENT_AUTHORITY**.

Deterministic RRF top-4 D:

- **3 SUFFICIENT_CLEAN**;
- **3 SUFFICIENT_WITH_CONFLATION_RISK**;
- **2 INSUFFICIENT_AUTHORITY**;
- authority-status improvements vs A: **0**;
- authority-status regressions vs A: **1**.

The preregistered promotion rule required 0 insufficient, at least 7/8 clean, at least 2 improvements, and 0 regressions.

> **G1d selection promotion is NOT_EARNED. Do not weaken the frozen rule.**

## What failed

### 1. RRF consensus can reinforce the distractor

On the first frozen v0 authority slice, posthoc RRF top-4 happened to remove same-name distractors. That did **not** generalize.

In G1d:

- BQ001 keeps `B004` (Diego Ortiz / Finance) in final top-4;
- BQ002 ranks `B004` first and pushes the uniquely load-bearing `B003` Dana Ortiz / D. Ortiz registry bridge to fifth, so the bridge is dropped;
- BQ007 keeps `B019` (Harbor Analytics, explicitly a different product);
- BQ008 keeps `B023` (vendor local-admin capability, explicitly not customer authorization policy).

All of these distractors are lexically close to the user question and remain visible across multiple exact/follow-up rankings. RRF rewards repeated retrieval agreement; it does not know whether that agreement represents **discriminative authority** or merely repeated lexical similarity.

### 2. Correctly naming the missing relation does not guarantee retrieval of the authority

BQ006 is the clearest retrieval failure.

The exact-query baseline misses `B013`, Cedar's authoritative residency rule, so A is `INSUFFICIENT_AUTHORITY`.

D's planner explicitly identifies the missing relation: Cedar's authoritative EU-only rule and whether it applies to every disaster-recovery copy. It then issues targeted queries for Cedar's rule and NimbusGrid's EU-only option.

But the same lexical BM25 follow-up still fails to bring `B013` into the top-3 candidate additions. The candidate pool remains authority-incomplete and D cannot repair the question.

This is important: the failure is not that the planner failed to reason about what was missing. The planner knew what authority was needed; **the retrieval surface could not reliably translate that need into the authoritative object**.

### 3. Removing the model selector avoided one failure class but did not create an authority-aware selector

G1c-R1 showed destructive free-form selector compression. G1d removes that model selector entirely, which prevents that exact failure mechanism.

But fixed RRF top-4 is still only a ranking heuristic. It cannot distinguish:

- identity bridge from same-surname distractor;
- policy authority from product capability;
- stable project identity from a same-name unrelated product;
- load-bearing negative evidence from merely topical evidence.

So G1d rejects the simplistic conclusion that **determinism alone** is enough for trustworthy final selection.

## Semantic adjudication

Frozen A semantic verdicts:

- **7 PASS**;
- **0 PARTIAL**;
- **0 FAIL_RETRIEVAL**;
- **0 FAIL_COMPOSITION**;
- **1 CRITICAL_ERROR**.

Frozen D semantic verdicts:

- **5 PASS**;
- **2 PARTIAL**;
- **0 FAIL_RETRIEVAL**;
- **0 FAIL_COMPOSITION**;
- **1 CRITICAL_ERROR**.

D semantic improvements vs A: **0**.  
D semantic regressions vs A: **2**.  
D new critical errors vs A: **0**.

### BQ002 — authority regression, but safer composition behavior

D drops the explicit `B003` identity bridge. Unlike the earlier G1c identity failure, the composer does **not** confidently merge Dana Ortiz with `D. Ortiz`; it says that the supplied records do not definitively establish they are the same person.

That is a useful trust behavior.

However, the structured `insufficient_authority` field remains `false`, contradicting the prose uncertainty and the frozen evaluator. BQ002 is therefore `PARTIAL`, not a pass.

### BQ004 — clean context, composition omission

D retains B009/B010/B011/B012 and is `SUFFICIENT_CLEAN`, but the answer cites B009/B011 and omits the explicit B010 retry/mitigation signal even though the prospective question marks that causal evidence path as load-bearing.

This is a composition omission, not retrieval failure.

### BQ006 — truth-by-luck compliance conclusion

Both A and D lack `B013`, the only frozen authority stating that Cedar's EU rule covers backups/replicas and that encryption does not waive it.

Both answers nevertheless begin with a definitive conclusion that NimbusGrid standard DR does not satisfy Cedar's rule. Both later express insufficiency/caveats, but those caveats do not supply the missing policy authority.

That is a high-consequence unsupported compliance conclusion and is recorded as `CRITICAL_ERROR` in both arms.

> **A correct-looking compliance conclusion without the governing policy anchor is still truth-by-luck.**

## What G1d earned

G1d did **not** earn its proposed selection mechanism. It did earn narrower knowledge about the G1 problem:

1. the G1c model-selector regression was real, but replacing it with fixed RRF is not sufficient;
2. lexical rank consensus can amplify semantically dangerous distractors;
3. the planner can correctly identify the *kind* of missing authority while lexical retrieval still fails to recover the authoritative object;
4. a composer can sometimes respond safely to missing identity authority by preserving uncertainty, but that safety behavior is not yet internally consistent;
5. authority sufficiency and semantic composition remain separable failure surfaces.

## Current core implication

Do **not** move to G2 because G1d failed. A G1 failure is not evidence for persistence.

The next controlled question is no longer “model selector or RRF?” It is:

> **How can query-time retrieval and evidence budgeting preserve consequence-sensitive authoritative relations — identity bridges, governing policy, negative evidence, temporal transitions — without importing the evaluator's hand-written clauses or installing a canonical entity/claim graph?**

Before another paid G1 run, use the frozen G1d rankings and candidate pools for zero-model diagnostics:

- measure where load-bearing anchors sit in exact/follow-up rankings;
- distinguish candidate-generation failure from final-budget failure;
- test whether simple retrieval-diversity / query-role / authority-type-aware but ontology-agnostic policies have any prospective justification;
- inspect whether whole-object BM25 itself is the limiting surface in BQ006;
- keep evaluation clauses strictly offline.

Only after a new mechanism is stated independently of BQ-specific anchor IDs/clauses should a new separated slice and paid comparison be considered.

## Boundaries unchanged

This result does **not** authorize:

- G2 persistent semantic dossiers;
- graph DB or universal Entity/Relation/KnowledgeUnit storage;
- automatic identity merge/split;
- vector retrieval as a default;
- evaluator clauses as runtime canonical structure;
- Dogfood runtime changes;
- reruns of G1d on the same BQxxx slice.
