#!/usr/bin/env python3
"""Isolated text-in/text-out Copilot CLI adapter for E009A.

The experiment prompt is the only semantic input. Workspace/web/tools/custom instructions are
excluded so verifier judgments cannot inspect repository gold labels or local files.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

EXCLUDED_TOOLS = (
    "bash", "powershell", "list_bash", "list_powershell", "read_bash", "read_powershell",
    "stop_bash", "stop_powershell", "write_bash", "write_powershell", "apply_patch", "create",
    "edit", "view", "glob", "grep", "rg", "web_fetch", "task", "list_agents", "read_agent",
    "write_agent", "skill", "ask_user",
)


def cli_version() -> str:
    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")
    proc = subprocess.run([exe, "--version"], text=True, capture_output=True, check=False, timeout=30)
    return (proc.stdout or proc.stderr).strip()


def cli_help_text(exe: str) -> str:
    proc = subprocess.run([exe, "help"], text=True, capture_output=True, check=False, timeout=30)
    return f"{proc.stdout}\n{proc.stderr}"


def help_has_flag(help_text: str, flag: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(flag)}(?![A-Za-z0-9_-])", help_text) is not None


def run_prompt(*, prompt: str, model: str, run_dir: Path, timeout_seconds: int = 900) -> dict[str, Any]:
    if not model or model.lower() == "auto":
        raise ValueError("E009A requires a concrete pinned model; 'auto' is not allowed")

    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")

    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    otel_path = run_dir / "otel.jsonl"
    response_path = run_dir / "response.txt"
    stderr_path = run_dir / "stderr.log"
    transcript_path = run_dir / "session.md"

    env = os.environ.copy()
    env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel_path)
    env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    env["OTEL_SERVICE_NAME"] = "llm-wiki-lab-e009a"
    env["COPILOT_MCP_TOOL_CACHE"] = "false"

    command = [
        exe,
        "--prompt", prompt,
        "--model", model,
        "--silent",
        "--no-ask-user",
        "--no-custom-instructions",
        "--disable-builtin-mcps",
    ]

    local_help = cli_help_text(exe)
    optional_flags_used: list[str] = []
    if help_has_flag(local_help, "--stream"):
        command.append("--stream=off")
        optional_flags_used.append("--stream=off")
    for flag in ("--no-remote", "--no-remote-export", "--no-color", "--no-experimental"):
        if help_has_flag(local_help, flag):
            command.append(flag)
            optional_flags_used.append(flag)
    if help_has_flag(local_help, "--share"):
        command.append(f"--share={transcript_path}")
        optional_flags_used.append("--share=<local transcript>")
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

    meta = {
        "requested_model": model,
        "copilot_cli_version": cli_version(),
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "wall_seconds": round((ended - started).total_seconds(), 3),
        "return_code": proc.returncode,
        "prompt_utf8_bytes": len(prompt.encode("utf-8")),
        "response_utf8_bytes": len(proc.stdout.encode("utf-8")),
        "optional_flags_supported_and_used": optional_flags_used,
        "excluded_tools": list(EXCLUDED_TOOLS),
        "otel_content_capture": False,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    if proc.returncode != 0:
        raise RuntimeError(f"Copilot CLI failed with return code {proc.returncode}; inspect local stderr.log")

    return {**meta, "response": proc.stdout}
