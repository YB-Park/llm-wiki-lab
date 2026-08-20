# Current Handoff

Last updated: 2026-08-20 KST — session-transfer checkpoint

This file is the **continuation checkpoint only**. Historical detail belongs in experiments, issues, PRs, ADRs, and Git. If this file conflicts with merged code or an accepted ADR, code/ADR wins and this file should be fixed immediately.

## Start here in a new session

Repository: `YB-Park/llm-wiki-lab`

Current authoritative `main` at this checkpoint:

- `edb571c0b431481ddac451fb5fc79a9b1b6eadeb`
- merge: **Freeze E023 authority-preserving composition contract (#191)**
- open PRs: **none** immediately after #191 merge

Before doing any work, re-check `main` and open PRs because they may have moved after this handoff was written.

### Important interrupted-session warning

There is a branch named `agent/e023-g1f-execution`. **Do not run it, do not open it as an execution PR, and do not treat it as preregistered work.**

It was created during an interrupted long session from the pre-#191 main (`714bc70a...`) and contains only four draft execution files:

- `experiments/E023-generality-retrieval-composition/g1f-execution-addendum-v0.md`
- `experiments/E023-generality-retrieval-composition/run_g1f.py`
- `experiments/E023-generality-retrieval-composition/validate_g1f_execution.py`
- `remote-lab/e023-g1f-request.json`

The draft runner imports `composition_prompt_v1` and expects an `authority-sufficiency-v3/` package. `composition_prompt_v1.py` is now on main only because #191 merged; **`authority-sufficiency-v3` does not exist in the repository at this checkpoint**. Therefore the branch is an incomplete scaffold, not an executable experiment contract.

No G1f preregistration PR exists. A repository search for G1f PRs returns only #191, which explicitly says **no G1f execution yet**.

**Preferred continuation:** create a fresh G1f preregistration branch from current main. Do not salvage the interrupted execution branch unless it is first rebased and audited against a newly merged preregistration; recreating it later is safer and clearer.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

Current architecture thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Generality is demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

Normal product use should remain ordinary VS Code Agent conversation. Users should not need to learn Wiki tool names, storage schemas, filing concepts, or semantic infrastructure.

## Product baseline remains Dogfood 0.1.16

E023 remains research-only and has not changed the product runtime.

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

Natural observation continues on Issue #141. Do not manufacture workload.

## Core architecture boundary

Tracking: Issue #160  
Working gate: `docs/14-generality-and-semantic-projections.md`  
Experiment family: `experiments/E023-generality-retrieval-composition/`

### Authority Core stays ontology-agnostic

The durable core owns evidence identity/integrity/provenance, temporal/contradiction semantics, Human Knowledge authorship, permission/privacy boundaries, and deterministic repairable storage invariants.

Do **not** add Person/Entity/Relation/KnowledgeUnit concepts merely to make the Wiki feel general. `source-note-v0` remains one DERIVED source-oriented projection, not the Wiki ontology.

### Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may help retrieval/navigation/compilation, but persistence never turns it into terminal authority.

### Gates remain ordered

1. **G1 Retrieval / Composition** — can the right authority be found, preserved, and composed at query time without persistent semantic state?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval strong/fixed and test durable-projection benefit after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent semantic targets themselves earn value, test automatic subject discovery/routing/merge-split.

A G1 failure is not evidence for G2. A G2 success would not automatically authorize G3.

## E023 evidence sequence — compressed

### G1a / G1b

- G1a run `32215941344`: exact BM25 top-5 and blind planner+RRF both **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**; planner improvements 0; `NOT_EARNED`.
- Q001 established the trust class: aliases were merged without an explicit authority bridge. **Truth-by-luck is not trustworthy semantic recovery.**
- G1b run `32217824760`: evidence-aware follow-up repaired Q001 `CRITICAL_ERROR -> PASS`, but the broad preregistered recovery threshold was missed; `NOT_EARNED`.

### Prospective authority-sufficiency evaluator

E023 now separates:

- `INSUFFICIENT_AUTHORITY`;
- `SUFFICIENT_CLEAN`;
- `SUFFICIENT_WITH_CONFLATION_RISK`.

The evaluator can express unique support, alternatives, repeated-support minima, identity/attribution bridges, negative evidence, temporal correction, forbidden conflation, and terminal `HUMAN_KNOWLEDGE`. It is **evaluation-only**, not product storage or a canonical claim graph.

### G1c-R1

Run `32232116273`, exact Luna, 18/18 calls, zero rerolls. Candidate pools reached positive-authority sufficiency on **6/6**, but the model selector discarded load-bearing evidence. Final selection `NOT_EARNED`.

### G1d

Run `32322429563`, exact Luna, 24/24 calls, zero rerolls.

- A exact BM25 top-5: **3 clean / 4 risk / 1 insufficient**;
- D planner + targeted BM25 + deterministic RRF top-4: **3 clean / 3 risk / 2 insufficient**;
- semantic A: **7 PASS / 1 CRITICAL**;
- semantic D: **5 PASS / 2 PARTIAL / 1 CRITICAL**;
- deterministic RRF did not generalize; `NOT_EARNED`.

Zero-model frontier PR #185 then showed exact top-6 removed the sole positive-authority miss on that separated slice. This became an evidence-budget signal, not a top-6 product rule.

## G1e — current strongest retrieval evidence

G1e used a new separated 35-anchor / 8-question slice.

### Phase 0 — zero-model authority gate

PR #187:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A5 exact BM25 top-5 | 2 | 4 | 2 |
| B6 same ranking top-6 | 3 | 5 | **0** |

B6 authority improvements: **2**. Regressions: **0**.

Rank-6 evidence repaired two prospectively frozen misses:

- CQ001: explicit `R. Singh -> Rina Singh` identity bridge;
- CQ008: second independent monthly-close observation required to establish recurrence.

### Phase 1 — semantic result

Frozen run:

- run `32324460519`;
- source `505740b74776fc7b7988e9c168c9c9d0ed2067fa`;
- exact `gpt-5.6-luna`;
- 16/16 semantic calls;
- planner 0 / selector 0 / rerolls 0;
- result SHA-256 `865d89ad8c8b219493823bd21413196f658a9ffa2fdd3ed2948bb34b20f16727`;
- result/adjudication PR #189.

Semantic result:

- A5: **5 PASS / 1 PARTIAL / 1 FAIL_RETRIEVAL / 1 CRITICAL_ERROR**;
- B6: **6 PASS / 2 PARTIAL / 0 FAIL / 0 CRITICAL_ERROR**;
- B6 improvements: **2**;
- B6 regressions: **0**;
- B6 new critical errors: **0**.

Frozen promotion required at least **7/8 B6 PASS**, so G1e remains **NOT_EARNED**. Do not weaken the frozen threshold.

What G1e did earn: exact BM25 plus a modestly larger evidence prefix is the current **strong simple retrieval baseline**. On that slice it removed all authority-incomplete contexts with no semantic regressions and no planner/selector calls.

The remaining G1e failures were composition-side:

- CQ002: `COMPOSITION_OVERCAUTIOUS_INSUFFICIENCY` — a support-complete `could satisfy` proposition was marked insufficient because the answer silently demanded a stronger guarantee;
- CQ008: `COMPOSITION_EPISTEMIC_TYPE_OMISSION` — a load-bearing user-owned decision was presented as an ordinary fact rather than preserving its ownership/epistemic type.

## Composition contract v0 — now frozen on main

PR #191 merged at `edb571c0...` after all zero-model/repo checks succeeded.

Authoritative files:

- `experiments/E023-generality-retrieval-composition/authority-preserving-composition-contract-v0.md`
- `experiments/E023-generality-retrieval-composition/composition-contract-fixtures-v0.json`
- `experiments/E023-generality-retrieval-composition/composition_prompt_v1.py`
- `experiments/E023-generality-retrieval-composition/validate_composition_contract.py`
- `.github/workflows/validate-e023-composition-contract.yml`

Status of contract v0:

> **PROSPECTIVE / ZERO-MODEL DESIGN CONTRACT / NOT YET A PROMOTED COMPOSER**

Core rule:

> **Answer only what the supplied terminal authority permits, preserve what kind of authority it is, and scope uncertainty to the proposition the user actually asked.**

Frozen generic behaviors C1–C8 cover:

1. user-owned epistemic commitment in natural language without requiring storage jargon;
2. direct vs attributed authorship;
3. no synthesized missing identity/policy/project/authorization bridge;
4. proposition-scoped insufficiency;
5. negative evidence and scope limits;
6. temporal hypothesis/signal/final/correction semantics;
7. citations terminating in supplied authority;
8. conflation risk not automatically implying insufficiency when explicit authority resolves the proposition.

The prompt candidate receives no evaluator clauses, expected answers, verdicts, promotion thresholds, or domain-specific hidden rules.

# NEXT CORE — prospectively preregister G1f; do not execute yet

**Paid semantic calls are paused. Do not rerun AQxxx, BQxxx, or CQxxx. Do not start G2.**

Immediate research question:

> **Does the frozen generic composition contract improve epistemic-type preservation and proposition-scoped sufficiency on new separated material when retrieval/evidence context is held identical?**

Recommended next sequence:

1. **Start fresh from current main.** Do not use `agent/e023-g1f-execution` as the basis.
2. Create a **new separated G1f corpus/question set** before model answers exist. A name such as `authority-sufficiency-v3` was used in an interrupted scaffold, but that name and corpus are not frozen; choose/freeze it prospectively.
3. Hold retrieval fixed to the current strong simple baseline for the causal comparison. Exact BM25 top-6 is the leading experimental baseline from G1e, but still **not a product policy**.
4. Feed the **identical selected context** to both arms:
   - O: frozen old composer;
   - N: `composition_prompt_v1` implementing contract v0.
5. Include enough cases to exercise user-owned decisions, direct/attributed evidence, identity or policy bridges, proposition-scoped insufficiency, temporal correction, negative characterization, and repeated support. At least one deliberately authority-incomplete negative control is useful, but freeze its retrieval condition before semantic outputs.
6. Add a **zero-model prereg validator and CI first**. It should prove corpus separation, identical O/N contexts, intended authority-sufficiency/negative-control conditions, no evaluator leakage into the new prompt, and `semantic_calls_authorized_on_this_pr=false`.
7. Merge that preregistration before creating an execution contract.
8. Only after prereg merge, create a **fresh execution branch from that merge SHA**. Freeze exact model, exact call count, zero rerolls, failure-safe evidence capture, and promotion criteria before any semantic call.
9. The interrupted WIP runner assumed 8 old + 8 new = 16 Luna calls, planner 0, selector 0. Treat this only as a **draft proposal**, not a frozen authorization. Re-decide and preregister it explicitly.
10. Adjudicate retrieval/context status separately from composition semantics. Measure at least semantic PASS/critical errors, user-owned-authority preservation, proposition-scoped insufficiency, bridge restraint, citation support, and model-call cost.
11. Even a successful G1f does not automatically authorize G2. First decide whether G1 as a whole is strong enough and continue natural Dogfood evidence in parallel.

## Do not start merely because it is available

- the interrupted `agent/e023-g1f-execution` branch as-is;
- semantic calls before a new G1f prereg is merged;
- same-slice AQ/BQ/CQ reruns;
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

## Retained operating edges

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

- current `main`: `edb571c0b431481ddac451fb5fc79a9b1b6eadeb` (#191)
- generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- E023 root: `experiments/E023-generality-retrieval-composition/`
- prospective evaluator: PR #172
- G1c-R1: PR #179 / run `32232116273`
- G1d: PRs #182/#183/#184 / run `32322429563`
- G1d budget frontier: PR #185
- G1e: PRs #187/#188/#189 / run `32324460519`
- G1e checkpoint: PR #190
- composition contract v0: PR #191
- natural installed dogfood: Issue #141
- current VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- user guide: `dogfood/vscode/README.md`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- reliability follow-up: Issue #132
