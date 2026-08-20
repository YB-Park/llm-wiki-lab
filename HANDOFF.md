# Current Handoff

Last updated: 2026-08-20 KST — post-G1f / G1-closure checkpoint

This file is the **continuation checkpoint only**. Historical detail belongs in experiments, issues, PRs, ADRs, and Git. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

## Start here

Repository: `YB-Park/llm-wiki-lab`

Authoritative completed semantic result before this checkpoint:

- G1f result merge: `d4897142e28ab950238ee799df51433b7718814f` (#195)
- G1f run: `32349241403`
- execution source: `eab8c9e4f5ebbe5f43b93a1558fd3f9cc295f772`
- evidence commit: `fdae1b5ce645d6951db0d6b703947405c3c3fa78`
- exact model: `gpt-5.6-luna`
- 16/16 semantic calls, zero rerolls
- open PRs were none immediately after #195 merge

Always re-check current `main` and open PRs before new work.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

Architecture thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Generality is demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

Normal product use should remain ordinary VS Code Agent conversation.

## Product baseline

Dogfood **0.1.16** remains the product baseline. E023 is research-only and has not changed runtime behavior.

Authority floor remains:

- explicit per-workspace opt-in;
- Check Setup and Health = 0 model calls / 0 state changes;
- disabling removes Agent availability while preserving Wiki data;
- new source bytes require human confirmation before durable admission;
- `RAW_MEMORY` is immutable admitted evidence/provenance;
- `DERIVED_MEMORY` is noncanonical/rebuildable synthesis;
- `HUMAN_KNOWLEDGE` is explicit user-owned decision/belief/rationale/hypothesis authority;
- changed remembered files require explicit correction/change/dispute/supersede/independent semantics;
- AI summaries remain off by default until granted.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**.

Natural installed dogfood continues on Issue #141. Do not manufacture workload.

## Architecture gates

1. **G1 Retrieval / Composition** — query-time authority discovery, evidence budgeting, composition.
2. **G2 Persistence** — only after a strong G1 path exists, test persistent semantic projection benefit against lifecycle/staleness cost.
3. **G3 Identity / Routing** — only if persistent semantic targets earn value, test automatic discovery/routing/merge-split.

Authority Core remains ontology-agnostic. Every load-bearing derived claim must resolve to terminal `RAW_MEMORY` or `HUMAN_KNOWLEDGE` with epistemic type preserved.

## G1 evidence — current synthesis

### Complexity did not earn itself

- G1a blind planner/RRF: NOT_EARNED.
- G1b evidence-follow: targeted repair only, broad gate NOT_EARNED.
- G1c-R1 model selector: discarded load-bearing evidence; NOT_EARNED.
- G1d deterministic RRF: did not generalize; NOT_EARNED.

Do not reintroduce planner/selector/RRF complexity without a new failure signal.

### G1e — strong simple retrieval signal, strict promotion NOT_EARNED

G1e prospectively compared exact BM25 top-5 vs top-6 on new separated material.

Top-6:

- removed both authority-incomplete contexts;
- authority improvements 2 / regressions 0;
- semantic improvements 2 / regressions 0 / new critical errors 0;
- planner 0 / selector 0.

Strict gate still failed at 6/8 PASS. Exact BM25 top-6 is therefore a **strong experimental baseline**, not a product default.

### G1f — composition candidate NOT_EARNED, simple path safety replicated

PRs #193/#194/#195; run `32349241403`.

O = frozen old composer.  
N = frozen `composition_prompt_v1`.  
Both received byte-identical exact-BM25 top-6 contexts.

Result:

- O: **7 PASS / 1 PARTIAL / 0 CRITICAL_ERROR**
- N: **7 PASS / 1 PARTIAL / 0 CRITICAL_ERROR**
- N improvements vs O: **0**
- regressions: **0**
- new critical errors: **0**
- DQ003 authority-incomplete identity negative control: PASS
- DQ004 proposition-scoped sufficiency: PASS
- DQ001/DQ007 user-owned authority: PASS
- sole shared PARTIAL: DQ006 omitted prospectively required D033 broader-serverless corroboration

Frozen composition candidate promotion required >=1 paired improvement, so:

> **`composition_prompt_v1` promotion is NOT_EARNED. Do not weaken the rule and do not rerun DQ material.**

What G1f still establishes: the existing simple query-time path replicated **7/8 with zero critical errors** on another separated composition-stress slice.

## G1 closure

Current architecture decision:

> **The simple query-time G1 path is strong enough to be the fixed research comparator for G2.**

Carry forward for controlled G2 research:

- exact whole-object BM25 top-6;
- frozen old composer from `run_g1c.py`;
- no planner / selector / RRF.

This does **not** promote either component to product policy.

`composition_prompt_v1` remains a research candidate and is not carried forward as the promoted composer because it showed zero incremental value.

## NEXT CORE — G2 preregistration, zero-model first

G2 design/preregistration may now start. G2 semantic execution and product persistence are **not** yet authorized.

Research question:

> **Holding authority, fixed subject identity, retrieval, and composition constant, does a rebuildable persistent semantic projection improve repeated-use answer quality/cost/latency enough to justify lifecycle and stale-state risk over query-time synthesis alone?**

Required boundaries:

- use new separated repeated-use/update material;
- fixed identities/subjects supplied prospectively; no automatic identity routing;
- control = frozen G1 comparator;
- persistent arm adds only rebuildable DERIVED projection anchored to terminal authority;
- include source addition, correction/supersession, and stale-view negative control;
- measure semantic quality/critical stale claims plus model/rebuild/human cost;
- no graph DB / universal Entity/Relation/KnowledgeUnit schema;
- no vector default;
- prereg PR semantic calls = 0;
- separate execution contract required after prereg merge.

A persistent arm with lower cost but a stale load-bearing claim fails.

## Product / reliability parallel tracks

Issue #141 natural dogfood remains the product-value source. Observe naturally:

- useful ambient recall days/weeks later;
- setup or popup friction;
- daily soft-guard behavior;
- whether hidden Luna usage becomes a repeated real problem;
- whether navigation/history UI is actually missed.

Do not build permanent Tree View/activity UI or usage accounting solely because it is imaginable.

Issue #132 reliability edges remain evidence-gated. Do not preemptively replace the storage model with a database/WAL.

## Do not start merely because it is available

- AQ/BQ/CQ/DQ semantic reruns;
- prompt tuning on frozen DQ material;
- top-6 product default;
- G2 execution before prereg merge + execution contract;
- graph/entity/KU schema;
- automatic identity merge/split/routing;
- vector defaults;
- evaluator clauses as runtime canonical structure;
- background semantic watching;
- broad automatic contradiction resolution;
- federation/X2 without recurring natural evidence.

## Retained operating edges

- Copilot CLI compatibility uses runtime capability probing; version alone is not authority.
- `compiled_provider=disabled` remains expected and unrelated to Agent Wiki maintenance.
- daily maintenance limit is a soft guard; `0` disables new model-backed maintenance generation.
- <=40k chars preferred single pass; 40,001–80k allowed; >80k preserves RAW and skips derived maintenance before model call; never silently truncate.
- exact-current-byte remember is no-op reuse without a second admission modal.
- multi-root remains fail-closed in 0.1.16.
- Human Knowledge file deletion is not independently detectable without an index.
- E013/E015 remain natural/data-gated; do not manufacture workload/divergence.

## Fast pointers

- G1f prereg: #193
- G1f execution contract: #194
- G1f result: #195 / run `32349241403`
- G1f result doc: `experiments/E023-generality-retrieval-composition/g1f-results-v0.md`
- G1 closure: `experiments/E023-generality-retrieval-composition/g1-closure-decision-v0.md`
- generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- natural installed dogfood: Issue #141
- reliability follow-up: Issue #132
- current VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
