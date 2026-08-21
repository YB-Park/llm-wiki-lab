# Current Handoff

Last updated: 2026-08-21 KST

This file is a **living continuation checkpoint**, not project history. Keep only current state, active boundaries, and next actions. Historical experiment detail belongs in experiment/ADR/issue records. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, relevant issues, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

- current product decision: **GO for installed self-dogfood / Alpha use**
- public Beta: **not declared**
- primary product-evidence track: **Issue #141 natural installed dogfood**
- validated/published dogfood: **0.1.18**
  - versioned VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.18.vsix`
  - stable path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
  - SHA-256: `c4a7df778f4b9a41d186a9bb69a1f00ae370812193e8a70d6f9a1231b86f45ed`
  - validated main product head: `09456e02ae25dfaf479c1ef77fd74b9757c45685`
  - validated `VS Code Dogfood` run: `32454671072`
- E024 L0 Query Plane: **EARNED for opt-in product dogfood**
- E025 F0 named-store authority preflight: **EARNED, 18/18 PASS, zero model calls**
- E025 F1 named-store read-only implementation: **READY FOR INSTALLED DOGFOOD and published in 0.1.18**
- Issue #202 remains the continuation point for cross-workspace / Personal Wiki behavior and evidence
- Issue #132 reliability remains evidence-gated; do not preemptively replace storage with DB/WAL

### Current cross-workspace topology

0.1.18 supports **same-extension-host / same-profile cross-workspace named-store reads**:

- each project keeps its own independent Authority Core (`.wiki-lab` by default);
- Personal Wiki Library is a routing/authorization catalog, not a merged global memory store;
- an existing external project store is registered by absolute filesystem root and logical name/aliases;
- catalog registration is extension-global state for that Extension Host/profile;
- each current workspace separately grants named-store access;
- ordinary `wikiMemory` / `wikiConsult` remain current-store-only unless the user explicitly names a registered project;
- external stores are read-only; current-store source/Human Knowledge/lineage writes are not widened.

**No server, Git repository, or shared database is required for same-host cross-workspace use.** The registered external `.wiki-lab` only needs to be visible on the filesystem to the Extension Host running LLM Wiki.

### Remote / multi-PC status

Do **not** claim automatic multi-PC sharing or sync in 0.1.18.

- sync/Git/cloud replication: **NOT IMPLEMENTED**
- catalog/grant synchronization across machines/profiles: **NOT IMPLEMENTED**
- multi-machine concurrent writers: **NOT SUPPORTED / NOT EARNED**
- live network-share / distributed Authority Core semantics: **NOT EARNED**
- Remote SSH / WSL / Dev Container / Codespaces: **NOT YET VALIDATED AS A PRODUCT BOUNDARY**

VS Code can run workspace extensions in a remote Extension Host. If LLM Wiki runs there, its Node filesystem/Python/runtime/storage naturally refer to that remote environment, so a remote-host-local topology is plausible. But 0.1.18 has no dedicated Remote test matrix and no explicit remote product claim yet. Treat Remote as the next validation slice, not as already supported.

`llmWiki.workspaceDirectory` may be an absolute path, so a project's own store can be relocated outside its repository. **Do not point multiple independent projects at one writable current-store directory** to simulate a global Wiki. Cross-workspace access should go through Personal Wiki Library registrations instead.

## AUTHORITY FLOOR

Non-negotiable current product invariants:

- trusted single-folder workspace only; multi-root fails closed
- workspace use is explicit opt-in
- disabling/re-enabling project memory invalidates stale model/library grants
- `Check Setup and Health` = **0 model calls / 0 state changes**
- `RAW_MEMORY` = immutable admitted evidence / provenance authority
- `DERIVED_MEMORY` = noncanonical, rebuildable navigation/synthesis aid
- `HUMAN_KNOWLEDGE` = explicit user-owned project decision/belief/rationale
- source admission, Human Knowledge authorship, and lineage semantics remain human-gated
- Query Plane is read-only and exact model remains `gpt-5.6-luna`
- terminal Wiki Brief refs terminate only on RAW/HUMAN_KNOWLEDGE
- external project Human Knowledge remains project-scoped; it is not automatically a current-project recommendation/global preference
- authorization and exact named-store scope are resolved before external retrieval/model exposure
- wrong/unknown/ambiguous/revoked/unavailable external scope fails closed with no current/other-store fallback
- external reads never authorize external source/HK/lineage/maintenance/config writes
- private filesystem roots stay out of normal Agent/model output
- Query Plane usage guard failure keeps `fallback=none`; durable usage-ledger enforcement failure blocks the model call
- daily attempt guard is local-profile/process-safe, **not** distributed billing/multi-machine coordination
- no silent broad-raw fallback

## CLOSED / PARKED

- library-wide ambient/union search: closed
- sync/Git/cloud replication: closed
- Personal/global writable store: closed
- cross-project writes: closed
- graph/entity/ontology infrastructure: closed
- vector-default retrieval: closed
- automatic identity/person routing or alias merging: closed
- background cross-project maintenance: closed
- multi-user/multi-machine authority coordination: closed
- E024 L1 iterative Librarian: **NOT EARNED**
- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- paid E023 semantic calls: **paused**
- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning remain unauthorized without new independent evidence

## ACTIVE EVIDENCE QUESTIONS

Natural 0.1.18 dogfood should answer only what real work exposes:

- does normal current-project memory remain natural and reliable?
- when the user explicitly names another registered project, does external `wikiConsult` route correctly and usefully?
- are separate Query Reasoning and Personal Wiki Library grants understandable?
- are scoped provenance and `wikiRead` follow-through understandable?
- do external Human Knowledge statements stay visibly project-scoped?
- do moved/replaced/revoked stores fail clearly without fallback pressure?
- does any actual workflow need Remote/multi-PC access strongly enough to justify the next bounded slice?

Do not manufacture dogfood evidence.

## FAST POINTERS

- installed natural dogfood: **#141**
- cross-workspace / Personal Wiki: **#202**
- Query Plane: **#204**
- reliability: **#132**
- current release metadata: `dogfood/releases/README.md`
- user guide: `dogfood/vscode/README.md`
- E025 contract/results: `experiments/E025-cross-workspace-named-store-federation/`
- E020 frozen product contract: **78 zero-model cases: 60 supported / 7 partial / 11 deferred**

## NEXT ACTION

1. Install/use the published **0.1.18** VSIX in ordinary work and record meaningful natural evidence on #141/#202.
2. Treat same-host named-store federation as the current supported topology; do not broaden ordinary retrieval.
3. Before claiming Remote or multi-PC support, define a separate bounded validation slice that distinguishes:
   - Remote-host-local use (SSH/WSL/Container/Codespaces), from
   - actual cross-machine transport/sync/replication.
4. If Remote/multi-PC becomes material, prove filesystem location, extension-host placement, catalog/grant locality, no cross-writes, and concurrency behavior before adding sync/server architecture.
5. Reliability/research work remains parked unless independent evidence activates it.
