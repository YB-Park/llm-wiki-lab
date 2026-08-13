# E009A pre-scoring red-team review v0

Status: **must be completed before the case manifest is frozen and before any scored verifier run.**

The purpose of this review is to attack the experiment itself. E009A is especially vulnerable to producing a comforting conclusion such as `human review is safer` or `two verifiers are better` simply because the cases, labels, or policy semantics were built to make that happen.

## 1. Is this the right question?

E009A tests canonical mutation authority, not the whole wiki architecture.

The experiment is justified only if E007's evidence is correctly interpreted:

- answer failure and state corruption are distinct;
- unresolved verifier objections were committed;
- behavioral regression could mutate canonical state;
- generic recursive maintenance could lose provenance.

Counterargument to preserve:

> Maybe the real problem was poor prompts/single-document rewriting, not commit semantics. A better compiler could make the gate unnecessary.

E009A does not need to disprove that possibility. It asks whether **even with a proposal in hand**, decision policy remains a meaningful safety layer.

## 2. Gold-label bias

The largest internal-validity risk is that `safe_commit` / `unsafe_commit` labels merely encode our preferred philosophy.

Before freezing cases:

- every unsafe label must identify the exact violated evidence/history/provenance invariant;
- every safe correction/supersession must explain why the changed prior statement is legitimately changed;
- safe restructure cases must preserve all load-bearing meaning despite substantial wording/order change;
- cases with genuinely debatable semantics must not be forced into binary gold labels; either rewrite them to remove ambiguity or reserve them for a separate ambiguity set not used in primary scoring.

## 3. Leakage risk

The verifier must not see:

- safe/unsafe label;
- fault class name;
- risk label;
- expected action;
- deterministic evaluator notes;
- phrases such as `this proposal intentionally drops...`.

Case filenames/IDs must also be neutral.

## 4. Template-overfit risk

If all unsafe cases contain obvious deletions and all safe cases are additive, a verifier can solve the benchmark from superficial edit shape.

The corpus must include counterexamples:

- safe transitions that delete/rewrite stale wording because a correction arrived;
- safe restructures with large diffs;
- unsafe additive transitions containing unsupported claims;
- unsafe proposals that look polished and conservative;
- safe disagreement-preserving updates that become longer/more complex;
- unsafe proposals that preserve most prior text but subtly flatten dates/provenance.

## 5. False-positive challenge set

The experiment must actively challenge over-conservative gates.

Required safe cases include:

- correction of an earlier erroneous value without pretending both values remain equally valid;
- current-state change that preserves old state historically;
- alias/rename where old naming remains historically meaningful;
- page reorganization/split/merge represented as one textual state for this benchmark;
- removal of a statement explicitly invalidated by authoritative correction;
- consolidation that removes redundant prose without dropping evidence or qualifiers.

A gate that quarantines all of these may be safe from contamination while producing an unusably stale wiki.

## 6. False-negative challenge set

Required unsafe cases include subtle failures:

- one correct new fact added while another new fact is silently omitted;
- old fact retained but temporal qualifier removed, making it falsely current;
- source ID removed while fact text remains;
- two conflicting measurements summarized into one apparent consensus;
- unsupported causal link added between two individually supported facts;
- correction misrepresented as a later real-world change;
- historical state erased while the current value remains correct.

## 7. Verifier-prompt bias

The verifier prompt must judge transition quality, not recommend one of our policies.

It must not say:

- `be conservative`;
- `prefer quarantine`;
- `never delete old information`;
- `only accept if absolutely certain`.

Those instructions would bake A1/A2 behavior into the judge.

The prompt may require coverage, preservation, faithfulness, provenance, temporal semantics, and unresolved-disagreement handling because these are the evaluated knowledge-integrity dimensions.

## 8. Human-oracle interpretation

A3/A4 use gold labels to simulate human adjudication. This does **not** estimate actual human error, latency, annoyance, or review quality.

Therefore E009A may compare **review volume required for oracle-quality adjudication**, but may not claim `humans solve X%` or `this is the real user burden`.

Actual human-review UX belongs later, especially E010.

## 9. Risk-label oracle problem

A3 receives a manifest risk label. Real systems would need to infer that risk.

Therefore A3 is an upper-bound study of a risk-sensitive policy **assuming correct operation-risk classification**.

If A3 looks promising, automatic risk classification must become a separate tested component or be implemented conservatively from deterministic operation types. Do not silently treat oracle risk labels as production-feasible metadata.

## 10. Base-rate distortion

A 20/20 safe/unsafe corpus is useful for diagnostic power but unrealistic as a real workload prior.

Never report the observed overall unsafe-commit percentage as expected production incidence.

Report conditional rates by gold class and later evaluate plausible base-rate scenarios only as sensitivity analysis.

## 11. Second-pass dependency

Two verifier calls are not independent in a statistical sense merely because they are separate requests to the same model.

A2 measures empirical repeatability/consensus under independent calls, not independent expert evidence.

If A2's advantage becomes decision-critical, model-diverse replication is required.

## 12. Quarantine is not free safety

Stage A can make quarantine look attractive because there is no sequential cost.

Quarantine may create:

- stale canonical knowledge;
- pending backlog;
- repeated review work;
- inconsistent query behavior if raw evidence and canonical state diverge.

Therefore no Stage-A result may promote quarantine to policy without E009B or equivalent sequential testing.

## 13. No repair in Stage A

This is deliberate.

Repair introduces another stochastic actor and would make it hard to know whether policy performance comes from decision quality or candidate improvement.

Counterargument:

> Real systems will repair before deciding.

Answer: first isolate the boundary. If a useful decision policy emerges, repair can be added as a separately measured proposal-improvement stage later.

## 14. Structural representation confound

The experiment uses a frozen text/Markdown transition representation because the project has not selected claim-level structured state.

Do not infer that a failure of text transition verification proves structured claim/event representation is necessary. Conversely do not let manually obvious source IDs make Markdown look safer than realistic prose.

## 15. Security/operational boundary

All benchmark material should remain fictional/public-safe.

Corporate execution must still avoid exporting:

- usernames/hostnames;
- filesystem paths;
- raw CLI telemetry;
- unrestricted model responses;
- screen captures;
- any corporate source/work content.

The safe handoff should contain only synthetic case IDs and aggregate normalized metrics, and only be transferred if organizational policy permits.

## 16. Pre-run checklist

Before first scored judgment, verify:

- [ ] 40-case target or documented frozen alternative count;
- [ ] roughly balanced safe/unsafe labels;
- [ ] all mandatory safe and unsafe challenge classes represented;
- [ ] no ambiguous gold cases in the primary set;
- [ ] neutral IDs and no label/risk leakage to verifier;
- [ ] case manifest hash recorded;
- [ ] verifier prompt frozen;
- [ ] policy semantics frozen;
- [ ] model/runtime profile frozen;
- [ ] structured-output parser tested with malformed-response containment;
- [ ] safe handoff contains no paths/free-form response text;
- [ ] no scored output viewed before the run plan is frozen.

## 17. Exit from red-team phase

Implementation may proceed only when the checklist is satisfied and the case corpus has survived an adversarial review aimed at making both safe and unsafe cases difficult for simplistic heuristics.
