from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "evidence" / "g1c-r1-run-32232116273" / "result.json"
CONTRACT_PATH = ROOT / "authority-sufficiency-v0" / "contract.json"
ANCHORS_PATH = ROOT / "authority-sufficiency-v0" / "anchors.jsonl"

RRF_K_SWEEP = [1, 5, 10, 20, 40, 60, 100, 200, 1000]
BUDGET_SWEEP = [3, 4, 5]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_anchors() -> dict[str, dict[str, Any]]:
    rows = [json.loads(line) for line in ANCHORS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["anchor_id"]: row for row in rows}


def evaluate_context(
    question_id: str,
    selected_anchor_ids: list[str],
    contract: dict[str, Any],
    anchors: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    question = contract["questions"][question_id]
    selected = set(selected_anchor_ids)
    clauses = []
    missing_clause_ids: list[str] = []

    for clause in question["clauses"]:
        allowed = set(clause["terminal_authority_types"])
        eligible = {
            anchor_id
            for anchor_id in clause["anchor_ids"]
            if anchors[anchor_id]["authority_type"] in allowed
        }
        clause_type = clause["type"]
        if clause_type == "all_of":
            satisfied = eligible <= selected
        elif clause_type == "any_of":
            satisfied = bool(eligible & selected)
        elif clause_type == "min_count":
            satisfied = len(eligible & selected) >= int(clause["min_count"])
        else:
            raise AssertionError(f"unknown_clause_type:{clause_type}")
        clauses.append({"clause_id": clause["clause_id"], "satisfied": satisfied})
        if not satisfied:
            missing_clause_ids.append(clause["clause_id"])

    forbidden = sorted(set(question["forbidden_conflation_anchor_ids"]) & selected)
    if missing_clause_ids:
        status = "INSUFFICIENT_AUTHORITY"
    elif forbidden:
        status = "SUFFICIENT_WITH_CONFLATION_RISK"
    else:
        status = "SUFFICIENT_CLEAN"

    return {
        "status": status,
        "clauses": clauses,
        "missing_clause_ids": missing_clause_ids,
        "forbidden_conflation_anchor_ids_present": forbidden,
    }


def rank_lists(row: dict[str, Any]) -> list[list[dict[str, Any]]]:
    return [row["initial_retrieval_ranking"], *[item["ranking"] for item in row["followup_retrieval"]]]


def rrf_select(row: dict[str, Any], *, k: int, budget: int) -> tuple[list[str], list[dict[str, Any]]]:
    candidate_ids = set(row["candidate_anchor_ids"])
    score: Counter[str] = Counter()
    appearances: Counter[str] = Counter()
    initial_rank = {item["anchor_id"]: item["rank"] for item in row["initial_retrieval_ranking"]}

    for ranking in rank_lists(row):
        for item in ranking:
            anchor_id = item["anchor_id"]
            if anchor_id not in candidate_ids:
                continue
            score[anchor_id] += 1.0 / (k + int(item["rank"]))
            appearances[anchor_id] += 1

    ordered = sorted(
        candidate_ids,
        key=lambda anchor_id: (
            -score[anchor_id],
            initial_rank.get(anchor_id, 10**9),
            anchor_id,
        ),
    )
    selected = ordered[:budget]
    trace = [
        {
            "anchor_id": anchor_id,
            "rrf_score": score[anchor_id],
            "retrieval_list_appearances": appearances[anchor_id],
            "initial_rank": initial_rank.get(anchor_id),
        }
        for anchor_id in ordered
    ]
    return selected, trace


def count_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(row["authority"]["status"] for row in rows)
    return {
        "SUFFICIENT_CLEAN": counts["SUFFICIENT_CLEAN"],
        "SUFFICIENT_WITH_CONFLATION_RISK": counts["SUFFICIENT_WITH_CONFLATION_RISK"],
        "INSUFFICIENT_AUTHORITY": counts["INSUFFICIENT_AUTHORITY"],
    }


def policy_rows(
    result_rows: list[dict[str, Any]],
    contract: dict[str, Any],
    anchors: dict[str, dict[str, Any]],
    *,
    policy: str,
    k: int | None = None,
    budget: int | None = None,
) -> list[dict[str, Any]]:
    out = []
    for row in result_rows:
        if policy == "initial":
            selected = list(row["initial_anchor_ids"])
            trace = None
        elif policy == "frozen_model_selector":
            selected = list(row["selected_anchor_ids"])
            trace = None
        elif policy == "candidate_all":
            selected = list(row["candidate_anchor_ids"])
            trace = None
        elif policy == "rrf":
            assert k is not None and budget is not None
            selected, trace = rrf_select(row, k=k, budget=budget)
        else:
            raise AssertionError(f"unknown_policy:{policy}")

        authority = evaluate_context(row["question_id"], selected, contract, anchors)
        out.append(
            {
                "question_id": row["question_id"],
                "selected_anchor_ids": selected,
                "authority": authority,
                "selection_trace": trace,
                "selected_characters": sum(len(anchors[anchor_id]["text"]) for anchor_id in selected),
            }
        )
    return out


def main() -> int:
    result = load_json(RESULT_PATH)
    contract = load_json(CONTRACT_PATH)
    anchors = load_anchors()
    rows = result["B"]

    assert result["format"] == "E023-G1c-R1-v0"
    assert result["execution_complete"] is True
    assert result["model_call_attempts"] == 18
    assert result["retrieval_selection_verdict"] == "NOT_EARNED"
    assert [row["question_id"] for row in rows] == [f"AQ00{i}" for i in range(1, 7)]

    initial = policy_rows(rows, contract, anchors, policy="initial")
    frozen_selector = policy_rows(rows, contract, anchors, policy="frozen_model_selector")
    candidate_all = policy_rows(rows, contract, anchors, policy="candidate_all")

    assert count_statuses(initial) == {
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 1,
        "INSUFFICIENT_AUTHORITY": 1,
    }
    assert count_statuses(frozen_selector) == {
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 0,
        "INSUFFICIENT_AUTHORITY": 2,
    }
    assert count_statuses(candidate_all)["INSUFFICIENT_AUTHORITY"] == 0

    sweep: dict[str, dict[str, Any]] = {}
    for k in RRF_K_SWEEP:
        for budget in BUDGET_SWEEP:
            key = f"k{k}_top{budget}"
            policy = policy_rows(rows, contract, anchors, policy="rrf", k=k, budget=budget)
            sweep[key] = {
                "counts": count_statuses(policy),
                "rows": policy,
            }

    canonical = sweep["k60_top4"]
    assert canonical["counts"] == {
        "SUFFICIENT_CLEAN": 6,
        "SUFFICIENT_WITH_CONFLATION_RISK": 0,
        "INSUFFICIENT_AUTHORITY": 0,
    }

    # Robustness check: the clean top-4 result must not depend on the conventional k=60 choice.
    for k in RRF_K_SWEEP:
        assert sweep[f"k{k}_top4"]["counts"] == canonical["counts"], (k, sweep[f"k{k}_top4"]["counts"])

    canonical_by_qid = {row["question_id"]: row for row in canonical["rows"]}
    assert "A003" in canonical_by_qid["AQ001"]["selected_anchor_ids"]
    assert "A004" not in canonical_by_qid["AQ001"]["selected_anchor_ids"]
    assert "A003" in canonical_by_qid["AQ002"]["selected_anchor_ids"]
    assert "A004" not in canonical_by_qid["AQ002"]["selected_anchor_ids"]
    assert {"A009", "A010", "A011"} <= set(canonical_by_qid["AQ004"]["selected_anchor_ids"])

    top3_counts = sweep["k60_top3"]["counts"]
    top5_counts = sweep["k60_top5"]["counts"]
    assert top3_counts["INSUFFICIENT_AUTHORITY"] > 0
    assert top5_counts["SUFFICIENT_WITH_CONFLATION_RISK"] > 0

    cutoff_margins = {}
    for row in rows:
        _, trace = rrf_select(row, k=60, budget=4)
        cutoff_margins[row["question_id"]] = trace[3]["rrf_score"] - trace[4]["rrf_score"]
    min_cutoff_question = min(cutoff_margins, key=cutoff_margins.get)

    output = {
        "model_calls": 0,
        "analysis_scope": "POSTHOC_FROZEN_G1C_R1_SELECTION_COUNTERFACTUAL",
        "selection_inputs": "retrieval_ranks_and_candidate_membership_only",
        "evaluator_used_for_selection": False,
        "initial_counts": count_statuses(initial),
        "candidate_all_counts": count_statuses(candidate_all),
        "frozen_model_selector_counts": count_statuses(frozen_selector),
        "rrf_k60_top3_counts": top3_counts,
        "rrf_k60_top4_counts": canonical["counts"],
        "rrf_k60_top5_counts": top5_counts,
        "rrf_top4_clean_for_all_k_values": RRF_K_SWEEP,
        "rrf_k60_top4_selected": {
            row["question_id"]: row["selected_anchor_ids"] for row in canonical["rows"]
        },
        "rrf_k60_top4_selected_characters": {
            row["question_id"]: row["selected_characters"] for row in canonical["rows"]
        },
        "rrf_k60_cutoff_margins": cutoff_margins,
        "minimum_cutoff_margin_question": min_cutoff_question,
        "minimum_cutoff_margin": cutoff_margins[min_cutoff_question],
        "promotion_authorized": False,
        "semantic_calls_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }

    print("E023 G1c-R1 zero-model selection counterfactual: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
