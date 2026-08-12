#!/usr/bin/env python3
"""Minimal programmatic adapter for reproducible GitHub Copilot CLI calls.

This module intentionally treats Copilot as a text-in/text-out semantic engine.
It denies workspace/web/memory tools so E007 conditions see only prompt-provided state.
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

DENIED_TOOLS = ("shell", "write", "read", "url", "memory")


def cli_version() -> str:
    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")
    proc = subprocess.run([exe, "--version"], text=True, capture_output=True, check=False, timeout=30)
    return (proc.stdout or proc.stderr).strip()


def run_prompt(*, prompt: str, model: str, run_dir: Path, timeout_seconds: int = 900) -> dict[str, Any]:
    if not model or model.lower() == "auto":
        raise ValueError("E007 requires a concrete pinned model; 'auto' is not allowed for scored runs")

    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("GitHub Copilot CLI executable 'copilot' was not found on PATH")

    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    otel_path = run_dir / "otel.jsonl"
    transcript_path = run_dir / "session.md"
    stdout_path = run_dir / "stdout.jsonl"
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
        "--no-ask-user",
        "--no-custom-instructions",
        "--no-remote",
        "--no-remote-export",
        "--no-color",
        "--output-format=json",
        "--stream=off",
        f"--share={transcript_path}",
    ]
    for tool in DENIED_TOOLS:
        command.append(f"--deny-tool={tool}")

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

    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    metadata = {
        "requested_model": model,
        "copilot_cli_version": cli_version(),
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "wall_seconds": (ended - started).total_seconds(),
        "return_code": proc.returncode,
        "denied_tools": list(DENIED_TOOLS),
        "no_custom_instructions": True,
        "otel_content_capture": False,
        "command_shape": "copilot --prompt <stored in prompt.md> --model <pinned> --output-format=json ...",
    }
    (run_dir / "meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if proc.returncode != 0:
        raise RuntimeError(f"Copilot CLI failed with return code {proc.returncode}; see {stderr_path}")

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one isolated Copilot CLI prompt and capture audit artifacts")
    parser.add_argument("--model", required=True, help="Concrete Copilot model string; 'auto' is rejected")
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    prompt = args.prompt_file.read_text(encoding="utf-8")
    meta = run_prompt(prompt=prompt, model=args.model, run_dir=args.run_dir, timeout_seconds=args.timeout)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
