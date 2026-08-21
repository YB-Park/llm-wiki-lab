# Current Handoff

Last updated: 2026-08-21 KST — parallel 0.1.17 dogfood + E025 F1 entry

This is a **living continuation checkpoint**, not project history. Keep only what independent continuation sessions need to decide and act now. If this file conflicts with merged code or an accepted ADR, code/ADR wins. Before repo work, re-check current `main`, open PRs, relevant issues, and current branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Current product posture:
- validated **Dogfood 0.1.17** remains the installed natural-use baseline;
- 0.1.17 includes the earned opt-in exact-Luna L0 Wiki Query Plane while preserving the Authority Core and low-level memory path;
- current product decision: **GO for installed self-dogfood / Alpha use**;
- public Beta: **not declared**;
- primary product-evidence track: **Issue #141 natural installed dogfood**;
- **E025 F0 named-store scope contract is EARNED: 18/18 PASS, zero model calls**;
- #202 is now open only for the narrow **F1 named-store read-only product slice**;
- library-wide/ambient federation, sync, cross-project writes, Personal store, graph/vector/entity infrastructure, and automatic identity routing remain closed;
- paid E023 semantic calls: **paused**;
- E023 G2/G3 remain closed/parked;
- E024 L1 iterative Librarian remains not earned;
- Issue #132 reliability remains evidence-gated.

Run dogfood and F1 as independent parallel continuations. Do not let the slow natural-dogfood timeline block a bounded F1 implementation, and do not let F1 destabilize the validated 0.1.17 baseline.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval, organization, compilation, and maintenance inside granted authority.**

Cross-project value must come from authorized access to multiple independent project Authority Cores, not from globalizing those Authority Cores.

## Parallel Track A — 0.1.17 installed natural dogfood

Primary issue: **#141**

Validated release:
- `dogfood/releases/llm-wiki-dogfood-0.1.17.vsix`
- stable path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- SHA-256: `a0d8f19696e12dfa92d643d739fdbf5386f26f4e0338f536406ba78ac85b2962`
- validated product head: `7348509b83202e473d3ef1925225dec39e6f5121`

Observe only natural evidence: correct memory-path use, Query Plane usefulness/insufficiency, latency, repeated `wikiRead`, long-source recovery, pending/history behavior, lifecycle/privacy/provenance behavior, usage-guard comprehension, and whether model spend is justified. Do **not** manufacture synthetic coverage just because a case exists.

Fix promptly only for meaningful blockers such as data loss/corruption, authority/privacy violation, broken enable/disable lifecycle, terminal provenance failure, misleading causal diagnostics, or unusable ordinary core/Query Plane behavior. Accumulate evidence before mild UX/default/architecture changes.

## Parallel Track B — cross-workspace Personal Wiki / E025 F1

Primary issue and continuation source of truth: **#202**.

### Promotion state

E025 F0 is merged and earned. The zero-model scope-authority preflight passed all mandatory cases while the 0.1.17 regression gate remained green.

`E025_F0_NAMED_STORE_SCOPE_CONTRACT = EARNED`

This earns **only** the next installed/product slice: named-store read-only federation. It does not earn broad federation.

### F1 allowed implementation surface

Implement the smallest product path that can support:

```text
Current trusted workspace B
        │ explicit named-store request
        ▼
Personal Wiki Library control plane
        │ deterministic authorization + exact scope resolution
        ▼
Named external project store A — READ ONLY
        ▼
Store-scoped Memory Read Service
        ▼
Existing 0.1.17 Query Plane composer
        ▼
Scope-qualified Wiki Brief
        ▼
Scoped wikiRead follow-through
```

Required F1 boundaries:
- authorization is resolved **before retrieval, scoring, candidate counts, diagnostics, or model exposure**;
- Luna never widens scope and never chooses which private store it may inspect;
- ordinary current-project questions remain current-store-only and do not enumerate library stores;
- the existing 0.1.17 Query Reasoning grant remains `current_store` scoped and must not silently become a federation grant;
- external-store registration/model exposure requires a distinct explicit local grant;
- current-workspace library access grant is separate and revocable, bound to the current workspace opt-in epoch;
- named external stores are read-only;
- opaque `library_store` IDs are routing identity; paths stay host-private;
- bare `src-...` IDs never select an external store;
- scoped provenance follow-through must read the same store that produced the hit;
- wrong-scope, unknown-store, unavailable-store, damaged-store, or ambiguous alias resolution fails closed with no cross-store fallback;
- external-store pending lineage may appear only for an explicit request to that store and remains nonterminal;
- project-local Human Knowledge is authoritative as a record of that project's/user's decision context, not automatically as a global preference;
- external-store readability never authorizes source admission, Human Knowledge writes, lineage writes, maintenance writes, or config writes there;
- normal diagnostics and model-visible results expose logical scope, not absolute private filesystem roots;
- Query Plane disabled/budget/unavailable/verification failure keeps `fallback=none`.

### Still closed

Do not open in F1:
- library-wide union ranking or ambient all-project search;
- sync/Git/cloud replication;
- Personal store writes or personal-global Human Knowledge;
- cross-project canonical/workflow/derived writes;
- graph/entity/ontology infrastructure;
- vector retrieval defaults;
- automatic identity/person routing or alias merging;
- background cross-project maintenance;
- multi-user/multi-machine concurrency;
- persistent store identity/schema migration;
- E024 L1 iterative Librarian;
- E023 G2/G3 or paid semantic tuning loops.

### F1 promotion boundary

A candidate F1 is not ready for installed dogfood unless tests prove at minimum:
- current-store path remains backward compatible and library-isolated by default;
- permission composition cannot be bypassed by any subset of grants;
- named scope resolves exactly one registered store before any external read;
- scope-qualified RAW/HUMAN terminal refs survive Query Plane validation;
- scoped `wikiRead` verifies immutable bytes from the originating store only;
- same source ID in A/B cannot cross-route;
- external-store write paths are structurally unavailable or demonstrably unchanged;
- workspace disable/re-enable invalidates stale library access;
- private roots are absent from normal output;
- existing Python/E020/VS Code integration/bundle/VSIX/packaged Extension Host regression gate remains green.

F1 may use the already-earned exact-Luna composer only after deterministic authorization, scope resolution, retrieval, and evidence verification have completed.

## Authority and privacy floor

These invariants remain non-negotiable across both active tracks:
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

## Parallel Track C — reliability, only when evidence makes it material

Issue **#132** remains evidence-gated:
- `.wiki-lab/agent-state.json` deletion is not independently detectable;
- canonical lineage append and pending workflow-state resolution are not one transaction;
- Human Knowledge file deletion is not independently detectable without an index.

Do not preemptively replace storage with a DB/WAL. Do not mix sync design into E025 F1. If installed dogfood or F1 makes a reliability edge material, fix the smallest causal defect first.

## Session entry points

### 0.1.17 dogfood/product evidence
- read #141 and this handoff;
- keep the validated 0.1.17 binary stable unless a real blocker requires a fix;
- record only meaningful natural observations.

### Cross-workspace/F1
- read #202 latest comments and this handoff;
- inspect current open PRs/branches first;
- implement/test only named-store read-only federation;
- keep every authorization/scope decision deterministic and before retrieval/model exposure;
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

Run the project as parallel continuations:

1. **Dogfood session:** keep 0.1.17 installed natural use running and record meaningful evidence on #141.
2. **Cross-workspace session:** implement the bounded E025 **F1 named-store read-only product slice** with distinct library permissions, deterministic pre-retrieval scope resolution, store-scoped reads, scope-qualified terminal refs, scoped `wikiRead`, fail-closed routing, private-root redaction, and current-store-only writes. Validate the full packaged regression gate before installed dogfood.
3. **Reliability/research sessions:** remain parked unless independent evidence activates them.

Do not let speculative parallel work destabilize the validated 0.1.17 product, and do not use F1 as a pretext to open library-wide federation or closed research axes.