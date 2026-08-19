# Current Handoff

Last updated: 2026-08-19 KST

This file is the **continuation checkpoint only**. Keep historical evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

Normal product use is ordinary VS Code Agent conversation. Users should not need to learn Wiki tool names, storage schemas, filing concepts, or semantic infrastructure.

Current core formulation:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Generality is demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

## Product baseline — Dogfood 0.1.16

Dogfood 0.1.16 remains the released/product baseline via PR #159. E023 is research only and changes no runtime behavior.

Core authority remains unchanged:

- **Set Up Project Memory** is explicit per-workspace opt-in. Before opt-in, Agent tool implementations are unavailable.
- **Check Setup and Health** is pure diagnostics: **0 model calls / 0 state changes**.
- **Disable for This Workspace** removes Agent availability while preserving Wiki data.
- New source bytes require product-owned human confirmation before durable evidence admission.
- `RAW_MEMORY` is immutable admitted factual/provenance evidence.
- `DERIVED_MEMORY` is noncanonical/rebuildable model synthesis.
- `HUMAN_KNOWLEDGE` is explicit user-owned decision/belief/rationale/hypothesis authority; it is **not external evidence**.
- Changed remembered files require explicit correction/change/dispute/supersede/independent semantics.
- AI summaries remain **OFF by default** until explicitly granted per workspace.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Natural installed multi-session dogfood remains required for product readiness; controlled research does not replace real use.

## Core architecture baseline

Tracking: Issue #160. Working gate: `docs/14-generality-and-semantic-projections.md`. Experiment: `experiments/E023-generality-retrieval-composition/`.

### Authority Core stays ontology-agnostic

The durable core owns trust facts rather than a universal semantic ontology:

- evidence identity / integrity / provenance;
- current/history and explicit temporal/contradiction semantics;
- Human Knowledge authorship;
- permission/privacy boundaries;
- deterministic repairable storage invariants.

Do not add Person/Entity/Relation/KnowledgeUnit concepts merely to make the Wiki feel more general.

### `source-note-v0` is one projection, not the Wiki ontology

Treat the current one-source Agent Wiki note as **one DERIVED source-oriented projection under product test**. Do not infer that every source should fit that shape, that source is the permanent semantic unit, or that adding universal semantic fields equals generality.

### Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may be working/navigation/compilation state, but persistence never makes it terminal authority by itself.

### Three gates, in order

1. **G1 Retrieval / Composition** — can authoritative material be found, preserved, and composed at query time without persistent semantic state?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval fixed and test whether durable projection materially improves repeated use after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent targets themselves earn value, test subject discovery/alias routing/merge-split automation.

A G1 failure is **not** evidence for G2. A G2 success is **not** evidence for G3.

## E023 frozen sequence

### G1a — complete / NOT EARNED

Run `32215941344`, source `7315b858ed5ce764fa81ed131ee17f77c1ea11ae`, exact `gpt-5.6-luna`, 30/30 calls, zero rerolls.

- A exact-question BM25 top-5: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**.
- C blind planner -> BM25 -> RRF top-5: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**.
- C semantic improvements: **0**.
- promotion: **NOT_EARNED**.

Q001 omitted the explicit identity bridge but confidently merged aliases. The merge happened to match frozen gold, but supplied authority did not establish it.

> **Truth-by-luck is not trustworthy semantic recovery.**

### G1b — complete / promotion NOT EARNED / targeted trust repair observed

Run `32217824760`, source `7c604dd8d57a90c99526bdce5fb55fe7cdb7056f`, exact Luna, 12/12 calls, zero rerolls.

Evidence-follow loop:

> exact top-5 -> inspect bounded hits -> identify missing/ambiguous relation -> targeted BM25 -> bounded selector -> unchanged composer.

Frozen result:

- missing source reached candidate pool: **2/4**;
- entered final context: **1/4** vs preregistered >=3/4;
- semantic verdicts: **4 PASS**;
- Q001: `CRITICAL_ERROR -> PASS`;
- regressions: **0**;
- promotion: **NOT_EARNED**.

This established a real narrow signal: evidence-aware follow-up retrieval can recover a missing load-bearing identity bridge without persistent identity state.

## Authority-sufficiency evaluation — prospectively frozen and exercised

G1b exposed that flat `required_sources` mixed uniquely load-bearing authority with redundant corroboration. A richer **evaluation-only** contract was therefore frozen on separated material before G1c answers existed.

Prospective slice:

- 15 typed authoritative anchors;
- 6 questions `AQ001`–`AQ006`;
- 14 `RAW_MEMORY` + 1 load-bearing `HUMAN_KNOWLEDGE`;
- unique support, alternatives, repeated-support minima, identity/attribution bridges, negative evidence, temporal correction, forbidden conflation;
- statuses: `INSUFFICIENT_AUTHORITY`, `SUFFICIENT_CLEAN`, `SUFFICIENT_WITH_CONFLATION_RISK`.

This evaluator is richer than product storage **by design**. Do not turn evaluation clauses into canonical claim nodes or a product graph.

## G1c v0 — INVALID_EXECUTION / no experiment verdict

Execution source `987ee7ec615f7eb869be59f14a1928a3811baeed`, run `32229563330`.

A runner aggregation bug crashed after six A composer calls and the first B planner/selector/composer sequence, before the first B row was persisted. Control flow establishes nine actual attempts; the three first-B outputs are unrecoverable.

Therefore:

- v0 is frozen as **`INVALID_EXECUTION`**;
- no G1c retrieval-selection verdict is taken from v0;
- six A outputs are auxiliary semantic baselines only;
- lost B output is not reconstructed or silently rerolled.

## G1c-R1 — complete / final selection NOT EARNED

Frozen evidence:

- run `32232116273`;
- execution source `5227ac2b3f93c4f807e388822bfff963d0041120`;
- exact `gpt-5.6-luna`;
- calls **18 / 18**;
- rerolls **0**;
- execution complete: **true**;
- result SHA-256 `8f3e77163db92f7dff0b0a9aed5776c6dadd0eebfdb122fbfecf4313d0dae822`;
- result/adjudication merged via PR #179;
- frozen retrieval-selection verdict: **NOT_EARNED**.

R1 executed only the B evidence-follow arm under the already-frozen G1c mechanism and authority evaluator.

### The key stage decomposition

| stage | clean | sufficient + conflation risk | insufficient |
|---|---:|---:|---:|
| exact-query initial top-5 | 4 | 1 | 1 |
| evidence-follow candidate pool | 4 | 2 | **0** |
| final selector output | 4 | 0 | **2** |

The candidate pools contained enough positive load-bearing authority for **6/6** questions.

This materially changes the diagnosis:

> **The current leading G1 bottleneck is no longer evidence discovery alone. It is authority-preserving final selection.**

### AQ001 — bridge recovered, then discarded

The initial context lacked A003, the explicit `M. Chen -> Maya Chen` bridge, and contained same-surname distractor A004. Follow-up retrieval recovered A003 into the candidate pool.

The selector removed A004 **and A003**, returning the final context to `INSUFFICIENT_AUTHORITY`. The composer then confidently asserted the identity anyway.

AQ001 remains `CRITICAL_ERROR`. Truth-by-luck is still a trust failure even when the missing authority was found earlier in the same loop and then discarded.

### AQ002 — selector improvement

The selector retained direct email, meeting attribution, and A003 identity bridge while removing A004. Final context became `SUFFICIENT_CLEAN`; semantic verdict is PASS.

### AQ004 — destructive over-compression

Initial and candidate contexts were already `SUFFICIENT_CLEAN`, but the selector compressed them to final postmortem A011 alone. That dropped the explicit early-hypothesis A009 and retry/rollback causal signal A010 required by the prospective authority contract.

Final context became `INSUFFICIENT_AUTHORITY`; semantic verdict regressed from auxiliary A PASS to B `FAIL_RETRIEVAL`.

### Separate composition findings

- **AQ003:** selected context is clean and substantively correct, but the answer does not make explicit that load-bearing A007 is `HUMAN_KNOWLEDGE`, not independently observed RAW evidence. Verdict: PARTIAL.
- **AQ006:** selected context is clean and supports the frozen proposition, but the composer unnecessarily declares authority insufficient by demanding a stronger guarantee than the question requires. Verdict: PARTIAL.

Frozen semantic counts:

- auxiliary A: **3 PASS / 2 PARTIAL / 1 CRITICAL_ERROR**;
- R1 B: **2 PASS / 2 PARTIAL / 1 FAIL_RETRIEVAL / 1 CRITICAL_ERROR**;
- improvements: **0**;
- regressions: **1**;
- new critical errors: **0**.

## NEXT CORE — zero-model authority-preserving selection/budget analysis

**Pause paid semantic calls again. Do not run G1d or G2 yet.**

Use only the frozen G1c-R1 rankings/candidate pools for the next deliberate work.

Immediate question:

> **Can a simple, general, evaluator-independent selection/budget rule preserve recovered load-bearing authority and avoid destructive compression, without installing a product claim graph?**

Next steps:

1. analyze frozen initial/candidate/final contexts with **zero model calls**;
2. compare simple non-destructive evidence-budget policies before inventing another semantic selector;
3. explicitly test whether a rule can retain recovered AQ001 authority and avoid AQ004 regression without consulting evaluator clauses at runtime;
4. keep evaluator structure evaluation-only;
5. only if a concrete selection/budget policy earns itself in zero-model analysis, preregister a separate semantic comparison;
6. treat `HUMAN_KNOWLEDGE` type preservation and overcautious sufficiency as separate composition-policy questions;
7. keep G2 persistence and G3 identity/routing outside scope.

Do **not** interpret candidate-pool 6/6 as product rollout approval. The final evidence policy remains NOT_EARNED.

## Natural product dogfood continues in parallel

Observation log: Issue #141.

Watch naturally for:

- cross-source semantic questions that source-note-v0 handles awkwardly;
- identity/alias/attribution uncertainty;
- decisions whose rationale spans sources;
- temporal correction or disagreement;
- whether Agent naturally follows load-bearing evidence;
- whether it expresses uncertainty when an authoritative bridge is absent;
- popup fatigue / soft-guard usefulness / causal error reporting;
- hidden maintenance usage uncertainty;
- long-horizon value days or weeks later.

Do not manufacture workload. A dedicated Tree/View remains evidence-gated.

## Retained 0.1.16 / maintenance boundaries

- Copilot CLI compatibility uses runtime capability probing; version alone is not compatibility authority.
- `compiled_provider=disabled` remains expected and unrelated to Agent Wiki maintenance.
- positive daily maintenance setting is a **soft guard**, not a hard cap; `0` disables new model-backed maintenance generation.
- <=40k chars preferred single pass; 40,001–80k allowed single pass; >80k preserves RAW and skips derived maintenance before model call; never silently truncate.
- exact-current-byte remember is no-op reuse without a second source-admission modal.
- multi-root remains fail-closed in 0.1.16.

## 0.1.16 validated artifact

- source `e9370663d4763ae0f29d67c572d45c5b80f6c120`;
- main validation run `32204779167`;
- Actions artifact `9348765994`;
- publisher `3366df98e33dabbe72d00d396c2ea1820e50d9a4`;
- VSIX bytes `102811`;
- SHA-256 `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`;
- current install path `dogfood/releases/llm-wiki-dogfood-latest.vsix`.

## Do not start merely because it is available

- another paid E023 semantic run before zero-model selection/budget analysis earns a concrete policy;
- G2 persistent semantic dossier;
- graph DB / universal Entity/Relation/KnowledgeUnit schema;
- automatic identity merge/split or automatic concept routing;
- vector retrieval default changes without a concrete gate;
- chunk compiler unless natural >80k sources recur;
- background source watching/semantic maintenance;
- broad automatic contradiction resolution;
- permanent Tree View/activity UI without observed need;
- federation/X2 without recurring natural evidence;
- paid reruns of frozen E017/E018/E019/E021/E022/E023 cases.

## Known non-blocking edges

- Issue #132: deletion detection for `agent-state.json` and relation/pending crash window.
- Human Knowledge file deletion is not independently detectable without an index.
- Relation append and pending-state resolution are not one cross-process transaction.
- Copilot CLI optional flags can change independently of public docs; runtime capability probing remains authoritative.
- 80k is a temporary product ceiling, not a claimed Luna technical limit.
- E013/E015 evidence remains natural/data-gated; do not manufacture workload/divergence.

## Fast pointers

- Core generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- E023: `experiments/E023-generality-retrieval-composition/`
- G1a result: PR #165 / run `32215941344`
- G1b result: PR #169 / run `32217824760`
- prospective evaluator: PR #172 / `authority-sufficiency-preregistration-v0.md`
- G1c prereg/execution: PRs #173/#174
- G1c v0 invalid run: `32229563330`
- G1c-R1 prereg/execution/result: PRs #177/#178/#179 / run `32232116273`
- R1 result doc: `experiments/E023-generality-retrieval-composition/g1c-r1-results-v0.md`
- R1 stage analysis: `analyze_g1c_r1_stage_transitions.py`
- Installed/natural dogfood: Issue #141
- Current validated VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- User guide: `dogfood/vscode/README.md`
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Reliability follow-up: Issue #132

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
