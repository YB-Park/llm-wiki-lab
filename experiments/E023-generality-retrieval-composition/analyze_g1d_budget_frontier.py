from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from g1d_common import evaluate_context

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "evidence" / "g1d-run-32322429563" / "result.json"
CONTRACT = ROOT / "authority-sufficiency-v1" / "contract.json"
ANCHORS = ROOT / "authority-sufficiency-v1" / "anchors.jsonl"
ADJUDICATION = ROOT / "g1d-adjudication-v0.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def counts(statuses: dict[str, str]) -> dict[str, int]:
    c = Counter(statuses.values())
    return {
        "SUFFICIENT_CLEAN": c["SUFFICIENT_CLEAN"],
        "SUFFICIENT_WITH_CONFLATION_RISK": c["SUFFICIENT_WITH_CONFLATION_RISK"],
        "INSUFFICIENT_AUTHORITY": c["INSUFFICIENT_AUTHORITY"],
    }


def main() -> int:
    result = load_json(RESULT)
    contract = load_json(CONTRACT)
    anchor_map = {row["anchor_id"]: row for row in load_jsonl(ANCHORS)}
    adjudication = load_json(ADJUDICATION)

    assert result["format"] == "E023-G1d-v0"
    assert result["execution_complete"] is True
    assert result["model_call_attempts"] == 24
    assert result["retrieval_selection_verdict"] == "NOT_EARNED"

    a_rows = {row["question_id"]: row for row in result["arms"]["A"]}
    d_rows = {row["question_id"]: row for row in result["arms"]["D"]}
    qids = [f"BQ00{i}" for i in range(1, 9)]
    assert sorted(a_rows) == qids
    assert sorted(d_rows) == qids

    frontier: dict[str, dict] = {}
    for k in range(3, 9):
        statuses = {}
        selected = {}
        for qid in qids:
            ranking = a_rows[qid]["retrieval_ranking"]
            ids = [item["anchor_id"] for item in ranking[:k]]
            statuses[qid] = evaluate_context(qid, ids, contract, anchor_map)["status"]
            selected[qid] = ids
        frontier[f"A@{k}"] = {
            "counts": counts(statuses),
            "statuses": statuses,
            "selected_anchor_ids": selected,
        }

    assert frontier["A@5"]["counts"] == {
        "SUFFICIENT_CLEAN": 3,
        "SUFFICIENT_WITH_CONFLATION_RISK": 4,
        "INSUFFICIENT_AUTHORITY": 1,
    }
    assert frontier["A@6"]["counts"] == {
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 4,
        "INSUFFICIENT_AUTHORITY": 0,
    }
    for k in (6, 7, 8):
        assert frontier[f"A@{k}"]["counts"]["INSUFFICIENT_AUTHORITY"] == 0

    # BQ006 is the sole A@5 positive-authority miss and its governing policy sits one rank outside the cutoff.
    bq006_exact = {item["anchor_id"]: item["rank"] for item in a_rows["BQ006"]["retrieval_ranking"]}
    assert bq006_exact["B013"] == 6
    assert frontier["A@5"]["statuses"]["BQ006"] == "INSUFFICIENT_AUTHORITY"
    assert frontier["A@6"]["statuses"]["BQ006"] == "SUFFICIENT_CLEAN"

    bq006_d = d_rows["BQ006"]
    assert "Cedar" in bq006_d["planner"]["missing_or_ambiguous_relation"]
    assert "B013" not in bq006_d["candidate_anchor_ids"]
    followup_positions = []
    for item in bq006_d["followup_retrieval"]:
        ranks = {row["anchor_id"]: row["rank"] for row in item["ranking"]}
        followup_positions.append(ranks.get("B013"))
    assert followup_positions[0] == 4
    assert followup_positions[1] is None

    # The four A@5 risk contexts were all semantically handled without conflation in the frozen adjudication.
    risk_qids = [
        qid
        for qid, status in frontier["A@5"]["statuses"].items()
        if status == "SUFFICIENT_WITH_CONFLATION_RISK"
    ]
    assert risk_qids == ["BQ001", "BQ002", "BQ007", "BQ008"]
    assert all(adjudication["A_semantic_verdicts"][qid]["verdict"] == "PASS" for qid in risk_qids)

    # D spent planner calls but did not improve authority status and regressed one question.
    assert result["selection_metrics"]["authority_improvements"] == 0
    assert result["selection_metrics"]["authority_regressions"] == 1
    assert result["selection_metrics"]["d_insufficient"] == 2

    output = {
        "model_calls": 0,
        "analysis_scope": "POSTHOC_FROZEN_G1D_EVIDENCE_BUDGET_FRONTIER",
        "A_frontier_counts": {key: row["counts"] for key, row in frontier.items()},
        "A_top5_risk_question_ids": risk_qids,
        "A_top5_risk_semantic_verdicts": {
            qid: adjudication["A_semantic_verdicts"][qid]["verdict"] for qid in risk_qids
        },
        "BQ006_governing_policy_anchor": "B013",
        "BQ006_B013_exact_rank": bq006_exact["B013"],
        "BQ006_B013_followup_ranks": followup_positions,
        "BQ006_present_in_D_candidate_pool": False,
        "D_planner_calls": result["request"]["d_planner_calls"],
        "D_authority_improvements": result["selection_metrics"]["authority_improvements"],
        "D_authority_regressions": result["selection_metrics"]["authority_regressions"],
        "interpretation": (
            "On this frozen slice, expanding exact BM25 from top-5 to top-6 removes the only positive-authority insufficiency, "
            "while evidence-follow planner plus RRF does not. This is a zero-model evidence-budget signal, not semantic promotion."
        ),
        "next_paid_run_authorized": False,
        "same_slice_semantic_rerun_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1d zero-model evidence-budget frontier: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
