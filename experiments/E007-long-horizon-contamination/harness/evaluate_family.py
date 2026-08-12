#!/usr/bin/env python3
"""Run the frozen post-hoc semantic evaluator across completed Family N runs.

Evaluation is separate from maintenance. This wrapper exists only to preserve the
frozen run set, reduce operator mistakes, and support resume after infrastructure
interruptions.
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
EVALUATOR = Path(__file__).resolve().with_name("evaluate_semantic.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate completed E007 Family N runs")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--expected-cli-version", default="1.0.35")
    parser.add_argument("--limit", type=int, help="Evaluate at most N next unevaluated runs")
    args = parser.parse_args()

    current_cli = cli_version()
    if args.expected_cli_version and args.expected_cli_version not in current_cli:
        raise SystemExit(
            "Runtime drift detected before semantic evaluation. "
            f"Expected CLI containing {args.expected_cli_version!r}, observed {current_cli!r}. "
            "Record a new evaluator execution block rather than silently mixing runtimes."
        )

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    print("E007-SEMANTIC-FAMILY-v0")
    print(f"model={args.model} cli={current_cli.splitlines()[0] if current_cli else '?'}")

    evaluated = 0
    for entry in plan["runs"]:
        run_id = str(entry["run_id"])
        run_dir = args.run_root / run_id
        summary_path = run_dir / "summary.json"
        semantic_path = run_dir / "evaluation" / "semantic-summary.json"

        if not summary_path.exists():
            raise SystemExit(f"STOP primary run is incomplete: {run_id}")
        if semantic_path.exists():
            print(f"SKIP evaluated {run_id}")
            continue
        if args.limit is not None and evaluated >= args.limit:
            print(f"STOP limit={args.limit}; next={run_id}")
            break

        print(f"EVAL seq={entry['sequence']} run={run_id} condition={entry['condition']}")
        proc = subprocess.run(
            [
                sys.executable,
                str(EVALUATOR),
                "--run-dir",
                str(run_dir),
                "--model",
                args.model,
            ],
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(f"STOP semantic evaluator failed for {run_id} with code {proc.returncode}")
        evaluated += 1

    remaining = [
        str(entry["run_id"])
        for entry in plan["runs"]
        if not (args.run_root / str(entry["run_id"]) / "evaluation" / "semantic-summary.json").exists()
    ]
    if remaining:
        print(f"SEMANTIC-BLOCK-INCOMPLETE remaining={','.join(remaining)}")
    else:
        print("SEMANTIC-BLOCK-COMPLETE")


if __name__ == "__main__":
    main()
