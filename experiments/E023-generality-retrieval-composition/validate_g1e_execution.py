from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
REQUEST = REPO / "remote-lab" / "e023-g1e-request.json"
RUNNER = ROOT / "run_g1e.py"
ADDENDUM = ROOT / "g1e-execution-addendum-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1e.yml"
PHASE0_SHA = "c674f93728db7d4fe0d8b84328feca34b87fd655"


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e023-g1e-exact-bm25-budget-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "a5_top_k": 5,
        "b6_top_k": 6,
        "a5_composer_calls": 8,
        "b6_composer_calls": 8,
        "planner_calls": 0,
        "selector_calls": 0,
        "max_model_call_attempts": 16,
        "max_ai_credits_per_call": 30,
    }
    assert request == expected, request

    runner = RUNNER.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert '"phase0_authority_gate": "PASS_FROZEN_PR187"' in runner
    assert '"semantic_promotion": "NOT_EXECUTED" if not args.execute_model else "PENDING_FROZEN_ADJUDICATION"' in runner
    assert "planner_prompt(" not in runner
    assert "parse_planner(" not in runner
    assert "selector_prompt(" not in runner
    assert "parse_selector(" not in runner
    assert 'G1C.composer_prompt(question, context).replace("Axxx", "Cxxx")' in runner
    assert 'for arm_name in ("A5", "B6")' in runner
    assert 'runner.attempts == request["max_model_call_attempts"]' in runner

    for phrase in [
        "A5 composer calls: **8**",
        "B6 composer calls: **8**",
        "exact/max semantic attempts: **16**",
        "planner calls: **0**",
        "selector calls: **0**",
        "rerolls: **0**",
        PHASE0_SHA,
        "PENDING_FROZEN_ADJUDICATION",
    ]:
        assert phrase in addendum, phrase

    assert "github.event_name == 'pull_request'" in workflow
    assert "copilot-requests: write" in workflow
    assert "github.event_name == 'push'" in workflow
    assert f"github.event.before == '{PHASE0_SHA}'" in workflow
    assert "--execute-model" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "result.sha256" in workflow

    output = {
        "model_calls": 0,
        "phase0_sha": PHASE0_SHA,
        "model": request["model"],
        "question_count": request["question_count"],
        "A5_top_k": request["a5_top_k"],
        "B6_top_k": request["b6_top_k"],
        "planner_calls": request["planner_calls"],
        "selector_calls": request["selector_calls"],
        "max_semantic_calls": request["max_model_call_attempts"],
        "semantic_calls_authorized_on_pr": False,
        "top6_product_policy_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1e execution contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
