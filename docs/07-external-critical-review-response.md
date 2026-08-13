# External Critical Review Response — 2026-08-13

Status: **research-program review note, not an ADR**

This note records the project's response to an external critical review received after E007 Family N and before the scored E009A block. The purpose is to use the review as adversarial input without allowing it to silently rewrite the already-frozen E009A experiment.

## 1. Executive assessment

The review identifies a real strategic risk:

> We may become increasingly sophisticated at maintaining a persistent compiled knowledge layer before demonstrating that such a layer earns its lifecycle cost over raw evidence plus retrieval.

This is not a reason to discard the project or E009A. It is a reason to move the research center of gravity one level upward after E009A.

The strongest architecture-neutral question is:

> Under what workloads, if any, does a persistent LLM-derived knowledge layer produce greater long-horizon net value than raw evidence plus retrieval, and what is the minimum trustworthy form when such a layer is justified?

The phrase **if any** matters. A result in which most information remains raw and only selected high-reuse knowledge is compiled is a successful research outcome, not a project failure.

## 2. Points accepted strongly

### A. Add a real null hypothesis / pivot criterion

The research program must be capable of concluding that persistent compilation is not justified as a default.

Candidate null hypothesis:

> H0: For the target personal-knowledge workloads, a persistent LLM-derived canonical layer does not deliver enough lifecycle utility over raw evidence plus retrieval to justify its maintenance, trust, and review cost.

Candidate pivot criterion:

If matched-budget experiments at realistic scale repeatedly show no material utility advantage for compiled variants while maintenance/review burden is higher, persistent compilation should not be the default. Prefer raw source-of-record + cheap retrieval + selective synthesis.

This should later become a Charter/ADR amendment, not merely a note.

### B. Positive utility must become first-class

The project already measures many negative outcomes well: contamination, omission, provenance loss, state inflation, churn, tokens, review burden, and maintenance debt.

It must also measure positive value directly. Candidate dimensions include:

- rediscovery time avoided;
- repeated investigation avoided;
- decision-rationale recovery;
- cross-source connection/sensemaking quality;
- provenance verification time;
- continuity after long gaps;
- reuse of prior reasoning;
- navigation effort.

These should not be collapsed prematurely into one arbitrary weighted score. Pareto analysis remains preferable.

### C. E009A should complete, but it should not automatically open a verifier branch

E009A remains useful because canonical mutation authority is a general problem whenever any durable derived state exists, even if only a small selective layer survives the Value Gate.

However, a good E009A result is not sufficient reason to proceed automatically to E009B, stronger verifiers, automatic risk classification, or a sophisticated quarantine platform.

After E009A, the default next gate should be **representation/retrieval lifecycle value**, unless E009A uncovers an urgent experiment-invalidating issue.

### D. Realistic/shadow workload measurement should start earlier than full automation

The project need not wait for a production mutation architecture to observe real workload distribution.

A read-only/shadow instrument can measure locally, without external transfer of sensitive content:

- query category and recurrence;
- source fallback frequency;
- repeated rediscovery;
- decision-history recovery attempts;
- topic revisit intervals;
- whether a synthesis is actually reused;
- stale-information encounters;
- time/steps needed to verify an answer.

This is a measurement instrument, not a production Wiki implementation.

### E. Statistical structure must be explicit

Future experiment reports should state the experimental unit, dependence/cluster structure, paired design, uncertainty interval method, replication rule, and effect-size interpretation.

Point estimates such as 58/60 vs 55/60 must not acquire decision weight merely because they look numerically different.

### F. Architecture-critical semantics should eventually receive independent evaluation

E009A's frozen labels must not change now. But future architecture decisions should distinguish:

- author labels;
- independent/blind labels;
- adjudicated labels;
- ambiguous cases.

This is particularly important when `safe`/`unsafe` depends on choices such as whether history belongs in canonical prose, an event log, or Git history.

## 3. Important qualifications / counterarguments

### A. E009A is not merely safety engineering for a possibly useless Wiki

Even a selective architecture can contain durable topic syntheses, materialized overviews, decisions, or other derived artifacts. Once a durable derived artifact can become future input, mutation authority matters.

Therefore one controlled commit-boundary experiment is justified before the Value Gate. What would be unjustified is turning E009A into an open-ended verifier program before compiled knowledge proves lifecycle value.

### B. The proposed E001 + E006 + scale + reuse-frequency gate can itself become too factorial

The external review is directionally right but its suggested combined experiment can explode into too many dimensions.

A better approach is staged falsification:

1. compare a small set of architecture-neutral baselines under matched task and lifecycle budgets;
2. identify whether any compiled variant shows a credible crossover region;
3. only then spend effort comparing detailed representation variants inside that region.

Otherwise E001 knowledge-unit design may again be optimized before compilation has earned the right to exist.

### C. Surface leakage does not automatically invalidate E009A

A cheap classifier predicting labels from candidate surface features does not prove the verifier used that shortcut. Some surface features (for example source-ID preservation) may also encode genuinely relevant semantics.

The correct use of a leakage audit after freeze is therefore:

- **do not edit the frozen corpus again**;
- report cheap baseline predictability;
- lower the evidence grade if cheap baselines are strong;
- require a harder replication before architecture policy if the headline model result barely exceeds them.

### D. Real workload collection must obey the security boundary

Read-only workload observation is valuable, but it must not become a pretext to export corporate/private traces. Content can remain local while only permitted aggregate metadata is used.

## 4. Proposed critical path after E009A

Provisional sequence, subject to the E009A result:

```text
E009A frozen scored block
  -> post-hoc leakage + statistical audit
  -> Representation/Retrieval Value Gate
  -> realistic/shadow workload validation
  -> temporal + provenance semantics where justified
  -> selective/staged maintenance
  -> sequential commit/backlog automation only if a durable layer survives
  -> real VS Code/Copilot automation trial
```

The key discipline is that every stage must be allowed to eliminate the need for later stages.

## 5. Value Gate design principle

The next major gate should answer:

> At what corpus scale, query class, and reuse frequency—if any—does persistent semantic compilation recover enough query/rediscovery/sensemaking value to repay build, update, verification, staleness, and review costs?

Candidate baselines should remain architecture-neutral:

- raw + deterministic/text search;
- raw + lexical retrieval;
- raw + vector retrieval where available and justified;
- raw + large context;
- minimal compiled topic synthesis;
- layered synthesis + raw fallback.

Important metrics include answer/source quality, latency, query cost, build/update cost, state size, human verification effort, recovery effort, and repeated-use benefit.

Do not select a representation merely because it produces attractive pages.

## 6. Kill / pivot criterion candidate

The project should explicitly permit the following outcome:

> If matched-budget, realistically scaled evaluation finds no repeatable lifecycle advantage for persistent compiled knowledge over raw+retrieval, while maintenance/review cost remains materially higher, do not adopt a persistent compiled Wiki as the default architecture.

If compiled knowledge wins only for high-reuse or global-sensemaking workloads, compile only those classes.

This would support a heterogeneous system rather than a universal Wiki representation.

## 7. What remains unchanged now

The following remain frozen until E009A completes:

- Corpus T-v1;
- E009A verifier prompt;
- gold/risk labels;
- call order and pass count;
- A0-A4 policy semantics;
- primary model;
- primary outcomes.

External criticism is interpretation input, not permission to move the goalposts of an in-flight preregistered experiment.

## 8. Immediate non-semantic actions

Safe to do before E009A scoring:

1. add stronger post-freeze surface-leakage audit;
2. define a project-wide statistical analysis standard;
3. draft (but do not silently ratify) the architecture-neutral mission/null hypothesis/kill criterion;
4. avoid designing E009B in detail before the Value Gate decision.

The next empirical information still needed for E009A is the frozen scored block itself.
