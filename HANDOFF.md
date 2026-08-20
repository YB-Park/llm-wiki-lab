# Current Handoff

Last updated: 2026-08-20 KST

This file is the **continuation checkpoint only**. Keep historical detail in experiments, issues, PRs, ADRs, and Git. Replace stale guidance rather than appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

Normal product use is ordinary VS Code Agent conversation. Users should not need to learn Wiki tool names, storage schemas, filing concepts, or semantic infrastructure.

Current architecture thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Generality is demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

## Product baseline — Dogfood 0.1.16

Dogfood 0.1.16 remains the released/product baseline via PR #159. E023 is research only and changes no product runtime behavior.

Authority floor remains unchanged:

- explicit per-workspace opt-in;
- **Check Setup and Health** = 0 model calls / 0 state changes;
- disabling removes Agent availability while preserving Wiki data;
- new source bytes require human confirmation before durable admission;
- `RAW_MEMORY` = immutable admitted evidence/provenance;
- `DERIVED_MEMORY` = noncanonical/rebuildable synthesis;
- `HUMAN_KNOWLEDGE` = explicit user-owned decision/belief/rationale/hypothesis authority, not external evidence;
- changed remembered files require explicit correction/change/dispute/supersede/independent semantics;
- AI summaries remain off by default until explicitly granted.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Natural installed multi-session dogfood remains required; controlled experiments do not establish long-horizon product value.

## Core architecture boundary

Tracking: Issue #160. Working gate: `docs/14-generality-and-semantic-projections.md`. Current experiment family: `experiments/E023-generality-retrieval-composition/`.

### Authority Core stays ontology-agnostic

The durable core owns evidence identity/integrity/provenance, temporal/contradiction semantics, Human Knowledge authorship, permission/privacy boundaries, and deterministic repairable storage invariants.

Do **not** add Person/Entity/Relation/KnowledgeUnit concepts merely to make the Wiki feel general.

`source-note-v0` remains one DERIVED source-oriented projection, not the Wiki ontology.

### Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may help retrieval/navigation/compilation, but persistence never turns it into terminal authority.

### Gates remain ordered

1. **G1 Retrieval / Composition** — can the right authority be found, preserved, and composed at query time without persistent semantic state?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval strong/fixed and test whether durable projections improve repeated use after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent semantic targets themselves earn value, test automatic subject discovery/routing/merge-split.

A G1 failure is **not** evidence for G2. A G2 success would not automatically authorize G3.

## E023 frozen sequence

### G1a — complete / NOT EARNED

Run `32215941344`, exact `gpt-5.6-luna`, 30 calls, zero rerolls.

- exact BM25 top-5 A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**;
- blind planner + BM25/RRF C: same semantic counts;
- semantic improvements: **0**;
- promotion: **NOT_EARNED**.

Q001 established the core trust lesson: aliases were merged without the explicit identity bridge. The final identity happened to be correct, but authority did not establish it.

> **Truth-by-luck is not trustworthy semantic recovery.**

### G1b — complete / NOT EARNED / targeted repair signal

Run `32217824760`, exact Luna, 12 calls, zero rerolls.

Evidence-aware follow-up recovered the missing Q001 identity bridge and moved Q001 `CRITICAL_ERROR -> PASS`, but the preregistered broad final-recovery threshold was missed (`1/4` vs required `>=3/4`). Promotion remains **NOT_EARNED**.

This earned only a narrow mechanism signal: query-time follow-up can repair a consequential missing bridge without persistent identity state.

### Prospective authority-sufficiency evaluator — frozen

E023 replaced flat required-source completeness with an evaluation-only authority contract that distinguishes:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

It models uniquely load-bearing support, alternatives, repeated-support minima, explicit identity/attribution bridges, negative evidence, temporal correction, and forbidden conflation. It is **not** product storage or a canonical claim graph.

### G1c v0 — INVALID_EXECUTION

Run `32229563330`, source `987ee7ec615f7eb869be59f14a1928a3811baeed`.

A runner aggregation bug invalidated the comparison. Do not reconstruct or reroll the lost B outputs. v0 remains `INVALID_EXECUTION`; its six persisted A outputs are auxiliary only.

### G1c-R1 — complete / model final selector NOT EARNED

Run `32232116273`, source `5227ac2b3f93c4f807e388822bfff963d0041120`, exact Luna, 18/18 calls, zero rerolls.

Stage result:

| stage | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| exact initial top-5 | 4 | 1 | 1 |
| evidence-follow candidate pool | 4 | 2 | **0** |
| model selector final | 4 | 0 | **2** |

Candidate pools contained enough positive authority for **6/6** questions, but the model selector discarded recovered/load-bearing authority in AQ001 and AQ004. Promotion: **NOT_EARNED**.

This moved the controlled bottleneck from evidence discovery alone to **authority-preserving evidence selection/budgeting**.

### G1c-R1 zero-model selector counterfactual — posthoc only

On the already-inspected AQ slice, deterministic RRF top-4 happened to produce **6/6 SUFFICIENT_CLEAN** contexts across a broad RRF-k sweep. Because that policy was chosen after seeing R1 failures, it was not promotable. It only justified a new prospective test.

### G1d — complete / deterministic RRF top-4 NOT EARNED

Preregistered on a new separated 23-anchor / 8-question slice (`authority-sufficiency-v1`).

Frozen run:

- run `32322429563`;
- source `c74673a83744789f271fa54c43b20212160007a2`;
- exact `gpt-5.6-luna`;
- semantic calls **24 / 24**;
- model-selector calls **0**;
- rerolls **0**;
- workflow conclusion **success**;
- result SHA-256 `ef57c7a43c782694a0c42d428421b5d9a4bbb72b0a48b52a60c36edafa310bda`;
- result/adjudication merged via PR #184;
- frozen selection promotion: **NOT_EARNED**.

Arms:

- **A:** exact BM25 top-5 -> composer;
- **D:** same initial top-5 -> evidence-aware planner -> targeted BM25 -> deterministic RRF `k=60` -> fixed top-4 -> composer.

Authority result:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A | 3 | 4 | 1 |
| D | 3 | 3 | 2 |

D authority improvements: **0**. D regressions: **1**.

Frozen semantic result:

- A: **7 PASS / 1 CRITICAL_ERROR**;
- D: **5 PASS / 2 PARTIAL / 1 CRITICAL_ERROR**;
- D semantic improvements: **0**;
- D semantic regressions: **2**;
- D new critical errors: **0**.

#### What G1d disproved

The posthoc AQ-slice RRF top-4 result did **not** generalize.

- BQ002: same-name distractor B004 is repeatedly retrieved and RRF places it above the uniquely load-bearing B003 identity bridge; B003 falls to fifth and is dropped.
- BQ007: unrelated same-name product B019 remains in final context.
- BQ008: vendor local-admin capability B023 remains in final context even though it is not customer authorization policy.

RRF consensus can therefore amplify **repeated lexical similarity**, not just repeated authoritative relevance.

#### BQ006 — planner knew what was missing, lexical retrieval still missed it

BQ006 is the most important G1d retrieval failure.

The planner explicitly identifies Cedar's governing EU-only policy as missing. But the authoritative policy anchor B013 ranks:

- exact BM25: **6**;
- first targeted follow-up: **4**;
- second targeted follow-up: absent.

The frozen follow-up candidate cutoff is top-3, so B013 never reaches the candidate pool. Both A and D then give a definitive-looking Cedar compliance conclusion without the governing policy anchor. Both are frozen `CRITICAL_ERROR`.

This is another truth-by-luck class, now for **policy/compliance authority**, not identity.

## New zero-model finding — evidence budget before more retrieval complexity

Posthoc analysis merged via PR #185; **0 model calls**; does not change G1d verdict.

Exact BM25 authority frontier on the G1d slice:

| budget | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| top-3 | 4 | 0 | 4 |
| top-4 | 2 | 2 | 4 |
| top-5 | 3 | 4 | 1 |
| **top-6** | **4** | **4** | **0** |
| top-7 | 4 | 4 | 0 |
| top-8 | 4 | 4 | 0 |

The sole A@5 positive-authority miss is BQ006; B013 sits exactly at rank 6. Therefore A@6 is positive-authority sufficient on **8/8** frozen G1d questions.

The four A@5 risk cases — BQ001/BQ002/BQ007/BQ008 — are all frozen semantic `PASS`: the composer ignored the distractors when the load-bearing authority was present.

This does **not** prove distractors are harmless and does **not** make top-6 a product constant. It does change research priority:

> **On the current controlled evidence, omission of governing/load-bearing authority is more consequential than making every context perfectly clean. Test evidence budget before adding more retrieval/selector machinery.**

The recurrence matters: earlier E023 work also found consequential authority immediately outside fixed top-5 cutoffs. G1d independently reproduces the rank-boundary problem on new material.

## NEXT CORE — prospective evidence-budget comparison, not another selector trick

**Paid calls are paused at this checkpoint. Do not semantically rerun AQxxx or BQxxx. Do not start G2.**

Immediate research question:

> **Can a modest, explicit query-time evidence budget recover load-bearing authority more reliably and cheaply than planner/selector complexity, without causing semantic conflation/noise failures?**

Next deliberate work:

1. treat `top-6` only as a **diagnostic signal**, not a product rule;
2. define the next budget prospectively on **new separated material** before semantic answers exist;
3. prefer an explicit **character/token evidence budget** over permanently hard-coding a source count when practical;
4. compare a strong exact-BM25 budget baseline against any more complex planner/selector path using the same composer;
5. score authority sufficiency, risk, semantic correctness, unsupported claims, model calls, and evidence size separately;
6. keep evaluator clauses offline; no BQ/AQ-specific anchor rules may enter runtime selection;
7. only if a stronger query-time path is earned may G2 persistence even be considered;
8. keep natural Dogfood 0.1.16 running in parallel.

Do not infer from this checkpoint that “six sources is enough.” The hypothesis is **evidence-budget-first**, not `k=6`.

## Natural product dogfood continues in parallel

Observation log: Issue #141. Do not manufacture workload.

Watch naturally for cross-source questions, identity/alias/attribution uncertainty, user-owned decisions spanning sources, temporal correction/disagreement, load-bearing evidence follow-through, uncertainty when bridges are absent, popup/soft-guard friction, hidden maintenance usage, and long-horizon value.

## Do not start merely because it is available

- another paid E023 run before a new prospective evidence-budget contract/slice exists;
- same-slice AQ/BQ semantic reruns;
- G2 persistent semantic dossiers;
- graph DB / universal Entity/Relation/KnowledgeUnit schema;
- automatic identity merge/split or concept routing;
- vector retrieval defaults without an independent gate;
- evaluator clauses as runtime canonical structure;
- background semantic watching/maintenance;
- broad automatic contradiction resolution;
- permanent Tree View/activity UI without natural evidence;
- federation/X2 without recurring natural evidence.

## Retained operating boundaries / known edges

- Copilot CLI compatibility uses runtime capability probing; version alone is not authority.
- `compiled_provider=disabled` remains expected and unrelated to Agent Wiki maintenance.
- daily maintenance limit is a soft guard; `0` disables new model-backed maintenance generation.
- <=40k chars preferred single pass; 40,001–80k allowed; >80k preserves RAW and skips derived maintenance before model call; never silently truncate.
- exact-current-byte remember is no-op reuse without a second admission modal.
- multi-root remains fail-closed in 0.1.16.
- Issue #132 remains the reliability follow-up for deletion detection and relation/pending crash windows.
- Human Knowledge file deletion is not independently detectable without an index.
- E013/E015 remain natural/data-gated; do not manufacture workload/divergence.

## 0.1.16 validated artifact

- source `e9370663d4763ae0f29d67c572d45c5b80f6c120`;
- main validation run `32204779167`;
- Actions artifact `9348765994`;
- publisher `3366df98e33dabbe72d00d396c2ea1820e50d9a4`;
- VSIX bytes `102811`;
- SHA-256 `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`;
- install path `dogfood/releases/llm-wiki-dogfood-latest.vsix`.

## Fast pointers

- Core generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- E023 root: `experiments/E023-generality-retrieval-composition/`
- G1a: PR #165 / run `32215941344`
- G1b: PR #169 / run `32217824760`
- prospective evaluator: PR #172
- G1c-R1: PR #179 / run `32232116273`
- G1c-R1 selector counterfactual: PR #181
- G1d prereg/execution/result: PRs #182/#183/#184 / run `32322429563`
- G1d budget frontier: PR #185 / `g1d-budget-frontier-v0.md`
- G1d result: `g1d-results-v0.md`
- natural installed dogfood: Issue #141
- current VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- user guide: `dogfood/vscode/README.md`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- reliability follow-up: Issue #132

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
