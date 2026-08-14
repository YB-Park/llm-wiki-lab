# E003 — minimum temporal semantics truth-table gate

Status: **preregistered before E003 implementation**

Date: 2026-08-14

## Question

Can the existing append-only, topic-scoped source-lineage core distinguish **generic replacement, correction, change-over-time, and unresolved disagreement** without introducing inference, destructive migration, a general bitemporal query engine, or hidden consensus?

This is a deterministic correctness/mechanism gate, not a statistical benchmark.

## Existing floor that must remain true

ADR-0003/0004 remain authoritative:

- raw bytes are immutable/content-addressed;
- `source_id` is an opaque evidence-revision identity;
- topic current/history is an append-only materialized projection;
- generic supersession is explicit and topic-scoped;
- `A -> B -> A` creates a new source revision for the second A while reusing raw bytes;
- unscoped retrieval makes no current-truth claim;
- no relation is inferred from filename/path, origin, similarity, timestamps, or model output;
- existing historical citations remain resolvable;
- content/provenance multiplicity does not create corroboration weight.

## Event semantics under test

### R0 — generic supersede (backward-compatible)

Existing event form remains valid:

```json
{
  "event": "supersede",
  "topic_id": "...",
  "predecessor_source_id": "A",
  "successor_source_id": "B",
  "recorded_at": "..."
}
```

Missing `relation_kind` is interpreted as `generic`.

New generic events may explicitly write `relation_kind: "generic"`, but this must not change old histories.

Meaning: A leaves the current set and B remains current. **No assertion is made about whether A was wrong or formerly valid.**

### R1 — correction

Stored as the same replacement event with:

```json
"relation_kind": "correction"
```

Meaning: A leaves current evidence because the caller explicitly asserts that A was erroneous and B corrects it. A remains audit-resolvable, but the core must not label A as a formerly-valid historical state merely because it was once recorded.

No `effective_at` is permitted.

### R2 — change-over-time

Stored as replacement with:

```json
"relation_kind": "change",
"effective_at": "timezone-aware ISO-8601 instant normalized to UTC"
```

Meaning: the caller explicitly asserts a state transition at `effective_at`; A leaves the current set and B remains current.

`recorded_at` is the append/knowledge-recording time and is distinct from `effective_at`.

V1 constraints:

- `effective_at` is required for `change`;
- it must be timezone-aware and parseable;
- it must not be later than the relation's recording time;
- future/scheduled transitions are rejected in v1;
- generic/correction relations reject `effective_at`.

E003 does **not** implement general as-of retrieval. The relation metadata is preserved so valid-time reasoning can be added only if later justified.

### R3 — disagreement

Append a topic-scoped symmetric revision-pair event:

```json
{
  "event": "dispute",
  "topic_id": "...",
  "source_ids": ["A", "B"],
  "recorded_at": "..."
}
```

The pair is stored in deterministic lexical source-ID order.

Meaning:

- both A and B must already be current in that topic;
- both remain current;
- neither is selected as winner;
- both project `contested=true` and list the other current source in `disputes_with`;
- duplicate assertion of the same active pair is idempotent;
- self-dispute or non-current/missing endpoints fail closed.

A dispute is a relation between **specific evidence revisions**, not an inferred enduring claim group. If either endpoint later leaves current membership through any replacement relation, that revision-pair is no longer an active current dispute. Conflict is **not automatically inherited** by a successor; if it remains, a new explicit dispute assertion is required.

V1 has no independent dispute-retraction event. This is a deliberate minimum. If this limitation proves operationally unacceptable, E003 v1 fails its simplicity criterion and must be reconsidered rather than silently adding a larger conflict workflow.

## Public compatibility contract

`source_status()` keeps its existing coarse field:

```text
status = current | superseded
```

so old consumers do not misclassify a corrected/changed source as current.

It may add:

- `replacement_kind`: `generic | correction | change | null`;
- `replacement_recorded_at`;
- `effective_at` for outgoing `change`;
- `valid_from` when the source is the successor of exactly one explicit change relation;
- `contested`: boolean;
- `disputes_with`: sorted current source IDs.

`status=superseded` remains a membership statement, not a historical-truth statement. `replacement_kind` carries the epistemic/temporal reason.

## Answer-boundary contract

For topic-scoped rendered evidence context:

- if any provenance source record for an evidence object is currently contested, the context must explicitly mark the object as contested and expose the relevant current dispute source IDs;
- the answer prompt must instruct the model that contested evidence is unresolved disagreement and must not be collapsed into one canonical fact solely to produce a single answer;
- no model call is needed to detect or create dispute state.

## Deterministic truth-table scenarios

E003 v0 survives only if **all** checks pass:

1. legacy generic A->B history without `relation_kind` replays exactly as before;
2. new explicit generic A->B has identical current/history membership and retry idempotency;
3. correction A(error)->B removes A from current, keeps B current, preserves A for audit, reports `replacement_kind=correction`, and carries no valid-time field;
4. change A->B with a past timezone-aware effective instant removes A, keeps B, preserves distinct `effective_at` and later `recorded_at`, and exposes successor `valid_from`;
5. invalid/naive/future change times fail before relation append;
6. exact retry of generic/correction/change relation is idempotent;
7. attempting to relabel an already-recorded replacement (different relation kind, successor, or effective time) fails closed and does not mutate history;
8. dispute A<->B keeps both current and marks both contested with symmetric metadata;
9. duplicate active dispute is idempotent;
10. self/missing/non-current dispute endpoints fail closed;
11. replacing one disputed endpoint removes only that revision-pair from current dispute projection and does not infer dispute inheritance to its successor;
12. the same source/relation activity in topic A does not change topic B projection;
13. generic/correction/change preserve `A -> B -> A` recurrence through a new evidence revision and raw-object reuse;
14. all historical raw/citations remain resolvable after every relation kind;
15. existing E013 maintenance-cycle and E015 shadow telemetry semantics/tests remain unchanged;
16. current/default retrieval still excludes replaced sources and includes both unresolved disputed current sources;
17. topic-scoped rendered context explicitly marks disputed evidence without changing object dedupe/BM25 scoring;
18. answer prompt explicitly forbids manufacturing consensus from `contested` evidence;
19. existing generic supersession unit tests remain green without fixture rewriting;
20. VS Code dev/packaged consumer regression remains green (consumer-only check; no VS Code feature work).

Any failure => **DOES_NOT_SURVIVE_E003_V0** until the implementation bug is fixed. If satisfying the table requires a materially larger ontology/workflow than the relations above, stop and record that the proposed minimum failed the simplicity boundary.

## Relation validation / retry rules

- replacement endpoints are distinct and topic-current at first append;
- exact replay is idempotent only while the recorded successor is still current, preserving ADR-0003 stale-relation protection;
- if predecessor is already inactive and the recorded relation metadata does not exactly match the requested relation, fail with semantic conflict rather than retroactively relabeling history;
- replacement of a disputed predecessor automatically removes current dispute pairs containing that predecessor during projection fold;
- no relation operation deletes raw/source records.

## Non-goals

Not authorized by E003 v0:

- as-of/historical-time query API;
- scheduled future changes;
- interval algebra or full bitemporal database;
- automatic contradiction detection;
- LLM temporal/relation classifier;
- dispute clustering/entity resolution;
- claim-level temporal ontology;
- graph/vector storage;
- persistent compiled-Wiki activation.

## Model/cost boundary

E003 v0 is deterministic local code only: **model calls = 0, AI credits = 0**.
