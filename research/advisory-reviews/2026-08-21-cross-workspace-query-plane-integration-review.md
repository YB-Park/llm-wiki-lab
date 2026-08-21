# Advisory Re-Review — Cross-Workspace Personal Wiki on the 0.1.17 Query Plane

Status: **ADVISORY / ACTIVATED DESIGN-PREFLIGHT / NOT AN ADR / NO RUNTIME MERGE DECISION**  
Review date: **2026-08-21 KST**  
Review target snapshot: **`7348509b83202e473d3ef1925225dec39e6f5121`**  
Repository: `YB-Park/llm-wiki-lab`  
Prior advisory snapshot: `review/cross-workspace-personal-wiki-2026-08-20@9628894234c24253f032be810139fee55d0a3558`

> **Authority disclaimer**
>
> This document is a follow-up architecture review against the post-#207 `0.1.17` codebase. It does not override accepted code/ADR behavior, E020, E023 closure, E024 evidence, or installed dogfood observations. It activates #202 only as a **parallel design/preflight track** while 0.1.17 natural dogfood continues. It does not authorize federation to silently widen the currently installed Query Plane grant or to introduce cross-project canonical writes.

## 1. Review question

The previous cross-workspace review asked:

> Can one user carry trustworthy knowledge across project boundaries without destroying the provenance, permissions, and project-specific meaning that made the knowledge trustworthy?

Its strongest answer was:

> **Do not globalize the Authority Core first. Globalize access to multiple existing Authority Cores.**

The question for this re-review is narrower and more current:

> **Now that 0.1.17 has an opt-in Luna Query Plane, where should cross-workspace federation attach, what is the smallest safe product slice, and which new risks must be preregistered before code?**

## 2. Executive verdict

The previous architecture direction is **confirmed**, but the first product slice should be narrower than the original advisory suggested.

### Confirmed target shape

Keep independent project stores as authority boundaries and place a user-level **Personal Wiki Library control plane above them**.

Do not migrate A/B/C into one giant root.

Do not encode projects as topics.

Do not make Luna discover stores or widen authorization.

### Important refinement after 0.1.17

The Query Plane now gives federation a clean insertion point:

```text
Main Agent
   │ wikiConsult(question, optional logical scope)
   ▼
Deterministic Scope Resolver / Library Control Plane
   │  resolves only pre-authorized logical store scope
   ▼
Store-scoped Memory Read Service
   │  verified RAW / HUMAN / nonterminal DERIVED + pending
   ▼
Evidence Packet
   ▼
Existing exact-Luna Query Plane
   ▼
Compact Brief with scope-qualified terminal refs
```

The order is non-negotiable:

> **authorization → scope resolution → retrieval/scoring → evidence verification → Luna exposure**

Luna never chooses which store is allowed.

### Refined first slice

The first cross-workspace product experiment should be **named-store L0**, not library-wide search.

Example:

> While working in B: “How did Project A decide retry policy?”

Expected scope:

```text
current workspace: B
requested external store: A
retrieval universe: A only
write target: still B only
```

This proves the core product value and the dangerous boundaries without yet solving:

- cross-store BM25 calibration;
- duplicate bytes across stores;
- incomplete-library negative evidence;
- multi-store availability semantics;
- broad ambient routing.

Library-wide “did I solve this in any other project?” retrieval should be the next earned slice after named-store use proves valuable.

## 3. Why #207 materially improves the federation design

The 2026-08-20 review was written against `ef8869...`, before E024 and before `wikiConsult` existed.

At `7348509...`, several federation prerequisites are now already explicit in code:

- `wikiConsult` is read-only;
- Query Plane permission is separately granted and revocable;
- Query Plane usage is locally reserved before the model attempt;
- exact `gpt-5.6-luna` is enforced;
- evidence is gathered before composition;
- candidate verification failure fails the consult closed;
- DERIVED and pending lineage are nonterminal;
- terminal refs already carry a `scope_ref` field;
- the Main Agent receives a bounded brief rather than the internal retrieval trace;
- model failure does not trigger a broad raw-memory fallback.

This means federation does **not** need to invent a second semantic composition path.

It should extend the scope/retrieval side while preserving the same Query Plane.

## 4. Architectural placement

### 4.1 Federation belongs above stores, below Luna

The Personal Wiki Library is a **routing/authorization control plane**, not a knowledge store.

It may know:

- opaque local store ID;
- private root locator;
- user-facing display name;
- aliases;
- whether the store is registered for cross-workspace read/model exposure;
- availability/health cache;
- current-workspace access mode.

It must not own copied canonical evidence or semantic truth.

### 4.2 The Memory Read Service should become explicitly store-parameterized

Today `memory-read-service.js` derives one root from the active workspace folder.

A federation-capable version should distinguish:

```text
active workspace context
resolved logical store
physical Wiki root
```

The model/tool must never supply an arbitrary filesystem root.

Only the deterministic scope resolver may turn an authorized opaque store ID into a root locator.

A useful internal shape is conceptually:

```text
ResolvedStore {
  storeId
  displayLabel
  root
  isCurrentStore
}
```

`root` is host-private and must not be returned to the model or diagnostics by default.

### 4.3 Query Plane remains one-shot L0

Federation does not earn L1 iterative Librarian behavior.

For a named store, the existing flow remains:

```text
deterministic retrieval
→ bounded verified RAW regions
→ HUMAN_KNOWLEDGE
→ DERIVED navigation
→ pending lineage context
→ one exact Luna composition
→ terminal validation
```

The only architectural difference is that the packet is built from an explicitly resolved store other than the current one.

## 5. Permission model — do not silently reuse 0.1.17 grants

This is the most important new product boundary.

The current 0.1.17 Query Plane grant explicitly validates:

```text
scope = current_store
```

That grant must **not** silently expand after an upgrade to mean “all registered stores.”

Cross-workspace model exposure needs additional explicit authority.

Recommended grant decomposition:

### A. Workspace memory opt-in

Existing boundary.

Authorizes project-memory tools for the current trusted workspace.

### B. Current-store Query Reasoning grant

Existing 0.1.17 boundary.

Authorizes retrieved current-store admitted memory to exact Luna under chosen usage guards.

### C. Library store registration / external-read grant

New user-level local control-plane state.

Registering A means:

> “This local project store may be used as a read-only cross-workspace Wiki source.”

Registration should make the evidence-exposure consequence explicit.

### D. Current-workspace library access grant

New workspace-local/revocable state, preferably bound to the current workspace opt-in epoch exactly as the Query Plane grant is.

For the first slice, mode should be effectively:

```text
OFF
NAMED_STORE_ONLY
```

No ambient all-project mode in L0.

### Effective authorization rule

A cross-workspace Luna consult is allowed only when all are true:

```text
current workspace enabled
AND current Query Reasoning grant valid
AND library access grant valid for current workspace epoch
AND requested store registered for external read/model exposure
AND requested alias resolves to exactly one store
AND requested store is healthy enough for verified read
```

Any missing clause fails before model exposure.

## 6. Store identity

The previous review correctly rejected path/repository-name/Git-remote as authority identity.

For the first local dogfood slice, a catalog-assigned opaque ID is sufficient:

```text
libstore-<opaque random id>
```

The ID lives in user-local catalog state and is not derived from:

- filesystem path;
- Git remote;
- repository name;
- display label;
- first source ID.

This avoids mutating existing project stores merely to register them.

### Known limitation accepted for local L0

If the user-level catalog is lost, those local library IDs may need re-registration.

That is acceptable for the first **same-machine local federation** slice because:

- canonical stores remain intact;
- no canonical source identity is changed;
- no sync/portable identity claim is being made;
- the catalog is explicitly control-plane state.

Portable stable store identity should be a separate pre-sync decision.

## 7. Scope reference contract

The current Query Plane already uses:

```text
scope_ref = { kind: "current_store" }
```

Federation should extend the union, not replace it.

Conceptually:

```text
{ kind: "current_store" }
{ kind: "library_store", store_id: "libstore-..." }
```

Important rules:

- `store_id` is opaque;
- filesystem paths never appear in terminal refs;
- display labels are UX metadata, not identity;
- bare `src-...` is never sufficient to route a cross-store read;
- an unknown `store_id` fails closed;
- a source ID is resolved only inside the store named by its scope ref.

## 8. `wikiRead` follow-through is a merge blocker for federation

Cross-workspace `wikiConsult` cannot be considered provenance-preserving unless its terminal refs can be drilled into safely.

Today `wikiRead` accepts a bare `sourceId` and reads the current store.

Named-store L0 therefore needs one of:

```text
wikiRead(sourceId, scopeRef)
```

or an equivalent opaque scoped terminal reference input.

Preferred behavior:

- no `scopeRef` → current-store behavior stays backward compatible;
- `scopeRef=library_store/...` → deterministic catalog resolution then verified read from that store;
- external store is read-only;
- ambiguous/missing/unauthorized scope never falls back to current store;
- the returned provenance repeats the logical project/store scope.

A cross-store terminal ref that cannot be verified with `wikiRead` is not sufficient for product promotion.

## 9. Human Knowledge applicability

Cross-workspace access creates a semantic danger that does not exist as strongly inside one project:

> A decision authoritative as “what we decided in A” is not automatically authoritative as “what B should do.”

The composer contract should add an explicit scope-applicability rule:

```text
Project-local HUMAN_KNOWLEDGE is authoritative as a record of the user’s decision/belief in that store.
Do not promote it into a cross-project/global user preference unless the user explicitly created/promoted Personal Human Knowledge.
```

For named-store L0, the answer should naturally say:

> “Project A decided X because Y.”

not:

> “We should use X in B.”

The Main Agent may reason about relevance after receiving that scoped fact.

## 10. Pending lineage and DERIVED behavior

For an explicit named-store consult:

- that store’s pending lineage may be included as nonterminal workflow context;
- other stores’ pending lineage must remain invisible;
- DERIVED notes remain navigation only;
- any load-bearing statement still terminates on RAW or HUMAN_KNOWLEDGE from the same resolved store.

Do not combine pending workflow state across stores in L0.

## 11. Read-only guarantee

Cross-workspace federation must not widen any existing write tool.

While B is current:

```text
rememberWikiSource → B only
rememberHumanKnowledge → B only
resolveWikiLineage → B only
AI-summary maintenance → B only unless separately redesigned later
```

A being registered/readable does not authorize:

- source admission into A;
- Human Knowledge creation/supersession in A;
- lineage resolution in A;
- derived maintenance in A;
- config changes in A.

The safest implementation is not merely UI policy: external-store handles should be passed only into read services that expose no mutation operations.

## 12. Failure semantics

Named-store L0 should fail closed before Luna in at least these cases:

- library access disabled;
- requested store not registered;
- alias matches zero stores;
- alias matches multiple stores;
- store root missing/unmounted;
- store manifest integrity not acceptable for verified read;
- requested store becomes unavailable between scope resolution and evidence verification;
- scoped source verification fails;
- current Query Reasoning grant missing/expired;
- library grant stale after workspace disable/re-enable;
- provider cannot enforce the user-selected per-response credit guard.

No failure may silently change scope.

Especially forbidden:

```text
A unavailable → search B instead
A unauthorized → search all other stores
scope ref invalid → try same source ID in current store
Luna unavailable → dump raw A memory into Main Agent
```

## 13. Current-store isolation must remain cheap

Ordinary current-project questions must not pay a privacy or performance tax merely because a Personal Wiki Library exists.

When no external scope is requested:

- do not enumerate library roots for retrieval;
- do not read external manifests;
- do not compute cross-store IDF;
- do not health-check every registered store;
- do not expose store names to Luna;
- preserve the 0.1.17 current-store contract.

This is both a performance and privacy invariant.

## 14. Usage guard behavior

Named-store `wikiConsult` should use the **current workspace’s Query Plane usage guard**, because the model call is being initiated from the current workspace/session.

Do not create hidden per-external-store model-call defaults.

The external-store registration/library grant is an exposure authorization, not a billing bucket.

The existing distinctions remain:

- local reserved model-call attempts;
- provider AI-credit guard;
- exact provider billing if reported.

Never infer one from another.

## 15. Why library-wide search should be F1, not first L0

The earlier advisory proposed both named-project and library-wide retrieval in the first slice.

After reviewing 0.1.17, I recommend splitting them.

Named-store lookup has one authorized corpus and preserves existing retrieval semantics almost exactly.

Library-wide search introduces four new questions simultaneously:

### 15.1 Score comparability

Independent per-store BM25 scores must not be compared directly.

A real authorized-union scorer is required.

### 15.2 Duplicate evidence

Identical bytes in A and C must not look like independent corroboration merely because two stores contain them.

The union layer needs cross-store membership/dedup semantics.

### 15.3 Partial availability and negative evidence

If the user asks “did I ever decide X anywhere?” while one registered store is offline, the system must not casually answer “no.”

The product needs explicit incomplete-scope semantics.

### 15.4 Broader exposure

A library-wide query sends evidence from multiple registered stores to Luna in one operation and therefore has a larger privacy surface than named-store lookup.

These are solvable, but they are not needed to prove the first cross-workspace value proposition.

## 16. Recommended sequence

### F0 — zero-model federation contract

No semantic benchmark and no paid Luna rerun.

Test routing/authorization/provenance only.

### F1 — named-store installed Query Plane dogfood

One current store B + one registered read-only A.

Use the existing Query Plane composer after deterministic A-only evidence collection.

### F2 — authorized library-wide union retrieval

Only if F1 produces real value and users naturally ask cross-project similarity/rediscovery questions.

At F2, implement one authorized-union scoring space and duplicate-membership semantics before Luna.

### F3 — Personal store / personal-global Human Knowledge

Only when natural use produces knowledge whose authority genuinely belongs to the person rather than a project.

### S0+ — sync remains separate

No Git/cloud replication is required for F0/F1/F2.

## 17. F0 zero-model preregistration target

The next concrete preparation should be a deterministic contract fixture with two independent Wiki stores A/B.

At minimum, freeze cases for:

1. current-store question never touches A;
2. unregistered A cannot be addressed;
3. registered A + library grant OFF cannot be addressed;
4. registered A + valid named-store grant resolves A only;
5. alias collision fails before retrieval;
6. missing A fails as unavailable, not B corruption;
7. damaged A fails named A request without disabling B current-store memory;
8. `scope_ref` is required for external terminal routing;
9. same `src-...` token intentionally present in A and B cannot cross-route;
10. scoped `wikiRead` returns verified bytes from the originating store only;
11. external read never invokes source/HK/lineage mutation;
12. workspace disable invalidates library access grant;
13. re-enable does not resurrect stale grant;
14. current-store Query Plane grant alone cannot expose A;
15. library registration alone cannot invoke Luna;
16. external filesystem root is absent from model-visible output and bounded diagnostics;
17. Query Plane disabled/budget/unavailable behavior still returns `fallback=none`;
18. existing 0.1.17 current-store contract remains unchanged.

Model calls for F0: **0**.

The new risk is scope authority, not semantic answer quality; E024 already earned the one-shot composer.

## 18. Candidate implementation seams after F0 passes

The narrowest likely product code surface is:

- new local library catalog/control-plane module in VS Code host;
- new configure/register command(s) with explicit modal disclosure;
- Memory Read Service accepts a resolver-produced store handle instead of always deriving current root;
- `wikiConsult` accepts an optional logical named scope while defaulting to current store;
- Query Plane payload/validator allows a strictly versioned `library_store` scope ref;
- `wikiRead` gains optional scoped routing;
- static/runtime tests lock all cross-store writes out;
- packaged Extension Host tests prove the scope contract survives VSIX packaging.

Avoid touching:

- canonical manifest schema;
- RAW source IDs;
- topic semantics;
- Human Knowledge record schema;
- E023 persistence/identity gates;
- writer lock;
- background maintenance.

## 19. Product UX recommendation

Do not add a large Tree/View just to manage the library initially.

A minimal user flow can be:

1. `LLM Wiki: Configure Personal Wiki Library`;
2. choose/register another local Wiki project store;
3. see the logical project label and explicit read/model-exposure disclosure;
4. enable named-store lookup for this workspace;
5. ask normal Agent conversation:
   - “How did Project A decide X?”
6. Agent calls `wikiConsult` with the named logical scope;
7. result visibly says it came from Project A;
8. optional `wikiRead` follows the scoped terminal ref.

The UI should expose logical project names, not raw filesystem roots.

## 20. Sync remains a separate gate

The earlier review’s Git conclusion remains correct.

Git may become Sync Provider #1, but federation does not require it and must not inherit Git semantics.

Before any multi-machine sync experiment, separately resolve:

- store-portable identity;
- canonical vs workflow vs host-local state classification;
- `agent-state.json` portability;
- remote exposure consent;
- divergence detection;
- no automatic semantic merge;
- pre/post sync integrity verification.

Do not let “Personal Wiki Library” quietly become “put `.wiki-lab` in Git.”

## 21. What this review changes from the 2026-08-20 advisory

### Kept

- independent project stores;
- user-level library/federation above them;
- current store read/write, external stores read-only;
- explicit grants;
- qualified provenance;
- authorization before retrieval/scoring/model exposure;
- no G3/vector/graph requirement;
- sync separate.

### Refined

- federation now attaches naturally **under the Query Controller and above store-scoped reads**;
- existing 0.1.17 current-store Query Reasoning permission must not widen silently;
- add a distinct library access/exposure grant;
- make scoped `wikiRead` a required provenance feature;
- add project-local applicability instructions for Human Knowledge;
- split named-store lookup from library-wide union retrieval;
- use zero-model F0 to test scope authority before any semantic/Luna experiment.

## 22. Activation decision

Issue #202 contained three activation conditions, including explicit owner promotion of cross-project Personal Wiki as the next product slice or a narrow zero/new-semantic-infrastructure prototype.

The current owner instruction explicitly asks that 0.1.17 long-horizon dogfood continue while this next axis is prepared in parallel.

Therefore the correct project-state interpretation is:

> **#202 is activated for design/preflight and zero-model F0 preparation.**

It is **not yet activated for broad runtime federation merge**.

The next decision boundary is F0, not another architecture debate and not a paid semantic benchmark.

## 23. Strongest recommendation

Proceed in parallel with 0.1.17 dogfood, but keep the next slice disciplined:

> **Personal Wiki Library → named authorized external store → store-scoped Memory Read Service → existing Query Plane → scope-qualified provenance.**

Do not start with global search.

Do not start with sync.

Do not start with persistent identity semantics.

Do not start with another Luna benchmark.

First prove that cross-workspace **scope authority and provenance routing** can be made boring, deterministic, and fail-closed.

If that passes, named-store installed dogfood is the right next product experiment.