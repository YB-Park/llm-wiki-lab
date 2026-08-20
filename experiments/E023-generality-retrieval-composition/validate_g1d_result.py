from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
EVIDENCE = ROOT / "evidence" / "g1d-run-32322429563"
RESULT = EVIDENCE / "result.json"
RESULT_SHA = EVIDENCE / "result.sha256"
RUN_FINAL = EVIDENCE / "run-final.json"
ADJUDICATION = ROOT / "g1d-adjudication-v0.json"
RESULT_DOC = ROOT / "g1d-results-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1d.yml"

EXPECTED_SHA256 = "ef57c7a43c782694a0c42d428421b5d9a4bbb72b0a48b52a60c36edafa310bda"
EXECUTION_SOURCE = "c74673a83744789f271fa54c43b20212160007a2"
RUN_ID = 32322429563


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

    actual_sha = hashlib.sha256(raw).hexdigest()
    assert actual_sha == EXPECTED_SHA256
    assert RESULT_SHA.read_text(encoding="utf-8").split()[0] == EXPECTED_SHA256

    assert result["format"] == "E023-G1d-v0"
    assert result["execute_model"] is True
    assert result["execution_complete"] is True
    assert result["execution_source_sha"] == EXECUTION_SOURCE
    assert result["model"] == "gpt-5.6-luna"
    assert result["model_call_attempts"] == 24
    assert result["usage"]["model_calls"] == 24
    assert result["request"]["d_selector_calls"] == 0
    assert result["request"]["rrf_k"] == 60
    assert result["request"]["final_top_k"] == 4
    assert result["retrieval_selection_verdict"] == "NOT_EARNED"

    expected_statuses = {
        "BQ001": ("SUFFICIENT_WITH_CONFLATION_RISK", "SUFFICIENT_WITH_CONFLATION_RISK"),
        "BQ002": ("SUFFICIENT_WITH_CONFLATION_RISK", "INSUFFICIENT_AUTHORITY"),
        "BQ003": ("SUFFICIENT_CLEAN", "SUFFICIENT_CLEAN"),
        "BQ004": ("SUFFICIENT_CLEAN", "SUFFICIENT_CLEAN"),
        "BQ005": ("SUFFICIENT_CLEAN", "SUFFICIENT_CLEAN"),
        "BQ006": ("INSUFFICIENT_AUTHORITY", "INSUFFICIENT_AUTHORITY"),
        "BQ007": ("SUFFICIENT_WITH_CONFLATION_RISK", "SUFFICIENT_WITH_CONFLATION_RISK"),
        "BQ008": ("SUFFICIENT_WITH_CONFLATION_RISK", "SUFFICIENT_WITH_CONFLATION_RISK"),
    }
    assert {
        qid: (row["A"], row["D"])
        for qid, row in result["selection_metrics"]["authority_statuses"].items()
    } == expected_statuses
    assert result["selection_metrics"]["authority_improvements"] == 0
    assert result["selection_metrics"]["authority_regressions"] == 1
    assert result["selection_metrics"]["d_clean"] == 3
    assert result["selection_metrics"]["d_insufficient"] == 2

    d_by_q = {row["question_id"]: row for row in result["arms"]["D"]}
    assert "B003" in d_by_q["BQ002"]["candidate_anchor_ids"]
    assert "B003" not in d_by_q["BQ002"]["selected_anchor_ids"]
    assert d_by_q["BQ002"]["rrf_trace"][4]["anchor_id"] == "B003"
    assert "B013" not in d_by_q["BQ006"]["candidate_anchor_ids"]
    assert "Cedar" in d_by_q["BQ006"]["planner"]["missing_or_ambiguous_relation"]
    assert "B019" in d_by_q["BQ007"]["selected_anchor_ids"]
    assert "B023" in d_by_q["BQ008"]["selected_anchor_ids"]

    assert adjudication["run"]["run_id"] == RUN_ID
    assert adjudication["run"]["result_sha256"] == EXPECTED_SHA256
    assert adjudication["run"]["retrieval_selection_verdict"] == "NOT_EARNED"
    assert count_verdicts(adjudication["A_semantic_verdicts"]) == {
        "PASS": 7,
        "PARTIAL": 0,
        "FAIL_RETRIEVAL": 0,
        "FAIL_COMPOSITION": 0,
        "CRITICAL_ERROR": 1,
    }
    assert count_verdicts(adjudication["D_semantic_verdicts"]) == {
        "PASS": 5,
        "PARTIAL": 2,
        "FAIL_RETRIEVAL": 0,
        "FAIL_COMPOSITION": 0,
        "CRITICAL_ERROR": 1,
    }
    assert adjudication["D_semantic_verdicts"]["BQ002"]["verdict"] == "PARTIAL"
    assert adjudication["D_semantic_verdicts"]["BQ004"]["verdict"] == "PARTIAL"
    assert adjudication["A_semantic_verdicts"]["BQ006"]["verdict"] == "CRITICAL_ERROR"
    assert adjudication["D_semantic_verdicts"]["BQ006"]["verdict"] == "CRITICAL_ERROR"
    assert adjudication["semantic_summary"]["D_semantic_improvements_vs_A"] == 0
    assert adjudication["semantic_summary"]["D_semantic_regressions_vs_A"] == 2
    assert adjudication["semantic_summary"]["D_new_critical_errors_vs_A"] == 0

    assert run_final == {
        "artifact": {
            "digest": "sha256:c6c69d06df4a66febbbfb0dde37dde9ead4a6d705e30853ce87ca0942bb5ba09",
            "id": 9390249066,
            "name": "e023-g1d-32322429563",
        },
        "conclusion": "success",
        "created_at": "2026-08-20T01:49:54Z",
        "execution_source_sha": EXECUTION_SOURCE,
        "run_attempt": 1,
        "run_id": RUN_ID,
        "status": "completed",
        "updated_at": "2026-08-20T01:51:55Z",
        "workflow": "E023 generality G1d",
    }

    assert "G1d selection promotion is NOT_EARNED" in result_doc
    assert "truth-by-luck compliance conclusion" in result_doc.lower()
    assert "github.sha == 'c74673a83744789f271fa54c43b20212160007a2'" in workflow

    output = {
        "model_calls": 0,
        "run_id": RUN_ID,
        "execution_source_sha": EXECUTION_SOURCE,
        "result_sha256": EXPECTED_SHA256,
        "frozen_model_calls": 24,
        "selection_promotion": "NOT_EARNED",
        "D_authority_improvements": 0,
        "D_authority_regressions": 1,
        "D_clean": 3,
        "D_insufficient": 2,
        "A_semantic": count_verdicts(adjudication["A_semantic_verdicts"]),
        "D_semantic": count_verdicts(adjudication["D_semantic_verdicts"]),
        "D_new_critical_errors": 0,
        "execution_source_locked": True,
        "semantic_calls_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1d frozen result validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
