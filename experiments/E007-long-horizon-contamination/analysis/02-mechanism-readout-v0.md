# E007 Family N — mechanism readout v0

Status: provisional mechanism interpretation after the frozen 15-run primary block and the post-hoc mechanism handoff. No new LLM calls or primary runs were used.

## Objective reminder

The project objective is not to maximize a benchmark score or select a C0-C4 winner. It is to find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

This note distinguishes **state failure**, **answer-generation failure**, **measurement failure**, and **automation-induced mutation**. Conflating those would lead to the wrong architecture.

## 1. Several observed query failures are answer-generation failures, not state contamination

The mechanism exporter compares preregistered deterministic literal/source anchors against the committed wiki state at the failing wave.

Important examples:

- `C4-r02 Q018`: state contained all 3/3 deterministic signals for the January latency correction, yet the primary answer failed.
- `C4-r01 Q018`: state also contained all 3/3 signals, yet the primary answer failed.
- `C2-r02 Q005`: state contained all 3/3 required local-exact signals, yet the primary answer failed.
- `C2-r03 Q026`: the state contained an allowed unsupported/unknown signal, while the answer still failed the deterministic wording requirement.

These are not evidence that maintenance erased the underlying facts. They show that a correct-enough state can still yield a bad query answer because of answer generation, retrieval from the state, wording, or scorer sensitivity.

Decision consequence: future trust evaluation must keep **state fidelity** and **answer behavior** as separate outcome layers.

## 2. C1 provenance failures are genuine state-level maintenance loss

C1's provenance cluster is different.

Examples from failing states:

- `Q021`: state source coverage `0/1`
- `Q022`: `0/1`
- `Q023`: `0/2`
- `Q024`: `0/1`
- `Q025`: `0/3` in the affected C1 trajectories

The fact-value signals may still be present, but source identity has disappeared from the persistent artifact itself. This is a real representation/maintenance failure, not merely answer stochasticity.

This strengthens the earlier conclusion: provenance must be an explicit invariant of the maintained representation/policy. Generic recursive summarization does not preserve it reliably.

## 3. C1 can also flatten uncertainty/conflict semantics

`C1-r03 Q027` failed with state diagnostic `any=N` for the preregistered dispute/unresolved signals and the answer returned `uncertainty=unknown` rather than disputed/ambiguous.

This is a candidate state-level loss of epistemic status: unresolved conflicting evidence may be compressed into generic uncertainty.

The literal-anchor diagnostic is not a semantic proof, so this remains a working hypothesis until the state is audited semantically. But it is directionally consistent with recursive-summary information loss.

## 4. Q025 is primarily a citation-selection / measurement problem outside C1

For C2/C3/C4 failing Q025 runs, the wiki state generally retained all three required source IDs (`src=3/3`). Yet the answer often cited only `S004,S013` or only `S013`.

Even C0 raw-context answers frequently cited `S004,S013` and omitted `S007`.

This reinforces the measurement-suspect classification:

- the state often contains the provenance;
- the answer model chooses a smaller evidence set;
- S013 itself restates much of the decision rationale;
- the preregistered rule nevertheless requires all three IDs.

Therefore Q025 should remain in the primary score for protocol integrity but must not drive an architecture decision or an automated mutation policy without sensitivity analysis.

## 5. Transition repair did not improve deterministic anchor coverage in any observed repair

Across all transition repairs:

- C3: 11 repairs, `anchorImproved=0`, `anchorSame=11`, `anchorWorsened=0`
- C4: 6 repairs, `anchorImproved=0`, `anchorSame=6`, `anchorWorsened=0`

This does **not** prove the verifier is useless. Most C3 initial findings were faithfulness issues, and literal deterministic anchors cannot detect unsupported prose removal, relationship clarification, or other semantic repair.

But it does establish that the substantial verifier/repair cost did not add or restore any of the preregistered exact/provenance anchors measured by this diagnostic.

The next diagnostic must therefore compare verifier issue counts before/after repair rather than equating unchanged anchors with no semantic benefit.

## 6. The current transition verifier is not a commit gate

Across C3/C4, many repaired transitions still ended with `final=revise` and were committed anyway.

Observed unresolved repaired transitions include:

- C3: 7 final-revise transitions
- C4: 3 final-revise transitions

So 10 repaired transitions were committed while the verifier still objected.

Current semantics are:

`detect -> one repair -> reverify -> commit regardless of final decision`

This is bounded repair, not a trust gate.

A future experiment should separate three independent design choices:

1. how to detect a suspect transition;
2. how many repair attempts are allowed;
3. what commit policy applies when the final state remains suspect.

Possible policies include commit, rollback/retain previous canonical state, quarantine/pending evidence, or human review. None is selected yet.

## 7. C4 demonstrates a concrete risk of answer-driven regression mutation

C4 performed three regression repairs. Each triggering regression probe passed immediately after repair. However the mechanism trace exposes a key hazard.

`C4-r03 W5` was triggered by `Q025`, a query already classified as measurement-suspect. The state was mutated (`6029 -> 6214` bytes) even though the broader anchor coverage remained `41/49 -> 41/49`.

This is a concrete example of a potentially noisy/over-strict behavioral probe causing canonical knowledge mutation.

It does not prove the repair was harmful, but it makes one principle decision-relevant:

> A stochastic answer failure should not automatically be treated as proof of canonical state corruption.

Any automated regression-to-state-repair loop needs a state-level diagnostic or stronger confirmation boundary before mutation.

## 8. C4's Q018 failures were not prevented by regression testing because they were first-seen queries

C4 regression checks only previously passed deterministic queries. Q018 first appears at W3, so it was not in the protected regression set before its first answer.

Both C4 Q018 failures occurred while the state contained all 3/3 literal signals. This shows two things:

1. regression protection cannot protect a first-seen behavior before that behavior has ever passed;
2. a failed current query is not necessarily a state regression.

Thus C4's behavioral regression layer has both **coverage limits** and **false-positive mutation risk**.

## 9. C4-r03 Q019 is a stronger state-omission candidate

`C4-r03 Q019` failed at W5 with only `2/4` deterministic temporal signals present in the committed state.

Q019 asks for the public name on May 31 vs June 2 and requires preservation of the Aster -> Aurora effective-date boundary.

Unlike Q018, this failure has state-level evidence of missing literal boundary information and is therefore a stronger candidate for actual maintenance omission.

However literal absence is not semantic proof; the state may encode equivalent timing in different wording. A final diagnostic should identify which anchors were absent and whether the temporal relation survived in another form before classifying it as confirmed contamination.

## 10. C4-r01 state inflation is path-dependent and not attributable to one repair alone

C4-r01 state bytes by wave:

- W0: 1,892
- W1: 3,134
- W2: 5,008
- W3: 14,640 (`transition repair=1`, `regression repair=1`)
- W4: 15,088 (`transition repair=1`, final verifier still `revise`)
- W5: 36,888 (`transition repair=0`, `regression repair=0`)

The W3 jump coincides with both transition and regression repair, but W5 more than doubles again with **no repair at all**.

Therefore the 4.514x final state inflation cannot be attributed solely to the regression repair mechanism. A more plausible family of explanations is path-dependent recursive rewrite expansion: once a verbose/inflated canonical state exists, subsequent full rewrite passes may amplify it even without repair.

A deterministic structural diagnostic is still needed to distinguish exact duplication/patch accumulation from non-duplicative verbosity and legitimate elaboration.

## 11. What this changes in the automation-boundary question

The strongest emerging distinction is not simply `automated vs human`.

It is between **semantic proposal** and **canonical mutation authority**.

The evidence increasingly supports treating these as separate roles:

- LLMs may propose organization, consolidation, contradiction detection, and repairs;
- deterministic contracts can enforce schema/provenance/transaction invariants;
- answer failures should not by themselves authorize canonical mutation;
- unresolved verifier objections may require quarantine/rollback/human escalation rather than unconditional commit;
- the canonical state should have an explicit transaction boundary.

This is still a working architectural direction, not a frozen decision.

## 12. Claims that are stronger after the mechanism audit

### Supported observations

1. C1 loses provenance in the persistent state, not merely in answers.
2. Some C2/C4 deterministic failures occur despite full literal state coverage, proving answer behavior and state fidelity must be evaluated separately.
3. All 17 observed transition repairs left deterministic anchor coverage unchanged.
4. Ten repaired C3/C4 transitions were committed while the verifier still returned `revise`.
5. C4 regression repair can be triggered by a measurement-suspect answer behavior (Q025) and then mutate canonical state.
6. C4-r01 state inflation is path-dependent; major growth occurs both with and without repair.

### Working hypotheses

1. Recursive full-document rewrite is a state-growth and stability risk even when source-grounded.
2. Query-answer regression is too noisy to directly drive canonical repair without state-level confirmation.
3. Verifier value, if any, is more likely in semantic faithfulness/tail-risk control than restoration of exact anchors.
4. A transaction boundary with quarantine/rollback semantics may be more important than adding more verifier calls.
5. Selective/staged consolidation is a stronger next maintenance candidate than full-history recompilation.

### Still unsupported

- C4 regression repair caused the Q018 failures.
- Every final-revise state was actually bad.
- Transition verification has zero semantic value.
- C4-r01 inflation is exact duplication.
- A hard rollback policy would be better than commit.

## 13. Final existing-artifact diagnostics before selecting the next experiment

No new LLM run is justified until four remaining questions are answered from the existing artifacts:

1. condition-level matrix of literal-state-complete vs answer-pass/fail;
2. verifier issue counts before vs after each repair;
3. trigger-state coverage for each of the three C4 regression repairs;
4. duplicate/heading/paragraph-density diagnostics for C4-r01 state growth.

After those are answered, E007 Family N forensics should be considered sufficiently exhausted and the next discriminating experiment can be preregistered.
