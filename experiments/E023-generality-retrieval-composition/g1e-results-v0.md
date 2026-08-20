# E023 G1e — exact BM25 evidence-budget result v0

Status: **COMPLETE / STRICT PROMOTION NOT EARNED / EVIDENCE-BUDGET SIGNAL STRENGTHENED**  
Run: `32324460519`  
Execution source: `505740b74776fc7b7988e9c168c9c9d0ed2067fa`  
Exact model: `gpt-5.6-luna`  
Semantic calls: **16 / 16**  
Planner calls: **0**  
Selector calls: **0**  
Rerolls: **0**  
Workflow conclusion: **success**  
Result SHA-256: `865d89ad8c8b219493823bd21413196f658a9ffa2fdd3ed2948bb34b20f16727`

## Frozen question

G1e prospectively tested the smallest mechanism suggested by repeated E023 rank-boundary evidence:

- **A5:** exact BM25 top-5 -> unchanged composer;
- **B6:** the exact same ranking top-6 -> the same composer.

No planner, query rewrite, RRF, selector model, evaluator-aware runtime rule, or Cxxx-specific semantic rule was added. The only causal difference was whether the sixth ranked whole authoritative object entered the answer context.

The new v2 slice contained 35 anchors and 8 questions and was frozen before semantic execution.

## Phase 0 — zero-model authority gate passed prospectively

PR #187 froze and validated Phase 0 with **0 model calls**:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A5 | 2 | 4 | 2 |
| B6 | 3 | 5 | **0** |

B6 authority-status improvements vs A5: **2**.  
B6 authority-status regressions: **0**.

The two improvements were deliberately consequential:

- **CQ001:** rank-6 `C003` is the explicit `R. Singh -> Rina Singh` identity bridge;
- **CQ008:** rank-6 `C033` is the second independent monthly-close CPU observation required to establish that the issue was repeated.

This prospective authority result justified the later 16-call semantic safety/value comparison. It did not itself promote top-6.

## Phase 1 — frozen semantic result

A5:

- **5 PASS**;
- **1 PARTIAL**;
- **1 FAIL_RETRIEVAL**;
- **0 FAIL_COMPOSITION**;
- **1 CRITICAL_ERROR**.

B6:

- **6 PASS**;
- **2 PARTIAL**;
- **0 FAIL_RETRIEVAL**;
- **0 FAIL_COMPOSITION**;
- **0 CRITICAL_ERROR**.

B6 semantic improvements vs A5: **2**.  
B6 semantic regressions: **0**.  
B6 new critical errors: **0**.

The frozen promotion rule required **at least 7/8 B6 PASS**. Actual was **6/8**, so:

> **G1e strict promotion is NOT_EARNED. Do not weaken the frozen threshold.**

## What the extra evidence actually fixed

### CQ001 — identity truth-by-luck removed

A5 omits C003, the explicit R. Singh / Rina Singh bridge, and includes same-surname distractor C004. The A5 composer nevertheless asserts that the Northstar security contact was Rina Singh and marks authority sufficient.

That is the same trust class first exposed in G1a: the answer happens to be correct, but the supplied authority does not establish the identity. A5 is `CRITICAL_ERROR`.

B6 adds rank-6 C003. With the bridge present, the composer grounds the identity explicitly and does not conflate Ravi Singh.

**CQ001: CRITICAL_ERROR -> PASS.**

This is the cleanest prospective evidence so far that a slightly larger simple evidence prefix can repair a consequential authority failure without planner or selector machinery.

### CQ008 — repeated evidence recovered

A5 contains the user-owned C034 capacity decision but only one independent monthly-close observation, C032. The frozen evaluation contract requires at least two raw observations before the Wiki may independently establish that the CPU issue was repeated.

The A5 composer behaves safely: it marks authority insufficient and explicitly says that no second dated incident is supplied. This is a retrieval/evidence-budget failure, not an unsupported composition error.

B6 adds rank-6 C033, the July monthly-close observation. The context then independently establishes recurrence using C032 + C033, and the answer correctly explains the repeated evidence.

**CQ008 improves from retrieval insufficiency to a substantively correct answer.**

However, the B6 answer presents the load-bearing capacity decision as an ordinary fact rather than making explicit that C034 is user-owned `HUMAN_KNOWLEDGE`. That remaining composition issue keeps B6 CQ008 at `PARTIAL`.

## What the extra evidence did not break

B6 adds one extra whole object to every question, including several already-risky contexts. Yet the frozen semantic adjudication finds:

- **0 semantic regressions**;
- **0 new critical errors**;
- no new same-name/project/vendor-capability conflation;
- no observed context-noise failure attributable to the sixth object.

This matters because the evidence-budget hypothesis was not merely “more evidence recovers misses”; it also had to survive the risk that more evidence would confuse the composer.

On this controlled slice, the sixth object increased raw evidence characters by roughly **12%–29%** depending on the question, while producing no semantic regression.

This still does not prove that larger contexts are monotonically safe or that six sources is a universal optimum.

## Why the strict gate still fails

The two B6 `PARTIAL` cases are **composition-side**, not evidence-budget failures.

### CQ002 — overcautious sufficiency calibration

The context already contains the governing Redwood policy C009 and AcmeCloud configuration C007. The answer correctly says standard DR does not satisfy the Australia-only rule and that the Australia-only option could satisfy it.

But it then marks `insufficient_authority=true` and demands stronger implementation/storage-scope confirmation than the frozen `could satisfy` proposition requires.

This is the same `COMPOSITION_OVERCAUTIOUS_INSUFFICIENCY` class previously observed in E023.

### CQ008 — epistemic type omission

After B6 adds C033, the evidence for recurrence is complete. But the answer does not make explicit that the load-bearing 8-to-12 capacity decision comes from user-owned `HUMAN_KNOWLEDGE` C034.

This is the same `COMPOSITION_EPISTEMIC_TYPE_OMISSION` class previously observed on user-owned decisions.

These failures are important because they prevent us from declaring the whole answer path earned merely because retrieval improved.

## What G1e earned despite strict NOT_EARNED

G1e does **not** earn a product rule or final G1 promotion. It does earn the strongest prospective evidence-budget mechanism signal in E023 so far:

1. Phase 0 prospectively moved **2 authority-incomplete A5 contexts to sufficient B6 contexts with 0 regressions**;
2. semantic execution moved the critical identity truth-by-luck case to PASS;
3. it recovered the missing repeated-evidence case without causing any semantic regression elsewhere;
4. it did this with **0 planner calls and 0 selector calls**;
5. the remaining strict-gate blockers are now known composition classes rather than missing authority in B6.

The architecture implication is therefore not “increase k and stop thinking.” It is:

> **A simple evidence-budget increase is now a credible strong G1 retrieval baseline. The next bottleneck is authority-preserving composition: calibrating insufficiency to the actual proposition and surfacing terminal epistemic type, especially HUMAN_KNOWLEDGE.**

## Current next question

Do **not** launch another retrieval/selector tuning run immediately.

The next controlled work should first ask, with zero model calls where possible:

- can the composer contract require terminal authority type to remain explicit without forcing unnatural user-facing jargon?
- can `insufficient_authority` be aligned with proposition-level authority sufficiency rather than a stronger, unstated guarantee?
- can these composition requirements be expressed generically for identity, policy, decisions, and repeated observations without importing evaluator clauses or domain-specific schemas?

Only after a prospectively stated composition mechanism exists should another semantic comparison be considered.

The evidence-budget result should remain the **strong simple retrieval baseline** for that comparison. A later product translation may express evidence size in character/token terms rather than hard-code six whole sources.

## Boundaries unchanged

This result does **not** authorize:

- a hard-coded top-6 product default;
- same-slice CQxxx semantic reruns;
- G2 persistent semantic dossiers;
- graph DB / universal Entity/Relation/KnowledgeUnit storage;
- automatic identity merge/split or routing;
- vector defaults;
- evaluator clauses as runtime canonical structure;
- Dogfood runtime changes.
