# Local Wiki backup and restore — Alpha operating procedure

Status: **current Alpha operating guidance**

The LLM Wiki local store (`.wiki-lab/` by default) is intentionally outside Git and contains private raw evidence, canonical history, provenance, topic metadata, and workload telemetry. Alpha integrity checks can detect many corruption/loss states, but **detection is not backup**.

This procedure is deliberately simple. It does not introduce cloud sync, a database, a recovery daemon, or background uploads.

## Before putting valuable knowledge in the Wiki

Use a backup destination that is permitted for the data you ingest. For company or sensitive material, follow your organization's storage/backup policy; do not copy protected data to a personal cloud account merely because this guide says to make a snapshot.

Treat a snapshot as sensitive: it contains the same private evidence as the live Wiki.

## Safe snapshot

1. Stop LLM Wiki writes. The simplest Alpha procedure is to close the VS Code window/workspace using the Wiki, or otherwise ensure no ingest/update/provenance command is running.
2. Locate the configured Wiki directory (`.wiki-lab/` unless `llmWiki.workspaceDirectory` was changed).
3. Copy the **entire directory as one snapshot** to an approved local/offline backup location. Do not copy only `raw/` or only `manifest.jsonl`; the directory is one operating state.
4. Preserve file contents exactly. Do not edit JSONL files in the snapshot and do not rebuild history from raw filenames.
5. Record enough outside the Wiki to know which workspace/snapshot date the copy belongs to. Do not put secrets into a public repo just to label a backup.

Example on a private local filesystem, while the Wiki is not being written:

```bash
cp -a .wiki-lab "$HOME/private-backups/my-project-wiki-2026-08-15"
```

Use an organization-approved equivalent on Windows/macOS or when `cp -a` is unavailable.

## Restore

1. Stop LLM Wiki writes / close the workspace using the live Wiki.
2. Keep the damaged/current directory aside until the restore has been verified; do not merge individual JSONL prefixes by hand.
3. Copy the chosen **whole snapshot** back to the configured Wiki directory.
4. Open the workspace and run `LLM Wiki: Doctor (Zero Model Calls)`.
5. Do not resume normal ingest/update work unless Doctor reports the local Alpha integrity boundary ready.
6. If Doctor reports torn/corrupt/missing canonical state or missing raw evidence, stop. The Alpha core intentionally does not invent/reconstruct canonical history from surviving content.

Conceptual example:

```bash
mv .wiki-lab .wiki-lab.damaged
cp -a "$HOME/private-backups/my-project-wiki-2026-08-15" .wiki-lab
```

Then run Doctor from VS Code.

## What this protects — and what it does not

This protects against loss of the working directory when a usable snapshot exists. It is **not**:

- live multi-writer backup;
- transactional snapshotting during concurrent writes;
- hostile-tamper detection;
- cloud synchronization;
- automatic retention/rotation;
- a promise that every external source file still exists at its old workspace path.

The immutable raw evidence and canonical history inside the restored snapshot remain the trust floor. VS Code source-location hints are convenience metadata and may need to fall back to the immutable raw snapshot when workspace files moved or changed.

## Alpha recommendation

Until real dogfood establishes a better cadence, make a whole-directory snapshot **before a period of valuable use or any risky local filesystem operation**, and keep at least one known-good snapshot according to the data's security policy.

A future one-click or automatic backup feature should be added only if actual dogfood shows this manual operating procedure is too error-prone or burdensome; it must not quietly weaken the current privacy/integrity boundaries.
