from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_ID = 32215941344
RESULT = ROOT / "evidence" / f"run-{RUN_ID}" / "result.json"
ADJUDICATION = ROOT / "adjudication-v0.json"
QUESTIONS = ROOT / "corpus" / "questions.json"

TIERS = {
    "CRITICAL_ERROR": 0,
    "FAIL_RETRIEVAL": 1,
    "FAIL_COMPOSITION": 1,
    "PARTIAL": 2,
    "PASS": 3,
}


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))["questions"]
    qids = [row["question_id"] for row in questions]

    assert result["format"] == "E023-G1-v0"
    assert result["execute_model"] is True
    assert result["model"] == "gpt-5.6-luna"
    assert result["model_call_attempts"] == 30
    assert result["usage"]["model_calls"] == 30
    assert adjudication["run_id"] == RUN_ID
    assert adjudication["run_source_sha"] == "7315b858ed5ce764fa81ed131ee17f77c1ea11ae"

    by_arm = {
        arm: {row["question_id"]: row for row in result["arms"][arm]}
        for arm in ("A", "C")
    }
    for arm in ("A", "C"):
        assert sorted(by_arm[arm]) == qids
        assert sorted(adjudication["verdicts"][arm]) == qids
        assert all(row.get("contract_ok") is True for row in by_arm[arm].values())
        assert all(row.get("model_receipt", {}).get("model") == "gpt-5.6-luna" for row in by_arm[arm].values())
    assert all(row.get("planner_contract_ok") is True for row in by_arm["C"].values())
    assert all(row.get("planner_receipt", {}).get("model") == "gpt-5.6-luna" for row in by_arm["C"].values())

    # The four preregistered lexical gaps remained gaps in both arms.
    expected_gaps = {"Q001", "Q002", "Q004", "Q010"}
    for arm in ("A", "C"):
        observed = {qid for qid, row in by_arm[arm].items() if row["required_recall_at_5"] < 1.0}
        assert observed == expected_gaps, (arm, observed)

    # Q001's authoritative identity bridge remained absent in both arms.
    for arm in ("A", "C"):
        assert "S004" in by_arm[arm]["Q001"]["missing_required_sources"]
        assert "S005" in by_arm[arm]["Q001"]["forbidden_conflation_sources_in_context"]

    improvements = 0
    regressions = 0
    new_critical = 0
    counts: dict[str, dict[str, int]] = {arm: {name: 0 for name in TIERS} for arm in ("A", "C")}
    for qid in qids:
        a = adjudication["verdicts"]["A"][qid]["verdict"]
        c = adjudication["verdicts"]["C"][qid]["verdict"]
        assert a in TIERS and c in TIERS
        counts["A"][a] += 1
        counts["C"][c] += 1
        if TIERS[c] > TIERS[a]:
            improvements += 1
        elif TIERS[c] < TIERS[a]:
            regressions += 1
        if c == "CRITICAL_ERROR" and a != "CRITICAL_ERROR":
            new_critical += 1

    comparison = adjudication["comparison"]
    assert improvements == comparison["c_net_question_level_improvements"] == 0
    assert regressions == 0
    assert new_critical == comparison["c_new_critical_errors"] == 0
    assert comparison["g1_promotion"] == "NOT_EARNED"

    assert counts["A"] == {"CRITICAL_ERROR": 1, "FAIL_RETRIEVAL": 0, "FAIL_COMPOSITION": 0, "PARTIAL": 1, "PASS": 8}
    assert counts["C"] == counts["A"]

    print("E023 G1 adjudication arithmetic: PASS")
    print(json.dumps({
        "model_calls": result["model_call_attempts"],
        "A": counts["A"],
        "C": counts["C"],
        "c_improvements": improvements,
        "c_regressions": regressions,
        "c_new_critical_errors": new_critical,
        "g1_promotion": comparison["g1_promotion"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
