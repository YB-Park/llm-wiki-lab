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
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

# Use --excluded-tools rather than permission denial: the experiment does not merely
# deny execution, it removes built-in tool capabilities that could change model input.
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


def cli_help_text(exe: str) -> str:
    """Return the flags actually exposed by this local CLI/account combination."""
    proc = subprocess.run([exe, "help"], text=True, capture_output=True, check=False, timeout=30)
    return f"{proc.stdout}\n{proc.stderr}"


def help_has_flag(help_text: str, flag: str) -> bool:
    # Require a token boundary so --no-remote does not accidentally match
    # --no-remote-export (or vice versa).
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(flag)}(?![A-Za-z0-9_-])", help_text) is not None


def run_prompt(*, prompt: str, model: str, run_dir: Path, timeout_seconds: int = 900) -> dict[str, Any]:
    """Run one isolated prompt and return metadata plus final response text.

    Isolation-critical flags remain explicit. Noncritical presentation/session flags are
    capability-detected because Copilot CLI exposure varies by version/account/policy.

    We record explicit payload sizes separately from adapter-level OTel token totals.
    Copilot's observed input-token count can include runtime/system context beyond the
    experiment prompt, so both views are needed for later cost interpretation.
    """
    if not model or model.lower() == "auto":
        raise ValueError("E007 requires a concrete pinned model; 'auto' is not allowed for scored runs")

    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")

    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    prompt_utf8_bytes = len(prompt.encode("utf-8"))
    prompt_chars = len(prompt)

    otel_path = run_dir / "otel.jsonl"
    transcript_path = run_dir / "session.md"
    response_path = run_dir / "response.txt"
    stderr_path = run_dir / "stderr.log"

    env = os.environ.copy()
    env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel_path)
    env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    env["OTEL_SERVICE_NAME"] = "llm-wiki-lab-e007"
    env["COPILOT_MCP_TOOL_CACHE"] = "false"

    # These flags define experimental isolation and are intentionally not silently
    # dropped if a future/older CLI rejects them.
    command = [
        exe,
        "--prompt",
        prompt,
        "--model",
        model,
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

    response_utf8_bytes = len(proc.stdout.encode("utf-8"))
    response_chars = len(proc.stdout)

    metadata: dict[str, Any] = {
        "requested_model": model,
        "copilot_cli_version": cli_version(),
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "wall_seconds": (ended - started).total_seconds(),
        "return_code": proc.returncode,
        "prompt_utf8_bytes": prompt_utf8_bytes,
        "prompt_chars": prompt_chars,
        "response_utf8_bytes": response_utf8_bytes,
        "response_chars": response_chars,
        "excluded_tools": list(EXCLUDED_TOOLS),
        "builtin_mcps_disabled": True,
        "mcp_tool_cache": False,
        "no_custom_instructions": True,
        "no_ask_user": True,
        "optional_flags_supported_and_used": optional_flags_used,
        "otel_content_capture": False,
        "response_file": response_path.name,
        "otel_file": otel_path.name,
        "command_shape": "copilot --prompt <stored in prompt.md> --model <pinned> --silent <supported optional flags> ...",
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
