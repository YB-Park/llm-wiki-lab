#!/usr/bin/env python3
"""T-v1 binding for the frozen E009A Stage A runner.

The orchestration/policy implementation remains in run_stage_a.py. This wrapper changes
only the frozen plan and run-root after the pre-scoring T-v0 surface-leak amendment, so
T-v0 artifacts can never be accidentally mixed with scored T-v1 artifacts.
"""

from pathlib import Path

import run_stage_a as base

ROOT = Path(__file__).resolve().parents[1]
base.PLAN = ROOT / "run-plan-v1.json"
base.RUN_ROOT = ROOT / "runs" / "stage-a-v1"


if __name__ == "__main__":
    base.main()
