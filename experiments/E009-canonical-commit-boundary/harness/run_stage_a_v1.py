#!/usr/bin/env python3
"""T-v1 binding for the frozen E009A Stage A runner.

The orchestration/policy implementation remains in run_stage_a.py. This wrapper binds the
frozen T-v1 plan/run-root, requires the non-scored preflight sentinel, sanitizes
infrastructure failures, and implements the preregistered risk-first A3 cost semantics.
T-v0 artifacts cannot be mixed with scored T-v1 artifacts.
"""

import json
from pathlib import Path

import run_stage_a as base

ROOT = Path(__file__).resolve().parents[1]
base.PLAN = ROOT / "run-plan-v1.json"
base.RUN_ROOT = ROOT / "runs" / "stage-a-v1"
PREFLIGHT_STATUS = ROOT / "runs" / "preflight-v1" / "status.json"

_original_run_prompt = base.run_prompt
_original_policy_telemetry = base.policy_telemetry


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


def _policy_telemetry_v1(policy, dirs, cases):
    if policy != "A3":
        return _original_policy_telemetry(policy, dirs, cases)
    selected = [
        dirs[(case_id, 1)]
        for case_id, case in sorted(cases.items())
        if case["risk"] == "low"
    ]
    return base.aggregate(selected)


def _require_preflight() -> None:
    if not PREFLIGHT_STATUS.exists():
        raise SystemExit("E009A-STOP preflight_required run=harness/preflight.py")
    try:
        status = json.loads(PREFLIGHT_STATUS.read_text(encoding="utf-8"))
    except Exception:
        raise SystemExit("E009A-STOP preflight_status_invalid") from None
    if status.get("status") != "PASS" or status.get("model") != "gpt-5.6-luna" or status.get("otel") != "yes":
        raise SystemExit("E009A-STOP preflight_not_passed")


base.run_prompt = _sanitized_run_prompt
base.policy_telemetry = _policy_telemetry_v1


if __name__ == "__main__":
    _require_preflight()
    base.main()
