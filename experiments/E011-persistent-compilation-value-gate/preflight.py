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


def report_pass():
    print("E011-PREFLIGHT-v0")
    print(f"status=PASS model={MODEL} calls=2 otel=2/2 contracts=compiler_nonempty,answer_json,visible_source_ids")
    print("corpus=NOT_USED quality_result=NONE")


def main():
    if STATUS.exists():
        try: status=json.loads(STATUS.read_text())
        except Exception: raise SystemExit("E011-PREFLIGHT status=FAIL reason=status_invalid") from None
        if status.get("status")=="PASS" and status.get("model")==MODEL and status.get("otel")=="yes":
            report_pass(); return

    RUN.mkdir(parents=True, exist_ok=True)
    build_dir=RUN/"compiler"; answer_dir=RUN/"answer"
    if build_dir.exists() or answer_dir.exists():
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=incomplete_artifact local_artifact_preserved=yes")

    build=inst.call(core.compiler_prompt(MICRO_DOCS),MODEL,build_dir,"preflight-compiler")
    summary=str(build["response"]).strip()
    if not summary:
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=empty_compiler local_artifact_preserved=yes")

    context="### COMPILED TOPIC NOTE\n"+summary
    answer=inst.call(core.answer_prompt(QUESTION,context),MODEL,answer_dir,"preflight-answer")
    parsed=core.parse_answer(str(answer["response"]),context)
    if not parsed["valid"]:
        raise SystemExit(f"E011-PREFLIGHT status=FAIL reason=answer_contract_{parsed.get('violation')} local_artifact_preserved=yes")

    rows=[inst.collect_call(build_dir),inst.collect_call(answer_dir)]
    if sum(int(r["otel_present"]) for r in rows)!=2:
        raise SystemExit("E011-PREFLIGHT status=FAIL reason=otel_missing local_artifact_preserved=yes")

    STATUS.write_text(json.dumps({"status":"PASS","model":MODEL,"otel":"yes","calls":2,"corpus_used":False},indent=2)+"\n")
    report_pass()


if __name__=="__main__": main()
