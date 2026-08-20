from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

from g1d_common import bm25_ranking, evaluate_context

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PKG = HERE / "persistence-comparison-v0"
REQUEST_PATH = REPO / "remote-lab" / "e023-g2-request.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e023-g2"
PREREG_MERGE_SHA = "080ac3d91d011be3ec16111bdc24eda9905f3d9c"
P_ID_RE = re.compile(r"^P\d{3}$")
ENTRY_ID_RE = re.compile(r"^E\d{2}$")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"import_failed:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G1 = _load_module("e023_g1_transport_for_g2", HERE / "run_g1.py")
G1C = _load_module("e023_g1c_composer_for_g2", HERE / "run_g1c.py")
PROJECTION = _load_module("e023_projection_prompt_for_g2", HERE / "projection_prompt_v0.py")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_request() -> dict[str, Any]:
    request = load_json(REQUEST_PATH)
    expected = {
        "request_id": "e023-g2-fixed-identity-persistence-v0",
        "model": "gpt-5.6-luna",
        "question_count": 12,
        "Q_composer_calls": 12,
        "P_composer_calls": 12,
        "projection_build_rebuild_calls": 5,
        "planner_calls": 0,
        "selector_calls": 0,
        "vector_calls": 0,
        "max_model_call_attempts": 29,
        "max_ai_credits_per_call": 30,
        "rerolls": 0,
        "question_order": [f"PQ{i:03d}" for i in range(1, 13)],
        "arm_order_by_question": {
            "PQ001": ["Q", "P"],
            "PQ002": ["P", "Q"],
            "PQ003": ["Q", "P"],
            "PQ004": ["P", "Q"],
            "PQ005": ["Q", "P"],
            "PQ006": ["P", "Q"],
            "PQ007": ["Q", "P"],
            "PQ008": ["P", "Q"],
            "PQ009": ["Q", "P"],
            "PQ010": ["P", "Q"],
            "PQ011": ["Q", "P"],
            "PQ012": ["P", "Q"],
        },
    }
    if request != expected:
        raise SystemExit(f"E023-G2-STOP request_mismatch actual={request}")
    return request


def canonical_json_sha(rows: list[dict[str, Any]]) -> str:
    text = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def active_anchors(all_anchors: list[dict[str, Any]], subject_id: str, state: str) -> list[dict[str, Any]]:
    if state not in {"S0", "S1"}:
        raise ValueError(f"unknown_state:{state}")
    return sorted(
        [
            row
            for row in all_anchors
            if row["subject_id"] == subject_id
            and (row["active_from_state"] == "S0" or state == "S1")
        ],
        key=lambda row: row["anchor_id"],
    )


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
    return G1C.composer_prompt(question, context).replace("Axxx", "Pxxx")


def parse_composer(text: str, allowed_ids: set[str]) -> dict[str, Any]:
    row = json.loads(text)
    if not isinstance(row, dict) or set(row) != {"answer", "cited_anchor_ids", "insufficient_authority"}:
        raise ValueError("g2_composer_shape_invalid")
    if not isinstance(row["answer"], str) or not row["answer"].strip():
        raise ValueError("g2_composer_answer_invalid")
    citations = row["cited_anchor_ids"]
    if not isinstance(citations, list) or len(citations) != len(set(citations)):
        raise ValueError("g2_composer_citations_invalid")
    if not all(isinstance(value, str) and P_ID_RE.fullmatch(value) and value in allowed_ids for value in citations):
        raise ValueError("g2_composer_citation_out_of_context")
    if not isinstance(row["insufficient_authority"], bool):
        raise ValueError("g2_composer_insufficient_invalid")
    return row


def parse_projection(text: str, allowed_ids: set[str]) -> dict[str, Any]:
    row = json.loads(text)
    if not isinstance(row, dict) or set(row) != {"entries"}:
        raise ValueError("g2_projection_shape_invalid")
    entries = row["entries"]
    if not isinstance(entries, list) or not 4 <= len(entries) <= 12:
        raise ValueError("g2_projection_entry_count_invalid")
    referenced: set[str] = set()
    out = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict) or set(entry) != {"entry_id", "statement", "anchor_ids"}:
            raise ValueError("g2_projection_entry_shape_invalid")
        expected_id = f"E{index:02d}"
        if entry["entry_id"] != expected_id or not ENTRY_ID_RE.fullmatch(entry["entry_id"]):
            raise ValueError("g2_projection_entry_id_invalid")
        statement = entry["statement"]
        if not isinstance(statement, str) or not statement.strip() or len(statement.strip()) > 320:
            raise ValueError("g2_projection_statement_invalid")
        anchor_ids = entry["anchor_ids"]
        if not isinstance(anchor_ids, list) or not 1 <= len(anchor_ids) <= 4 or len(anchor_ids) != len(set(anchor_ids)):
            raise ValueError("g2_projection_anchor_count_invalid")
        if not all(isinstance(value, str) and P_ID_RE.fullmatch(value) and value in allowed_ids for value in anchor_ids):
            raise ValueError("g2_projection_anchor_out_of_scope")
        referenced.update(anchor_ids)
        out.append({"entry_id": expected_id, "statement": statement.strip(), "anchor_ids": list(anchor_ids)})
    if referenced != allowed_ids:
        raise ValueError(f"g2_projection_not_broad_subject_view missing={sorted(allowed_ids - referenced)}")
    return {"entries": out}


def projection_ranking(entries: list[dict[str, Any]], question: str) -> list[tuple[str, float]]:
    docs = [{"anchor_id": row["entry_id"], "text": row["statement"]} for row in entries]
    return bm25_ranking(docs, question)


def select_persistent(
    *,
    question: str,
    active: list[dict[str, Any]],
    current_snapshot_sha: str,
    projection_state: dict[str, Any] | None,
    q_selected: list[str],
) -> dict[str, Any]:
    if not projection_state or not projection_state.get("contract_ok"):
        return {
            "selection_mode": "PROJECTION_UNAVAILABLE_FALLBACK_Q",
            "selected_anchor_ids": list(q_selected),
            "projection_used": False,
            "stored_snapshot_sha256": projection_state.get("source_snapshot_sha256") if projection_state else None,
            "current_snapshot_sha256": current_snapshot_sha,
            "projection_entry_ranking": [],
            "selected_projection_entry_ids": [],
        }
    stored_sha = projection_state["source_snapshot_sha256"]
    if stored_sha != current_snapshot_sha:
        return {
            "selection_mode": "STALE_PROJECTION_BYPASS",
            "selected_anchor_ids": list(q_selected),
            "projection_used": False,
            "stored_snapshot_sha256": stored_sha,
            "current_snapshot_sha256": current_snapshot_sha,
            "projection_entry_ranking": [],
            "selected_projection_entry_ids": [],
        }

    entries = projection_state["projection"]["entries"]
    entry_map = {row["entry_id"]: row for row in entries}
    ranked_entries = projection_ranking(entries, question)
    if not ranked_entries:
        return {
            "selection_mode": "FRESH_PROJECTION_ZERO_SCORE_FALLBACK_Q",
            "selected_anchor_ids": list(q_selected),
            "projection_used": False,
            "stored_snapshot_sha256": stored_sha,
            "current_snapshot_sha256": current_snapshot_sha,
            "projection_entry_ranking": [],
            "selected_projection_entry_ids": [],
        }

    selected_entry_ids = [entry_id for entry_id, _ in ranked_entries[:2]]
    selected: list[str] = []
    seen: set[str] = set()
    for entry_id in selected_entry_ids:
        for anchor_id in entry_map[entry_id]["anchor_ids"]:
            if anchor_id not in seen:
                seen.add(anchor_id)
                selected.append(anchor_id)
            if len(selected) >= 6:
                break
        if len(selected) >= 6:
            break

    raw_ranking = bm25_ranking(active, question)
    for anchor_id, _ in raw_ranking:
        if len(selected) >= 4:
            break
        if anchor_id not in seen:
            seen.add(anchor_id)
            selected.append(anchor_id)
    if len(selected) < 4:
        raise ValueError("g2_persistent_minimum_terminal_anchors_unmet")
    selected = selected[:6]
    return {
        "selection_mode": "FRESH_PROJECTION_RETRIEVAL",
        "selected_anchor_ids": selected,
        "projection_used": True,
        "stored_snapshot_sha256": stored_sha,
        "current_snapshot_sha256": current_snapshot_sha,
        "projection_entry_ranking": [
            {"rank": rank, "entry_id": entry_id, "score": score}
            for rank, (entry_id, score) in enumerate(ranked_entries, start=1)
        ],
        "selected_projection_entry_ids": selected_entry_ids,
    }


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_material(request: dict[str, Any]) -> dict[str, Any]:
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions = load_json(PKG / "questions.json")["questions"]
    contract = load_json(PKG / "authority-contract.json")
    lifecycle = load_json(PKG / "lifecycle.json")
    frozen_rows = load_json(PKG / "control-contexts.json")["contexts"]
    if len(anchors) != 36 or len(questions) != request["question_count"]:
        raise SystemExit("E023-G2-STOP material_count_mismatch")
    anchor_map = {row["anchor_id"]: row for row in anchors}
    question_map = {row["question_id"]: row for row in questions}
    frozen_map = {row["question_id"]: row for row in frozen_rows}
    if set(question_map) != set(request["question_order"]) or set(frozen_map) != set(request["question_order"]):
        raise SystemExit("E023-G2-STOP question_identity_mismatch")
    return {
        "anchors": anchors,
        "anchor_map": anchor_map,
        "questions": questions,
        "question_map": question_map,
        "contract": contract,
        "lifecycle": lifecycle,
        "frozen_map": frozen_map,
    }


def verified_q_context(material: dict[str, Any], question: dict[str, Any]) -> dict[str, Any]:
    anchors = material["anchors"]
    anchor_map = material["anchor_map"]
    contract = material["contract"]
    frozen = material["frozen_map"][question["question_id"]]
    active = active_anchors(anchors, question["subject_id"], question["state"])
    current_sha = canonical_json_sha(active)
    expected_state = material["lifecycle"]["subjects"][question["subject_id"]]["states"][question["state"]]
    if current_sha != expected_state["snapshot_sha256"]:
        raise SystemExit(f"E023-G2-STOP snapshot_sha_mismatch:{question['question_id']}")
    ranking = bm25_ranking(active, question["question"])
    selected = [anchor_id for anchor_id, _ in ranking[:6]]
    if selected != frozen["selected_anchor_ids"]:
        raise SystemExit(f"E023-G2-STOP q_selected_mismatch:{question['question_id']}")
    context = evidence_context(anchor_map, selected)
    if sha256_text(context) != frozen["selected_context_sha256"] or len(context) != frozen["selected_context_chars"]:
        raise SystemExit(f"E023-G2-STOP q_context_mismatch:{question['question_id']}")
    authority = evaluate_context(question["question_id"], selected, contract, anchor_map)
    if authority["status"] != frozen["authority_status"]:
        raise SystemExit(f"E023-G2-STOP q_authority_mismatch:{question['question_id']}")
    return {
        "active": active,
        "snapshot_sha256": current_sha,
        "ranking": ranking,
        "selected_anchor_ids": selected,
        "context": context,
        "authority": authority,
        "raw_evidence_chars": sum(len(anchor_map[anchor_id]["text"]) for anchor_id in selected),
    }


def zero_model_preflight(request: dict[str, Any], material: dict[str, Any]) -> dict[str, Any]:
    q_rows = {}
    for qid in request["question_order"]:
        question = material["question_map"][qid]
        q = verified_q_context(material, question)
        q_rows[qid] = {
            "subject_id": question["subject_id"],
            "state": question["state"],
            "phase": question["phase"],
            "selected_anchor_ids": q["selected_anchor_ids"],
            "context_sha256": sha256_text(q["context"]),
            "authority_status": q["authority"]["status"],
        }
    return {
        "format": "E023-G2-v0",
        "execute_model": False,
        "model_call_attempts": 0,
        "execution_complete": False,
        "semantic_promotion": "NOT_EXECUTED",
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "question_count": len(q_rows),
        "lifecycle_event_count": len(material["lifecycle"]["events"]),
        "planned_projection_build_rebuild_calls": request["projection_build_rebuild_calls"],
        "planned_semantic_attempts": request["max_model_call_attempts"],
        "Q": q_rows,
    }


def build_projection_slot(
    *,
    runner,
    result: dict[str, Any],
    material: dict[str, Any],
    subject_id: str,
    state: str,
    event_index: int,
    event_kind: str,
) -> dict[str, Any]:
    active = active_anchors(material["anchors"], subject_id, state)
    current_sha = canonical_json_sha(active)
    expected_sha = material["lifecycle"]["subjects"][subject_id]["states"][state]["snapshot_sha256"]
    if current_sha != expected_sha:
        raise SystemExit(f"E023-G2-STOP build_snapshot_mismatch:{subject_id}:{state}")
    active_ids = [row["anchor_id"] for row in active]
    context = evidence_context(material["anchor_map"], active_ids)
    slot: dict[str, Any] = {
        "event_index": event_index,
        "event": event_kind,
        "subject_id": subject_id,
        "state": state,
        "source_snapshot_sha256": current_sha,
        "terminal_anchor_ids": active_ids,
        "terminal_context_sha256": sha256_text(context),
        "contract_ok": False,
        "call_index": runner.attempts + 1,
    }
    try:
        receipt = runner.call(PROJECTION.projection_prompt_v0(subject_id, context))
        slot["model_receipt"] = {key: value for key, value in receipt.items() if key != "text"}
        slot["raw_model_text"] = receipt["text"]
        slot["projection"] = parse_projection(receipt["text"], set(active_ids))
        slot["contract_ok"] = True
    except Exception as exc:
        slot["error"] = str(exc)
    result["model_call_attempts"] = runner.attempts
    result["usage"]["model_calls"] = runner.attempts
    result["projection_builds"].append(slot)
    save_result(result)
    return slot


def execute_query_pair(
    *,
    runner,
    result: dict[str, Any],
    material: dict[str, Any],
    projection_states: dict[str, dict[str, Any]],
    question_id: str,
) -> None:
    question = material["question_map"][question_id]
    anchor_map = material["anchor_map"]
    q = verified_q_context(material, question)
    p_selection = select_persistent(
        question=question["question"],
        active=q["active"],
        current_snapshot_sha=q["snapshot_sha256"],
        projection_state=projection_states.get(question["subject_id"]),
        q_selected=q["selected_anchor_ids"],
    )
    p_selected = p_selection["selected_anchor_ids"]
    p_context = evidence_context(anchor_map, p_selected)
    p_authority = evaluate_context(question_id, p_selected, material["contract"], anchor_map)
    pair: dict[str, Any] = {
        "question_id": question_id,
        "question": question["question"],
        "question_sha256": sha256_text(question["question"]),
        "subject_id": question["subject_id"],
        "state": question["state"],
        "phase": question["phase"],
        "snapshot_sha256": q["snapshot_sha256"],
        "Q": {
            "selected_anchor_ids": q["selected_anchor_ids"],
            "context_sha256": sha256_text(q["context"]),
            "context_chars": len(q["context"]),
            "raw_evidence_chars": q["raw_evidence_chars"],
            "authority": q["authority"],
            "composer_contract_ok": False,
        },
        "P": {
            **p_selection,
            "context_sha256": sha256_text(p_context),
            "context_chars": len(p_context),
            "raw_evidence_chars": sum(len(anchor_map[anchor_id]["text"]) for anchor_id in p_selected),
            "authority": p_authority,
            "composer_contract_ok": False,
        },
    }
    result["pairs"][question_id] = pair
    save_result(result)

    contexts = {"Q": q["context"], "P": p_context}
    for arm in result["request"]["arm_order_by_question"][question_id]:
        arm_row = pair[arm]
        arm_row["call_index"] = runner.attempts + 1
        arm_row["input_question_sha256"] = pair["question_sha256"]
        arm_row["input_context_sha256"] = arm_row["context_sha256"]
        prompt = old_composer_prompt(question["question"], contexts[arm])
        arm_row["prompt_sha256"] = sha256_text(prompt)
        try:
            receipt = runner.call(prompt)
            arm_row["model_receipt"] = {key: value for key, value in receipt.items() if key != "text"}
            arm_row["raw_model_text"] = receipt["text"]
            arm_row["composer"] = parse_composer(receipt["text"], set(arm_row["selected_anchor_ids"]))
            arm_row["composer_contract_ok"] = True
        except Exception as exc:
            arm_row["error"] = str(exc)
        result["model_call_attempts"] = runner.attempts
        result["usage"]["model_calls"] = runner.attempts
        save_result(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()

    request = load_request()
    material = load_material(request)
    if not args.execute_model:
        preflight = zero_model_preflight(request, material)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "result.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(preflight, indent=2, sort_keys=True))
        return 0

    result: dict[str, Any] = {
        "format": "E023-G2-v0",
        "execute_model": True,
        "model": request["model"],
        "execution_source_sha": os.environ.get("GITHUB_SHA", ""),
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "request": request,
        "model_call_attempts": 0,
        "execution_complete": False,
        "semantic_promotion": "PENDING_EXECUTION",
        "usage": {
            "model_calls": 0,
            "tokens": "unavailable_unless_transport_exposes_machine_readable_usage",
            "ai_credits_or_premium_requests": "unavailable_do_not_infer",
        },
        "projection_builds": [],
        "pairs": {},
        "lifecycle_trace": [],
        "interpretation_boundary": (
            "G2 tests fixed-identity rebuildable DERIVED retrieval persistence against the frozen G1 query-time control. "
            "Projection text is never terminal authority or composer context. No result directly authorizes product persistence or G3 identity/routing."
        ),
    }
    save_result(result)

    runner = G1.ModelRunner(request)
    projection_states: dict[str, dict[str, Any]] = {}
    current_states = {"iris": "S0", "juniper": "S0", "keystone": "S0"}

    for event in material["lifecycle"]["events"]:
        trace = dict(event)
        if event["event"] in {"BUILD_PROJECTION", "REBUILD_PROJECTION"}:
            slot = build_projection_slot(
                runner=runner,
                result=result,
                material=material,
                subject_id=event["subject_id"],
                state=event["state"],
                event_index=event["event_index"],
                event_kind=event["event"],
            )
            projection_states[event["subject_id"]] = slot
            trace["projection_contract_ok"] = slot["contract_ok"]
            trace["projection_call_index"] = slot["call_index"]
        elif event["event"] == "MUTATE_AUTHORITY":
            if current_states[event["subject_id"]] != event["from_state"]:
                raise SystemExit(f"E023-G2-STOP lifecycle_state_mismatch:{event['subject_id']}")
            current_states[event["subject_id"]] = event["to_state"]
            trace["model_calls"] = 0
        elif event["event"] == "QUERY_PAIR":
            question = material["question_map"][event["question_id"]]
            if current_states[question["subject_id"]] != question["state"]:
                raise SystemExit(f"E023-G2-STOP query_state_mismatch:{event['question_id']}")
            execute_query_pair(
                runner=runner,
                result=result,
                material=material,
                projection_states=projection_states,
                question_id=event["question_id"],
            )
            trace["Q_call_index"] = result["pairs"][event["question_id"]]["Q"].get("call_index")
            trace["P_call_index"] = result["pairs"][event["question_id"]]["P"].get("call_index")
            trace["P_selection_mode"] = result["pairs"][event["question_id"]]["P"]["selection_mode"]
        else:
            raise SystemExit(f"E023-G2-STOP unknown_lifecycle_event:{event['event']}")
        result["lifecycle_trace"].append(trace)
        save_result(result)

    projection_ok = len(result["projection_builds"]) == 5 and all(row.get("contract_ok") for row in result["projection_builds"])
    pair_ok = len(result["pairs"]) == 12 and all(
        result["pairs"][qid][arm].get("composer_contract_ok") is True
        for qid in request["question_order"]
        for arm in ("Q", "P")
    )
    stale_ok = all(
        result["pairs"][qid]["P"]["selection_mode"] == "STALE_PROJECTION_BYPASS"
        and result["pairs"][qid]["P"]["selected_anchor_ids"] == result["pairs"][qid]["Q"]["selected_anchor_ids"]
        and result["pairs"][qid]["P"]["context_sha256"] == result["pairs"][qid]["Q"]["context_sha256"]
        for qid in ("PQ007", "PQ011")
    )
    result["execution_complete"] = bool(
        runner.attempts == request["max_model_call_attempts"] and projection_ok and pair_ok and stale_ok
    )
    result["semantic_promotion"] = (
        "PENDING_FROZEN_ADJUDICATION" if result["execution_complete"] else "NOT_EARNED_INCOMPLETE_EXECUTION"
    )
    save_result(result)

    print(json.dumps({
        "format": result["format"],
        "execution_complete": result["execution_complete"],
        "model_call_attempts": result["model_call_attempts"],
        "projection_builds": len(result["projection_builds"]),
        "pair_count": len(result["pairs"]),
        "stale_bypass_ok": stale_ok,
        "semantic_promotion": result["semantic_promotion"],
        "usage": result["usage"],
    }, indent=2, sort_keys=True))
    return 0 if result["execution_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
