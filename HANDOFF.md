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

## Core architecture baseline

Tracking: Issue #160. Working gate: `docs/14-generality-and-semantic-projections.md`. Experiment: `experiments/E023-generality-retrieval-composition/`.

### Authority Core stays ontology-agnostic

The durable core owns trust facts rather than a universal semantic ontology:

- evidence identity / integrity / provenance;
- current/history and explicit temporal/contradiction semantics;
- Human Knowledge authorship;
- permission/privacy boundaries;
- deterministic repairable storage invariants.

Do not add Person/Entity/Relation/KnowledgeUnit concepts to the Authority Core merely to make the Wiki feel more general.

### `source-note-v0` is one projection, not the Wiki ontology

The current Agent Wiki note is useful but narrow: one source plus developer-friendly summary/rules/boundaries/open-questions structure.

Treat it as **one DERIVED source-oriented projection under product test**.

Do not infer that:

- every source should fit that shape;
- source is the permanent semantic unit;
- source notes must mediate every query;
- adding more universal fields to source-note schema equals generality.

### Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. `DERIVED_MEMORY` may be working/navigation/compilation state, but persistence does not make it terminal authority.

### Three gates, in order

1. **G1 Retrieval / Composition** — can authoritative material be found and composed at query time without persistent semantic state?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval fixed and test whether durable projection materially improves repeated use after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent targets themselves earn value, test subject discovery/alias routing/merge-split automation.

A G1 failure is **not** evidence for G2. A G2 success is **not** evidence for G3.

## E023 G1a — completed / NOT EARNED

Frozen semantic run:

- run `32215941344`
- execution source `7315b858ed5ce764fa81ed131ee17f77c1ea11ae`
- exact `gpt-5.6-luna`
- semantic calls **30 / 30**
- rerolls **0**
- result SHA-256 `e578feb61454f124fce2294bf1a8e6ce396de213984cd889f760343f788c779a`
- result/adjudication merged via PR #165 -> main `219ac4f0c6e69b64f4dced1910890edb7c84b3f3`

A = exact question -> BM25 -> top-5 -> composer.

C = question-only Luna planner -> 1–3 blind query rewrites -> BM25 -> deterministic RRF -> same top-5 -> same composer.

Frozen semantic adjudication:

- A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**
- C: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**
- C semantic improvements: **0**
- C new critical errors: **0**
- promotion: **NOT_EARNED**

C added 10 planner calls and produced no semantic improvement.

### Q001 trust lesson

Both A and C omitted S004, the explicit bridge connecting `Park Jihoon / Jihoon Park / J.H. Park`, while a same-surname distractor remained in context. Both nevertheless asserted the identity merge.

The merge happened to match frozen gold, but the supplied authority did not establish it.

> **Truth-by-luck is not trustworthy semantic recovery.**

Q001 is recorded as `CRITICAL_ERROR` for a retrieval-rooted unsupported identity merge / epistemic upgrade.

### G1a zero-model frontier

Using only frozen rankings, without semantic reruns:

- A@5 flat required-source complete: **6 / 10**
- A@6: **7 / 10**
- C@5: **6 / 10**
- C@6: **10 / 10**

Every source missing from C top-5 sat at fused rank 6. This did not rescue C's frozen semantic verdict, but it motivated an evidence-follow test rather than a persistence jump.

## E023 G1b — completed / frozen promotion NOT EARNED / targeted trust repair observed

Preregistration: PR #167.

Execution contract: PR #168 -> source `7c604dd8d57a90c99526bdce5fb55fe7cdb7056f`.

Frozen run:

- run `32217824760`
- exact `gpt-5.6-luna`
- semantic calls **12 / 12**
- rerolls **0**
- result SHA-256 `0b092a1b85577a12bb664fc9bee31a648b316fc317277d35454a9a72c0b7c2c1`
- immutable evidence commit `58adefbc321c51734ca834b592e2f8e364e52d0d`
- result/adjudication/support analysis merged via PR #169 -> main `f97462f158fbb273607bee14d050440a5b2d1c31`

G1b targeted only Q001/Q002/Q004/Q010, selected prospectively from frozen retrieval condition `A recall@5 < 1 AND C recall@5 < 1`.

Loop:

1. same exact-query top-5 as G1a A;
2. planner inspects bounded metadata/snippets for those hits;
3. planner states a missing/ambiguous relation and issues 0–2 targeted queries;
4. same BM25 adds temporary candidates;
5. selector chooses at most five final sources;
6. unchanged G1a composer answers from selected full evidence.

No persistent semantic state and no identity-specific composer rule were added.

### Frozen G1b result

- previously-missing source reached candidate pool: **2 / 4**
- previously-missing source entered final context: **1 / 4**
- semantic verdicts: **4 PASS / 0 PARTIAL / 0 FAIL / 0 CRITICAL**
- semantic improvements vs frozen A: **1**
- regressions: **0**
- new critical errors: **0**

The preregistered promotion rule required final recovery for at least **3 / 4** targets. Actual was 1 / 4.

> **G1b promotion is NOT_EARNED. Do not retroactively weaken the frozen rule.**

### What G1b did genuinely earn

Q001 improved `CRITICAL_ERROR -> PASS`.

The planner recognized the missing identity/disambiguation relation, queried for `J.H. Park` / `Jihoon Park`, retrieved S004 at rank 1, and the selector chose S001/S003/S004 while dropping the same-surname distractor. The composer prompt was unchanged.

This is a real mechanism signal:

> **Evidence-aware follow-up retrieval repaired the exact authoritative bridge whose absence caused the critical trust failure.**

It does not yet earn G1b as a broad product policy.

## New evaluation finding — authority sufficiency, not flat source-list completeness

G1b exposed a problem in E023's original flat `required_sources` metric: it treated uniquely load-bearing authority and redundant corroboration as equivalent.

Examples:

- Q001 S004 is genuinely load-bearing for the identity merge.
- Q002 S003 is corroborating when S001 provides meeting attribution and S004 provides the identity bridge.
- Q004 S008 corroborates rationale already directly recorded in S009.
- Q010 S003 is not necessary to reject the broad anti-cloud characterization when S002 provides explicit negative evidence.

A **posthoc / zero-model / non-primary** support-clause hypothesis was added only to explain frozen outcomes. It does not alter G1a/G1b verdicts and is not a product claim graph.

Against already-frozen selected contexts:

- G1a A flat complete: **6 / 10**; support-clause complete: **9 / 10**
- G1a C flat complete: **6 / 10**; support-clause complete: **9 / 10**
- G1b final contexts: **4 / 4 support-complete**
- unique G1a support-incomplete question: **Q001**, exactly the frozen critical error
- Q008 is support-complete yet semantically PARTIAL, separating composition omission from retrieval insufficiency.

The useful evaluation question is now:

> **Did the context contain enough authoritative support to establish every load-bearing proposition in the expected answer?**

Evaluation may need:

- uniquely required authority;
- one-of alternative support;
- minimum repeated support for claims like “repeatedly”;
- explicit negative evidence;
- explicit identity/attribution bridges;
- forbidden-conflation checks.

This richer evaluator may be more structured than product storage. **Do not turn evaluation clauses into canonical Wiki nodes or a claim graph.**

## NEXT CORE — prospectively freeze authority-sufficiency evaluation before more paid tuning

Do **not** run G1c or G2 yet.

Next deliberate work:

1. define a small **evaluation-only authority-sufficiency contract** prospectively, before seeing held-out answers;
2. use held-out or clearly separated material so the support clauses are not reverse-engineered from E023 outcomes;
3. include load-bearing unique support, alternative support, repeated-support minima, negative evidence, identity/attribution bridges, and forbidden conflation;
4. verify the evaluator itself with zero model calls;
5. only then decide whether another G1 retrieval/selection/composition mechanism comparison deserves semantic calls;
6. keep persistence/entity/graph/automatic routing outside scope until a stronger G1 path plus natural dogfood gives evidence for them.

The immediate research question is no longer “which retrieval trick is best?” It is:

> **Can we prospectively measure whether the Agent received the authority necessary for a trustworthy semantic claim, without confusing redundant corroboration with missing evidence?**

Paid retrieval tuning pauses until that measurement contract is frozen.

## Natural product dogfood continues in parallel

Observation log: Issue #141.

Watch naturally for:

- cross-source semantic questions that source-note-v0 handles awkwardly;
- identity/alias/attribution uncertainty;
- decisions whose rationale spans sources;
- temporal correction or disagreement;
- whether Agent naturally searches and follows load-bearing evidence;
- whether it expresses uncertainty when an authoritative bridge is absent;
- popup fatigue / soft-guard usefulness / causal error reporting;
- long-horizon value days or weeks later.

A dedicated Tree/View remains evidence-gated.

## Retained 0.1.16 / maintenance boundaries

- Copilot CLI compatibility uses runtime capability probing; version alone is not the compatibility authority.
- `compiled_provider=disabled` remains expected and unrelated to Agent Wiki maintenance.
- positive daily maintenance setting is a **soft guard**, not a hard cap.
- `0` disables new model-backed maintenance generation.
- source-size policy: <=40k preferred single pass; 40,001–80k allowed single pass; >80k preserves RAW and skips derived maintenance before model call; never silently truncate.
- exact-current-byte remember is no-op reuse without a second source-admission modal.
- multi-root remains fail-closed in 0.1.16.

## 0.1.16 validated artifact

- source `e9370663d4763ae0f29d67c572d45c5b80f6c120`
- main validation run `32204779167`
- Actions artifact `9348765994`
- publisher `3366df98e33dabbe72d00d396c2ea1820e50d9a4`
- VSIX bytes `102811`
- SHA-256 `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`
- current install path `dogfood/releases/llm-wiki-dogfood-latest.vsix`

## Do not start merely because it is available

- another paid E023 retrieval-tuning run before prospective authority-sufficiency evaluation is frozen;
- G2 persistent semantic dossier;
- graph DB / universal Entity/Relation/KnowledgeUnit schema;
- automatic identity merge/split or automatic concept routing;
- vector retrieval default changes without a concrete gate;
- chunk compiler unless natural >80k sources recur;
- background source watching/semantic maintenance;
- broad automatic contradiction resolution;
- permanent Tree View/activity UI without observed need;
- federation/X2 without recurring natural evidence;
- paid reruns of frozen E017/E018/E019/E021/E022/E023 G1a/G1b cases.

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
- G1b prereg/execution/result: PRs #167/#168/#169 / run `32217824760`
- G1b result doc: `experiments/E023-generality-retrieval-composition/g1b-results-v0.md`
- support-clause analysis: `experiments/E023-generality-retrieval-composition/support-clause-analysis-v0.md`
- Installed/natural dogfood: Issue #141
- 0.1.16 release UX: PR #159
- Current validated VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- User guide: `dogfood/vscode/README.md`
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Reliability follow-up: Issue #132

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
