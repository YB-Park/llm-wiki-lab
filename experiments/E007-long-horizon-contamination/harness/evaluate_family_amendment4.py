#!/usr/bin/env python3
"""Run frozen E007 semantic evaluation with A4 missing-primary containment."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from copilot_cli import cli_version
from run_e007 import RUNS

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "run-plan-v0.json"
EVALUATOR = Path(__file__).resolve().with_name("evaluate_semantic_amendment4.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate E007 Family N runs with amendment A4")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--expected-cli-version", default="1.0.35")
    args = parser.parse_args()

    current_cli = cli_version()
    if args.expected_cli_version and args.expected_cli_version not in current_cli:
        raise SystemExit(
            "Runtime drift detected before semantic evaluation. "
            f"Expected CLI containing {args.expected_cli_version!r}, observed {current_cli!r}."
        )

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    print("E007-SEMANTIC-FAMILY-A4-v0")
    print(f"model={args.model} cli={current_cli.splitlines()[0] if current_cli else '?'}")

    for entry in plan["runs"]:
        run_id = str(entry["run_id"])
        run_dir = args.run_root / run_id
        if not (run_dir / "summary.json").exists():
            raise SystemExit(f"STOP primary run is incomplete: {run_id}")
        print(f"EVAL seq={entry['sequence']} run={run_id} condition={entry['condition']}")
        proc = subprocess.run(
            [sys.executable, str(EVALUATOR), "--run-dir", str(run_dir), "--model", args.model],
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(f"STOP semantic evaluator A4 failed for {run_id} with code {proc.returncode}")

    print("SEMANTIC-BLOCK-A4-COMPLETE")


if __name__ == "__main__":
    main()
