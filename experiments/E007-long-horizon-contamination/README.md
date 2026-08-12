# E007 — Long-Horizon Contamination / Trust Gate

Status: **PRE-REGISTERED — no results yet**
Date: 2026-08-12
Related: E007 in `docs/03-experiment-plan.md`, Issues #3 and #7

## 1. Research question

How do different LLM Wiki maintenance policies behave after repeated source ingestion, synthesis, retrieval, correction, and update cycles?

Specifically, how quickly do these failures appear and propagate?

- unsupported fabrication,
- compilation loss / omission,
- corruption of still-valid prior knowledge,
- stale/incorrect temporal state,
- source-ownership error,
- derived-error amplification,
- downstream query regression.

This experiment is the first gate because an attractive document structure is irrelevant if repeated maintenance cannot preserve trustworthy knowledge.

---

## 2. Primary hypotheses

These are directional hypotheses, not expected results.

### H1 — Recursive derived evidence increases contamination radius

Allowing derived wiki prose to serve as sufficient factual evidence for later synthesis will cause injected or naturally occurring synthesis errors to survive and propagate farther than policies that require a path back to primary evidence.

### H2 — Final-state grounding alone will miss preservation/omission failures

A verifier that checks only whether the final page is supported will fail to detect cases where valid old knowledge or important new knowledge silently disappears.

### H3 — Transition verification reduces persistent corruption

Checking `(old state + new evidence -> proposed state)` for coverage, preservation, and faithfulness will reduce persistent error compared with final-state lint/grounding alone.

### H4 — Regression queries detect useful failures not visible in document inspection

A behavioral test suite will detect lost answerability after rewrites even when prose remains coherent and source-grounded.

### H5 — Stronger protection has real lifecycle cost

More verification will consume additional tokens/model calls and may reject legitimate changes. The goal is a cost-quality frontier, not maximum checking at any price.

---

## 3. Experimental unit

One run is a complete multi-wave knowledge lifecycle:

```text
clean source corpus
  -> compile initial state
  -> query
  -> add evidence wave
  -> propose/update derived state
  -> verify according to condition
  -> query/regression
  -> repeat
```

A run must preserve all prompts, outputs, accepted/rejected candidate edits, metrics, and model/config identifiers needed for later analysis where available.

---

## 4. Controlled corpus

Use **Corpus C v0**, defined separately under `corpus/`.

The corpus must include ground-truth cases for:

- exact dates/numbers,
- single-source facts,
- repeated corroborated facts,
- aliases / confusable entities,
- real temporal changes,
- corrections of previously wrong information,
- unresolved source disagreement,
- plausible but unsupported inference,
- source-ownership traps,
- irrelevant distractors,
- facts that become query-relevant only in later waves,
- structural rename/split pressure.

Source text must not explicitly encode the scoring labels in a way visible to the model.

---

## 5. Knowledge waves

Minimum design: **6 waves**.

### W0 — initial clean state

Introduce basic entities, topics, exact facts, and relationships.

### W1 — reinforcement + distractors

Add corroborating information plus unrelated but lexically similar material.

### W2 — temporal changes

Add facts that legitimately supersede earlier current-state facts while preserving historical truth.

### W3 — corrections + disagreements

Correct at least one earlier source-derived belief and introduce at least one unresolved contradiction between credible sources.

### W4 — long-range dependencies

Add evidence whose significance depends on material from W0/W1 and ask queries requiring cross-wave synthesis.

### W5 — structural pressure + delayed questions

Create conditions that tempt page merge/split/rename and introduce questions requiring facts that were easy to omit during earlier compilation.

The exact number of source documents per wave will be fixed in the corpus manifest before the first experimental run.

---

## 6. Conditions

All conditions receive the same sources, wave order, query set, and base model family/settings where technically possible.

### C0 — Raw/search control

No durable LLM-derived wiki is maintained.

Use raw sources plus the experiment's baseline retrieval method. This establishes whether a maintained wiki is helping at all.

### C1 — Naive compiled wiki

- compile/synthesize from sources and existing wiki,
- derived pages may be reused as normal context/evidence,
- no explicit source-path requirement,
- no transition verifier,
- ordinary structural lint only.

Purpose: represent the failure-prone simple implementation we explicitly want to challenge.

### C2 — Source-grounded compiled wiki

- derived wiki guides navigation/synthesis,
- load-bearing factual promotion must retain a path to authoritative source material,
- derived page alone is insufficient evidence for new factual promotion,
- final-state grounding checks,
- no explicit old→new transition preservation check.

Purpose: isolate the value of source grounding.

### C3 — Transition-verified compiled wiki

C2 plus verification of proposed updates against:

- **coverage** — important new evidence is represented or intentionally deferred,
- **preservation** — still-valid old knowledge is not accidentally lost,
- **faithfulness** — new content is evidence-supported.

Rejected/flagged updates remain observable; they are not silently repaired outside the recorded procedure.

### C4 — Transition + behavioral regression

C3 plus a regression set containing:

- previously passing queries,
- delayed diagnostic probes,
- high-risk exact/temporal/provenance questions.

A candidate high-impact edit can be flagged/rejected when it causes defined regressions.

Purpose: estimate the marginal value and cost of behavioral testing.

---

## 7. Controlled error injection

Natural model errors are useful but not reproducible enough for causal comparison.

Therefore each run family also includes predefined injected faults introduced at controlled points.

Fault classes:

### I1 — fabricated exact value

Modify one derived exact number/date to a plausible unsupported alternative.

### I2 — omitted still-valid fact

Remove one prior fact that remains necessary for later queries.

### I3 — omitted new fact

Drop a new important fact during a wave update.

### I4 — false supersession

Mark a still-current fact as obsolete, or overwrite a historical change as though the earlier state had never existed.

### I5 — source ownership swap

Keep a fact present but attribute it to the wrong source.

### I6 — derived-only propagation seed

Insert a plausible unsupported interpretation into derived state and observe whether later pages/answers repeat or amplify it.

Injected faults must be identical across applicable conditions and clearly marked in run metadata, never in model-visible source text.

---

## 8. Query suite

Queries are fixed before the first run and divided into classes.

### Local / exact

Dates, numbers, names, direct attributes.

### Global / synthesis

Themes, cross-source comparisons, corpus-level conclusions.

### Multi-hop

Require combining facts from multiple sources/waves.

### Temporal

Current state, historical state, correction vs change-over-time.

### Provenance

Which source supports a claim; distinguish source ownership.

### Delayed probes

Ask for facts introduced early but never queried until W5. These directly measure compilation loss that ordinary early evaluation may miss.

### Negative / uncertainty

Cases where the correct answer is disputed, unknown, unsupported, or ambiguous.

Every scored query must have a ground-truth rubric defined before runs.

---

## 9. Primary metrics

### M1 — Unsupported claim rate

Fraction of scored factual claims not supportable by the authoritative source set.

### M2 — Important omission rate

Fraction of ground-truth facts required by the query/probe suite that become unavailable from the maintained derived state under the tested retrieval policy.

### M3 — Preservation failure rate

Still-valid knowledge present before an update but absent/corrupted after it without legitimate lifecycle reason.

### M4 — Temporal semantic error rate

Incorrect handling of current vs historical truth, correction, supersession, and disagreement.

### M5 — Source-ownership accuracy

Whether claims are attributed to the correct supporting source(s).

### M6 — Injected-error survival

How many subsequent waves/queries retain an injected error before detection or repair.

### M7 — Contamination radius

Number of distinct derived artifacts and answers downstream of an injected unsupported seed that repeat or rely on it.

### M8 — Regression rate

Fraction of previously passing queries that fail after a maintenance update.

### M9 — Repair radius

How many artifacts/operations are required to remove a rooted error and restore affected regressions.

---

## 10. Cost metrics

Track per condition and per wave:

- input tokens,
- output tokens,
- model calls,
- semantic verification calls,
- deterministic checks,
- candidate edits generated,
- candidate edits rejected/flagged,
- human interventions,
- repair operations,
- wall-clock latency where meaningful.

The primary cost view is **cumulative lifecycle cost**, not cost of a single query.

---

## 11. Human-review policy

Initial experiment should minimize discretionary human correction.

Allowed human actions:

- start/stop failed tooling,
- classify infrastructure errors,
- execute pre-specified review decisions where a condition explicitly includes human review.

Not allowed:

- silently rewrite a poor wiki page because it looks wrong,
- provide extra hints to one condition,
- adjust prompts after seeing which condition is losing without creating a new protocol version.

Every semantic intervention must be logged.

---

## 12. Repetition and model variance

Because LLM behavior is stochastic, one run is insufficient.

Before execution, select:

- a fixed model/configuration,
- temperature/sampling settings where exposed,
- minimum repeated runs per condition,
- randomization strategy if supported.

The exact repetition count will be chosen after a dry-run cost estimate **without looking at comparative outcome quality**.

If deterministic seeding is unavailable, preserve raw outputs and report distribution/variance rather than implying deterministic reproducibility.

---

## 13. Pass/fail interpretation

This experiment does **not** have a single pass threshold chosen in advance because we do not yet know the practical error/cost frontier.

Instead it answers:

1. Does naive recursive compilation exhibit materially greater persistent error than the raw/search control?
2. Does source grounding reduce propagation enough to justify its cost?
3. Does transition verification catch failures missed by final-state checks?
4. Do regression queries catch meaningful losses missed by semantic verification?
5. At what incremental lifecycle cost do those protections operate?

Any architecture recommendation must report both quality and cost.

---

## 14. Anti-overfitting rules

- Do not rewrite the corpus to favor a preferred architecture after results begin.
- New discovered failure cases go into a **future holdout extension**, not retroactively into the scored primary set.
- Prompt changes after initial runs require a new protocol/run version.
- Keep a holdout subset of delayed questions undisclosed to maintenance prompts.
- LLM-as-judge scoring must be paired with deterministic ground truth or sampled human audit where feasible.

---

## 15. Artifacts

Planned structure:

```text
experiments/E007-long-horizon-contamination/
  README.md                # this preregistration
  corpus/
    README.md
    manifest.json
    sources/
    ground-truth.json
  prompts/
  harness/
  runs/
  results/
  analysis.md
```

`analysis.md` must not be created as a conclusion until run artifacts exist.

---

## 16. Next implementation step

Build Corpus C v0 and its deterministic ground-truth/query manifest without running any LLM condition yet.

That keeps corpus design logically prior to observing experimental outcomes.
