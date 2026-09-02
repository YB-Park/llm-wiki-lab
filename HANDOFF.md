# Current Handoff

Last updated: 2026-09-02 KST

This file is a **living continuation checkpoint**, not project history. Keep current state, authority boundaries, active evidence questions, and next actions only. Historical rationale belongs in merged commits, PRs, ADRs, experiments, or dedicated design documents. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

Before repo work: re-check `main`, open PRs, #213, E026, relevant current design docs, and active branches.

## NOW

Repository: `YB-Park/llm-wiki-lab`

### Published baseline

- validated/published dogfood: **0.1.22**
- product merge head: `0e727d77a070c2babdfaaad923be01c8a14c0098`
- published release commit: `d5c4de6ecfd003acf97edd42035a0037d9a3fa4c`
- versioned VSIX: `dogfood/releases/llm-wiki-dogfood-0.1.22.vsix`
- stable convenience path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- VSIX SHA-256: `54715451477769cfa1aad8ed85c163e6f648bd6ab612ddbb180f62efdc0f6a02`
- validated main build: GitHub Actions `32688939217`
- PR #220: merged — action-oriented UX
- PR #221: merged — 0.1.22 living handoff
- public Beta: **not declared**

### Active product milestone — remote-capable Personal Wiki

The owner explicitly changed sequencing on 2026-09-02:

> Local-only memory materially suppresses real-use investment. Complete a useful remote/multi-PC capability before another broad satisfaction/UX dogfood cycle.

Therefore **broad UX iteration is paused**. Fix only UX issues that block the remote milestone itself.

The remote architecture has three separate layers; do not conflate them:

1. **Local cross-project federation — E025 / #202:** already implemented as explicit named-store read-only Personal Wiki Library. Independent project stores remain authority boundaries.
2. **Existing-store portability — E026 S0-A / #213:** **EARNED, 12/12 PASS**, shipped since 0.1.19. Existing `.wiki-lab` stores survive relocation without canonical identity/schema migration; destination authorization is fresh.
3. **Multi-PC replication — E026 S0-B/S1 / #213:** **ACTIVE NOW**. This is the current product milestone.

Active branch: `agent/ssh-replication-s1`.

Design/contract: `experiments/E026-ssh-store-portability/README.md`.

## REMOTE TARGET

The first useful remote product journey is:

```text
PC A
  existing project Wiki
  -> Connect Sync Location (user-owned SSH)
  -> Sync Project Memory

PC B
  same/equivalent project checkout
  -> connect same location
  -> pull verified Wiki
  -> explicitly Set Up Project Memory locally
  -> normal Agent questions / Remember / lineage review
  -> Sync Project Memory

PC A
  -> pull fast-forward update
  -> continue normally
```

If both PCs independently changed portable Wiki state, sync must stop safely. S1 does **not** merge or choose a winner.

After replicated project stores exist locally on a host, the already-implemented Personal Wiki Library may register them for explicit read-only cross-project consultation. Do not create one global writable Wiki merely to support multi-project use.

## S0-B — FAST REMOTE-HOST COMPATIBILITY GATE

Treat VS Code Remote-SSH execution as engineering compatibility, not a long research program.

Validate:

- LLM Wiki executes on the workspace host when the workspace is remote;
- Python runtime discovery/core commands operate on that host;
- filesystem privacy/integrity checks refer to that host's `.wiki-lab`;
- Agent tools, Query Plane, admission, lineage and Doctor preserve the same workspace-local authority boundary;
- packaging works in a remote Extension Host;
- workspace opt-in remains local to that host/workspace.

VS Code's architecture expects workspace extensions that access workspace files/invoke tools to run where the workspace lives. Make placement explicit if needed; do not mistake Remote-SSH execution for sync.

## S1 — USER-OWNED SSH REPLICATION

Primary transport hypothesis: **Git over explicitly configured user-owned SSH**, used only as byte-preserving transport/version ancestry.

Required first-slice invariants:

- no GitHub/company cloud/product server dependency;
- existing store format carried forward;
- transport Git metadata/remote/credentials stay host-local outside canonical/model-visible Wiki state;
- only the E026 frozen portable allowlist is transported;
- no EOL conversion of RAW or other payload bytes;
- verify local store before publication;
- fetch/ancestry check before push;
- verify pulled candidate before activation;
- destination re-hardens private artifacts;
- destination requires a fresh workspace authority epoch;
- explicit sync only; no background sync yet;
- single-writer/fast-forward only;
- remote divergence fails closed;
- no merge/rebase/semantic conflict resolution;
- SSH host-key verification is never disabled.

Prefer user-facing language such as `Sync Project Memory`, `Connect Sync Location`, `Up to date`, `Newer memory available`, and `Sync conflict — both PCs changed memory`. Git terminology belongs under Technical details.

## AUTHORITY FLOOR — DO NOT WEAKEN FOR SYNC

Non-negotiable current invariants:

- workspace use remains explicit opt-in;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` remains immutable admitted evidence / provenance authority;
- `DERIVED_MEMORY` remains noncanonical/rebuildable;
- `HUMAN_KNOWLEDGE` remains explicit user-owned project knowledge;
- source admission and canonical lineage semantics remain human-gated;
- changed remembered files never silently get correction/change/dispute/supersession semantics;
- authorization constrains external scope before retrieval/model exposure;
- Personal Wiki external project reads remain explicitly registered, named-store-only, read-only and separately granted;
- external reads never authorize writes;
- no wrong-scope fallback;
- no silent broad-RAW fallback;
- transport metadata/host identity/credentials never become Wiki evidence or model-visible context.

## PORTABLE VS HOST-LOCAL STATE

Frozen by E026 S0-A unless new deterministic evidence proves otherwise.

Portable authority/project state:

- `config.json`
- `manifest.jsonl`
- `raw/`
- `provenance.jsonl`
- `topics.json`
- `human-knowledge/`

Portable workflow as one unit, never semantic-merge:

- `agent-state.json`

Portable/rebuildable:

- `agent-wiki/`
- local workload/retrieval-shadow telemetry may be carried but is never authority

Host-local; do not replicate:

- `workspace-opt-in.json`
- Personal Wiki Library catalog/store IDs
- Query/Library grants
- Query usage ledger
- UI-selected topic/ack state
- Python/runtime settings
- SSH/Git remote, credentials, known-hosts, transport revision state
- `.writer.lock`

## OUT OF SCOPE UNTIL S1 DOGFOOD EARNS IT

- concurrent multi-writer collaboration;
- distributed writer locks/leases;
- automatic conflict resolution or Git merge/rebase;
- ambient/background sync;
- automatic peer discovery;
- live shared `.wiki-lab` over SSHFS/NFS/SMB;
- product-operated cloud sync;
- portable global writable store;
- cross-project writes;
- ambient all-project union search;
- portable global identity / entity graph / ontology;
- E023 G2/G3 reopening;
- DB/WAL migration solely for sync.

## UX STATE

0.1.22's U0-U4 changes remain the current baseline. They are not rolled back, but broad satisfaction dogfood is postponed until remote usefulness exists.

Do not spend the next cycle polishing a host-bound product unless a UX blocker prevents remote setup/sync/recovery.

## RELEASE / VALIDATION BASELINE

0.1.22 release gate is complete and remains the regression floor:

- Python 3.9 bundled core;
- full Python/core regressions;
- E020 78-case authority/product contract;
- E025 named-store federation safety;
- Query Plane usage/revocation;
- Human Knowledge integrity;
- lineage revalidation;
- normal Extension Host;
- VSIX packaging;
- unpacked packaged-VSIX Extension Host.

E026 S0-A portability must remain green throughout S1.

## FAST POINTERS

- remote/replication owner issue: **#213**
- E026 portability + active S1 contract: `experiments/E026-ssh-store-portability/README.md`
- local cross-project federation: **#202** / `experiments/E025-cross-workspace-named-store-federation/`
- current release metadata: `dogfood/releases/README.md`
- Query Plane: **#204**
- action-oriented UX: merged PR **#220** / `docs/product-ux-vnext.md`
- autonomy/UX philosophy: `docs/12-autonomy-ux-philosophy.md`
- Authority Core readiness: `docs/09-alpha-core-readiness-gate.md`

## NEXT ACTION

1. Implement/validate the short **S0-B workspace-host execution contract**; explicitly classify the extension as workspace-side if necessary.
2. Implement **S1 user-owned SSH replication** with a host-local Git transport layer and frozen portable allowlist.
3. Add deterministic transport tests: exact bytes, host-local exclusion, A -> B -> A fast-forward round trip, divergence fail-closed, permission re-hardening, existing-store carry-forward.
4. Add a real SSH transport CI proof (localhost/container SSH is acceptable for transport mechanics; it does not replace later Windows/Linux installed evidence).
5. Ship a remote-capable dogfood VSIX only after the full existing regression/package gates remain green.
6. Then perform the next broad real-use/UX dogfood on the remote-capable product and let that evidence choose subsequent UX/reconciliation work.
