# Current Handoff

Last updated: 2026-08-21 KST — E025 F1 validated for installed dogfood handoff

This is a **living continuation checkpoint**, not project history. Keep only what independent continuation sessions need to decide and act now. If this file conflicts with merged code or an accepted ADR, code/ADR wins. Before repo work, re-check current `main`, open PRs, relevant issues, and current branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Current product posture:
- validated **Dogfood 0.1.17** remains the installed natural-use baseline until 0.1.18 is merged, rebuilt on `main`, and published by the validated-VSIX workflow;
- 0.1.17 includes the earned opt-in exact-Luna L0 Wiki Query Plane while preserving the Authority Core and low-level memory path;
- current product decision: **GO for installed self-dogfood / Alpha use**;
- public Beta: **not declared**;
- primary product-evidence track: **Issue #141 natural installed dogfood**;
- **E025 F0 named-store scope contract is EARNED: 18/18 PASS, zero model calls**;
- **E025 F1 named-store read-only implementation is READY FOR INSTALLED DOGFOOD**;
- validated F1 runtime head: `514daf17027827c3ec8090b6fd7e3317e00561d2`;
- validated F1 `VS Code Dogfood` run: `32454285838` — Python 3.9, 172 Python tests, E020 78/60/7/11 zero-model, static/federation safety, cross-process usage-cap test, Extension Host, bundle, VSIX, packaged Extension Host, artifact upload all PASS;
- E010 self-repo dogfood and E004/E014 validation workflows are green on the same tested head;
- PR #211 may now be promoted/merged for the narrow 0.1.18 installed slice, followed by a fresh `main` build and automated validated-VSIX publish;
- library-wide/ambient federation, sync, cross-project writes, Personal store, graph/vector/entity infrastructure, and automatic identity routing remain closed;
- paid E023 semantic calls: **paused**;
- E023 G2/G3 remain closed/parked;
- E024 L1 iterative Librarian remains not earned;
- Issue #132 reliability remains evidence-gated.

The F1 promotion is a **deployment-readiness decision for one explicitly named read-only external project store path**, not an architecture-wide federation promotion. Do not use it to broaden ordinary retrieval.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval, organization, compilation, and maintenance inside granted authority.**

Cross-project value must come from authorized access to multiple independent project Authority Cores, not from globalizing those Authority Cores.

## Track A — installed natural dogfood

Primary issue: **#141**

Current installed validated release until 0.1.18 publication:
- `dogfood/releases/llm-wiki-dogfood-0.1.17.vsix`
- stable path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- SHA-256: `a0d8f19696e12dfa92d643d739fdbf5386f26f4e0338f536406ba78ac85b2962`
- validated product head: `7348509b83202e473d3ef1925225dec39e6f5121`

Once #211 is merged, do not manually replace these files. The existing `publish-vsix-in-repo.yml` workflow must publish the exact 0.1.18 VSIX bytes only after the `main` `VS Code Dogfood` workflow completes successfully, including packaged Extension Host execution.

Observe only natural evidence: correct memory-path use, Query Plane usefulness/insufficiency, latency, repeated `wikiRead`, long-source recovery, pending/history behavior, lifecycle/privacy/provenance behavior, usage-guard comprehension, named-store usefulness, and whether model spend is justified. Do **not** manufacture synthetic coverage just because a case exists.

Fix promptly only for meaningful blockers such as data loss/corruption, authority/privacy violation, broken enable/disable lifecycle, terminal provenance failure, misleading causal diagnostics, usage-guard bypass, external-store mutation, or unusable ordinary core/Query Plane behavior. Accumulate evidence before mild UX/default/architecture changes.

## Track B — cross-workspace Personal Wiki / E025 F1

Primary issue and continuation source of truth: **#202**.

### Promotion state

E025 F0 is merged and earned:

`E025_F0_NAMED_STORE_SCOPE_CONTRACT = EARNED`

The narrow F1 implementation has now passed its adversarial product/runtime/package gate:

`E025_F1_NAMED_STORE_READ_ONLY = READY_FOR_INSTALLED_DOGFOOD`

Tested runtime head: `514daf17027827c3ec8090b6fd7e3317e00561d2`

Validated `VS Code Dogfood` run: `32454285838`

Evidence includes:
- Python 3.9 bundled-core compatibility PASS;
- Python suite PASS, 172 tests;
- E020 frozen contract PASS: 78 cases / 60 supported / 7 partial / 11 deferred / zero model calls;
- dedicated federation safety/static PASS;
- separate-process atomic Query Plane usage-cap test PASS;
- Extension Host integration PASS;
- bundled core PASS;
- VSIX package contents PASS;
- unpacked packaged VSIX Extension Host PASS;
- artifact upload PASS;
- E010/E004/E014 companion workflows PASS.

This earns **installation/natural-use evaluation of the named-store read-only slice only**. It does not earn broad federation.

### F1 implemented boundary

```text
Current trusted workspace B
        │ explicit named-store request
        ▼
Personal Wiki Library control plane
        │ deterministic authorization + exact scope resolution
        ▼
Named external project store A — READ ONLY
        ▼
Bundled trusted federation read bridge
        ▼
Store-scoped Memory Read Service
        ▼
Existing exact-Luna Query Plane composer
        ▼
Scope-qualified Wiki Brief
        ▼
Scoped wikiRead follow-through
```

Enforced F1 boundaries:
- authorization is resolved **before external retrieval/model exposure**, and authorization/identity is revalidated during external reads and immediately before model spawn;
- Luna never widens scope and never chooses which private store it may inspect;
- ordinary current-project `wikiMemory` and `wikiConsult` remain current-store-only unless an external store is explicitly named;
- the Query Reasoning grant remains `current_store` scoped and is insufficient by itself for external access;
- external-store registration plus current-workspace library access are distinct explicit local grants;
- current-workspace library access is bound to the workspace opt-in authority epoch;
- named external stores have only a dedicated read bridge; the generic Python runner refuses external handles;
- external read bridge uses the bundled trusted core with isolated Python startup rather than current-workspace `corePath`/configured runtime/PYTHONPATH;
- registration continuity is tied to an immutable manifest authority witness and checked before/after bounded bridge operations;
- opaque `library_store` IDs are routing identity; private paths do not enter normal Agent/model output;
- bare `src-...` IDs never select an external store;
- scoped provenance follow-through reads only the originating store and never retries against current/other stores;
- catalog corruption, identity change, unavailable/damaged store, revoked grant, and ambiguous alias fail closed;
- external project Human Knowledge remains that project's confirmed decision/belief record and is not automatically current-project advice/global preference;
- external-store pending lineage is nonterminal workflow state;
- source admission, Human Knowledge writes, lineage writes, maintenance, and config writes remain current-store-only; existing `agent-tools.js` write implementation was not widened for F1;
- optional DERIVED note failures cannot hide external authorization/catalog/identity revocation;
- Health reports library access/catalog validity/store count only, not roots/evidence;
- Query Plane disabled/budget/scope/verification/usage-guard failure keeps `fallback=none`;
- the user-chosen Query Plane daily model-attempt cap is process-safe across concurrent local Extension Hosts sharing the same extension profile/global storage, using atomic slot claims under a hash-only workspace key;
- 0.1.17 same-day usage is conservatively carried forward into the new ledger;
- crash/uncertain reservations remain counted rather than refunded;
- inability to enforce the durable usage ledger blocks the model call with `model_calls=0`.

The process-safe daily-attempt ledger is a **local-profile safety boundary**, not a distributed billing or multi-machine coordination claim.

### Still closed

Do not open from this F1 result:
- library-wide union ranking or ambient all-project search;
- sync/Git/cloud replication;
- Personal store writes or personal-global Human Knowledge;
- cross-project canonical/workflow/derived writes;
- graph/entity/ontology infrastructure;
- vector retrieval defaults;
- automatic identity/person routing or alias merging;
- background cross-project maintenance;
- multi-user/multi-machine concurrency;
- cross-profile/global distributed usage coordination;
- persistent canonical store identity/schema migration;
- E024 L1 iterative Librarian;
- E023 G2/G3 or paid semantic tuning loops.

### Installed F1 dogfood questions

Natural installed use should now answer:
- does explicitly naming another project feel natural or burdensome?;
- does the Agent invoke external `wikiConsult` only when the user actually names that project?;
- are Query Reasoning and Personal Wiki Library permission surfaces understandable as separate grants?;
- are scope-qualified terminal refs and scoped `wikiRead` understandable?;
- do external Human Knowledge statements stay visibly project-scoped in real answers?;
- do missing/moved/replaced/revoked stores fail clearly without creating fallback pressure?;
- are external reads observably non-mutating?;
- does the compact brief reduce Main-Agent context/tool-turn burden?;
- do local usage guards behave as expected under ordinary concurrent VS Code use?;
- does any real use reveal a blocker that justifies the smallest causal fix?

Do not manufacture evidence and do not treat successful installed use as automatic permission for ambient federation.

## Authority and privacy floor

These invariants remain non-negotiable:
- workspace use is explicit opt-in and trusted-workspace only;
- workspace disable makes Agent tool runtime implementations non-invokable while preserving Wiki data;
- disabling and later re-enabling project memory invalidates previous model-exposure grants;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` = immutable admitted evidence / provenance authority;
- `DERIVED_MEMORY` = noncanonical, rebuildable navigation/synthesis aid;
- `HUMAN_KNOWLEDGE` = explicit user-owned decision, belief, rationale, or approved synthesis;
- pending lineage is workflow state, never terminal authority;
- source admission, Human Knowledge authorship, and lineage semantics remain human-gated;
- Query Plane is read-only with respect to canonical epistemic state;
- no hidden product-owned Query Plane spend default exists;
- selected-candidate verification failure fails the consult closed;
- RAW/DERIVED hints may be merged for navigation, but DERIVED never becomes terminal authority;
- terminal Wiki Brief refs may terminate only on RAW/HUMAN_KNOWLEDGE;
- exact model for the current Query Plane slice is `gpt-5.6-luna`;
- composer evidence travels through stdin and the Copilot subprocess uses a neutral temporary cwd;
- no hidden chain-of-thought or retrieval transcript is returned;
- silent broad-raw fallback is forbidden.

## E020 deterministic contract

The existing synthetic product contract remains:

**78 zero-model cases: 60 supported / 7 partial / 11 deferred.**

Do not change case judgments merely to accommodate implementation movement. E025 scope-authority tests are separate until deliberately promoted into the frozen product contract.

## Research posture

- E023 G1 exploratory retrieval/composition mechanism search: closed.
- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning remain unauthorized as a tuning loop.
- paid E023 semantic calls: **paused**.
- E024 L0 Query Plane: **EARNED for opt-in product dogfood**.
- E024 L1 iterative Librarian: **NOT EARNED**.
- cross-workspace scope generality is a separate axis and does not reopen E023 persistence/identity gates.

Frozen E023 continuation marker: **Run the Day-0 installed smoke on the exact 0.1.16 VSIX**. This remains a historical closure invariant required by the E023 closure validator; later E024/E025 work does not change the G2/G3 verdict.

Retained principles:

> A representation may preserve authority globally while a later selection bottleneck destroys it locally.

> Hide retrieval/composition work from the Main Agent's context, not terminal provenance from the user/system.

> Federation decides which stores are authorized/searchable; Query Plane decides who performs retrieval/composition and what reaches the Main Agent.

## Track C — reliability, only when evidence makes it material

Issue **#132** remains evidence-gated:
- `.wiki-lab/agent-state.json` deletion is not independently detectable;
- canonical lineage append and pending workflow-state resolution are not one transaction;
- Human Knowledge file deletion is not independently detectable without an index.

Do not preemptively replace storage with a DB/WAL. Do not mix sync design into E025 F1. If installed dogfood makes a reliability edge material, fix the smallest causal defect first.

## Session entry points

### Installed dogfood/product evidence
- read #141, #202, and this handoff;
- until 0.1.18 is published by the validated workflow, the installed binary remains 0.1.17;
- once 0.1.18 is published, install the validated repo VSIX and observe ordinary work;
- record only meaningful natural observations.

### Cross-workspace/F1
- read #202 latest comments and this handoff;
- inspect current open PRs/branches first;
- treat F1 implementation as ready for installed dogfood, not broad federation;
- keep every authorization/scope decision deterministic and before model exposure;
- do not widen into library-wide search, sync, cross-project writes, or identity infrastructure.

### Persistence/identity research
- stop unless genuinely new independent evidence reopens the gate; G2/G3 are not available merely because a mechanism is interesting.

### Reliability
- read #132; act only on concrete product/federation evidence that makes the known edge material.

## Fast pointers

- natural installed dogfood: **#141**
- Query Plane product issue: **#204**
- cross-workspace/federation: **#202**
- E025: `experiments/E025-cross-workspace-named-store-federation/`
- reliability: **#132**
- semantic generality gate: **#160**
- current release metadata: `dogfood/releases/README.md`
- user guide: `dogfood/vscode/README.md`
- E020 deterministic contract: `experiments/E020-synthetic-agent-ux/README.md`
- E024 Query Plane experiment: `experiments/E024-query-plane-token-firewall/`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`

## NEXT ACTION

Proceed in this order:

1. **PR #211:** mark ready and merge only the bounded 0.1.18 F1 named-store read-only slice after recording tested head/run evidence on #202.
2. **Main validation/publish:** require a fresh successful `VS Code Dogfood` push run on merged `main`; let `publish-vsix-in-repo.yml` publish the validated 0.1.18 bytes automatically. Do not manually replace release files.
3. **Installed dogfood:** install the published 0.1.18 VSIX and collect natural evidence on #141/#202. Keep broad federation and closed research axes closed.
4. **Reliability/research:** remain parked unless independent evidence activates them.

Do not let speculative work destabilize the validated installed product, and do not use F1 readiness as a pretext to open library-wide federation or closed research axes.