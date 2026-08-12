# E007 Scoring Protocol v0

Status: frozen scoring design before first scored run
Date: 2026-08-12

## 1. Separation of roles

E007 uses three different evaluation layers.

### Layer A — maintenance-time deterministic regression

Used only by C4 as part of the experimental condition.

- 20 queries from deterministic-friendly classes
- rules frozen in `corpus/deterministic-checks.json`
- no LLM judge
- only previously passing queries can become regression gates

This layer can change the C4 wiki because that is exactly the mechanism being tested.

### Layer B — post-hoc deterministic scoring

Applied equally to every condition after outputs are produced.

- the same 20 deterministic rules,
- source-ID ownership checks where specified,
- no influence on wiki maintenance outside C4's explicitly defined regression gate.

### Layer C — post-hoc semantic scoring

Used for the 10 `global_synthesis` and `multi_hop` queries and for selected semantic integrity audits.

Layer C **never feeds back into an E007 v0 run**. It exists only to measure results.

---

## 2. Why we do not use an LLM judge inside C1–C3

Adding a semantic judge to every maintenance step would confound:

- wiki generation policy,
- verifier quality,
- judge quality,
- and maintenance cost.

The Trust Gate first asks whether source grounding, transition verification, and deterministic behavioral regression materially change failure behavior. Richer semantic judging is analysis, not hidden maintenance.

---

## 3. Semantic query score

For each global-synthesis or multi-hop answer, the evaluator assigns:

### Correctness

- `2` — satisfies the rubric's material requirements with no material factual error,
- `1` — partially correct but omits a material required relationship/fact or contains a minor non-central error,
- `0` — materially incorrect, unsupported, confuses entities/time/source ownership, or fails the central task.

### Omission flag

`true` when the answer fails because required evidence that should be available is absent from the answer/evidence path.

### Unsupported-claim flag

`true` when the answer adds a material factual or causal claim not supported by evaluator ground truth/source material.

### Temporal-error flag

`true` when the answer incorrectly collapses historical/current/corrected/disputed state.

### Entity-conflation flag

`true` when Aster/Aurora, Astra, ASTR-1, ASTR1, or another distinct identity is incorrectly merged.

The evaluator also records a short rationale referencing fact/source IDs, not free-form new facts.

---

## 4. Blind evaluation input

The semantic evaluator sees:

- query ID and question,
- the candidate answer and its source IDs,
- the query rubric,
- only the evaluator facts/sources relevant to the rubric,
- **no condition label** (`C0`–`C4`),
- no maintenance prompt,
- no token/cost information,
- no expected hypothesis direction.

This reduces bias toward a favored architecture.

---

## 5. Evaluator method

Preferred procedure for the first scored family:

1. Pin one evaluator model/configuration for all conditions, distinct from condition identity.
2. Run two independent evaluator passes for Layer C when budget permits.
3. If the two passes disagree on correctness by more than one point, or disagree on a major error flag, route the item to human adjudication.
4. Human adjudication uses the same blinded packet and ground-truth rubric.

If a second evaluator pass is too expensive, use one pass plus the deterministic human-audit sample below. The selected mode must be frozen before scored runs.

The evaluator model may be the same model family used by the experiment if necessary, but this limitation must be reported. A different fixed evaluator is preferable for reducing self-preference bias.

---

## 6. Deterministic human-audit sample

To prevent cherry-picking, sampled audits are selected by stable hashing rather than researcher choice.

For each `(run_id, query_id)` semantic item:

```text
sha256(run_id + ':' + query_id)
```

Interpret the first 8 hex digits as an integer. Audit the item when:

```text
value mod 5 == 0
```

This yields an approximately 20% reproducible sample.

Additionally audit:

- every semantic item where two evaluator passes materially disagree,
- every item with evaluator parse failure,
- every item involved in an unexpected headline conclusion before publishing that conclusion.

Human audit changes the **score record**, never the original answer/wiki artifact.

---

## 7. Integrity metrics from wiki states

Query accuracy alone does not measure persistent-state quality.

Post-hoc state audits should also sample/final-state check:

- unsupported exact claims,
- facts required by delayed probes but missing from derived state,
- unresolved conflicts incorrectly collapsed,
- obsolete facts presented as current,
- source IDs attached to the wrong claim,
- Aster/Astra/ASTR-1/ASTR1 conflation.

Where these can be checked deterministically, prefer deterministic checks. LLM semantic audit is reserved for genuinely semantic cases.

---

## 8. Regression metric

A regression is counted when a query that previously passed its frozen scoring rule fails after a later maintenance wave without a legitimate world-state reason.

For temporal queries, an expected answer can legitimately change as new evidence arrives. The query/rubric semantics decide whether a change is a regression; simple string equality with an old answer is not sufficient.

C4's online regression gate uses only the frozen deterministic set. Post-hoc analysis may identify additional semantic regressions but must not retroactively alter the run.

---

## 9. Cost metrics

Cost is aggregated from Copilot CLI OpenTelemetry and harness metadata.

Per call and cumulatively record when available:

- requested model,
- resolved model,
- input tokens,
- output tokens,
- cache read/creation tokens,
- inference call count,
- turn count,
- Copilot cost,
- AI units,
- wall time.

Report cost separately for:

- update/compilation,
- transition verification,
- transition repair,
- regression query,
- regression repair,
- primary answering.

The primary economic comparison is cumulative lifecycle cost by condition and wave.

---

## 10. Headline reporting

Do not reduce E007 to one leaderboard score.

At minimum report a vector/frontier containing:

- deterministic query pass rate,
- semantic correctness distribution,
- omission rate,
- unsupported-claim rate,
- temporal/source-ownership errors,
- regressions,
- repair usage/residual issues,
- cumulative input/output tokens,
- cumulative AI units/cost if exposed,
- number of semantic maintenance calls.

A condition is not "better" merely because it minimizes one metric.

---

## 11. Protocol version rule

Any change to scoring rules after first scored results exist creates `scoring-protocol-v1.md`. v0 outputs remain scored under v0 as well as any later re-analysis; they are never silently relabeled.
