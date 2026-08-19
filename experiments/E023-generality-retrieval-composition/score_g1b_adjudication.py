from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_ID = 32217824760
RESULT = ROOT / "evidence" / f"g1b-run-{RUN_ID}" / "result.json"
ADJUDICATION = ROOT / "g1b-adjudication-v0.json"
TARGETS = ["Q001", "Q002", "Q004", "Q010"]

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

    assert result["format"] == "E023-G1b-v0"
    assert result["execute_model"] is True
    assert result["model"] == "gpt-5.6-luna"
    assert result["model_call_attempts"] == 12
    assert result["usage"]["model_calls"] == 12
    assert result["execution_source_sha"] == "7c604dd8d57a90c99526bdce5fb55fe7cdb7056f"
    assert adjudication["run_id"] == RUN_ID
    assert adjudication["result_sha256"] == "0b092a1b85577a12bb664fc9bee31a648b316fc317277d35454a9a72c0b7c2c1"

    rows = {row["question_id"]: row for row in result["targets"]}
    assert list(rows) == TARGETS
    assert all(row.get("planner_contract_ok") is True for row in rows.values())
    assert all(row.get("selector_contract_ok") is True for row in rows.values())
    assert all(row.get("composer_contract_ok") is True for row in rows.values())
    assert all(row.get("planner_receipt", {}).get("model") == "gpt-5.6-luna" for row in rows.values())
    assert all(row.get("selector_receipt", {}).get("model") == "gpt-5.6-luna" for row in rows.values())
    assert all(row.get("composer_receipt", {}).get("model") == "gpt-5.6-luna" for row in rows.values())

    candidate_recovery = 0
    final_recovery = 0
    improvements = 0
    regressions = 0
    new_critical = 0
    for qid in TARGETS:
        row = rows[qid]
        missing = set(row["previously_missing_required_sources_for_measurement_only"])
        candidate = set(row["candidate_source_ids"])
        final = set(row["selected_source_ids"])
        observed_candidate = missing <= candidate
        observed_final = missing <= final
        verdict = adjudication["verdicts"][qid]
        assert observed_candidate is verdict["candidate_recovered_previously_missing_source"]
        assert observed_final is verdict["final_selected_previously_missing_source"]
        candidate_recovery += int(observed_candidate)
        final_recovery += int(observed_final)

        previous = verdict["previous_verdict"]
        current = verdict["verdict"]
        assert previous in TIERS and current in TIERS
        if TIERS[current] > TIERS[previous]:
            improvements += 1
        elif TIERS[current] < TIERS[previous]:
            regressions += 1
        if current == "CRITICAL_ERROR" and previous != "CRITICAL_ERROR":
            new_critical += 1

    comparison = adjudication["comparison"]
    assert candidate_recovery == comparison["candidate_pool_missing_source_recovery_count"] == 2
    assert final_recovery == comparison["final_context_missing_source_recovery_count"] == 1
    assert improvements == comparison["semantic_improvements"] == 1
    assert regressions == comparison["semantic_regressions"] == 0
    assert new_critical == comparison["new_critical_errors"] == 0
    assert comparison["g1b_promotion"] == "NOT_EARNED"
    assert all(adjudication["verdicts"][qid]["verdict"] == "PASS" for qid in TARGETS)

    # Frozen promotion condition 1 required >=3/4 final missing-source recovery.
    assert final_recovery < 3

    print("E023 G1b adjudication arithmetic: PASS")
    print(json.dumps({
        "model_calls": result["model_call_attempts"],
        "semantic_verdicts": {qid: adjudication["verdicts"][qid]["verdict"] for qid in TARGETS},
        "semantic_improvements": improvements,
        "semantic_regressions": regressions,
        "candidate_missing_source_recovery": f"{candidate_recovery}/4",
        "final_missing_source_recovery": f"{final_recovery}/4",
        "g1b_promotion": comparison["g1b_promotion"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
