from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RUN_ID = 32353304896
EXECUTION_SOURCE = "3cf65d7255b8edc73a9d8cb3d13338e019cc92f8"
PREREG_MERGE = "080ac3d91d011be3ec16111bdc24eda9905f3d9c"
EVIDENCE_COMMIT = "c0a1cb01fbff29910c270283106217a111d00057"
EXPECTED_SHA256 = "f241d3059bb174aacff84f2e54ad30ed390fc575c8141a2965558fe93dd9adfa"
EVIDENCE = ROOT / "evidence" / f"g2-run-{RUN_ID}"
RESULT = EVIDENCE / "result.json"
RESULT_SHA = EVIDENCE / "result.sha256"
RUN_FINAL = EVIDENCE / "run-final.json"
ADJUDICATION = ROOT / "g2-adjudication-v0.json"
RESULT_DOC = ROOT / "g2-results-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g2.yml"

VERDICTS = ["PASS", "PARTIAL", "FAIL_RETRIEVAL", "FAIL_COMPOSITION", "CRITICAL_ERROR"]
FRESH = ["PQ001", "PQ002", "PQ003", "PQ004", "PQ005", "PQ006", "PQ008", "PQ009", "PQ010", "PQ012"]


def counts(rows: dict[str, dict]) -> dict[str, int]:
    c = Counter(row["verdict"] for row in rows.values())
    return {name: c[name] for name in VERDICTS}


def main() -> int:
    raw = RESULT.read_bytes()
    result = json.loads(raw)
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    run_final = json.loads(RUN_FINAL.read_text(encoding="utf-8"))
    result_doc = RESULT_DOC.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    assert RESULT_SHA.read_text(encoding="utf-8").split()[0] == EXPECTED_SHA256
    assert result["format"] == "E023-G2-v0"
    assert result["execute_model"] is True
    assert result["execution_complete"] is True
    assert result["execution_source_sha"] == EXECUTION_SOURCE
    assert result["prereg_merge_sha"] == PREREG_MERGE
    assert result["model"] == "gpt-5.6-luna"
    assert result["model_call_attempts"] == 29
    assert result["usage"]["model_calls"] == 29
    assert result["semantic_promotion"] == "PENDING_FROZEN_ADJUDICATION"
    assert result["request"]["projection_build_rebuild_calls"] == 5
    assert result["request"]["Q_composer_calls"] == 12
    assert result["request"]["P_composer_calls"] == 12
    assert result["request"]["planner_calls"] == 0
    assert result["request"]["selector_calls"] == 0
    assert result["request"]["vector_calls"] == 0
    assert result["request"]["rerolls"] == 0
    assert len(result["projection_builds"]) == 5
    assert all(row["contract_ok"] for row in result["projection_builds"])

    # Stale guards must reproduce exact Q terminal contexts.
    for qid in ["PQ007", "PQ011"]:
        pair = result["pairs"][qid]
        assert pair["P"]["selection_mode"] == "STALE_PROJECTION_BYPASS"
        assert pair["P"]["projection_used"] is False
        assert pair["P"]["selected_anchor_ids"] == pair["Q"]["selected_anchor_ids"]
        assert pair["P"]["context_sha256"] == pair["Q"]["context_sha256"]
        assert pair["P"]["prompt_sha256"] == pair["Q"]["prompt_sha256"]

    expected_q_status = {
        "PQ004": "INSUFFICIENT_AUTHORITY",
        "PQ007": "INSUFFICIENT_AUTHORITY",
        "PQ008": "INSUFFICIENT_AUTHORITY",
        "PQ011": "SUFFICIENT_CLEAN",
    }
    for qid, status in expected_q_status.items():
        assert result["pairs"][qid]["Q"]["authority"]["status"] == status

    assert result["pairs"]["PQ004"]["P"]["authority"]["status"] == "SUFFICIENT_WITH_CONFLATION_RISK"
    assert result["pairs"]["PQ008"]["P"]["authority"]["status"] == "INSUFFICIENT_AUTHORITY"
    assert result["pairs"]["PQ009"]["P"]["authority"]["status"] == "INSUFFICIENT_AUTHORITY"
    assert result["pairs"]["PQ012"]["P"]["authority"]["status"] == "INSUFFICIENT_AUTHORITY"

    p_chars = sum(result["pairs"][qid]["P"]["raw_evidence_chars"] for qid in FRESH)
    q_chars = sum(result["pairs"][qid]["Q"]["raw_evidence_chars"] for qid in FRESH)
    assert p_chars == 7019
    assert q_chars == 10282
    assert p_chars / q_chars <= 0.85

    q_sem = counts(adjudication["Q_semantic_verdicts"])
    p_sem = counts(adjudication["P_semantic_verdicts"])
    assert q_sem == {"PASS": 10, "PARTIAL": 0, "FAIL_RETRIEVAL": 0, "FAIL_COMPOSITION": 0, "CRITICAL_ERROR": 2}
    assert p_sem == {"PASS": 8, "PARTIAL": 0, "FAIL_RETRIEVAL": 1, "FAIL_COMPOSITION": 0, "CRITICAL_ERROR": 3}
    summary = adjudication["semantic_summary"]
    assert summary["P_paired_semantic_improvements_vs_Q"] == 2
    assert summary["P_paired_semantic_regressions_vs_Q"] == 3
    assert summary["P_new_critical_errors_vs_Q"] == 3
    assert summary["P_stale_or_unsupported_load_bearing_claims"] == 3
    assert summary["PQ011_primary_stale_negative_control"] == "PASS"
    assert summary["PQ012_post_rebuild_correction_verdict"] == "CRITICAL_ERROR"
    assert summary["frozen_final_promotion"] == "NOT_EARNED"

    authority = adjudication["authority_summary"]
    assert authority["required_opportunity_PQ004_improved"] is True
    assert authority["required_opportunity_PQ008_improved"] is False
    assert authority["P_authority_regressions_vs_Q"] == ["PQ009", "PQ012"]
    assert authority["PQ007_exact_stale_bypass"] is True
    assert authority["PQ011_exact_stale_bypass"] is True

    arithmetic = adjudication["promotion_arithmetic"]
    assert arithmetic["promotion"] == "NOT_EARNED"
    assert arithmetic["P_PASS_count"] == 8
    assert arithmetic["paired_semantic_improvements"] == 2
    assert arithmetic["paired_semantic_regressions"] == 3
    assert arithmetic["new_critical_errors"] == 3
    assert arithmetic["fresh_evidence_efficiency_passed"] is True
    assert "PQ008_REQUIRED_AUTHORITY_OPPORTUNITY_NOT_IMPROVED" in arithmetic["binding_failures"]
    assert "P_SEMANTIC_REGRESSIONS_3_GT_ALLOWED_0" in arithmetic["binding_failures"]

    assert run_final == {
        "artifact": {
            "digest": "sha256:f5c962274d67bd1d60164fc45218b78699e4e525d2b8cfea4b65db1c5f9a52a0",
            "id": 9400755044,
            "name": "e023-g2-32353304896",
        },
        "conclusion": "success",
        "created_at": "2026-08-20T09:19:37Z",
        "execution_source_sha": EXECUTION_SOURCE,
        "prereg_merge_sha": PREREG_MERGE,
        "run_attempt": 1,
        "run_id": RUN_ID,
        "status": "completed",
        "updated_at": "2026-08-20T09:22:54Z",
        "workflow": "E023 generality G2",
    }

    assert "G2 fixed-identity persistence promotion is NOT_EARNED" in result_doc
    assert "68.3%" in result_doc
    assert "PQ009: Q PASS -> P CRITICAL_ERROR" in result_doc
    assert "github.sha == '3cf65d7255b8edc73a9d8cb3d13338e019cc92f8'" in workflow

    output = {
        "model_calls": 0,
        "run_id": RUN_ID,
        "execution_source_sha": EXECUTION_SOURCE,
        "evidence_commit_sha": EVIDENCE_COMMIT,
        "result_sha256": EXPECTED_SHA256,
        "frozen_semantic_calls": 29,
        "Q_semantic": q_sem,
        "P_semantic": p_sem,
        "P_semantic_improvements": 2,
        "P_semantic_regressions": 3,
        "P_new_critical_errors": 3,
        "fresh_evidence_ratio": p_chars / q_chars,
        "stale_guard_passed": True,
        "strict_promotion": "NOT_EARNED",
        "execution_source_locked": True,
        "semantic_calls_authorized": False,
        "g2_product_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G2 frozen result validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
