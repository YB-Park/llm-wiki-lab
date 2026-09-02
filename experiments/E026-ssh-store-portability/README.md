# E026 — Existing-store portability and user-owned SSH authority

Status: **S0-A EARNED / S0-B + S1 ACTIVE / ZERO MODEL CALLS REQUIRED FOR TRANSPORT GATES**

Owner requirement: useful Wiki memory must not be trapped on one PC. Remote capability is now a prerequisite for the next broad real-use/UX cycle.

The first remote product is intentionally narrow:

- one explicitly configured **user-owned SSH authority host per project**;
- **Linux-only for S1** unless implementation evidence shows another OS is effectively free;
- SSH is the only required network transport;
- when the authority host is reachable and healthy, project-memory reads/writes use that authority;
- when SSH/authority is unavailable, the last fully verified local replica remains **read-only**;
- no project-memory mutation is allowed while the authority is unavailable or unverified.

This replaces the earlier first-choice Git replication hypothesis. Git may be reconsidered later as backup/version transport, but S1 does not require Git, cloud storage, a product server, peer discovery, or multi-writer merge semantics.

Cross-project federation remains a separate layer owned by E025/#202. Personal Wiki Library may read explicitly registered local replicas; it does not become a global writable store.

## S0-A result — EARNED / shipped in 0.1.19

S0-A already proved that existing stores can cross a host/root boundary without canonical migration:

- 12/12 deterministic cases PASS;
- Python 3.9;
- 0 model calls;
- canonical RAW/source identity survives relocation;
- exact provenance survives relocation;
- topic/temporal history survives relocation;
- Human Knowledge survives with integrity and lineage identity intact;
- pending-lineage/source-locator workflow state survives as workspace-relative state;
- no absolute source-host root is required to replay portable state;
- `workspace-opt-in.json` is intentionally not transported; destination authorization is fresh;
- permission loss can be re-hardened without changing bytes;
- LF/CRLF mutation of content-addressed RAW fails closed;
- no canonical store schema migration was required.

Therefore the existing 0.1.22-era store format is the S1 input format.

## Frozen portable boundary

Portable authority/project state:

- `config.json`
- `manifest.jsonl`
- `raw/`
- `provenance.jsonl`
- `topics.json`
- `human-knowledge/`

Portable workflow state, moved as one state and never text/semantic-merged:

- `agent-state.json`

Portable but rebuildable/non-authoritative:

- `agent-wiki/`
- workload/retrieval-shadow telemetry if carried at all

Host-local; never silently replicated:

- `workspace-opt-in.json`
- Personal Wiki Library catalog / `libstore-*` IDs
- Query/Library grants
- Query usage ledger
- selected-topic / UI acknowledgement state
- Python/runtime configuration
- SSH target, credentials, keys, agent state, known-hosts
- local cache/transport status metadata
- `.writer.lock`

## S0-B — short Remote-SSH compatibility gate

Treat Remote-SSH as engineering compatibility, not a research program.

LLM Wiki accesses workspace files and invokes local Python tooling, so it should be a VS Code **workspace extension**. In a Remote-SSH workspace that means execution on the remote workspace host, consistent with VS Code's extension-host model.

Validate:

- extension placement/execution is on the workspace host;
- Python discovery/core commands run on that host;
- `.wiki-lab` privacy/integrity checks refer to that host filesystem;
- Agent tools, Query Plane, admission, lineage, and Doctor preserve the same authority boundary;
- no UI-client path is mistaken for the remote workspace path;
- packaged VSIX works in a remote Extension Host;
- workspace opt-in stays host/workspace-local.

S0-B does not itself provide multi-PC shared memory.

## S1 — remote-authoritative SSH model

### Core rule

For a connected project, the designated SSH authority host is the **only writer location** for project-memory state.

Each participating workspace host keeps a local, fully verified replica for fast reads and disconnected fallback. That replica is not an independent writer.

```text
SSH authority healthy
  read  -> refresh/check remote snapshot, then read verified replica
  write -> execute guarded mutation on authority host, verify, refresh replica

SSH authority unavailable / incompatible / unverifiable
  read  -> last fully verified local replica, clearly marked read-only/stale-capable
  write -> BLOCKED before project-memory mutation
```

All persistent project-memory mutations follow this rule, including:

- source admission / Remember;
- Human Knowledge publication/supersession;
- lineage resolution;
- topic/canonical mutations;
- derived maintenance that writes inside the project Wiki.

Host-local control-plane changes needed to reconnect/configure SSH are not project-memory mutations and may remain local.

Read-only Query Plane use may continue against the last verified replica under its existing local grant/usage rules, but the UI must make the disconnected/read-only state visible and must not imply freshness.

### Why this simplifies S1

This model deliberately removes the hardest first-release cases:

- no offline writes;
- no A/B independent canonical branches;
- no Git merge/rebase semantics;
- no fast-forward reconciliation protocol between writable replicas;
- no distributed semantic conflict resolution;
- no peer topology/discovery;
- no product-operated coordination service.

Concurrent write requests from several PCs are serialized at the single Linux authority host using a host-local operation lock plus the existing Authority Core writer/integrity guards. That is ordinary single-host serialization, not a distributed lock protocol.

### SSH transport contract

S1 uses OpenSSH-compatible SSH only.

- honor normal SSH config, keys, agent, proxy/jump configuration, and known-hosts policy;
- never disable host-key verification;
- do not persist credentials in `.wiki-lab`;
- remote target/path and cache metadata are host-local and never model-visible;
- invoke only a fixed LLM Wiki remote helper/operation allowlist;
- user/evidence payload travels on stdin or a framed stream, never interpolated into a remote shell command;
- no arbitrary remote shell capability is exposed to the Agent/model.

The authority host runs a small on-demand helper; no always-on daemon is required for S1. The helper uses the existing Python Authority Core rather than reimplementing evidence/lineage semantics.

### Existing local store bootstrap

For the first PC attaching an existing `.wiki-lab`:

1. verify local store integrity and S0-A portability assumptions;
2. require the selected authority location to be empty/uninitialized or an exact known match;
3. transfer only the frozen portable payload;
4. verify the authority copy before marking it active;
5. record SSH/cache configuration outside canonical Wiki state;
6. keep the local copy as the first verified read replica.

A second PC attaches by pulling/verifying the authority snapshot, then explicitly enabling Project Memory under a fresh local workspace authority epoch.

### Write flow

A project-memory write is accepted only when all preconditions are true:

1. SSH connection succeeds;
2. remote helper identity/version is compatible;
3. authority store integrity passes;
4. remote operation lock is acquired;
5. the user-facing guarded operation obtains any existing required human confirmation;
6. the mutation runs on the authority host through the existing Authority Core path;
7. post-write integrity passes;
8. a new portable snapshot identity is computed;
9. the caller refreshes a temporary local replica, verifies it, then activates it atomically/best-effort safely;
10. the remote operation lock is released.

If failure happens **before remote canonical mutation**, the write has not happened.

If transport fails **after a successful remote canonical mutation**, the remote authority remains truth; the local client must report `write committed remotely; local replica refresh pending`, disable further local write UI until it can re-read authority state, and keep reads on the last verified local replica with an explicit stale warning. It must never invent a rollback or mutate the stale replica to guess the remote outcome.

### Replica refresh

Replica transfer must be byte-preserving and allowlist-based.

Preferred first implementation: the remote Python helper emits a deterministic/framed portable snapshot stream over SSH; the receiver materializes into a temporary directory, runs full integrity verification and permission hardening, then replaces/activates the local replica only after success.

Do not use SSHFS/NFS/SMB as the live store. Do not copy host-local grants/credentials/locks.

A transport `snapshot_id` may be computed from the portable file set/hashes and stored only as host-local cache metadata. It is not canonical Wiki identity or evidence.

## First useful journey

```text
Linux authority host
  owns canonical project Wiki

PC A / workspace host
  existing .wiki-lab
  -> Connect Remote Memory
  -> bootstrap verified store to authority
  -> local becomes verified replica
  -> Remember / lineage / HK writes execute remotely

PC B / workspace host
  -> Connect same Remote Memory
  -> pull + verify replica
  -> Set Up Project Memory locally
  -> normal Agent reads
  -> writes execute on the same authority host

network/SSH unavailable on either PC
  -> last verified memory remains readable
  -> all project-memory writes are disabled
```

## Product UX target

User-facing concepts:

- **Remote Project Memory**
- **Connect Remote Memory**
- **Connected — read/write**
- **Offline — read only**
- **Refreshing memory…**
- **Local copy may be stale**
- **Remote write succeeded; local refresh pending**
- **Technical details** for host/helper/snapshot diagnostics

Do not teach Git branches, merge, rebase, distributed locking, or replica ancestry because S1 no longer uses them as the product model.

## S1 platform boundary

For S1, support **Linux authority/workspace hosts only**. This is a deliberate complexity constraint, not a claim that the core can never support Windows/macOS.

A desktop UI client may itself run another OS when VS Code Remote-SSH places the workspace extension on a supported Linux host, but local-workspace S1 support is only claimed where the workspace host is Linux.

Later cross-platform widening requires explicit transport/private-filesystem evidence; it must not delay the first useful remote product.

## Cannot earn in S0-B/S1

- offline writes;
- writable local replicas;
- automatic conflict resolution;
- Git merge/rebase sync semantics;
- peer-to-peer mesh sync or discovery;
- distributed writer leases across multiple authority hosts;
- background/ambient sync;
- product-operated cloud sync;
- live shared `.wiki-lab` over SSHFS/NFS/SMB;
- portable Personal Wiki Library routing identity;
- global/personal writable shared store;
- cross-project writes;
- ambient library-wide union search;
- G2/G3 reopening;
- DB/WAL migration solely for remote support;
- model-backed sync/transport decisions.

## Promotion gate

Promote S1 to installed dogfood only when packaged-product tests prove:

- existing 0.1.22 stores bootstrap to the authority without canonical schema/identity migration;
- only the frozen portable allowlist crosses SSH;
- host-local grants/credentials/opt-in are absent from remote/replica payloads;
- source/HK/provenance/temporal identities survive authority -> replica transfer exactly;
- source bytes sent from a workspace can be admitted remotely through the existing guarded path;
- two independent clients can serialize writes through one authority without semantic merge;
- SSH unavailable => deterministic read-only mode and zero project-memory mutations;
- remote write success + replica-refresh failure is reported safely and recovers by re-pull;
- corrupt/truncated/unverified snapshots never replace the last verified replica;
- S0-A, Authority Core, E025 federation, Query Plane, Human Knowledge, lineage, packaging, and Extension Host gates stay green.

After this remote-capable VSIX ships, resume broad real-use/UX dogfood against that product.