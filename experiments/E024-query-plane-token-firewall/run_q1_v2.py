from __future__ import annotations

import argparse
import importlib.util
import json
import os
import statistics
import subprocess
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CORPUS = HERE / "q1-corpus"
REQUEST_PATH = REPO / "remote-lab" / "e024-q1-request.json"
SIGNAL_PATH = REPO / "remote-lab" / "e024-q1-v2-execute.json"
OUT_DIR = REPO / "remote-lab" / "out" / "e024-q1-v2"
SIGNAL_REL = "remote-lab/e024-q1-v2-execute.json"
MODEL = "gpt-5.6-luna"
ADAPTERS_BLOB = "fc62367ab929349a6be13e83258957ba1714265e"


def load_legacy():
    path = HERE / "run_q1.py"
    spec = importlib.util.spec_from_file_location("e024_q1_legacy", path)
    if spec is None or spec.loader is None:
        raise SystemExit("E024-Q1-V2-STOP legacy_loader_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


legacy = load_legacy()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"E024-Q1-V2-STOP git_failed:{' '.join(args)}:{proc.stderr.strip()}")
    return proc.stdout.strip()


def validate_execution_signal() -> dict[str, Any]:
    if not SIGNAL_PATH.exists():
        raise SystemExit("E024-Q1-V2-STOP execution_signal_missing")
    signal = load_json(SIGNAL_PATH)
    expected_keys = {"execute", "frozen_parent_sha", "request_id"}
    if set(signal) != expected_keys:
        raise SystemExit(f"E024-Q1-V2-STOP signal_shape:{sorted(signal)}")
    if signal["execute"] is not True or signal["request_id"] != "e024-q1-token-firewall-v2":
        raise SystemExit("E024-Q1-V2-STOP signal_invalid")

    head = git("rev-parse", "HEAD")
    parent = git("rev-parse", "HEAD^")
    if parent != signal["frozen_parent_sha"]:
        raise SystemExit(f"E024-Q1-V2-STOP frozen_parent_mismatch:{parent}")
    changed = [row for row in git("diff", "--name-only", parent, head).splitlines() if row.strip()]
    if changed != [SIGNAL_REL]:
        raise SystemExit(f"E024-Q1-V2-STOP execution_commit_scope:{changed}")

    adapter_blob = git("rev-parse", f"{parent}:dogfood/llm_wiki/adapters.py")
    if adapter_blob != ADAPTERS_BLOB:
        raise SystemExit(f"E024-Q1-V2-STOP adapters_blob_mismatch:{adapter_blob}")

    return {
        **signal,
        "execution_head_sha": head,
        "changed_paths": changed,
        "adapters_blob": adapter_blob,
    }


def expected_request() -> dict[str, Any]:
    return {
        "answer_max_chars": 900,
        "arms": ["M", "Q"],
        "context_top_k": 6,
        "main_proxy_calls": 9,
        "max_ai_credits_per_call": 30,
        "max_model_call_attempts": 18,
        "model": MODEL,
        "planner_calls": 0,
        "query_plane_calls": 9,
        "question_count": 9,
        "rerolls": 0,
        "request_id": "e024-q1-token-firewall-v0",
        "retrieval_model_calls": 0,
        "selector_calls": 0,
    }


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_pairs(request: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sources = load_jsonl(CORPUS / "sources.jsonl")
    questions = load_json(CORPUS / "questions.json")["questions"]
    frozen_rows = load_json(CORPUS / "context-freeze.json")["contexts"]
    freeze = {row["question_id"]: row for row in frozen_rows}
    by_id = {row["id"]: row for row in sources}

    if len(sources) != 29 or len(questions) != 9 or len(freeze) != 9:
        raise SystemExit("E024-Q1-V2-STOP corpus_count")

    pairs: dict[str, Any] = {}
    for question in questions:
        qid = question["question_id"]
        ranking = legacy.bm25_rank(sources, question["question"])
        selected = [memory_id for memory_id, _ in ranking[: request["context_top_k"]]]
        if selected != freeze[qid]["selected_ids"]:
            raise SystemExit(f"E024-Q1-V2-STOP selection_mismatch:{qid}:{selected}")
        if not set(question["required_terminal_ids"]) <= set(selected):
            raise SystemExit(f"E024-Q1-V2-STOP required_authority_missing:{qid}")
        if not all(by_id[memory_id]["status"] == "current" for memory_id in selected):
            raise SystemExit(f"E024-Q1-V2-STOP noncurrent_selected:{qid}")

        context = legacy.render_context(sources, selected)
        allowed_types = {
            memory_id: by_id[memory_id]["authority_type"]
            for memory_id in selected
            if by_id[memory_id]["authority_type"] in legacy.TERMINAL_TYPES
        }
        pairs[qid] = {
            "question_id": qid,
            "question": question["question"],
            "selected_ids": selected,
            "context_sha256": legacy.sha256_text(context),
            "context_chars": len(context),
            "allowed_terminal_types": allowed_types,
            "required_terminal_ids": question["required_terminal_ids"],
            "expected_insufficient": question["expected_insufficient"],
            "arms": {"M": {}, "Q": {}},
        }

    schedule: list[dict[str, Any]] = []
    call_index = 0
    for position, question in enumerate(questions):
        order = ["M", "Q"] if position % 2 == 0 else ["Q", "M"]
        for arm in order:
            call_index += 1
            schedule.append({"call_index": call_index, "question_id": question["question_id"], "arm": arm})
    return pairs, schedule


def save_result(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args(argv)

    request = load_json(REQUEST_PATH)
    if request != expected_request():
        raise SystemExit(f"E024-Q1-V2-STOP request_mismatch:{request}")

    signal = validate_execution_signal() if args.execute_model else None
    pairs, schedule = build_pairs(request)

    result: dict[str, Any] = {
        "format": "E024-Q1-v2",
        "execute_model": args.execute_model,
        "execution_source_sha": os.environ.get("GITHUB_SHA", "") if args.execute_model else "",
        "execution_signal": signal,
        "request": request,
        "model_call_attempts": 0,
        "execution_complete": False,
        "paired_context_identity": True,
        "call_schedule": schedule,
        "pairs": pairs,
        "usage": {
            "model_calls": 0,
            "tokens": "unavailable_unless_transport_exposes_machine_readable_usage",
            "ai_credits_or_premium_requests": "unavailable_do_not_infer",
        },
        "interpretation_boundary": (
            "Q1-v2 fixes only presemantic freeze mechanics. Question, selected IDs, rendered context, prompts, "
            "model, parsers, and thresholds remain paired/frozen. It does not test iterative retrieval."
        ),
    }
    save_result(result)

    if not args.execute_model:
        chars = sorted(pair["context_chars"] for pair in pairs.values())
        print("E024 Q1 v2 zero-model preflight: PASS")
        print(json.dumps({
            "execute_model": False,
            "model_call_attempts": 0,
            "question_count": len(pairs),
            "scheduled_calls": len(schedule),
            "context_chars_min": chars[0],
            "context_chars_median": chars[len(chars) // 2],
            "context_chars_max": chars[-1],
            "paired_context_identity": True,
            "planner_calls": request["planner_calls"],
            "selector_calls": request["selector_calls"],
            "retrieval_model_calls": request["retrieval_model_calls"],
        }, indent=2, sort_keys=True))
        return 0

    runner = legacy.ModelRunner(request)
    sources = load_jsonl(CORPUS / "sources.jsonl")
    freeze = {row["question_id"]: row for row in load_json(CORPUS / "context-freeze.json")["contexts"]}

    for call in schedule:
        qid = call["question_id"]
        arm = call["arm"]
        pair = pairs[qid]
        context = legacy.render_context(sources, freeze[qid]["selected_ids"])
        allowed_types = pair["allowed_terminal_types"]
        record: dict[str, Any] = {"call_index": call["call_index"]}
        try:
            if arm == "M":
                prompt = legacy.main_prompt(pair["question"], context, request["answer_max_chars"])
            else:
                prompt = legacy.query_plane_prompt(pair["question"], context, request["answer_max_chars"])
            receipt = runner.call(prompt)
            record["model_receipt"] = {k: v for k, v in receipt.items() if k != "text"}
            record["raw_response_chars"] = len(receipt["text"])
            if arm == "M":
                parsed = legacy.parse_main(receipt["text"], set(allowed_types))
                record["result"] = parsed
                record["serialized_result_chars"] = len(compact_json(parsed))
                record["external_chars"] = pair["context_chars"]
            else:
                parsed = legacy.parse_query_plane(receipt["text"], allowed_types)
                serialized = compact_json(parsed)
                record["result"] = parsed
                record["serialized_result_chars"] = len(serialized)
                record["external_chars"] = len(serialized)
                record["external_char_ratio"] = round(len(serialized) / pair["context_chars"], 6)
            record["contract_ok"] = True
        except Exception as exc:
            record["contract_ok"] = False
            record["error"] = str(exc)
        pair["arms"][arm] = record
        result["model_call_attempts"] = runner.attempts
        result["usage"]["model_calls"] = runner.attempts
        save_result(result)

    result["execution_complete"] = runner.attempts == request["max_model_call_attempts"]
    q_records = [pair["arms"]["Q"] for pair in pairs.values()]
    q_valid = [row for row in q_records if row.get("contract_ok") is True]
    ratios = [row["external_char_ratio"] for row in q_valid if "external_char_ratio" in row]
    brief_chars = [row["serialized_result_chars"] for row in q_valid if "serialized_result_chars" in row]
    result["structural_summary"] = {
        "q_contract_valid_count": len(q_valid),
        "q_contract_invalid_count": len(q_records) - len(q_valid),
        "q_external_char_ratio_median": round(statistics.median(ratios), 6) if ratios else None,
        "q_external_char_ratio_max": max(ratios) if ratios else None,
        "q_serialized_brief_chars_max": max(brief_chars) if brief_chars else None,
        "all_attempts_completed": result["execution_complete"],
    }
    save_result(result)
    print(json.dumps(result["structural_summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
