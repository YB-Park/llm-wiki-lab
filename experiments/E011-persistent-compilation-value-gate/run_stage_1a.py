#!/usr/bin/env python3
"""Run frozen E011 Stage 1A value-gate conditions."""

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import generate_corpus as corpus
import instrumentation as inst
import stage1a_core as core

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "stage-1a-v0"
PREFLIGHT = ROOT / "runs" / "preflight-v0" / "status.json"
MODEL = "gpt-5.6-luna"
DOCS_SHA = "356ee876645e306a1a875211f2a2e9a3831d46ec11c75323d51f56e4427ed48d"
QUERIES_SHA = "41fd6241483207f02a83a954d788d54ad60e98dc90dc6a7591d39457bcf99c71"
BUILD_SEED = 20260814
ANSWER_SEED = 20260815
CONDS = ("R0", "R1", "C0", "C1")
SCALES = ("small", "large")


def h(text): return hashlib.sha256(text.encode()).hexdigest()


def fingerprints(docs, queries):
    d = corpus.sha256_bytes(corpus.jsonl_bytes(docs))
    q = corpus.sha256_bytes((json.dumps(queries, indent=2, sort_keys=True) + "\n").encode())
    return d, q


def require_preflight():
    if not PREFLIGHT.exists(): raise SystemExit("E011-STOP preflight_required run=preflight.py")
    try: s = json.loads(PREFLIGHT.read_text())
    except Exception: raise SystemExit("E011-STOP preflight_status_invalid") from None
    if s.get("status") != "PASS" or s.get("model") != MODEL or s.get("otel") != "yes":
        raise SystemExit("E011-STOP preflight_not_passed")


def fixture_lock(dsha, qsha):
    f = {"model":MODEL,"docs":dsha,"queries":qsha,"compiler":h((ROOT/"compiler-prompt.md").read_text()),
         "answer":h((ROOT/"answer-prompt.md").read_text()),"core":h((ROOT/"stage1a_core.py").read_text()),
         "json_transport":h((ROOT/"json_transport.py").read_text()),"lexical":h((ROOT/"lexical.py").read_text()),
         "build_seed":BUILD_SEED,"answer_seed":ANSWER_SEED}
    RUN.mkdir(parents=True, exist_ok=True); p = RUN / "fixture.json"
    if p.exists() and json.loads(p.read_text()) != f: raise SystemExit("E011-STOP fixture_mismatch")
    if not p.exists(): p.write_text(json.dumps(f, indent=2) + "\n")


def build_all(docs, topics):
    keys = [(s,t) for s in SCALES for t in topics]; random.Random(BUILD_SEED).shuffle(keys); out = {}
    for seq,(scale,topic) in enumerate(keys,1):
        d = RUN/"build"/f"{seq:03d}-{scale}-{topic}"; p = d/"summary.md"
        if p.exists(): out[(scale,topic)] = p.read_text(); print(f"BUILD-SKIP seq={seq}"); continue
        if d.exists(): raise SystemExit(f"E011-STOP incomplete_build synthetic_call={seq:03d}-{scale}-{topic} local_artifact_preserved=yes")
        r = inst.call(core.compiler_prompt(core.topic_docs(docs,topic,scale)), MODEL, d, f"build-{seq:03d}-{scale}-{topic}")
        text = str(r["response"]).strip()
        if not text: raise SystemExit(f"E011-STOP empty_compilation synthetic_call={seq:03d}-{scale}-{topic}")
        p.write_text(text + "\n"); out[(scale,topic)] = text + "\n"; print(f"BUILD-DONE seq={seq}")
    return out


def tasks(queries):
    rows = [(s,q["query_id"],c) for s in SCALES for q in queries for c in CONDS]
    random.Random(ANSWER_SEED).shuffle(rows); return rows


def run_answers(docs, queries, summaries):
    qmap = {q["query_id"]:q for q in queries}; cache={}; dirs={}; results=[]; seq=0
    for scale,qid,cond in tasks(queries):
        q=qmap[qid]; ctx,rawn=core.context_for(cond,q,scale,docs,summaries[(scale,q["topic_id"])])
        prompt=core.answer_prompt(q["question"],ctx); ph=h(prompt)
        if ph not in cache:
            seq += 1; d=RUN/"answers"/f"{seq:03d}-{ph[:12]}"; p=d/"parsed.json"
            if p.exists(): parsed=json.loads(p.read_text()); print(f"ANSWER-SKIP seq={seq}")
            elif d.exists(): raise SystemExit(f"E011-STOP incomplete_answer synthetic_call={seq:03d}-{ph[:12]} local_artifact_preserved=yes")
            else:
                r=inst.call(prompt,MODEL,d,f"answer-{seq:03d}-{ph[:12]}"); parsed=core.parse_answer(str(r["response"]),ctx); p.write_text(json.dumps(parsed,indent=2)+"\n")
                print(f"ANSWER-DONE seq={seq} contract={'valid' if parsed['valid'] else 'invalid'}")
            cache[ph]=parsed; dirs[ph]=d
        score=core.score(q,cache[ph])
        results.append({"scale":scale,"topic_id":q["topic_id"],"query_id":qid,"query_class":q["class"],"condition":cond,
                        "prompt_hash":ph,"call_dir":str(dirs[ph].relative_to(RUN)),"raw_docs_exposed":rawn,"score":score})
    (RUN/"logical-results.local.json").write_text(json.dumps(results,indent=2)+"\n")
    return results


def summarize(results):
    by=defaultdict(list)
    for r in results: by[r["condition"]].append(r)
    build_dirs=sorted((RUN/"build").iterdir()); bm=inst.aggregate(build_dirs); state=sum((d/"summary.md").stat().st_size for d in build_dirs)
    lines=["E011-STAGE1A-SAFE-HANDOFF-v0",
           f"logicalAnswers={len(results)} actualAnswerCalls={len({r['prompt_hash'] for r in results})} buildCalls={bm['call_count']} model={MODEL}",
           f"build in={int(bm['input_tokens'])} out={int(bm['output_tokens'])} wall={bm['wall_seconds']} stateBytes={state}"]
    for cond in CONDS:
        c=Counter(); tin=tout=wall=0.0; raw=0
        for r in by[cond]:
            s=r["score"]; c["strict"]+=int(s["strict_pass"]); c["hit"]+=s["signal_hits"]; c["total"]+=s["signal_total"]
            c["sh"]+=s["source_hits"]; c["st"]+=s["source_total"]; c["invalid"]+=int(not s["valid"]); raw+=r["raw_docs_exposed"]
            m=inst.collect_call(RUN/r["call_dir"]); tin+=m["input_tokens"]; tout+=m["output_tokens"]; wall+=m["wall_seconds"]
        lines.append(f"{cond} strict={c['strict']}/{len(by[cond])} signals={c['hit']}/{c['total']} prov={c['sh']}/{c['st']} invalid={c['invalid']} queryIn={int(tin)} queryOut={int(tout)} queryWall={wall:.3f} rawDocs={raw}")
    lines.append("reuse=N1,N3,N10 postscore=required freeform=none paths=none")
    return "\n".join(lines)+"\n"


def main():
    require_preflight(); docs,queries=corpus.generate(); dsha,qsha=fingerprints(docs,queries)
    if dsha!=DOCS_SHA or qsha!=QUERIES_SHA: raise SystemExit("E011-STOP corpus_fingerprint_mismatch")
    fixture_lock(dsha,qsha); summaries=build_all(docs,sorted({d["topic_id"] for d in docs})); results=run_answers(docs,queries,summaries)
    text=summarize(results); (RUN/"safe-handoff.txt").write_text(text); print(text,end="")


if __name__ == "__main__": main()
