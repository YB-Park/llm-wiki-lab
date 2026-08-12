#!/usr/bin/env python3
"""Execute the frozen E007 Family N primary block in preregistered order.

This script reduces manual execution error; it does not choose conditions or tune
prompts. Completed runs are never rerolled automatically. An incomplete run directory
causes a stop so the operator must inspect the infrastructure failure explicitly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from copilot_cli import cli_version
from handoff_summary import write_handoff
from run_e007 import RUNS, run_condition
from structural_metrics import analyze_run

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "run-plan-v0.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_is_complete(run_dir: Path) -> bool:
    return (run_dir / "summary.json").exists()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run frozen E007 Family N primary block")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    parser.add_argument("--expected-cli-version", default="1.0.35")
    parser.add_argument(
        "--limit",
        type=int,
        help="Infrastructure convenience only: execute at most N next planned runs, preserving order",
    )
    args = parser.parse_args()

    plan = load_json(args.plan)
    model = str(plan["model"])
    max_wave = int(plan["max_wave"])
    current_cli = cli_version()

    if args.expected_cli_version and args.expected_cli_version not in current_cli:
        raise SystemExit(
            "Runtime drift detected before scored execution. "
            f"Expected CLI containing {args.expected_cli_version!r}, observed {current_cli!r}. "
            "Do not silently mix runtimes; update the execution profile/run block deliberately."
        )

    print("E007-FAMILY-N-v0")
    print(f"model={model} max_wave={max_wave} cli={current_cli.splitlines()[0] if current_cli else '?'}")
    print(f"plan={args.plan}")

    executed = 0
    for entry in plan["runs"]:
        run_id = str(entry["run_id"])
        condition = str(entry["condition"])
        run_dir = args.run_root / run_id

        if run_is_complete(run_dir):
            print(f"SKIP complete {run_id}")
            continue

        if run_dir.exists():
            raise SystemExit(
                f"STOP incomplete run directory exists: {run_dir}. "
                "Inspect the infrastructure failure; do not delete/reroll it silently."
            )

        if args.limit is not None and executed >= args.limit:
            print(f"STOP limit={args.limit}; next={run_id}")
            break

        print(f"START seq={entry['sequence']} run={run_id} condition={condition}")
        run_condition(
            condition=condition,
            model=model,
            run_dir=run_dir,
            max_wave=max_wave,
        )

        structure = analyze_run(run_dir)
        write_json(run_dir / "structural-metrics.json", structure)
        handoff = write_handoff(run_dir)
        print(handoff, end="")
        print(f"DONE {run_id}")
        executed += 1

    remaining = [
        str(entry["run_id"])
        for entry in plan["runs"]
        if not run_is_complete(args.run_root / str(entry["run_id"]))
    ]
    if remaining:
        print(f"PRIMARY-BLOCK-INCOMPLETE remaining={','.join(remaining)}")
    else:
        print("PRIMARY-BLOCK-COMPLETE")


if __name__ == "__main__":
    main()
