from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

from g1d_common import bm25_ranking, evaluate_context, rrf_select

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PKG = HERE / "authority-sufficiency-v1"
REQUEST_PATH = REPO / "remote-lab" / "e023-g1d-request.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e023-g1d"
MODEL = "gpt-5.6-luna"
B_ID_RE = re.compile(r"^B\d{3}$")
B_ID_ANY_RE = re.compile(r"\bB\d{3}\b")

EXPECTED_A_TOP5 = {
    "BQ001": ["B005", "B002", "B001", "B004", "B003"],
    "BQ002": ["B004", "B005", "B001", "B003", "B002"],
    "BQ003": ["B007", "B008", "B006", "B018", "B017"],
    "BQ004": ["B009", "B011", "B010", "B012", "B022"],
    "BQ005": ["B012", "B009", "B010", "B019", "B011"],
    "BQ006": ["B014", "B015", "B023", "B016", "B021"],
    "BQ007": ["B017", "B016", "B018", "B019", "B007"],
    "BQ008": ["B021", "B022", "B020", "B023", "B013"],
}
STATUS_ORDER = {
    "INSUFFICIENT_AUTHORITY": 0,
    "SUFFICIENT_WITH_CONFLATION_RISK": 1,
    "SUFFICIENT_CLEAN": 2,
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"import_failed:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G1 = _load_module("e023_g1_transport_for_g1d", HERE / "run_g1.py")
G1C = _load_module("e023_g1c_prompt_semantics_for_g1d", HERE / "run_g1c.py")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_request() -> dict[str, Any]:
    request = load_json(REQUEST_PATH)
    expected = {
        "request_id": "e023-g1d-deterministic-selection-v0",
        "model": MODEL,
        "question_count": 8,
        "initial_top_k": 5,
        "max_followup_queries": 2,
        "candidate_followup_top_k": 3,
        "rrf_k": 60,
        "final_top_k": 4,
        "planner_snippet_chars": 320,
        "a_composer_calls": 8,
        "d_planner_calls": 8,
        "d_composer_calls": 8,
        "d_selector_calls": 0,
        "max_model_call_attempts": 24,
        "max_ai_credits_per_call": 30,
    }
    if request != expected:
        raise SystemExit(f"E023-G1D-STOP request_mismatch actual={request}")
    return request


def planner_prompt(question: str, initial_view: str) -> str:
    # Semantic instructions are unchanged from G1c; only the frozen handle syntax changes Axxx -> Bxxx.
    return G1C.planner_prompt(question, initial_view).replace("Axxx", "Bxxx")


def parse_planner(text: str, *, max_queries: int) -> dict[str, Any]:
    row = json.loads(text)
    if not isinstance(row, dict) or set(row) != {"missing_or_ambiguous_relation", "queries"}:
        raise ValueError("g1d_planner_shape_invalid")
    relation = row["missing_or_ambiguous_relation"]
    queries = row["queries"]
    if not isinstance(relation, str) or not relation.strip() or len(relation.strip()) > 240:
        raise ValueError("g1d_planner_relation_invalid")
    if not isinstance(queries, list) or not 0 <= len(queries) <= max_queries:
        raise ValueError("g1d_planner_query_count_invalid")
    out = []
    seen = set()
    for value in queries:
        if not isinstance(value, str):
            raise ValueError("g1d_planner_query_type_invalid")
        query = value.strip()
        if not query or len(query) > 160 or B_ID_ANY_RE.search(query):
            raise ValueError("g1d_planner_query_value_invalid")
        key = query.casefold()
        if key in seen:
            raise ValueError("g1d_planner_query_duplicate")
        seen.add(key)
        out.append(query)
    return {"missing_or_ambiguous_relation": relation.strip(), "queries": out}


def composer_prompt(question: str, context: str) -> str:
    return G1C.composer_prompt(question, context).replace("Axxx", "Bxxx")


def parse_composer(text: str, allowed_ids: set[str]) -> dict[str, Any]:
    row = json.loads(text)
    if not isinstance(row, dict) or set(row) != {"answer", "cited_anchor_ids", "insufficient_authority"}:
        raise ValueError("g1d_composer_shape_invalid")
    if not isinstance(row["answer"], str) or not row["answer"].strip():
        raise ValueError("g1d_composer_answer_invalid")
    citations = row["cited_anchor_ids"]
    if not isinstance(citations, list) or len(citations) != len(set(citations)):
        raise ValueError("g1d_composer_citations_invalid")
    if not all(isinstance(value, str) and B_ID_RE.fullmatch(value) and value in allowed_ids for value in citations):
        raise ValueError("g1d_composer_citation_out_of_context")
    if not isinstance(row["insufficient_authority"], bool):
        raise ValueError("g1d_composer_insufficient_invalid")
    return row


def authority_eval(contract: dict[str, Any], anchor_map: dict[str, dict[str, Any]], question_id: str, selected: list[str]) -> dict[str, Any]:
    return evaluate_context(question_id, selected, contract, anchor_map)


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def selection_metrics(result: dict[str, Any]) -> dict[str, Any]:
    a_by_q = {row["question_id"]: row for row in result["arms"]["A"]}
    d_by_q = {row["question_id"]: row for row in result["arms"]["D"]}
    expected = [f"BQ00{i}" for i in range(1, 9)]
    if sorted(a_by_q) != expected or sorted(d_by_q) != expected:
        return {"complete": False}
    if any("final_authority" not in d_by_q[qid] for qid in expected):
        return {"complete": False}

    improvements = 0
    regressions = 0
    d_clean = 0
    d_insufficient = 0
    rows = {}
    for qid in expected:
        a_status = a_by_q[qid]["authority"]["status"]
        d_status = d_by_q[qid]["final_authority"]["status"]
        if STATUS_ORDER[d_status] > STATUS_ORDER[a_status]:
            improvements += 1
        elif STATUS_ORDER[d_status] < STATUS_ORDER[a_status]:
            regressions += 1
        d_clean += int(d_status == "SUFFICIENT_CLEAN")
        d_insufficient += int(d_status == "INSUFFICIENT_AUTHORITY")
        rows[qid] = {"A": a_status, "D": d_status}
    return {
        "complete": True,
        "authority_statuses": rows,
        "authority_improvements": improvements,
        "authority_regressions": regressions,
        "d_clean": d_clean,
        "d_insufficient": d_insufficient,
    }


def retrieval_selection_verdict(result: dict[str, Any]) -> str:
    metrics = selection_metrics(result)
    if not metrics.get("complete"):
        return "NOT_EXECUTED"
    d_rows = result["arms"]["D"]
    contracts_ok = all(row.get("planner_contract_ok") and row.get("composer_contract_ok") for row in d_rows)
    if (
        contracts_ok
        and metrics["d_insufficient"] == 0
        and metrics["d_clean"] >= 7
        and metrics["authority_improvements"] >= 2
        and metrics["authority_regressions"] == 0
    ):
        return "EARNED_PENDING_SEMANTIC_SAFETY"
    return "NOT_EARNED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()

    request = load_request()
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions_doc = load_json(PKG / "questions.json")
    contract = load_json(PKG / "contract.json")
    anchor_map = {row["anchor_id"]: row for row in anchors}
    question_by_id = {row["question_id"]: row for row in questions_doc["questions"]}

    assert len(anchors) == 23
    assert sorted(question_by_id) == [f"BQ00{i}" for i in range(1, 9)]

    result: dict[str, Any] = {
        "format": "E023-G1d-v0",
        "execute_model": args.execute_model,
        "model": request["model"] if args.execute_model else None,
        "execution_source_sha": os.environ.get("GITHUB_SHA", ""),
        "request": request,
        "model_call_attempts": 0,
        "execution_complete": False,
        "usage": {
            "model_calls": 0,
            "tokens": "unavailable_unless_transport_exposes_machine_readable_usage",
            "ai_credits_or_premium_requests": "unavailable_do_not_infer",
        },
        "arms": {"A": [], "D": []},
        "retrieval_selection_verdict": "NOT_EXECUTED",
        "selection_metrics": {"complete": False},
        "interpretation_boundary": (
            "G1d tests query-time evidence-follow retrieval plus deterministic RRF evidence budgeting on a new prospectively frozen slice. "
            "No result directly authorizes persistence, entity/graph storage, vector defaults, or automatic identity/routing."
        ),
    }
    save_result(result)
    model_runner = G1.ModelRunner(request) if args.execute_model else None

    # Arm A: exact-query BM25 top-5 + composer.
    for question_id in sorted(question_by_id):
        question = question_by_id[question_id]
        ranking = bm25_ranking(anchors, question["question"])
        selected = [anchor_id for anchor_id, _ in ranking[: request["initial_top_k"]]]
        assert selected == EXPECTED_A_TOP5[question_id], (question_id, selected, EXPECTED_A_TOP5[question_id])
        row: dict[str, Any] = {
            "question_id": question_id,
            "question": question["question"],
            "selected_anchor_ids": selected,
            "retrieval_ranking": [
                {"rank": rank, "anchor_id": anchor_id, "score": score}
                for rank, (anchor_id, score) in enumerate(ranking, start=1)
            ],
            "authority": authority_eval(contract, anchor_map, question_id, selected),
        }
        result["arms"]["A"].append(row)
        save_result(result)
        if args.execute_model:
            try:
                receipt = model_runner.call(
                    composer_prompt(question["question"], G1C.evidence_context(anchor_map, selected))
                )
                row["composer_receipt"] = {k: v for k, v in receipt.items() if k != "text"}
                row["composer"] = parse_composer(receipt["text"], set(selected))
                row["composer_contract_ok"] = True
            except Exception as exc:
                row["composer_contract_ok"] = False
                row["error"] = str(exc)
            result["model_call_attempts"] = model_runner.attempts
            result["usage"]["model_calls"] = model_runner.attempts
            save_result(result)

    # Arm D: same initial retrieval -> evidence-aware planner -> deterministic RRF top-4 -> composer.
    for question_id in sorted(question_by_id):
        question = question_by_id[question_id]
        ranking = bm25_ranking(anchors, question["question"])
        initial_ids = [anchor_id for anchor_id, _ in ranking[: request["initial_top_k"]]]
        assert initial_ids == EXPECTED_A_TOP5[question_id]
        row: dict[str, Any] = {
            "question_id": question_id,
            "question": question["question"],
            "initial_anchor_ids": initial_ids,
            "initial_authority": authority_eval(contract, anchor_map, question_id, initial_ids),
            "initial_retrieval_ranking": [
                {"rank": rank, "anchor_id": anchor_id, "score": score}
                for rank, (anchor_id, score) in enumerate(ranking, start=1)
            ],
            "stage": "INITIAL_PERSISTED",
        }
        result["arms"]["D"].append(row)
        save_result(result)

        if not args.execute_model:
            row["not_executed"] = "planner_and_composer_require_model"
            row["stage"] = "ZERO_MODEL_PREFLIGHT_ONLY"
            save_result(result)
            continue

        initial_view = G1C.candidate_view(
            anchor_map,
            initial_ids,
            question=question["question"],
            initial_ids=set(initial_ids),
            snippet_chars=request["planner_snippet_chars"],
        )
        try:
            planner_receipt = model_runner.call(planner_prompt(question["question"], initial_view))
            planner = parse_planner(planner_receipt["text"], max_queries=request["max_followup_queries"])
            row["planner_receipt"] = {k: v for k, v in planner_receipt.items() if k != "text"}
            row["planner"] = planner
            row["planner_contract_ok"] = True
            row["stage"] = "PLANNER_PERSISTED"
        except Exception as exc:
            row["planner_contract_ok"] = False
            row["error"] = str(exc)
            row["stage"] = "PLANNER_FAILED"
            result["model_call_attempts"] = model_runner.attempts
            result["usage"]["model_calls"] = model_runner.attempts
            save_result(result)
            continue
        result["model_call_attempts"] = model_runner.attempts
        result["usage"]["model_calls"] = model_runner.attempts
        save_result(result)

        followup_rankings = [bm25_ranking(anchors, query) for query in planner["queries"]]
        row["followup_retrieval"] = [
            {
                "query": query,
                "ranking": [
                    {"rank": rank, "anchor_id": anchor_id, "score": score}
                    for rank, (anchor_id, score) in enumerate(followup, start=1)
                ],
            }
            for query, followup in zip(planner["queries"], followup_rankings)
        ]
        candidate_ids = G1C.build_candidate_pool(
            initial_ids,
            followup_rankings,
            request["candidate_followup_top_k"],
        )
        row["candidate_anchor_ids"] = candidate_ids
        row["candidate_authority"] = authority_eval(contract, anchor_map, question_id, candidate_ids)
        selected, rrf_trace = rrf_select(
            ranking,
            followup_rankings,
            candidate_ids,
            rrf_k=request["rrf_k"],
            final_top_k=request["final_top_k"],
        )
        row["rrf_trace"] = rrf_trace
        row["selected_anchor_ids"] = selected
        row["final_authority"] = authority_eval(contract, anchor_map, question_id, selected)
        row["deterministic_selector_contract_ok"] = True
        row["stage"] = "SELECTION_PERSISTED"
        save_result(result)

        try:
            composer_receipt = model_runner.call(
                composer_prompt(question["question"], G1C.evidence_context(anchor_map, selected))
            )
            row["composer_receipt"] = {k: v for k, v in composer_receipt.items() if k != "text"}
            row["composer"] = parse_composer(composer_receipt["text"], set(selected))
            row["composer_contract_ok"] = True
            row["stage"] = "COMPOSER_PERSISTED"
        except Exception as exc:
            row["composer_contract_ok"] = False
            row["error"] = str(exc)
            row["stage"] = "COMPOSER_FAILED"
        result["model_call_attempts"] = model_runner.attempts
        result["usage"]["model_calls"] = model_runner.attempts
        result["selection_metrics"] = selection_metrics(result)
        result["retrieval_selection_verdict"] = retrieval_selection_verdict(result)
        save_result(result)

    result["selection_metrics"] = selection_metrics(result)
    result["retrieval_selection_verdict"] = retrieval_selection_verdict(result)
    if model_runner:
        result["model_call_attempts"] = model_runner.attempts
        result["usage"]["model_calls"] = model_runner.attempts
    all_a = all(row.get("composer_contract_ok") for row in result["arms"]["A"]) if args.execute_model else False
    all_d = all(
        row.get("planner_contract_ok")
        and row.get("deterministic_selector_contract_ok")
        and row.get("composer_contract_ok")
        for row in result["arms"]["D"]
    ) if args.execute_model else False
    result["execution_complete"] = bool(
        args.execute_model
        and model_runner is not None
        and model_runner.attempts == request["max_model_call_attempts"]
        and all_a
        and all_d
    )
    save_result(result)

    summary = {
        "format": result["format"],
        "execute_model": args.execute_model,
        "execution_complete": result["execution_complete"],
        "model_call_attempts": result["model_call_attempts"],
        "A_statuses": {row["question_id"]: row["authority"]["status"] for row in result["arms"]["A"]},
        "D_statuses": {row["question_id"]: row.get("final_authority", {}).get("status") for row in result["arms"]["D"]},
        "selection_metrics": result["selection_metrics"],
        "retrieval_selection_verdict": result["retrieval_selection_verdict"],
        "usage": result["usage"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

    if args.execute_model and not result["execution_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
