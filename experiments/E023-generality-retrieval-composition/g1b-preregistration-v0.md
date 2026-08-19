# E023 G1b preregistration v0 — evidence-follow retrieval

Status before semantic generation: **PREREGISTERED CANDIDATE / ZERO MODEL CALLS ON THIS PR**.

G1a is complete and `NOT_EARNED`. This follow-up stays inside **G1 Retrieval / Composition**. It does not test persistence, entities, graphs, vectors, or automatic durable identity.

## 1. Frozen causal question

For the four E023 questions where **both frozen G1a arms had incomplete required-source recall@5**, can an evidence-aware search loop recover missing authoritative evidence and select a better final top-5 context than blind pre-retrieval query expansion?

The four questions are selected **only by the preregistered retrieval condition** `A recall@5 < 1 AND C recall@5 < 1` in frozen run `32215941344`:

- Q001 — missing explicit identity bridge S004;
- Q002 — missing repeated meeting evidence S003;
- Q004 — missing Operations rationale S008;
- Q010 — missing repeated meeting evidence S003.

No other semantic outcome is used to choose the subset. The subset intentionally contains one critical semantic failure (Q001) and three semantic PASS cases, so retrieval improvement is not allowed to masquerade automatically as answer-quality improvement.

## 2. Hypothesis under test

G1a planned **before seeing evidence**:

> question -> blind query rewrites -> BM25 -> consensus RRF -> fixed top-5 -> answer

G1b instead tests a more Agent-like loop:

> question -> initial retrieval -> inspect bounded hits/snippets -> state the missing/ambiguous relation -> targeted follow-up retrieval -> select final evidence -> answer

The hypothesis is not “more LLM calls are better.” It is:

> **A planner that can inspect what was already found can target a concrete evidence gap more effectively than blind query expansion, while keeping the final full-evidence source count fixed.**

## 3. Frozen architecture boundary

G1b creates **no persistent semantic state**.

It may use temporary planner/selector text inside one question, then discards it. No temporary output becomes RAW evidence, HUMAN_KNOWLEDGE, source-note input, or future-query evidence.

The Authority Core and Dogfood 0.1.16 product remain unchanged.

## 4. Frozen target subset and baseline

Baseline semantic outcomes are the immutable G1a A-arm adjudication from `adjudication-v0.json`:

- Q001: CRITICAL_ERROR;
- Q002: PASS;
- Q004: PASS;
- Q010: PASS.

Baseline retrieval context is the immutable G1a A exact-query BM25 top-5 for each question.

No baseline answer is rerun. G1b spends calls only on the new evidence-follow arm.

## 5. G1b loop — execution shape to freeze before calls

A separate execution addendum must freeze exact prompts, output schemas, snippet limits, BM25/fusion mechanics, and CLI workflow before the first semantic call. It may not change the following structure.

For each of the four frozen questions:

### Step 1 — initial retrieval — zero model calls

- exact user question;
- same production-shaped BM25 used by G1a;
- initial top 5 sources;
- expose bounded title/kind/date + retrieval snippet for those five sources to the follow-up planner;
- do **not** expose frozen required/forbidden IDs, gold answers, adjudication, or full corpus.

### Step 2 — evidence-gap planner — one model call

Planner sees the question and initial five hit summaries/snippets.

It returns a bounded machine-readable request containing:

- a concise `missing_or_ambiguous_relation` description;
- 0–2 targeted follow-up search queries;
- no answer;
- no invented source IDs.

The planner must be allowed to say that no follow-up search is necessary.

### Step 3 — deterministic follow-up retrieval — zero model calls

Run the same BM25 retrieval for each follow-up query. Add only a bounded number of top follow-up candidates to a temporary candidate pool.

### Step 4 — evidence selector — one model call

Selector sees:

- exact question;
- bounded metadata/snippets for the temporary candidate pool;
- which five sources came from initial retrieval;
- the planner's `missing_or_ambiguous_relation` as working state, explicitly not evidence.

Selector chooses **at most 5 source IDs** for final full evidence. It must not answer the question or create a semantic dossier.

This keeps the final source-count budget equal to G1a top-5. The purpose is to test evidence-aware replacement/selection, not “just add a sixth source.”

### Step 5 — composer — one model call

Use the **same G1a composer prompt and output contract** from `run_g1.py`, byte-for-byte except for the newly selected evidence context.

Do not add the identity-specific caution rule in G1b. That rule may be valuable, but adding it here would confound retrieval/selection with composition policy. If Q001 still overclaims after retrieval is improved or still lacks the bridge, consequence-sensitive composition must be tested separately.

Maximum: **3 semantic model calls per question / 12 calls total**.

Semantic rerolls: **0**.

## 6. Primary retrieval measurements

For each question record:

- initial top-5 IDs;
- planner gap description and follow-up queries;
- follow-up candidate IDs/ranks;
- final selected top <=5 IDs;
- required-source recall in initial context;
- required-source recall in final context;
- whether the previously missing required source was recovered into the candidate pool;
- whether it was selected into final context;
- frozen forbidden-conflation sources present in final context;
- full model-call count.

The runner/evaluator may know the frozen required IDs for **measurement only**. They must never be shown to planner, selector, or composer.

## 7. Semantic adjudication

Use the existing frozen question requirements and critical-error classes.

For the four G1b answers record PASS / PARTIAL / FAIL_RETRIEVAL / FAIL_COMPOSITION / CRITICAL_ERROR.

Q001 is especially important:

- if S004 is absent and the composer again confidently merges `J.H. Park` with `Jihoon Park`, it remains CRITICAL_ERROR;
- if S004 is absent and the answer explicitly says identity is not established, that is a trust improvement but remains retrieval-incomplete;
- if S004 is present and the answer correctly uses it to establish the identity while excluding S005, the critical G1a failure is repaired by evidence-follow retrieval/selection.

Do not score an unsupported merge as PASS merely because it matches frozen gold.

## 8. Promotion rule frozen before execution

G1b evidence-follow is **EARNED FOR FURTHER CONSIDERATION** only if all are true:

1. the previously missing required source is selected into final context for **at least 3 of 4** questions;
2. Q001 improves from `CRITICAL_ERROR` to at least `PARTIAL` without an unsupported identity merge;
3. Q002, Q004, and Q010 have **no semantic regression** from their frozen G1a PASS baselines;
4. G1b introduces **zero new critical errors**;
5. all planner/selector/composer calls respect the frozen contracts with zero semantic rerolls.

If criterion 1 fails, evidence-follow retrieval/selection is not earned on this targeted failure set.

If criterion 1 passes but Q001 remains a critical merge with S004 present, the remaining problem is composition/epistemic policy, not retrieval persistence.

If S004 cannot be recovered/selected, do not infer persistent identity is required; diagnose follow-up retrieval/selection first.

## 9. Explicit non-conclusions

No G1b outcome directly authorizes:

- G2 persistent dossiers;
- Entity/Relation/KnowledgeUnit schemas;
- graph storage;
- automatic alias merge/split;
- vector default changes;
- persistent identity cache;
- production rollout of an additional planner/selector call.

Even a G1b PASS only earns the hypothesis that **iterative evidence-follow is worth broader/natural validation**.

## 10. Cost/usage discipline

The execution addendum must cap G1b at **12 semantic model-call attempts**.

Record model calls exactly. Record tokens only if the transport exposes machine-readable usage. Record AI credits/premium requests only if upstream reports them. Never infer credits from calls/tokens.

This targeted follow-up deliberately avoids rerunning the six G1a questions that already had complete required-source recall@5.
