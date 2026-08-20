from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
REQUEST = REPO / "remote-lab" / "e023-g1f-request.json"
RUNNER = ROOT / "run_g1f.py"
ADDENDUM = ROOT / "g1f-execution-addendum-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1f.yml"
PREREG = ROOT / "g1f-preregistration-v0.md"
EVAL = ROOT / "g1f-evaluation-contract-v0.json"
PREREG_MERGE_SHA = "1e5a3f991d0c3b76552725933149702ff6e53d15"
EXECUTION_SOURCE_SHA = "eab8c9e4f5ebbe5f43b93a1558fd3f9cc295f772"


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e023-g1f-composition-comparison-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "arms": ["O", "N"],
        "old_composer_calls": 8,
        "new_composer_calls": 8,
        "planner_calls": 0,
        "selector_calls": 0,
        "retrieval_model_calls": 0,
        "max_model_call_attempts": 16,
        "max_ai_credits_per_call": 30,
        "rerolls": 0,
        "question_order": [f"DQ00{i}" for i in range(1, 9)],
        "arm_order_by_question": {
            "DQ001": ["O", "N"],
            "DQ002": ["N", "O"],
            "DQ003": ["O", "N"],
            "DQ004": ["N", "O"],
            "DQ005": ["O", "N"],
            "DQ006": ["N", "O"],
            "DQ007": ["O", "N"],
            "DQ008": ["N", "O"],
        },
    }
    assert request == expected, request

    runner = RUNNER.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    prereg = PREREG.read_text(encoding="utf-8")
    evaluation = json.loads(EVAL.read_text(encoding="utf-8"))

    assert "G1f — authority-preserving composition comparison preregistration" in prereg
    assert evaluation["status"] == "PROSPECTIVE_G1F_EVALUATION_ONLY_NOT_RUNTIME"
    assert evaluation["paired_design"]["same_exact_bm25_top6_context_both_arms"] is True
    assert evaluation["paired_design"]["same_exact_model_required_later"] is True
    assert evaluation["promotion"]["name"] == "G1F_COMPOSITION_CANDIDATE_EARNED"

    assert 'PKG = HERE / "composition-comparison-v0"' in runner
    assert 'load_json(PKG / "context-freeze.json")' in runner
    assert "bm25_ranking(" not in runner
    assert "planner_prompt(" not in runner
    assert "selector_prompt(" not in runner
    assert "rrf_" not in runner.casefold()
    assert "g1f-evaluation-contract-v0.json" not in runner
    assert "authority-contract.json" not in runner
    assert 'G1C.composer_prompt(question, context).replace("Axxx", "Dxxx")' in runner
    assert "NEW.composer_prompt_v1(question, context)" in runner
    assert 'context = contexts[qid]' in runner
    assert '"input_context_sha256": pair["context_sha256"]' in runner
    assert 'arm_row["raw_model_text"] = receipt["text"]' in runner
    assert 'runner.attempts == request["max_model_call_attempts"]' in runner
    assert '"PENDING_FROZEN_ADJUDICATION"' in runner
    assert PREREG_MERGE_SHA in runner

    flattened = [
        (qid, arm)
        for qid in request["question_order"]
        for arm in request["arm_order_by_question"][qid]
    ]
    assert len(flattened) == 16
    assert sum(arm == "O" for _, arm in flattened) == 8
    assert sum(arm == "N" for _, arm in flattened) == 8
    for index, qid in enumerate(request["question_order"], start=1):
        expected_first = "O" if index % 2 else "N"
        assert request["arm_order_by_question"][qid] == [expected_first, "N" if expected_first == "O" else "O"]

    for phrase in [
        "FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL",
        PREREG_MERGE_SHA,
        "exact model: `gpt-5.6-luna`",
        "O composer calls: **8**",
        "N composer calls: **8**",
        "exact/max semantic attempts: **16**",
        "planner calls: **0**",
        "selector calls: **0**",
        "retrieval model calls: **0**",
        "rerolls: **0**",
        "same question string and same rendered context to O and N",
        "continues through the frozen schedule",
        "Raw model text is preserved",
        "does not load `g1f-evaluation-contract-v0.json`",
        "execution PR itself performs **0 semantic/model calls**",
        "PENDING_FROZEN_ADJUDICATION",
        "N >= **7 / 8 PASS**",
        "G2 persistence is not automatically authorized",
        "Natural installed dogfood on Issue #141 remains a parallel product-evidence track",
    ]:
        assert phrase in addendum, phrase

    assert "github.event_name == 'pull_request'" in workflow
    assert "github.event_name == 'push'" in workflow
    prereg_one_shot = f"github.event.before == '{PREREG_MERGE_SHA}'" in workflow
    completed_source_lock = f"github.sha == '{EXECUTION_SOURCE_SHA}'" in workflow
    assert prereg_one_shot ^ completed_source_lock
    assert "workflow_dispatch" not in workflow
    assert "copilot-requests: write" in workflow
    assert "--execute-model" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "result.sha256" in workflow
    assert "Capture frozen E023 G1f run" in workflow
    assert "e023-g1f-evidence" in workflow

    output = {
        "model_calls": 0,
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "model": request["model"],
        "question_count": request["question_count"],
        "old_composer_calls": request["old_composer_calls"],
        "new_composer_calls": request["new_composer_calls"],
        "max_semantic_calls": request["max_model_call_attempts"],
        "rerolls": request["rerolls"],
        "planner_calls": request["planner_calls"],
        "selector_calls": request["selector_calls"],
        "retrieval_model_calls": request["retrieval_model_calls"],
        "counterbalanced_interleaving": True,
        "shared_context_per_pair_required": True,
        "semantic_calls_authorized_on_pr": False,
        "semantic_calls_authorized_only_after_merge_from_exact_prereg_base": prereg_one_shot,
        "completed_execution_source_locked": completed_source_lock,
        "top6_product_default_authorized": False,
        "g2_persistence_authorized": False,
        "graph_entity_ku_authorized": False,
        "vector_default_authorized": False,
        "automatic_identity_routing_authorized": False,
    }
    print("E023 G1f execution contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
