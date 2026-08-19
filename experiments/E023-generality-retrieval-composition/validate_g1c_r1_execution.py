from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RUNNER = ROOT / "run_g1c_r1.py"
PREREG = ROOT / "g1c-r1-preregistration-v0.md"
ADDENDUM = ROOT / "g1c-r1-execution-addendum-v0.md"
REQUEST = REPO / "remote-lab" / "e023-g1c-r1-request.json"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1c-r1.yml"
V0_WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1c.yml"

EXPECTED_REQUEST = {
    "b_composer_calls": 6,
    "b_planner_calls": 6,
    "b_selector_calls": 6,
    "candidate_followup_top_k": 3,
    "final_anchor_limit": 5,
    "initial_top_k": 5,
    "max_ai_credits_per_call": 30,
    "max_followup_queries": 2,
    "max_model_call_attempts": 18,
    "model": "gpt-5.6-luna",
    "planner_snippet_chars": 320,
    "question_count": 6,
    "request_id": "e023-g1c-r1-b-only-recovery-v0",
}


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    runner = RUNNER.read_text(encoding="utf-8")
    prereg = PREREG.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    v0_workflow = V0_WORKFLOW.read_text(encoding="utf-8")

    assert request == EXPECTED_REQUEST, request
    assert "B-only" in prereg
    assert "18 semantic call attempts" in prereg
    assert "Persistence-before-aggregation" in prereg
    assert "EXECUTION CONTRACT FROZEN" in addendum
    assert "does not rerun A" in addendum
    assert "every model stage is saved immediately" in addendum

    # Semantic mechanics are reused directly from the frozen v0 module rather
    # than copied and edited in R1.
    for needle in [
        "V0.G1C.bm25_ranking",
        "V0.candidate_view",
        "V0.planner_prompt",
        "V0.parse_planner",
        "V0.build_candidate_pool",
        "V0.selector_prompt",
        "V0.parse_selector",
        "V0.evidence_context",
        "V0.composer_prompt",
        "V0.parse_composer",
        "V0.authority_eval",
    ]:
        assert needle in runner, needle

    assert '"format": "E023-G1c-R1-v0"' in runner
    assert '"max_model_call_attempts": 18' in runner
    assert '"retrieval_selection_verdict": "NOT_EXECUTED"' in runner
    assert 'result["retrieval_selection_verdict"] = aggregate_verdict(result["B"])' in runner
    assert runner.count("save_result(result)") >= 8
    assert "for question_id in QUESTION_IDS:" in runner
    assert "V0.G1.ModelRunner(request)" in runner

    # PR is zero-model; main push is the only semantic path for this new R1
    # workflow. The archived v0 paid path remains source-SHA locked.
    assert "if: github.event_name == 'pull_request'" in workflow
    assert "if: github.event_name == 'push'" in workflow
    assert "--execute-model" in workflow
    assert "copilot-requests: write" in workflow
    assert (
        "github.event_name == 'push' && github.sha == "
        "'987ee7ec615f7eb869be59f14a1928a3811baeed'"
    ) in v0_workflow

    output = {
        "model_calls": 0,
        "request_id": request["request_id"],
        "question_count": request["question_count"],
        "r1_arm": "B_ONLY",
        "max_semantic_calls": request["max_model_call_attempts"],
        "semantic_mechanics_reused_from_v0": True,
        "stage_persistence_required": True,
        "aggregate_after_loop_only": True,
        "v0_workflow_source_locked": True,
        "pr_semantic_execution": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1c-R1 execution contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
