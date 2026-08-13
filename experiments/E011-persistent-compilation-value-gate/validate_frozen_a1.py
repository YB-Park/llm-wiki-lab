#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
import generate_corpus as corpus
import json_transport

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
LOCK=ROOT/"fixture-lock-v0.json"
LOCK_SHA="ee363d5850cae8f6a3b4635f4aab34cf91c814ff"
DOCS_SHA="356ee876645e306a1a875211f2a2e9a3831d46ec11c75323d51f56e4427ed48d"
QUERIES_SHA="41fd6241483207f02a83a954d788d54ad60e98dc90dc6a7591d39457bcf99c71"

def blob(p): return subprocess.check_output(["git","hash-object",p],cwd=REPO,text=True).strip()

def main():
    assert blob(str(LOCK.relative_to(REPO)))==LOCK_SHA
    lock=json.loads(LOCK.read_text())
    assert lock["scored_results_observed_at_lock"] is False
    for p,h in lock["files"].items(): assert blob(p)==h,(p,blob(p),h)
    plain='{"answer":"ok","source_ids":[],"uncertainty":"none"}'; f=chr(96)*3
    assert json_transport.loads(plain)[1] is None
    assert json_transport.loads(f+"json\n"+plain+"\n"+f)[1]=="outer_json_fence"
    try: json_transport.loads("comment\n"+plain)
    except json.JSONDecodeError: pass
    else: raise AssertionError("prose extraction forbidden")
    docs,queries=corpus.generate()
    d=corpus.sha256_bytes(corpus.jsonl_bytes(docs)); q=corpus.sha256_bytes((json.dumps(queries,indent=2,sort_keys=True)+"\n").encode())
    assert len(docs)==384 and len(queries)==36 and d==DOCS_SHA and q==QUERIES_SHA
    print(f"fixtureLock=PASS files={len(lock['files'])} manifest={LOCK_SHA[:12]}")
    print("jsonEnvelope=PASS strict=yes outerFence=yes proseExtraction=no")
    print(f"docsSha={d}")
    print(f"queriesSha={q}")
    print("status=PASS modelCalls=0 frozen=yes amendment=A1")

if __name__=="__main__": main()
