# E026 — Existing-store portability before SSH sync

Status: **S0-A PREREGISTERED / ZERO MODEL CALLS / NO SYNC RUNTIME**

Owner requirement: future remote/multi-PC support must carry forward an existing 0.1.18 local Wiki. A user who accumulates useful memory during installed dogfood must not have to recreate canonical knowledge when a user-owned SSH transport is added later.

This experiment is deliberately narrower than sync. It asks only:

> Can the current 0.1.18 store move to a different absolute root / host boundary without changing canonical identity, while host-local authority is re-established rather than silently copied?

## Environment assumption

Do not assume a generic public-cloud network.

- Corporate/private networks may have unusual proxy, certificate, port, and software restrictions.
- At least one user-controlled Windows or Linux host may be reachable by SSH.
- Only explicitly configured user-owned/approved SSH endpoints are in scope.
- GitHub, Bitbucket, company-managed remotes, cloud buckets, peer discovery, and product-operated servers are not prerequisites.

## Frozen S0-A boundary

S0-A is zero-model and does **not** implement transport.

It validates:

1. canonical RAW/source identity survives relocation;
2. exact provenance survives relocation;
3. topic/temporal history survives relocation;
4. Human Knowledge survives relocation with integrity and lineage identity intact;
5. pending-lineage/source-locator workflow state survives as workspace-relative state;
6. derived Agent Wiki notes remain readable but noncanonical;
7. telemetry remains non-authoritative;
8. no absolute source-host root is required to replay portable state;
9. host-local workspace opt-in is intentionally not carried into the transport snapshot;
10. the destination requires a fresh workspace authority epoch;
11. a Git-like permission loss can be re-hardened before normal use;
12. line-ending mutation of content-addressed RAW fails closed rather than silently changing authority.

## Candidate state classification

This classification is part of the experiment and may be revised only by explicit evidence.

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

## Git/SSH implication

Passing S0-A does not earn Git sync.

If Git becomes Sync Provider #1 later, it is only a byte transport/version carrier. The first earned slice must remain:

```text
single writer at a time
pull/verify before use
write locally
verify
commit/push
remote divergence => fail closed
no automatic semantic merge/rebase
```

A Windows/Linux transport must disable working-tree byte transformations for the Wiki payload. In particular, `raw/<sha>.txt` is content-addressed authority; CRLF/LF conversion is corruption, not formatting.

Git file modes also do not preserve the Wiki privacy boundary across platforms, so destination activation must re-harden known private artifacts.

## Cannot earn

S0-A cannot earn or authorize:

- multi-writer replication;
- distributed locks or leases;
- automatic Git merge/rebase of Wiki state;
- cloud/company-managed remotes;
- generic network-share / SSHFS / SMB / NFS live-store safety;
- portable Personal Wiki Library routing identity;
- Personal/global writable memory;
- cross-project writes;
- G2/G3 reopening;
- DB/WAL migration;
- model-backed semantic benchmarks.

## Promotion rule

If the deterministic harness passes, preserve the 0.1.18 store schema and proceed to a separate Remote-SSH host-local validation slice.

If it fails because canonical or workflow identity depends on the old host/root, make only the smallest backward-compatible repair before long dogfood creates migration debt.
