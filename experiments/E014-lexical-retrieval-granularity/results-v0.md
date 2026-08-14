# E014 Stage A results v0 — lexical retrieval granularity gate

Status: **DOES_NOT_SURVIVE_DETERMINISTIC_GATE**

Official score date: 2026-08-14

Official GitHub Actions push run: `31782899247`

Scored branch head: `95f15870aa074fe21b5cdad35d1bae2c030e30dd`

Result artifact: `e014-stage-a-heldout-v0`, artifact ID `9212361877`

Artifact SHA-256 digest: `97906545dc4915e300fbc8eebc7c0a2a5a3b7d573ec728a6339abf638c49e917`

Model calls: **0**

## Formal conclusion

The preregistered primary candidate `G2` **does not survive the deterministic gate** because one of eight frozen checks failed.

The failed check was:

> On the three frozen flat cross-boundary decision queries, G2 required-object recall@5 must exceed G1 required-object recall@5 by at least +0.10.

Observed:

- G1 cross-boundary required-object recall@5: `1.000`
- G2 cross-boundary required-object recall@5: `1.000`
- difference: `+0.000`

Therefore the frozen gate outcome is `DOES_NOT_SURVIVE_DETERMINISTIC_GATE`. This result is not changed even though the other seven checks passed and the overall G2-vs-W0 signal was large.

No post-score threshold, corpus, top-k, BM25 parameter, section/window rule, or gate metric was changed.

## Held-out corpus and primary comparison

- held-out corpus SHA-256: `4dde1977666bf8f7494f5ca688631cfd2bb878272ccc1b7821456127d6778eed`
- topics: 20
- queries: 60
- target shapes: `structured`, `flat` — 10 topics total
- negative controls: `short`, `monolithic` — 10 topics total
- experimental unit: topic
- bootstrap: 20,000 topic-level paired resamples, seed `20260815`
- primary comparison: G2 - W0

## Primary held-out results

| Metric, target shapes | W0 | G2 | G2-W0 | topic-bootstrap 95% CI |
|---|---:|---:|---:|---:|
| required-object recall@5 | 0.767 | 1.000 | +0.233 | [+0.017, +0.517] |
| required-object MRR | 0.278 | 0.917 | +0.639 | [+0.567, +0.702] |
| required-signal recall@5 | 0.700 | 1.000 | +0.300 | [+0.083, +0.550] |

Additional target-region diagnostics:

- W0 top-1 lexical-lure rate: `1.000`
- G2 top-1 lexical-lure rate: `0.000`
- G1 top-1 lexical-lure rate: `0.000`

The held-out corpus therefore reproduces the intended **whole-object BM25 dilution/lure mechanism** in the target region: deterministic finer structural units dramatically improved object ranking and removed the frozen short-lure top-1 failure mode.

This mechanism result is real within the synthetic held-out benchmark, but it does not override the preregistered G2 gate failure.

## G1 vs G2

G1 was preregistered as a diagnostic baseline, not the primary candidate.

Observed target-region means:

| Metric | G1 | G2 |
|---|---:|---:|
| required-object recall@5 | 1.000 | 1.000 |
| required-object MRR | 0.917 | 0.917 |
| required-signal recall@5 | 0.900 | 1.000 |
| top-1 lure rate | 0.000 | 0.000 |
| indexed-character multiplier vs W0 | 0.998x | 1.552x |
| mean top-5 context chars, all shapes | 536.0 | 540.15 |

Thus the held-out score does **not** show that indexing adjacent two-paragraph windows improves object ranking over the simpler G1 structural index. G2's extra indexed-character cost was not rewarded by better object recall or MRR.

However, G2 did improve returned-context signal coverage in the frozen flat cross-boundary decision cases. That distinction was not captured by frozen gate check #8.

## Negative controls

On `short + monolithic` topics, G2-W0 differences were exactly zero for the preregistered control metrics:

- required-object recall@5 difference: `0.000`, 95% CI `[0.000, 0.000]`
- required-object MRR difference: `0.000`, 95% CI `[0.000, 0.000]`
- required-signal recall@5 difference: `0.000`, 95% CI `[0.000, 0.000]`

So the target-region gain did not come with an observed negative-control retrieval regression in this benchmark.

## Index/provenance cost

| Condition | retrieval units | indexed chars | indexed-char multiplier vs W0 | provenance reversible |
|---|---:|---:|---:|---|
| W0 | 300 | 401,772 | 1.000x | yes |
| G1 | 981 | 401,118 | 0.998x | yes |
| G2 | 1,308 | 623,746 | 1.552x | yes |

All conditions had:

- provenance reversibility: 100%
- final duplicate-object rate: 0

G1's indexed-character total is slightly below W0 because heading segmentation excludes text before the first heading in documents with >=2 headings under the frozen rule. This is a benchmark/index-accounting property and must not be interpreted as a general storage saving.

## Frozen gate checks

| Frozen check | Result |
|---|---|
| target recall@5 gain >= +0.15 | PASS |
| target recall@5 CI lower bound > 0 | PASS |
| target MRR gain >= +0.10 | PASS |
| negative-control recall regression >= -0.05 | PASS |
| provenance reversibility = 100% | PASS |
| final duplicate-object rate = 0 | PASS |
| G2 indexed-char multiplier <= 3.0x | PASS |
| cross-boundary G2-G1 object recall@5 >= +0.10 | **FAIL** |

Formal result: **7/8 checks passed; gate fails because all eight were required.**

## Post-score diagnostic — metric-design failure, not gate repair

This section is explicitly **post hoc** and cannot change the v0 outcome.

The three frozen cross-boundary flat decision queries were inspected only after the official score. Their aggregate behavior was:

| Condition | required-object recall@5 | required-signal recall@5 | MRR |
|---|---:|---:|---:|
| W0 | 0.667 | 0.000 | 0.206 |
| G1 | 1.000 | 0.000 | 1.000 |
| G2 | 1.000 | 1.000 | 1.000 |

Interpretation:

- G1 found and ranked the correct object, so **object recall could not distinguish G1 from G2**.
- G1 returned only the winning single paragraph, which did not contain the gold signal that crossed the paragraph boundary.
- G2's adjacent two-paragraph unit returned the required cross-boundary signal.

Therefore frozen gate check #8 measured the wrong quantity for the mechanism it intended to test. The intended cross-boundary mechanism is about **returned retrieval-unit/context coverage**, not object discovery once final results are aggregated to one hit per object.

This is a protocol-design lesson, not permission to change the v0 metric after seeing the result.

## Post-score minimum-architecture hypothesis

The held-out result suggests a simpler hypothesis than G2's all-window index:

> Rank deterministic sections/paragraphs as in G1, then expand the winning paragraph to adjacent context **after ranking**, instead of indexing every adjacent two-paragraph window.

Why this is promising:

- G1 matched G2 object recall/MRR in the target region;
- G1 used ~1.0x W0 indexed characters instead of G2's 1.552x;
- G1's failure was context coverage on cross-boundary spans, not object ranking;
- deterministic neighbor expansion may recover the missing context without increasing the BM25 corpus with overlapping windows.

This hypothesis was created **after seeing v0 held-out outcomes**. It is not E014-v0 evidence and must be tested on a new frozen corpus before implementation/adoption.

## Decision

Do **not**:

- make G2 the default retrieval path;
- reinterpret v0 as a formal pass;
- tune G2/window sizes against this held-out corpus;
- add vectors, embeddings, a graph DB, or learned reranking;
- run Stage B answer-quality model calls from this failed primary gate.

Next justified step:

- run a fresh, non-tuned replication comparing W0, G1, and **G1 + deterministic neighbor context expansion**;
- use retrieval-unit/signal coverage, not object recall, for the cross-boundary-specific check;
- retain object recall/MRR as core ranking metrics;
- keep provenance/current-history/object-dedup semantics fixed;
- keep model calls at zero until the cheaper lexical design earns a confirmatory pass.

## Evidence grade and limitations

Evidence grade: **controlled held-out synthetic mechanism benchmark**.

Limitations:

- synthetic author-designed lexical-lure mechanism;
- G2 was selected using a separate development corpus before the held-out run;
- only 20 topic units, with primary target inference over 10 target topics;
- no realistic user corpus;
- no answer-quality measurement;
- no human-time/latency operational measurement;
- no semantic/paraphrase retrieval stress;
- no evidence that persistent compiled Wiki state should be enabled.

The useful conclusion is narrower:

> Whole-object BM25 has a demonstrated synthetic long/noisy lexical-dilution failure region. Structural lexical ranking appears promising, but the preregistered overlapping-window G2 candidate did not earn its extra complexity under the frozen v0 gate. A simpler rank-then-expand design deserves a fresh confirmatory test.