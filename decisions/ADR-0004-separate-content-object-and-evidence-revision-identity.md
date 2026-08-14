# ADR-0004 — Separate immutable content-object identity from evidence/source-revision identity

Status: **Accepted**

Date: 2026-08-14

## Context

ADR-0003 established append-only, topic-scoped source lineage and a current/history projection over immutable raw evidence. Its largest remaining limitation was structural: `source_id` was derived from the content SHA-256.

That conflated two different facts:

1. **these bytes are identical**, and
2. **this is the same evidence/provenance record**.

Those are not equivalent.

Two independent documents may contain identical bytes. Conversely, the same logical source may change bytes over time. A copied/echoed document may be byte-identical to its upstream source without providing independent corroboration. A legitimate revision may later return to exactly the same bytes (`A -> B -> A`) while still being a new evidence occurrence.

If content hash remains the provenance identity, the core cannot represent these distinctions cleanly.

## Decision

### 1. Immutable content objects remain SHA-256 addressed

Raw bytes continue to be stored once under their full SHA-256.

New records expose:

```text
object_id = obj-<full sha256>
```

`object_id` means only byte identity. It is not a statement about source ownership, independence, truth, or temporal status.

### 2. `source_id` becomes an opaque evidence-revision identity

New source records use an opaque UUID-backed `source_id`.

A source record points to one immutable content object and is the identity used for:

- citation,
- direct provenance lookup,
- current/history membership,
- explicit supersession.

The source record's content identity and optional origin identity are immutable after creation. Repeated observations may reuse the same current source record but may not rewrite its identity metadata.

### 3. Origin identity is optional and caller-asserted

A caller may provide an opaque `origin_id` when it can safely assert that evidence records belong to the same logical source/origin.

The core does **not** derive origin identity from:

- filename,
- absolute/local path,
- content similarity,
- document text,
- timestamps,
- an LLM.

CLI `origin_id` values are restricted to opaque ASCII tokens. Raw paths/usernames are not an accepted origin-ID format.

An `origin_id` is still only an asserted identity link. Different origin IDs do not prove statistical or editorial independence; copied/echoed sources remain possible.

### 4. Anonymous/no-origin evidence is conservative

When no origin identity is asserted:

- repeated identical current evidence is idempotent rather than becoming extra apparent corroboration;
- a previously superseded anonymous identity is not silently reactivated by plain re-ingest;
- intentional reversion requires explicit supersession.

The absence of origin information never authorizes the system to claim independent provenance.

### 5. Same-origin ambiguity is preserved until explicitly resolved

If the same origin supplies changed bytes without an explicit supersession relation, both source revisions remain current.

The core does not infer which one replaces the other.

If lineage is learned later and the intended successor source revision is already current, the core reuses that existing successor and appends only the missing supersession relationship rather than inventing a duplicate source revision.

### 6. Reversion creates a new source revision while reusing the raw object

For a deliberate `A -> B -> A` transition:

- first A: source revision `S1` -> object A,
- B: source revision `S2` -> object B,
- second A: source revision `S3` -> object A.

Thus there are three evidence revisions but only two raw content objects.

This removes the content-ID recurrence problem that motivated ADR-0003's compatibility reactivation mechanism for legacy records.

### 7. Backward compatibility is read-old / write-new

Existing manifests are not destructively rewritten.

Legacy ingest records without `object_id`/new record schema are interpreted as:

```text
object_id = obj-<legacy sha256>
source_id = existing legacy source_id
origin_id = unknown
```

Old content-derived source IDs remain resolvable and may participate in new supersession histories. New writes use the v1 source-record schema and opaque source IDs.

A destructive migration is explicitly avoided because silently changing historical citation identities would be worse than carrying compatibility logic.

### 8. Retrieval ranks unique content objects, not evidence-record count

BM25 corpus units are unique current `object_id`s.

If multiple active source records point to identical bytes:

- the text is ranked once,
- it occupies one top-k slot,
- the hit retains all active `source_id`s for provenance.

This prevents duplicated/copied evidence from changing lexical document frequency or appearing more relevant merely because it has more provenance records.

### 9. Provenance multiplicity is not corroboration weight

No reliability or corroboration bonus is assigned from source-record count or origin count in this ADR.

The model-answer prompt explicitly states that multiple source IDs attached to one evidence object represent identical bytes and must not be counted as independent corroboration or additional semantic support.

Any future corroboration model must separately test source ownership, copying/echo relations, and independence assumptions.

## Rejected alternatives

### Keep content hash as `source_id`

Rejected because byte identity and provenance identity are semantically different and legitimate same-byte recurrence becomes awkward.

### Every ingest creates a new provenance record unconditionally

Rejected as the default because accidental duplicate ingestion would manufacture apparent evidence multiplicity and create retrieval clutter.

### Filename/path as source identity

Rejected because moves, renames, mirrors, different machines, and privacy boundaries make path identity unreliable. Hashing a path does not make the underlying identity assumption true.

### Deterministic `source_id = hash(origin + content)`

Rejected because a later return to identical content from the same origin would reuse the same source-revision identity, reintroducing `A -> B -> A` recurrence problems.

### Automatic source-independence/corroboration weighting

Rejected. Distinct provenance records or origin IDs do not prove independence.

### Destructive manifest migration

Rejected because old citations and historical auditability must remain stable.

## Consequences

Positive:

- identical bytes from explicitly different origins can remain distinct provenance records while sharing one raw object;
- changed bytes no longer force provenance identity to equal content identity;
- reversion is naturally represented as a new evidence revision;
- duplicate provenance cannot inflate lexical relevance;
- legacy citations remain resolvable;
- no LLM, graph database, vector database, verifier, or compiled layer is required.

Costs/limitations:

- new source IDs are intentionally opaque and are not deterministic across independently rebuilt stores;
- `origin_id` is optional/caller-asserted and is not proof of independence or authorship;
- source revisions are currently records in an ingest/topic context rather than a fully normalized global external-source registry; the same asserted origin may therefore have different source IDs across topic contexts;
- identical anonymous evidence from genuinely independent origins cannot be recognized as independent unless the caller supplies distinct origin IDs;
- no provenance-quality weighting, copy/echo detection, claim-level ownership verification, or source trust scoring exists yet.

These limitations are preferable to false certainty.

## Relationship to other work

- **ADR-0003 / E003:** current/history source lineage remains topic-scoped. E003 still owns correction vs change-over-time vs disagreement and valid-time semantics.
- **E004:** claim-to-source ownership and risk-adaptive provenance remain separate research questions. This ADR only provides safer source identities underneath them.
- **E013:** realistic workload sessionization, authoritative-update boundaries, and sanitized aggregate export remain unchanged.
- **Persistent compilation:** still disabled. Better provenance substrate is not evidence that a compiled Wiki layer has earned activation.
