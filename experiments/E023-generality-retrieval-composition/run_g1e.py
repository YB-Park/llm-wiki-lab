from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

from g1d_common import bm25_ranking, evaluate_context

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PKG = HERE / "authority-sufficiency-v2"
REQUEST_PATH = REPO / "remote-lab" / "e023-g1e-request.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e023-g1e"
C_ID_RE = re.compile(r"^C\d{3}$")

EXPECTED_PREFIXES = {
    "CQ001": ["C001", "C005", "C002", "C006", "C004", "C003"],
    "CQ002": ["C007", "C008", "C009", "C011", "C010", "C013"],
    "CQ003": ["C014", "C013", "C021", "C030", "C034", "C027"],
    "CQ004": ["C015", "C017", "C016", "C014", "C018", "C034"],
    "CQ005": ["C019", "C020", "C021", "C022", "C013", "C030"],
    "CQ006": ["C024", "C025", "C023", "C026", "C006", "C004"],
    "CQ007": ["C027", "C030", "C028", "C031", "C029", "C001"],
    "CQ008": ["C034", "C021", "C014", "C001", "C032", "C033"],
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"import_failed:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G1 = _load_module("e023_g1_transport_for_g1e", HERE / "run_g1.py")
G1C = _load_module("e023_g1c_composer_for_g1e", HERE / "run_g1c.py")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_request() -> dict[str, Any]:
    request = load_json(REQUEST_PATH)
    expected = {
        "request_id": "e023-g1e-exact-bm25-budget-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "a5_top_k": 5,
        "b6_top_k": 6,
        "a5_composer_calls": 8,
        "b6_composer_calls": 8,
        "planner_calls": 0,
        "selector_calls": 0,
        "max_model_call_attempts": 16,
        "max_ai_credits_per_call": 30,
    }
    if request != expected:
        raise SystemExit(f"E023-G1E-STOP request_mismatch actual={request}")
    return request


def composer_prompt(question: str, context: str) -> str:
    return G1C.composer_prompt(question, context).replace("Axxx", "Cxxx")


def parse_composer(text: str, allowed_ids: set[str]) -> dict[str, Any]:
    row = json.loads(text)
    if not isinstance(row, dict) or set(row) != {"answer", "cited_anchor_ids", "insufficient_authority"}:
        raise ValueError("g1e_composer_shape_invalid")
    if not isinstance(row["answer"], str) or not row["answer"].strip():
        raise ValueError("g1e_composer_answer_invalid")
    citations = row["cited_anchor_ids"]
    if not isinstance(citations, list) or len(citations) != len(set(citations)):
        raise ValueError("g1e_composer_citations_invalid")
    if not all(isinstance(value, str) and C_ID_RE.fullmatch(value) and value in allowed_ids for value in citations):
        raise ValueError("g1e_composer_citation_out_of_context")
    if not isinstance(row["insufficient_authority"], bool):
        raise ValueError("g1e_composer_insufficient_invalid")
    return row


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def make_row(question: dict[str, Any], ranking: list[tuple[str, float]], k: int, contract, anchor_map) -> dict[str, Any]:
    selected = [anchor_id for anchor_id, _ in ranking[:k]]
    expected = EXPECTED_PREFIXES[question["question_id"]][:k]
    assert selected == expected, (question["question_id"], k, selected, expected)
    return {
        "question_id": question["question_id"],
        "question": question["question"],
        "top_k": k,
        "selected_anchor_ids": selected,
        "selected_evidence_chars": sum(len(anchor_map[anchor_id]["text"]) for anchor_id in selected),
        "authority": evaluate_context(question["question_id"], selected, contract, anchor_map),
        "retrieval_ranking": [
            {"rank": rank, "anchor_id": anchor_id, "score": score}
            for rank, (anchor_id, score) in enumerate(ranking, start=1)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()

    request = load_request()
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions = load_json(PKG / "questions.json")["questions"]
    contract = load_json(PKG / "contract.json")
    anchor_map = {row["anchor_id"]: row for row in anchors}
    assert len(anchors) == 35
    assert [row["question_id"] for row in questions] == [f"CQ00{i}" for i in range(1, 9)]

    result: dict[str, Any] = {
        "format": "E023-G1e-v0",
        "execute_model": args.execute_model,
        "model": request["model"] if args.execute_model else None,
        "execution_source_sha": os.environ.get("GITHUB_SHA", ""),
        "request": request,
        "phase0_authority_gate": "PASS_FROZEN_PR187",
        "model_call_attempts": 0,
        "execution_complete": False,
        "semantic_promotion": "NOT_EXECUTED" if not args.execute_model else "PENDING_FROZEN_ADJUDICATION",
        "usage": {
            "model_calls": 0,
            "tokens": "unavailable_unless_transport_exposes_machine_readable_usage",
            "ai_credits_or_premium_requests": "unavailable_do_not_infer",
        },
        "arms": {"A5": [], "B6": []},
        "interpretation_boundary": (
            "G1e compares one exact-BM25 evidence-prefix increment on prospectively frozen material. "
            "No result makes top-6 a product policy or authorizes persistence, entity/graph storage, vector defaults, or automatic identity/routing."
        ),
    }

    for question in questions:
        ranking = bm25_ranking(anchors, question["question"])
        result["arms"]["A5"].append(make_row(question, ranking, request["a5_top_k"], contract, anchor_map))
        result["arms"]["B6"].append(make_row(question, ranking, request["b6_top_k"], contract, anchor_map))
    save_result(result)

    if not args.execute_model:
        summary = {
            "format": result["format"],
            "execute_model": False,
            "model_call_attempts": 0,
            "execution_complete": False,
            "semantic_promotion": "NOT_EXECUTED",
            "A5_statuses": {row["question_id"]: row["authority"]["status"] for row in result["arms"]["A5"]},
            "B6_statuses": {row["question_id"]: row["authority"]["status"] for row in result["arms"]["B6"]},
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    runner = G1.ModelRunner(request)
    for arm_name in ("A5", "B6"):
        for row in result["arms"][arm_name]:
            selected = row["selected_anchor_ids"]
            try:
                receipt = runner.call(
                    composer_prompt(row["question"], G1C.evidence_context(anchor_map, selected))
                )
                row["composer_receipt"] = {k: v for k, v in receipt.items() if k != "text"}
                row["composer"] = parse_composer(receipt["text"], set(selected))
                row["composer_contract_ok"] = True
            except Exception as exc:
                row["composer_contract_ok"] = False
                row["error"] = str(exc)
            result["model_call_attempts"] = runner.attempts
            result["usage"]["model_calls"] = runner.attempts
            save_result(result)

    result["execution_complete"] = bool(
        runner.attempts == request["max_model_call_attempts"]
        and all(row.get("composer_contract_ok") for row in result["arms"]["A5"])
        and all(row.get("composer_contract_ok") for row in result["arms"]["B6"])
    )
    result["semantic_promotion"] = "PENDING_FROZEN_ADJUDICATION" if result["execution_complete"] else "NOT_EARNED_INCOMPLETE_EXECUTION"
    save_result(result)

    summary = {
        "format": result["format"],
        "execute_model": True,
        "execution_complete": result["execution_complete"],
        "model_call_attempts": result["model_call_attempts"],
        "semantic_promotion": result["semantic_promotion"],
        "A5_statuses": {row["question_id"]: row["authority"]["status"] for row in result["arms"]["A5"]},
        "B6_statuses": {row["question_id"]: row["authority"]["status"] for row in result["arms"]["B6"]},
        "usage": result["usage"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if result["execution_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
