#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOCK = ROOT / "experiments" / "E009-canonical-commit-boundary" / "semantic-fixture-lock-v1.json"


def git_blob_sha(path: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def main() -> None:
    payload = json.loads(LOCK.read_text(encoding="utf-8"))
    assert payload["experiment"] == "E009A"
    assert payload["lock_version"] == "v1"
    assert payload["created_before_scored_corpus_T_judgments"] is True

    fixtures = payload["fixtures"]
    assert isinstance(fixtures, dict) and fixtures

    mismatches = []
    for relpath, expected in sorted(fixtures.items()):
        path = ROOT / relpath
        if not path.exists():
            mismatches.append((relpath, expected, "MISSING"))
            continue
        actual = git_blob_sha(path)
        if actual != expected:
            mismatches.append((relpath, expected, actual))

    if mismatches:
        print("E009A-SEMANTIC-FIXTURE-LOCK FAIL")
        for relpath, expected, actual in mismatches:
            print(f"mismatch path={relpath} expected={expected} actual={actual}")
        raise SystemExit(1)

    print("E009A-SEMANTIC-FIXTURE-LOCK PASS")
    print(f"fixtures={len(fixtures)} lock=v1")


if __name__ == "__main__":
    main()
