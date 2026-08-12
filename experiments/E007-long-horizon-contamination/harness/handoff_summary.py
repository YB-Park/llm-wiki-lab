#!/usr/bin/env python3
"""Create a tiny sanitized E007 result handoff for restricted-network environments.

Raw prompts, responses, wiki states, and OTel remain in the local run directory.
This module emits only aggregate experiment metadata and scores that are practical
to transfer manually when ChatGPT and GitHub push are unavailable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

OTEL_KEYS = {
    "gen_ai.request.model",
    "gen_ai.response.model",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "gen_ai.usage.cache_creation.input_tokens",
    "github.copilot.turn_count",
    "github.copilot.cost",
    "github.copilot.aiu",
}

NUMERIC_SUM_KEYS = {
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "gen_ai.usage.cache_creation.input_tokens",
    "github.copilot.turn_count",
    "github.copilot.cost",
    "github.copilot.aiu",
}


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def unwrap_otel_value(value: Any) -> Any:
    if isinstance(value, dict):
        for key in ("stringValue", "intValue", "doubleValue", "boolValue", "value"):
            if key in value:
                return unwrap_otel_value(value[key])
        if "arrayValue" in value:
            return unwrap_otel_value(value["arrayValue"])
        if "values" in value and isinstance(value["values"], list):
            return [unwrap_otel_value(v) for v in value["values"]]
    return value


def walk_otel(obj: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        key_field = obj.get("key")
        if isinstance(key_field, str) and key_field in OTEL_KEYS and "value" in obj:
            yield key_field, unwrap_otel_value(obj["value"])
        for key, value in obj.items():
            if key in OTEL_KEYS:
                yield key, unwrap_otel_value(value)
            yield from walk_otel(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_otel(item)


def collect_otel(path: Path) -> dict[str, list[Any]]:
    found: dict[str, list[Any]] = {key: [] for key in OTEL_KEYS}
    if not path.exists():
        return found
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key, value in walk_otel(obj):
            found[key].append(value)
    return found


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def aggregate_telemetry(run_dir: Path) -> dict[str, Any]:
    call_dirs = sorted((run_dir / "calls").glob("*")) if (run_dir / "calls").exists() else []
    totals: dict[str, float] = {key: 0.0 for key in NUMERIC_SUM_KEYS}
    observations: dict[str, int] = {key: 0 for key in NUMERIC_SUM_KEYS}
    requested_models: set[str] = set()
    response_models: set[str] = set()
    wall_seconds = 0.0
    otel_files = 0
    prompt_utf8_bytes = 0
    response_utf8_bytes = 0
    prompt_chars = 0
    response_chars = 0

    for call_dir in call_dirs:
        meta = load_json(call_dir / "meta.json", {}) or {}
        wall_seconds += float(meta.get("wall_seconds") or 0.0)
        prompt_utf8_bytes += int(meta.get("prompt_utf8_bytes") or 0)
        response_utf8_bytes += int(meta.get("response_utf8_bytes") or 0)
        prompt_chars += int(meta.get("prompt_chars") or 0)
        response_chars += int(meta.get("response_chars") or 0)
        if meta.get("requested_model"):
            requested_models.add(str(meta["requested_model"]))

        otel_path = call_dir / "otel.jsonl"
        if otel_path.exists():
            otel_files += 1
        attrs = collect_otel(otel_path)
        for value in attrs.get("gen_ai.response.model", []):
            response_models.add(str(value))
        for key in NUMERIC_SUM_KEYS:
            for value in attrs.get(key, []):
                number = as_number(value)
                if number is not None:
                    totals[key] += number
                    observations[key] += 1

    return {
        "call_count": len(call_dirs),
        "call_wall_seconds_sum": round(wall_seconds, 3),
        "otel_file_count": otel_files,
        "requested_models": sorted(requested_models),
        "response_models": sorted(response_models),
        "payload": {
            "prompt_utf8_bytes": prompt_utf8_bytes,
            "response_utf8_bytes": response_utf8_bytes,
            "prompt_chars": prompt_chars,
            "response_chars": response_chars,
        },
        "totals": totals,
        "observations": observations,
    }


def aggregate_primary_scores(run_dir: Path) -> dict[str, Any]:
    latest: dict[str, dict[str, Any]] = {}
    score_dir = run_dir / "scores"
    if score_dir.exists():
        for path in sorted(score_dir.glob("W*-primary-deterministic.json")):
            payload = load_json(path, {}) or {}
            for item in payload.get("scores", []):
                query_id = item.get("query_id")
                if query_id:
                    latest[str(query_id)] = item
    passed = sorted(qid for qid, item in latest.items() if item.get("passed"))
    failed = sorted(qid for qid, item in latest.items() if not item.get("passed"))
    return {"scored": len(latest), "passed": passed, "failed": failed}


def aggregate_guard_activity(summary: dict[str, Any]) -> dict[str, int]:
    transition_repairs = 0
    transition_final_flags = 0
    regression_repairs = 0
    for wave in summary.get("waves", []):
        transition = wave.get("transition") or {}
        if transition.get("repair_used"):
            transition_repairs += 1
        final_transition = transition.get("final") or {}
        if final_transition.get("decision") == "revise":
            transition_final_flags += 1
        if wave.get("regression_repair_used"):
            regression_repairs += 1
    return {
        "transition_repairs": transition_repairs,
        "transition_final_flags": transition_final_flags,
        "regression_repairs": regression_repairs,
    }


def structural_snapshot(run_dir: Path) -> dict[str, Any]:
    metrics = load_json(run_dir / "structural-metrics.json", {}) or {}
    aggregate = metrics.get("aggregate") or {}
    return {
        "state_count": aggregate.get("state_count", 0),
        "final_wiki_to_raw_byte_ratio": aggregate.get("final_wiki_to_raw_byte_ratio"),
        "final_wiki_utf8_bytes": aggregate.get("final_wiki_utf8_bytes"),
        "final_raw_utf8_bytes": aggregate.get("final_raw_utf8_bytes"),
        "cumulative_changed_lines": aggregate.get("cumulative_changed_lines"),
        "max_changed_lines_per_previous_line": aggregate.get("max_changed_lines_per_previous_line"),
    }


def artifact_fingerprint(run_dir: Path) -> str:
    digest = hashlib.sha256()
    for name in ("run-config.json", "summary.json", "structural-metrics.json"):
        path = run_dir / name
        if path.exists():
            digest.update(name.encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def compact_number(value: float | int) -> str:
    value = float(value)
    if value == int(value):
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def build_handoff(run_dir: Path) -> tuple[dict[str, Any], str]:
    config = load_json(run_dir / "run-config.json", {}) or {}
    summary = load_json(run_dir / "summary.json", {}) or {}
    scores = aggregate_primary_scores(run_dir)
    guards = aggregate_guard_activity(summary)
    telemetry = aggregate_telemetry(run_dir)
    structure = structural_snapshot(run_dir)

    payload = {
        "format": "E007-HANDOFF-v0",
        "run_id": run_dir.name,
        "condition": config.get("condition", "?"),
        "model": config.get("model", "?"),
        "max_wave": config.get("max_wave", "?"),
        "deterministic": {
            "passed_count": len(scores["passed"]),
            "scored_count": scores["scored"],
            "failed_query_ids": scores["failed"],
        },
        "guards": guards,
        "telemetry": telemetry,
        "structure": structure,
        "fingerprint": artifact_fingerprint(run_dir),
    }

    totals = telemetry["totals"]
    tokens = (
        f"in={compact_number(totals['gen_ai.usage.input_tokens'])} "
        f"out={compact_number(totals['gen_ai.usage.output_tokens'])} "
        f"cacheR={compact_number(totals['gen_ai.usage.cache_read.input_tokens'])} "
        f"cacheW={compact_number(totals['gen_ai.usage.cache_creation.input_tokens'])}"
    )
    if telemetry["otel_file_count"] == 0:
        tokens = "unavailable"

    failed = ",".join(scores["failed"]) if scores["failed"] else "-"
    resolved = ",".join(telemetry["response_models"]) if telemetry["response_models"] else "?"
    payload_sizes = telemetry["payload"]

    if structure["state_count"]:
        state_line = (
            f"state=ratio:{structure['final_wiki_to_raw_byte_ratio']} "
            f"wikiB:{structure['final_wiki_utf8_bytes']} rawB:{structure['final_raw_utf8_bytes']} "
            f"churnLines:{structure['cumulative_changed_lines']} "
            f"maxChurn:{structure['max_changed_lines_per_previous_line']}"
        )
    else:
        state_line = "state=n/a"

    lines = [
        "E007-HANDOFF-v0",
        (
            f"run={run_dir.name} condition={payload['condition']} requested={payload['model']} "
            f"resolved={resolved} waves=0..{payload['max_wave']}"
        ),
        f"det={len(scores['passed'])}/{scores['scored']} failed={failed}",
        (
            f"calls={telemetry['call_count']} otel={telemetry['otel_file_count']}/{telemetry['call_count']} "
            f"call_wall_s={telemetry['call_wall_seconds_sum']}"
        ),
        (
            f"guards=transition_repair:{guards['transition_repairs']} "
            f"transition_flag:{guards['transition_final_flags']} "
            f"regression_repair:{guards['regression_repairs']}"
        ),
        (
            f"payload=promptB:{payload_sizes['prompt_utf8_bytes']} "
            f"responseB:{payload_sizes['response_utf8_bytes']}"
        ),
        f"tokens={tokens}",
        state_line,
        (
            f"otel_opaque=cost:{compact_number(totals['github.copilot.cost'])} "
            f"aiu:{compact_number(totals['github.copilot.aiu'])}"
            if telemetry["otel_file_count"]
            else "otel_opaque=unavailable"
        ),
        f"fingerprint={payload['fingerprint']}",
    ]
    return payload, "\n".join(lines) + "\n"


def write_handoff(run_dir: Path) -> str:
    payload, text = build_handoff(run_dir)
    (run_dir / "handoff.txt").write_text(text, encoding="utf-8")
    (run_dir / "handoff.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a compact sanitized handoff for one E007 run")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="Print sanitized JSON instead of compact text")
    args = parser.parse_args()

    payload, text = build_handoff(args.run_dir)
    (args.run_dir / "handoff.txt").write_text(text, encoding="utf-8")
    (args.run_dir / "handoff.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
