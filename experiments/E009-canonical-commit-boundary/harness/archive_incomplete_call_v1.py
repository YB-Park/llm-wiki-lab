#!/usr/bin/env python3
"""Archive one incomplete E009A T-v1 call before an infrastructure-only retry.

This helper refuses to archive any call that already has a parsed judgment. It never
changes the frozen plan and never deletes evidence; it moves the incomplete local attempt
under `_failed_attempts/` so the exact same planned call can be retried explicitly.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "run-plan-v1.json"
RUN_ROOT = ROOT / "runs" / "stage-a-v1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence", type=int, required=True)
    args = parser.parse_args()

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    rows = [row for row in plan["calls"] if int(row["sequence"]) == args.sequence]
    if len(rows) != 1:
        raise SystemExit("E009A-ARCHIVE-STOP invalid_sequence")
    row = rows[0]
    name = f"{args.sequence:03d}-{row['case_id']}-p{row['pass']}"
    source = RUN_ROOT / "calls" / name
    if not source.exists():
        raise SystemExit(f"E009A-ARCHIVE-STOP synthetic_call={name} reason=no_incomplete_call")
    if (source / "judgment.json").exists():
        raise SystemExit(f"E009A-ARCHIVE-STOP synthetic_call={name} reason=judgment_already_exists")

    archive_root = RUN_ROOT / "_failed_attempts"
    archive_root.mkdir(parents=True, exist_ok=True)
    attempt = 1
    while True:
        target = archive_root / f"{name}-infra-{attempt:02d}"
        if not target.exists():
            break
        attempt += 1
    shutil.move(str(source), str(target))
    print("E009A-INFRA-ATTEMPT-ARCHIVED-v0")
    print(f"synthetic_call={name} archived=yes retry_same_planned_call=yes")


if __name__ == "__main__":
    main()
