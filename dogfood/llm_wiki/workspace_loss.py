from __future__ import annotations

from pathlib import Path


def has_surviving_raw_files(root: Path) -> bool:
    raw = root / "raw"
    if not raw.is_dir():
        return False
    try:
        return any(child.is_file() for child in raw.iterdir())
    except OSError:
        # Inability to inspect a surviving raw directory is not evidence of a
        # clean first initialization. Fail conservatively at the caller.
        return True


def missing_manifest_is_state_loss(root: Path) -> bool:
    """Whether a missing manifest cannot safely mean a brand-new workspace.

    Normal initialization creates config/manifest before any raw object or exact
    provenance log can exist. Therefore an existing config, surviving raw files,
    or a surviving provenance log makes a missing manifest evidence of prior
    state loss, never an empty new Wiki.
    """
    if (root / "manifest.jsonl").exists():
        return False
    return (
        (root / "config.json").exists()
        or has_surviving_raw_files(root)
        or (root / "provenance.jsonl").exists()
    )
