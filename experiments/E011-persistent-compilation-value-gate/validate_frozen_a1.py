#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
import generate_corpus as corpus
import preflight

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
LOCK=ROOT/"fixture-lock-v0.json"
LOCK_SHA="30cedc7e32b530de7c9ca52ee820fc0c9d670b67"

def blob(p): return subprocess.check_output(["git","hash-object",p],cwd=REPO,text=True).strip()

def main():
    assert blob(str(LOCK.relative_to(REPO)))==LOCK_SHA
    lock=json.loads(LOCK.read_text())
    assert lock["scored_results_observed_at_lock"] is False
    for p,h in lock["files"].items(): assert blob(p)==h,(p,blob(p),h)
    ctx='### SOURCE T99-S01\nsynthetic evidence'
    payload='{"answer":"ok","source_ids":["T99-S01"],"uncertainty":"none"}'
    recovered,v=preflight.parse_preflight_payload("leading note\n"+payload,ctx)
    assert recovered["valid"] and recovered["normalization"]=="preflight_leading_prefix_payload" and v=="prefix_noise"
    rejected,v=preflight.parse_preflight_payload("leading note\n"+payload+"\ntrailing note",ctx)
    assert not rejected["valid"] and rejected["violation"]=="json" and v is None
    docs,queries=corpus.generate()
    assert len(docs)==384 and len(queries)==36
    print(f"fixtureLock=PASS files={len(lock['files'])} manifest={LOCK_SHA[:12]}")
    print("preflightPrefix=PASS leading=yes trailing=no scoredParser=unchanged")
    print("status=PASS modelCalls=0 frozen=yes amendment=A2")

if __name__=="__main__": main()
