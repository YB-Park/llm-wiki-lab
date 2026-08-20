from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
REQUEST = REPO / "remote-lab" / "e023-g1f-request.json"
RUNNER = ROOT / "run_g1f.py"
ADDENDUM = ROOT / "g1f-execution-addendum-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1f.yml"
PROMPT_V1 = ROOT / "composition_prompt_v1.py"


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e023-g1f-authority-preserving-composition-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "context_top_k": 6,
        "old_composer_calls": 8,
        "new_composer_calls": 8,
        "planner_calls": 0,
        "selector_calls": 0,
        "max_model_call_attempts": 16,
        "max_ai_credits_per_call": 30,
    }
    assert request == expected, request

    runner = RUNNER.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    prompt_v1 = PROMPT_V1.read_text(encoding="utf-8")

    assert '"arms": {"O": [], "N": []}' in runner
    assert 'for arm_name in ("O", "N")' in runner
    assert 'context = evidence_context(anchor_map, row["selected_anchor_ids"])' in runner
    assert 'old_prompt(row["question"], context) if arm_name == "O" else composer_prompt_v1(row["question"], context)' in runner
    assert "planner_prompt(" not in runner
    assert "selector_prompt(" not in runner
    assert 'assert "D017" not in contexts["DQ004"]["selected_anchor_ids"]' in runner
    assert 'runner.attempts == request["max_model_call_attempts"]' in runner

    for phrase in [
        "O composer calls: **8**",
        "N composer calls: **8**",
        "total semantic attempts: **16**",
        "planner calls: **0**",
        "selector calls: **0**",
        "rerolls: **0**",
        "Freeze E023 G1f execution contract",
        "PENDING_FROZEN_ADJUDICATION",
    ]:
        assert phrase in addendum, phrase

    for phrase in [
        "authority-preserving composer",
        "preserve that user ownership naturally",
        "Never synthesize a load-bearing identity, attribution, policy, project, temporal, or authorization bridge",
        "Set insufficient_authority=true if and only if at least one load-bearing part of the user's actual question",
    ]:
        assert phrase in prompt_v1, phrase
    for forbidden in ["DQ001", "DQ004", "Redis Streams", "CloudArc", "Quasar", "INC-517"]:
        assert forbidden not in prompt_v1, forbidden

    assert "github.event_name == 'pull_request'" in workflow
    assert "copilot-requests: write" in workflow
    assert "github.event_name == 'push'" in workflow
    assert "startsWith(github.event.head_commit.message, 'Freeze E023 G1f execution contract')" in workflow
    assert "--execute-model" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "result.sha256" in workflow

    output = {
        "model_calls": 0,
        "model": request["model"],
        "question_count": request["question_count"],
        "context_top_k": request["context_top_k"],
        "old_composer_calls": request["old_composer_calls"],
        "new_composer_calls": request["new_composer_calls"],
        "planner_calls": request["planner_calls"],
        "selector_calls": request["selector_calls"],
        "max_semantic_calls": request["max_model_call_attempts"],
        "same_context_both_arms": True,
        "semantic_calls_authorized_on_pr": False,
        "product_prompt_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1f execution contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
