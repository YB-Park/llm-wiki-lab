# Current Handoff

Last updated: 2026-09-02 KST

This is a **living continuation checkpoint**, not project history. Keep current state, active authority boundaries, evidence questions, and next actions only. Historical rationale belongs in merged commits/PRs, ADRs, experiments, or dedicated design docs. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, #213, E026, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Published baseline:

- dogfood: **0.1.22**
- product merge head: `0e727d77a070c2babdfaaad923be01c8a14c0098`
- published release commit: `d5c4de6ecfd003acf97edd42035a0037d9a3fa4c`
- VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.22.vsix`
- latest path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- SHA-256: `54715451477769cfa1aad8ed85c163e6f648bd6ab612ddbb180f62efdc0f6a02`
- validated main build: GitHub Actions `32688939217`
- public Beta: **not declared**

Active branch: `agent/ssh-replication-s1`.

Active milestone: **remote-capable Personal Wiki before another broad satisfaction/UX dogfood cycle**.

The owner explicitly treats local-only memory as a real-use suppressor. Broad UX polishing is paused except where it blocks remote setup/use/recovery.

## REMOTE ARCHITECTURE — CURRENT DECISION

Three layers remain separate:

1. **Cross-project federation — E025 / #202:** already shipped as explicit named-store read-only Personal Wiki Library.
2. **Store portability — E026 S0-A / #213:** **EARNED, 12/12 PASS**, shipped since 0.1.19. Existing stores relocate without canonical schema/identity migration; destination authorization is fresh.
3. **Remote multi-PC use — E026 S0-B/S1 / #213:** **ACTIVE NOW**.

S1 is no longer “each PC writes locally then Git-syncs.” The owner intentionally narrowed the product:

> **One designated user-owned SSH authority host per project is the only project-memory writer. Local copies are verified read replicas. If SSH/authority is unavailable, memory falls back to read-only and all project-memory writes are blocked.**

This restriction is a feature of S1, not a temporary error mode.

## S1 PLATFORM / NETWORK BOUNDARY

- **SSH only**; no GitHub/Bitbucket/cloud/product server requirement.
- private/corporate network assumptions are first-class.
- only explicitly configured user-owned SSH targets participate.
- **Linux authority/workspace hosts only for S1** unless another OS is effectively free to support.
- VS Code desktop UI may be on another OS when Remote-SSH runs the workspace extension on a supported Linux host.
- no peer discovery or mesh topology.
- one designated authority host per project.

VS Code workspace extensions that access workspace files/tools are expected to run where the workspace lives in Remote-SSH; S0-B should make that placement explicit and test packaged behavior.

## CONNECTED / DISCONNECTED CONTRACT

Connected and verified:

```text
read  -> refresh/check authority snapshot -> read verified local replica
write -> guarded operation runs on authority -> verify -> refresh verified replica
```

Authority unavailable, incompatible, or unverifiable:

```text
read  -> last fully verified local replica
write -> BLOCKED before project-memory mutation
```

UI must make this legible as **Offline — read only** / **Local copy may be stale**.

Read-only Query Plane use may continue against the last verified replica under existing local grant/usage rules, but must not imply remote freshness.

If a remote canonical write succeeds and the network fails before local replica refresh, remote state remains truth. Report **remote write succeeded; local refresh pending**, keep the last verified replica for reads with a stale warning, and block further writes until authority state is re-read. Never invent rollback or mutate the stale replica to guess the remote result.

## REMOTE WRITE BOUNDARY

All persistent project-Wiki mutations execute on the designated authority host:

- Remember/source admission;
- Human Knowledge publication/supersession;
- lineage resolution;
- topic/canonical mutations;
- derived maintenance that writes inside the project Wiki.

Use a fixed remote helper/operation allowlist over SSH. Evidence/user payload goes through stdin or framed streams, never interpolated into a remote shell command. No arbitrary remote shell capability is exposed to Agent/model.

Concurrent callers serialize through one host-local remote operation lock plus existing Authority Core writer/integrity guards. This is not a distributed lock protocol.

## STORE / CACHE BOUNDARY

Portable authority/project state, frozen by E026 S0-A:

- `config.json`
- `manifest.jsonl`
- `raw/`
- `provenance.jsonl`
- `topics.json`
- `human-knowledge/`

Portable workflow state as one unit:

- `agent-state.json`

Portable/rebuildable only:

- `agent-wiki/`
- workload/retrieval-shadow telemetry if carried at all

Host-local; never replicate:

- `workspace-opt-in.json`
- Personal Wiki Library catalog/store IDs
- Query/Library grants and Query usage ledger
- UI-selected topic/ack state
- runtime/Python configuration
- SSH target, credentials, keys, agent, known-hosts
- local snapshot/cache metadata
- `.writer.lock`

Replica refresh must materialize into a temporary location, verify full integrity + private permissions, and only then replace/activate the local read replica. Corrupt/truncated/unverified transfers never replace the last good replica.

## AUTHORITY FLOOR — DO NOT WEAKEN FOR REMOTE

- workspace use remains explicit opt-in;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` stays immutable admitted evidence/provenance authority;
- `DERIVED_MEMORY` stays noncanonical/rebuildable;
- `HUMAN_KNOWLEDGE` stays explicit user-owned project knowledge;
- source admission and canonical lineage semantics stay human-gated;
- changed remembered files never silently receive correction/change/dispute/supersession semantics;
- authorization constrains external scope before retrieval/model exposure;
- Personal Wiki external reads remain registered, named-store-only, read-only, separately granted;
- external reads never authorize writes;
- no wrong-scope fallback;
- no silent broad-RAW fallback;
- transport metadata/host identity/credentials never become Wiki evidence or model-visible context.

## OUT OF SCOPE UNTIL REMOTE DOGFOOD EARNS IT

- offline writes;
- writable independent local replicas;
- Git merge/rebase sync semantics;
- automatic conflict resolution;
- peer-to-peer mesh/discovery;
- distributed writer leases across multiple authority hosts;
- background/ambient sync;
- product cloud sync;
- SSHFS/NFS/SMB live store;
- global/personal writable shared store;
- cross-project writes;
- ambient all-project union search;
- portable global identity/entity graph/ontology;
- E023 G2/G3 reopening;
- DB/WAL migration solely for remote support.

## RELEASE / TEST FLOOR

0.1.22 remains the regression floor:

- Python 3.9 bundled core + full Python/core regressions;
- E020 78-case authority/product contract;
- E025 named-store federation safety;
- Query Plane usage/revocation;
- Human Knowledge integrity;
- lineage revalidation;
- normal Extension Host;
- VSIX packaging;
- unpacked packaged-VSIX Extension Host;
- E026 S0-A portability.

New S1 promotion tests must prove:

- existing 0.1.22 store bootstrap to remote authority without canonical migration;
- SSH-only portable allowlist transfer and host-local exclusion;
- source bytes admitted remotely through the existing guarded path;
- authority -> replica identity/byte preservation;
- two clients serialize writes through one authority;
- SSH unavailable => deterministic read-only, zero project-memory mutations;
- post-write replica-refresh failure is recoverable and honestly reported;
- corrupt transfer never replaces last verified replica;
- packaged Remote-SSH/workspace-host execution is viable.

## FAST POINTERS

- owner issue: **#213**
- active contract: `experiments/E026-ssh-store-portability/README.md`
- local cross-project federation: **#202** / `experiments/E025-cross-workspace-named-store-federation/`
- Query Plane: **#204**
- current release metadata: `dogfood/releases/README.md`
- UX baseline: merged PR **#220** / `docs/product-ux-vnext.md`
- Authority Core readiness: `docs/09-alpha-core-readiness-gate.md`

## NEXT ACTION

1. Make S0-B explicit: classify/package/test LLM Wiki as a workspace-side extension on Linux Remote-SSH style hosts.
2. Build the **SSH remote helper + host-local connection/cache metadata**; no Git dependency for S1.
3. Route project-memory writes through the remote authority while leaving read paths on a verified local replica.
4. Implement authority bootstrap and verified snapshot-stream refresh with temp materialization + integrity check + safe activation.
5. Gate every project-memory write on SSH/helper/authority health; disconnected state is read-only by construction.
6. Add real SSH CI proof using Linux localhost/container SSH plus the existing full regression/package gates.
7. Ship a remote-capable VSIX, then resume broad real-use/UX dogfood on that product.