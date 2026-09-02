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

Active draft PR: **#222 — S1: remote-authoritative Personal Wiki over SSH**.

Active milestone: **remote-capable Personal Wiki before another broad satisfaction/UX dogfood cycle**.

The owner treats local-only memory as a real-use suppressor. Broad UX polishing is paused except where it blocks remote setup/use/recovery.

## REMOTE ARCHITECTURE — CURRENT DECISION

The previous “one authority host per project / equivalent checkout” framing is superseded.

The product model is now:

- one explicitly configured **Personal Wiki SSH authority location** may hold many independent project stores;
- every local workspace is an independent project instance by default;
- project identity is an opaque store identity, never inferred from Git repo/path/content;
- two unrelated projects share the same Personal Wiki through read-only cross-project access;
- two clones/checkouts of the same repository are also **different projects by default**;
- a workspace writes only its own current project store;
- other project stores remain named-store-only/read-only through the existing Personal Wiki Library authority model.

Example:

```text
Personal Wiki SSH authority
├─ project-store-A  <- PC A / z
├─ project-store-B  <- PC B / y
└─ project-store-C  <- PC B / z clone (still separate)
```

Do not infer project sameness from repository URL, branch, commit, directory name, workspace path, or content similarity.

## S1 NETWORK / PLATFORM BOUNDARY

- **SSH only**; no GitHub/Bitbucket/cloud/product server requirement.
- private/corporate network assumptions are first-class.
- one user-owned Personal Wiki SSH authority may serve many project stores.
- **Linux authority/workspace hosts only for S1** unless another OS is effectively free to support.
- VS Code desktop UI may be on another OS when Remote-SSH runs the workspace extension on a supported Linux host.
- no peer discovery or mesh topology.
- OpenSSH-compatible **non-interactive** access only; existing SSH config/key/agent/proxy/jump/known-hosts are used.
- LLM Wiki does not manage passwords, keys, or interactive SSH authentication.

## CONNECTED / DISCONNECTED CONTRACT

For this workspace's exact current project store:

```text
Connected + verified
  read  -> refresh/check remote snapshot -> read verified local replica
  write -> guarded operation runs on exact remote current store -> verify -> refresh replica

Authority unavailable/incompatible/unverified
  read  -> last fully verified local replica
  write -> BLOCKED before Project Memory mutation
```

Other project memories:

```text
Connected
  -> explicit named-store read-only access

Offline
  -> last verified cached external replica may be read if present
  -> never writable
```

UI must make disconnected state legible as **Offline — read only** / **Local copy may be stale**.

If a remote canonical write succeeds and the network fails before local replica refresh, remote state remains truth. Report **remote write succeeded; local refresh pending**, keep the last verified replica for stale-marked reads, and block further writes until authority state is re-read. Never invent rollback.

## PROJECT IDENTITY / BOOTSTRAP

On first connection, a workspace receives a **new opaque remote project-store ID**.

For an existing local `.wiki-lab`:

1. verify local integrity/S0-A portability;
2. create a new remote project store;
3. never search for an existing store based on Git/path/content similarity;
4. transfer only the frozen portable payload;
5. verify remote state;
6. keep the local copy as the first verified read replica.

A future explicit attach/migration-to-existing-store flow is outside S1 unless installed evidence requires it. There is no automatic same-repository linking.

## SHARED PERSONAL WIKI / CROSS-PROJECT RULE

The Personal Wiki authority can contain many independent project stores and expose them for user-controlled registration/display.

Existing E025/#202 principles remain the floor:

- current project store is the only writable project scope for this workspace;
- other stores are explicit, named-store-only and read-only;
- authorization occurs before retrieval/model exposure;
- wrong/unknown/ambiguous scope fails closed;
- external reads never authorize writes;
- no automatic all-project union search in S1;
- no global/personal writable shared store.

Remote catalog identity and local `libstore-*` routing identity remain separate control-plane concepts.

## REMOTE WRITE BOUNDARY

All persistent current-project Wiki mutations execute on the authority host against the exact current project store:

- Remember/source admission;
- Human Knowledge publication/supersession;
- lineage resolution;
- topic/canonical mutations;
- derived maintenance that writes inside the current project Wiki.

Use a fixed remote helper/operation allowlist over SSH. Evidence/user payload goes through stdin/framed streams, never interpolated into remote shell text. No arbitrary remote shell capability is exposed to Agent/model.

## STORE / CACHE BOUNDARY

Portable per-project authority state, frozen by E026 S0-A:

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

Host-local; never replicate as project authority:

- `workspace-opt-in.json`
- local Personal Wiki Library catalog/store IDs
- Query/Library grants and Query usage ledger
- UI-selected topic/ack state
- runtime/Python configuration
- SSH target, credentials, keys, agent, known-hosts
- local snapshot/cache metadata
- `.writer.lock`

The remote authority may keep a host-local Personal Wiki catalog mapping opaque project-store IDs to display names. That catalog is routing/control-plane state, not evidence/model authority.

Replica refresh must materialize into a temporary location, verify full integrity + private permissions, and only then replace/activate the local replica. Corrupt/truncated/unverified transfers never replace the last good replica.

## AUTHORITY FLOOR — DO NOT WEAKEN FOR REMOTE

- workspace use remains explicit opt-in;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` stays immutable admitted evidence/provenance authority;
- `DERIVED_MEMORY` stays noncanonical/rebuildable;
- `HUMAN_KNOWLEDGE` stays explicit user-owned project knowledge;
- source admission and canonical lineage semantics stay human-gated;
- changed remembered files never silently receive correction/change/dispute/supersession semantics;
- authorization constrains external scope before retrieval/model exposure;
- external reads remain registered, named-store-only, read-only, separately granted;
- no wrong-scope fallback;
- no silent broad-RAW fallback;
- transport metadata/host identity/credentials never become Wiki evidence or model-visible context.

## OUT OF SCOPE UNTIL REMOTE DOGFOOD EARNS IT

- repository/path/content-based automatic project identity;
- automatic same-repository linking across machines;
- offline writes;
- writable independent local replicas;
- writing another project's store;
- Git merge/rebase sync semantics;
- automatic conflict resolution;
- peer-to-peer mesh/discovery;
- distributed writer leases across multiple authority hosts;
- background/ambient sync;
- product cloud sync;
- SSHFS/NFS/SMB live store;
- global/personal writable shared store;
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

- unrelated workspaces on different hosts create distinct remote project stores under one Personal Wiki authority;
- same-repository checkouts also create distinct stores by default;
- no Git/path/content identity is used for automatic linking;
- existing 0.1.22 store bootstrap without canonical migration;
- SSH-only portable allowlist transfer and host-local exclusion;
- source bytes admitted remotely through the exact current-store guarded path;
- authority -> replica identity/byte preservation;
- external project reads remain read-only and cannot authorize writes;
- SSH unavailable => deterministic read-only, zero Project Memory mutations;
- post-write replica-refresh failure is recoverable and honestly reported;
- corrupt transfer never replaces last verified replica;
- packaged Remote-SSH/workspace-host execution is viable.

## FAST POINTERS

- owner issue: **#213**
- active PR: **#222**
- active contract: `experiments/E026-ssh-store-portability/README.md`
- local cross-project federation: **#202** / `experiments/E025-cross-workspace-named-store-federation/`
- Query Plane: **#204**
- current release metadata: `dogfood/releases/README.md`
- UX baseline: merged PR **#220** / `docs/product-ux-vnext.md`
- Authority Core readiness: `docs/09-alpha-core-readiness-gate.md`

## NEXT ACTION

1. Make S0-B explicit: classify/package/test LLM Wiki as a workspace-side extension on Linux Remote-SSH style hosts.
2. Build the **SSH Personal Wiki remote helper + remote catalog + host-local connection/cache metadata**; no Git dependency for S1.
3. Create a new opaque remote project-store identity per workspace by default; never infer sameness from repository/path/content.
4. Route current-project writes to that exact remote store while leaving reads on verified local replicas.
5. Expose remote-backed other project stores through existing named-store read-only federation semantics.
6. Implement verified snapshot-stream refresh with temp materialization + integrity check + safe activation.
7. Gate every Project Memory write on SSH/helper/authority/current-store health; disconnected state is read-only by construction.
8. Add real SSH CI proof using Linux localhost/container SSH plus the existing full regression/package gates.
9. Ship a remote-capable VSIX, then resume broad real-use/UX dogfood on that product.