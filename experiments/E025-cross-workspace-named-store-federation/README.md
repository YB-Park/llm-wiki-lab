# E025 — Cross-Workspace Named-Store Federation

Status: **F0 PREREGISTRATION PREPARED / NOT EXECUTED / ZERO MODEL CALLS**

Primary issue: #202

Reviewed product baseline: `main@7348509b83202e473d3ef1925225dec39e6f5121` (`0.1.17` L0 Query Plane)

Frozen F0 evaluation contract: `f0-evaluation-contract-v0.json`

## Question

Can LLM Wiki add a local Personal Wiki Library that allows the current trusted workspace to read one explicitly named, explicitly registered external project store **without weakening current-store authority/privacy, provenance routing, Query Plane usage guards, or write isolation**?

This experiment is about **scope authority and routing**, not semantic answer quality.

E024 already earned the one-shot exact-Luna Query Plane composer. E025 F0 therefore makes **zero model calls** and does not rerun a semantic benchmark.

## Hypothesis

A named external project store can be resolved deterministically before retrieval, read through the existing authority-preserving memory seam, and represented with scope-qualified provenance while all writes remain current-store-only.

If this hypothesis fails, cross-workspace federation is not ready for product implementation even if the user value proposition remains attractive.

## Architecture under test

```text
Current trusted workspace B
        │
        │ explicit named-store request
        ▼
Local Personal Wiki Library / Scope Resolver
        │
        │ pre-authorized opaque store ID only
        ▼
External project store A — READ ONLY
        │
        ▼
Store-scoped Memory Read Service
        │
        ▼
Scope-qualified evidence packet
```

F0 stops before Luna.

The later installed product path, if F0 earns promotion, is:

```text
scope-qualified evidence packet
        ▼
existing 0.1.17 exact-Luna Query Plane
        ▼
compact Wiki Brief
```

## Frozen first-slice scope

Included:

- one current store B;
- one or more locally registered external stores;
- named-store lookup only;
- user-local opaque library store IDs;
- explicit external-read/model-exposure registration;
- current-workspace library access grant;
- store-scoped read routing;
- scope-qualified terminal/provenance routing;
- scoped `wikiRead` follow-through contract;
- fail-closed unavailable/ambiguous/unauthorized behavior;
- current-store write isolation;
- zero-model deterministic tests.

Excluded:

- library-wide union search;
- ambient all-project search;
- sync/Git/cloud replication;
- cross-project writes;
- Personal store;
- persistent entity/person graph;
- vector default;
- automatic identity/alias merge;
- background indexing/maintenance;
- canonical manifest/schema migration;
- paid Luna calls;
- new semantic adjudication.

## Required permission composition

A future named-store query is authorized only when all required grants are valid:

```text
current workspace opt-in
AND current 0.1.17 Query Reasoning grant
AND current-workspace library access grant
AND requested external store registration/read-exposure grant
AND exact unambiguous logical store resolution
```

F0 specifically tests that no subset silently widens authority.

The existing 0.1.17 Query Reasoning grant is current-store-scoped and must not be reinterpreted as a cross-workspace grant.

## Identity contract

For local F0, the library catalog assigns opaque user-local IDs such as:

```text
libstore-<opaque-id>
```

The ID is not derived from path, Git remote, repository name, display label, or source ID.

Paths remain host-private routing metadata.

Portable store identity is deferred to the separate sync/portability gate.

## Scope reference contract

Current store remains:

```json
{"kind":"current_store"}
```

External local store is conceptually:

```json
{"kind":"library_store","store_id":"libstore-..."}
```

Rules:

- unknown store ID fails closed;
- bare source ID never selects an external store;
- a scoped source resolves only within the named store;
- failure never retries the same source ID against the current store;
- filesystem paths are not model-visible terminal identity.

## F0 deterministic case matrix

All cases are required.

### F0-01 — current-store isolation

Ordinary current-store collection does not enumerate/read external stores merely because a library exists.

Expected:

- external store reads: 0;
- model calls: 0;
- current 0.1.17 behavior unchanged.

### F0-02 — unregistered external store

A filesystem path that contains a valid Wiki store but is not registered is not searchable/readable through library routing.

Expected: fail closed before evidence collection.

### F0-03 — library grant off

A registered store remains unavailable when current-workspace library access is disabled.

Expected: fail closed, no external read.

### F0-04 — named registered store

A valid registered A under a valid current-workspace library grant resolves to A and A only.

Expected: verified read candidates are labeled with A's opaque scope ref.

### F0-05 — ambiguous alias

Two registered stores share an alias.

Expected: explicit ambiguity result; no store chosen; no evidence read.

### F0-06 — unavailable root

Registered A's root is missing/unmounted.

Expected: `library_store_unavailable`-class bounded failure; B is not treated as damaged.

### F0-07 — damaged external authority

A is reachable but fails required manifest/raw integrity verification.

Expected: named A request fails closed; ordinary B memory remains usable.

### F0-08 — scoped terminal identity

External terminal evidence carries `library_store + store_id` scope.

Expected: no bare external terminal address.

### F0-09 — no cross-store source fallback

Use a source ID that exists in B but request it under A's scope.

Expected: not found/fail closed in A; never read B as fallback.

### F0-10 — scoped provenance read

A valid A scope ref + A source ID resolves verified immutable bytes from A.

Expected: returned provenance repeats A logical scope and does not expose A filesystem root by default.

### F0-11 — write isolation

With A registered/readable while B is current, exercise existing write tools/handlers.

Expected:

- source admission target: B only;
- Human Knowledge target: B only;
- lineage resolution target: B only;
- no A canonical/workflow/derived mutation.

### F0-12 — stale library grant invalidation

Enable B, create valid library access grant, disable B, then re-enable B.

Expected: old library access grant does not revive.

### F0-13 — Query Plane grant alone is insufficient

Current 0.1.17 Query Reasoning grant is valid but no library grant exists.

Expected: A remains inaccessible.

### F0-14 — library registration alone is insufficient

A is registered but current Query Reasoning/library access composition is incomplete.

Expected: no model-capable external evidence exposure path is authorized.

### F0-15 — private locator redaction

Failures, briefs, terminal refs, and normal diagnostics are inspected for A's absolute root.

Expected: host-private root absent unless an explicit local diagnostic mode separately authorizes it.

### F0-16 — no model path

All F0 tests instrument/spoof model launch points.

Expected: total model calls = 0.

### F0-17 — existing product regression gate

Run current Python tests, E020 zero-model contract, VS Code static/runtime lifecycle tests, bundle, VSIX packaging, and packaged Extension Host tests.

Expected: all remain green.

### F0-18 — no semantic gate reopening

Inspect diff/test surface.

Expected:

- no E023 G2/G3 reopening;
- no persistent semantic dossier/entity layer;
- no vector default;
- no canonical schema migration.

## Strict promotion rule

`E025_F0_NAMED_STORE_SCOPE_CONTRACT = EARNED` only if:

- all F0-01..F0-18 required assertions pass;
- model calls are exactly 0;
- no external-store write path is introduced;
- no absolute-root leak is found in normal model-visible/bounded diagnostic output;
- no current 0.1.17 regression gate fails.

Any required-case failure yields:

```text
E025_F0_NAMED_STORE_SCOPE_CONTRACT = NOT_EARNED
```

No partial promotion.

## What F0 cannot earn

Even a perfect F0 pass does **not** earn:

- library-wide search;
- ambient cross-project retrieval;
- cross-project writes;
- sync;
- Personal store;
- persistent identity infrastructure;
- semantic quality superiority over current-store Query Plane.

F0 can earn only the right to implement/test the **named-store read-only installed slice**.

## F1 after F0, if earned

F1 is installed dogfood with one real current project B and one real registered project A.

Observe:

- whether users naturally ask A-specific questions from B;
- whether cross-project recall saves rediscovery effort;
- whether project labels/applicability remain understandable;
- whether scoped provenance follow-through works;
- whether grants are comprehensible;
- whether latency/usage remains acceptable;
- whether users then naturally ask for library-wide similarity search.

Do not manufacture library-wide demand.

## Relationship to 0.1.17 dogfood

0.1.17 natural Query Plane dogfood remains active in parallel.

E025 F0 preparation must not alter the installed 0.1.17 binary or interpretation of its existing grants.

Natural 0.1.17 defects still take priority if they expose data loss, authority/privacy violations, provenance breakage, or unusable core behavior.