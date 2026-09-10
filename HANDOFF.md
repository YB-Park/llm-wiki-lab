# Current Handoff

Last updated: 2026-09-02 KST

This is a **living continuation checkpoint**, not project history. Keep only current state, authority boundaries, earned evidence, blockers, and next actions. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Published baseline:

- dogfood release: **0.1.22**
- product merge head: `0e727d77a070c2babdfaaad923be01c8a14c0098`
- published release commit: `d5c4de6ecfd003acf97edd42035a0037d9a3fa4c`
- published VSIX SHA-256: `54715451477769cfa1aad8ed85c163e6f648bd6ab612ddbb180f62efdc0f6a02`

Active branch: `agent/ssh-replication-s1`

Active draft PR: **#222 — S1: remote-authoritative Personal Wiki over SSH**

Remote S1 candidate product head: `0329ee60efbf50647aa3ba25460b19ee732c0b90`

Candidate status: **CI PROMOTION GATE GREEN / READY FOR INSTALLED VS CODE REMOTE-SSH DOGFOOD**.

Candidate evidence:

- real OpenSSH S1 workflow: `33614870377` — PASS
- VS Code Dogfood/package workflow: `33614870257` — PASS
- all PR workflows on candidate head: PASS
- CI artifact ID: `9840583064`
- artifact archive digest: `sha256:2d012a82c9dc824f16a468708b10e3042032b92f6cab23df46b3e6aefc366b47`
- extracted candidate VSIX: `175623` bytes
- extracted candidate VSIX SHA-256: `e66e947965794d8c4489cc0105556eb5a4c784a2e8a042c26fc41359625363ff`

**Installed VS Code Remote-SSH support is not yet earned.** Localhost OpenSSH CI proves product transport mechanics and packaged Extension Host viability, but the exact candidate still needs one installed VS Code Remote-SSH Linux-workspace dogfood pass before PR #222 leaves draft / S1 is declared installed-ready.

Active milestone remains: **remote-capable Personal Wiki before broad UX/satisfaction dogfood resumes**. The prior **UX/UI convergence phase** remains the product baseline, but broad polishing is paused until remote installed dogfood is available.

## WHAT IS NOW IMPLEMENTED

### 1. Existing-store portability — E026 S0-A

**EARNED / shipped since 0.1.19.** Existing `.wiki-lab` portable authority survives root/host relocation without canonical migration; host-local workspace authorization does not travel.

### 2. Workspace-host placement — S0-B mechanics

The extension is explicitly a VS Code `workspace` extension. Python/core/workspace filesystem behavior is packaged and tested on Linux-host semantics.

Status: **CI GREEN; installed Remote-SSH evidence still pending.**

### 3. Remote-authoritative Personal Wiki — S1

One user-owned SSH authority can hold many independent project stores.

- project identity is an opaque `project-*` store identity;
- Git repo/path/branch/commit/content similarity never auto-links projects;
- current workspace writes only its exact remote current store;
- remote writes execute through a fixed helper/operation allowlist using the existing Authority Core;
- reads use verified local replicas;
- SSH unavailable/unverified => last verified replica stays readable, all Project Memory writes fail closed;
- no product cloud, Git sync, background sync, peer mesh, or offline writes.

### 4. Explicit multi-PC attach

`Connect Personal Wiki` now separates:

- **Create New Project Memory** — new independent remote identity; and
- **Use Existing Project Memory** — user explicitly selects one exact existing remote store.

Existing-store attach:

- requires freshly initialized **empty** local Project Memory;
- is never a merge;
- rejects unexpected portable state and symlinked authority entries;
- permits only the normal ephemeral `.writer.lock` rendezvous file;
- acquires the OS store writer lock before final empty-state validation;
- verifies the incoming snapshot;
- preserves host-local `workspace-opt-in.json`;
- atomically activates the selected portable store;
- publishes the host-local remote binding only after successful materialization.

Real SSH CI proves:

```text
PC A -> exact remote store A
PC B -> explicit attach to exact store A
PC B -> remote write to store A
PC A -> explicit refresh sees PC B write
independent store B -> unchanged
```

The same proof checks strict host-key policy, `BatchMode=yes`, CRLF/raw byte preservation, zero model calls, no same-bytes auto-linking, and no cross-store write leak.

### 5. Remote other-project federation

A connected workspace may explicitly choose another project from the same Personal Wiki.

- snapshot is verified into private host-local extension storage;
- SSH target contributes only to a hashed host-local cache key;
- current remote store is excluded;
- cached project is registered through the existing E025 Personal Wiki Library;
- registration does **not** grant access;
- existing separate workspace `Allow Here` grant remains required;
- external project scope remains named-store-only/read-only;
- no ambient union search, external writes, or cross-project maintenance.

## AUTHORITY FLOOR — DO NOT WEAKEN

- workspace use is explicit opt-in;
- Doctor/health = **0 model calls / 0 state changes**;
- `RAW_MEMORY` remains immutable admitted evidence/provenance authority;
- `HUMAN_KNOWLEDGE` remains explicit user-owned decision/belief/rationale;
- `DERIVED_MEMORY` remains noncanonical/rebuildable;
- source admission and lineage meaning remain human-gated;
- authorization happens before retrieval/model exposure;
- external reads never authorize writes;
- no wrong-scope or broad-RAW fallback;
- transport target/credentials/host identity never become canonical or model-visible;
- current-store-only writes remain absolute.

Portable project payload remains frozen around:

- `config.json`
- `manifest.jsonl`
- `raw/`
- `provenance.jsonl`
- `topics.json`
- `human-knowledge/`
- `agent-state.json` as one workflow unit
- rebuildable `agent-wiki/` / bounded telemetry when present

Host-local includes:

- `workspace-opt-in.json`
- Personal Wiki Library routing/grants
- Query grants/usage ledger
- UI/runtime/Python state
- SSH target/config/credentials/keys/agent/known-hosts
- remote binding/cache metadata
- `.writer.lock`

## FAILURE SEMANTICS

- failure before remote canonical mutation => write did not happen;
- remote mutation succeeded but replica refresh failed => remote remains truth; local replica is stale/read-only and further writes stay blocked until refresh succeeds;
- truncated/corrupt/unverified snapshots never replace the last verified copy;
- attach with non-empty/unexpected/symlinked/busy local authority fails closed;
- no rollback fiction, merge, rebase, conflict resolution, or offline queue.

## PARKED RESEARCH GUARDS

Remote work does not reopen closed E023 persistence/identity research. Query-time reconstruction remains the default posture outside explicitly earned product slices, and **paid E023 semantic reruns remain paused**.

- G2 Persistence: **NOT_EARNED; parked**
- G3 Identity / Routing: **NOT_OPENED**

Do not treat Personal Wiki routing/catalog identities as evidence that E023 global persistence or identity projections were earned.

## STILL OUT OF SCOPE

- automatic same-repository/project linking;
- repository/path/content-derived identity;
- offline writes / writable independent replicas;
- cross-project writes;
- Git merge/rebase sync semantics;
- background/ambient sync;
- peer discovery/mesh;
- product cloud sync;
- SSHFS/NFS/SMB live store;
- portable global writable memory;
- ambient all-project search;
- E023 G2/G3 reopening or DB/WAL migration just for remote.

## CURRENT RELEASE DECISION

Do **not** merge/release PR #222 yet solely from localhost CI.

The exact green candidate must first be exercised in an **installed VS Code Remote-SSH session whose workspace host is Linux**. The intended installed journey is:

1. install the candidate VSIX;
2. open a trusted Linux workspace through VS Code Remote-SSH and confirm LLM Wiki runs as a workspace extension;
3. Set Up Project Memory;
4. connect to a user-owned non-interactive SSH Personal Wiki authority;
5. create or explicitly attach one exact project store;
6. remember/read project evidence;
7. from a second workspace/PC, explicitly attach the same store, write, then refresh the first and observe it;
8. verify another remote project is addable only read-only through Other Project Memories;
9. disconnect authority and confirm stale local reads remain available while writes are blocked;
10. reconnect/refresh and confirm recovery.

## NEXT ACTION

1. Run the exact `0329ee60...` candidate VSIX in an actual installed VS Code Remote-SSH Linux workspace.
2. Record installed evidence against #213 / E026, including workspace-host placement, create/attach, A→B→A visibility, other-project read-only federation, offline read-only, and recovery.
3. If installed evidence passes with no semantic changes, mark E026 S0-B/S1 installed gate earned, move PR #222 out of draft, run final unchanged-code gates, merge.
4. Bump/package the next dogfood release (expected **0.1.23**) from the merged remote-capable product and publish versioned/latest VSIX metadata.
5. Only then resume broad real-use UX dogfood on the remote-capable build.

Fast pointers: #213, #222, `experiments/E026-ssh-store-portability/README.md`, E025/#202, Query Plane #204, `docs/09-alpha-core-readiness-gate.md`.
