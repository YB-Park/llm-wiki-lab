from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RUNNER = ROOT / "run_g2.py"
ADDENDUM = ROOT / "g2-execution-addendum-v0.md"
PREREG = ROOT / "g2-preregistration-v0.md"
EVAL = ROOT / "g2-evaluation-contract-v0.json"
PROMPT = ROOT / "projection_prompt_v0.py"
REQUEST = REPO / "remote-lab" / "e023-g2-request.json"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g2.yml"
PREREG_MERGE_SHA = "080ac3d91d011be3ec16111bdc24eda9905f3d9c"


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e023-g2-fixed-identity-persistence-v0",
        "model": "gpt-5.6-luna",
        "question_count": 12,
        "Q_composer_calls": 12,
        "P_composer_calls": 12,
        "projection_build_rebuild_calls": 5,
        "planner_calls": 0,
        "selector_calls": 0,
        "vector_calls": 0,
        "max_model_call_attempts": 29,
        "max_ai_credits_per_call": 30,
        "rerolls": 0,
        "question_order": [f"PQ{i:03d}" for i in range(1, 13)],
        "arm_order_by_question": {
            "PQ001": ["Q", "P"], "PQ002": ["P", "Q"],
            "PQ003": ["Q", "P"], "PQ004": ["P", "Q"],
            "PQ005": ["Q", "P"], "PQ006": ["P", "Q"],
            "PQ007": ["Q", "P"], "PQ008": ["P", "Q"],
            "PQ009": ["Q", "P"], "PQ010": ["P", "Q"],
            "PQ011": ["Q", "P"], "PQ012": ["P", "Q"],
        },
    }
    assert request == expected, request

    runner = RUNNER.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    prereg = PREREG.read_text(encoding="utf-8")
    evaluation = json.loads(EVAL.read_text(encoding="utf-8"))
    prompt_source = PROMPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "PREREGISTRATION / ZERO-MODEL FIRST" in prereg
    assert evaluation["status"] == "PROSPECTIVE_G2_EVALUATION_ONLY_NOT_RUNTIME"
    assert evaluation["semantic_calls_authorized_on_this_pr"] is False
    assert evaluation["planned_execution"]["max_semantic_call_attempts"] == 29
    assert evaluation["promotion"]["name"] == "G2_PERSISTENCE_CANDIDATE_EARNED"

    for phrase in [
        'PKG = HERE / "persistence-comparison-v0"',
        'PREREG_MERGE_SHA = "080ac3d91d011be3ec16111bdc24eda9905f3d9c"',
        'PROJECTION.projection_prompt_v0(subject_id, context)',
        'G1C.composer_prompt(question, context).replace("Axxx", "Pxxx")',
        '"selection_mode": "STALE_PROJECTION_BYPASS"',
        '"selection_mode": "FRESH_PROJECTION_RETRIEVAL"',
        'ranked_entries[:2]',
        'if len(selected) >= 4',
        'selected = selected[:6]',
        'contexts = {"Q": q["context"], "P": p_context}',
        'p_context = evidence_context(anchor_map, p_selected)',
        'runner.attempts == request["max_model_call_attempts"]',
        '"PENDING_FROZEN_ADJUDICATION"',
    ]:
        assert phrase in runner, phrase

    # Runtime may score selected terminal contexts for evidence capture but must not load evaluator artifacts or frozen outcomes.
    for forbidden in [
        "g2-evaluation-contract-v0.json",
        "g2-adjudication-v0.json",
        "g2-results-v0.md",
        "expected_control_authority_status",
        "G2_PERSISTENCE_CANDIDATE_EARNED",
        "semantic_verdict",
        "primary_stale_negative_control",
    ]:
        assert forbidden not in runner, forbidden
    assert "def projection_prompt_v0(subject_id: str, authority_context: str)" in prompt_source
    assert "USER QUESTION" not in prompt_source
    assert "question:" not in prompt_source

    # Projection is retrieval-only: statement text is ranked but final context comes from terminal anchor map.
    assert 'docs = [{"anchor_id": row["entry_id"], "text": row["statement"]}' in runner
    assert 'evidence_context(anchor_map, p_selected)' in runner
    assert 'parse_composer(receipt["text"], set(arm_row["selected_anchor_ids"]))' in runner
    assert 'PROJECTION.projection_prompt_v0(subject_id, context)' in runner
    assert 'old_composer_prompt(question["question"], contexts[arm])' in runner

    # Frozen lifecycle and semantic attempt arithmetic.
    assert request["projection_build_rebuild_calls"] == 5
    assert request["Q_composer_calls"] + request["P_composer_calls"] == 24
    assert 5 + 24 == request["max_model_call_attempts"] == 29
    assert sum(order[0] == "Q" for order in request["arm_order_by_question"].values()) == 6
    assert sum(order[0] == "P" for order in request["arm_order_by_question"].values()) == 6
    assert request["planner_calls"] == request["selector_calls"] == request["vector_calls"] == request["rerolls"] == 0

    for phrase in [
        "FROZEN EXECUTION CONTRACT / PR PREFLIGHT ZERO MODEL",
        PREREG_MERGE_SHA,
        "exact model: `gpt-5.6-luna`",
        "Q composer calls: **12**",
        "P composer calls: **12**",
        "projection build/rebuild calls: **5**",
        "exact/max semantic attempts: **29**",
        "STALE_PROJECTION_BYPASS",
        "Projection statements are never composer context",
        "PQ011 is the primary stale negative control",
        "execution PR itself performs **0 semantic/model calls**",
        "PENDING_FROZEN_ADJUDICATION",
        "both PQ004 and PQ008",
        "P >= **10/12 PASS**",
        ">= **2 paired semantic improvements**",
        "<= **85%** of Q",
        "does not automatically authorize",
    ]:
        assert phrase in addendum, phrase

    # One-shot CI: PR preflight is zero-model; push execution only from exact prereg base.
    assert "github.event_name == 'pull_request'" in workflow
    assert "github.event_name == 'push'" in workflow
    assert f"github.event.before == '{PREREG_MERGE_SHA}'" in workflow
    assert "workflow_dispatch" not in workflow
    assert "copilot-requests: write" in workflow
    assert "run_g2.py --execute-model" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "Capture frozen E023 G2 run" in workflow
    assert "e023-g2-evidence" in workflow

    # No result/adjudication artifact exists before execution.
    assert not (ROOT / "g2-adjudication-v0.json").exists()
    assert not (ROOT / "g2-results-v0.md").exists()

    output = {
        "model_calls": 0,
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "model": request["model"],
        "question_count": request["question_count"],
        "Q_composer_calls": request["Q_composer_calls"],
        "P_composer_calls": request["P_composer_calls"],
        "projection_build_rebuild_calls": request["projection_build_rebuild_calls"],
        "max_semantic_calls": request["max_model_call_attempts"],
        "rerolls": 0,
        "counterbalanced_QP_order": True,
        "stale_projection_bypass_frozen": True,
        "projection_text_to_composer": False,
        "semantic_calls_authorized_on_pr": False,
        "semantic_calls_authorized_only_after_merge_from_exact_prereg_base": True,
        "g2_product_persistence_authorized": False,
        "graph_entity_ku_authorized": False,
        "vector_default_authorized": False,
        "automatic_identity_routing_authorized": False,
        "dogfood_runtime_change_authorized": False,
    }
    print("E023 G2 execution contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
