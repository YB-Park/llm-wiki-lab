#!/usr/bin/env python3
"""Archive an incomplete E007 run without deleting evidence.

Use only for an infrastructure-aborted attempt that has no summary.json. The run is
moved under runs/_failed_attempts/ with a timestamped name so the frozen run_id can be
executed again without erasing the failed attempt.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path

from run_e007 import RUNS


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive incomplete E007 attempt")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    args = parser.parse_args()

    source = args.run_root / args.run_id
    if not source.exists():
        raise SystemExit(f"run directory does not exist: {source}")
    if (source / "summary.json").exists():
        raise SystemExit("refusing to archive a completed scored run")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest_root = args.run_root / "_failed_attempts"
    dest_root.mkdir(parents=True, exist_ok=True)
    dest = dest_root / f"{args.run_id}-infra-{stamp}"
    if dest.exists():
        raise SystemExit(f"archive destination already exists: {dest}")

    shutil.move(str(source), str(dest))
    print("E007-INCOMPLETE-ARCHIVED-v0")
    print(f"run_id={args.run_id}")
    print(f"archived={dest}")
    print("reason=infrastructure_abort evidence_preserved=yes")


if __name__ == "__main__":
    main()
