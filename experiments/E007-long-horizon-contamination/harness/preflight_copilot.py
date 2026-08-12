#!/usr/bin/env python3
"""Non-scored local preflight for the E007 Copilot CLI adapter.

This uses unrelated synthetic facts so it validates authentication, response capture,
JSON parsing, and OpenTelemetry without revealing any E007 comparative result.

Default stdout is intentionally tiny because the target corporate network cannot use
ChatGPT or GitHub push. Use --json only when detailed sanitized diagnostics are needed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Iterable

from copilot_cli import run_prompt
from score_deterministic import extract_json_object

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local"

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

PREFLIGHT_PROMPT = """This is a non-scored infrastructure test for a synthetic knowledge-maintenance harness.
Do not use tools or outside knowledge.

Synthetic evidence:
- Note P1: Project Zephyr uses a Cedar datastore and cache TTL of 12 minutes.
- Note P2: On 2026-07-01, Zephyr changed its cache TTL from 12 minutes to 7 minutes. Cedar did not change.
- Note P3: The exact export marker is ZPHR9. This marker is unrelated to the cache change.

Return JSON only, exactly in this shape:
{
  "current_store": "...",
  "current_cache_ttl_minutes": 0,
  "historical_cache_ttl_minutes": 0,
  "export_marker": "...",
  "change_kind": "temporal_change"
}
"""


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


def summarize_otel(path: Path) -> dict[str, Any]:
    found: dict[str, list[Any]] = {key: [] for key in sorted(OTEL_KEYS)}
    if not path.exists():
        return {"otel_file_exists": False, "attributes": {}}

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key, value in walk_otel(obj):
            if value not in found[key]:
                found[key].append(value)

    compact = {key: values for key, values in found.items() if values}
    return {"otel_file_exists": True, "attributes": compact}


def validate_preflight_answer(text: str) -> dict[str, Any]:
    payload = extract_json_object(text)
    expected = {
        "current_store": "Cedar",
        "current_cache_ttl_minutes": 7,
        "historical_cache_ttl_minutes": 12,
        "export_marker": "ZPHR9",
        "change_kind": "temporal_change",
    }
    mismatches = {}
    for key, value in expected.items():
        if payload.get(key) != value:
            mismatches[key] = {"expected": value, "actual": payload.get(key)}
    return {"passed": not mismatches, "mismatches": mismatches, "parsed_response": payload}


def short_values(attributes: dict[str, list[Any]], key: str) -> str:
    values = attributes.get(key, [])
    if not values:
        return "?"
    return ",".join(str(v) for v in values)


def compact_handoff(summary: dict[str, Any]) -> str:
    attrs = summary["otel_attributes"]
    resolved = short_values(attrs, "gen_ai.response.model")
    input_tokens = short_values(attrs, "gen_ai.usage.input_tokens")
    output_tokens = short_values(attrs, "gen_ai.usage.output_tokens")
    cost = short_values(attrs, "github.copilot.cost")
    aiu = short_values(attrs, "github.copilot.aiu")
    status = "PASS" if summary["response_contract_passed"] and summary["return_code"] == 0 else "FAIL"
    otel = "yes" if summary["otel_file_exists"] else "no"
    return "\n".join(
        [
            "PREFLIGHT-HANDOFF-v0",
            (
                f"status={status} requested={summary['requested_model']} resolved={resolved} "
                f"cli={summary['copilot_cli_version']} wall_s={summary['wall_seconds']:.2f}"
            ),
            f"otel={otel} in={input_tokens} out={output_tokens} cost={cost} aiu={aiu}",
        ]
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one non-scored Copilot CLI infrastructure preflight")
    parser.add_argument("--model", required=True, help="Concrete Copilot model string; do not use auto")
    parser.add_argument("--json", action="store_true", help="Print detailed sanitized JSON instead of 3-line handoff")
    args = parser.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = LOCAL / f"preflight-{stamp}"
    result = run_prompt(prompt=PREFLIGHT_PROMPT, model=args.model, run_dir=run_dir, timeout_seconds=300)

    answer_check = validate_preflight_answer(str(result["response"]))
    otel = summarize_otel(run_dir / "otel.jsonl")

    summary = {
        "preflight": "E007-non-scored",
        "requested_model": args.model,
        "copilot_cli_version": result["copilot_cli_version"],
        "return_code": result["return_code"],
        "wall_seconds": result["wall_seconds"],
        "response_contract_passed": answer_check["passed"],
        "response_mismatches": answer_check["mismatches"],
        "otel_file_exists": otel["otel_file_exists"],
        "otel_attributes": otel["attributes"],
        "note": "Raw local artifacts are gitignored. Transfer only this sanitized handoff unless deeper debugging is needed.",
    }

    handoff = compact_handoff(summary)
    (run_dir / "handoff.txt").write_text(handoff, encoding="utf-8")
    (run_dir / "handoff.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(handoff, end="")


if __name__ == "__main__":
    main()
