#!/usr/bin/env python3
"""Run frozen E011 Stage 1A through GitHub Actions Copilot JSONL transport."""

from __future__ import annotations

import json
from pathlib import Path

import run_stage_1a as base
import stage1a_core as core
import remote_instrumentation_v1 as remote

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
REQUEST = REPO / "remote-lab" / "e011-request.json"
RUN = ROOT / "runs" / "stage-1a-remote-v1"
MODEL = "gpt-5.6-luna"


def load_request():
    data = json.loads(REQUEST.read_text(encoding="utf-8"))
    required = {"request_id", "kind", "model", "per_call_max_ai_credits", "total_estimated_ai_credit_guard"}
    if set(data) != required:
        raise SystemExit("E011-REMOTE-STOP request_schema")
    if data["kind"] != "e011-stage1a-remote-v1":
        raise SystemExit("E011-REMOTE-STOP request_kind")
    if data["model"] != MODEL:
        raise SystemExit("E011-REMOTE-STOP request_model")
    if not isinstance(data["per_call_max_ai_credits"], int):
        raise SystemExit("E011-REMOTE-STOP request_per_call_guard")
    if not isinstance(data["total_estimated_ai_credit_guard"], (int, float)):
        raise SystemExit("E011-REMOTE-STOP request_total_guard")
    return data


def remote_preflight():
    d = RUN / "remote-preflight"
    p = d / "status.json"
    if p.exists():
        s = json.loads(p.read_text(encoding="utf-8"))
        if s.get("status") == "PASS" and s.get("model") == MODEL:
            print("E011-REMOTE-PREFLIGHT status=PASS reused=yes modelCallsThisRun=0 corpus=NOT_USED quality=NONE")
            return
        raise SystemExit("E011-REMOTE-STOP preflight_status_invalid")
    if d.exists():
        raise SystemExit("E011-REMOTE-STOP incomplete_remote_preflight local_artifact_preserved=yes")

    context = "### SOURCE T99-S01 — Garden note\nZephyr Garden approved the blue notebook as the current field notebook."
    question = "Which notebook is the current approved field notebook for Zephyr Garden?"
    r = remote.call(core.answer_prompt(question, context), MODEL, d, "remote-preflight")
    parsed = core.parse_answer(str(r["response"]), context, {"T99-S01"})
    if not parsed["valid"]:
        raise SystemExit(
            f"E011-REMOTE-STOP preflight_answer_contract_{parsed.get('violation')} local_artifact_preserved=yes"
        )
    p.write_text(json.dumps({"status":"PASS","model":MODEL,"corpus_used":False}, indent=2) + "\n", encoding="utf-8")
    print("E011-REMOTE-PREFLIGHT status=PASS reused=no modelCallsThisRun=1 corpus=NOT_USED quality=NONE")


def main():
    req = load_request()
    remote.configure(
        RUN,
        int(req["per_call_max_ai_credits"]),
        float(req["total_estimated_ai_credit_guard"]),
    )
    RUN.mkdir(parents=True, exist_ok=True)
    remote_preflight()

    # Preserve every frozen semantic operation in the original runner; replace only runtime paths/instrumentation.
    base.RUN = RUN
    base.inst = remote
    base.require_preflight = lambda: None
    base.main()

    print("E011-REMOTE-RUNTIME-HANDOFF-v1")
    print(
        f"request={req['request_id']} model={MODEL} transport=copilot-jsonl "
        f"estimatedCredits={remote.estimated_used():.3f} totalGuard={float(req['total_estimated_ai_credit_guard']):.0f} "
        f"perCallGuard={int(req['per_call_max_ai_credits'])}"
    )
    print("semanticFixture=frozen-v0 modelRerolls=none companyData=NOT_ALLOWED")


if __name__ == "__main__":
    main()
