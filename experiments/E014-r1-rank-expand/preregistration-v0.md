# E014 R1 — rank-then-expand lexical retrieval confirmation

Status: **preregistered before R1 held-out scoring**

Date: 2026-08-14

## Provenance of this hypothesis

E014 Stage A v0 formally failed its all-required G2 gate. A post-score diagnostic showed that the simpler G1 section/paragraph index often found the correct object, while its returned single paragraph missed a signal spanning a paragraph boundary. G2 recovered that span by indexing adjacent paragraph windows, but its extra overlapping-window index did not improve object recall/MRR over G1.

R1 is therefore a **new confirmatory experiment** for a post-score hypothesis. E014-v0 held-out results are not reused as confirmation.

## Question

Can retrieval ranking and context expansion be separated so that a simple structural lexical index retains G1's ranking/index cost while deterministic query-time neighbor expansion recovers cross-boundary evidence spans at least as well as G2's overlapping-window index?

## Conditions

All conditions preserve ADR-0003/ADR-0004 current/history, content-object dedupe, and provenance semantics.

### W0 — whole-object baseline

Current whole-content-object BM25 ranking. One scoring unit per object.

### G1 — structural rank / no expansion

- If document has >=2 ATX headings: heading sections are scoring units.
- Else if >2 paragraphs: individual paragraphs are scoring units.
- Else: whole object.
- Final object score = max unit score.
- Returned context = winning unit.

### X1 — primary rank-then-expand candidate

**Ranking/indexing must be byte-for-byte/score-for-score identical to G1.**

- Uses exactly G1 scoring units and BM25 scores.
- If the winning unit is a heading section or whole object: context unchanged.
- If the winning unit is paragraph `p[i]`: inspect only immediate paragraph neighbors `p[i-1]` and `p[i+1]` when present.
- Neighbor score for expansion = count of query-token occurrences in that neighbor using the frozen tokenizer.
- Choose the adjacent neighbor with greater query-token count.
- Tie rule: choose the **next** paragraph if present; otherwise previous.
- Returned context is the contiguous original-document span covering winning paragraph + chosen neighbor, in original document order.
- Expansion changes context only; it may not alter object score/order/top-k membership.

### G2 — v0 overlapping-window reference

Same structural rule as E014-v0 G2: headings as sections; otherwise paragraphs plus every adjacent two-paragraph window; final object score = max unit score. Included as a reference, not the primary candidate.

## Frozen lexical parameters

- tokenizer: `[0-9a-zA-Z_가-힣]+`, casefold;
- BM25: `k1=1.5`, `b=0.75`;
- primary object top-k: 5;
- secondary object top-k: 8;
- final object dedupe required;
- returned context is the full winning/expanded structural span for Stage R1 metrics; context characters are measured explicitly rather than hidden by a truncation cap.

## Fresh R1 corpus

R1 uses a new synthetic corpus generator and a new held-out seed. It must not reuse v0 query terms, gold strings, lure ordering, document lengths, or cross-boundary locations.

Planned held-out design:

- 40 topic scenarios;
- 5 shapes x 8 topics each:
  - `short`;
  - `structured`;
  - `flat_contained`;
  - `flat_cross`;
  - `monolithic`;
- 3 paired query classes/topic = 120 queries;
- all three query classes in `flat_cross` contain a required signal split across adjacent paragraphs;
- cross-boundary direction alternates across topics so required continuation may be previous or next relative to the strongest lexical paragraph;
- lexical lures repeat partial query terms but omit one required term/signal;
- some objects have multiple synthetic source IDs attached to identical bytes to validate object-level ranking invariance.

The canonical held-out corpus SHA-256 is frozen in a separate pre-run freeze after generator-only structural/hash validation and before any condition scoring.

## Experimental unit

Primary unit: topic scenario.

Query rows within a topic are not independent. Paired bootstrap resamples topics only.

## Primary comparisons

### Ranking mechanism: X1 vs W0

Because X1 ranking is exactly G1 ranking, this confirms that structural lexical ranking still beats whole-object BM25 on the fresh target region.

Primary target shapes: `structured + flat_contained + flat_cross`.

Metrics:

1. required-object recall@5;
2. required-object MRR.

### Expansion mechanism: X1 vs G1

Primary expansion region: `flat_cross`.

Metrics:

1. required-signal recall@5 — **primary expansion metric**;
2. all-required-signal-at5 fraction;
3. returned-context characters@5.

This explicitly fixes the E014-v0 protocol mismatch: cross-boundary expansion is judged by returned span/signal coverage, not by object recall when both conditions already retrieve the same object.

### Complexity reference: X1 vs G2

Compare:

- signal recall@5 on `flat_cross`;
- indexed characters/units;
- returned context characters.

## Bootstrap

- 20,000 paired topic-level resamples;
- seed `20260824`;
- percentile 95% CI;
- no query-row pseudo-replication.

## Frozen R1 gate

X1 survives only if **all** checks pass:

1. **ranking identity invariant:** X1 and G1 object IDs, ranks, and numeric BM25 scores are identical for every query;
2. target required-object recall@5 gain X1-W0 >= +0.15;
3. target recall@5 paired-bootstrap CI lower bound > 0;
4. target MRR gain X1-W0 >= +0.10;
5. `flat_cross` required-signal recall@5 gain X1-G1 >= +0.30;
6. `flat_cross` signal-recall paired-bootstrap CI lower bound > 0;
7. X1 `flat_cross` signal recall@5 >= G2 - 0.05;
8. X1 indexed characters are exactly equal to G1 and <= 1.05x W0;
9. negative-control (`short + monolithic`) required-object recall@5 X1-W0 >= -0.05;
10. negative-control signal recall@5 X1-G1 >= -0.05;
11. provenance reversibility = 100% for all conditions;
12. final duplicate-object rate = 0 for all conditions;
13. X1 mean returned-context chars@5 <= 1.10x G2 on `flat_cross`.

Any failure => `DOES_NOT_SURVIVE_R1_GATE`.

## Interpretation ceiling

A pass means only:

> on a fresh synthetic mechanism corpus, paragraph/section lexical ranking plus query-time neighbor expansion is a credible simpler alternative to overlapping-window indexing.

A pass does **not** justify:

- default production rollout without shadow/realistic confirmation;
- vectors/embeddings/graph retrieval;
- learned/model reranking;
- persistent compiled Wiki activation.

A failure kills X1 as currently specified. Do not tune neighbor selection or expansion width on R1 held-out outcomes.

## Model/network boundary

R1 Stage A uses zero model calls and no external network data. Stage B answer-quality testing is not authorized by this preregistration.
