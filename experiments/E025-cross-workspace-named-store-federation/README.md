# E025 — Cross-Workspace Named-Store Federation

Status: **F0 EARNED / F1 NAMED-STORE READ-ONLY IMPLEMENTATION READY FOR INSTALLED DOGFOOD**

Primary issue: #202

Frozen baseline: `main@7f0c4045a6341a16c92e4582a92fcd99e6352fcb`

Frozen F0 evaluation contract: `f0-evaluation-contract-v0.json`

Executable zero-model preflight: `run_f0.py`

Validated F1 runtime head: `514daf17027827c3ec8090b6fd7e3317e00561d2`

Validated F1 GitHub Actions run: `32454285838`

## Question

Can LLM Wiki add a local Personal Wiki Library that allows the current trusted workspace to read one explicitly named, explicitly registered external project store **without weakening current-store authority/privacy, provenance routing, Query Plane usage guards, or write isolation**?

This experiment is about **scope authority and routing**, not semantic answer quality. E024 already earned the one-shot exact-Luna Query Plane composer. F0 therefore made zero model calls, and the F1 promotion gate deliberately proves authorization/routing/write-isolation with deterministic and zero-model tests rather than spending model calls merely to exercise permission mechanics.

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
        │
        ▼
Existing exact-Luna Query Plane composer
        │
        ▼
Scope-qualified Wiki Brief / scoped wikiRead
```

F0 stopped before Luna and earned only the right to implement the narrow installed F1 slice. F1 now implements that slice while keeping model exposure behind the existing Query Reasoning grant plus distinct library authorization.

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
- process-safe same-profile daily Query Plane attempt cap across concurrent local Extension Hosts;
- deterministic zero-model permission/routing tests.

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
- multi-machine/profile-global concurrency claims;
- paid Luna tuning/reruns;
- E023 G2/G3 reopening or new semantic adjudication.

## Required permission composition

A named-store Query Plane operation is authorized only when all required grants are valid:

```text
current workspace opt-in
AND current Query Reasoning grant
AND current-workspace library access grant
AND requested external store registration/read-exposure grant
AND exact unambiguous logical store resolution
```

The existing Query Reasoning grant remains `current_store` scoped. F1 treats it as insufficient by itself and does not reinterpret it as a federation grant.

## Identity and scope contract

Local F1 uses opaque catalog IDs such as `libstore-<opaque-id>`. IDs are not derived from filesystem path, Git remote, repository name, display label, or source ID. Filesystem roots remain host-private routing metadata.

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
- normal results and diagnostics do not expose absolute external roots;
- external project Human Knowledge remains authoritative only as that project's confirmed decision/belief record and is never automatically promoted into current-project advice or a global preference.

## F0 deterministic case matrix

All cases were required and passed.

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

## F0 adjudication

Frozen-contract execution produced:

```text
F0-01..F0-18: PASS (18/18)
model_calls: 0
0.1.17 regression gate: PASS
F0 no-runtime-federation diff boundary: PASS
E025_F0_NAMED_STORE_SCOPE_CONTRACT = EARNED
```

This was a preflight promotion only. It earned F1 implementation/testing, not broad federation.

## F1 implementation and adversarial review

The 0.1.18 F1 candidate adds only the named-store read-only product slice and deliberately keeps the existing write layer current-store-only.

Key earned runtime properties at tested head `514daf17027827c3ec8090b6fd7e3317e00561d2`:

- host-local Personal Wiki Library catalog with opaque `libstore-*` IDs;
- registration continuity witness tied to immutable manifest authority and rechecked at use;
- separate current-workspace library grant bound to the workspace authority epoch;
- exact named-store resolution before external retrieval/model exposure;
- dedicated external read-only bridge using the bundled trusted core and isolated Python startup;
- bridge continuity checked before and immediately before successful operation output;
- `wikiConsult` current-store default remains unchanged;
- exact-Luna composer receives one scope-qualified packet and rejects mixed scope;
- public `wikiRead` preserves originating scope and never cross-store-falls back;
- external RAW/HUMAN terminal refs remain scope-qualified;
- external Human Knowledge cannot become automatic current-project recommendation/global preference;
- optional DERIVED read failures never mask authorization/catalog/identity revocation;
- catalog corruption fails closed rather than looking like “not registered” or “source missing”;
- source/Human Knowledge/lineage write implementation remains structurally current-store-only;
- Health exposes only library access/catalog validity/store count, never external roots or evidence;
- Query Plane daily attempt cap is atomically claimed in extension-local global storage using workspace-hash-only paths; concurrent local Extension Hosts cannot exceed the same local-profile cap;
- legacy 0.1.17 same-day usage is conservatively carried forward; crash/uncertain reservations remain counted;
- if the durable usage guard cannot be enforced, the model call is blocked with `model_calls=0`.

The daily-attempt ledger is a local safety boundary, not a distributed billing/coordination system. F1 makes no multi-machine or cross-profile global cap claim.

## F1 validation evidence

Exact tested runtime head: `514daf17027827c3ec8090b6fd7e3317e00561d2`

GitHub Actions `VS Code Dogfood` run: `32454285838`

Required gate results:

```text
Python 3.9 bundled-core compatibility: PASS
Python unit regression suite: PASS (172 tests)
CLI smoke: PASS
E020 frozen synthetic contract: PASS (78 / 60 supported / 7 partial / 11 deferred / zero model calls)
VS Code static + federation safety: PASS
Cross-process query usage ledger test: PASS
Extension Host integration: PASS
Bundled core verification: PASS
VSIX packaging: PASS
Unpacked packaged VSIX Extension Host: PASS
VSIX artifact upload: PASS
E010 self-repo dogfood: PASS
E004/E014 frozen/prescore workflows: PASS
```

No paid E023 semantic rerun was used to earn this boundary.

## F1 adjudication

```text
E025_F1_NAMED_STORE_READ_ONLY = READY_FOR_INSTALLED_DOGFOOD
```

This is **not** a broad-federation promotion and not a public Beta declaration. It means the narrow 0.1.18 implementation has passed the deterministic/runtime/package gate strongly enough to install and observe in natural work.

Installed dogfood must now answer whether the scope/permission UX is useful and understandable in real use. It may reveal blockers requiring a narrow fix; it does not pre-authorize architecture expansion.

## What F1 still cannot earn

Even a perfect installed pass does **not** automatically earn:

- library-wide/ambient all-project search;
- sync or replication;
- cross-project writes;
- Personal store/global Human Knowledge;
- persistent identity/entity/ontology infrastructure;
- vector-default retrieval;
- background federation maintenance;
- E023 G2 persistence or G3 identity/routing;
- E024 L1 iterative Librarian;
- multi-user/multi-machine authority coordination.

Those require separate evidence and promotion decisions.

## Installed dogfood boundary

The next step is the validated 0.1.18 named-store slice in natural installed use. Observe:

- whether explicitly naming another registered project feels natural;
- whether the Agent selects external `wikiConsult` only when the user actually identifies that project;
- whether separate Query Reasoning + Library grants are understandable;
- whether scoped provenance and `wikiRead` follow-through remain understandable;
- whether external Human Knowledge stays project-scoped in actual answers;
- whether missing/moved/replaced/revoked stores fail clearly without fallback temptation;
- whether external reads remain observably non-mutating;
- whether the compact Query Plane result reduces Main-Agent context/tool-turn burden;
- whether local usage guards behave as users expect across ordinary concurrent VS Code use.

Do not manufacture evidence. Record natural installed observations on #202/#141 as appropriate.

0.1.17 natural dogfood on #141 continues independently until the validated 0.1.18 artifact is merged, rebuilt on `main`, and published by the existing validated-VSIX workflow.