#!/usr/bin/env python3
"""Minimal programmatic adapter for reproducible GitHub Copilot CLI calls.

This module intentionally treats Copilot as a text-in/text-out semantic engine.
It excludes workspace/web/memory tools so E007 conditions see only prompt-provided state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

# Use --excluded-tools rather than permission denial: the experiment does not merely
# deny execution, it removes tool capabilities that could change the model's input.
EXCLUDED_TOOLS = (
    "bash",
    "powershell",
    "list_bash",
    "list_powershell",
    "read_bash",
    "read_powershell",
    "stop_bash",
    "stop_powershell",
    "write_bash",
    "write_powershell",
    "apply_patch",
    "create",
    "edit",
    "view",
    "glob",
    "grep",
    "rg",
    "web_fetch",
    "task",
    "list_agents",
    "read_agent",
    "write_agent",
    "skill",
    "ask_user",
)


def cli_version() -> str:
    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")
    proc = subprocess.run([exe, "--version"], text=True, capture_output=True, check=False, timeout=30)
    return (proc.stdout or proc.stderr).strip()


def run_prompt(*, prompt: str, model: str, run_dir: Path, timeout_seconds: int = 900) -> dict[str, Any]:
    """Run one isolated prompt and return metadata plus final response text.

    GitHub documents --silent as the scripting-oriented mode that emits only the
    agent response. We keep telemetry separate in the OTel file so the response
    parser is not coupled to Copilot CLI's JSONL event representation.
    """
    if not model or model.lower() == "auto":
        raise ValueError("E007 requires a concrete pinned model; 'auto' is not allowed for scored runs")

    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")

    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    otel_path = run_dir / "otel.jsonl"
    transcript_path = run_dir / "session.md"
    response_path = run_dir / "response.txt"
    stderr_path = run_dir / "stderr.log"

    env = os.environ.copy()
    env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel_path)
    env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    env["OTEL_SERVICE_NAME"] = "llm-wiki-lab-e007"

    command = [
        exe,
        "--prompt",
        prompt,
        "--model",
        model,
        "--silent",
        "--stream=off",
        "--no-ask-user",
        "--no-custom-instructions",
        "--no-remote",
        "--no-remote-export",
        "--no-color",
        "--no-experimental",
        f"--share={transcript_path}",
    ]
    for tool in EXCLUDED_TOOLS:
        command.append(f"--excluded-tools={tool}")

    started = dt.datetime.now(dt.timezone.utc)
    proc = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
        env=env,
    )
    ended = dt.datetime.now(dt.timezone.utc)

    response_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    metadata: dict[str, Any] = {
        "requested_model": model,
        "copilot_cli_version": cli_version(),
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "wall_seconds": (ended - started).total_seconds(),
        "return_code": proc.returncode,
        "excluded_tools": list(EXCLUDED_TOOLS),
        "no_custom_instructions": True,
        "no_experimental": True,
        "otel_content_capture": False,
        "response_file": response_path.name,
        "otel_file": otel_path.name,
        "command_shape": "copilot --prompt <stored in prompt.md> --model <pinned> --silent --stream=off ...",
    }
    (run_dir / "meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if proc.returncode != 0:
        raise RuntimeError(f"Copilot CLI failed with return code {proc.returncode}; see {stderr_path}")

    return {**metadata, "response": proc.stdout}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one isolated Copilot CLI prompt and capture audit artifacts")
    parser.add_argument("--model", required=True, help="Concrete Copilot model string; 'auto' is rejected")
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    prompt = args.prompt_file.read_text(encoding="utf-8")
    result = run_prompt(prompt=prompt, model=args.model, run_dir=args.run_dir, timeout_seconds=args.timeout)
    print(json.dumps({k: v for k, v in result.items() if k != "response"}, indent=2))


if __name__ == "__main__":
    main()
