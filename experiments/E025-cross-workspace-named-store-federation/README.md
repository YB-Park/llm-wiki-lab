# E025 — Cross-Workspace Named-Store Federation

Status: **F0 EARNED / 18 OF 18 PASS / ZERO MODEL CALLS / RUNTIME FEDERATION NOT YET IMPLEMENTED**

Primary issue: #202

Frozen baseline: `main@7f0c4045a6341a16c92e4582a92fcd99e6352fcb`

Frozen F0 evaluation contract: `f0-evaluation-contract-v0.json`

Executable zero-model preflight: `run_f0.py`

## Question

Can LLM Wiki add a local Personal Wiki Library that allows the current trusted workspace to read one explicitly named, explicitly registered external project store **without weakening current-store authority/privacy, provenance routing, Query Plane usage guards, or write isolation**?

This experiment is about **scope authority and routing**, not semantic answer quality. E024 already earned the one-shot exact-Luna Query Plane composer, so E025 F0 makes **zero model calls**.

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
Scope-qualified verified evidence packet
```

F0 stops before Luna. F0 promotion permits the next implementation/test step only: a small installed named-store read-only F1 slice that may pass the scope-qualified packet into the existing 0.1.17 Query Plane composer.

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

- library-wide union search or ambient all-project search;
- sync/Git/cloud replication;
- cross-project writes;
- Personal store;
- persistent entity/person graph;
- vector default;
- automatic identity/alias merge;
- background indexing/maintenance;
- canonical manifest/schema migration;
- paid Luna calls;
- E023 G2/G3 reopening or new semantic adjudication.

## Required permission composition

A future named-store Query Plane operation is authorized only when all required grants are valid:

```text
current workspace opt-in
AND current 0.1.17 Query Reasoning grant
AND current-workspace library access grant
AND requested external store registration/read-exposure grant
AND exact unambiguous logical store resolution
```

The existing 0.1.17 Query Reasoning grant remains `current_store` scoped. F0 treats it as insufficient by itself and does not reinterpret it as a federation grant.

## Identity and scope contract

Local F0 uses opaque catalog IDs such as `libstore-<opaque-id>`. IDs are not derived from filesystem path, Git remote, repository name, display label, or source ID. Filesystem roots remain host-private routing metadata.

Current store:

```json
{"kind":"current_store"}
```

External local store:

```json
{"kind":"library_store","store_id":"libstore-..."}
```

Rules:

- unknown or ambiguous store resolution fails closed;
- bare source IDs never select an external store;
- a scoped source resolves only within the named store;
- failure never retries the same source ID against the current store;
- normal results and diagnostics do not expose absolute external roots.

## F0 deterministic case matrix

All cases are required.

1. **F0-01 current-store isolation** — ordinary current-store reads do not enumerate/read external stores.
2. **F0-02 unregistered external store** — an unregistered valid-looking store is invisible to library routing.
3. **F0-03 library grant off** — registration alone does not permit access.
4. **F0-04 named registered store** — valid named resolution selects A and A only.
5. **F0-05 ambiguous alias** — collisions fail before evidence read.
6. **F0-06 unavailable root** — missing A fails as bounded external unavailability without damaging B.
7. **F0-07 damaged external authority** — verification failure in A is contained; B remains usable.
8. **F0-08 scoped terminal identity** — external evidence carries `library_store + store_id`.
9. **F0-09 no cross-store source fallback** — a source missing in A never falls back to the same ID in B.
10. **F0-10 scoped provenance read** — A scope + A source returns verified immutable A bytes and repeats A logical scope.
11. **F0-11 write isolation** — source/HK/lineage writes target current store B only; A is unchanged.
12. **F0-12 stale library grant invalidation** — workspace opt-in epoch changes invalidate prior library access.
13. **F0-13 Query Plane grant alone insufficient** — current-store query permission does not expose A.
14. **F0-14 registration alone insufficient** — registration/library state without full permission composition cannot authorize model-capable external evidence exposure.
15. **F0-15 private locator redaction** — external absolute roots are absent from normal results/errors.
16. **F0-16 no model path** — total model calls are exactly zero.
17. **F0-17 existing product regression gate** — Python tests, E020, VS Code static/runtime integration, bundle, VSIX packaging, and packaged Extension Host tests remain green.
18. **F0-18 semantic/research boundary** — E023 G2/G3 remain closed and the F0 PR introduces no runtime federation/product change.

## Execution design

`run_f0.py` is a standard-library-only deterministic reference preflight. It constructs independent temporary stores A/B with intentionally colliding source identities, a host-private library catalog, workspace-epoch grants, scoped verified reads, and current-store-only write handles.

The GitHub workflow `.github/workflows/validate-e025-f0.yml` performs the 0.1.17 regression gate first. Only after those commands succeed does it run `run_f0.py --regression-gate-pass --diff-boundary-pass`. The final harness invocation therefore cannot mark F0-17/F0-18 PASS unless the existing product checks and the F0 no-runtime-diff boundary have already passed in the same job.

No network model/API invocation exists in the F0 harness.

## F0 adjudication

Frozen-contract execution produced:

```text
F0-01..F0-18: PASS (18/18)
model_calls: 0
0.1.17 regression gate: PASS
F0 no-runtime-federation diff boundary: PASS
E025_F0_NAMED_STORE_SCOPE_CONTRACT = EARNED
```

This is a **preflight promotion only**. No product/runtime federation code was changed to obtain this result.

## Strict promotion rule

`E025_F0_NAMED_STORE_SCOPE_CONTRACT = EARNED` only if:

- all F0-01..F0-18 required assertions pass;
- model calls are exactly 0;
- no external-store write path is introduced;
- no absolute-root leak is found in normal output;
- no current 0.1.17 regression gate fails.

Any required-case failure yields `NOT_EARNED`. No partial promotion.

## What F0 cannot earn

Even a perfect pass does **not** earn library-wide search, ambient cross-project retrieval, cross-project writes, sync, Personal store, persistent identity/entity infrastructure, vector defaults, or semantic quality promotion.

F0 earns only the right to implement/test the **named-store read-only installed slice**.

## Next boundary — F1 named-store installed slice

The next product step may implement one current project B plus one explicitly registered read-only project A while preserving these boundaries:

- deterministic authorization and scope resolution before retrieval/scoring/model exposure;
- current-store Query Reasoning grant remains insufficient without the distinct library grants;
- Luna cannot choose or widen store scope;
- external stores expose read-only handles only;
- `wikiConsult` defaults to current store and accepts only resolver-produced logical external scope;
- scoped `wikiRead` follow-through is mandatory for promotion;
- wrong/ambiguous/unavailable scope fails closed with no current-store fallback;
- terminal refs expose logical scope, not private filesystem roots;
- current-store writes remain the only write target;
- library-wide search, sync, Personal store, cross-project writes, graph/vector/entity infrastructure, G3, and L1 remain closed.

F1 should be a small product branch/PR and then installed dogfood, not a broad federation rewrite.

0.1.17 natural dogfood on #141 continues independently; this experiment does not modify the validated 0.1.17 installed binary.