#!/usr/bin/env python3
"""Reuse validated E009 CLI/OTel plumbing for E011."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E009 = ROOT.parent / "E009-canonical-commit-boundary" / "harness"
sys.path.insert(0, str(E009))

from copilot_cli import run_prompt  # type: ignore
from telemetry import aggregate, collect_call  # type: ignore


def call(prompt, model, run_dir, label):
    try:
        return run_prompt(prompt=prompt, model=model, run_dir=run_dir)
    except Exception:
        raise SystemExit(f"E011-STOP infrastructure_call_failure synthetic_call={label} local_artifact_preserved=yes") from None
