# ADR-0006 — Local exact raw-span provenance pointers, not a claim graph

Status: **Accepted**

Date: 2026-08-14

## Context

ADR-0003 through ADR-0005 established the authority floor:

- immutable raw content objects;
- opaque evidence-revision identities;
- topic-scoped append-only current/history lineage;
- explicit generic/correction/change/dispute semantics.

E004 then tested whether provenance finer than page/structural ownership deserves to exist before building any persistent claim graph.

E004-v0 Gate A passed all 10 preregistered checks: exact claim-to-raw-span provenance materially improved bounded audit correctness, source ownership, and inspected-character efficiency over structural provenance in the controlled mechanism corpus. Gate B failed: the tested “structural everywhere + exact on high-risk” policy became dual bookkeeping and increased both metadata and W1 update burden over universal exact precision.

Therefore the evidence supports one narrow capability, not a general claim architecture.

## Decision

Add an **optional local exact raw-span provenance record** to the core.

A record contains only:

- deterministic opaque `record_id`;
- `topic_id`;
- optional opaque `local_label`;
- raw evidence revision `source_id`;
- immutable `object_id` and SHA-256 snapshot;
- exact UTF-8 text character range `[start,end)`;
- append `recorded_at` and schema identifier.

Records live in a separate append-only `.wiki-lab/provenance.jsonl` log.

### 1. The record is a pointer, not authority

An exact provenance record answers:

> “Which exact characters of which immutable evidence revision was this local attachment intended to point to?”

It does **not** answer:

- whether the derived claim is true;
- whether the source is currently valid/current;
- whether a correction/change/dispute has been resolved;
- which of several records with the same local label is canonical;
- whether two labels represent the same conceptual claim.

Raw/source/temporal layers remain authoritative for those questions.

### 2. Historical revision identity is intentional

Resolution uses the stored `source_id`, including superseded historical revisions.

If A is later superseded/corrected/changed by B, an A provenance record continues to resolve A's exact immutable bytes. It is **not** silently remapped to B.

A caller that wants a provenance record for B must append a new explicit record.

This preserves audit history and avoids recursive provenance mutation.

### 3. Exact means exact; no fuzzy repair

Creation requires:

- an existing raw source revision in the named topic;
- `0 <= start < end <= len(raw_text)`;
- raw object SHA/object identity to match storage.

Resolution re-checks:

- source revision identity;
- object ID / SHA snapshot;
- current raw object bytes;
- span bounds;
- record identity digest.

Corruption or mismatch fails closed.

V1 performs no fuzzy relocation, semantic search, successor following, or LLM repair.

### 4. Exact retries are idempotent

`record_id` is derived deterministically from the canonical attachment identity:

`topic + local_label + source_id + object_id + sha256 + start + end`.

`recorded_at` is not part of identity. Repeating the exact attachment returns the existing record rather than appending a duplicate.

Different local labels may intentionally point to the same exact raw span. This creates multiple local attachment records but does not duplicate raw content.

### 5. Local label is deliberately weak

`local_label` is optional and restricted to an opaque ASCII token.

It is **not**:

- a global claim ID;
- a path;
- free-form claim text;
- an entity/ontology node;
- an inferred semantic key.

Multiple historical records may share a local label. The core does not infer a current winner among them.

### 6. Temporal/dispute state remains separate

Provenance records do not copy `relation_kind`, `effective_at`, `contested`, or dispute edges.

A source may later become superseded or contested without changing the provenance record. Temporal state is resolved through the E003 layer when needed.

This avoids a second stale copy of temporal truth.

### 7. Derived-only authoritative targets are rejected

V1 can bind only to a source revision known by the raw evidence store.

A derived page/artifact ID is not an authoritative target and cannot be substituted for a raw source of record.

### 8. No default product behavior changes

This capability is core-only in v1.

It does not add:

- a CLI command;
- a VS Code command/view;
- a retrieval ranking signal;
- answer prompt behavior;
- canonical mutation;
- E013/E015 telemetry content.

Binding a provenance pointer must not change default retrieval results.

## Evidence for acceptance

Implementation issue: #45  
Implementation PR: #46

Latest pre-ADR implementation head with the same core bytes plus Unicode regression:

- Python unit tests: **74/74 PASS**;
- exact resolution/retry/multi-label/invalid-target tests: PASS;
- A→B historical resolution / no-auto-follow: PASS;
- correction/change/dispute independence: PASS;
- raw object and provenance-log tamper fail-closed: PASS;
- Korean/Unicode character-span round trip: PASS;
- E013 sanitized-export provenance privacy: PASS;
- default retrieval invariance: PASS;
- E013/E015 existing regressions: PASS;
- frozen E004/E014/E014-R1 validations: PASS;
- CLI smoke: PASS;
- VS Code development Extension Host: PASS;
- bundled Python core: PASS;
- packaged VSIX Extension Host: PASS;
- compiled provider remains disabled;
- model calls / AI credits: **0 / 0**.

The E004 prescore workflow also received a post-merge CI-scope repair: its “evidence branch must not mutate core” guard now runs only for the original E004 evidence branch. Frozen E004 corpus/auditor/scorer/validator hashes were not changed.

## Consequences

### Positive

- Exact provenance can be represented without introducing a claim graph.
- Historical evidence remains auditable after supersession/correction/change.
- Pointer corruption is detectable before use.
- Raw/source/temporal authority remains single-sourced rather than copied into a provenance layer.
- The capability can later support realistic provenance audit tests without changing user-facing behavior now.

### Costs / limitations

- Exact provenance adds metadata and potential rewrite/reattachment burden, as E004 D1 explicitly demonstrated.
- V1 has no current-attachment projection for a local label.
- V1 has no automatic relocation after a source revision or derived-page rewrite.
- V1 has no claim/entity resolution and no claim graph.
- V1 has no automatic provenance extraction or assignment.
- V1 does not evaluate whether the pointed text actually entails a derived claim.
- The append log follows the project's existing simple local-file concurrency model; this ADR does not introduce multi-writer locking/transactions.

These are deliberate boundaries, not missing invitations to add complexity immediately.

## Alternatives rejected

### Build a global claim graph now

Rejected. E004 demonstrated value for exact local ownership, not for global claim identity, entity resolution, graph traversal, or graph maintenance.

### Implement P3 selective dual bookkeeping

Rejected by E004 Gate B. The tested policy increased metadata and W1 update actions relative to P2 while merely matching P2 on its high-risk subset.

### Auto-follow current successor

Rejected. It would rewrite historical ownership semantics and could turn a formerly correct citation into a silently different assertion.

### Fuzzy/LLM span repair

Rejected until separately evaluated. A wrong automatic repair at this boundary could make provenance look precise while pointing at the wrong evidence.

### Store temporal/dispute state inside provenance records

Rejected as duplicate mutable truth that would become stale independently of ADR-0005's temporal projection.

## Follow-up boundary

Do **not** immediately add UI or a claim graph.

The next useful evidence is realistic/shadow use of the local capability:

- when exact provenance is actually requested;
- whether it reduces verification effort in natural work;
- how often source/derived rewrites make local pointers burdensome;
- whether users need an explicit current-attachment/rebind action.

Only observed need should justify a next provenance maintenance layer.
