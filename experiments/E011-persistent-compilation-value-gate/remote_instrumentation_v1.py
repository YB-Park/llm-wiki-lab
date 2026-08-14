#!/usr/bin/env python3
"""GitHub Actions Copilot JSONL instrumentation for E011 remote replication v1."""

from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

MODEL = "gpt-5.6-luna"
DEFAULT_THRESHOLD = 200_000
DEFAULT_INPUT_USD_PER_M = 1.00
DEFAULT_CACHE_USD_PER_M = 0.10
DEFAULT_OUTPUT_USD_PER_M = 6.00
LONG_INPUT_USD_PER_M = 2.00
LONG_CACHE_USD_PER_M = 0.20
LONG_OUTPUT_USD_PER_M = 9.00
USD_PER_AI_CREDIT = 0.01
EXCLUDED_TOOLS = (
    "bash,powershell,list_bash,list_powershell,read_bash,read_powershell,"
    "stop_bash,stop_powershell,write_bash,write_powershell,apply_patch,create,edit,view,"
    "glob,grep,rg,web_fetch,task,list_agents,read_agent,write_agent,skill,ask_user"
)

_RUN_ROOT: Path | None = None
_PER_CALL_MAX = 30
_TOTAL_GUARD = 700.0


def configure(run_root: Path, per_call_max: int, total_guard: float) -> None:
    global _RUN_ROOT, _PER_CALL_MAX, _TOTAL_GUARD
    if per_call_max <= 0 or per_call_max > 100:
        raise ValueError("per-call credit guard out of range")
    if total_guard <= 0 or total_guard > 1000:
        raise ValueError("total credit guard out of range")
    _RUN_ROOT = run_root
    _PER_CALL_MAX = int(per_call_max)
    _TOTAL_GUARD = float(total_guard)


def estimated_used() -> float:
    if _RUN_ROOT is None or not _RUN_ROOT.exists():
        return 0.0
    total = 0.0
    for p in _RUN_ROOT.rglob("remote-meta.json"):
        try:
            total += float(json.loads(p.read_text(encoding="utf-8"))["estimated_ai_credits"])
        except Exception:
            continue
    return total


def _invoke_agent_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError("otel_missing")
    candidates = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("name") == "invoke_agent" and isinstance(obj.get("attributes"), dict):
            candidates.append(obj["attributes"])
    if len(candidates) != 1:
        raise ValueError(f"invoke_agent_span_count_{len(candidates)}")
    a = candidates[0]
    return {
        "model": str(a.get("gen_ai.request.model") or ""),
        "input_tokens": int(a.get("gen_ai.usage.input_tokens") or 0),
        "output_tokens": int(a.get("gen_ai.usage.output_tokens") or 0),
        "cache_read_tokens": int(a.get("gen_ai.usage.cache_read.input_tokens") or 0),
        "cache_write_tokens": int(a.get("gen_ai.usage.cache_creation.input_tokens") or 0),
        "otel_cost_raw": float(a.get("github.copilot.cost") or 0.0),
        "otel_nano_aiu_raw": float(a.get("github.copilot.nano_aiu") or 0.0),
        "turn_count": int(a.get("github.copilot.turn_count") or 0),
    }


def _estimated_credits(input_tokens: int, output_tokens: int, cache_read_tokens: int) -> float:
    long = input_tokens > DEFAULT_THRESHOLD
    input_rate = LONG_INPUT_USD_PER_M if long else DEFAULT_INPUT_USD_PER_M
    cache_rate = LONG_CACHE_USD_PER_M if long else DEFAULT_CACHE_USD_PER_M
    output_rate = LONG_OUTPUT_USD_PER_M if long else DEFAULT_OUTPUT_USD_PER_M
    normal_input = max(0, input_tokens - cache_read_tokens)
    usd = (
        normal_input * input_rate / 1_000_000
        + cache_read_tokens * cache_rate / 1_000_000
        + output_tokens * output_rate / 1_000_000
    )
    return usd / USD_PER_AI_CREDIT


def _final_message(stdout: str) -> tuple[str, str, int]:
    events = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError("jsonl_invalid") from exc
    finals = []
    for event in events:
        if event.get("type") != "assistant.message":
            continue
        data = event.get("data")
        if not isinstance(data, dict) or data.get("phase") != "final_answer":
            continue
        if not isinstance(data.get("content"), str):
            continue
        finals.append(data)
    if len(finals) != 1:
        raise ValueError(f"final_message_count_{len(finals)}")
    data = finals[0]
    tools = data.get("toolRequests")
    if tools not in (None, []):
        raise ValueError("tool_request_present")
    return data["content"], str(data.get("model") or ""), len(events)


def call(prompt: str, model: str, run_dir: Path, label: str) -> dict[str, Any]:
    if _RUN_ROOT is None:
        raise RuntimeError("remote instrumentation not configured")
    if model != MODEL:
        raise SystemExit(f"E011-REMOTE-STOP model_mismatch synthetic_call={label}")
    used = estimated_used()
    if used >= _TOTAL_GUARD:
        raise SystemExit(
            f"E011-REMOTE-STOP total_credit_guard estimatedUsed={used:.2f} guard={_TOTAL_GUARD:.0f} "
            f"synthetic_call={label} partial_artifact_preserved=yes"
        )

    exe = shutil.which("copilot")
    if not exe:
        raise SystemExit(f"E011-REMOTE-STOP copilot_missing synthetic_call={label}")
    if not os.environ.get("GITHUB_TOKEN"):
        raise SystemExit(f"E011-REMOTE-STOP github_token_missing synthetic_call={label}")

    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    stdout_path = run_dir / "stream.jsonl"
    stderr_path = run_dir / "stderr.log"
    response_path = run_dir / "response.txt"
    otel_path = run_dir / "otel.jsonl"

    env = os.environ.copy()
    env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel_path)
    env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    env["OTEL_SERVICE_NAME"] = "llm-wiki-lab-e011-remote-v1"
    env["COPILOT_MCP_TOOL_CACHE"] = "false"

    cmd = [
        exe,
        "--prompt", prompt,
        "--model", MODEL,
        "--output-format=json",
        "--stream=off",
        "--no-ask-user",
        "--no-custom-instructions",
        "--disable-builtin-mcps",
        "--no-color",
        "--no-experimental",
        "--no-remote",
        "--no-remote-export",
        f"--excluded-tools={EXCLUDED_TOOLS}",
        f"--max-ai-credits={_PER_CALL_MAX}",
    ]
    started = dt.datetime.now(dt.timezone.utc)
    proc = subprocess.run(cmd, text=True, capture_output=True, env=env, timeout=900, check=False)
    ended = dt.datetime.now(dt.timezone.utc)
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    if proc.returncode != 0:
        raise SystemExit(
            f"E011-REMOTE-STOP infrastructure_call_failure synthetic_call={label} "
            "local_artifact_preserved=yes"
        )
    try:
        content, event_model, event_count = _final_message(proc.stdout)
        metrics = _invoke_agent_metrics(otel_path)
    except ValueError as exc:
        raise SystemExit(
            f"E011-REMOTE-STOP transport_contract_{str(exc)} synthetic_call={label} "
            "local_artifact_preserved=yes"
        ) from None
    if event_model != MODEL or metrics["model"] != MODEL:
        raise SystemExit(
            f"E011-REMOTE-STOP observed_model_mismatch synthetic_call={label} local_artifact_preserved=yes"
        )

    response_path.write_text(content, encoding="utf-8")
    credits = _estimated_credits(metrics["input_tokens"], metrics["output_tokens"], metrics["cache_read_tokens"])
    meta = {
        "requested_model": MODEL,
        "event_model": event_model,
        "otel_model": metrics["model"],
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "wall_seconds": round((ended - started).total_seconds(), 3),
        "return_code": proc.returncode,
        "event_count": event_count,
        "prompt_utf8_bytes": len(prompt.encode("utf-8")),
        "response_utf8_bytes": len(content.encode("utf-8")),
        **metrics,
        "estimated_ai_credits": credits,
        "estimated_total_after_call": used + credits,
        "per_call_max_ai_credits": _PER_CALL_MAX,
        "total_estimated_credit_guard": _TOTAL_GUARD,
    }
    (run_dir / "remote-meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return {**meta, "response": content}


def collect_call(call_dir: Path) -> dict[str, Any]:
    p = call_dir / "remote-meta.json"
    if not p.exists():
        return {
            "otel_present": False, "models": [], "input_tokens": 0.0, "output_tokens": 0.0,
            "cache_read_tokens": 0.0, "cache_write_tokens": 0.0, "wall_seconds": 0.0,
            "prompt_utf8_bytes": 0, "response_utf8_bytes": 0, "estimated_ai_credits": 0.0,
            "otel_cost_raw": 0.0, "otel_nano_aiu_raw": 0.0,
        }
    m = json.loads(p.read_text(encoding="utf-8"))
    return {
        "otel_present": True,
        "models": [m["otel_model"]] if m.get("otel_model") else [],
        "input_tokens": float(m.get("input_tokens") or 0),
        "output_tokens": float(m.get("output_tokens") or 0),
        "cache_read_tokens": float(m.get("cache_read_tokens") or 0),
        "cache_write_tokens": float(m.get("cache_write_tokens") or 0),
        "wall_seconds": float(m.get("wall_seconds") or 0),
        "prompt_utf8_bytes": int(m.get("prompt_utf8_bytes") or 0),
        "response_utf8_bytes": int(m.get("response_utf8_bytes") or 0),
        "estimated_ai_credits": float(m.get("estimated_ai_credits") or 0),
        "otel_cost_raw": float(m.get("otel_cost_raw") or 0),
        "otel_nano_aiu_raw": float(m.get("otel_nano_aiu_raw") or 0),
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
        "estimated_ai_credits": sum(row["estimated_ai_credits"] for row in rows),
        "otel_cost_raw": sum(row["otel_cost_raw"] for row in rows),
        "otel_nano_aiu_raw": sum(row["otel_nano_aiu_raw"] for row in rows),
    }
