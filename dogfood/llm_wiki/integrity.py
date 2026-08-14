from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .jsonl_log import audit_canonical_logs
from .store import verify_raw_integrity


def audit_alpha_integrity(root: Path) -> dict:
    """Return privacy-minimal aggregate readiness for existing Alpha invariants.

    This audit is read-only. It never repairs, truncates, quarantines, or invents
    canonical state. Raw integrity depends on a replayable manifest; when the
    manifest itself is damaged we report raw as not checked rather than guessing
    at source identity from a partial prefix.
    """
    initialized = (
        (root / "config.json").is_file()
        and (root / "raw").is_dir()
        and (root / "manifest.jsonl").is_file()
    )
    canonical = audit_canonical_logs(root)

    if not initialized:
        raw: dict = {"status": "not_checked_uninitialized", "ok": False}
    elif not canonical.manifest.ok:
        raw = {"status": "not_checked_manifest_damaged", "ok": False}
    else:
        try:
            report = verify_raw_integrity(root)
        except (RuntimeError, ValueError, KeyError, TypeError, UnicodeError, OSError):
            raw = {"status": "audit_failed", "ok": False}
        else:
            raw = {
                "status": "clean" if report.ok else "failed",
                **asdict(report),
            }

    return {
        "format": "LLM-WIKI-ALPHA-INTEGRITY-v0",
        "privacy": "aggregate_only_no_ids_paths_hashes_names_or_content",
        "workspace_initialized": initialized,
        "raw": raw,
        "canonical_logs": asdict(canonical),
        "ok": bool(initialized and raw.get("ok") is True and canonical.ok),
    }
