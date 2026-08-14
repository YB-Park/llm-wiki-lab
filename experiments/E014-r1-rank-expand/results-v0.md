# E014 R1 — official held-out result v0

Status: **SURVIVES_R1_GATE**

Date: 2026-08-14

## Decision

The frozen R1 candidate **X1 survives all 13 preregistered deterministic checks** on the fresh held-out synthetic mechanism corpus.

This result is sufficient to justify implementing X1 as a **non-default / shadow retrieval candidate** in the core so that realistic workloads can evaluate it. It is **not** sufficient to make X1 the production default, add embeddings/vector/graph retrieval, add learned reranking, or activate persistent compiled Wiki state.

## What X1 is

X1 separates ranking from returned-context expansion:

1. index and rank exactly the same structural units as G1 (heading sections when structured, otherwise paragraphs, otherwise whole object);
2. preserve exactly the same G1 object ranking and BM25 score;
3. only after the winning paragraph is known, deterministically add one adjacent paragraph using frozen query-token-overlap selection;
4. preserve original-document contiguous spans and source/object provenance.

The candidate therefore avoids G2's overlapping-window index while attempting to recover the same cross-boundary context.

## Methodology integrity

- R1 hypothesis was generated **after** E014-v0 official results, so R1 used a completely fresh corpus/protocol.
- Fresh seed: `20260823`.
- Held-out corpus: 40 topics / 120 queries / 5 shapes x 8.
- Canonical corpus SHA-256: `f3126cc8e61455c4b962a7f2efb7505003ec92767f342a4eefb43f105348b442`.
- Frozen score-affecting file SHA-256 values:
  - generator: `82667717662d1a84e874d133e98d37cfb80ea9fce12fb129c3115ff08e94ed97`
  - retrieval: `1821a9e16d665a95cfa0d1d0edf4b6790d0ced2d00d47b784b7ac7218cb0c7bf`
  - analysis: `2db4b66ca2ad7a94038f60258d55d1b2ce6cdaeb5770b7821ea26d7b2c945ca2`
- Initial prescore failure was a validator-only Python 3.12 `importlib` / `dataclass` module-registration bug. Frozen generator/retrieval/analysis bytes were unchanged; held-out scoring had not begun.
- Green prescore after the plumbing-only fix: PR workflow run `31785580766`.
- First and only automatic official score: push workflow run `31785676474` at commit `5a8240e1ccd15c409e07917703ba08b38804ab54`.
- Official result artifact: `e014-r1-heldout-v0`, artifact ID `9213391107`, archive digest `sha256:5048a0e1a73113b21ad7c7d8b221ecd420d4f5363312c6c168a09981047556b4`.
- Automatic scoring was removed immediately after the official run. Frozen-result validation run `31785777316` succeeded.
- Model calls: **0**.

## Official headline results

Target shapes are `structured + flat_contained + flat_cross`.

| Condition | target recall@5 | target MRR | target signal@5 | cross signal@5 | cross context chars@5 | index chars vs W0 |
|---|---:|---:|---:|---:|---:|---:|
| W0 | 0.583 | 0.217 | 0.389 | 0.000 | 447.2 | 1.000x |
| G1 | 1.000 | 0.917 | 0.667 | 0.000 | 744.0 | 0.997x |
| X1 | 1.000 | 0.917 | 1.000 | 1.000 | 877.3 | 0.997x |
| G2 | 1.000 | 0.917 | 1.000 | 1.000 | 877.3 | 1.806x |

Paired topic-bootstrap results:

- X1 - W0 target recall@5: **+0.417**, 95% CI **[+0.243, +0.611]**.
- X1 - W0 target MRR: **+0.700**, 95% CI **[+0.673, +0.726]**.
- X1 - G1 flat-cross signal recall@5: **+1.000**, 95% CI **[+1.000, +1.000]**.

## All 13 frozen gate checks

All are `true` in the preserved result artifact:

1. X1/G1 object IDs, ranks, and numeric BM25 scores are identical for every query.
2. Target recall@5 gain X1-W0 >= +0.15.
3. Target recall@5 paired-bootstrap CI lower bound > 0.
4. Target MRR gain X1-W0 >= +0.10.
5. Flat-cross signal recall@5 gain X1-G1 >= +0.30.
6. Flat-cross signal paired-bootstrap CI lower bound > 0.
7. X1 flat-cross signal recall@5 >= G2 - 0.05.
8. X1 indexed characters exactly equal G1 and <= 1.05x W0.
9. Negative-control object recall regression no worse than -0.05.
10. Negative-control signal regression no worse than -0.05.
11. Provenance reversibility = 100% for every condition.
12. Final duplicate-object rate = 0 for every condition.
13. X1 mean flat-cross returned-context chars <= 1.10x G2.

Observed negative-control differences were exactly zero:

- X1-W0 object recall: `0.000`, 95% CI `[0.000, 0.000]` across 16 negative-control topics.
- X1-G1 signal recall: `0.000`, 95% CI `[0.000, 0.000]` across 16 negative-control topics.

## Complexity result

The important result is not merely that X1 matched G2 quality on this mechanism corpus. It did so without G2's overlapping-window index.

- W0 indexed chars: `765,932`.
- G1 indexed chars: `763,580`.
- X1 indexed chars: `763,580` — **exactly G1**.
- G2 indexed chars: `1,383,483` — **1.806x W0**.

On the flat-cross region, X1 and G2 returned exactly the same mean context characters (`877.2917`) and both achieved signal recall@5 = `1.0`.

This supports the minimum-architecture hypothesis:

> rank compact structural units first; expand only the winning context at query time; do not pre-index overlapping windows unless future evidence shows a need.

## Interpretation ceiling

Evidence grade remains **controlled synthetic mechanism confirmation**. The corpus is author-designed and specifically stresses lexical dilution, lures, structural boundaries, and adjacent-span recovery. No model answer quality and no realistic user workload were measured in R1.

Therefore the next justified step is:

1. implement X1 semantics in the real core behind an explicit non-default/shadow mode;
2. prove production-core equivalence to the frozen X1 mechanism with deterministic tests;
3. use realistic/dogfood workloads to compare the default W0 path and X1 shadow path without changing user-visible answers by default;
4. only promote X1 if realistic evidence supports the change.

Do **not** use this result to justify vectors, graphs, learned reranking, or persistent compiled state.
