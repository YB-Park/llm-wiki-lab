from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
EVIDENCE = ROOT / "evidence" / "g1e-run-32324460519"
RESULT = EVIDENCE / "result.json"
RESULT_SHA = EVIDENCE / "result.sha256"
RUN_FINAL = EVIDENCE / "run-final.json"
ADJUDICATION = ROOT / "g1e-adjudication-v0.json"
RESULT_DOC = ROOT / "g1e-results-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1e.yml"

RUN_ID = 32324460519
EXECUTION_SOURCE = "505740b74776fc7b7988e9c168c9c9d0ed2067fa"
EXPECTED_SHA256 = "865d89ad8c8b219493823bd21413196f658a9ffa2fdd3ed2948bb34b20f16727"


def count_verdicts(rows: dict[str, dict]) -> dict[str, int]:
    counts = Counter(row["verdict"] for row in rows.values())
    return {
        "PASS": counts["PASS"],
        "PARTIAL": counts["PARTIAL"],
        "FAIL_RETRIEVAL": counts["FAIL_RETRIEVAL"],
        "FAIL_COMPOSITION": counts["FAIL_COMPOSITION"],
        "CRITICAL_ERROR": counts["CRITICAL_ERROR"],
    }


def main() -> int:
    raw = RESULT.read_bytes()
    result = json.loads(raw)
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    run_final = json.loads(RUN_FINAL.read_text(encoding="utf-8"))
    result_doc = RESULT_DOC.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    assert RESULT_SHA.read_text(encoding="utf-8").split()[0] == EXPECTED_SHA256

    assert result["format"] == "E023-G1e-v0"
    assert result["execute_model"] is True
    assert result["execution_complete"] is True
    assert result["execution_source_sha"] == EXECUTION_SOURCE
    assert result["phase0_authority_gate"] == "PASS_FROZEN_PR187"
    assert result["model"] == "gpt-5.6-luna"
    assert result["model_call_attempts"] == 16
    assert result["usage"]["model_calls"] == 16
    assert result["request"]["planner_calls"] == 0
    assert result["request"]["selector_calls"] == 0
    assert result["semantic_promotion"] == "PENDING_FROZEN_ADJUDICATION"

    a5 = {row["question_id"]: row for row in result["arms"]["A5"]}
    b6 = {row["question_id"]: row for row in result["arms"]["B6"]}
    qids = [f"CQ00{i}" for i in range(1, 9)]
    assert sorted(a5) == qids
    assert sorted(b6) == qids
    assert all(len(a5[qid]["selected_anchor_ids"]) == 5 for qid in qids)
    assert all(len(b6[qid]["selected_anchor_ids"]) == 6 for qid in qids)

    expected_a_status = {
        "CQ001": "INSUFFICIENT_AUTHORITY",
        "CQ002": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ003": "SUFFICIENT_CLEAN",
        "CQ004": "SUFFICIENT_CLEAN",
        "CQ005": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ006": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ007": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ008": "INSUFFICIENT_AUTHORITY",
    }
    expected_b_status = {
        "CQ001": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ002": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ003": "SUFFICIENT_CLEAN",
        "CQ004": "SUFFICIENT_CLEAN",
        "CQ005": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ006": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ007": "SUFFICIENT_WITH_CONFLATION_RISK",
        "CQ008": "SUFFICIENT_CLEAN",
    }
    assert {qid: a5[qid]["authority"]["status"] for qid in qids} == expected_a_status
    assert {qid: b6[qid]["authority"]["status"] for qid in qids} == expected_b_status

    # The two prospectively frozen rank-6 authority improvements must be present.
    assert a5["CQ001"]["selected_anchor_ids"][-1] == "C004"
    assert b6["CQ001"]["selected_anchor_ids"][-1] == "C003"
    assert "C003" not in a5["CQ001"]["selected_anchor_ids"]
    assert "C003" in b6["CQ001"]["selected_anchor_ids"]
    assert a5["CQ008"]["selected_anchor_ids"][-1] == "C032"
    assert b6["CQ008"]["selected_anchor_ids"][-1] == "C033"
    assert "C033" not in a5["CQ008"]["selected_anchor_ids"]
    assert "C033" in b6["CQ008"]["selected_anchor_ids"]

    # Frozen semantic behavior around the two authority repairs.
    assert a5["CQ001"]["composer"]["insufficient_authority"] is False
    assert "Rina Singh" in a5["CQ001"]["composer"]["answer"]
    assert "C003" in b6["CQ001"]["composer"]["cited_anchor_ids"]
    assert a5["CQ008"]["composer"]["insufficient_authority"] is True
    assert b6["CQ008"]["composer"]["insufficient_authority"] is False
    assert {"C032", "C033"} <= set(b6["CQ008"]["composer"]["cited_anchor_ids"])

    a_semantic = count_verdicts(adjudication["A5_semantic_verdicts"])
    b_semantic = count_verdicts(adjudication["B6_semantic_verdicts"])
    assert a_semantic == {
        "PASS": 5,
        "PARTIAL": 1,
        "FAIL_RETRIEVAL": 1,
        "FAIL_COMPOSITION": 0,
        "CRITICAL_ERROR": 1,
    }
    assert b_semantic == {
        "PASS": 6,
        "PARTIAL": 2,
        "FAIL_RETRIEVAL": 0,
        "FAIL_COMPOSITION": 0,
        "CRITICAL_ERROR": 0,
    }
    assert adjudication["semantic_summary"]["B6_semantic_improvements_vs_A5"] == 2
    assert adjudication["semantic_summary"]["B6_semantic_regressions_vs_A5"] == 0
    assert adjudication["semantic_summary"]["B6_new_critical_errors_vs_A5"] == 0
    assert adjudication["semantic_summary"]["frozen_final_promotion"] == "NOT_EARNED"
    assert adjudication["promotion_arithmetic"]["B6_PASS_count"] == 6
    assert adjudication["promotion_arithmetic"]["required_B6_PASS_count"] == 7
    assert adjudication["promotion_arithmetic"]["binding_failure"] == "B6_PASS_COUNT_6_LT_REQUIRED_7"

    assert adjudication["A5_semantic_verdicts"]["CQ001"]["verdict"] == "CRITICAL_ERROR"
    assert adjudication["B6_semantic_verdicts"]["CQ001"]["verdict"] == "PASS"
    assert adjudication["A5_semantic_verdicts"]["CQ008"]["verdict"] == "FAIL_RETRIEVAL"
    assert adjudication["B6_semantic_verdicts"]["CQ008"]["verdict"] == "PARTIAL"
    assert adjudication["B6_semantic_verdicts"]["CQ002"]["root_cause"] == "COMPOSITION_OVERCAUTIOUS_INSUFFICIENCY"
    assert adjudication["B6_semantic_verdicts"]["CQ008"]["root_cause"] == "COMPOSITION_EPISTEMIC_TYPE_OMISSION"

    assert run_final == {
        "artifact": {
            "digest": "sha256:7728781fd036fdb4b6531fdef2338761300b831b21e7b57627e71c53a0a08868",
            "id": 9390862358,
            "name": "e023-g1e-32324460519",
        },
        "conclusion": "success",
        "created_at": "2026-08-20T02:23:33Z",
        "execution_source_sha": EXECUTION_SOURCE,
        "run_attempt": 1,
        "run_id": RUN_ID,
        "status": "completed",
        "updated_at": "2026-08-20T02:24:58Z",
        "workflow": "E023 generality G1e",
    }

    assert "G1e strict promotion is NOT_EARNED" in result_doc
    assert "CRITICAL_ERROR -> PASS" in result_doc
    assert "0 semantic regressions" in result_doc
    assert "github.sha == '505740b74776fc7b7988e9c168c9c9d0ed2067fa'" in workflow

    output = {
        "model_calls": 0,
        "run_id": RUN_ID,
        "execution_source_sha": EXECUTION_SOURCE,
        "result_sha256": EXPECTED_SHA256,
        "frozen_semantic_calls": 16,
        "phase0_authority_gate": "PASS",
        "A5_semantic": a_semantic,
        "B6_semantic": b_semantic,
        "B6_semantic_improvements": 2,
        "B6_semantic_regressions": 0,
        "B6_new_critical_errors": 0,
        "strict_promotion": "NOT_EARNED",
        "binding_failure": "B6_PASS_COUNT_6_LT_REQUIRED_7",
        "evidence_budget_signal": "STRENGTHENED",
        "execution_source_locked": True,
        "semantic_calls_authorized": False,
        "top6_product_policy_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1e frozen result validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
