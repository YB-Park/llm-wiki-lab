# Experimental Statistics and Evidence Standard

Status: **project-wide research standard; applies prospectively**

This document defines the minimum statistical/evidence information that future experiment reports should state. It does not retroactively change preregistered metrics or rerun completed experiments.

## 1. Experimental unit

Every experiment must state what is treated as the unit of variation and why.

Possible units include:

- corpus;
- scenario / transition;
- query;
- run / stochastic repetition;
- user session;
- topic / project.

Do not count correlated observations as independent merely because they produce separate rows in a score table.

## 2. Dependence and clustering

State shared structure explicitly, including:

- repeated queries over the same underlying scenario;
- multiple model passes over the same transition;
- multiple waves in the same synthetic world;
- repeated runs with the same corpus and prompt;
- paired safe/unsafe variants from one scenario group;
- repeated observations from the same user/topic.

When uncertainty is estimated, prefer the highest meaningful independent cluster rather than naïvely treating every answer as independent.

## 3. Paired vs unpaired comparisons

If two conditions operate on the same cases/questions/scenarios, report paired differences whenever possible.

Useful summaries may include:

- case-level win/loss/tie;
- paired accuracy difference;
- paired cost difference;
- within-scenario change;
- bootstrap over scenario groups.

Unpaired aggregate means should not replace available paired evidence.

## 4. Uncertainty reporting

Where sample size permits, report uncertainty around headline effects.

Candidate methods:

- exact/binomial intervals for genuinely independent binary units;
- bootstrap over scenario groups or other appropriate clusters;
- run-level dispersion for stochastic repeats;
- paired bootstrap for matched conditions.

The chosen method must match the experiment's dependence structure.

Do not imply false precision when the number of independent scenarios is small.

## 5. Sample-size rationale

Before scoring, state why the chosen sample size is sufficient for the intended claim.

Acceptable rationales include:

- mechanism-discovery pilot;
- ability to observe a predefined large effect;
- cost-constrained exploratory block with explicit replication trigger;
- enough independent scenario groups for a planned interval width.

A pilot may be small, but its claims must remain pilot-sized.

## 6. Effect-size interpretation

Report absolute effects, not only ranks.

Examples:

- unsafe commits reduced from 8/20 to 2/20;
- review burden increased from 0% to 55%;
- median query cost changed by X;
- time-to-source-verification changed by Y.

Small point-estimate differences should not drive architecture decisions when uncertainty overlaps materially or the lifecycle trade-off dominates.

## 7. Multiple comparisons

If many conditions, query classes, risk tiers, or subgroups are inspected, distinguish:

- preregistered primary comparisons;
- secondary diagnostics;
- post-hoc exploratory findings.

Do not promote an isolated favorable subgroup to a primary result after inspection.

Formal multiplicity correction is not mandatory for every exploratory study, but the number of opportunities to find a pattern must be visible.

## 8. Benchmark leakage / cheap baselines

Before interpreting strong model performance, ask whether cheap non-semantic or weak-semantic baselines can predict the target.

Candidate audits:

- length / length ratio;
- diff size;
- citation/source counts;
- simple lexical features;
- TF-IDF + fixed linear classifier;
- nearest-neighbor/template similarity;
- leave-one-scenario-group-out validation.

A strong cheap baseline does not prove the LLM used a shortcut. It lowers the benchmark's evidence grade and raises the replication bar.

Frozen benchmarks should not be repeatedly edited to chase chance-level cheap-baseline performance after scoring starts.

## 9. LLM-as-judge

When an LLM evaluator is used, report separately:

- evaluator schema/contract failure;
- evaluator disagreement across passes;
- missing candidate answers;
- deterministic metric conflicts;
- human-audit subset where available;
- whether evaluator and candidate model are the same family/model.

Evaluation infrastructure failure must not be silently counted as knowledge-system failure, or vice versa.

## 10. Gold-label provenance

Architecture-relevant labels should identify their provenance:

- author-labeled;
- independent/blind-labeled;
- adjudicated;
- objective/deterministic ground truth;
- ambiguous / excluded from primary semantics.

If a label depends on an architecture convention rather than an objective fact, state that explicitly.

## 11. Cost accounting

Quality must be interpreted with lifecycle cost.

Where applicable report separately:

- initial build;
- ingest/update;
- consolidation;
- verification;
- retrieval/query;
- repair/recovery;
- human review;
- backlog/staleness cost proxy.

Adapter-level token/cost telemetry should be labeled as such and should not be promoted to monetary truth without verified semantics.

## 12. Replication rule

Each experiment should state before interpretation what result requires replication.

Typical triggers:

- architecture conclusion depends on a narrow difference;
- one model drives the result;
- strong residual benchmark leakage exists;
- gold semantics are author-dependent;
- result appears only in one scenario class;
- effect is large but surprising enough to suspect instrumentation.

Replication should change one relevant axis at a time when possible.

## 13. Evidence grade

Use qualitative evidence grades rather than pretending every experiment has the same external validity.

Suggested vocabulary:

- **mechanism evidence** — demonstrates a failure/success mode can occur;
- **benchmark evidence** — repeatable on a defined controlled corpus;
- **cross-corpus evidence** — survives a second materially different corpus;
- **cross-model evidence** — survives a relevant model change;
- **realistic-workload evidence** — survives heterogeneous realistic tasks;
- **operational evidence** — observed in sustained real use.

Architecture policy should normally require more than mechanism evidence when the decision is expensive or difficult to reverse.

## 14. Negative results and kill criteria

An experiment program must allow a candidate architecture to lose.

Where practical, state before major investment what evidence would cause the project to:

- stop adding complexity;
- retain a simpler baseline;
- narrow the candidate to a subset of workloads;
- abandon/pivot the architecture hypothesis.

A null result that prevents unnecessary infrastructure is a successful research outcome.
