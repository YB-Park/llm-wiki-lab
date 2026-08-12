# E007 Analysis Protocol v0

Status: **pre-registered before first scored run**
Date: 2026-08-12

This document defines analyses that do not affect maintenance-time behavior. It complements `scoring-protocol-v0.md` and the pre-scoring red-team review.

## 1. Analysis principle

Do not turn E007 into a single accuracy leaderboard.

A trustworthy Wiki should not win merely by:

- copying nearly all raw text,
- rewriting enormous portions of state every wave,
- spending arbitrarily many verifier calls,
- overfitting to previously asked regression questions,
- or exploiting one fixed workload's query frequency.

The analysis therefore treats quality, state compactness/stability, intervention behavior, and lifecycle cost as separate axes.

---

## 2. State-size and compression analysis

For every C1–C4 Wiki state compute deterministically:

- Wiki UTF-8 bytes / characters / lines,
- available rendered raw-source bytes / characters / lines,
- Wiki/raw byte ratio,
- bytes saved relative to raw,
- source IDs present in the derived state,
- descriptive source-ID coverage.

Use `harness/structural_metrics.py`.

### Interpretation

Neither extreme is automatically good.

Very low Wiki/raw ratio may indicate destructive compression. Very high ratio may indicate a degenerate near-copy of raw evidence.

The useful region is empirical: enough compression/organization to justify compilation while preserving the knowledge needed for future questions and audits.

Source-ID coverage is descriptive, not a score. C1 does not have the same provenance instruction as C2–C4.

---

## 3. Rewrite-churn analysis

For each successive derived Wiki state compute line-level additions/deletions using a deterministic diff.

Report:

- changed lines per wave,
- changed lines relative to previous-state line count,
- cumulative changed lines across the lifecycle,
- maximum single-wave churn.

This is a proxy for:

- review burden,
- instability,
- unnecessary rewrite exposure,
- future Git-diff usability.

It is **not** semantic edit distance. A large structural reorganization can look expensive even when semantically justified; surprising cases should be inspected qualitatively.

---

## 4. Payload size vs adapter-level token accounting

Each model-call metadata record should contain explicit:

- prompt UTF-8 bytes,
- prompt characters,
- response UTF-8 bytes,
- response characters.

Separately retain Copilot OTel observations such as:

- input/output/cache tokens,
- requested/resolved model,
- turn count,
- cost/AIU fields when present,
- wall time.

### Why both are necessary

Observed adapter input tokens may include runtime/system context not present in the explicit experiment payload. Therefore:

- use OTel totals for **actual observed adapter consumption**,
- use payload sizes to explain how much experiment material is being sent,
- do not infer fixed system overhead by simple subtraction unless accounting boundaries/tokenizers are verified.

---

## 5. Cost categories

Every call should be classified into one of these logical categories based on the frozen orchestration:

- `maintenance_update`,
- `transition_verify`,
- `transition_repair`,
- `regression_probe`,
- `regression_repair`,
- `primary_answer`.

Report costs by category and cumulatively.

This matters because two conditions with equal total tokens can have very different operational profiles. For example, one may spend heavily during ingest while another pays at every downstream query.

---

## 6. Query-frequency sensitivity / break-even analysis

The fixed E007 workload is only one usage pattern.

For each condition estimate:

- cumulative maintenance/verification/repair cost independent of ordinary downstream querying,
- observed primary-answer cost,
- average answer cost per query or query batch with the batching caveat stated.

Then project lifecycle consumption for a range of additional downstream query volumes `q`.

Conceptually:

```text
compiled_total(q) = compiled_maintenance + q * compiled_answer
raw_total(q)      = raw_maintenance + q * raw_answer
```

For C0, raw maintenance is approximately zero in E007.

Report whether a break-even point exists within a plausible range. Do not assume one universal real-world `q`.

If batching materially affects the estimate, report a range rather than false precision.

---

## 7. Intervention-yield analysis

Extra model calls are useful only when they change outcomes productively.

### Transition verifier

For C3/C4 report:

- verifier calls,
- initial `accept` vs `revise`,
- transition repairs invoked,
- final unresolved verifier flags,
- cases where repair improved later correctness,
- cases where repair was followed by new regressions or integrity failures.

A verifier that mostly restates harmless concerns or triggers changes without measurable benefit is ceremony, even if it sounds prudent.

### Behavioral regression layer

For C4 distinguish:

1. regression probe failure,
2. confirmed loss/corruption in the provisional Wiki,
3. likely answer-generation miss while the Wiki remained sufficient,
4. repair invoked,
5. repair recovered the failed behavior,
6. repair introduced a new integrity/regression failure.

Items 2 and 3 require post-hoc blinded inspection against the provisional state and evaluator evidence; do not infer them merely from the online probe.

A case of type 3 that triggers mutation is an **automation false positive**.

---

## 8. Post-hoc state-integrity audit

Query accuracy cannot detect every silent deletion or unsupported statement.

Audit derived states, at minimum final states plus selected intermediate/high-risk waves, for:

- still-valid early facts lost,
- exact identifiers/numbers corrupted,
- current/historical state collapsed,
- corrections treated as temporal changes or vice versa,
- unresolved disagreement incorrectly resolved,
- unsupported derived claims,
- source ownership errors,
- confusable entity merges.

Prefer deterministic ground-truth checks when possible. Use blinded semantic evaluation only where wording/synthesis makes deterministic matching unreliable.

State audits never feed back into the original run.

---

## 9. Condition interpretation constraints

### C1 → C2

Treat as the effect of a **bundled source-grounded maintenance package**, not a proof of one isolated mechanism.

If the difference is important, schedule a targeted ablation later.

### C2 → C3

Interpret as the marginal effect of same-model fresh-pass transition verification plus bounded repair in this runtime.

Do not generalize to independent verifier architectures without replication.

### C3 → C4

Interpret as the effect of adding an online behavioral regression/repair mechanism, including its false-positive and repair-induced risks.

### C0 vs compiled conditions

Interpret jointly with query-frequency sensitivity and state-size metrics. A small controlled corpus where raw full-context is cheap is intentionally a strong baseline.

---

## 10. Model/runtime interpretation constraints

The first Family N block uses `gpt-5.6-luna` through Copilot CLI as frozen experimental equipment.

A result is initially evidence about **maintenance policies under this model/runtime**, not a universal model-independent law.

If a policy effect is large enough to matter, replicate the key comparison later on at least one different model/runtime before promoting it to a broad design principle.

---

## 11. Headline-result vetoes

Do not publish or adopt a headline such as "C3 wins" without checking all of the following:

- query correctness,
- omission/unsupported/temporal/provenance failures,
- Wiki/raw size ratio,
- rewrite churn,
- verifier/repair activity,
- cumulative lifecycle consumption,
- false-positive interventions,
- post-hoc state integrity,
- stochastic variation across repetitions.

A safeguard that improves one axis by catastrophically degrading another is a trade-off, not an unconditional winner.

---

## 12. Conditional follow-up rule

Use the first block to choose **which uncertainty deserves the next experiment**.

Do not automatically run every ablation listed in the red-team review.

This keeps the research program deep without turning the first experiment into an endless factorial design.
