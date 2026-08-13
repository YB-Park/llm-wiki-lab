# E011 Stage 1A preregistration v0

Status: **pre-scoring**. No E011 model result has been observed.

## Research question

Does persistent topic synthesis have a credible static lifecycle-value region over raw evidence, before paying any update/maintenance cost?

## Null

For the tested workloads, compiled conditions do not provide a repeatable quality/effort advantage large enough to repay their one-time build cost over strong raw baselines.

## Experimental unit

The independent cluster is the **topic scenario**. Conditions, two corpus scales, and three query classes are paired within topic. Query rows are not treated as independent experimental units.

Stage 1A is a mechanism/value pilot intended to detect large crossover effects, not production evidence.

### Sample-size rationale

Use 12 topic clusters as a deliberately bounded falsification pilot. This is not powered to distinguish small effects. A narrow advantage in only a few topics is not enough to justify architecture. Stage 1A should advance the compiled-layer hypothesis only when the value region is broad enough to remain visible in topic-level paired effects, uncertainty intervals, and the frozen lifecycle regimes.

A surviving value region still requires replication on a materially different workload and, for architecture-level claims, a changed build or answer model axis before it becomes decision-grade evidence.

## Corpus plan

Use 12 fictional topic scenarios. Each topic has a stable answerable core plus near-relevant and irrelevant distractors.

Two nested scales:

- `small`: 8 raw documents per topic;
- `large`: 32 raw documents per topic; the first 8 are identical to small and the added documents increase redundancy, lexical competition, and navigation/context burden without changing the core ground truth.

Each topic has three fixed queries:

1. `exact_provenance` — recover an exact fact and its source ID;
2. `global_synthesis` — recover a fixed set of distributed topic-level factors;
3. `decision_rationale` — connect multiple distributed facts to recover why a decision was made.

Queries are hidden from the compilation prompt. The synthesis is built as a reusable topic artifact, not as a question-specific answer cache.

## Conditions

### R0 — raw lexical

Deterministic lexical retrieval over the full corpus at the current scale. Supply top-k raw documents to the answer model.

### R1 — raw topic-context ceiling

Supply every raw document belonging to the queried topic at the current scale. This intentionally strong baseline removes lexical-retrieval failure and asks whether precompilation itself adds value.

### C0 — compiled only

Build one minimal durable synthesis per topic/scale from exactly the same topic documents visible to R1. Query using only that synthesis.

The compiler must preserve source IDs for factual claims but receives no future questions or answer keys.

### C1 — compiled + raw lexical

Use the same compiled synthesis as C0 plus the same lexical top-k raw evidence as R0.

No conditional agentic fallback is allowed in Stage 1A; C1 always receives both layers so routing policy is not another variable.

## Fixed answering model

Use `gpt-5.6-luna` as experimental equipment for build and answer calls. Architecture conclusions remain model-conditional until replicated.

All conditions use one shared answer contract and prompt except for clearly labeled context sections.

## Retrieval

Lexical retrieval must be deterministic and model-free. Tokenizer, ranking formula, tie-breaking, and top-k are frozen before scored calls.

The initial top-k=6 candidate was rejected by corpus-only red-team diagnostics as an unnecessarily weak large-scale raw baseline. `retrieval-red-team-amendment-v1.md` freezes topic-scoped BM25 with `top-k=12`. Do not tune retrieval from scored answer quality.

## Primary quality outcomes

Ground truth is deterministic/author-generated synthetic metadata.

Report separately:

- required answer-signal coverage;
- strict all-required-signals pass;
- required source-ID coverage for provenance-bearing queries;
- structured answer-contract failures;
- unsupported/unknown behavior where the query contract defines it.

Do not collapse these into one weighted quality score.

No LLM-as-judge metric is used in Stage 1A primary analysis. The deterministic corpus contract is sufficient for this gate. Any later semantic judgment is exploratory and cannot rewrite the frozen primary result.

## Cost / effort outcomes

Report separately:

- compilation calls and input/output tokens;
- answer calls and input/output tokens;
- wall time;
- compiled artifact bytes;
- number of raw documents exposed to the answer model;
- lexical retrieval payload size.

Telemetry is adapter-level measurement, not assumed dollar billing truth.

## Reuse economics

One **topic revisit** is the fixed three-query bundle for a topic at one scale.

Freeze three reuse regimes before scoring:

- `N=1` — one-off / rare revisit;
- `N=3` — occasional reuse;
- `N=10` — high reuse.

Do not rerun identical questions to simulate these regimes. Replay lifecycle economics from the measured one-time build cost and the measured three-query bundle cost.

For each compiled-vs-raw comparison, also report whether a positive token break-even count exists:

`compiled_build + N * compiled_query_bundle <= N * raw_query_bundle`

If compiled query cost is not lower, token break-even is `none`.

A cost break-even is not a value win when compiled quality is materially worse. Quality and cost remain a Pareto analysis.

Primary causal-style paired comparisons:

- `C0 vs R1` — precompiled synthesis versus direct access to the same topic evidence;
- `C1 vs R0` — incremental value of durable synthesis when the same lexical raw evidence is already available.

The architecture-level value frontier nevertheless compares all four conditions at `N in {1,3,10}`. A compiled condition earns a candidate value region only if it is non-dominated by the raw conditions on the relevant quality/cost dimensions.

## Statistical plan

- topic scenario is the bootstrap/paired unit;
- report per-topic paired differences and scenario-level bootstrap intervals for headline quality differences;
- scale/query-class breakdowns are secondary diagnostics unless explicitly stated otherwise before scoring;
- do not treat 72 query rows as 72 independent samples;
- no multiplicity-adjusted significance hunt is used: the headline paired comparisons are fixed above, while class/scale cells remain diagnostic;
- point estimates and uncertainty are interpreted as effect evidence, not pass/fail p-values.

Follow `docs/08-statistical-analysis-standard.md`.

## Evidence grade and replication trigger

Stage 1A can produce at most **controlled pilot / benchmark evidence** because it uses synthetic author ground truth, oracle topic grouping, a static corpus, and the same model family for compilation and answering.

If a compiled condition survives the Value Gate, the next evidence step is not automatic architecture adoption. Replicate the surviving workload region on a materially different realistic/shadow workload. Any architecture-critical claim that depends on model behavior should additionally change the compiler or answer model axis.

## Kill / narrow criteria

Stage 1A does **not** justify detailed Wiki representation work unless at least one compiled condition shows a credible value region: comparable-or-better paired quality plus a material query-effort/token reduction or quality gain that makes the lifecycle trade plausible at one or more frozen reuse regimes.

If no compiled condition is non-dominated at `N=1`, `N=3`, or `N=10`, stop Stage 1B and prefer raw source-of-record + retrieval + selective/on-demand synthesis as the default hypothesis.

If advantage appears only for global/high-reuse workloads, narrow compilation to those classes rather than universalizing it.

## Conditional next stage

Only if Stage 1A survives, Stage 1B may add one controlled update wave to test whether maintenance destroys the static advantage.

Do not preregister detailed E001 representation variants or E009B automation as part of Stage 1A.
