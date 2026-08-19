# Design Question Register

This is the **current** register of architecture/product questions. Keep it concise and update statuses as accepted ADRs or active evidence gates change. Historical wording and abandoned candidate detail remain in Git history, experiments, issues, and ADRs.

A question becomes `DECIDED` only when an accepted ADR actually resolves policy. Experiment results can narrow a question without silently becoming policy.

## Status vocabulary

- `OPEN` — unresolved and not on the active critical path.
- `RESEARCHING` — active prior-art/implementation review.
- `EXPERIMENTING` — an active evidence gate or natural dogfood observation is deciding the next move.
- `DECIDED` — resolved by accepted ADR.
- `REOPENED` — an accepted decision is under explicit reconsideration.

## A. Ingestion and selection

### Q-INGEST-001 — What should be eligible for durable ingestion?
**Status:** OPEN / NATURAL DOGFOOD

Over-capture creates retrieval/maintenance debt; under-capture recreates rediscovery work. Real installed use remains the authority for the capture threshold.

### Q-INGEST-002 — Should raw sources be immutable?
**Status:** **DECIDED — ADR-0004 / ADR-0007**

Immutable SHA-addressed raw content is the authority floor. Evidence revisions are separate opaque identities; semantic reads verify declared raw identity before use.

### Q-INGEST-003 — Should new information update derived Wiki state immediately?
**Status:** EXPERIMENTING — 0.1.16 DOGFOOD / E013 / E023

RAW admission is immediate after explicit approval. `source-note-v0` maintenance is optional/derived/off-by-default and must not be generalized into a universal persistent semantic layer. Broader persistence must earn value after a strong query-time path exists.

### Q-INGEST-004 — How should conversations and personal thoughts enter the system?
**Status:** OPEN WITH HUMAN_KNOWLEDGE FLOOR

Explicit user-owned decisions/beliefs/rationale belong to `HUMAN_KNOWLEDGE`, not external RAW evidence. Additional conversation-capture policy remains open.

## B. Knowledge representation

### Q-REP-001 — What is the canonical knowledge unit?
**Status:** **EXPERIMENTING — E023 / Issue #160**

The current answer is deliberately asymmetric:

- the **Authority Core** has durable evidence/history/Human Knowledge units;
- no universal semantic Wiki unit is accepted;
- `source-note-v0` is one DERIVED source-oriented projection, not the ontology;
- query-time semantic views are first-class candidates;
- semantic persistence is an optimization that must earn itself.

See `docs/14-generality-and-semantic-projections.md`.

### Q-REP-002 — Which epistemic classes require distinct authority?
**Status:** OPEN ABOVE CURRENT FLOOR

The minimum product floor distinguishes `RAW_MEMORY`, `DERIVED_MEMORY`, and `HUMAN_KNOWLEDGE`. Do not add universal fact/hypothesis/entity schemas until they materially improve trust or retrieval.

### Q-REP-003 — How much structure belongs in metadata vs prose?
**Status:** OPEN / E023-GATED

Current core metadata stays narrow. A future semantic projection may have task-specific structure, but common safety properties are more important than one common schema.

### Q-REP-004 — What is the optimal document/retrieval granularity?
**Status:** EXPERIMENTING — E015 + E023

W0 whole-object lexical retrieval remains the product floor. E023 shows that source-count top-k is a crude evidence budget: a load-bearing source can sit just outside the cutoff even when another query retrieves it well. Future gates should reason in explicit character/token evidence budgets where practical.

## C. Classification, schema, and semantic identity

### Q-SCHEMA-001 — How much hierarchy should exist initially?
**Status:** OPEN

### Q-SCHEMA-002 — Who may create a new category/page/projection type?
**Status:** OPEN

### Q-SCHEMA-003 — How should taxonomy rename/split/merge/migration work?
**Status:** OPEN

### Q-SCHEMA-004 — How should semantic subjects and aliases be resolved?
**Status:** **EXPERIMENTING — E023 G1, NO PERSISTENT IDENTITY SYSTEM**

E023 Q001 produced a concrete trust failure: the explicit identity bridge was absent from context, yet Luna confidently merged `J.H. Park` with `Jihoon Park`. The merge happened to match frozen gold, but authority did not establish it.

Current consequence:

- identity/alias similarity is not authority;
- high-consequence identity claims need an explicit authoritative bridge, further retrieval, or expressed ambiguity;
- do **not** add automatic entity merge/split, persistent identity objects, or graph infrastructure from this result.

The architectural concept is broader than people: project/concept/vendor/incident/decision subject identity can have the same problem.

## D. Update, contradiction, and time

### Q-UPD-001 — How should replacement, correction, change, and disagreement differ?
**Status:** **DECIDED — ADR-0005**

Generic replacement, explicit correction, change with separate `effective_at`/`recorded_at`, and symmetric unresolved dispute are distinct caller-explicit semantics. No winner or relation type is inferred by the LLM.

### Q-UPD-002 — Do we need temporal metadata as a first-class concept?
**Status:** **DECIDED AT MINIMUM FLOOR — ADR-0005**

The accepted floor preserves `effective_at` and `recorded_at` for explicit change. Full bitemporal/as-of machinery remains unearned.

### Q-UPD-003 — How should unresolved contradictions be represented?
**Status:** **DECIDED AT MINIMUM FLOOR — ADR-0005**

Two current evidence revisions may be explicitly disputed while both remain current; answer context must preserve unresolved disagreement.

### Q-UPD-004 — What triggers reconsolidation of a derived projection?
**Status:** OPEN / E013 + E023 DEPENDENT

Do not design broad recurring semantic maintenance until both persistence value and realistic reuse justify it.

## E. Lifecycle and forgetting

### Q-LIFE-001 — When should a semantic projection split?
**Status:** OPEN

### Q-LIFE-002 — When should projections merge?
**Status:** OPEN

### Q-LIFE-003 — What does deletion mean?
**Status:** OPEN

### Q-LIFE-004 — Should knowledge decay or require reaffirmation?
**Status:** OPEN

These remain post-Alpha unless natural use makes one a concrete blocker.

## F. Provenance and trust

### Q-PROV-001 — What is the minimum viable provenance granularity?
**Status:** **DECIDED AT LOCAL CAPABILITY FLOOR — ADR-0006**

Optional exact `[source revision, raw character span]` pointers are accepted. A global claim graph was not justified.

### Q-PROV-002 — Can derived projections become evidence for other projections?
**Status:** OPEN WITH CURRENT SAFETY BOUNDARY

Working invariant from Issue #160/E023:

> Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.

Terminal authority may be admitted RAW evidence or explicit HUMAN_KNOWLEDGE. DERIVED state may help compilation/navigation but does not become terminal authority merely because it persists.

### Q-PROV-003 — Should model/prompt/generation metadata be durable?
**Status:** OPEN

### Q-PROV-004 — How should unsupported derived claims be detected or prevented?
**Status:** **EXPERIMENTING — E023**

E023 Q001 demonstrates a concrete unsupported semantic upgrade even when the final answer happens to be true. First test consequence-sensitive retrieval/uncertainty before adding a general verifier stack.

### Q-PROV-005 — How should users navigate from evidence back to the original local source?
**Status:** EXPERIMENTING IN DOGFOOD

Navigation locators must remain separate from evidence identity/trust. Continue validating the 0.1.16 user path naturally.

## G. Retrieval and answering

### Q-RET-001 — What is the baseline retrieval strategy?
**Status:** **EXPERIMENTING — W0 FLOOR / E015 SHADOW / E023**

Object-level lexical BM25 remains a credible simple floor. E023's exact-query A arm still achieved 8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR across heterogeneous cross-source questions. Blind question-only planner + query rewrites + consensus RRF used twice the model calls and earned **0 semantic improvements**, so that G1a mechanism is not promoted.

### Q-RET-002 — When must an answer descend to more authoritative evidence?
**Status:** **EXPERIMENTING — NATURAL DOGFOOD + E023 G1**

If a load-bearing identity/attribution/temporal relation is not established by current context, the Agent should retrieve more or surface uncertainty rather than silently bridge it. Q001 is the current controlled failure case.

### Q-RET-003 — How should negative evidence and uncertainty be retrieved/expressed?
**Status:** **EXPERIMENTING — E023**

Q010 shows explicit negative evidence can successfully block an unsupported broad characterization. Q001 shows missing bridge evidence still needs consequence-sensitive uncertainty behavior.

### Q-RET-004 — How should retrieval failures feed maintenance?
**Status:** OPEN / DO NOT ASSUME PERSISTENCE

First diagnose missing context vs composition error. A retrieval miss is not evidence that a persistent semantic page is required.

### Q-RET-005 — How should users recover knowledge when they forgot the topic?
**Status:** EXPERIMENTING IN 0.1.16 DOGFOOD

The Agent-facing `wikiMemory` path performs global current-evidence discovery; normal users no longer need to select a topic for the primary Agent loop. Keep validating natural routing rather than reopening the old manual topic ritual.

### Q-RET-006 — How should cross-source semantic recovery work before persistence?
**Status:** **EXPERIMENTING — E023 G1**

G1a is complete and **NOT_EARNED**: blind query expansion + RRF + top-5 did not outperform exact-query top-5. Zero-model posthoc shows C's four missing required sources all landed at fused rank 6, so selection/evidence budget remains a live simpler explanation.

Next candidate, only after separate preregistration: **iterative evidence-follow retrieval** — initial search, inspect bounded hits/snippets, identify the missing relation, targeted follow-up search, then compose under a bounded evidence budget.

## H. Human review and automation

### Q-HUM-001 — Which operations can be autonomous?
**Status:** OPEN WITH 0.1.16 FLOOR

Read/retrieval and reversible DERIVED maintenance may be autonomous inside granted scope. Canonical epistemic mutation remains human-controlled.

### Q-HUM-002 — What review workflow is sustainable?
**Status:** EXPERIMENTING IN NATURAL DOGFOOD

0.1.16 reduced routine notification noise while preserving real authority boundaries. Continue observing popup/soft-guard fatigue naturally.

### Q-HUM-003 — How should corrections become durable system learning?
**Status:** OPEN

## I. Evaluation

### Q-EVAL-001 — What does “better Wiki” mean operationally?
**Status:** **EXPERIMENTING — E010/E013/E015/E023 + NATURAL DOGFOOD**

No single answer score is sufficient. E023 adds explicit separation of retrieval recall, semantic correctness, attribution/identity errors, epistemic upgrades, model-call cost, and posthoc selection behavior.

### Q-EVAL-002 — What corpus best approximates personal use?
**Status:** EXPERIMENTING

Use both natural private dogfood and controlled heterogeneous corpora. E023 exists because developer-project dogfood structurally favors developer-shaped `source-note-v0` and can hide a generality problem.

### Q-EVAL-003 — How do we measure maintenance debt?
**Status:** OPEN

### Q-EVAL-004 — How do we measure long-horizon contamination?
**Status:** MECHANISM EVIDENCE COMPLETE / POLICY OPEN

E007 established important mechanisms. New work should be triggered by a concrete persistent-derived decision or natural failure.

### Q-EVAL-005 — How do we measure compilation loss separately from hallucination?
**Status:** OPEN / PARKED UNTIL PERSISTENCE EARNS USE

### Q-EVAL-006 — How should persistent derived edits be downstream-regression tested?
**Status:** OPEN / PARKED UNTIL PERSISTENCE EARNS USE

## J. VS Code + GitHub Copilot integration

### Q-UX-001 — What interaction surface should the user actually use daily?
**Status:** **EXPERIMENTING — DOGFOOD 0.1.16**

Primary surface is ordinary Agent conversation. The extension exposes a small lifecycle/configuration surface, not the old command-driven storage-console mental model.

### Q-UX-002 — What instructions should be global vs task-specific?
**Status:** OPEN

### Q-UX-003 — When would MCP/dedicated retrieval service be justified?
**Status:** OPEN / NOT JUSTIFIED NOW

### Q-UX-004 — What is the acceptable lifecycle cost of Wiki automation?
**Status:** EXPERIMENTING — E013 + 0.1.16 DOGFOOD

Internal model calls are countable; token/AI-credit visibility remains incomplete. Do not optimize a persistent maintenance system before persistent semantic value is established.

### Q-UX-005 — What events should trigger expensive maintenance?
**Status:** OPEN / PERSISTENCE-DEPENDENT

### Q-UX-006 — Should VS Code-native Copilot LM APIs replace the current CLI transport?
**Status:** OPEN / NOT ON CORE CRITICAL PATH

Dogfood currently uses exact-Luna Copilot CLI with runtime capability probing. A transport change needs independent reliability/privacy/model-identity value; do not conflate it with semantic architecture.

### Q-UX-007 — How should product feedback be captured naturally?
**Status:** EXPERIMENTING — 0.1.16 / Issue #141

Native Issue Reporter exists for bounded diagnostics; natural product observations continue in Issue #141.

### Q-UX-008 — What is the minimum backup/restore story for valuable local knowledge?
**Status:** EXPERIMENTING / OPERATING-SAFETY FOLLOW-UP

Fail-closed integrity is not recovery. Keep the local backup/restore story aligned with `docs/11-local-backup-restore.md` and natural use.

## K. Cross-cutting system questions

### Q-SYS-001 — Should the Wiki ever become an irreversible compression boundary?
**Status:** **EXPERIMENTING — E013 + E023**

Current answer remains no. RAW/HUMAN authority remains recoverable; DERIVED projections are noncanonical. E023 explicitly requires persistence to earn itself only after a strong ephemeral path exists.

### Q-SYS-002 — Should knowledge maintenance be evaluated like software maintenance?
**Status:** OPEN

### Q-SYS-003 — How should one-off failures become durable system learning?
**Status:** **EXPERIMENTING — E023 / DOGFOOD**

E023 Q001 has already become an explicit trust failure class and design gate rather than a one-off prompt fix. Continue this pattern for natural failures.

## Current critical path

Two tracks run in parallel and must not be confused.

### Product evidence

1. Continue **natural installed Dogfood 0.1.16** across real sessions (Issue #141). Do not manufacture workload.
2. Observe long-horizon recall, Agent routing/source follow-through, popup/soft-guard friction, causal errors, and hidden maintenance usage.

### Core architecture evidence

1. E023 G1a is complete: blind planner/RRF is **NOT_EARNED** and G2 persistence remains unearned.
2. Use the frozen E023 artifact for **zero-model** evidence-budget/selection analysis first.
3. If another semantic gate is justified, preregister a narrow **G1b iterative evidence-follow retrieval** experiment before any calls.
4. Only after a strong G1 path exists may a separate G2 compare ephemeral vs fixed-target persistent projection.
5. G3 automatic identity/routing comes only after persistence itself earns value.

Do not reopen graph/entity/vector/ontology infrastructure merely because the semantic generality question is active.
