# E014 — Lexical retrieval granularity gate — preregistration v0

Status: **preregistered before held-out scoring**

Date: 2026-08-14

## Question

Does deterministic finer-grained lexical retrieval materially improve retrieval quality/efficiency over the current whole-content-object BM25 baseline under long/noisy evidence, while preserving exact provenance and avoiding duplicate-content ranking artifacts?

This is a **cheap-baseline gate**. It must run before adding embeddings, a vector database, graph retrieval, learned reranking, or any other semantic retrieval layer.

## Non-evidentiary development preflight disclosure

Before this preregistration, a separate synthetic development sandbox was inspected and used to choose the primary granular rule. The development sandbox showed that single-paragraph units can fail when a relevant phrase crosses a paragraph boundary, so the primary candidate was frozen as `G2` below.

**Development results are not evidence and must not be included in the E014 gate.**

The official Stage A score uses a distinct held-out corpus whose seed, vocabulary, lure ordering, long-document lengths, and flat-document cross-boundary locations differ from development. The held-out corpus is frozen by canonical SHA-256 before any held-out scoring call.

## Experimental unit and dependence

- Primary experimental unit: **topic scenario**.
- Held-out topics: **20**.
- Four corpus shapes, 5 topics each: `short`, `structured`, `flat`, `monolithic`.
- Each topic has 3 paired queries: `exact_provenance`, `synthesis`, `decision_history`.
- Total held-out queries: 60.
- Query rows within a topic are **not independent**; paired uncertainty is bootstrapped at topic level.

This is a synthetic mechanism benchmark, not a realistic-workload estimate.

## Frozen corpus roles

### Target shapes

`structured` and `flat` are the primary target region. They contain long/noisy objects with stable structural boundaries that a deterministic granular index can exploit.

### Negative controls

`short` and `monolithic` are negative/control regions.

- `short`: whole-object retrieval should already be strong.
- `monolithic`: long text has no paragraph/heading structure useful to G2, so a granular rule should not magically improve it.

A useful granular rule must improve the target region without materially regressing these controls.

## Frozen lexical-lure mechanism

Each topic contains relevant objects plus 1–5 short lexical lure objects per query class. Lures repeat two query terms while omitting one required term and contain no required gold signal.

This intentionally tests a known BM25 failure mechanism: a long relevant object containing a concentrated relevant passage can be outranked by short objects with repeated partial lexical overlap.

Held-out lure ordering/counts differ from development. Query text never contains `GOLD_` or `LURE_` markers.

## Conditions

All conditions operate on the same current immutable content objects and preserve the same `object_id -> source_ids` provenance metadata.

### W0 — whole-object BM25 baseline

- One BM25 scoring unit per content object.
- Tokenizer: `[0-9a-zA-Z_가-힣]+`, case-folded.
- BM25: `k1=1.5`, `b=0.75`.
- Final object ranking is normal BM25 score.
- Returned context mirrors the current core behavior: choose the paragraph with greatest query-token overlap, earliest paragraph as tie-break, truncate to 320 characters.

`validate_prescore.py` must prove W0 order/scores equal the current dogfood core on a separate non-held-out fixture.

### G1 — diagnostic single-granularity baseline

Not primary. Used only to test whether adjacent-pair windows solve cross-boundary fragmentation.

- If a document has >=2 ATX headings: section units.
- Otherwise, if >2 paragraphs: individual paragraph units.
- Otherwise: whole object.
- BM25 over retrieval units using the same tokenizer/k1/b.
- Final object score = maximum score among its units.
- One final hit per object.

### G2 — primary deterministic granular candidate

Frozen after development preflight, before held-out scoring.

- If a document has >=2 ATX headings: section units.
- Otherwise, if >2 paragraphs: index **both** individual paragraphs and every adjacent two-paragraph window.
- Otherwise: whole object.
- Same BM25 tokenizer/k1/b.
- Final object score = maximum score among its units.
- One final hit per object.
- Returned context = winning unit truncated to 320 characters.

G2 parameters may not be retuned after held-out scoring.

## Provenance invariant

Every retrieval unit must deterministically map back to:

- one `doc_id` / `object_id`,
- all source IDs attached to that object,
- exact character start/end offsets,
- a stable structural locator.

For every frozen unit, `document_text[start:end] == unit_text` must hold.

Final top-k results must contain zero duplicate object IDs even when one object produces many internal retrieval units or has multiple provenance source IDs.

## Primary metrics

Primary comparison: **G2 - W0**, paired at topic level over target shapes (`structured`, `flat`).

1. `required_object_recall_at5` — primary quality metric.
2. `required_object_mrr` — mean reciprocal rank over each query's required objects.
3. `signal_recall_at5` — fraction of required frozen signals present in the returned top-5 contexts.

For each metric, report topic-level paired point difference and percentile bootstrap 95% CI.

Bootstrap:

- 20,000 topic-level resamples;
- seed `20260815`;
- no query-row bootstrap.

## Secondary diagnostics

- required-object recall@8;
- all-required@5;
- top-1 lure-context rate;
- context characters across top 5;
- unit count and indexed-character multiplier vs W0;
- provenance reversibility;
- final duplicate-object rate;
- G1 vs G2 recall on frozen flat cross-boundary decision queries;
- breakdown by corpus shape and query class.

No LLM judge is used in Stage A.

## Frozen gate

G2 survives the deterministic gate only if **all** checks pass:

1. target-shape recall@5 gain `G2-W0 >= +0.15`;
2. target-shape recall@5 paired-bootstrap 95% CI lower bound `> 0`;
3. target-shape MRR gain `>= +0.10`;
4. negative-control (`short` + `monolithic`) recall@5 difference `>= -0.05`;
5. provenance reversibility = 100% for W0/G1/G2;
6. final duplicate-object rate = 0 for all conditions;
7. G2 indexed-character multiplier vs W0 `<= 3.0x`;
8. frozen cross-boundary flat-decision recall@5 improves over G1 by at least `+0.10`.

If any condition fails, Stage A outcome is `DOES_NOT_SURVIVE_DETERMINISTIC_GATE`.

No post-score threshold, top-k, section rule, window size, overlap, BM25 parameter, or corpus edit is permitted.

## Interpretation ceiling

Passing means only:

> deterministic structural lexical granularity has a credible mechanism advantage over whole-object BM25 in this held-out synthetic target region.

It does **not** prove:

- realistic user value;
- answer-quality improvement;
- need for a vector store;
- need for a graph store;
- need for embeddings or semantic reranking;
- permission to enable persistent compiled Wiki state.

Failure means the current granular rule has not earned product complexity. We do not tune it on the held-out score.

## Stage B boundary

Stage B is optional and may run only if Stage A survives.

If opened, Stage B must use the frozen W0 and G2 retrieval outputs/parameters and a separately frozen answer-quality protocol. Model calls must be paired, bounded, and may not be used to retune retrieval.

A Stage A pass alone is sufficient to justify a **shadow/experimental deterministic granular index**, not a default production retrieval change.

## Relationship to core identity

ADR-0003/ADR-0004 remain upstream:

- current/history projection is held constant;
- content object is the lexical ranking object;
- multiple source IDs attached to identical bytes remain provenance metadata only;
- provenance multiplicity is never a BM25 document-count or corroboration bonus.

## Evidence grade

Target grade for Stage A: **controlled held-out mechanism benchmark**.

Any architecture claim beyond that requires non-tuned corpus replication and/or realistic workload evidence under `docs/08-statistical-analysis-standard.md`.