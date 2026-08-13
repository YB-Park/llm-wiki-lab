#!/usr/bin/env python3
"""Non-scored E011 compiler/answer rehearsal on a separate micro-world."""

import json
from pathlib import Path

import instrumentation as inst
import stage1a_core as core

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "preflight-v0"
STATUS = RUN / "status.json"
MODEL = "gpt-5.6-luna"

MICRO_DOCS = [
    {"source_id":"T99-S01","title":"Garden note","text":"Zephyr Garden approved the blue notebook as the current field notebook."},
    {"source_id":"T99-S02","title":"Retired draft","text":"An earlier Zephyr Garden draft proposed the green notebook, but that draft was retired."},
]
QUESTION = "Which notebook is the current approved field notebook for Zephyr Garden?"
ALLOWED_IDS = {d["source_id"] for d in MICRO_DOCS}


def report_pass(model_calls_this_run, normalization, contract_violation=None):
    print("E011-PREFLIGHT-v0")
    print(
        f"status=PASS model={MODEL} callsObserved=2 modelCallsThisRun={model_calls_this_run} "
        f"otel=2/2 payloadJson=yes visibleSourceIds=yes "
        f"normalization={normalization or 'none'} contractViolation={contract_violation or 'none'}"
    )
    print("corpus=NOT_USED quality_result=NONE")


def parse_preflight_payload(text, context):
    parsed = core.parse_answer(text, context, ALLOWED_IDS)
    if parsed["valid"] or parsed.get("violation") != "json":
        return parsed, None

    s = text.strip()
    first = s.find("{")
    last = s.rfind("}")
    if first <= 0 or last <= first:
        return parsed, None
    if s[last + 1:].strip():
        return parsed, None

    inner = s[first:last + 1]
    recovered = core.parse_answer(inner, context, ALLOWED_IDS)
    if not recovered["valid"]:
        return parsed, None

    recovered = dict(recovered)
    recovered["normalization"] = "preflight_leading_prefix_payload"
    return recovered, "prefix_noise"


def accept_existing(build_dir, answer_dir):
    bp=build_dir/"response.txt"; ap=answer_dir/"response.txt"
    if not (bp.exists() and ap.exists()): return False
    summary=bp.read_text(encoding="utf-8").strip()
    if not summary: raise SystemExit("E011-PREFLIGHT status=FAIL reason=empty_compiler local_artifact_preserved=yes")
    context="### COMPILED TOPIC NOTE\n"+summary
    parsed, contract_violation = parse_preflight_payload(ap.read_text(encoding="utf-8"),context)
    if not parsed["valid"]:
        raise SystemExit(f"E011-PREFLIGHT status=FAIL reason=answer_contract_{parsed.get('violation')} local_artifact_preserved=yes")
    rows=[inst.collect_call(build_dir),inst.collect_call(answer_dir)]
    if sum(int(r["otel_present"]) for r in rows)!=2:
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=otel_missing local_artifact_preserved=yes")
    STATUS.write_text(json.dumps({"status":"PASS","model":MODEL,"otel":"yes","calls":2,"corpus_used":False,"reused_existing":True,"normalization":parsed.get("normalization"),"contract_violation":contract_violation},indent=2)+"\n")
    report_pass(0,parsed.get("normalization"),contract_violation); return True


def main():
    if STATUS.exists():
        try: status=json.loads(STATUS.read_text())
        except Exception: raise SystemExit("E011-PREFLIGHT status=FAIL reason=status_invalid") from None
        if status.get("status")=="PASS" and status.get("model")==MODEL and status.get("otel")=="yes":
            report_pass(0,status.get("normalization"),status.get("contract_violation")); return

    RUN.mkdir(parents=True, exist_ok=True)
    build_dir=RUN/"compiler"; answer_dir=RUN/"answer"
    if build_dir.exists() or answer_dir.exists():
        if build_dir.exists() and answer_dir.exists() and accept_existing(build_dir,answer_dir): return
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=incomplete_artifact local_artifact_preserved=yes")

    build=inst.call(core.compiler_prompt(MICRO_DOCS),MODEL,build_dir,"preflight-compiler")
    summary=str(build["response"]).strip()
    if not summary:
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=empty_compiler local_artifact_preserved=yes")

    context="### COMPILED TOPIC NOTE\n"+summary
    answer=inst.call(core.answer_prompt(QUESTION,context),MODEL,answer_dir,"preflight-answer")
    parsed, contract_violation = parse_preflight_payload(str(answer["response"]),context)
    if not parsed["valid"]:
        raise SystemExit(f"E011-PREFLIGHT status=FAIL reason=answer_contract_{parsed.get('violation')} local_artifact_preserved=yes")

    rows=[inst.collect_call(build_dir),inst.collect_call(answer_dir)]
    if sum(int(r["otel_present"]) for r in rows)!=2:
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=otel_missing local_artifact_preserved=yes")

    STATUS.write_text(json.dumps({"status":"PASS","model":MODEL,"otel":"yes","calls":2,"corpus_used":False,"reused_existing":False,"normalization":parsed.get("normalization"),"contract_violation":contract_violation},indent=2)+"\n")
    report_pass(2,parsed.get("normalization"),contract_violation)


if __name__=="__main__": main()
