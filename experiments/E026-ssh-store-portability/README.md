# E026 — Existing-store portability and remote Personal Wiki authority

Status: **S0-A EARNED / S0-B + S1 ACTIVE / ZERO MODEL CALLS REQUIRED FOR TRANSPORT GATES**

Owner requirement: useful Wiki memory must not be trapped on one PC. Remote capability is a prerequisite for the next broad real-use/UX cycle.

## S1 identity correction

The remote unit is **not a Git repository and not a project checkout**.

A user has one explicitly configured **Personal Wiki SSH authority location**. That authority may contain many independent project stores.

Each local workspace is a project instance. On first connection it gets its own opaque remote project-store identity unless the user later invokes an explicit migration/attachment flow. Project identity is never inferred from:

- Git remote URL;
- repository name;
- repository commit/history;
- absolute or relative workspace path;
- file/content similarity;
- another machine having the same checkout.

Therefore these are independent by default:

```text
PC A / workspace z      -> project-store-A
PC B / workspace y      -> project-store-B
PC B / another z clone  -> project-store-C
```

Even when `z` and `z clone` are the same Git repository, they are distinct LLM Wiki projects unless a future explicit user action says otherwise.

What is shared is the **Personal Wiki authority/catalog and read access across its independent project stores**. A workspace writes only its own current project store. Other project stores remain read-only under the existing named-store/federation authority rules.

This replaces the earlier mistaken “one SSH authority host per project / equivalent checkout” framing.

## S1 environment boundary

The first remote product is intentionally narrow:

- one explicitly configured **user-owned Personal Wiki SSH authority** may serve many project stores;
- **Linux-only for S1** unless another OS is effectively free to support;
- SSH is the only required network transport;
- private/corporate-network use is the primary environment;
- no GitHub/Bitbucket/cloud/product-operated server dependency;
- no peer discovery or mesh;
- OpenSSH-compatible non-interactive access only; existing SSH config/keys/agent/jump/proxy/known-hosts are honored;
- LLM Wiki does not manage passwords, keys, or interactive SSH authentication.

When the authority is reachable and healthy, current-project writes execute on the authority. When SSH/authority is unavailable, the last fully verified local replicas remain **read-only** and every Project Memory write is blocked.

Git is not required for S1. SSH itself carries fixed helper operations, payloads, and verified snapshot streams.

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

Therefore the existing 0.1.22-era store format remains the per-project store format under the remote Personal Wiki authority.

## Frozen per-project portable boundary

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

Host-local; never silently replicated as project authority:

- `workspace-opt-in.json`
- local Personal Wiki Library routing IDs/grants
- Query/Library grants and Query usage ledger
- selected-topic / UI acknowledgement state
- Python/runtime configuration
- SSH target, credentials, keys, agent state, known-hosts
- local cache/transport status metadata
- `.writer.lock`

The remote authority may maintain a **host-local Personal Wiki catalog** mapping opaque remote project-store IDs to user-facing display names. That catalog is routing/control-plane state, not Wiki evidence, and is never exposed to the model as authority.

## S0-B — short Remote-SSH compatibility gate

Treat VS Code Remote-SSH as engineering compatibility, not the sharing mechanism.

LLM Wiki accesses workspace files and invokes Python tooling, so it should be a VS Code **workspace extension**. In a Remote-SSH workspace that means execution on the remote workspace host.

Validate:

- extension placement/execution is on the workspace host;
- Python discovery/core commands run on that host;
- `.wiki-lab` privacy/integrity checks refer to that host filesystem;
- Agent tools, Query Plane, admission, lineage, and Doctor preserve the same authority boundary;
- no UI-client path is mistaken for the remote workspace path;
- packaged VSIX works in a remote Extension Host;
- workspace opt-in stays host/workspace-local.

S0-B does not itself provide Personal Wiki sharing.

## S1 — remote-authoritative Personal Wiki model

### Core rule

For a connected workspace, its designated remote project store under the Personal Wiki authority is the **only writer location** for that workspace's Project Memory.

Each workspace host keeps a local, fully verified replica of its current project store. It may also cache verified read-only replicas of other Personal Wiki project stores used through federation.

```text
SSH authority healthy
  current-store read  -> refresh/check remote snapshot -> read verified replica
  current-store write -> guarded mutation on that remote project store -> verify -> refresh replica
  other-store read    -> explicit named-store read-only access

SSH authority unavailable / incompatible / unverifiable
  current-store read  -> last fully verified local replica
  other-store read    -> last verified cached replicas if present
  any Project Memory write -> BLOCKED before mutation
```

No local workspace may write another project store. External project reads never authorize external writes.

### Project-store creation / bootstrap

For a workspace connecting an existing local `.wiki-lab`:

1. verify local store integrity and S0-A portability assumptions;
2. create a **new opaque remote project-store ID** under the Personal Wiki authority;
3. never search for or infer an existing store from Git/path/content identity;
4. transfer only the frozen portable payload;
5. verify the remote project store before activation;
6. record connection/cache metadata outside canonical Wiki state;
7. keep the local copy as the first verified read replica.

For a new workspace without prior Wiki state, create a new empty remote project store after explicit setup.

A future explicit “attach/migrate to existing project store” operation is out of S1 unless installed evidence proves it necessary. There is no automatic same-repository linking.

### Cross-project sharing

The Personal Wiki authority can enumerate its project stores for user-controlled registration/display. The existing E025/#202 principles still apply:

- current project store is writable only through its own guarded path;
- other project stores are explicitly named and read-only;
- authorization happens before retrieval/model exposure;
- wrong/unknown/ambiguous scope fails closed;
- there is no automatic all-project union search in S1;
- there is no global writable memory store.

A local Personal Wiki Library entry may point at a verified remote-backed replica. Remote catalog identity and local `libstore-*` routing identity remain separate control-plane concepts.

### Remote write boundary

All persistent current-project Wiki mutations execute on the authority host:

- Remember/source admission;
- Human Knowledge publication/supersession;
- lineage resolution;
- topic/canonical mutations;
- derived maintenance that writes inside the current project Wiki.

Host-local control-plane changes needed to reconnect/configure SSH are not Project Memory writes.

Read-only Query Plane use may continue against the last verified replica under existing local grant/usage rules, but disconnected reads must not imply freshness.

### SSH transport contract

S1 uses OpenSSH-compatible SSH only.

- non-interactive SSH must already work through the user's existing config/key/agent setup;
- honor proxy/jump and known-hosts policy;
- never disable host-key verification;
- do not persist credentials in `.wiki-lab`;
- remote target/path and cache metadata are host-local and never model-visible;
- invoke only a fixed LLM Wiki remote helper/operation allowlist;
- user/evidence payload travels on stdin or a framed stream, never interpolated into remote shell text;
- no arbitrary remote shell capability is exposed to the Agent/model;
- no always-on daemon is required for S1.

The remote helper uses the existing Python Authority Core rather than reimplementing evidence/lineage semantics.

### Failure semantics

A project-memory write is accepted only after SSH/helper/authority/current-store verification succeeds.

If failure happens **before remote canonical mutation**, the write has not happened.

If transport fails **after a successful remote canonical mutation**, the remote project store remains truth. Report `write committed remotely; local replica refresh pending`, keep the last verified replica for stale-marked reads, and block further writes from that workspace until authority state is re-read. Never invent rollback.

### Replica refresh

Replica transfer is byte-preserving and allowlist-based.

The remote helper emits a deterministic/framed portable snapshot stream for one exact project-store ID. The receiver materializes into a temporary directory, runs full integrity verification and permission hardening, then replaces/activates the local replica only after success.

Corrupt/truncated/unverified transfers never replace the last verified replica. Do not use SSHFS/NFS/SMB as the live store.

## First useful journey

```text
Linux Personal Wiki authority
  project-store-A  <- PC A / z
  project-store-B  <- PC B / y
  project-store-C  <- PC B / z clone (still separate)

PC A / z
  -> Connect Personal Wiki
  -> bootstrap/create project-store-A
  -> writes go only to A
  -> may explicitly read B/C as other project memories

PC B / y
  -> Connect same Personal Wiki
  -> bootstrap/create project-store-B
  -> writes go only to B
  -> may explicitly read A/C

network/SSH unavailable
  -> last verified current/external replicas remain readable when cached
  -> all Project Memory writes are disabled
```

## Product UX target

User-facing concepts should prefer:

- **Personal Wiki**
- **Connect Personal Wiki**
- **This project memory**
- **Other project memories**
- **Connected — read/write**
- **Offline — read only**
- **Local copy may be stale**
- **Remote write succeeded; local refresh pending**
- **Technical details** for host/helper/store/snapshot diagnostics

Do not teach Git branches, merge, repo identity, or checkout equivalence because none define project identity.

## S1 platform boundary

For S1, support **Linux authority/workspace hosts only**. A desktop UI client may itself run another OS when VS Code Remote-SSH places the workspace extension on a supported Linux host.

Later cross-platform widening requires explicit transport/private-filesystem evidence; it must not delay the first useful remote product.

## Cannot earn in S0-B/S1

- repository/path/content-based automatic project identity;
- automatic same-repository linking across machines;
- offline writes;
- writable independent local replicas;
- writing another project's store;
- automatic conflict resolution;
- Git merge/rebase sync semantics;
- peer-to-peer mesh/discovery;
- distributed writer leases across multiple authority hosts;
- background/ambient sync;
- product-operated cloud sync;
- live shared `.wiki-lab` over SSHFS/NFS/SMB;
- global/personal writable shared store;
- ambient library-wide union search;
- G2/G3 reopening;
- DB/WAL migration solely for remote support;
- model-backed sync/transport decisions.

## Promotion gate

Promote S1 to installed dogfood only when packaged-product tests prove:

- two unrelated workspaces on different hosts create distinct remote project stores under one Personal Wiki authority;
- two checkouts of the same repository also create distinct stores by default;
- no Git/path/content identity is used for automatic store linking;
- existing 0.1.22 stores bootstrap without canonical schema/identity migration;
- only the frozen portable allowlist crosses SSH;
- host-local grants/credentials/opt-in are absent from remote/replica payloads;
- source/HK/provenance/temporal identities survive authority -> replica transfer exactly;
- source bytes from a workspace are admitted remotely through the existing guarded path into that workspace's exact current project store;
- external project reads remain named-store-only/read-only and cannot authorize writes;
- SSH unavailable => deterministic read-only mode and zero Project Memory mutations;
- remote write success + replica-refresh failure is reported safely and recovers by re-pull;
- corrupt/truncated/unverified snapshots never replace the last verified replica;
- S0-A, Authority Core, E025 federation, Query Plane, Human Knowledge, lineage, packaging, and Extension Host gates stay green.

After this remote-capable VSIX ships, resume broad real-use/UX dogfood against that product.