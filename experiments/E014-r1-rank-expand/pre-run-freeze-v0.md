# E014 R1 pre-run freeze v0

Status: **FROZEN BEFORE R1 HELD-OUT SCORING**

Date: 2026-08-14

## Hypothesis provenance

R1 tests a hypothesis created only after E014-v0's formal held-out result was frozen: structural G1 ranking appeared sufficient for object discovery, while returned single-paragraph context missed cross-boundary signals. R1 therefore tests rank-then-expand on a completely fresh synthetic corpus.

E014-v0 held-out outcomes are not used as R1 confirmation.

## Scoring status at freeze

At this freeze:

- `analysis_r1.py` has **not** been executed on the R1 corpus;
- no R1 condition ranking/metric has been computed on held-out topics;
- hash-discovery workflows executed only current core regressions, `generate_corpus.py`, and file-hash reporting;
- model calls: 0.

## Frozen held-out corpus

- format: `llm-wiki-e014-r1-corpus-v0`
- seed: `20260823`
- topics: 40
- queries: 120
- shapes: 8 topics each of `short`, `structured`, `flat_contained`, `flat_cross`, `monolithic`
- flat-cross query classes: exact provenance, synthesis, decision history
- required cross-boundary continuation occurs both before and after the strongest lexical paragraph under frozen direction metadata
- canonical corpus SHA-256:
  `f3126cc8e61455c4b962a7f2efb7505003ec92767f342a4eefb43f105348b442`

## Frozen score-affecting file SHA-256 values

The following repository byte hashes were discovered by hash-only CI before scoring:

- `generate_corpus.py`:
  `82667717662d1a84e874d133e98d37cfb80ea9fce12fb129c3115ff08e94ed97`
- `retrieval_r1.py`:
  `1821a9e16d665a95cfa0d1d0edf4b6790d0ced2d00d47b784b7ac7218cb0c7bf`
- `analysis_r1.py`:
  `2db4b66ca2ad7a94038f60258d55d1b2ce6cdaeb5770b7821ea26d7b2c945ca2`

These three files plus the canonical corpus hash define the score-affecting frozen R1 protocol. Any mismatch must stop official scoring.

`validate_prescore.py` is an authorization/structural-validation harness, not a score-producing input. It is intentionally not part of the score-byte hash set. Its required behavior is frozen conceptually below: corpus hash/count/shape/gold/direction/provenance checks plus non-held-out W0/G1/G2 equivalence and X1/G1 ranking-identity fixture checks. Any later harness change before scoring must be documented and cannot alter the three score-affecting frozen files or corpus hash.

## Frozen conditions

### W0

- whole-object BM25 scoring;
- one scoring unit per object;
- returned-context diagnostics use the full paragraph with greatest query-token occurrence count, earliest tie; whole object if no multi-paragraph structure.

### G1

- >=2 ATX headings -> heading-section scoring units;
- otherwise >2 paragraphs -> paragraph scoring units;
- otherwise whole object;
- final object score = best unit score;
- returned context = full winning unit.

### X1 — primary candidate

- **exact same scoring/index units and BM25 scores as G1**;
- only returned context changes;
- if winning unit is a paragraph, inspect immediate previous/next paragraph;
- neighbor score = query-token occurrence count;
- choose greater count;
- tie -> next if present, otherwise previous;
- returned context = contiguous original span covering winner + selected neighbor;
- may not alter object score/order/top-k.

### G2 — reference only

- same as E014-v0 G2: sections, else paragraphs + every adjacent two-paragraph scoring window, else whole;
- final object score = best unit score;
- returned context = full winning unit.

## Frozen lexical parameters

- tokenizer: `[0-9a-zA-Z_가-힣]+`, casefold;
- BM25 `k1=1.5`, `b=0.75`;
- primary object top-k = 5;
- secondary top-k = 8;
- no Stage R1 returned-context truncation;
- final duplicate object IDs forbidden;
- content-object/source provenance semantics from ADR-0003/ADR-0004 held fixed.

## Frozen experimental unit and uncertainty

- topic scenario is the experimental unit;
- 40 topics total;
- query rows within a topic are not independent;
- paired percentile bootstrap at topic level only;
- 20,000 resamples;
- seed `20260824`;
- no query-row bootstrap.

## Frozen target regions and comparisons

Ranking target shapes:

- `structured`
- `flat_contained`
- `flat_cross`

Primary ranking comparison: `X1 - W0` on required-object recall@5 and required-object MRR.

Primary expansion region: `flat_cross`.

Primary expansion comparison: `X1 - G1` on required-signal recall@5.

Complexity/noninferiority reference: X1 vs G2 on cross-boundary signal recall, indexed characters, and returned-context characters.

Negative controls: `short + monolithic`.

## Frozen R1 gate

All 13 checks must pass:

1. X1 and G1 object IDs, ranks, ranking-unit IDs, and numeric BM25 scores identical for every query;
2. target required-object recall@5 gain X1-W0 >= +0.15;
3. target recall paired-bootstrap 95% CI lower bound > 0;
4. target MRR gain X1-W0 >= +0.10;
5. `flat_cross` required-signal recall@5 gain X1-G1 >= +0.30;
6. cross signal-recall paired-bootstrap 95% CI lower bound > 0;
7. X1 `flat_cross` signal recall@5 >= G2 - 0.05;
8. X1 indexed characters exactly equal G1 and <= 1.05x W0;
9. negative-control required-object recall@5 X1-W0 >= -0.05;
10. negative-control signal recall@5 X1-G1 >= -0.05;
11. provenance reversibility = 100% for W0/G1/X1/G2;
12. final duplicate-object rate = 0 for all conditions;
13. X1 mean returned-context chars@5 on `flat_cross` <= 1.10x G2.

Any failure => `DOES_NOT_SURVIVE_R1_GATE`.

## Forbidden post-score changes

After official R1 held-out scoring begins, do not change:

- corpus seed/text/query/gold/lures/direction metadata;
- corpus SHA expectation;
- score-affecting generator/retrieval/scorer bytes;
- W0/G1/X1/G2 rules;
- tokenizer/BM25 parameters;
- top-k values;
- context-expansion neighbor rule/tie rule;
- target/control shapes;
- metrics/bootstrap/gate thresholds.

A scoring bug requires preservation of the invalid run and an explicit versioned abort/amendment. It does not authorize quiet repair/rescore.

## Prescore authorization required

Before enabling the first official score, CI must:

1. verify all three frozen score-affecting SHA-256 values;
2. compile current core/R1;
3. pass all current dogfood core regressions;
4. run `validate_prescore.py` against the frozen corpus SHA;
5. verify 40 topics / 120 queries / 8 per shape;
6. verify forward/backward flat-cross structure and gold uniqueness without held-out BM25 scoring;
7. verify retrieval-unit character/provenance reversibility structurally;
8. verify W0/G1/G2 ranking equivalence to E014-v0 definitions only on a separate non-held-out fixture;
9. verify X1/G1 ranking identity only on a separate non-held-out fixture;
10. assert the prescore workflow does not execute `analysis_r1.py`.

Only after a green prescore run may a **separate workflow-only commit** enable the first official score on push, with a second frozen-byte verification immediately before scoring.

## Model/network boundary

R1 Stage A uses zero model calls and no external network data.

## Interpretation ceiling

A pass would be a fresh synthetic mechanism confirmation that G1 ranking + query-time neighbor expansion is a credible lower-complexity alternative to overlapping-window indexing. It would not authorize default production adoption, vectors/embeddings/graph retrieval, model reranking, or compiled-Wiki activation.