# Design Question Register

This is the **current** register of architecture/product questions. Keep it concise and update statuses as accepted ADRs or active evidence gates change. Historical wording and abandoned candidate detail remain available in Git history, experiment artifacts, issues, and ADRs.

A question becomes `DECIDED` only when an accepted ADR actually resolves the policy. Experiment results can narrow a question without silently becoming policy.

## Status vocabulary

- `OPEN` — unresolved and not on the active critical path.
- `RESEARCHING` — active prior-art/implementation review.
- `EXPERIMENTING` — an active evidence gate or real dogfood observation is deciding the next move.
- `DECIDED` — resolved by an accepted ADR.
- `REOPENED` — an accepted decision is under explicit reconsideration.

## A. Ingestion and selection

### Q-INGEST-001 — What should be eligible for durable ingestion?
**Status:** OPEN

We still need real-use evidence for the right capture threshold. Over-capture creates retrieval/maintenance debt; under-capture recreates rediscovery work.

### Q-INGEST-002 — Should raw sources be immutable?
**Status:** **DECIDED — ADR-0004 / ADR-0007**

Immutable SHA-addressed raw content is the authority floor. Evidence revisions are separate opaque identities; semantic reads verify the declared raw identity before use.

### Q-INGEST-003 — Should new information update the Wiki immediately or enter staging?
**Status:** OPEN

Raw evidence is appended immediately. The unresolved part is derived/compiled maintenance. Persistent compilation stays disabled until E013 demonstrates a realistic high-reuse region.

### Q-INGEST-004 — How should conversations and personal thoughts enter the system?
**Status:** OPEN

They need an explicit epistemic treatment rather than silently masquerading as external evidence.

## B. Knowledge representation

### Q-REP-001 — What is the canonical knowledge unit?
**Status:** EXPERIMENTING

The Alpha authority floor is decided enough for use: immutable content object + evidence revision + topic history. A persistent derived Wiki unit remains data-gated by E013 rather than assumed necessary.

### Q-REP-002 — Should fact, interpretation, hypothesis, preference, and decision use separate structures?
**Status:** OPEN

Do not add schema until real use shows the minimum distinctions that materially improve trust or retrieval.

### Q-REP-003 — How much structure belongs in metadata vs prose?
**Status:** OPEN

Current core metadata is deliberately narrow. Additional structure needs observed value and maintenance evidence.

### Q-REP-004 — What is the optimal document/retrieval granularity?
**Status:** EXPERIMENTING — E015

W0 whole-object lexical retrieval remains visible/default. E014-R1's structural rank-then-expand mechanism survives controlled testing but remains shadow-only until realistic divergent cases justify any change.

## C. Classification and schema

### Q-SCHEMA-001 — How much hierarchy should exist initially?
**Status:** OPEN

### Q-SCHEMA-002 — Who may create a new category/page type?
**Status:** OPEN

### Q-SCHEMA-003 — How should taxonomy rename/split/merge/migration work?
**Status:** OPEN

### Q-SCHEMA-004 — How should entities and aliases be resolved?
**Status:** OPEN

These are deliberately parked until real dogfood demonstrates that the current topic/file model is causing material retrieval or maintenance failures.

## D. Update, contradiction, and time

### Q-UPD-001 — How should replacement, correction, change, and disagreement differ?
**Status:** **DECIDED — ADR-0005**

Generic replacement, explicit correction, change with separate `effective_at`/`recorded_at`, and symmetric unresolved dispute are distinct caller-explicit semantics. No winner or relation type is inferred by the LLM.

### Q-UPD-002 — Do we need temporal metadata as a first-class concept?
**Status:** **DECIDED AT MINIMUM FLOOR — ADR-0005**

The accepted floor preserves `effective_at` and `recorded_at` for explicit change. Full bitemporal/as-of machinery remains unearned.

### Q-UPD-003 — How should unresolved contradictions be represented?
**Status:** **DECIDED AT MINIMUM FLOOR — ADR-0005**

Two current evidence revisions may be explicitly disputed while both remain current; answer context must preserve the unresolved disagreement.

### Q-UPD-004 — What triggers reconsolidation of a derived page?
**Status:** OPEN / E013-DEPENDENT

Do not design recurring compiled maintenance until a durable compiled provider earns existence in realistic use.

## E. Lifecycle and forgetting

### Q-LIFE-001 — When should a page split?
**Status:** OPEN

### Q-LIFE-002 — When should pages merge?
**Status:** OPEN

### Q-LIFE-003 — What does deletion mean?
**Status:** OPEN

### Q-LIFE-004 — Should knowledge decay or require reaffirmation?
**Status:** OPEN

These are post-Alpha unless observed dogfood friction makes one a concrete blocker.

## F. Provenance and trust

### Q-PROV-001 — What is the minimum viable provenance granularity?
**Status:** **DECIDED AT LOCAL CAPABILITY FLOOR — ADR-0006**

Optional exact `[source revision, raw character span]` pointers are accepted. A global claim graph and selective dual-bookkeeping policy were not justified.

### Q-PROV-002 — Can derived Wiki pages be evidence for other Wiki pages?
**Status:** OPEN WITH CURRENT SAFETY BOUNDARY

Generated answers and derived text do not become canonical evidence automatically. Persistent compiled state remains disabled; any future derived layer must preserve raw fallback/authority unless separately justified.

### Q-PROV-003 — Should model/prompt/generation metadata be durable?
**Status:** OPEN

### Q-PROV-004 — How should unsupported derived claims be detected?
**Status:** OPEN / PARKED

Verifier stacks and compilation-loss repair remain candidates only if a compiled layer is activated and real failures demand them.

### Q-PROV-005 — How should a customer navigate from immutable evidence back to the original local source?
**Status:** **EXPERIMENTING — E010 PRODUCT BLOCKER**

E010 self-dogfood found 22 duplicate-basename groups while current ingest preserves no original relative workspace path. A safe local navigation locator is needed, but it must remain separate from evidence identity, trust, and corroboration.

## G. Retrieval and answering

### Q-RET-001 — What is the baseline retrieval strategy?
**Status:** EXPERIMENTING — W0 DEFAULT / E015 SHADOW

Object-level lexical BM25 is the current floor. E010 full-repo self-dogfood achieved 12/12 target top-5 hits and MRR 0.753, supporting W0 as a credible Alpha floor. This is not proof that W0 is the final universal policy.

### Q-RET-002 — When must an answer descend to primary evidence?
**Status:** EXPERIMENTING IN DOGFOOD

E013 provenance-follow behavior and real-use failures should determine how much automatic escalation is justified.

### Q-RET-003 — How should negative evidence and uncertainty be retrieved?
**Status:** OPEN

### Q-RET-004 — How should retrieval failures feed maintenance?
**Status:** OPEN

### Q-RET-005 — How should users recover knowledge when they forgot the topic?
**Status:** **EXPERIMENTING — E010 PRODUCT BLOCKER**

Current VS Code search requires a selected topic. The fix must search topic-current views safely; do not solve this by feeding unscoped all-history evidence into model-backed Ask.

## H. Human review and automation

### Q-HUM-001 — Which operations can be autonomous?
**Status:** OPEN WITH CURRENT FLOOR

Read/query operations are safe; canonical semantic relations remain explicit. Autonomous canonical mutation is not justified.

### Q-HUM-002 — What review workflow is sustainable?
**Status:** EXPERIMENTING IN E010 REAL USE

### Q-HUM-003 — How should corrections become durable system learning?
**Status:** OPEN

## I. Evaluation

### Q-EVAL-001 — What does “better Wiki” mean operationally?
**Status:** **EXPERIMENTING — E010 + E013 + E015**

Core correctness is no longer the whole question. Current evaluation combines: customer-like VS Code usefulness (E010), realistic reuse/query economics (E013), and realistic retrieval divergence (E015).

### Q-EVAL-002 — What corpus best approximates personal use?
**Status:** EXPERIMENTING

Controlled corpora remain useful for mechanisms; E010 adds the actual project repository as a self-hosting realistic corpus. Repeated private real-life dogfood is still required.

### Q-EVAL-003 — How do we measure maintenance debt?
**Status:** OPEN

### Q-EVAL-004 — How do we measure long-horizon contamination?
**Status:** MECHANISM EVIDENCE COMPLETE / POLICY OPEN

E007 established important failure mechanisms. Additional work should be triggered by a concrete derived/compiled product decision, not repeated by default.

### Q-EVAL-005 — How do we measure compilation loss separately from hallucination?
**Status:** OPEN / PARKED UNTIL COMPILED STATE EARNS USE

### Q-EVAL-006 — How should derived Wiki edits be downstream-regression tested?
**Status:** OPEN / PARKED UNTIL COMPILED STATE EARNS USE

## J. VS Code + GitHub Copilot integration

### Q-UX-001 — What interaction surface should the user actually use daily?
**Status:** **EXPERIMENTING — E010**

The current command-driven VS Code shell is useful enough to dogfood but not yet customer-ready. E010 product blockers, not speculative polish, drive the next UX changes.

### Q-UX-002 — What instructions should be global vs task-specific?
**Status:** OPEN

### Q-UX-003 — When would MCP/dedicated retrieval service be justified?
**Status:** OPEN / NOT JUSTIFIED NOW

### Q-UX-004 — What is the acceptable lifecycle cost of Wiki automation?
**Status:** **EXPERIMENTING — E013**

E011/E012 established a controlled high-reuse region; E013 now decides whether that region exists materially in natural use.

### Q-UX-005 — What events should trigger expensive maintenance?
**Status:** OPEN / E013-DEPENDENT

### Q-UX-006 — Can the VS Code-native Copilot LM API replace the CLI adapter without model ambiguity?
**Status:** **EXPERIMENTING — Issue #24**

Zero-generation discovery tooling is shipped. The remaining gate requires the user's actual VS Code/Copilot Pro session and exact `gpt-5.6-luna` metadata; no silent model substitution.

### Q-UX-007 — How should product feedback be captured naturally?
**Status:** **EXPERIMENTING — E010 PRODUCT BLOCKER**

E013 already supports fixed-code feedback, but VS Code does not expose it. Real dogfood needs a low-friction first-class path.

### Q-UX-008 — What is the minimum backup/restore story for valuable local knowledge?
**Status:** **EXPERIMENTING — E010 PRODUCT BLOCKER**

Fail-closed integrity checks are not recovery. Define a minimal safe local operating story before calling the product customer-ready.

## K. Cross-cutting system questions

### Q-SYS-001 — Should the Wiki ever become an irreversible compression boundary?
**Status:** **EXPERIMENTING — E013**

Current answer: no. Raw remains authoritative and persistent compilation is disabled. E013 decides whether any durable compiled region earns activation.

### Q-SYS-002 — Should knowledge maintenance be evaluated like software maintenance?
**Status:** OPEN

### Q-SYS-003 — How should one-off failures become durable system learning?
**Status:** OPEN

## Current critical path

1. **E010 product readiness:** fix the concrete self-dogfood blockers around source navigation, VS Code temporal operations, feedback, forgotten-topic recall, and backup/restore operating safety.
2. **Issue #24 real-session gate:** test exact Luna availability in the user's real VS Code/Copilot Pro session; if exact Luna exists, allow only the preregistered tiny smoke before an adapter decision.
3. **Repeated E010 dogfood:** use the installed Wiki across multiple real sessions; let natural E013/E015 events accumulate from actual work.
4. **E013:** decide whether any persistent compiled provider earns a narrow product region.
5. **E015:** decide whether realistic W0/X1 divergence warrants a quality trial or retrieval-default reconsideration.
6. Reopen parked schema/graph/verifier/maintenance research only when one of the above produces a concrete need.
