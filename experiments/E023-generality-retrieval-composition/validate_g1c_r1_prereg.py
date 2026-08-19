from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V0 = ROOT / "evidence" / "g1c-run-32229563330"
V0_RESULT = V0 / "result.json"
V0_RUN = V0 / "run.json"
V0_FAILURE = ROOT / "g1c-v0-execution-failure-v0.md"
R1_PREREG = ROOT / "g1c-r1-preregistration-v0.md"
V0_WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1c.yml"


def main() -> int:
    result = json.loads(V0_RESULT.read_text(encoding="utf-8"))
    run = json.loads(V0_RUN.read_text(encoding="utf-8"))
    failure = V0_FAILURE.read_text(encoding="utf-8")
    prereg = R1_PREREG.read_text(encoding="utf-8")
    workflow = V0_WORKFLOW.read_text(encoding="utf-8")

    assert result["format"] == "E023-G1c-v0"
    assert result["execute_model"] is True
    assert result["execution_source_sha"] == "987ee7ec615f7eb869be59f14a1928a3811baeed"
    assert result["request"]["max_model_call_attempts"] == 24
    assert result["model_call_attempts"] == 6
    assert len(result["arms"]["A"]) == 6
    assert result["arms"]["B"] == []
    assert result["retrieval_selection_verdict"] == "NOT_EXECUTED"
    assert run["databaseId"] == 32229563330
    assert run["headSha"] == "987ee7ec615f7eb869be59f14a1928a3811baeed"
    assert run["status"] == "completed"
    assert run["conclusion"] == "failure"

    assert "INVALID_EXECUTION" in failure
    assert "nine semantic call attempts occurred" in failure
    assert "B-only" in prereg
    assert "18 semantic call attempts" in prereg
    assert "A semantic model calls are not repeated" in prereg
    assert "semantic rerolls inside R1: 0" in prereg

    assert "github.event_name == 'push' && github.sha == '987ee7ec615f7eb869be59f14a1928a3811baeed'" in workflow

    assert not (ROOT / "run_g1c_r1.py").exists()
    assert not (REPO / "remote-lab" / "e023-g1c-r1-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g1c-r1.yml").exists()

    output = {
        "model_calls": 0,
        "v0_run_id": 32229563330,
        "v0_status": "INVALID_EXECUTION",
        "v0_persisted_model_call_attempts": 6,
        "v0_actual_attempts_from_control_flow": 9,
        "r1_arm": "B_ONLY",
        "r1_max_semantic_calls_if_later_executed": 18,
        "r1_semantic_calls_authorized_on_this_pr": False,
        "v0_workflow_source_locked": True,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1c-R1 prereg validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
