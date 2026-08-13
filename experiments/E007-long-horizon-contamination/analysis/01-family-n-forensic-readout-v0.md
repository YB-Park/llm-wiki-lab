# E007 Family N — forensic readout v0

Status: provisional forensic interpretation after the frozen 15-run primary block, A4 semantic evaluation, and query-level forensic export. No new primary runs were used.

## Project objective

The objective is not to pick a C0-C4 winner. It is to find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

## Primary observations

### 1. Q025 is a measurement-suspect common-mode failure

Q025 failed in 10/15 runs: C0=2, C1=2, C2=2, C3=2, C4=2. Seven failures were only `missing required source_ids: ['S007']`; two omitted all S004/S007/S013; one omitted S004/S007.

The deterministic rule requires all of S004, S007, and S013. However S013 itself restates the 4 GB constraint, the PostgreSQL-backed metadata path, and the >5.5 GB full-snapshot prototype. Therefore omission of S007 is not obviously a wrong substantive answer; it may be an over-strict provenance rubric.

Protocol consequence:
- preserve the preregistered score unchanged;
- mark Q025 as measurement-suspect;
- report sensitivity excluding Q025 rather than retroactively editing the rule.

Sensitivity excluding Q025 (57 remaining deterministic opportunities per condition):
- C0: 57/57
- C1: 47/57
- C2: 55/57
- C3: 57/57
- C4: 54/57

This sensitivity analysis is diagnostic, not a replacement primary endpoint.

### 2. Naive recursive wiki maintenance (C1) loses provenance and is highly unstable

C1 failures cluster strongly in provenance:
- Q021: 2/3 failures
- Q022: 2/3
- Q023: 2/3
- Q024: 2/3
- Q025: 2/3

The failure reasons are missing required source IDs. C1 does not require preservation of source IDs and explicitly permits the current derived wiki to be relied on as working knowledge. C2 adds an authority rule, raw-source grounding, and compact source IDs for exact/disputed facts; Q021-Q024 then have zero failures.

This is decision-relevant evidence that provenance should not be expected to emerge implicitly from generic summarization. It must be part of the maintenance representation/policy.

C1 also has the largest deterministic run dispersion: 14/20, 20/20, 14/20. Final wiki/raw ratios range 0.832-1.850 and churn 254-589 lines. This is consistent with unstable recursive rewriting, although n=3 prevents strong distributional claims.

### 3. C2 is the strongest simple-wiki candidate, but it has not demonstrated economic value over raw context

C2 removes the systematic C1 provenance collapse and has 56/60 deterministic passes; excluding measurement-suspect Q025 it is 55/57. Its semantic mean is approximately tied with C0 and slightly higher in this block.

However C2 does not currently provide compression/economic evidence:
- mean total input: ~185k vs C0 ~84k (about 2.19x)
- mean maintenance input: ~98k vs C0 0
- mean answer input: ~87k vs C0 ~84k
- final wiki/raw ratio mean: 1.185

At this corpus size, the wiki is not reducing query input and adds a substantial maintenance pass. The source-grounding policy may be a quality floor, but the current `re-read all raw sources every wave and rewrite one artifact` implementation is not yet justified economically.

Working hypothesis: source grounding is useful, while full-history recompilation on every ingest is likely the wrong maintenance algorithm. This points toward staging/selective consolidation rather than abandoning provenance.

### 4. C3 transition verification is active but has weak demonstrated intervention yield

Across three C3 runs:
- initial revise decisions: 11
- repairs: 11
- final revise decisions after repair: 7
- initial issues: coverage 4, preservation 3, faithfulness 14

Thus only 4/11 repaired transitions changed from revise to accept; 7/11 remained unresolved under the verifier yet were committed because the protocol allows only one repair.

This means C3 is not a hard trust gate. It is `detect -> one repair -> commit even if still rejected`.

Cost is high:
- mean total input ~462k (~5.48x C0, ~2.50x C2)
- maintenance input ~373k (~3.80x C2 maintenance)
- calls ~25.3 vs C2 12
- state ratio 1.236, churn 557

C3 matches C0 at 58/60 deterministic (57/57 excluding Q025) but is slightly lower semantically. This does not establish that verification is useless: it may reduce tail risk or stabilize state shape. Indeed C3 state ratio/churn are noticeably more consistent across the three runs than C1/C2. That possible variance-reduction benefit requires mechanism-level auditing before rejection.

### 5. C4 regression protection fixes its immediate probes but introduces a large complexity/state-risk signal

Across C4:
- transition initial revise: 6
- transition repairs: 6
- transition final revise: 3
- regression checks: 15
- triggered: 3
- regression repairs: 3
- immediate failures before repair: 3
- immediate failures after repair: 0

So the local regression repair succeeds on the exact immediate probe that triggered it. But overall C4 has only 55/60 deterministic passes, semantic invalid mass 4/30, and the largest operational cost.

Most strikingly one run (`C4-r01`) has final wiki/raw ratio 4.514 and churn 1119 lines, compared with C4-r02=0.921/411 and C4-r03=0.760/252. This is a strong state-inflation/outlier signal.

C4-specific deterministic regressions are temporal:
- Q018 correction/history: 2/3 failures
- Q019 rename timing: 1/3 failure

These queries first appear at their own wave, so a gate that only retests previously passed queries cannot protect them before first answer. Therefore these failures do not by themselves prove regression repair damaged old knowledge. We must inspect whether the relevant facts were absent from the committed state or merely missed during answer generation.

Working hypothesis: local behavioral repair can overfit to probes and/or create patching/state debt. The 4.514 ratio outlier makes this a priority mechanism question, not yet a conclusion.

### 6. C0 is a strong control, but this does not mean 'wiki is unnecessary'

C0 is 58/60 deterministic and 57/57 excluding Q025, with zero maintenance cost and no semantic invalid items. On this six-wave, 18-source synthetic corpus, full raw context is extremely competitive.

The correct inference is narrower: **E007 v0 has not demonstrated a quality or cost advantage for persistent compilation at this scale.**

Strong alternatives remain:
- the horizon/corpus is too small for raw-context attention/retrieval failure;
- synthetic sources are unusually clean and compact;
- long-term repeated queries may change amortization;
- real personal corpora contain heterogeneous formats, noise, duplicate evidence, and much larger history.

A future scale/horizon stress test is justified only after the current mechanism audit.

### 7. Common semantic weaknesses are not being solved by these maintenance policies

Several semantic questions remain weak across most/all conditions (notably Q009, Q012, Q013). This suggests that the current single-artifact maintenance variants do not automatically solve global synthesis/multi-hop reasoning.

E007 is a maintenance trust gate, so this is not a failure of its purpose. It is evidence against overclaiming that 'better wiki maintenance' alone implies better reasoning.

### 8. Operational reliability is part of system reliability

During execution, model-facing structured-output failures included literal JSON control characters, missing/extra answer IDs, malformed individual answer items, boolean schema mismatches, and missing primary answers. Separately, our harness had its own recursion/schema-drift bugs.

These must remain separated:
- model/LLM contract failures are evidence about automation interface reliability;
- harness bugs are evidence about orchestration complexity and our implementation discipline, not model quality.

Both matter to the larger automation-boundary question.

## Strongest claims that survive v0

### Supported observation
1. C1 systematically loses provenance under a generic rewrite policy.
2. Explicit source grounding/provenance policy (C2+) removes the Q021-Q024 provenance failure cluster in this block.
3. C0 remains highly competitive at this scale.
4. C3 verification is expensive and often ends with unresolved verifier objections that are nevertheless committed.
5. C4 immediate regression repairs pass their triggering probes but exhibits the largest state-size outlier and additional temporal failures.
6. Q025's preregistered deterministic rule is likely over-strict and should be treated as measurement-suspect in interpretation.

### Working hypotheses
1. Source grounding is necessary; full-history recompilation every wave is not.
2. Transition verification may reduce variance/tail risk more than it improves mean accuracy.
3. One-shot repair with unconditional commit is a weak trust boundary.
4. Behavioral regression repair may create patching/state inflation and test-specific overfitting.
5. Raw long-context remains the rational baseline until scale/horizon creates measurable recall or economics pressure.

## Claims not supported

- C2 is 'the winner'.
- C3 verifier is useless.
- C4 regression testing is harmful in general.
- Wiki compilation is unnecessary.
- Luna is uniquely responsible for the observed patterns.
- A single 18-source synthetic corpus establishes an architecture decision.

## Next discriminating questions before any new primary experiment

Use the existing run artifacts only:

1. For each deterministic failure, was the required information actually absent from the wiki state, or present but missed by the answer model?
2. For C1 provenance failures, were source IDs already lost in the state before answering?
3. For Q025, exactly which source IDs did each condition cite?
4. For each C3/C4 transition repair, did ground-truth anchor coverage improve, remain unchanged, or worsen from candidate to repaired state?
5. Which C3/C4 repairs ended in verifier `revise`, and why were those states still committed?
6. For the three C4 regression repairs, which query triggered each repair, what changed in state size/anchor coverage, and did later failures recur?
7. What caused C4-r01 to inflate to 4.514x raw size?

Only after these mechanism questions are answered should we choose the next ablation/scale experiment.
