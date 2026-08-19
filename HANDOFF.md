# Current Handoff

Last updated: 2026-08-19 KST

This file is the **continuation checkpoint only**. Keep historical evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

The normal product loop is ordinary VS Code Agent conversation. Users should not need to learn Wiki tool names, storage schemas, or filing concepts.

A second core formulation is now explicit:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Generality is demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

## Product baseline — Dogfood 0.1.16

0.1.16 remains the released/dogfood product baseline via PR #159. E023 is research only and changes no product runtime behavior.

Core authority remains unchanged:

- **Set Up Project Memory** is explicit per-workspace opt-in. Before opt-in, Agent tool implementations are unavailable.
- **Check Setup and Health** is pure diagnostics: **0 model calls / 0 state changes**.
- **Disable for This Workspace** removes Agent availability while preserving Wiki data.
- New source bytes require product-owned human confirmation before durable evidence admission.
- **RAW_MEMORY** is immutable factual/provenance evidence.
- **DERIVED_MEMORY** is noncanonical/rebuildable model synthesis.
- **HUMAN_KNOWLEDGE** is explicit user-owned decision/belief/rationale/hypothesis authority; it is not external evidence.
- Changed remembered files require explicit correction/change/dispute/supersede/independent semantics.
- AI summaries remain **OFF by default** until explicitly granted per workspace.

The five Agent tools remain the model-facing mechanism; normal users should not need to invoke them by name.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**. Natural installed multi-session dogfood remains required for product readiness; controlled research does not replace real use.

## Core architecture baseline after advisory review + E023

Tracking: Issue #160. Working gate: `docs/14-generality-and-semantic-projections.md`.

### Authority Core must stay ontology-agnostic

The durable core owns trust facts, not a universal semantic ontology:

- evidence identity/integrity/provenance;
- current/history and explicit temporal/contradiction semantics;
- Human Knowledge authorship;
- permission/privacy boundaries;
- repairable deterministic storage invariants.

Do not add Person/Entity/Relation/KnowledgeUnit concepts to the Authority Core merely to make the Wiki feel more general.

### `source-note-v0` is one projection, not the Wiki ontology

The current Agent Wiki note is useful but deliberately narrow: one source plus developer-friendly `summary / operational_rules / boundaries / open_questions` structure.

Treat it as **one DERIVED source-oriented projection under product test**.

Do not infer that:

- every source should fit that shape;
- source is the permanent semantic unit;
- source notes must mediate every query;
- adding more universal fields to source-note schema equals generality.

### Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be:

- admitted `RAW_MEMORY`; or
- explicit `HUMAN_KNOWLEDGE` for user-owned commitments.

`DERIVED_MEMORY` may be working/navigation/compilation state, but persistence does not make it terminal authority.

### Three gates, in order

1. **G1 Retrieval / Composition** — can authoritative material be found and composed at query time without persistent semantic state?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval fixed and test whether durable projection materially improves repeated use after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent targets themselves earn value, test subject discovery/alias routing/merge-split automation.

A G1 failure is **not** evidence for G2. A G2 success is **not** evidence for G3.

## E023 G1a — completed / NOT EARNED

Preregistration: PR #162 -> main `17d1a2798357c2723c4776a7fa45ffc081124c9f`.

Execution contract: PR #163 -> main `7315b858ed5ce764fa81ed131ee17f77c1ea11ae`.

Frozen semantic run:

- Actions run: `32215941344`
- exact model: `gpt-5.6-luna`
- semantic calls: **30 / 30**
- semantic rerolls: **0**
- immutable result: `experiments/E023-generality-retrieval-composition/evidence/run-32215941344/result.json`
- result SHA-256: `e578feb61454f124fce2294bf1a8e6ce396de213984cd889f760343f788c779a`
- results/adjudication merged via PR #165 -> main `219ac4f0c6e69b64f4dced1910890edb7c84b3f3`.

### Frozen comparison

A:

- exact user question;
- production-shaped BM25;
- top 5 raw source objects;
- one Luna composer.

C / G1a:

- one Luna planner sees only the question;
- 1–3 blind retrieval-query rewrites;
- original + planned-query BM25;
- deterministic RRF(k=60);
- **same top-5 source budget**;
- same Luna composer.

Semantic adjudication:

- A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**
- C: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**
- C net question-level improvements: **0**
- C new critical errors relative A: **0**
- preregistered C promotion: **NOT_EARNED**

C spent 20 calls vs A's 10 and produced no semantic improvement. Tokens and AI-credit/premium-request totals were not machine-readable in this runner; do not infer them from call count.

### Critical Q001 lesson — truth by luck is not enough

Q001 asked who the ABC person repeatedly raising the DPA concern was.

The explicit alias/identity bridge S004 connected `Park Jihoon / Jihoon Park / J.H. Park` and the stable contact metadata.

Both A and C omitted S004 from final context while including same-surname distractor S005. Both nevertheless asserted `J.H. Park == Jihoon Park`.

That merge matches frozen gold, but the supplied authoritative evidence did **not** establish it. This is recorded as:

> **CRITICAL_ERROR — retrieval-rooted epistemic upgrade / unsupported identity merge.**

Do not score a trustworthy Wiki as successful merely because an unsupported inference happened to be true.

### Zero-model posthoc selection frontier

No semantic rerun was performed.

Using only frozen rankings:

- A top-5 complete required-source coverage: **6 / 10**
- A top-6: **7 / 10**
- C top-5: **6 / 10**
- C top-6: **10 / 10**

Every source missing from C top-5 sat exactly at fused rank 6.

This does **not** rescue C's frozen verdict. It shows that the tested blind planner produced some latent retrieval signal which the top-5 selection policy discarded.

Therefore do not summarize E023 as “query-time synthesis failed.” The exact result is narrower:

> **question-only blind query expansion + consensus RRF + fixed top-5 did not outperform the strong simple baseline.**

## NEXT CORE — stay inside G1

Do **not** move to persistent semantic dossiers/entities/graphs yet.

Before any further semantic calls:

1. keep using the frozen E023 artifact for zero-model selection/evidence-budget analysis;
2. if another controlled gate is justified, separately preregister **G1b iterative evidence-follow retrieval**;
3. G1b should resemble the real Agent loop: initial retrieval -> inspect bounded hits/snippets -> identify a concrete missing/ambiguous relation -> targeted follow-up retrieval -> compose under a bounded final evidence budget;
4. use an explicit character/token evidence budget rather than assume source-count `top-k` generalizes to real heterogeneous documents;
5. isolate retrieval improvement from composition policy where possible;
6. for high-consequence identity/attribution claims, test consequence-sensitive behavior: if no authoritative bridge is recovered, retrieve more or surface ambiguity instead of silently merging.

A promising controlled target is Q001 because the missing identity bridge was discoverable (one G1a planned query ranked S004 at 3) yet the frozen RRF/top-5 selector discarded it.

Do not spend another 30-call batch merely to tune retrieval. Use zero-model analysis to narrow the next semantic gate first.

## Natural product dogfood continues in parallel

Observation log: Issue #141.

Real-project dogfood will take time and that is expected. Do not manufacture workload simply to make 0.1.16 look validated.

Watch naturally for:

- cross-source semantic questions that source-note-v0 handles awkwardly;
- identity/alias/attribution uncertainty;
- decisions whose rationale spans sources;
- temporal correction or disagreement;
- whether Agent naturally searches, follows evidence, and asks/expresses uncertainty when a bridge is missing;
- remaining authority-popup fatigue;
- soft-guard usefulness;
- causal error reporting;
- long-horizon value days/weeks later.

A dedicated Tree/View remains evidence-gated.

## Maintenance usage visibility — still important, no longer the leading core question

Internal Luna use remains insufficiently visible:

- **model calls** — locally countable;
- **tokens** — exact only when transport exposes machine-readable input/output/cache usage;
- **AI credits / premium requests** — never infer from calls/tokens; report only upstream values.

Product-owned usage visibility remains a valid UX slice, but do not let it drive semantic architecture. The maintenance mechanism itself may evolve as generality research clarifies which projections deserve persistent upkeep.

## Retained 0.1.16 / maintenance boundaries

- Copilot CLI compatibility uses runtime capability probing; version alone is not the compatibility authority.
- `compiled_provider=disabled` remains expected and unrelated to Agent Wiki maintenance.
- positive daily maintenance setting is a **soft guard**, not a hard cap; Continue Today / Pause AI Summaries Today are available.
- `0` disables new model-backed maintenance generation.
- source-size policy: <=40k preferred single pass; 40,001–80k allowed single pass; >80k preserves RAW and skips derived maintenance before model call; never silently truncate.
- exact-current-byte remember is no-op reuse without a second source-admission modal.
- multi-root remains fail-closed in 0.1.16.

## 0.1.16 validated artifact

- source: `e9370663d4763ae0f29d67c572d45c5b80f6c120`
- main validation run: `32204779167`
- Actions artifact: `9348765994`
- publisher: `3366df98e33dabbe72d00d396c2ea1820e50d9a4`
- VSIX bytes: `102811`
- SHA-256: `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`
- repo release Git blob: `025c90bba243e7594c8e2b621c28bd51e5b9acd3`
- current install path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`

## Do not start merely because it is available

- G2 persistent semantic dossier before a stronger G1 path earns it;
- graph DB / universal Entity/Relation/KnowledgeUnit schema;
- automatic identity merge/split or automatic concept routing;
- vector retrieval default changes without a concrete retrieval gate;
- chunk compiler unless natural >80k sources recur;
- background source watching/semantic maintenance;
- broad automatic contradiction resolution;
- permanent Tree View/activity UI without observed need;
- federation/X2 without recurring natural evidence;
- paid reruns of frozen E017/E018/E019/E021/E022/E023-G1a cases.

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
- E023 G1 result: PR #165 / run `32215941344`
- Installed/natural dogfood: Issue #141
- 0.1.16 release UX: PR #159
- Current validated VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- User guide: `dogfood/vscode/README.md`
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Reliability follow-up: Issue #132
- Backup/restore: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
