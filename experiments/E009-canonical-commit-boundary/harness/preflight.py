#!/usr/bin/env python3
"""One-call non-scored rehearsal for the E009A verifier transport/contract path."""

from __future__ import annotations

import json
from pathlib import Path

from copilot_cli import run_prompt
from telemetry import collect_call
from verifier_contract import parse_judgment

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "prompts" / "transition-verifier.md"
OUT = ROOT / "runs" / "preflight-v0"
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
    if (OUT / "status.json").exists():
        status = json.loads((OUT / "status.json").read_text(encoding="utf-8"))
        print("E009A-PREFLIGHT-v0")
        print(f"status={status['status']} model={status['model']} judgment=valid otel={status['otel']}")
        print("quality_result=NONE corpus_T=NOT_USED")
        return
    if call_dir.exists():
        raise SystemExit("E009A-PREFLIGHT-STOP incomplete_local_attempt preserve=yes")

    result = run_prompt(prompt=render(), model=MODEL, run_dir=call_dir)
    parsed = parse_judgment(str(result["response"]))
    if not parsed["valid"]:
        raise SystemExit("E009A-PREFLIGHT-FAIL verifier_contract_invalid inspect_local_artifact=yes")
    tel = collect_call(call_dir)
    OUT.mkdir(parents=True, exist_ok=True)
    status = {"status": "PASS", "model": MODEL, "otel": "yes" if tel["otel_present"] else "no"}
    (OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print("E009A-PREFLIGHT-v0")
    print(f"status=PASS model={MODEL} judgment=valid otel={status['otel']}")
    print("quality_result=NONE corpus_T=NOT_USED")


if __name__ == "__main__":
    main()
