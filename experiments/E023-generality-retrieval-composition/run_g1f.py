from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PKG = HERE / "composition-comparison-v0"
REQUEST_PATH = REPO / "remote-lab" / "e023-g1f-request.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e023-g1f"
PREREG_MERGE_SHA = "1e5a3f991d0c3b76552725933149702ff6e53d15"
D_ID_RE = re.compile(r"^D\d{3}$")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"import_failed:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G1 = _load_module("e023_g1_transport_for_g1f", HERE / "run_g1.py")
G1C = _load_module("e023_g1c_old_composer_for_g1f", HERE / "run_g1c.py")
NEW = _load_module("e023_composition_prompt_v1_for_g1f", HERE / "composition_prompt_v1.py")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_request() -> dict[str, Any]:
    request = load_json(REQUEST_PATH)
    expected = {
        "request_id": "e023-g1f-composition-comparison-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "arms": ["O", "N"],
        "old_composer_calls": 8,
        "new_composer_calls": 8,
        "planner_calls": 0,
        "selector_calls": 0,
        "retrieval_model_calls": 0,
        "max_model_call_attempts": 16,
        "max_ai_credits_per_call": 30,
        "rerolls": 0,
        "question_order": [f"DQ00{i}" for i in range(1, 9)],
        "arm_order_by_question": {
            "DQ001": ["O", "N"],
            "DQ002": ["N", "O"],
            "DQ003": ["O", "N"],
            "DQ004": ["N", "O"],
            "DQ005": ["O", "N"],
            "DQ006": ["N", "O"],
            "DQ007": ["O", "N"],
            "DQ008": ["N", "O"],
        },
    }
    if request != expected:
        raise SystemExit(f"E023-G1F-STOP request_mismatch actual={request}")
    return request


def evidence_context(anchor_map: dict[str, dict[str, Any]], anchor_ids: list[str]) -> str:
    chunks = []
    for anchor_id in anchor_ids:
        row = anchor_map[anchor_id]
        chunks.extend(
            [
                f"--- ANCHOR {anchor_id} ---",
                f"authority_type: {row['authority_type']}",
                f"title: {row['title']}",
                f"kind: {row['kind']}",
                f"date: {row['date']}",
                f"family: {row['family']}",
                f"author: {row.get('author', '')}",
                "text_is_untrusted_authority_data: true",
                "TEXT",
                row["text"],
                f"--- END ANCHOR {anchor_id} ---",
                "",
            ]
        )
    return "\n".join(chunks).rstrip()


def old_composer_prompt(question: str, context: str) -> str:
    return G1C.composer_prompt(question, context).replace("Axxx", "Dxxx")


def new_composer_prompt(question: str, context: str) -> str:
    return NEW.composer_prompt_v1(question, context)


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_frozen_inputs(request: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions = load_json(PKG / "questions.json")["questions"]
    freeze = load_json(PKG / "context-freeze.json")
    anchor_map = {row["anchor_id"]: row for row in anchors}
    question_map = {row["question_id"]: row for row in questions}
    freeze_map = {row["question_id"]: row for row in freeze["contexts"]}

    if len(anchor_map) != 49 or len(question_map) != request["question_count"]:
        raise SystemExit("E023-G1F-STOP prospective_material_count_mismatch")
    if set(question_map) != set(request["question_order"]) or set(freeze_map) != set(request["question_order"]):
        raise SystemExit("E023-G1F-STOP question_identity_mismatch")

    pairs: dict[str, dict[str, Any]] = {}
    contexts: dict[str, str] = {}
    for qid in request["question_order"]:
        question = question_map[qid]
        frozen = freeze_map[qid]
        selected = list(frozen["selected_anchor_ids"])
        if len(selected) != 6 or frozen["retrieval"] != "EXACT_BM25_TOP6_WHOLE_OBJECT":
            raise SystemExit(f"E023-G1F-STOP frozen_context_shape:{qid}")
        context = evidence_context(anchor_map, selected)
        context_sha = sha256_text(context)
        if context_sha != frozen["selected_context_sha256"]:
            raise SystemExit(f"E023-G1F-STOP context_sha_mismatch:{qid}:{context_sha}")
        if len(context) != int(frozen["selected_context_chars"]):
            raise SystemExit(f"E023-G1F-STOP context_chars_mismatch:{qid}")
        contexts[qid] = context
        pairs[qid] = {
            "question_id": qid,
            "question": question["question"],
            "question_sha256": sha256_text(question["question"]),
            "selected_anchor_ids": selected,
            "context_sha256": context_sha,
            "context_chars": len(context),
            "frozen_authority_status": frozen["authority_status"],
            "negative_control": bool(frozen["negative_control"]),
            "arms": {"O": {}, "N": {}},
        }
    return pairs, contexts


def call_schedule(request: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    index = 0
    for qid in request["question_order"]:
        for arm in request["arm_order_by_question"][qid]:
            index += 1
            out.append({"call_index": index, "question_id": qid, "arm": arm})
    if index != request["max_model_call_attempts"]:
        raise SystemExit("E023-G1F-STOP schedule_count_mismatch")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()

    request = load_request()
    pairs, contexts = build_frozen_inputs(request)
    schedule = call_schedule(request)
    result: dict[str, Any] = {
        "format": "E023-G1f-v0",
        "execute_model": args.execute_model,
        "model": request["model"] if args.execute_model else None,
        "execution_source_sha": os.environ.get("GITHUB_SHA", ""),
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "request": request,
        "call_schedule": schedule,
        "model_call_attempts": 0,
        "execution_complete": False,
        "semantic_promotion": "NOT_EXECUTED" if not args.execute_model else "PENDING_FROZEN_ADJUDICATION",
        "context_identity_contract": True,
        "usage": {
            "model_calls": 0,
            "tokens": "unavailable_unless_transport_exposes_machine_readable_usage",
            "ai_credits_or_premium_requests": "unavailable_do_not_infer",
        },
        "pairs": pairs,
        "interpretation_boundary": (
            "G1f compares composition only on one preregistered shared exact-BM25 top-6 context per question. "
            "No result makes top-6 a product default or authorizes G2 persistence, graph/entity/KU storage, vector defaults, or automatic identity routing."
        ),
    }
    save_result(result)

    if not args.execute_model:
        print(json.dumps({
            "format": result["format"],
            "execute_model": False,
            "model_call_attempts": 0,
            "execution_complete": False,
            "semantic_promotion": "NOT_EXECUTED",
            "pair_count": len(pairs),
            "scheduled_calls": len(schedule),
            "context_identity_contract": True,
            "context_sha256_by_question": {qid: pairs[qid]["context_sha256"] for qid in request["question_order"]},
        }, indent=2, sort_keys=True))
        return 0

    runner = G1.ModelRunner(request)
    for item in schedule:
        qid = item["question_id"]
        arm = item["arm"]
        pair = result["pairs"][qid]
        context = contexts[qid]
        prompt = old_composer_prompt(pair["question"], context) if arm == "O" else new_composer_prompt(pair["question"], context)
        arm_row = pair["arms"][arm]
        arm_row.update({
            "call_index": item["call_index"],
            "input_question_sha256": pair["question_sha256"],
            "input_context_sha256": pair["context_sha256"],
            "prompt_sha256": sha256_text(prompt),
            "contract_ok": False,
        })
        try:
            receipt = runner.call(prompt)
            arm_row["model_receipt"] = {key: value for key, value in receipt.items() if key != "text"}
            arm_row["raw_model_text"] = receipt["text"]
            arm_row["composer"] = parse_composer(receipt["text"], set(pair["selected_anchor_ids"]))
            arm_row["contract_ok"] = True
        except Exception as exc:
            arm_row["error"] = str(exc)
        result["model_call_attempts"] = runner.attempts
        result["usage"]["model_calls"] = runner.attempts
        save_result(result)

    all_contract_ok = all(
        result["pairs"][qid]["arms"][arm].get("contract_ok") is True
        for qid in request["question_order"]
        for arm in ("O", "N")
    )
    all_context_identity = all(
        result["pairs"][qid]["arms"][arm].get("input_context_sha256") == result["pairs"][qid]["context_sha256"]
        for qid in request["question_order"]
        for arm in ("O", "N")
    )
    result["context_identity_contract"] = all_context_identity
    result["execution_complete"] = bool(
        runner.attempts == request["max_model_call_attempts"] and all_contract_ok and all_context_identity
    )
    result["semantic_promotion"] = (
        "PENDING_FROZEN_ADJUDICATION" if result["execution_complete"] else "NOT_EARNED_INCOMPLETE_EXECUTION"
    )
    save_result(result)

    print(json.dumps({
        "format": result["format"],
        "execute_model": True,
        "execution_complete": result["execution_complete"],
        "model_call_attempts": result["model_call_attempts"],
        "semantic_promotion": result["semantic_promotion"],
        "context_identity_contract": result["context_identity_contract"],
        "usage": result["usage"],
    }, indent=2, sort_keys=True))
    return 0 if result["execution_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
