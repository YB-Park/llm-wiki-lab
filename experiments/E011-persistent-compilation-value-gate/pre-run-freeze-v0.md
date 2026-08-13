# E011 Stage 1A pre-run freeze v0

Status: **FROZEN BEFORE SCORED MODEL CALLS**

At this freeze point, no E011 corpus build or scored answer result has been observed. Only deterministic corpus/retrieval diagnostics and CI self-tests have run.

## Research purpose

Test whether persistent topic compilation deserves to exist for any tested workload region before investing in detailed Wiki representation, maintenance, or stronger automation.

A negative result is valid and may stop the compiled-Wiki branch.

## Frozen corpus

- 12 independent fictional topic scenarios
- small scale: 8 documents/topic
- large scale: 32 documents/topic, containing the unchanged small core
- 3 queries/topic: exact/provenance, global synthesis, decision rationale
- generated documents: 384
- generated queries: 36

Content fingerprints:

- documents SHA-256: `356ee876645e306a1a875211f2a2e9a3831d46ec11c75323d51f56e4427ed48d`
- queries SHA-256: `41fd6241483207f02a83a954d788d54ad60e98dc90dc6a7591d39457bcf99c71`

The compiler never receives future questions or answer keys.

## Frozen conditions

- `R0`: topic-scoped BM25 top-k raw evidence
- `R1`: all raw documents in the topic at the current scale
- `C0`: one generic durable topic synthesis only
- `C1`: the same durable synthesis plus the exact R0 raw evidence

No vector store, graph, verifier, repair, regression gate, conditional agentic fallback, or detailed Wiki schema is allowed in Stage 1A.

## Frozen lexical baseline

`retrieval-red-team-amendment-v1.md` supersedes the initial top-k candidate.

- tokenizer: lowercase regex `[a-z0-9]+`
- BM25 `k1=1.5`, `b=0.75`
- deterministic source-ID tie break
- topic-scoped retrieval
- `top-k=12`

Prescore corpus-only diagnostics:

- small exact/global/decision: complete required-signal payload, 12/12 strict in each class
- large exact: complete payload and approval source 12/12
- large global: complete payload 12/12
- large decision rationale: 0.250 mean required-signal payload, 0/12 strict

Do not tune retrieval using scored answer outcomes.

## Frozen model and prompts

Experimental equipment: `gpt-5.6-luna`.

One generic compiler prompt is used for all compiled artifacts. One shared answer prompt/JSON contract is used across all four conditions.

Malformed answer JSON or answer-contract failure is a scored invalid outcome and is not rerolled for a cleaner semantic response.

Source IDs returned by the answer must be visible in supplied context. Compiled-state diagnostics separately report source IDs invented by the compiler.

## Frozen call semantics

- build order seed: `20260814`
- logical answer order seed: `20260815`
- 24 logical compilation calls: 12 topics x 2 scales
- 288 logical answer tasks: 12 topics x 2 scales x 3 questions x 4 conditions

Exact duplicate answer prompts share one actual model response. This is intentional paired-control behavior: byte-identical evidence/question prompts should not differ only because of model sampling. Small-scale R0 and R1 are guaranteed identical by CI and therefore share responses.

This deduplication changes experimental execution cost, not the counterfactual lifecycle cost assigned to each architecture. Post-score economics count the measured query call cost for each logical condition as if that condition were deployed independently.

## Frozen primary quality outcomes

Report separately:

- strict answer pass
- required answer-signal coverage
- exact/provenance source-ID coverage
- structured answer-contract invalid count

No weighted winner score. No LLM-as-judge primary metric.

Secondary predeclared diagnostics include compiled-state required-signal/source preservation, invented source IDs, state/raw byte ratio, scale breakdown, and query-class breakdown.

## Frozen economics

One topic revisit is the three-query bundle for one topic at one scale.

Reuse regimes:

- `N=1`
- `N=3`
- `N=10`

Use measured build/query input+output token counts as a token-volume proxy. Do not interpret adapter telemetry as dollar billing without separate field validation.

Report:

- build/query tokens
- wall time
- compiled state bytes
- raw documents exposed
- C0-vs-R1 and C1-vs-R0 break-even revisit counts where finite
- four-condition Pareto frontier at N=1/3/10

A token break-even is not a value win when quality is materially worse.

## Frozen statistical interpretation

- independent cluster: topic scenario (`n=12`)
- conditions, scale, and query class are paired within topic
- scenario-level paired bootstrap for headline C0-R1 and C1-R0 quality differences
- scale/class cells are secondary diagnostics
- 72 rows/condition are not treated as 72 independent samples
- Stage 1A is controlled pilot/benchmark evidence only

## Stop / narrow rule

If no compiled condition has a credible non-dominated region at N=1/3/10, do not open Stage 1B. Default hypothesis becomes raw source-of-record + retrieval + selective/on-demand synthesis.

If compilation survives only for a narrow workload such as large-scale decision recovery or high reuse, carry forward only that workload region.

Even a surviving Stage 1A result requires realistic/shadow-workload replication; architecture-critical model-dependent claims also require a changed model axis.

## Runtime failure policy

- infrastructure/transport failure: stop with sanitized synthetic call ID; preserve local artifact; archive that incomplete attempt; retry only the same frozen call
- semantic malformed output: record invalid; no clean-result retry
- empty compiler output: infrastructure/contract stop; preserve attempt
- fixture mismatch on resume: hard stop

Raw prompts, responses, OTel, local paths, usernames, and free-form compiled notes remain local.

## No-change rule after scoring starts

Do not change based on scored outcomes:

- corpus/generator or ground truth
- BM25/tokenizer/top-k
- compiler prompt
- answer prompt/contract
- conditions
- model
- build/answer order seeds
- scoring semantics
- N=1/3/10 reuse regimes
- primary paired comparisons
- post-score analysis semantics

Infrastructure-only defects may receive explicit amendments while preserving all existing scored artifacts. New semantic ideas become follow-up experiments rather than edits to Stage 1A.
