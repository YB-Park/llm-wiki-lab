#!/usr/bin/env python3
"""Guarded GitHub Actions runner for the synthetic/public llm-wiki-lab remote lab."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "remote-lab"
REQUEST = LAB / "request.json"
OUT = LAB / "out"
MODEL = "gpt-5.6-luna"
MAX_ALLOWED_CREDITS = 100
EXPECTED = "REMOTE-LAB-LUNA-OK"
EXCLUDED_TOOLS = (
    "bash,powershell,list_bash,list_powershell,read_bash,read_powershell,"
    "stop_bash,stop_powershell,write_bash,write_powershell,apply_patch,create,edit,view,"
    "glob,grep,rg,web_fetch,task,list_agents,read_agent,write_agent,skill,ask_user"
)


def walk(obj: Any):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v
            yield from walk(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk(item)


def unwrap(value: Any) -> Any:
    if isinstance(value, dict):
        for key in ("stringValue", "intValue", "doubleValue", "boolValue", "value"):
            if key in value:
                return unwrap(value[key])
    return value


def otel_summary(path: Path) -> dict[str, Any]:
    totals = {
        "gen_ai.usage.input_tokens": 0.0,
        "gen_ai.usage.output_tokens": 0.0,
        "gen_ai.usage.cache_read.input_tokens": 0.0,
        "github.copilot.cost": 0.0,
        "github.copilot.aiu": 0.0,
    }
    models: set[str] = set()
    if not path.exists():
        return {"present": False, "models": [], **totals}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key, value in walk(obj):
            if key == "key" and isinstance(value, str):
                continue
            if key == "gen_ai.response.model":
                models.add(str(unwrap(value)))
            if key in totals:
                try:
                    totals[key] += float(unwrap(value))
                except (TypeError, ValueError):
                    pass
            if isinstance(obj, dict) and obj.get("key") == "gen_ai.response.model" and "value" in obj:
                models.add(str(unwrap(obj["value"])))
            if isinstance(obj, dict) and obj.get("key") in totals and "value" in obj:
                try:
                    totals[obj["key"]] += float(unwrap(obj["value"]))
                except (TypeError, ValueError):
                    pass
    return {"present": True, "models": sorted(models), **totals}


def contains_signal(obj: Any) -> bool:
    if isinstance(obj, str):
        return EXPECTED in obj
    if isinstance(obj, dict):
        return any(contains_signal(v) for v in obj.values())
    if isinstance(obj, list):
        return any(contains_signal(v) for v in obj)
    return False


def load_request() -> dict[str, Any]:
    data = json.loads(REQUEST.read_text(encoding="utf-8"))
    allowed = {"request_id", "kind", "model", "max_ai_credits"}
    if set(data) != allowed:
        raise SystemExit("REMOTE-LAB status=FAIL reason=request_schema")
    if data["kind"] != "smoke":
        raise SystemExit("REMOTE-LAB status=FAIL reason=unsupported_kind")
    if data["model"] != MODEL:
        raise SystemExit("REMOTE-LAB status=FAIL reason=model_not_luna")
    credits = data["max_ai_credits"]
    if not isinstance(credits, int) or not (1 <= credits <= MAX_ALLOWED_CREDITS):
        raise SystemExit("REMOTE-LAB status=FAIL reason=credit_guard")
    if not isinstance(data["request_id"], str) or not data["request_id"].strip():
        raise SystemExit("REMOTE-LAB status=FAIL reason=request_id")
    return data


def main() -> None:
    req = load_request()
    exe = shutil.which("copilot")
    if not exe:
        raise SystemExit("REMOTE-LAB status=FAIL reason=copilot_missing")
    if not os.environ.get("GITHUB_TOKEN"):
        raise SystemExit("REMOTE-LAB status=FAIL reason=github_token_missing")

    OUT.mkdir(parents=True, exist_ok=True)
    response = OUT / "response.jsonl"
    stderr = OUT / "stderr.log"
    otel = OUT / "otel.jsonl"

    prompt = (
        "This is a transport/authentication smoke test on fictional data. "
        f"Respond with exactly this ASCII token and nothing else: {EXPECTED}"
    )
    env = os.environ.copy()
    env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel)
    env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    env["OTEL_SERVICE_NAME"] = "llm-wiki-lab-remote"
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
        f"--max-ai-credits={req['max_ai_credits']}",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, env=env, timeout=300, check=False)
    response.write_text(proc.stdout, encoding="utf-8")
    stderr.write_text(proc.stderr, encoding="utf-8")

    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    parsed = []
    bad = 0
    for line in lines:
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    signal = any(contains_signal(obj) for obj in parsed)
    tele = otel_summary(otel)
    observed = tele["models"]
    model_ok = (not observed) or any(MODEL in m for m in observed)
    status = proc.returncode == 0 and bool(lines) and bad == 0 and signal and model_ok and tele["present"]

    meta = {
        "request_id": req["request_id"],
        "status": "PASS" if status else "FAIL",
        "return_code": proc.returncode,
        "model_requested": MODEL,
        "models_observed": observed,
        "jsonl_lines": len(lines),
        "jsonl_invalid": bad,
        "expected_signal": signal,
        "otel_present": tele["present"],
        "input_tokens": int(tele["gen_ai.usage.input_tokens"]),
        "output_tokens": int(tele["gen_ai.usage.output_tokens"]),
        "cache_read_tokens": int(tele["gen_ai.usage.cache_read.input_tokens"]),
        "otel_cost_raw": tele["github.copilot.cost"],
        "otel_aiu_raw": tele["github.copilot.aiu"],
        "max_ai_credits": req["max_ai_credits"],
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print("REMOTE-LAB-SMOKE-HANDOFF-v0")
    print(
        f"request={req['request_id']} status={meta['status']} modelRequested={MODEL} "
        f"modelObserved={','.join(observed) if observed else 'otel-model-not-exposed'}"
    )
    print(
        f"jsonlLines={len(lines)} invalidJsonl={bad} expectedSignal={'yes' if signal else 'no'} "
        f"otel={'yes' if tele['present'] else 'no'}"
    )
    print(
        f"tokens in={meta['input_tokens']} out={meta['output_tokens']} cacheRead={meta['cache_read_tokens']} "
        f"otelCostRaw={meta['otel_cost_raw']} otelAiuRaw={meta['otel_aiu_raw']} maxAiCredits={req['max_ai_credits']}"
    )
    print("raw=artifact-only corpus=NOT_USED companyData=NOT_ALLOWED")
    if not status:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
