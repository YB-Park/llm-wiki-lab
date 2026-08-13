#!/usr/bin/env python3
"""T-v1 binding for the frozen E009A Stage A runner.

The orchestration/policy implementation remains in run_stage_a.py. This wrapper changes
only the frozen plan/run-root and sanitizes infrastructure failures after the pre-scoring
T-v0 surface-leak amendment. T-v0 artifacts can never be mixed with scored T-v1 artifacts.
"""

from pathlib import Path

import run_stage_a as base

ROOT = Path(__file__).resolve().parents[1]
base.PLAN = ROOT / "run-plan-v1.json"
base.RUN_ROOT = ROOT / "runs" / "stage-a-v1"

_original_run_prompt = base.run_prompt


def _sanitized_run_prompt(**kwargs):
    try:
        return _original_run_prompt(**kwargs)
    except Exception:
        run_dir = kwargs.get("run_dir")
        synthetic_call = Path(run_dir).name if run_dir is not None else "unknown"
        raise SystemExit(
            f"E009A-STOP infrastructure_call_failure synthetic_call={synthetic_call} "
            "local_artifact_preserved=yes"
        ) from None


base.run_prompt = _sanitized_run_prompt


if __name__ == "__main__":
    base.main()
