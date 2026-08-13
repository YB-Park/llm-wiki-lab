#!/usr/bin/env python3
"""One-call non-scored rehearsal for the E009A T-v1 verifier transport/contract path."""

from __future__ import annotations

import json
from pathlib import Path

from copilot_cli import run_prompt
from telemetry import collect_call
from verifier_contract import parse_judgment

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "prompts" / "transition-verifier.md"
OUT = ROOT / "runs" / "preflight-v1"
MODEL = "gpt-5.6-luna"


def render() -> str:
    text = PROMPT.read_text(encoding="utf-8")
    values = {
        "PREVIOUS_STATE": "# Zephyr package\nThe bundle header is ZP1. [P001]",
        "NEW_EVIDENCE": "### P002\nDocumentation is reorganized, but the ZP1 bundle header remains unchanged.",
        "CANDIDATE_STATE": "# Zephyr compatibility\nBundles continue to use the ZP1 header. [P001][P002]",
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> None:
    call_dir = OUT / "call"
    status_path = OUT / "status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        print("E009A-PREFLIGHT-v1")
        print(f"status={status['status']} model={status['model']} judgment=valid otel={status['otel']}")
        print("quality_result=NONE corpus_T=NOT_USED")
        return
    if call_dir.exists():
        raise SystemExit("E009A-PREFLIGHT-STOP incomplete_local_attempt preserve=yes")

    try:
        result = run_prompt(prompt=render(), model=MODEL, run_dir=call_dir)
    except Exception:
        raise SystemExit("E009A-PREFLIGHT-FAIL infrastructure_call_failure local_artifact_preserved=yes") from None

    parsed = parse_judgment(str(result["response"]))
    if not parsed["valid"]:
        raise SystemExit("E009A-PREFLIGHT-FAIL verifier_contract_invalid local_artifact_preserved=yes")
    tel = collect_call(call_dir)
    if not tel["otel_present"]:
        raise SystemExit("E009A-PREFLIGHT-FAIL telemetry_missing local_artifact_preserved=yes")

    OUT.mkdir(parents=True, exist_ok=True)
    status = {"status": "PASS", "model": MODEL, "otel": "yes"}
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print("E009A-PREFLIGHT-v1")
    print(f"status=PASS model={MODEL} judgment=valid otel=yes")
    print("quality_result=NONE corpus_T=NOT_USED")


if __name__ == "__main__":
    main()
