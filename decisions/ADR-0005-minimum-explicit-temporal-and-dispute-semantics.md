# ADR-0005 — Minimum explicit temporal and dispute semantics

Status: **Accepted**

Date: 2026-08-14

## Context

ADR-0003 established append-only, topic-scoped source lineage and a current/history projection. ADR-0004 separated immutable content identity from evidence-revision identity.

That floor still left a serious ambiguity: a generic replacement `A -> B` can say that A is no longer current, but it cannot distinguish whether:

- A was simply replaced for an unspecified reason;
- A was erroneous and B corrects it;
- A was valid before an explicit change-over-time and B became valid later;
- A and B are both current evidence that disagree, with no justified winner.

Collapsing those cases would make a future Wiki either lose audit meaning or manufacture temporal/epistemic certainty that the evidence does not contain.

E003 preregistered a 20-check deterministic gate for the smallest explicit semantics that could resolve this ambiguity while preserving the existing raw-first architecture. The implementation passed all 20 checks, including existing E013/E015 and VS Code consumer regressions. See `experiments/E003-temporal-semantics/results-v0.md`.

## Decision

Adopt a **small, caller-explicit, topic-scoped temporal/epistemic relation layer** over the existing append-only evidence history.

### 1. Generic replacement remains backward-compatible

A `supersede` event without `relation_kind` is interpreted as `generic`.

Generic means only:

- predecessor leaves the topic-current set;
- successor remains current;
- predecessor remains historically/audit resolvable.

It deliberately makes **no claim** that the predecessor was wrong or that it was formerly valid.

### 2. Correction is an explicit epistemic assertion

`relation_kind = correction` means the caller explicitly asserts that the predecessor evidence revision was erroneous and that the successor corrects it.

Correction:

- removes predecessor from current membership;
- keeps raw/source history resolvable;
- does not attach `effective_at` or imply a formerly-valid interval.

### 3. Change is an explicit valid-time assertion with a separate recording clock

`relation_kind = change` requires a timezone-aware `effective_at`.

The event preserves two distinct clocks:

- `effective_at`: when the represented state is asserted to have changed;
- `recorded_at`: when this relation was appended to the Wiki history.

V1 accepts only non-future effective instants and normalizes them to UTC. Scheduled future transitions are out of scope.

This metadata does **not** create a general as-of query engine. It preserves the minimum information needed so a future as-of capability can be evaluated without reconstructing lost temporal meaning.

### 4. Disagreement is a symmetric relation between specific current evidence revisions

A topic-scoped `dispute` event links two distinct current source revisions.

While active:

- both sources remain current;
- neither is selected as winner;
- both project `contested=true`;
- each lists the other in `disputes_with`.

A dispute belongs to a **specific revision pair**, not an inferred enduring claim identity. If either endpoint is later replaced, that pair ceases to be an active current dispute. The successor does not inherit conflict automatically; continued disagreement requires another explicit assertion.

V1 does not add a standalone dispute-retraction event.

### 5. Relation semantics are never inferred

The core must not infer `generic`, `correction`, `change`, or `dispute` from:

- text similarity or contradiction;
- file/path/name;
- origin identity;
- timestamps alone;
- retrieval ranking;
- an LLM or another model.

These are explicit semantic assertions supplied by a caller or future reviewed workflow.

### 6. Raw/source identity and membership remain authoritative floors

This ADR does not replace ADR-0003/0004.

- raw bytes remain immutable/content-addressed;
- evidence revisions remain opaque source identities;
- append-only topic history remains the durable event record;
- the existing store/current-history projection remains the coarse membership authority;
- temporal projection enriches **why** a source left current membership or whether current evidence is contested.

No relation operation deletes or rewrites historical raw evidence.

### 7. Retry and conflict handling are fail-closed

Exact typed replacement retries are idempotent only while the recorded successor remains current.

Once a replacement is recorded, attempts to reinterpret the same predecessor with a different:

- successor;
- relation kind; or
- effective time

must fail rather than retroactively relabel history.

Invalid, naive, missing, or future change times fail before relation append. Invalid dispute endpoints also fail before append.

### 8. Contest state reaches the answer boundary without changing retrieval ranking

For topic-scoped rendered context, temporal/contest metadata is added **after retrieval**.

Therefore asserting a dispute must not alter:

- BM25 scores;
- object ranking;
- object deduplication;
- provenance multiplicity semantics.

If an evidence object includes a currently contested provenance record, rendered context explicitly marks the unresolved contest.

The answer prompt must treat `epistemic_status: contested` as unresolved disagreement and must not manufacture consensus, silently choose a winner, or collapse competing evidence into a single canonical fact solely to provide one answer.

Unscoped retrieval/context continues to make no topic-current or dispute-state claim.

## Evidence for acceptance

E003 v0 passed all 20 preregistered deterministic checks.

Latest pre-ADR implementation evidence:

- Python tests: 62/62 PASS;
- E013 workload-calibration regressions: PASS;
- E015 privacy-minimal retrieval-shadow regressions: PASS;
- frozen E014/E014-R1 retrieval regressions: PASS;
- CLI smoke: PASS;
- VS Code development Extension Host: 4/4 PASS;
- bundled core and packaged VSIX Extension Host: 4/4 PASS;
- compiled provider remains disabled;
- model calls / AI credits: 0.

This is a correctness/mechanism evidence grade, not realistic-workload validation of human relation labeling.

## Consequences

### Positive

- Current/history membership no longer conflates correction with real-world change.
- The system can preserve a minimal valid-time statement without adopting a bitemporal database.
- Explicit unresolved disagreement can remain visible instead of being forced into a winner.
- Historical citations and recurrence remain compatible with immutable evidence identity.
- Retrieval behavior remains separable from temporal annotation.

### Costs and limitations

- Correct semantics depend on explicit caller assertions; the core does not know automatically whether an update is a correction or a change.
- `change` stores a single effective instant, not intervals or interval algebra.
- There is no general `as_of` retrieval API.
- There is no future scheduling.
- Dispute is revision-pair scoped and has no standalone retraction event in v1.
- There is no claim/entity resolution, so two documents that disagree about the same conceptual claim are not automatically linked.

These limitations are intentional. They are preferable to adding unearned temporal/claim complexity.

## Alternatives rejected

### Keep only generic supersession

Rejected as the long-term semantic floor because it cannot distinguish error correction, true state transition, and unresolved disagreement. It remains supported for backward compatibility and cases where the caller does not know more.

### Infer correction/change/disagreement automatically

Rejected. Incorrect inference at this boundary would contaminate current truth and history semantics. Any future classifier must be separately evaluated and must not silently mutate canonical relation state.

### Adopt a full bitemporal database now

Rejected as premature. E003 only demonstrated the need for separate valid and recorded instants on explicit change relations, not a full bitemporal query engine or interval algebra.

### Pick a winner whenever evidence disagrees

Rejected. That would manufacture consensus and hide unresolved evidence conflict.

### Build a claim graph now

Rejected as unearned complexity. Claim-level ownership and provenance are a separate E004 question and must be justified by a smaller evidence/maintenance gate first.

## Follow-up boundary

E003 passing does not authorize more temporal machinery by default.

The next core research should test the smallest useful **claim-to-provenance ownership** representation. Only if document/object-level provenance demonstrably fails important audit tasks should span/claim-level state be added, and any such state must preserve the raw/source/temporal floors established by ADR-0003 through ADR-0005.
