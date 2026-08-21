# Current Handoff

Last updated: 2026-08-21 KST

This file is a **living continuation checkpoint**, not project history. Keep only current state, authority boundaries, and next actions. Historical detail belongs in experiment/ADR/issue records. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, relevant issues/comments, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

- current product decision: **GO for installed self-dogfood / Alpha use**
- public Beta: **not declared**
- current `main` publication checkpoint: `c5cfc1304f6026b84c1e37478e0f85e7c917e8ca`
- validated/published dogfood: **0.1.19**
  - versioned VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.19.vsix`
  - stable convenience path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
  - SHA-256: `5ad0aa719f1b104f1a2378ade2ba71fdf959e472a524f3f3ee39c91f41b5f787`
  - validated product head: `71ba27537e39be36b2ba1709c68bc36c955c967c`
  - validated `VS Code Dogfood` run: `32461723526`
- existing **0.1.18 store format remains the compatibility baseline**; 0.1.19 introduced no canonical schema migration
- E024 L0 Query Plane: **EARNED for opt-in product dogfood**
- E025 F0 named-store authority preflight: **EARNED, 18/18 PASS, zero model calls**
- E025 F1 named-store read-only federation: **EARNED FOR INSTALLED DOGFOOD and shipped**
- E026 S0-A existing-store portability: **EARNED, 12/12 PASS, Python 3.9, zero model calls; shipped in 0.1.19**
- primary natural product evidence: **#141**; cross-workspace evidence/continuation: **#202**; portability/remote continuation: **#213**
- #132 reliability remains evidence-gated; do not preemptively introduce DB/WAL or speculative persistence

## CURRENT PRODUCT SHAPE

- trusted **single-folder** workspace only; multi-root fails closed
- each project keeps an independent Authority Core (`.wiki-lab` by default)
- ordinary `wikiMemory` / `wikiConsult` remain **current-store-only**
- Personal Wiki Library is local routing/authorization state, not a merged/global knowledge store
- an external project is usable only as an **explicitly registered, explicitly named, read-only store** with a separate current-workspace library grant
- exact external scope is resolved before retrieval; scoped `wikiRead` follow-through stays in that exact store
- external store failure never falls back to the current store or another registered store
- source admission, Human Knowledge, lineage, maintenance, and configuration writes remain current-store-only
- external Human Knowledge remains **project-scoped context**, not a global preference or automatic recommendation
- the host-local registration continuity witness detects accidental store replacement; it is **not portable/global store identity**
- Query Plane is read-only; exact composer model remains `gpt-5.6-luna`

## PORTABILITY / REMOTE BOUNDARY

E026 S0-A earned only **existing-store portability**, not synchronization.

What is now proven:

- a representative existing 0.1.18 Wiki can move to a different absolute root without changing RAW/source identity, temporal history, exact provenance, Human Knowledge identity/lineage, workflow state, or derived-note readability
- host-local `workspace-opt-in.json` is not portable authority; the destination requires a fresh workspace authority epoch
- 0.1.19 re-hardens known private Wiki files/subtrees after permission-losing copy/checkout without changing bytes
- permission recovery does not follow private-subtree symlinks
- LF/CRLF mutation of content-addressed RAW fails closed as integrity corruption

Do **not** infer from S0-A that any of the following are supported:

- SSH/Git/cloud replication or automatic multi-PC sharing
- Remote SSH / WSL / Dev Container / Codespaces as a validated product boundary
- multi-machine concurrent writers or distributed writer/usage coordination
- live network-share Authority Core semantics
- automatic Git merge/rebase/conflict resolution of Wiki state
- portable/global store identity or synchronized Personal Wiki catalog/grants

If remote work is deliberately activated, the earned sequence is: **S0-B host-local Remote/SSH runtime matrix first, then S1 user-owned SSH transport proof**. S1 should remain byte-preserving, single-writer/fast-forward, and fail closed on divergence until evidence earns anything broader.

## AUTHORITY FLOOR

Non-negotiable current invariants:

- workspace use is explicit opt-in; disabling/re-enabling invalidates stale Query/Library grants
- `Check Setup and Health` = **0 model calls / 0 state changes**
- `RAW_MEMORY` = immutable admitted evidence / provenance authority
- `DERIVED_MEMORY` = noncanonical, rebuildable navigation/synthesis aid
- `HUMAN_KNOWLEDGE` = explicit user-owned project decision/belief/rationale
- source admission, Human Knowledge authorship, and lineage semantics remain human-gated
- terminal Wiki Brief refs terminate only on RAW/HUMAN_KNOWLEDGE
- authorization constrains scope **before retrieval, scoring, candidate counts, diagnostics, or model exposure**
- named-store authorization is revalidated across external reads and immediately before model execution
- wrong/unknown/ambiguous/revoked/unavailable external scope fails closed
- external reads never authorize external mutation
- private filesystem roots stay out of normal Agent/model output
- Query usage reservations are conservative; uncertain/failed attempts are not silently refunded
- the daily Query attempt guard is local process/profile protection, **not distributed billing or multi-machine coordination**
- no silent broad-RAW fallback

## NOT EARNED / PARKED

- library-wide ambient/union search
- sync/Git/cloud replication and automatic remote discovery
- multi-writer semantic merge, distributed locks, or automatic conflict resolution
- Personal/global writable store or cross-project writes
- portable global identity, automatic person/alias routing, graph/entity/ontology infrastructure
- vector-default retrieval or background cross-project maintenance
- E024 L1 iterative Librarian
- **G2 Persistence: NOT_EARNED; parked**
- **G3 Identity / Routing: NOT_OPENED**
- paid E023 semantic reruns remain **paused**; do not spend on model-backed benchmark work without explicit authorization

## ACTIVE DOGFOOD QUESTIONS

Natural **0.1.19** use should answer only what real work exposes:

- does ordinary current-project memory remain natural, reliable, and low-friction?
- when another registered project is explicitly named, does `wikiConsult` route correctly and usefully?
- are separate Query Reasoning and Personal Wiki Library grants understandable?
- is scope-qualified `wikiRead` provenance follow-through sufficient and appropriately narrow?
- do external Human Knowledge statements stay visibly project-scoped?
- do moved/replaced/revoked stores fail clearly without fallback pressure?
- does real usage create a strong enough Remote/multi-PC need to activate #213 S0-B/S1?

Do not manufacture dogfood evidence.

## FAST POINTERS

- installed natural dogfood: **#141**
- cross-workspace / Personal Wiki: **#202**
- Query Plane: **#204**
- portability / future user-owned SSH transport: **#213**
- reliability: **#132**
- current release metadata: `dogfood/releases/README.md`
- user guide: `dogfood/vscode/README.md`
- E025 contract/results: `experiments/E025-cross-workspace-named-store-federation/`
- E026 portability contract/results: `experiments/E026-ssh-store-portability/`
- E020 frozen product contract: **78 zero-model cases: 60 supported / 7 partial / 11 deferred**

## NEXT ACTION

1. Install/use the published **0.1.19** VSIX in ordinary work; existing 0.1.18 Wiki data carries forward unchanged.
2. Record only meaningful natural evidence on #141/#202; keep same-host named-store federation narrow and read-only.
3. Do not add sync/server/global-memory architecture merely because portability is now proven.
4. If Remote/multi-PC becomes material, continue #213 with **S0-B before S1** and preserve byte-exact authority plus fresh destination-local authorization.
5. Reliability/research work remains parked unless independent evidence activates it.
