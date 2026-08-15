from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = ROOT / "experiments/E018-steward-policy/run_e018.py"
REQUEST_PATH = ROOT / "remote-lab/e018-steward-policy-request.json"
SEED_PATH = ROOT / "experiments/E018-steward-policy/phase1-seed-run-31888767216.json"


def load_base():
    spec = importlib.util.spec_from_file_location("e018_phase1_base", BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("e018_base_runner_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_request_v2() -> dict[str, Any]:
    row = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e018-steward-policy-20260815-1",
        "phase1_max_model_calls": 24,
        "phase2_max_model_calls": 4,
        "steward_model": "gpt-5.6-luna",
        "baseline_models": ["gpt-5.4", "claude-sonnet-4.6"],
        "phase2_case_ids": ["C1-relevant-read", "C6-conflict-pending-decision"],
        "max_ai_credits_policy": 30,
        "max_ai_credits_answer": 30,
    }
    if row != expected:
        raise RuntimeError(f"request_mismatch:{row}")
    return row


def robust_parse_final(stdout: str):
    """Accept the current Copilot CLI final-message shapes across model families.

    GPT currently emits `phase=final_answer`; Claude may emit the same terminal
    `assistant.message` without a phase field. Tools are disabled, so exactly one
    content-bearing terminal assistant message is expected.
    """
    events: list[dict[str, Any]] = []
    messages: list[dict[str, Any]] = []
    explicit_finals: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if isinstance(event, dict):
            events.append(event)
        if event.get("type") != "assistant.message":
            continue
        data = event.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("content"), str):
            continue
        if data.get("toolRequests") not in (None, []):
            raise RuntimeError("copilot_tool_request_present")
        messages.append(data)
        if data.get("phase") == "final_answer":
            explicit_finals.append(data)
    if len(explicit_finals) == 1:
        data = explicit_finals[0]
    elif not explicit_finals and len(messages) == 1:
        data = messages[0]
    else:
        raise RuntimeError(
            f"copilot_final_message_ambiguous:explicit={len(explicit_finals)}:messages={len(messages)}"
        )
    return data["content"].strip(), str(data.get("model") or ""), events


def load_seed(base, cases_by_id: dict[str, dict[str, Any]], request: dict[str, Any]):
    doc = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    if doc.get("format") != "E018-PHASE1-SEED-v0":
        raise RuntimeError("seed_format_mismatch")
    if doc.get("source_run_id") != 31888767216 or doc.get("source_artifact_id") != 9247969739:
        raise RuntimeError("seed_source_mismatch")
    rows = doc.get("rows")
    if not isinstance(rows, list) or len(rows) != 2:
        raise RuntimeError("seed_count_mismatch")
    expected_keys = {
        ("baseline", "C1-relevant-read", "gpt-5.4"),
        ("baseline", "C1-relevant-read", "claude-sonnet-4.6"),
    }
    result = {}
    for row in rows:
        key = (row.get("condition"), row.get("case_id"), row.get("model"))
        if key not in expected_keys or key in result:
            raise RuntimeError(f"seed_key_invalid:{key}")
        if row["model"] not in request["baseline_models"]:
            raise RuntimeError(f"seed_model_invalid:{row['model']}")
        memory = base.normalize_memory(row.get("memory"))
        if memory is None:
            raise RuntimeError(f"seed_memory_invalid:{key}")
        call = row.get("call")
        if not isinstance(call, dict) or call.get("model_match") is not True:
            raise RuntimeError(f"seed_call_invalid:{key}")
        score = base.score(cases_by_id[row["case_id"]], memory, True)
        if not score["case_pass"]:
            raise RuntimeError(f"seed_no_longer_scores_pass:{key}:{score}")
        result[key] = {
            "case_id": row["case_id"],
            "model": row["model"],
            "memory": memory,
            "assistant_reply": row.get("assistant_reply"),
            "call": call,
            "score": score,
            "reused_seed": True,
            "raw_jsonl_sha256": row.get("raw_jsonl_sha256"),
            "source_run_id": doc["source_run_id"],
            "source_artifact_id": doc["source_artifact_id"],
        }
    if set(result) != expected_keys:
        raise RuntimeError("seed_keys_incomplete")
    return result


def aggregate_and_finish(base, request, baseline, steward, new_model_calls, seeded_calls):
    baseline_aggregate = {model: base.aggregate(rows) for model, rows in baseline.items()}
    steward_aggregate = base.aggregate(steward)
    left_model, right_model = request["baseline_models"]
    disagreements = []
    for left, right in zip(baseline[left_model], baseline[right_model]):
        if left["memory"] != right["memory"]:
            disagreements.append({
                "case_id": left["case_id"],
                left_model: left["memory"],
                right_model: right["memory"],
            })
    baseline_mean_passes = sum(row["passes"] for row in baseline_aggregate.values()) / len(baseline_aggregate)
    phase2_eligible = (
        steward_aggregate["passes"] >= 7
        and steward_aggregate["protected_violations"] == 0
        and (
            len(disagreements) >= 2
            or any(row["protected_violations"] > 0 for row in baseline_aggregate.values())
            or any(row["passes"] <= 6 for row in baseline_aggregate.values())
        )
        and steward_aggregate["passes"] - baseline_mean_passes >= 1.0
    )
    return {
        "status": "PHASE1_COMPLETE_PHASE2_ELIGIBLE" if phase2_eligible else "PHASE1_COMPLETE_STOP",
        "model_calls": new_model_calls,
        "seeded_completed_calls": seeded_calls,
        "total_scored_calls": new_model_calls + seeded_calls,
        "baseline": baseline,
        "steward": steward,
        "baseline_aggregate": baseline_aggregate,
        "steward_aggregate": steward_aggregate,
        "baseline_cross_model_disagreements": disagreements,
        "baseline_mean_passes": baseline_mean_passes,
        "phase2_eligible": phase2_eligible,
        "phase2_reserved_case_ids": request["phase2_case_ids"],
        "phase2_reserved_max_calls": request["phase2_max_model_calls"],
    }


def main() -> int:
    base = load_base()
    base.load_request = load_request_v2
    base.parse_final = robust_parse_final
    request = load_request_v2()
    cases = base.validate_cases()
    cases_by_id = {case["id"]: case for case in cases}
    seeds = load_seed(base, cases_by_id, request)
    seeded_calls = len(seeds)
    if seeded_calls != 2 or request["phase1_max_model_calls"] - seeded_calls != 22:
        raise RuntimeError("resume_budget_mismatch")

    base.OUT.mkdir(parents=True, exist_ok=True)
    base.RAW_OUT.mkdir(parents=True, exist_ok=True)
    for path in base.OUT.rglob("*"):
        if path.is_file():
            path.unlink()

    result: dict[str, Any] = {
        "format": "E018-STEWARD-PHASE1-RESUME-v2",
        "request": request,
        "model_calls": 0,
        "seeded_completed_calls": seeded_calls,
        "case_ids": base.EXPECTED_CASE_IDS,
    }
    if os.environ.get("E018_EXECUTE_MODEL") != "1":
        result.update({
            "status": "PREFLIGHT_PASS",
            "preflight": {
                "cases": len(cases),
                "seeded_completed_calls": seeded_calls,
                "new_calls_if_executed": 22,
                "total_scored_calls_if_executed": 24,
                "baseline_models": request["baseline_models"],
                "steward_model": request["steward_model"],
                "phase2_reserved_followup_calls": request["phase2_max_model_calls"],
            },
        })
        (base.OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result["preflight"], ensure_ascii=False, indent=2))
        return 0

    baseline: dict[str, list[dict[str, Any]]] = {model: [] for model in request["baseline_models"]}
    steward: list[dict[str, Any]] = []
    new_model_calls = 0
    try:
        for case in cases:
            for model in request["baseline_models"]:
                key = ("baseline", case["id"], model)
                if key in seeds:
                    baseline[model].append(seeds[key])
                    continue
                if seeded_calls + new_model_calls >= request["phase1_max_model_calls"]:
                    raise RuntimeError("phase1_total_call_budget_exhausted")
                new_model_calls += 1
                call = base.call_model(
                    base.baseline_prompt(case),
                    model,
                    request["max_ai_credits_policy"],
                    base.RAW_OUT / f"baseline-{base.safe_name(model)}-{case['id']}.jsonl",
                )
                parsed = call.pop("parsed")
                memory = base.normalize_memory(parsed.get("memory"))
                baseline[model].append({
                    "case_id": case["id"],
                    "model": model,
                    "memory": memory,
                    "assistant_reply": parsed.get("assistant_reply"),
                    "call": call,
                    "score": base.score(case, memory, call["model_match"]),
                    "reused_seed": False,
                })

            if seeded_calls + new_model_calls >= request["phase1_max_model_calls"]:
                raise RuntimeError("phase1_total_call_budget_exhausted")
            model = request["steward_model"]
            new_model_calls += 1
            call = base.call_model(
                base.steward_prompt(case),
                model,
                request["max_ai_credits_policy"],
                base.RAW_OUT / f"steward-{base.safe_name(model)}-{case['id']}.jsonl",
            )
            parsed = call.pop("parsed")
            memory = base.normalize_memory(parsed)
            steward.append({
                "case_id": case["id"],
                "model": model,
                "memory": memory,
                "call": call,
                "score": base.score(case, memory, call["model_match"]),
                "reused_seed": False,
            })
    except Exception as exc:
        result.update({
            "status": "INFRA_FAIL",
            "error": f"{type(exc).__name__}:{exc}",
            "model_calls": new_model_calls,
            "baseline": baseline,
            "steward": steward,
        })
        (base.OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": result["status"], "new_model_calls": new_model_calls, "seeded": seeded_calls, "error": result["error"]}, ensure_ascii=False, indent=2))
        return 2

    result.update(aggregate_and_finish(base, request, baseline, steward, new_model_calls, seeded_calls))
    if result["total_scored_calls"] != 24:
        raise RuntimeError(f"scored_call_count_mismatch:{result['total_scored_calls']}")
    (base.OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "new_model_calls": result["model_calls"],
        "seeded_completed_calls": result["seeded_completed_calls"],
        "total_scored_calls": result["total_scored_calls"],
        "baseline_aggregate": result["baseline_aggregate"],
        "steward_aggregate": result["steward_aggregate"],
        "baseline_disagreements": len(result["baseline_cross_model_disagreements"]),
        "phase2_eligible": result["phase2_eligible"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
