from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADJ = ROOT / "g1c-r1-adjudication-v0.json"
RESULT = ROOT / "evidence" / "g1c-r1-run-32232116273" / "result.json"
RESULT_SHA = ROOT / "evidence" / "g1c-r1-run-32232116273" / "result.sha256"

CATEGORIES = ["PASS", "PARTIAL", "FAIL_RETRIEVAL", "FAIL_COMPOSITION", "CRITICAL_ERROR"]


def tally(rows: dict) -> dict[str, int]:
    counter = Counter(row["verdict"] for row in rows.values())
    return {category: counter[category] for category in CATEGORIES}


def main() -> int:
    adj = json.loads(ADJ.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    sha_line = RESULT_SHA.read_text(encoding="utf-8").strip()

    assert adj["experiment"] == "E023-G1c-R1"
    assert adj["r1"]["run_id"] == 32232116273
    assert adj["r1"]["execution_source_sha"] == "5227ac2b3f93c4f807e388822bfff963d0041120"
    assert adj["r1"]["exact_model"] == "gpt-5.6-luna"
    assert adj["r1"]["model_call_attempts"] == 18
    assert adj["r1"]["semantic_rerolls"] == 0
    assert adj["r1"]["execution_complete"] is True
    assert adj["r1"]["retrieval_selection_verdict"] == "NOT_EARNED"

    expected_sha = "8f3e77163db92f7dff0b0a9aed5776c6dadd0eebfdb122fbfecf4313d0dae822"
    assert adj["r1"]["result_sha256"] == expected_sha
    assert sha_line.startswith(expected_sha + "  "), sha_line

    assert result["format"] == "E023-G1c-R1-v0"
    assert result["execution_complete"] is True
    assert result["model_call_attempts"] == 18
    assert result["retrieval_selection_verdict"] == "NOT_EARNED"
    assert result["execution_source_sha"] == adj["r1"]["execution_source_sha"]
    assert [row["question_id"] for row in result["B"]] == [f"AQ00{i}" for i in range(1, 7)]

    a = tally(adj["A_auxiliary_semantic_verdicts"])
    b = tally(adj["B_R1_semantic_verdicts"])
    assert a == adj["semantic_summary"]["A_auxiliary"], (a, adj["semantic_summary"])
    assert b == adj["semantic_summary"]["B_R1"], (b, adj["semantic_summary"])
    assert a == {
        "PASS": 3,
        "PARTIAL": 2,
        "FAIL_RETRIEVAL": 0,
        "FAIL_COMPOSITION": 0,
        "CRITICAL_ERROR": 1,
    }, a
    assert b == {
        "PASS": 2,
        "PARTIAL": 2,
        "FAIL_RETRIEVAL": 1,
        "FAIL_COMPOSITION": 0,
        "CRITICAL_ERROR": 1,
    }, b

    order = {"PASS": 4, "PARTIAL": 3, "FAIL_RETRIEVAL": 2, "FAIL_COMPOSITION": 2, "CRITICAL_ERROR": 0}
    improvements = 0
    regressions = 0
    new_critical = 0
    for qid in [f"AQ00{i}" for i in range(1, 7)]:
        av = adj["A_auxiliary_semantic_verdicts"][qid]["verdict"]
        bv = adj["B_R1_semantic_verdicts"][qid]["verdict"]
        if order[bv] > order[av]:
            improvements += 1
        elif order[bv] < order[av]:
            regressions += 1
        if bv == "CRITICAL_ERROR" and av != "CRITICAL_ERROR":
            new_critical += 1
    assert improvements == adj["semantic_summary"]["B_semantic_improvements_vs_A_auxiliary"] == 0
    assert regressions == adj["semantic_summary"]["B_semantic_regressions_vs_A_auxiliary"] == 1
    assert new_critical == adj["semantic_summary"]["B_new_critical_errors_vs_A_auxiliary"] == 0

    stage = adj["authority_stage_summary"]
    assert stage["candidate_pool_positive_authority_complete"] == "6/6"
    assert stage["selector_clean_improvements"] == ["AQ002"]
    assert stage["selector_regressions_from_candidate_pool"] == ["AQ001", "AQ004"]
    assert stage["strict_promotion"] == stage["targeted_signal_promotion"] == "NOT_EARNED"

    output = {
        "model_calls": 0,
        "run_id": adj["r1"]["run_id"],
        "result_sha256": expected_sha,
        "retrieval_selection_verdict": adj["r1"]["retrieval_selection_verdict"],
        "A_auxiliary": a,
        "B_R1": b,
        "B_semantic_improvements": improvements,
        "B_semantic_regressions": regressions,
        "B_new_critical_errors": new_critical,
        "candidate_pool_positive_authority_complete": stage["candidate_pool_positive_authority_complete"],
    }
    print("E023 G1c-R1 adjudication arithmetic: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
