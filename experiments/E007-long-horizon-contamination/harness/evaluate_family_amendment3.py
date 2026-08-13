#!/usr/bin/env python3
"""Run E007 post-hoc semantic evaluation with A3 contract containment.

Unlike earlier family wrappers, A3 intentionally revisits every completed primary run
so already-produced raw evaluator responses are re-parsed under one consistent A3
policy. Existing response.txt files are reused by the evaluator; they are not rerolled.
"""

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
EVALUATOR = Path(__file__).resolve().with_name("evaluate_semantic_amendment3.py")


def summary_is_a3(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return payload.get("format") == "E007-SEMANTIC-EVAL-A3-v0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate E007 Family N runs with amendment A3")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--expected-cli-version", default="1.0.35")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    current_cli = cli_version()
    if args.expected_cli_version and args.expected_cli_version not in current_cli:
        raise SystemExit(
            "Runtime drift detected before semantic evaluation. "
            f"Expected CLI containing {args.expected_cli_version!r}, observed {current_cli!r}."
        )

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    print("E007-SEMANTIC-FAMILY-A3-v0")
    print(f"model={args.model} cli={current_cli.splitlines()[0] if current_cli else '?'}")

    evaluated = 0
    for entry in plan["runs"]:
        run_id = str(entry["run_id"])
        run_dir = args.run_root / run_id
        primary_summary = run_dir / "summary.json"
        semantic_summary = run_dir / "evaluation" / "semantic-summary.json"
        if not primary_summary.exists():
            raise SystemExit(f"STOP primary run is incomplete: {run_id}")
        if summary_is_a3(semantic_summary):
            print(f"SKIP A3-evaluated {run_id}")
            continue
        if args.limit is not None and evaluated >= args.limit:
            print(f"STOP limit={args.limit}; next={run_id}")
            break

        print(f"EVAL-A3 seq={entry['sequence']} run={run_id} condition={entry['condition']}")
        proc = subprocess.run(
            [sys.executable, str(EVALUATOR), "--run-dir", str(run_dir), "--model", args.model],
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(f"STOP A3 semantic evaluator failed for {run_id} with code {proc.returncode}")
        evaluated += 1

    remaining = [
        str(entry["run_id"])
        for entry in plan["runs"]
        if not summary_is_a3(args.run_root / str(entry["run_id"]) / "evaluation" / "semantic-summary.json")
    ]
    print("SEMANTIC-BLOCK-A3-COMPLETE" if not remaining else f"SEMANTIC-BLOCK-A3-INCOMPLETE remaining={','.join(remaining)}")


if __name__ == "__main__":
    main()
