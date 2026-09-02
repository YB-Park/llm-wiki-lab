# E026 — Existing-store portability and remote Personal Wiki authority

Status: **S0-A EARNED / S0-B+S1 CI PROMOTION GATE GREEN / READY FOR INSTALLED REMOTE-SSH DOGFOOD / 0 MODEL CALLS FOR TRANSPORT GATES**

Owner requirement: useful Wiki memory must not be trapped on one PC. Remote capability is a prerequisite for the next broad real-use/UX cycle.

## Exact candidate

Product/code head with full green gates:

`0329ee60efbf50647aa3ba25460b19ee732c0b90`

Evidence:

- E026 S1 real OpenSSH workflow `33614870377`: PASS;
- VS Code Dogfood/package workflow `33614870257`: PASS;
- all PR workflows on the candidate product head: PASS;
- CI artifact ID `9840583064`;
- extracted candidate VSIX: `175623` bytes;
- extracted VSIX SHA-256: `e66e947965794d8c4489cc0105556eb5a4c784a2e8a042c26fc41359625363ff`.

This earns **CI promotion to installed dogfood**, not final installed Remote-SSH support. One actual VS Code Remote-SSH session with a Linux workspace host is still required before S0-B/S1 installed support is declared earned.

## Identity model

The remote unit is **not a Git repository or checkout**.

One explicitly configured user-owned **Personal Wiki SSH authority** may contain many independent project stores. Project identity is one opaque remote `project-*` identity and is never inferred from:

- Git remote/repository/branch/commit;
- absolute or relative workspace path;
- folder/repository name;
- file/content similarity;
- another machine having the same checkout.

Independent stores may therefore have the same display name and identical bytes.

A workspace writes only its exact current remote project store. Other stores remain explicit named-store-only/read-only through the existing E025 Personal Wiki Library boundary.

## S0-A — EARNED / shipped since 0.1.19

Existing `.wiki-lab` stores can cross root/host boundaries without canonical migration:

- 12/12 deterministic cases PASS;
- Python 3.9;
- 0 model calls;
- RAW/source identity, exact provenance, topics/temporal history, Human Knowledge, and workflow identity survive relocation;
- `workspace-opt-in.json` does not travel;
- destination permissions are re-hardened;
- LF/CRLF mutation of content-addressed RAW fails closed;
- no canonical schema migration.

Therefore the existing project-store format remains the store format for remote S1.

## Frozen portable boundary

Portable authority/project state:

- `config.json`
- `manifest.jsonl`
- `raw/`
- `provenance.jsonl`
- `topics.json`
- `human-knowledge/`

Portable workflow state, moved as one unit and never semantic-merged:

- `agent-state.json`

Portable/rebuildable only:

- `agent-wiki/`
- bounded workload/retrieval-shadow telemetry when carried

Host-local only:

- `workspace-opt-in.json`
- local Personal Wiki Library catalog/routing IDs/grants
- Query grants and usage ledger
- selected-topic/UI state
- Python/runtime configuration
- SSH target/config/credentials/keys/agent/known-hosts
- remote binding/cache metadata
- `.writer.lock` rendezvous file

The authority's remote store catalog is host-local routing/control-plane state, not Wiki evidence or model authority.

## S0-B — workspace-host compatibility

LLM Wiki is explicitly packaged as a VS Code **workspace extension**.

CI proves:

- `extensionKind: ["workspace"]` contract;
- Python 3.9 bundled-core compatibility;
- normal Extension Host execution;
- packaged VSIX inventory includes all remote helper/snapshot/attach/replica components;
- unpacked packaged VSIX executes in an Extension Host;
- workspace file/core assumptions remain workspace-host based.

Status: **CI mechanics green; installed VS Code Remote-SSH Linux-workspace evidence pending.**

## S1 — remote-authoritative Personal Wiki

### Connected/current-store contract

```text
SSH authority healthy
  current-store read  -> verified local replica
  current-store write -> guarded operation on exact remote store -> verify -> explicit replica refresh

SSH authority unavailable / incompatible / unverifiable
  current-store read  -> last fully verified local replica
  any Project Memory write -> BLOCKED before mutation
```

All persistent current-project mutations run remotely through a fixed helper/operation allowlist and reuse the existing Authority Core. SSH transports framed/control input and exact snapshot bytes. Git is not required.

If a remote mutation succeeds but replica refresh fails, remote state remains truth; the local copy is stale/read-only and further writes remain blocked until refresh succeeds.

### New project bootstrap

A workspace may choose **Create New Project Memory**:

1. verify local integrity/portability;
2. create one new opaque remote store;
3. never infer/link an existing store;
4. transfer only frozen portable state;
5. verify remote state;
6. keep remote binding/cache metadata host-local;
7. keep the local store as verified replica.

### Explicit existing-store attach

S1 now includes the minimum explicit multi-PC attach required for useful sharing.

A user may choose **Use Existing Project Memory** and explicitly select one exact bootstrapped remote store.

Attach rules:

- local Project Memory must be freshly initialized and empty;
- attach is not a merge and never resolves conflicting local authority;
- unexpected portable state fails closed;
- symlinked root/config/manifest/raw/opt-in/lock entries fail closed;
- a normal `.writer.lock` rendezvous file is allowed for retry;
- the Python attach importer acquires the OS store writer lock;
- under that lock it revalidates the local empty-authority shape;
- the incoming snapshot is fully verified and permission-hardened;
- host-local `workspace-opt-in.json` is preserved;
- portable state is atomically activated;
- the remote binding is published only after successful materialization.

### Real multi-PC mechanics proof

The real OpenSSH CI gate starts an isolated `sshd`, uses public-key auth with `BatchMode=yes` and strict known-host verification, deploys the product helper over SSH, and proves:

```text
PC A -> remote project store A
PC B -> fresh host-local authority epoch
PC B -> explicit attach to exact store A
PC B -> remote evidence write to exact store A
PC A -> explicit refresh sees PC B write
independent store B -> unchanged
```

The same gate proves:

- `model_calls = 0`;
- same bytes do not auto-link project identity;
- CRLF/raw bytes survive exactly;
- host-local workspace authority never crosses transport;
- cross-store write leak is false;
- PC B host-local opt-in survives attach;
- attach importer is writer-locked;
- verified offline replica reads leave the entire replica tree unchanged.

### Cross-project sharing

A connected workspace can explicitly choose another store from the same Personal Wiki.

The product:

1. excludes the exact current remote store;
2. downloads one verified snapshot into private host-local extension storage;
3. derives the cache location from a hashed authority key plus opaque store ID, not a model-visible host string;
4. registers the verified cache through existing E025 `Personal Wiki Library` code;
5. requires the existing separate workspace `Allow Here` grant before use.

Other-project stores remain named-store-only/read-only. Registration never authorizes writes. No automatic all-project union search or cross-project maintenance exists.

## SSH / security contract

- user-owned SSH authority only;
- Linux authority/workspace hosts for S1;
- non-interactive OpenSSH-compatible access;
- honor user's SSH config/key/agent/proxy/jump/known-hosts policy;
- never disable host-key verification;
- no password/key management by LLM Wiki;
- credentials/target/host identity stay outside `.wiki-lab` and outside model-visible evidence;
- fixed helper/operation allowlist only;
- evidence/user payload is never interpolated into remote shell text;
- no arbitrary model/Agent shell capability;
- no always-on daemon required.

## Failure semantics

- failure before remote canonical mutation => no Project Memory write occurred;
- remote mutation succeeded, refresh failed => remote remains truth; local replica becomes stale/read-only until successful refresh;
- corrupt/truncated/unverified snapshot => last verified replica remains active;
- non-empty/unexpected/symlinked/busy attach destination => fail closed;
- no fabricated rollback, merge, rebase, automatic conflict resolution, or offline write queue.

## Cannot be claimed by S1

- repository/path/content-based automatic project identity;
- automatic same-repository linking;
- offline writes / writable independent replicas;
- cross-project writes;
- Git merge/rebase sync semantics;
- background/ambient sync;
- peer mesh/discovery;
- distributed writer leases across multiple authorities;
- product cloud sync;
- live SSHFS/NFS/SMB `.wiki-lab`;
- global/personal writable store;
- ambient library-wide union search;
- E023 G2/G3 reopening;
- DB/WAL migration solely for remote;
- model-backed transport/sync decisions.

## Promotion state

### Earned now

- S0-A existing-store portability;
- deterministic remote helper/store/snapshot boundaries;
- real OpenSSH transport mechanics;
- exact opaque current-store write isolation;
- explicit PC B attach to exact existing store;
- writer-locked/atomic attach materialization;
- A -> B write -> A refresh visibility;
- verified offline read-only replica behavior;
- remote other-project cache into existing named-store federation;
- Python 3.9 bundled core;
- workspace-extension packaging contract;
- package inventory and unpacked Extension Host gate;
- full existing regression floor on candidate code head.

### Still required to earn installed S0-B/S1

Exercise the exact candidate VSIX in one actual **VS Code Remote-SSH session with a Linux workspace host** and record:

1. extension runs on workspace host;
2. Project Memory setup/Doctor use the remote workspace filesystem/runtime correctly;
3. create-new remote current store works;
4. explicit attach to an existing remote store works on a fresh local memory;
5. evidence write on attached PC is visible after refresh on the first PC/workspace;
6. another remote project registers/read-only through Other Project Memories and requires the separate workspace grant;
7. authority disconnect leaves stale verified reads but blocks every Project Memory write;
8. reconnect/refresh restores writable state without identity change.

If this installed pass succeeds without semantic changes, mark S0-B/S1 installed gate **EARNED**, move PR #222 out of draft, merge after final unchanged-code gates, package the next dogfood release, then resume broad UX dogfood.
