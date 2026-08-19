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

Explicit user-owned decisions/beliefs/rationale belong to `HUMAN_KNOWLEDGE`, not external RAW evidence. E023 G1c-R1 confirms that downstream answers must preserve that epistemic type when it is load-bearing.

## B. Knowledge representation

### Q-REP-001 — What is the canonical knowledge unit?
**Status:** **EXPERIMENTING — E023 / Issue #160**

The current answer remains deliberately asymmetric:

- the **Authority Core** has durable evidence/history/Human Knowledge units;
- no universal semantic Wiki unit is accepted;
- `source-note-v0` is one DERIVED source-oriented projection, not the ontology;
- query-time semantic views are first-class candidates;
- semantic persistence is an optimization that must earn itself.

See `docs/14-generality-and-semantic-projections.md`.

### Q-REP-002 — Which epistemic classes require distinct authority?
**Status:** OPEN ABOVE CURRENT FLOOR / E023 COMPOSITION SIGNAL

The minimum floor distinguishes `RAW_MEMORY`, `DERIVED_MEMORY`, and `HUMAN_KNOWLEDGE`. G1c-R1 AQ003 shows that merely carrying the type in retrieval metadata is not enough if the answer later presents user-owned knowledge as an ordinary externally observed fact. Do not respond by inventing a universal fact ontology; first preserve the existing epistemic floor end to end.

### Q-REP-003 — How much structure belongs in metadata vs prose?
**Status:** OPEN / E023-GATED

Current core metadata stays narrow. Evaluation may use richer load-bearing support clauses than product storage. Do not turn evaluator structure into canonical runtime schema merely because it improves diagnosis.

### Q-REP-004 — What is the optimal document/retrieval granularity?
**Status:** EXPERIMENTING — E015 + E023 / SELECTION-BUDGET ACTIVE

W0 whole-object lexical retrieval remains the product floor. E023 now shows two distinct top-k/budget failures: a needed anchor can sit outside initial top-k, and a later semantic selector can destructively compress an already-sufficient candidate pool. The next gate is zero-model evidence-budget/selection analysis, not a new storage granularity decision.

## C. Classification, schema, and semantic identity

### Q-SCHEMA-001 — How much hierarchy should exist initially?
**Status:** OPEN

### Q-SCHEMA-002 — Who may create a new category/page/projection type?
**Status:** OPEN

### Q-SCHEMA-003 — How should taxonomy rename/split/merge/migration work?
**Status:** OPEN

### Q-SCHEMA-004 — How should semantic subjects and aliases be resolved?
**Status:** **EXPERIMENTING — E023 G1 / NO PERSISTENT IDENTITY SYSTEM**

E023 has now produced three controlled identity observations:

- G1a Q001: explicit bridge absent; Luna confidently merged aliases anyway -> CRITICAL_ERROR.
- G1b Q001: evidence-follow recovered and selected the bridge -> PASS.
- G1c-R1 AQ001: evidence-follow recovered the bridge into the candidate pool, but the final selector discarded it; Luna again confidently merged identity -> CRITICAL_ERROR.

Current consequence:

- identity/alias similarity is not authority;
- high-consequence identity claims need an explicit authoritative bridge, further retrieval, or expressed ambiguity;
- finding the bridge is insufficient if later selection drops it;
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

G1c-R1 adds an operational corollary: the authoritative anchor must survive intermediate retrieval/selection stages; an anchor found and then discarded cannot ground the final claim.

### Q-PROV-003 — Should model/prompt/generation metadata be durable?
**Status:** OPEN

### Q-PROV-004 — How should unsupported derived claims be detected or prevented?
**Status:** **EXPERIMENTING — E023 AUTHORITY-SUFFICIENCY / SELECTION**

The prospective evaluator is now frozen and exercised on separated material. It distinguishes missing authority, clean sufficiency, and sufficient-but-dangerous conflation risk.

G1c-R1 AQ001 is the key new case: the missing identity bridge was recovered into the candidate pool but discarded before composition, and the composer still made the unsupported merge. Prevention therefore cannot be framed only as “retrieve more”; authority-preserving selection and consequence-sensitive composition are separate controls to test.

### Q-PROV-005 — How should users navigate from evidence back to the original local source?
**Status:** EXPERIMENTING IN DOGFOOD

Navigation locators must remain separate from evidence identity/trust. Continue validating the 0.1.16 user path naturally.

## G. Retrieval and answering

### Q-RET-001 — What is the baseline retrieval strategy?
**Status:** **EXPERIMENTING — W0 FLOOR / E015 SHADOW / E023**

Object-level lexical BM25 remains a credible simple floor. G1a blind question-only planning/RRF added cost with zero semantic improvement. G1c-R1 shows that targeted evidence-follow can improve candidate coverage, but the current final selector is not safe enough for promotion.

### Q-RET-002 — When must an answer descend to more authoritative evidence?
**Status:** **EXPERIMENTING — NATURAL DOGFOOD + E023 G1**

If a load-bearing identity/attribution/temporal relation is not established by final context, the Agent should retrieve more or surface uncertainty rather than silently bridge it.

G1c-R1 sharpens this: AQ001's identity bridge was recovered into the candidate pool and then lost. “Descend to authority” therefore includes **preserving already-found load-bearing authority through final selection**, not just issuing another query.

### Q-RET-003 — How should negative evidence and uncertainty be retrieved/expressed?
**Status:** **EXPERIMENTING — E023**

Explicit negative evidence can block unsupported broad characterizations. Missing identity authority still requires uncertainty even when contextual similarity is strong. G1c-R1 shows the composer can remain overconfident after selection has made context insufficient.

### Q-RET-004 — How should retrieval failures feed maintenance?
**Status:** OPEN / DO NOT ASSUME PERSISTENCE

Diagnose the earliest failure stage first: initial retrieval, candidate generation, final selection, or composition. G1c-R1 is direct evidence that a final retrieval failure can be caused by **selector over-compression after successful retrieval**, not by absent persistent semantic structure.

### Q-RET-005 — How should users recover knowledge when they forgot the topic?
**Status:** EXPERIMENTING IN 0.1.16 DOGFOOD

The Agent-facing `wikiMemory` path performs global current-evidence discovery; normal users no longer need to select a topic for the primary Agent loop. Keep validating natural routing rather than reopening the old manual topic ritual.

### Q-RET-006 — How should cross-source semantic recovery work before persistence?
**Status:** **EXPERIMENTING — E023 G1 / PAID CALLS PAUSED / SELECTION-BUDGET NEXT**

Frozen progression:

- **G1a:** blind query expansion/RRF `NOT_EARNED`.
- **G1b:** final evidence-follow policy `NOT_EARNED`, but Q001 targeted trust repair showed evidence-aware follow-up can recover a missing authoritative bridge.
- **Prospective authority evaluator:** frozen before G1c semantic outputs and successfully exercised.
- **G1c v0:** `INVALID_EXECUTION`; no experiment verdict.
- **G1c-R1:** complete, 18/18 calls, zero rerolls, final selection `NOT_EARNED`.

G1c-R1 candidate pools were positive-authority complete on **6/6** questions, but final selection produced only 4/6 clean contexts. AQ001 lost a recovered identity bridge; AQ004 regressed from a clean candidate context to an insufficient single-source final context.

Therefore the next controlled G1 question is **authority-preserving selection/evidence budget**, not another retrieval query trick and not G2 persistence. Paid semantic calls remain paused until a concrete evaluator-independent selection/budget policy earns comparison in zero-model analysis.

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
**Status:** **EXPERIMENTING — E023 AUTHORITY-SUFFICIENCY + NATURAL DOGFOOD**

No single answer score or flat source-recall score is sufficient.

The prospective authority-sufficiency contract is now exercised and demonstrates useful stage separation:

- exact initial authority: 4 clean / 1 risk / 1 insufficient;
- evidence-follow candidate pools: 4 clean / 2 risk / 0 insufficient;
- final selector: 4 clean / 0 risk / 2 insufficient.

This distinguishes **candidate retrieval success from destructive final selection**. Semantic adjudication then separately identifies unsupported identity merge, HUMAN_KNOWLEDGE type omission, temporal correctness, and overcautious insufficiency.

The evaluator remains evaluation-only. Its clauses are not product storage requirements.

### Q-EVAL-002 — What corpus best approximates personal use?
**Status:** EXPERIMENTING

Use both natural private dogfood and controlled heterogeneous corpora. E023's prospective slice was intentionally separated from the original G1 outcomes so authority clauses were not reverse-engineered from model answers. Natural use remains necessary for long-horizon value.

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

Current answer remains no. RAW/HUMAN authority remains recoverable; DERIVED projections are noncanonical. G1c-R1 adds a query-time analogue: final semantic selection must not become an irreversible **epistemic compression boundary** that discards load-bearing authority already available upstream.

### Q-SYS-002 — Should knowledge maintenance be evaluated like software maintenance?
**Status:** OPEN

### Q-SYS-003 — How should one-off failures become durable system learning?
**Status:** **EXPERIMENTING — E023 / DOGFOOD**

E023 repeatedly turns trust failures into explicit gates instead of one-off prompt patches: G1a unsupported identity, G1b evidence-follow repair, prospective authority evaluation, G1c v0 execution failure discipline, and G1c-R1 selection regression. Continue this pattern for natural failures.

## Current critical path

Two tracks run in parallel and must not be confused.

### Product evidence

1. Continue **natural installed Dogfood 0.1.16** across real sessions (Issue #141). Do not manufacture workload.
2. Observe long-horizon recall, Agent routing/source follow-through, popup/soft-guard friction, causal errors, hidden maintenance usage, and real cross-source authority failures.

### Core architecture evidence

1. G1a blind planner/RRF: **NOT_EARNED**.
2. G1b final evidence-follow policy: **NOT_EARNED**; targeted identity-bridge repair observed.
3. Prospective authority-sufficiency evaluator: frozen and exercised on separated material.
4. G1c v0: **INVALID_EXECUTION**; no verdict.
5. G1c-R1: complete, final selection **NOT_EARNED**; candidate pools positive-authority complete **6/6**.
6. **Pause paid semantic calls.** Run zero-model selection/evidence-budget counterfactual analysis on frozen G1c-R1 candidate pools.
7. Only if a simple, general, evaluator-independent selection/budget rule preserves recovered authority and avoids clean-context regression should another G1 semantic comparison be preregistered.
8. Separately preserve `HUMAN_KNOWLEDGE` type in composition and test sufficiency judgment; do not conflate these with retrieval selection.
9. G2 persistent projection remains future-only after a stronger G1 path.
10. G3 automatic identity/routing remains last.

Do not reopen graph/entity/vector/ontology infrastructure merely because semantic generality remains active.
