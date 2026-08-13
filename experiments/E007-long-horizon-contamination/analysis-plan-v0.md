# E007 Family N forensic analysis plan v0

Status: analysis protocol frozen after the primary + A4 semantic blocks completed, before query-level forensic export was inspected.

## Purpose

E007 is not a Copilot benchmark and not a winner-selection contest among C0-C4. Its job is to determine whether increasingly strong maintenance safeguards change long-horizon failure behavior enough to justify their state, inference, and operational cost.

The project-level objective remains: find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

## Analysis order

We will interpret the completed Family N block in this order:

1. common-mode failures across all conditions;
2. condition-induced failures and recoveries;
3. repetition/run dispersion;
4. semantic validity and evaluator contract failures;
5. transition/regression intervention yield;
6. state size, compression/inflation, rewrite churn, and inference cost;
7. alternative explanations and threats to validity;
8. only then: claims that survive and follow-up experiments required to distinguish remaining hypotheses.

Condition-level means are not sufficient evidence by themselves.

## Required distinctions

### Common-mode failure

A query that repeatedly fails across C0-C4 may indicate a shared model limitation, corpus/question ambiguity, deterministic-rule defect, or task difficulty. It must not be attributed to wiki maintenance without further evidence.

### Condition-induced failure

A failure that appears or increases after introducing a maintenance policy is a candidate policy-induced regression, not proof of one. We must inspect whether it is repeatable, whether the affected fact was actually lost/altered in state, and whether answer-generation stochasticity could explain it.

### Intervention yield

Verifier/repair/regression calls are valuable only if they prevent or reverse meaningful failures. Their existence or high activity count is not evidence of value. We will compare initial flags, repairs, final unresolved flags, regression failures before/after repair, downstream query outcomes, and additional inference/state churn.

### Semantic invalid mass

`invalid_or_incomplete` semantic items remain explicit reliability failures/uncertainty. They are never silently removed from interpretation merely because the mean over valid items is high.

### State economics

A condition is not considered a successful compact wiki if it achieves quality by retaining or expanding to raw-like/supra-raw state, or by excessive rewrites. Final wiki/raw ratio and cumulative changed lines are first-class outcomes, not cosmetic diagnostics.

## Strong alternative explanations to test

- **Short-horizon advantage for raw context:** Corpus C may be too small/short for long-context C0 to experience the retrieval and attention problems that motivate a wiki.
- **Synthetic-corpus overfit:** fixed entities and clean source structure may favor one policy unnaturally or fail to represent real personal knowledge messiness.
- **Model-specific interaction:** Luna may respond differently to source-grounding/verifier prompts than other models; architecture-level claims require replication if headline conclusions depend on this.
- **Answer stochasticity vs state corruption:** a failed query may reflect generation noise even when the state remains correct. State-level evidence is required before calling it contamination.
- **Evaluator/scorer measurement error:** Q-specific failures can be caused by deterministic signal rules or judge behavior. Common failures receive special scrutiny.
- **Complexity-induced operational failure:** additional LLM calls, structured-output contracts, repair loops, and reporting paths may create new failure surfaces independent of knowledge quality.
- **Compression confound:** a larger state may preserve more facts and therefore score better without proving better knowledge organization.
- **Prompt-strength confound:** C1-C4 differ not only in abstract policy but in instructions and access to raw sources; follow-up ablations may be needed before assigning causality to a named mechanism.

## Claim discipline

Possible outcomes after forensics:

- **Supported observation:** directly visible in the completed artifacts.
- **Working hypothesis:** plausible causal interpretation with competing explanations remaining.
- **Decision-relevant evidence:** strong enough to change the next experiment or architecture option.
- **Architecture decision:** requires evidence beyond this single Family N block unless the decision is explicitly provisional/reversible.

We will not label a condition a winner solely from aggregate accuracy, semantic mean, or cost.

## Follow-up experiment triggers

Follow-ups are opened only if the completed forensics identify a discriminating question. Candidate triggers include:

- C0 remains competitive because horizon is too short -> long-horizon/scale stress experiment.
- C2 looks Pareto-efficient -> ablate source grounding vs all-source recompilation vs selective maintenance.
- C3 repairs are active but downstream-neutral -> intervention-yield / verifier-ceremony ablation.
- C4 degrades while state inflates -> regression false-positive and post-repair transition-verification experiment.
- state and answer outcomes disagree -> state-fidelity probes independent of answer generation.
- one or more common-mode queries dominate results -> audit scorer/query/corpus validity before changing architecture.

No follow-up is selected until the forensic handoff is reviewed.
