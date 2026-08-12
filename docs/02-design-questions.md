# Design Question Register

This is the canonical list of unresolved design questions.

A question remains open until an ADR explicitly resolves it. Research notes and experiment results may change our confidence but do not themselves constitute a decision.

## Status vocabulary

- `OPEN` — unresolved.
- `RESEARCHING` — active literature/implementation review.
- `EXPERIMENTING` — a controlled experiment is in progress.
- `DECIDED` — resolved by an ADR.
- `REOPENED` — an earlier decision is being reconsidered.

---

## A. Ingestion and selection

### Q-INGEST-001 — What should be eligible for durable ingestion?

**Status:** OPEN

Should every useful-looking source enter the system, or should the wiki enforce a threshold such as expected future reuse, novelty, personal importance, or evidentiary value?

Risks on each side:

- ingest too much -> maintenance debt and retrieval noise,
- ingest too little -> lost context and repeated rediscovery.

### Q-INGEST-002 — Should raw sources be immutable?

**Status:** OPEN

Candidate policies:

1. immutable raw source,
2. append-only versions,
3. editable source with Git history,
4. external source pointer plus local metadata.

### Q-INGEST-003 — Should new information update the wiki immediately or enter a staging area?

**Status:** OPEN

Compare immediate integration with buffered/periodic consolidation.

### Q-INGEST-004 — How should conversations and personal thoughts enter the system?

**Status:** OPEN

They are neither primary external evidence nor ordinary wiki facts. We need an explicit epistemic category and promotion rule.

---

## B. Knowledge representation

### Q-REP-001 — What is the canonical knowledge unit?

**Status:** OPEN

Candidates:

- source summary,
- topic document,
- atomic note,
- claim,
- entity page,
- event/observation,
- layered combination.

### Q-REP-002 — Should fact, interpretation, hypothesis, preference, and decision use separate structures?

**Status:** OPEN

The objective is to avoid derived interpretation silently acquiring the status of sourced fact without creating excessive authoring overhead.

### Q-REP-003 — How much structure belongs in frontmatter vs prose?

**Status:** OPEN

Potential metadata includes source IDs, dates, lifecycle state, aliases, confidence, validity interval, review date, and relationships.

### Q-REP-004 — What is the optimal document granularity?

**Status:** OPEN

Need criteria based on semantic cohesion, retrieval quality, edit locality, and maintenance cost rather than arbitrary token count alone.

---

## C. Classification and schema

### Q-SCHEMA-001 — How much hierarchy should exist initially?

**Status:** OPEN

Flat/tag-first, shallow folders, deep taxonomy, dynamic maps-of-content, or hybrid.

### Q-SCHEMA-002 — Who is allowed to create a new category or page type?

**Status:** OPEN

Possible controls range from autonomous creation to proposal/review thresholds.

### Q-SCHEMA-003 — How should taxonomy evolution be performed?

**Status:** OPEN

Need explicit semantics for rename, redirect, split, merge, re-parent, and migration.

### Q-SCHEMA-004 — How do we resolve entities and aliases?

**Status:** OPEN

Duplicate entity creation can fragment evidence and retrieval.

---

## D. Update, contradiction, and time

### Q-UPD-001 — When should new information overwrite old information?

**Status:** OPEN

We must distinguish:

- correction of an error,
- temporal change,
- conflicting evidence,
- changed personal belief/preference,
- refinement with added detail.

### Q-UPD-002 — Do we need temporal metadata as a first-class concept?

**Status:** OPEN

Candidate fields: `observed_at`, `valid_from`, `valid_to`, `supersedes`.

### Q-UPD-003 — How should unresolved contradictions be represented?

**Status:** OPEN

The system should not manufacture consensus simply to keep one canonical sentence.

### Q-UPD-004 — What triggers reconsolidation of an existing page?

**Status:** OPEN

Possibilities include source count, age, detected contradiction, page size, query failures, or scheduled review.

---

## E. Lifecycle and forgetting

### Q-LIFE-001 — When should a page split?

**Status:** OPEN

Candidate signals: multiple independent subtopics, repeated partial retrieval, excessive edit conflicts, token/size threshold, weak internal cohesion.

### Q-LIFE-002 — When should pages merge?

**Status:** OPEN

Need to distinguish legitimate specialization from accidental duplication.

### Q-LIFE-003 — What does deletion mean?

**Status:** OPEN

Options include hard delete, archive, tombstone, supersede, redirect, or remove only from active retrieval.

### Q-LIFE-004 — Should knowledge decay or require periodic reaffirmation?

**Status:** OPEN

Some domains change quickly; others are effectively timeless. A single stale-age threshold is unlikely to work.

---

## F. Provenance and trust

### Q-PROV-001 — What is the minimum viable provenance granularity?

**Status:** OPEN

Source-file-level attribution is cheap. Claim/span-level provenance is more precise but costly. We need evidence about the trade-off.

### Q-PROV-002 — Can derived wiki pages be used as evidence for other wiki pages?

**Status:** OPEN

This is central to recursive contamination risk. Candidate rule: derived pages can guide retrieval but cannot be sole evidence for factual promotion.

### Q-PROV-003 — Should we store model identity, prompt version, or generation metadata?

**Status:** OPEN

Useful for reproducibility and debugging, but potentially high-noise metadata.

### Q-PROV-004 — How should unsupported claims be detected?

**Status:** OPEN

Potential methods: citation checks, source entailment checks, adversarial audit, sampled human review.

---

## G. Retrieval and answering

### Q-RET-001 — What is the baseline retrieval strategy?

**Status:** OPEN

Candidates:

- filesystem/index navigation,
- lexical search,
- embeddings,
- hierarchical summaries,
- graph traversal,
- agentic mixed retrieval.

### Q-RET-002 — When must an answer descend from synthesis to primary evidence?

**Status:** OPEN

Likely query-dependent: exact values, dates, controversial statements, and high-impact decisions may require source verification.

### Q-RET-003 — How should negative evidence and uncertainty be retrieved?

**Status:** OPEN

A system optimized only for matching supporting facts can systematically miss disagreement and absence.

### Q-RET-004 — How should retrieval failures feed maintenance?

**Status:** OPEN

If information exists but cannot be found, that should generate a repair signal rather than merely a poor answer.

---

## H. Human review and automation

### Q-HUM-001 — Which operations can be autonomous?

**Status:** OPEN

Candidate risk tiers:

- additive observation: low risk,
- derived-page edit: medium risk,
- merge/split/rename: higher risk,
- deletion/source mutation: highest risk.

### Q-HUM-002 — What is the minimum review workflow that remains sustainable?

**Status:** OPEN

A perfect review policy that users bypass is worse than a lightweight policy they actually follow.

### Q-HUM-003 — How should user corrections become durable system improvements?

**Status:** OPEN

Candidate mechanisms: error book, lint rule, prompt rule, regression test, ADR amendment.

---

## I. Evaluation

### Q-EVAL-001 — What does "better wiki" mean operationally?

**Status:** OPEN

Need a multi-dimensional scorecard rather than document count or answer accuracy alone.

### Q-EVAL-002 — What benchmark corpus best approximates real personal use?

**Status:** OPEN

We need both controlled synthetic cases and realistic heterogeneous personal-knowledge workloads.

### Q-EVAL-003 — How do we measure maintenance debt?

**Status:** OPEN

Candidate signals: unresolved contradictions, duplicate pages, stale claims, orphaned pages, review backlog, mean repair effort.

### Q-EVAL-004 — How do we measure long-horizon contamination?

**Status:** OPEN

The benchmark must test repeated derive-update-retrieve cycles, not only one-shot ingestion.

---

## J. VS Code + GitHub Copilot integration

### Q-UX-001 — What interaction surface should the user actually use daily?

**Status:** OPEN

Potentially Copilot prompt files/custom agents plus ordinary file operations. The system should minimize context switching.

### Q-UX-002 — What instructions should be global vs task-specific?

**Status:** OPEN

Overly broad Copilot instructions may unintentionally influence unrelated coding work.

### Q-UX-003 — When would MCP or a dedicated retrieval service become justified?

**Status:** OPEN

It should be introduced because measured corpus scale or retrieval failure requires it, not because it is architecturally fashionable.

---

## Next action

The first research pass should prioritize the questions with the greatest irreversible-risk implications:

1. provenance / recursive contamination,
2. update and temporal semantics,
3. knowledge unit and split/merge behavior,
4. lifecycle/deletion,
5. evaluation methodology.
