# E023 G1b execution addendum v0

Status before semantic generation: **FROZEN EXECUTION CANDIDATE / 0 MODEL CALLS ON PR**.

This addendum completes `g1b-preregistration-v0.md`. It must merge to `main` before the first G1b semantic call.

## Fixed target and budget

- exact model: `gpt-5.6-luna`;
- target questions: `Q001`, `Q002`, `Q004`, `Q010` only;
- baseline answers are reused from frozen G1a; no baseline reruns;
- max calls per target: one evidence-gap planner + one selector + one composer;
- maximum semantic attempts: **12**;
- semantic rerolls: **0**;
- final full-evidence source limit: **5**, equal to G1a;
- initial retrieval: production-shaped BM25 exact-query top 5;
- follow-up search queries: 0–2;
- each follow-up retrieval contributes its top 3 to the temporary candidate pool;
- planner/selector snippets: at most 320 characters per source.

## Initial hit presentation

The planner sees only:

- exact question;
- initial five source IDs;
- source title, kind, date;
- a query-focused bounded snippet from each initial source.

The planner does **not** see:

- required/forbidden gold IDs;
- frozen adjudication;
- sources outside the initial five;
- full corpus;
- prior G1a planner output;
- the final answer.

Synthetic source IDs are allowed as handles for already-visible hits, but planner follow-up queries must not contain `Sxxx` handles.

## Evidence-gap planner contract

Return JSON only:

```json
{
  "missing_or_ambiguous_relation": "...",
  "queries": ["...", "..."]
}
```

Rules:

- `missing_or_ambiguous_relation` is a non-empty <=240-character description of what evidence would make the answer safer or more complete;
- `queries` contains 0–2 unique non-empty strings, each <=160 characters;
- do not answer the user's question;
- do not claim access to sources not shown;
- do not emit source IDs in search queries;
- if the initial hits are sufficient, `queries` may be empty.

Invalid output is a frozen contract failure; no reroll.

## Candidate-pool construction

For each valid follow-up query:

- run the same BM25 over all 18 frozen source texts;
- take top 3;
- union with the initial top 5;
- deduplicate by source ID;
- retain deterministic first-seen order: initial hits first, then follow-up-query results in query order/rank order.

The candidate pool is temporary and is not semantic memory.

## Selector contract

The selector sees:

- exact question;
- planner `missing_or_ambiguous_relation`, explicitly marked **working state / not evidence**;
- candidate-pool IDs, title/kind/date, bounded snippets;
- whether each candidate was in the initial top 5.

Return JSON only:

```json
{"selected_source_ids": ["S001", "S004"]}
```

Rules:

- select 1–5 unique IDs from the supplied candidate pool only;
- choose evidence that is sufficient and discriminative for the user's question;
- prefer an explicit bridge/attribution/temporal/rationale source over circumstantial similarity when the distinction is load-bearing;
- do not answer the question;
- planner working state is not evidence;
- do not select an ID merely because it looks like a gold label; IDs have no semantics beyond handles.

Invalid output is a frozen contract failure; no reroll.

## Composer contract

Use `run_g1.py`'s existing `composer_prompt` and `parse_composer` unchanged.

This is deliberate. G1b tests **retrieval/selection**, not a new identity-specific answer policy. If retrieval improves but the unchanged composer still performs a semantic upgrade, that becomes evidence for a separate composition-policy gate rather than permission to modify the result posthoc.

## Frozen automatic measurements

For each target:

- initial selected IDs and frozen G1a initial context equality;
- initial required recall;
- planner receipt/gap/queries;
- each follow-up BM25 ranking;
- temporary candidate IDs;
- whether the previously missing required source entered candidate pool;
- selector receipt/final IDs;
- final required recall;
- whether the previously missing required source entered final context;
- forbidden-conflation sources in final context;
- composer contract/citations/model receipt;
- exact model-call attempts and elapsed time.

Gold required/forbidden IDs are evaluator-only and are never inserted into planner/selector/composer prompts.

## Semantic adjudication and promotion

Use the already frozen G1b rules:

G1b is earned for further consideration only if:

1. missing required source enters final context for >=3/4 targets;
2. Q001 improves from CRITICAL_ERROR to at least PARTIAL without unsupported identity merge;
3. Q002/Q004/Q010 do not regress from PASS;
4. zero new critical errors;
5. all contracts hold with zero rerolls.

A retrieval improvement is not automatically a semantic improvement.

## Evidence publication

The main/push workflow uploads the raw result artifact and commits a unique immutable evidence directory:

`experiments/E023-generality-retrieval-composition/evidence/g1b-run-<run_id>/`

containing result JSON, run metadata, and result SHA-256.

The evidence directory path is deliberately excluded from the paid workflow's push trigger, so publishing result evidence cannot trigger another G1b execution.

## Non-authorization

No G1b outcome directly authorizes G2 persistence, an entity/graph schema, automatic identity routing, vector defaults, or product rollout of the planner/selector loop.
