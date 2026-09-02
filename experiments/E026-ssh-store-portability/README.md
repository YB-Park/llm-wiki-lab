# E026 — Existing-store portability and user-owned SSH replication

Status: **S0-A EARNED / S0-B + S1 ACTIVE / ZERO MODEL CALLS REQUIRED FOR TRANSPORT GATES**

Owner requirement: useful local Wiki memory must remain worth accumulating before remote support exists. Existing `.wiki-lab` data must carry forward unchanged into any remote/multi-PC product slice.

The remote track has two distinct product questions:

1. **S0-B — remote-host execution:** does the extension/core behave correctly when the workspace itself lives on a VS Code Remote host?
2. **S1 — replication:** can one project Wiki move between explicitly configured user-owned SSH-reachable PCs without weakening authority semantics?

Cross-project read-only federation is a separate layer owned by E025/#202 and is already present in the product. Replication should make independent project stores available on more than one host; Personal Wiki Library can then compose explicitly registered local replicas without creating a global writable store.

## S0-A result — EARNED / shipped in 0.1.19

S0-A validated the existing-store portability boundary before transport code:

- 12/12 deterministic cases PASS;
- Python 3.9;
- 0 model calls;
- canonical RAW/source identity survives relocation;
- exact provenance survives relocation;
- topic/temporal history survives relocation;
- Human Knowledge survives with integrity and lineage identity intact;
- pending-lineage/source-locator workflow state survives as workspace-relative state;
- no absolute source-host root is required to replay portable state;
- `workspace-opt-in.json` is intentionally not transported and the destination requires a fresh authority epoch;
- Git-like permission loss is re-hardened without byte changes;
- LF/CRLF mutation of content-addressed RAW fails closed;
- no canonical store schema migration was required.

Therefore **the existing store format is the S1 input format**. Do not create a new canonical schema merely to add transport.

## Frozen state classification

### Portable authority / project state

- `config.json`
- `manifest.jsonl`
- `raw/`
- `provenance.jsonl`
- `topics.json`
- `human-knowledge/`

### Portable workflow state — move as a unit, never auto-merge semantically

- `agent-state.json`
  - pending lineage
  - source locators
  - maintenance usage

### Portable but rebuildable / non-authoritative

- `agent-wiki/`
- `workload-events.jsonl`
- `retrieval-shadow-events.jsonl`

### Host-local authority/runtime — do not silently replicate

- `workspace-opt-in.json`
- Personal Wiki Library catalog / `libstore-*` routing IDs
- Query Reasoning and Personal Wiki Library grants
- selected-topic and maintenance-ack UI state
- Query Plane usage ledger
- configured Python/runtime paths
- SSH/Git remotes, credentials, keys, agent state, known-hosts

### Ephemeral

- `.writer.lock`

## S0-B — remote-host compatibility gate

Treat this as engineering compatibility, not a new research program.

Validate that LLM Wiki is a **workspace-side extension** when a workspace is remote, because it directly accesses workspace files and invokes the Python core/tooling on the workspace host.

Minimum checks:

- extension placement/execution is on the workspace host for Remote-SSH style use;
- Python runtime discovery runs on that host;
- `.wiki-lab` privacy/integrity checks apply to that host filesystem;
- Agent tools, Query Plane authorization, source admission, lineage and Doctor still use the same local-to-workspace authority boundary;
- no local-client path is accidentally treated as the remote workspace path;
- package/install behavior remains valid in a remote Extension Host;
- explicit workspace opt-in remains host/workspace-local.

S0-B cannot claim replication.

## S1 — user-owned SSH replication

The first product transport is intentionally conservative.

```text
explicit sync action
  -> verify local store
  -> fetch remote transport state
  -> require fast-forward / known-parent relation
  -> if pulling: materialize candidate -> verify -> apply under local writer exclusion
  -> if pushing: snapshot allowed portable payload -> verify -> commit -> push
  -> divergence => stop and explain; never merge/rebase automatically
```

### Transport provider hypothesis

Evaluate **Git over user-owned SSH** first because it provides immutable versions, ancestry and fast-forward checks without requiring a product server.

Git is only a transport/version carrier. It does not define Wiki truth, canonical event order, or conflict semantics.

Preferred implementation shape:

- transport Git metadata lives in a **host-local directory outside `.wiki-lab`**;
- `.wiki-lab` or a byte-exact staging mirror is the transport work tree;
- remote URL, credentials, SSH configuration and last-seen transport revision remain host-local;
- only the frozen portable allowlist is tracked;
- byte conversion is disabled (`core.autocrlf=false` or stronger equivalent) and transport tests prove exact RAW bytes survive checkout/materialization;
- destination private permissions are re-hardened before normal use;
- SSH host-key verification follows the user's existing SSH policy and is never disabled.

Do not place a credential-bearing `.git` directory or remote URL inside canonical/model-visible Wiki state.

### Single-writer / fast-forward contract

First S1 supports **one writer lineage at a time**, not concurrent collaboration.

Required behavior:

1. a local host knows the last remote transport revision it successfully materialized/published;
2. before push, fetch remote and require remote HEAD to equal that known revision;
3. before pull, refuse to overwrite unsynced local portable changes;
4. after pull candidate materialization, run full store integrity verification before activation;
5. after push snapshot creation, verify the exact payload before publication;
6. remote advancement plus local unsynced changes is **divergence**;
7. divergence fails closed with no merge, rebase, winner selection, or semantic inference;
8. sync never copies host-local grants/opt-in/credentials;
9. the destination explicitly enables Project Memory under a fresh authority epoch.

### First useful end-to-end scenario

```text
PC A
  existing project + existing .wiki-lab
  configure user-owned SSH remote
  Sync -> publish verified snapshot

PC B
  same/equivalent project checkout
  attach same remote
  Sync -> pull verified snapshot
  Set Up Project Memory locally
  ask / remember / resolve changes normally
  Sync -> publish new verified snapshot

PC A
  Sync -> fast-forward pull
  continue normally
```

A deliberately created A/B divergence must stop safely and preserve both local histories for manual recovery. Automatic reconciliation is not part of S1.

## S1 product UX target

Do not expose Git mechanics as the user's mental model.

Preferred user language:

- **Sync Project Memory**
- **Connect Sync Location**
- **Up to date**
- **Changes on this PC**
- **Newer memory available**
- **Sync conflict — both PCs changed memory**
- **Technical details** for Git revision/remote diagnostics

The normal user should not need to understand branch names, rebase, remotes, object IDs, or transport commits.

## Cannot earn in S0-B/S1

- multi-writer semantic merge;
- distributed writer locks/leases across hosts;
- automatic Git merge/rebase of Wiki state;
- background/ambient sync;
- peer discovery;
- product-operated cloud sync service;
- generic SSHFS/NFS/SMB live-store safety;
- portable Personal Wiki Library routing identity;
- Personal/global writable memory;
- cross-project writes;
- ambient library-wide union search;
- G2/G3 reopening;
- DB/WAL migration;
- model-backed sync decisions.

## Promotion rule

Promote S1 to installed dogfood only when a packaged VSIX proves:

- existing 0.1.22-era stores can be published without canonical byte/schema migration;
- a second isolated host/root can pull and verify the same identities;
- host-local authority is absent from transported payload;
- exact bytes survive the Git/SSH transport path;
- A -> B -> A fast-forward round trip succeeds;
- independent A/B writes cause deterministic fail-closed divergence;
- ordinary Authority Core, E025 federation, Query Plane, Human Knowledge and lineage gates remain green.

After S1 is usable, resume broad real-use/UX dogfood against the **remote-capable** product rather than spending the next iteration polishing a host-bound baseline.
