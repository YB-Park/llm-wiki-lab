from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "evidence" / "g1c-r1-run-32232116273" / "result.json"


def counts(statuses: list[str]) -> dict[str, int]:
    counter = Counter(statuses)
    return {
        "SUFFICIENT_CLEAN": counter["SUFFICIENT_CLEAN"],
        "SUFFICIENT_WITH_CONFLATION_RISK": counter["SUFFICIENT_WITH_CONFLATION_RISK"],
        "INSUFFICIENT_AUTHORITY": counter["INSUFFICIENT_AUTHORITY"],
    }


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["format"] == "E023-G1c-R1-v0"
    assert result["execution_complete"] is True
    assert result["model_call_attempts"] == 18
    rows = {row["question_id"]: row for row in result["B"]}
    assert sorted(rows) == [f"AQ00{i}" for i in range(1, 7)]

    initial = counts([rows[qid]["initial_authority"]["status"] for qid in sorted(rows)])
    candidate = counts([rows[qid]["candidate_authority"]["status"] for qid in sorted(rows)])
    final = counts([rows[qid]["final_authority"]["status"] for qid in sorted(rows)])

    transitions = {
        qid: {
            "initial": rows[qid]["initial_authority"]["status"],
            "candidate": rows[qid]["candidate_authority"]["status"],
            "final": rows[qid]["final_authority"]["status"],
        }
        for qid in sorted(rows)
    }

    assert initial == {
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 1,
        "INSUFFICIENT_AUTHORITY": 1,
    }, initial
    assert candidate == {
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 2,
        "INSUFFICIENT_AUTHORITY": 0,
    }, candidate
    assert final == {
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 0,
        "INSUFFICIENT_AUTHORITY": 2,
    }, final

    assert transitions["AQ001"] == {
        "initial": "INSUFFICIENT_AUTHORITY",
        "candidate": "SUFFICIENT_WITH_CONFLATION_RISK",
        "final": "INSUFFICIENT_AUTHORITY",
    }
    assert transitions["AQ002"] == {
        "initial": "SUFFICIENT_WITH_CONFLATION_RISK",
        "candidate": "SUFFICIENT_WITH_CONFLATION_RISK",
        "final": "SUFFICIENT_CLEAN",
    }
    assert transitions["AQ004"] == {
        "initial": "SUFFICIENT_CLEAN",
        "candidate": "SUFFICIENT_CLEAN",
        "final": "INSUFFICIENT_AUTHORITY",
    }

    candidate_positive_complete = sum(
        int(rows[qid]["candidate_authority"]["status"] != "INSUFFICIENT_AUTHORITY")
        for qid in rows
    )
    assert candidate_positive_complete == 6

    output = {
        "model_calls": 0,
        "status": "POSTHOC_STAGE_DECOMPOSITION_DOES_NOT_CHANGE_FROZEN_VERDICT",
        "initial_counts": initial,
        "candidate_counts": candidate,
        "final_counts": final,
        "candidate_positive_authority_complete": "6/6",
        "retrieval_candidate_improvement": ["AQ001"],
        "selector_clean_improvement": ["AQ002"],
        "selector_regressions_from_candidate_pool": ["AQ001", "AQ004"],
        "transitions": transitions,
        "frozen_retrieval_selection_verdict": result["retrieval_selection_verdict"],
    }
    assert output["frozen_retrieval_selection_verdict"] == "NOT_EARNED"

    print("E023 G1c-R1 zero-model stage analysis: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
