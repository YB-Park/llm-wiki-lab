#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

OTEL_KEYS = {
    "gen_ai.response.model",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "gen_ai.usage.cache_creation.input_tokens",
}

NUMERIC_KEYS = OTEL_KEYS - {"gen_ai.response.model"}


def unwrap(value: Any) -> Any:
    if isinstance(value, dict):
        for key in ("stringValue", "intValue", "doubleValue", "boolValue", "value"):
            if key in value:
                return unwrap(value[key])
        if "values" in value and isinstance(value["values"], list):
            return [unwrap(v) for v in value["values"]]
    return value


def walk(obj: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        key_field = obj.get("key")
        if isinstance(key_field, str) and key_field in OTEL_KEYS and "value" in obj:
            yield key_field, unwrap(obj["value"])
        for key, value in obj.items():
            if key in OTEL_KEYS:
                yield key, unwrap(value)
            yield from walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk(item)


def number(value: Any) -> float | None:
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


def collect_call(call_dir: Path) -> dict[str, Any]:
    totals = {key: 0.0 for key in NUMERIC_KEYS}
    models: set[str] = set()
    otel_path = call_dir / "otel.jsonl"
    if otel_path.exists():
        for line in otel_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            for key, value in walk(obj):
                if key == "gen_ai.response.model":
                    models.add(str(value))
                else:
                    n = number(value)
                    if n is not None:
                        totals[key] += n

    meta_path = call_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    return {
        "otel_present": otel_path.exists(),
        "models": sorted(models),
        "input_tokens": totals["gen_ai.usage.input_tokens"],
        "output_tokens": totals["gen_ai.usage.output_tokens"],
        "cache_read_tokens": totals["gen_ai.usage.cache_read.input_tokens"],
        "cache_write_tokens": totals["gen_ai.usage.cache_creation.input_tokens"],
        "wall_seconds": float(meta.get("wall_seconds") or 0.0),
        "prompt_utf8_bytes": int(meta.get("prompt_utf8_bytes") or 0),
        "response_utf8_bytes": int(meta.get("response_utf8_bytes") or 0),
    }


def aggregate(call_dirs: list[Path]) -> dict[str, Any]:
    rows = [collect_call(path) for path in call_dirs]
    models = sorted({m for row in rows for m in row["models"]})
    return {
        "call_count": len(rows),
        "otel_file_count": sum(int(row["otel_present"]) for row in rows),
        "models": models,
        "input_tokens": sum(row["input_tokens"] for row in rows),
        "output_tokens": sum(row["output_tokens"] for row in rows),
        "cache_read_tokens": sum(row["cache_read_tokens"] for row in rows),
        "cache_write_tokens": sum(row["cache_write_tokens"] for row in rows),
        "wall_seconds": round(sum(row["wall_seconds"] for row in rows), 3),
        "prompt_utf8_bytes": sum(row["prompt_utf8_bytes"] for row in rows),
        "response_utf8_bytes": sum(row["response_utf8_bytes"] for row in rows),
    }
