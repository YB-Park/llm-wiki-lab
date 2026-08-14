from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .jsonl_log import audit_canonical_logs
from .store import verify_raw_integrity


def audit_alpha_integrity(root: Path) -> dict:
    """Return privacy-minimal aggregate readiness for existing Alpha invariants.

    This audit is read-only. It never repairs, truncates, quarantines, or invents
    canonical state. Raw integrity depends on a replayable manifest; when the
    manifest itself is missing or damaged we report raw as not checked rather
    than guessing at source identity from surviving raw files or a partial log.
    """
    config_present = (root / "config.json").is_file()
    raw_dir_present = (root / "raw").is_dir()
    manifest_present = (root / "manifest.jsonl").is_file()
    initialized = config_present and raw_dir_present and manifest_present

    canonical_report = audit_canonical_logs(root)
    canonical = asdict(canonical_report)

    # `config.json` is the durable initialization marker. Once it exists, a
    # missing manifest is canonical-state loss, not a clean empty log.
    if config_present and not manifest_present:
        canonical["manifest"]["status"] = "missing"
        canonical["manifest"]["ok"] = False
        canonical["ok"] = False
        raw: dict = {"status": "not_checked_manifest_missing", "ok": False}
    elif not initialized:
        raw = {"status": "not_checked_uninitialized", "ok": False}
    elif not canonical_report.manifest.ok:
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
        "canonical_logs": canonical,
        "ok": bool(initialized and raw.get("ok") is True and canonical["ok"] is True),
    }
