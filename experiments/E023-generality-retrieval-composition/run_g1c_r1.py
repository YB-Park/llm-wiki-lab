from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REQUEST_PATH = REPO / "remote-lab" / "e023-g1c-r1-request.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e023-g1c-r1"
MODEL = "gpt-5.6-luna"
QUESTION_IDS = [f"AQ00{i}" for i in range(1, 7)]
BASELINE_CLEAN = {"AQ003", "AQ004", "AQ005", "AQ006"}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"import_failed:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V0 = _load_module("e023_g1c_v0", HERE / "run_g1c.py")


def load_request() -> dict[str, Any]:
    request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    expected = {
        "b_composer_calls": 6,
        "b_planner_calls": 6,
        "b_selector_calls": 6,
        "candidate_followup_top_k": 3,
        "final_anchor_limit": 5,
        "initial_top_k": 5,
        "max_ai_credits_per_call": 30,
        "max_followup_queries": 2,
        "max_model_call_attempts": 18,
        "model": MODEL,
        "planner_snippet_chars": 320,
        "question_count": 6,
        "request_id": "e023-g1c-r1-b-only-recovery-v0",
    }
    if request != expected:
        raise SystemExit(f"E023-G1C-R1-STOP request_mismatch actual={request}")
    return request


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def aggregate_verdict(rows: list[dict[str, Any]]) -> str:
    by_q = {row["question_id"]: row for row in rows}
    if sorted(by_q) != QUESTION_IDS:
        return "NOT_EXECUTED"
    if not all(
        row.get("planner_contract_ok")
        and row.get("selector_contract_ok")
        and isinstance(row.get("final_authority"), dict)
        for row in rows
    ):
        return "NOT_EXECUTED"

    if all(
        row["final_authority"]["status"] == "SUFFICIENT_CLEAN"
        and len(row.get("selected_anchor_ids", [])) <= 5
        for row in rows
    ):
        return "EARNED_FOR_BROADER_G1_CONSIDERATION"

    clean_count = sum(
        int(row["final_authority"]["status"] == "SUFFICIENT_CLEAN")
        for row in rows
    )
    no_clean_regression = all(
        by_q[qid]["final_authority"]["status"] == "SUFFICIENT_CLEAN"
        for qid in BASELINE_CLEAN
    )
    no_new_risk_on_clean = all(
        by_q[qid]["final_authority"]["forbidden_conflation_anchor_ids_present"] == []
        for qid in BASELINE_CLEAN
    )
    if clean_count > 4 and no_clean_regression and no_new_risk_on_clean:
        return "TARGETED_SIGNAL_ONLY"
    return "NOT_EARNED"


def update_attempts(result: dict[str, Any], model_runner: Any) -> None:
    result["model_call_attempts"] = model_runner.attempts
    result["usage"]["model_calls"] = model_runner.attempts


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()

    request = load_request()
    anchors = V0.load_jsonl(V0.PKG / "anchors.jsonl")
    questions_doc = V0.load_json(V0.PKG / "questions.json")
    contract = V0.load_json(V0.PKG / "contract.json")
    question_by_id = {
        row["question_id"]: row
        for row in questions_doc["questions"]
    }
    anchor_map = {row["anchor_id"]: row for row in anchors}

    assert sorted(question_by_id) == QUESTION_IDS
    assert request["question_count"] == len(QUESTION_IDS)

    result: dict[str, Any] = {
        "format": "E023-G1c-R1-v0",
        "recovery_of": {
            "experiment": "E023-G1c-v0",
            "run_id": 32229563330,
            "source_sha": "987ee7ec615f7eb869be59f14a1928a3811baeed",
            "status": "INVALID_EXECUTION",
        },
        "execute_model": args.execute_model,
        "model": request["model"] if args.execute_model else None,
        "execution_source_sha": os.environ.get("GITHUB_SHA", ""),
        "request": request,
        "baseline_A_authority_statuses": {
            qid: V0.G1C.EXPECTED[qid]["status"]
            for qid in QUESTION_IDS
        },
        "model_call_attempts": 0,
        "usage": {
            "model_calls": 0,
            "tokens": "unavailable_unless_transport_exposes_machine_readable_usage",
            "ai_credits_or_premium_requests": "unavailable_do_not_infer",
        },
        "B": [],
        "execution_complete": False,
        "retrieval_selection_verdict": "NOT_EXECUTED",
        "interpretation_boundary": (
            "G1c-R1 is a new B-only recovery replication after invalid G1c v0 execution. "
            "It reuses frozen G1c retrieval/composition semantics and cannot authorize G2/G3."
        ),
    }
    save_result(result)
    model_runner = V0.G1.ModelRunner(request) if args.execute_model else None

    for question_id in QUESTION_IDS:
        question = question_by_id[question_id]
        ranking = V0.G1C.bm25_ranking(anchors, question["question"])
        initial_ids = [
            anchor_id
            for anchor_id, _ in ranking[: request["initial_top_k"]]
        ]
        assert initial_ids == V0.G1C.EXPECTED[question_id]["top5"], (
            question_id,
            initial_ids,
            V0.G1C.EXPECTED[question_id]["top5"],
        )

        row: dict[str, Any] = {
            "question_id": question_id,
            "question": question["question"],
            "initial_anchor_ids": initial_ids,
            "initial_authority": V0.authority_eval(contract, question_id, initial_ids),
            "initial_retrieval_ranking": [
                {"rank": rank, "anchor_id": anchor_id, "score": score}
                for rank, (anchor_id, score) in enumerate(ranking, start=1)
            ],
            "stage": "INITIAL_PERSISTED",
        }
        result["B"].append(row)
        save_result(result)

        if not args.execute_model:
            row["not_executed"] = "planner_selector_composer_require_model"
            row["stage"] = "ZERO_MODEL_PREFLIGHT_ONLY"
            save_result(result)
            continue

        initial_view = V0.candidate_view(
            anchor_map,
            initial_ids,
            question=question["question"],
            initial_ids=set(initial_ids),
            snippet_chars=request["planner_snippet_chars"],
        )
        try:
            receipt = model_runner.call(
                V0.planner_prompt(question["question"], initial_view)
            )
            update_attempts(result, model_runner)
            row["planner_receipt"] = {
                k: v for k, v in receipt.items() if k != "text"
            }
            row["planner"] = V0.parse_planner(
                receipt["text"],
                max_queries=request["max_followup_queries"],
            )
            row["planner_contract_ok"] = True
            row["stage"] = "PLANNER_PERSISTED"
            save_result(result)
        except Exception as exc:
            update_attempts(result, model_runner)
            row["planner_contract_ok"] = False
            row["planner_error"] = str(exc)
            row["stage"] = "PLANNER_FAILED"
            save_result(result)
            continue

        followup_rankings = [
            V0.G1C.bm25_ranking(anchors, query)
            for query in row["planner"]["queries"]
        ]
        row["followup_retrieval"] = [
            {
                "query": query,
                "ranking": [
                    {"rank": rank, "anchor_id": anchor_id, "score": score}
                    for rank, (anchor_id, score) in enumerate(followup, start=1)
                ],
            }
            for query, followup in zip(
                row["planner"]["queries"], followup_rankings
            )
        ]
        candidate_ids = V0.build_candidate_pool(
            initial_ids,
            followup_rankings,
            request["candidate_followup_top_k"],
        )
        row["candidate_anchor_ids"] = candidate_ids
        row["candidate_authority"] = V0.authority_eval(
            contract, question_id, candidate_ids
        )
        row["stage"] = "CANDIDATES_PERSISTED"
        save_result(result)

        candidate_view = V0.candidate_view(
            anchor_map,
            candidate_ids,
            question=question["question"],
            initial_ids=set(initial_ids),
            snippet_chars=request["planner_snippet_chars"],
        )
        try:
            receipt = model_runner.call(
                V0.selector_prompt(
                    question["question"],
                    row["planner"]["missing_or_ambiguous_relation"],
                    candidate_view,
                    final_limit=request["final_anchor_limit"],
                )
            )
            update_attempts(result, model_runner)
            row["selector_receipt"] = {
                k: v for k, v in receipt.items() if k != "text"
            }
            selected = V0.parse_selector(
                receipt["text"],
                allowed_ids=set(candidate_ids),
                final_limit=request["final_anchor_limit"],
            )
            row["selected_anchor_ids"] = selected
            row["selector_contract_ok"] = True
            row["final_authority"] = V0.authority_eval(
                contract, question_id, selected
            )
            row["stage"] = "SELECTOR_PERSISTED"
            save_result(result)
        except Exception as exc:
            update_attempts(result, model_runner)
            row["selector_contract_ok"] = False
            row["selector_error"] = str(exc)
            row["stage"] = "SELECTOR_FAILED"
            save_result(result)
            continue

        try:
            receipt = model_runner.call(
                V0.composer_prompt(
                    question["question"],
                    V0.evidence_context(anchor_map, selected),
                )
            )
            update_attempts(result, model_runner)
            row["composer_receipt"] = {
                k: v for k, v in receipt.items() if k != "text"
            }
            row["composer"] = V0.parse_composer(
                receipt["text"], set(selected)
            )
            row["composer_contract_ok"] = True
            row["stage"] = "COMPOSER_PERSISTED"
            save_result(result)
        except Exception as exc:
            update_attempts(result, model_runner)
            row["composer_contract_ok"] = False
            row["composer_error"] = str(exc)
            row["stage"] = "COMPOSER_FAILED"
            save_result(result)

    result["retrieval_selection_verdict"] = aggregate_verdict(result["B"])
    if model_runner is not None:
        update_attempts(result, model_runner)
    result["execution_complete"] = bool(
        args.execute_model
        and len(result["B"]) == 6
        and all(
            row.get("planner_contract_ok")
            and row.get("selector_contract_ok")
            and row.get("composer_contract_ok")
            for row in result["B"]
        )
        and model_runner is not None
        and model_runner.attempts == request["max_model_call_attempts"]
    )
    save_result(result)

    summary = {
        "format": result["format"],
        "execute_model": args.execute_model,
        "model_call_attempts": result["model_call_attempts"],
        "execution_complete": result["execution_complete"],
        "B_statuses": {
            row["question_id"]: row.get("final_authority", {}).get("status")
            for row in result["B"]
        },
        "retrieval_selection_verdict": result["retrieval_selection_verdict"],
        "usage": result["usage"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

    if args.execute_model and not result["execution_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
