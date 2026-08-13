# Experiment Program

The purpose of experiments is to prevent attractive architecture from becoming policy based only on intuition.

## 1. Experimental principles

1. Compare alternatives on the **same corpus** and **same questions**.
2. Preserve all prompts, model settings, input corpus versions, and outputs needed for replay when feasible.
3. Separate measured results from interpretation.
4. Include adversarial and long-horizon cases, not only clean one-shot examples.
5. Measure maintenance cost as well as answer quality.
6. Do not optimize the benchmark around the architecture we already prefer.
7. Any LLM-as-judge metric should be paired with deterministic checks or sampled human review where practical.

## 2. Baseline evaluation dimensions

### Retrieval quality

- answerable question success rate,
- exact-fact retrieval accuracy,
- multi-source synthesis quality,
- temporal/current-state accuracy,
- contradiction-awareness rate,
- source recall.

### Knowledge integrity

- unsupported claim rate,
- stale claim rate,
- duplicate/conflicting canonical statement rate,
- source-attribution coverage,
- broken-link rate,
- orphan-page rate.

### Structural health

- page-size distribution,
- semantic cohesion,
- split/merge frequency,
- taxonomy churn,
- alias/entity duplication.

### Operational cost

- tokens / model calls per ingest,
- tokens / model calls per query,
- human review actions,
- average repair effort,
- maintenance backlog.

### Long-horizon behavior

- contamination after repeated synthesis cycles,
- ability to recover from injected error,
- preservation of historical states,
- retrieval performance as corpus size grows.

## 3. Experimental corpus design

We should maintain two complementary corpora.

### Corpus C — Controlled

Synthetic or carefully curated material designed to expose specific failure modes.

Include:

- exact dates and numbers,
- aliases and near-duplicate entities,
- facts that change over time,
- genuine contradictions between sources,
- correction of previously wrong information,
- multiple documents about the same topic,
- highly related but distinct concepts,
- irrelevant distractor material.

Advantages: known ground truth and repeatability.

### Corpus R — Realistic

A heterogeneous collection approximating personal use:

- technical articles,
- papers,
- project notes,
- personal observations,
- conversations,
- decisions,
- documentation,
- periodically updated sources.

Advantages: exposes friction and emergent maintenance problems that synthetic data misses.

Private/sensitive real-life material should not enter the public experimental corpus.

## 4. E001 — Knowledge-unit comparison

### Question

What representation gives the best trade-off between retrieval, synthesis, and maintenance?

### Variants

- V1: source-level summaries,
- V2: topic documents,
- V3: atomic notes,
- V4: claim/event layer + topic synthesis.

### Procedure

1. Ingest the same initial corpus into each variant.
2. Ask the same broad, exact, multi-hop, and temporal questions.
3. Add a second wave of overlapping sources.
4. Repeat the questions.
5. Measure fragmentation, duplication, edit locality, and review effort.

### Key outcome

Do not pick a representation merely because its first ingest looks clean; inspect how it evolves.

## 5. E002 — Immediate update vs staged consolidation

### Question

Should every new source rewrite durable knowledge immediately?

### Variants

- V1: immediate integration,
- V2: append to observation buffer; consolidate after N observations,
- V3: trigger-based consolidation on contradiction/topic density/age.

### Stress cases

- noisy sources,
- repeated small updates,
- partially contradictory evidence,
- corrections arriving later.

### Measures

- unnecessary rewrite count,
- unsupported synthesis rate,
- contradiction handling,
- maintenance tokens,
- final answer accuracy.

## 6. E003 — Temporal update semantics

### Question

How should the wiki distinguish correction, change-over-time, and unresolved disagreement?

### Test set

At least 50 update chains covering:

- objective current facts,
- historical facts,
- software/version changes,
- personal preferences,
- decisions later reversed,
- disputed claims,
- earlier source later corrected.

### Variants

- overwrite latest,
- append-only chronological notes,
- explicit supersession/status model,
- validity-interval model.

### Measures

- current-state answer accuracy,
- historical-state answer accuracy,
- false contradiction rate,
- accidental history loss.

## 7. E004 — Provenance granularity

### Question

How much provenance is necessary to prevent recursive contamination without making maintenance impractical?

### Variants

- source-file reference,
- section/heading reference,
- claim-to-span reference,
- source reference plus selective precise citation for high-risk claims.

### Injected faults

- invented number,
- source says A but synthesis says B,
- derived page cites another derived page only,
- source becomes unavailable,
- source contains two conflicting passages.

### Measures

- fault detection rate,
- verification effort,
- metadata maintenance cost,
- robustness after page rewrites.

## 8. E005 — Split/merge policy

### Question

When does document granularity become harmful?

### Procedure

Construct topics with increasing breadth and overlap. Compare:

- fixed size thresholds,
- semantic-cohesion trigger,
- retrieval-failure trigger,
- no automatic split/merge.

### Measures

- retrieval precision/recall,
- routing errors,
- duplicate content,
- number of cross-page reads needed,
- migration effort.

## 9. E006 — Retrieval escalation

### Question

When is a synthesized wiki page enough, and when must retrieval descend to raw evidence?

### Variants

- summary only,
- lexical search only,
- summary -> detail,
- summary -> detail -> source on demand,
- agentic mixed retrieval.

### Query classes

- overview,
- exact number/date,
- comparison,
- source attribution,
- temporal question,
- disputed claim,
- multi-hop synthesis.

### Measures

Accuracy, tokens, latency, source verification rate, hallucination rate.

## 10. E007 — Long-horizon contamination

### Question

How rapidly does error compound when derived knowledge is repeatedly reused?

### Procedure

1. Begin with clean source corpus.
2. Generate wiki version 1.
3. Add sources in batches.
4. Permit later synthesis to read earlier derived pages under controlled policies.
5. Inject a small number of realistic synthesis errors.
6. Continue for many generations.

### Compare

- derived pages may be treated as evidence,
- derived pages may guide retrieval but source verification is required,
- claim-level provenance enforcement.

### Measures

- survival/amplification of injected errors,
- unsupported descendants per original error,
- repair radius,
- ability to detect root cause.

This is a critical experiment for the project.

## 11. E008 — Error-book / feedback learning

### Question

Does recording recurring failure patterns improve later maintenance?

### Variants

- one-off correction only,
- persistent natural-language error book,
- error book + deterministic lint/test where possible.

### Measures

- recurrence rate of known failure,
- new false-positive behavior caused by overgeneralized rules,
- maintenance overhead.

## 12. E009 — Human review risk tiers

### Question

Which edits need explicit review?

### Candidate tiers

- T0: read/query only,
- T1: append source/observation,
- T2: edit derived page,
- T3: change taxonomy / merge / split / rename,
- T4: delete or mutate source-of-record data.

### Measure

Compare review burden and prevented error across different approval policies.

## 13. E010 — VS Code + Copilot usability trial

Only run after core semantics are reasonably stable.

### Question

Can the architecture be used consistently in the actual daily environment without excessive ceremony?

### Trial workflow

- capture source,
- ingest,
- ask questions,
- inspect provenance,
- correct error,
- consolidate,
- review changes with Git,
- recover an older state.

### Measures

- steps per common task,
- user interventions,
- abandoned/avoided actions,
- time-to-correction,
- policy violations by Copilot,
- subjective usefulness.

## 14. E011 — Persistent compilation value gate

### Question

Under what workloads, if any, does a persistent LLM-derived synthesis layer earn enough reusable lifecycle value over raw evidence plus retrieval to justify existing at all?

### Stage 1A baselines

- R0: raw + lexical top-k retrieval,
- R1: all ground-truth-relevant raw context as a strong raw ceiling,
- C0: minimal durable topic synthesis only,
- C1: durable topic synthesis + lexical raw evidence.

Keep Stage 1A intentionally small: paired topic scenarios, two source scales, and three query classes (exact/provenance, global synthesis, multi-hop/decision rationale). Model reuse economics from measured build cost plus repeated query cost rather than repeatedly asking identical questions.

### Primary interpretation

Report quality/cost Pareto frontiers and the break-even reuse count, if one exists. Persistent compilation does not earn complexity merely because it wins one answer-accuracy cell. If it has no credible value region, default to raw source-of-record + retrieval + selective/on-demand synthesis.

Only if Stage 1A survives should Stage 1B add an update wave to test whether maintenance cost destroys the static advantage. Detailed E001 representation optimization remains deferred until E011 establishes that persistent compilation deserves to exist for at least one workload region.

## 15. Experiment artifact structure

Each experiment should live under:

```text
experiments/E###-short-name/
  README.md
  corpus/
  prompts/
  runs/
  results/
  analysis.md
```

`README.md` should state the hypothesis and protocol **before** results are interpreted when possible.

## 16. Current critical path

1. E007 long-horizon contamination — completed mechanism/trust gate,
2. E009A canonical commit boundary — completed controlled pilot,
3. E011 persistent compilation value gate — current,
4. realistic/shadow workload validation,
5. E003/E004/E002 only where a durable layer survives,
6. E010 operational usability trial after core semantics are justified.

This order intentionally allows negative evidence to eliminate unnecessary downstream architecture work.
