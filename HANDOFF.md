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

Tracking: Issue #160. Working gate: `docs/14-generality-and-semantic-projections.md`. Experiment family: `experiments/E023-generality-retrieval-composition/`.

### Authority Core stays ontology-agnostic

The durable core owns evidence identity/integrity/provenance, temporal/contradiction semantics, Human Knowledge authorship, permission/privacy boundaries, and deterministic repairable storage invariants.

Do **not** add Person/Entity/Relation/KnowledgeUnit concepts merely to make the Wiki feel general. `source-note-v0` remains one DERIVED source-oriented projection, not the Wiki ontology.

### Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may help retrieval/navigation/compilation, but persistence never turns it into terminal authority.

### Gates remain ordered

1. **G1 Retrieval / Composition** — can the right authority be found, preserved, and composed at query time without persistent semantic state?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval strong/fixed and test whether durable projections improve repeated use after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent semantic targets themselves earn value, test automatic subject discovery/routing/merge-split.

A G1 failure is **not** evidence for G2. A G2 success would not automatically authorize G3.

## E023 frozen sequence — current interpretation

### G1a / G1b

- G1a run `32215941344`: exact BM25 top-5 and blind planner+RRF both **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**; planner improvements 0; NOT_EARNED.
- Q001 established the trust class: aliases were merged without the explicit authority bridge. **Truth-by-luck is not trustworthy semantic recovery.**
- G1b run `32217824760`: evidence-aware follow-up repaired Q001 `CRITICAL_ERROR -> PASS`, but broad preregistered recovery threshold missed; NOT_EARNED.

### Prospective authority-sufficiency evaluator

E023 now distinguishes:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

The evaluation-only contract can express unique support, alternatives, repeated-support minima, identity/attribution bridges, negative evidence, temporal correction, forbidden conflation, and terminal `HUMAN_KNOWLEDGE`. It is **not** product storage or a canonical claim graph.

### G1c-R1 — model final selector NOT EARNED

Run `32232116273`, exact Luna, 18/18 calls, zero rerolls.

Candidate pools reached positive-authority sufficiency on **6/6**, but the model selector discarded load-bearing evidence and produced two insufficient final contexts. This moved the bottleneck from discovery alone to authority-preserving evidence budgeting/selection.

### G1d — deterministic RRF top-4 NOT EARNED

Run `32322429563`, source `c74673a83744789f271fa54c43b20212160007a2`, exact Luna, 24/24 calls, zero rerolls.

- A exact BM25 top-5: **3 clean / 4 risk / 1 insufficient**;
- D planner + targeted BM25 + deterministic RRF top-4: **3 clean / 3 risk / 2 insufficient**;
- D authority improvements 0, regressions 1;
- semantic A **7 PASS / 1 CRITICAL**;
- semantic D **5 PASS / 2 PARTIAL / 1 CRITICAL**;
- deterministic RRF did not generalize from the posthoc G1c slice.

BQ006 was especially informative: the planner correctly identified the missing governing policy, but lexical candidate generation still excluded that authority. Both arms then made a truth-by-luck compliance conclusion.

### G1d zero-model budget frontier

PR #185, 0 model calls:

- exact BM25 top-5: 3 clean / 4 risk / 1 insufficient;
- exact BM25 top-6: **4 clean / 4 risk / 0 insufficient**;
- sole top-5 positive-authority miss sat at exact rank 6;
- all four top-5 risk cases were frozen semantic PASS.

This was a budget signal, not a top-6 product rule.

## G1e — exact top-5 vs top-6 prospective replication

G1e used a **new separated 35-anchor / 8-question slice** and a two-stage gate.

### Phase 0 — zero-model authority gate PASSED

PR #187, 0 model calls:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A5 exact BM25 top-5 | 2 | 4 | 2 |
| B6 same ranking top-6 | 3 | 5 | **0** |

B6 authority improvements: **2**.  
B6 authority regressions: **0**.

The rank-6 additions repaired two prospectively frozen authority misses:

- CQ001: explicit `R. Singh -> Rina Singh` identity bridge;
- CQ008: second independent monthly-close observation required to establish recurrence.

Evidence characters increased roughly 12–29% per question. No global character threshold was claimed; current product 6,000/12,000-char boundaries are per-source `wikiRead`, not multi-source answer budgets.

### Phase 1 — semantic run complete / strict promotion NOT EARNED

Frozen run:

- run `32324460519`;
- source `505740b74776fc7b7988e9c168c9c9d0ed2067fa`;
- exact `gpt-5.6-luna`;
- semantic calls **16 / 16**;
- planner calls **0**;
- selector calls **0**;
- rerolls **0**;
- workflow success;
- result SHA-256 `865d89ad8c8b219493823bd21413196f658a9ffa2fdd3ed2948bb34b20f16727`;
- result/adjudication merged via PR #189.

Frozen semantic result:

- A5: **5 PASS / 1 PARTIAL / 1 FAIL_RETRIEVAL / 1 CRITICAL_ERROR**;
- B6: **6 PASS / 2 PARTIAL / 0 FAIL / 0 CRITICAL_ERROR**;
- B6 semantic improvements: **2**;
- B6 semantic regressions: **0**;
- B6 new critical errors: **0**.

The frozen rule required at least **7/8 B6 PASS**. Actual was 6/8.

> **G1e strict promotion is NOT_EARNED. Do not weaken the frozen rule.**

### What G1e genuinely earned

The simple evidence-budget mechanism signal is now prospective and materially stronger:

1. B6 removed **both** authority insufficiencies with zero authority regressions;
2. CQ001 moved from A5 truth-by-luck identity `CRITICAL_ERROR` to supported B6 `PASS` when rank-6 identity authority entered context;
3. CQ008 moved from safe A5 retrieval insufficiency to complete repeated-observation authority under B6;
4. the sixth object caused **0 semantic regressions and 0 new critical errors** across the eight questions;
5. the result required **no planner and no selector calls**.

This does **not** make six sources a product default. It establishes exact-BM25 + modestly larger evidence prefix as the current **strong simple retrieval baseline**.

### Why the strict gate still failed — composition is now the binding bottleneck

B6 has **0 authority-incomplete contexts**. Its two remaining partials are composition-side:

- **CQ002 — `COMPOSITION_OVERCAUTIOUS_INSUFFICIENCY`:** the context is sufficient for the frozen `could satisfy` proposition, the prose answer is substantively correct, but `insufficient_authority=true` demands a stronger unstated guarantee.
- **CQ008 — `COMPOSITION_EPISTEMIC_TYPE_OMISSION`:** the context now contains the user-owned C034 capacity decision plus two independent raw observations, but the answer presents the decision as an ordinary fact rather than making explicit that terminal decision authority is `HUMAN_KNOWLEDGE`.

These are recurring E023 classes, not new G1e noise failures.

## NEXT CORE — composition authority semantics, not more retrieval tuning

**Paid calls pause here. Do not semantically rerun AQxxx/BQxxx/CQxxx. Do not start G2.**

Immediate research question:

> **Can the composer preserve terminal epistemic type and calibrate insufficiency to the actual load-bearing proposition, without exposing internal storage jargon or importing evaluator clauses/domain schemas into runtime?**

Next deliberate work:

1. treat B6 as the strong simple retrieval baseline for the next composition test; do **not** tune retrieval again first;
2. define a small **generic composition contract** for at least:
   - explicit user-owned decision/belief/rationale authority;
   - direct vs attributed evidence;
   - missing identity/policy bridges;
   - proposition-scoped insufficiency rather than stronger unstated guarantees;
3. keep the contract architecture-level and ontology-agnostic — no Cxxx/AQ/BQ-specific rules and no product claim graph;
4. validate the contract itself with zero model calls and adversarial fixtures before any paid run;
5. only then use **new separated material** for a composer comparison while holding retrieval/evidence budget fixed;
6. measure semantic PASS/critical errors, epistemic-type preservation, insufficiency calibration, citations, and model calls separately;
7. a composition success still would not by itself authorize G2; natural Dogfood evidence remains necessary.

The key shift is:

> **The leading controlled problem is no longer “can we get enough authority into context?” On the G1e B6 slice, we can. The next problem is “does the Agent express exactly what that authority permits, with the right epistemic type?”**

## Natural product dogfood continues in parallel

Observation log: Issue #141. Do not manufacture workload.

Watch naturally for cross-source questions, identity/alias/attribution uncertainty, user-owned decisions spanning sources, temporal correction/disagreement, load-bearing evidence follow-through, uncertainty when bridges are absent, popup/soft-guard friction, hidden maintenance usage, and long-horizon value.

## Do not start merely because it is available

- another paid retrieval/planner/selector tuning run before a composition contract is frozen;
- same-slice AQ/BQ/CQ semantic reruns;
- a hard-coded top-6 product default;
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

## Fast pointers

- Core generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- E023 root: `experiments/E023-generality-retrieval-composition/`
- prospective evaluator: PR #172
- G1c-R1: PR #179 / run `32232116273`
- G1d: PRs #182/#183/#184 / run `32322429563`
- G1d budget frontier: PR #185
- G1e Phase 0 / execution / result: PRs #187/#188/#189 / run `32324460519`
- G1e result: `g1e-results-v0.md`
- natural installed dogfood: Issue #141
- current VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- user guide: `dogfood/vscode/README.md`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- reliability follow-up: Issue #132

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
