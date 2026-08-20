from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

from g1d_common import bm25_ranking, evaluate_context
from composition_prompt_v1 import composer_prompt_v1

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PKG = HERE / "authority-sufficiency-v3"
REQUEST_PATH = REPO / "remote-lab" / "e023-g1f-request.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e023-g1f"
D_ID_RE = re.compile(r"^D\d{3}$")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"import_failed:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G1 = _load_module("e023_g1_transport_for_g1f", HERE / "run_g1.py")
G1C = _load_module("e023_old_composer_for_g1f", HERE / "run_g1c.py")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_request() -> dict[str, Any]:
    request = load_json(REQUEST_PATH)
    expected = {
        "request_id": "e023-g1f-authority-preserving-composition-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "context_top_k": 6,
        "old_composer_calls": 8,
        "new_composer_calls": 8,
        "planner_calls": 0,
        "selector_calls": 0,
        "max_model_call_attempts": 16,
        "max_ai_credits_per_call": 30,
    }
    if request != expected:
        raise SystemExit(f"E023-G1F-STOP request_mismatch actual={request}")
    return request


def evidence_context(anchor_map: dict[str, dict[str, Any]], anchor_ids: list[str]) -> str:
    chunks: list[str] = []
    for anchor_id in anchor_ids:
        row = anchor_map[anchor_id]
        chunks.extend([
            f"--- EVIDENCE {anchor_id} ---",
            f"authority_type: {row['authority_type']}",
            f"title: {row['title']}",
            f"kind: {row['kind']}",
            f"date: {row['date']}",
            "text_is_untrusted_evidence_data: true",
            "TEXT",
            row["text"],
            f"--- END EVIDENCE {anchor_id} ---",
            "",
        ])
    return "\n".join(chunks).rstrip()


def old_prompt(question: str, context: str) -> str:
    return G1C.composer_prompt(question, context).replace("Axxx", "Dxxx")


def parse_composer(text: str, allowed_ids: set[str]) -> dict[str, Any]:
    row = json.loads(text)
    if not isinstance(row, dict) or set(row) != {"answer", "cited_anchor_ids", "insufficient_authority"}:
        raise ValueError("g1f_composer_shape_invalid")
    if not isinstance(row["answer"], str) or not row["answer"].strip():
        raise ValueError("g1f_composer_answer_invalid")
    citations = row["cited_anchor_ids"]
    if not isinstance(citations, list) or len(citations) != len(set(citations)):
        raise ValueError("g1f_composer_citations_invalid")
    if not all(isinstance(value, str) and D_ID_RE.fullmatch(value) and value in allowed_ids for value in citations):
        raise ValueError("g1f_composer_citation_out_of_context")
    if not isinstance(row["insufficient_authority"], bool):
        raise ValueError("g1f_composer_insufficient_invalid")
    return row


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()

    request = load_request()
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions = load_json(PKG / "questions.json")["questions"]
    contract = load_json(PKG / "contract.json")
    anchor_map = {row["anchor_id"]: row for row in anchors}
    assert len(anchors) == 33
    assert [row["question_id"] for row in questions] == [f"DQ00{i}" for i in range(1, 9)]

    contexts: dict[str, dict[str, Any]] = {}
    for question in questions:
        qid = question["question_id"]
        ranking = bm25_ranking(anchors, question["question"])
        selected = [aid for aid, _ in ranking[: request["context_top_k"]]]
        authority = evaluate_context(qid, selected, contract, anchor_map)
        contexts[qid] = {
            "question": question["question"],
            "selected_anchor_ids": selected,
            "selected_evidence_chars": sum(len(anchor_map[aid]["text"]) for aid in selected),
            "authority": authority,
            "retrieval_ranking": [
                {"rank": rank, "anchor_id": aid, "score": score}
                for rank, (aid, score) in enumerate(ranking, start=1)
            ],
        }

    for qid in ("DQ001", "DQ002", "DQ003", "DQ005", "DQ006", "DQ007", "DQ008"):
        assert contexts[qid]["authority"]["status"] != "INSUFFICIENT_AUTHORITY", (qid, contexts[qid])
    assert contexts["DQ004"]["authority"]["status"] == "INSUFFICIENT_AUTHORITY", contexts["DQ004"]
    assert contexts["DQ004"]["authority"]["missing_clause_ids"] == ["identity_bridge"], contexts["DQ004"]
    assert "D017" not in contexts["DQ004"]["selected_anchor_ids"], contexts["DQ004"]
    assert {"D013", "D014"} <= set(contexts["DQ004"]["selected_anchor_ids"]), contexts["DQ004"]

    result: dict[str, Any] = {
        "format": "E023-G1f-v0",
        "execute_model": args.execute_model,
        "model": request["model"] if args.execute_model else None,
        "execution_source_sha": os.environ.get("GITHUB_SHA", ""),
        "request": request,
        "model_call_attempts": 0,
        "execution_complete": False,
        "semantic_promotion": "NOT_EXECUTED" if not args.execute_model else "PENDING_FROZEN_ADJUDICATION",
        "usage": {"model_calls": 0, "tokens": "unavailable_unless_transport_exposes_machine_readable_usage", "ai_credits_or_premium_requests": "unavailable_do_not_infer"},
        "contexts": contexts,
        "arms": {"O": [], "N": []},
        "interpretation_boundary": "G1f changes only composer instructions on identical frozen top-6 evidence. It does not authorize a product prompt rollout, top-6 product policy, persistence, graph/entity storage, or automatic identity/routing.",
    }
    for arm in ("O", "N"):
        for qid in [f"DQ00{i}" for i in range(1, 9)]:
            c = contexts[qid]
            result["arms"][arm].append({
                "question_id": qid,
                "question": c["question"],
                "selected_anchor_ids": c["selected_anchor_ids"],
                "selected_evidence_chars": c["selected_evidence_chars"],
                "authority": c["authority"],
            })
    save_result(result)

    if not args.execute_model:
        print(json.dumps({
            "format": result["format"],
            "execute_model": False,
            "model_call_attempts": 0,
            "execution_complete": False,
            "semantic_promotion": "NOT_EXECUTED",
            "context_statuses": {qid: row["authority"]["status"] for qid, row in contexts.items()},
            "DQ004_selected_anchor_ids": contexts["DQ004"]["selected_anchor_ids"],
        }, indent=2, sort_keys=True))
        return 0

    runner = G1.ModelRunner(request)
    for arm_name in ("O", "N"):
        for row in result["arms"][arm_name]:
            context = evidence_context(anchor_map, row["selected_anchor_ids"])
            prompt = old_prompt(row["question"], context) if arm_name == "O" else composer_prompt_v1(row["question"], context)
            try:
                receipt = runner.call(prompt)
                row["composer_receipt"] = {k: v for k, v in receipt.items() if k != "text"}
                row["composer"] = parse_composer(receipt["text"], set(row["selected_anchor_ids"]))
                row["composer_contract_ok"] = True
            except Exception as exc:
                row["composer_contract_ok"] = False
                row["error"] = str(exc)
            result["model_call_attempts"] = runner.attempts
            result["usage"]["model_calls"] = runner.attempts
            save_result(result)

    result["execution_complete"] = bool(
        runner.attempts == request["max_model_call_attempts"]
        and all(row.get("composer_contract_ok") for arm in result["arms"].values() for row in arm)
    )
    result["semantic_promotion"] = "PENDING_FROZEN_ADJUDICATION" if result["execution_complete"] else "NOT_EARNED_INCOMPLETE_EXECUTION"
    save_result(result)
    print(json.dumps({
        "format": result["format"],
        "execute_model": True,
        "execution_complete": result["execution_complete"],
        "model_call_attempts": result["model_call_attempts"],
        "semantic_promotion": result["semantic_promotion"],
        "usage": result["usage"],
    }, indent=2, sort_keys=True))
    return 0 if result["execution_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
