#!/usr/bin/env python3
"""Deterministic E007 call-category cost ledger.

This classifies already-recorded calls by frozen orchestration names and aggregates
payload sizes, OTel tokens, opaque cost/AIU fields, and wall time. It is post-hoc
measurement only and never changes maintenance behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from handoff_summary import NUMERIC_SUM_KEYS, as_number, collect_otel, load_json

CATEGORIES = (
    "maintenance_update",
    "transition_verify",
    "transition_repair",
    "regression_probe",
    "regression_repair",
    "primary_answer",
    "other",
)


def classify_call(name: str) -> str:
    if "regression-repair" in name:
        return "regression_repair"
    if "regression-before" in name or "regression-after" in name:
        return "regression_probe"
    if "transition-repair" in name:
        return "transition_repair"
    if "verify-" in name:
        return "transition_verify"
    if name.endswith("-primary"):
        return "primary_answer"
    if name.endswith("-update") or name.endswith("-candidate"):
        return "maintenance_update"
    return "other"


def empty_bucket() -> dict[str, Any]:
    return {
        "call_count": 0,
        "wall_seconds": 0.0,
        "prompt_utf8_bytes": 0,
        "response_utf8_bytes": 0,
        "otel_file_count": 0,
        "otel_totals": {key: 0.0 for key in NUMERIC_SUM_KEYS},
    }


def add_call(bucket: dict[str, Any], call_dir: Path) -> None:
    meta = load_json(call_dir / "meta.json", {}) or {}
    bucket["call_count"] += 1
    bucket["wall_seconds"] += float(meta.get("wall_seconds") or 0.0)
    bucket["prompt_utf8_bytes"] += int(meta.get("prompt_utf8_bytes") or 0)
    bucket["response_utf8_bytes"] += int(meta.get("response_utf8_bytes") or 0)

    otel_path = call_dir / "otel.jsonl"
    if otel_path.exists():
        bucket["otel_file_count"] += 1
    attrs = collect_otel(otel_path)
    for key in NUMERIC_SUM_KEYS:
        for value in attrs.get(key, []):
            number = as_number(value)
            if number is not None:
                bucket["otel_totals"][key] += number


def rounded_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    result = dict(bucket)
    result["wall_seconds"] = round(float(result["wall_seconds"]), 3)
    result["otel_totals"] = {
        key: (int(value) if float(value).is_integer() else round(float(value), 4))
        for key, value in result["otel_totals"].items()
    }
    return result


def analyze_cost(run_dir: Path) -> dict[str, Any]:
    config = load_json(run_dir / "run-config.json", {}) or {}
    buckets = {category: empty_bucket() for category in CATEGORIES}
    call_dirs = sorted((run_dir / "calls").glob("*")) if (run_dir / "calls").exists() else []

    call_index: list[dict[str, str]] = []
    for call_dir in call_dirs:
        category = classify_call(call_dir.name)
        add_call(buckets[category], call_dir)
        call_index.append({"call": call_dir.name, "category": category})

    rounded = {category: rounded_bucket(bucket) for category, bucket in buckets.items()}

    maintenance_categories = (
        "maintenance_update",
        "transition_verify",
        "transition_repair",
        "regression_probe",
        "regression_repair",
    )

    def sum_field(categories: tuple[str, ...], field: str) -> float:
        return sum(float(rounded[category][field]) for category in categories)

    def sum_otel(categories: tuple[str, ...], key: str) -> float:
        return sum(float(rounded[category]["otel_totals"][key]) for category in categories)

    maintenance_input = sum_otel(maintenance_categories, "gen_ai.usage.input_tokens")
    maintenance_output = sum_otel(maintenance_categories, "gen_ai.usage.output_tokens")
    primary_input = float(rounded["primary_answer"]["otel_totals"]["gen_ai.usage.input_tokens"])
    primary_output = float(rounded["primary_answer"]["otel_totals"]["gen_ai.usage.output_tokens"])

    return {
        "experiment": config.get("experiment", "E007"),
        "run_id": run_dir.name,
        "condition": config.get("condition", "?"),
        "model": config.get("model", "?"),
        "measurement_role": "post-hoc; never feeds maintenance",
        "categories": rounded,
        "call_index": call_index,
        "headline_split": {
            "maintenance_call_count": int(sum_field(maintenance_categories, "call_count")),
            "primary_answer_call_count": int(rounded["primary_answer"]["call_count"]),
            "maintenance_input_tokens": int(maintenance_input) if maintenance_input.is_integer() else maintenance_input,
            "maintenance_output_tokens": int(maintenance_output) if maintenance_output.is_integer() else maintenance_output,
            "primary_answer_input_tokens": int(primary_input) if primary_input.is_integer() else primary_input,
            "primary_answer_output_tokens": int(primary_output) if primary_output.is_integer() else primary_output,
            "maintenance_prompt_utf8_bytes": int(sum_field(maintenance_categories, "prompt_utf8_bytes")),
            "primary_answer_prompt_utf8_bytes": int(rounded["primary_answer"]["prompt_utf8_bytes"]),
        },
        "cautions": [
            "OTel token counts are adapter-level observations and may include runtime/system context.",
            "Copilot cost/AIU fields remain opaque unless independently verified.",
            "Regression probes are maintenance-time cost in C4 even though they are query-shaped calls.",
        ],
    }


def compact_text(result: dict[str, Any]) -> str:
    split = result["headline_split"]
    return (
        f"COST run={result['run_id']} condition={result['condition']} "
        f"maintCalls={split['maintenance_call_count']} answerCalls={split['primary_answer_call_count']} "
        f"maintIn={split['maintenance_input_tokens']} answerIn={split['primary_answer_input_tokens']} "
        f"maintPromptB={split['maintenance_prompt_utf8_bytes']} "
        f"answerPromptB={split['primary_answer_prompt_utf8_bytes']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute E007 call-category cost metrics")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    result = analyze_cost(args.run_dir)
    (args.run_dir / "cost-metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.compact:
        print(compact_text(result), end="")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
