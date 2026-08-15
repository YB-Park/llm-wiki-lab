from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = ROOT / "experiments/E018-steward-policy/run_e018.py"
REQUEST_PATH = ROOT / "remote-lab/e018-steward-policy-request.json"


def load_base():
    spec = importlib.util.spec_from_file_location("e018_phase1_v0", BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("e018_base_runner_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_request_v1() -> dict:
    row = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e018-steward-policy-20260815-1",
        "phase1_max_model_calls": 24,
        "phase2_max_model_calls": 4,
        "steward_model": "gpt-5.6-luna",
        "baseline_models": ["gpt-5.4", "claude-sonnet-4.6"],
        "phase2_case_ids": ["C1-relevant-read", "C6-conflict-pending-decision"],
        "max_ai_credits_policy": 30,
        "max_ai_credits_answer": 30,
    }
    if row != expected:
        raise RuntimeError(f"request_mismatch:{row}")
    return row


def main() -> int:
    module = load_base()
    module.load_request = load_request_v1
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
