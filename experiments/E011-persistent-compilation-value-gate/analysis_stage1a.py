#!/usr/bin/env python3
"""Read-only post-score analysis for frozen E011 Stage 1A."""

import json
import math
import random
from collections import defaultdict
from pathlib import Path

import generate_corpus as corpus
import instrumentation as inst
import stage1a_core as core

ROOT=Path(__file__).resolve().parent
RUN=ROOT/"runs"/"stage-1a-v0"
RESULTS=RUN/"logical-results.local.json"
CONDS=("R0","R1","C0","C1")
SCALES=("small","large")
REUSE=(1,3,10)
BOOT_SEED=20260816
BOOT_N=20000


def rate(n,d): return n/d if d else 1.0

def quality(rows):
    strict=sum(int(r["score"]["strict_pass"]) for r in rows)
    sh=sum(r["score"]["signal_hits"] for r in rows); st=sum(r["score"]["signal_total"] for r in rows)
    ph=sum(r["score"]["source_hits"] for r in rows); pt=sum(r["score"]["source_total"] for r in rows)
    invalid=sum(int(not r["score"]["valid"]) for r in rows)
    return {"strict":strict,"n":len(rows),"signal_hits":sh,"signal_total":st,"prov_hits":ph,"prov_total":pt,"invalid":invalid,
            "strict_rate":rate(strict,len(rows)),"signal_rate":rate(sh,st),"prov_rate":rate(ph,pt)}


def query_tokens(row):
    m=inst.collect_call(RUN/row["call_dir"])
    return m["input_tokens"]+m["output_tokens"]


def build_map():
    out={}
    for d in sorted((RUN/"build").iterdir()):
        _,scale,topic=d.name.split("-",2)
        m=inst.collect_call(d); summary=(d/"summary.md").read_text(encoding="utf-8")
        out[(scale,topic)]={"tokens":m["input_tokens"]+m["output_tokens"],"input":m["input_tokens"],"output":m["output_tokens"],"summary":summary,"bytes":len(summary.encode())}
    if len(out)!=24: raise SystemExit("E011-ANALYSIS incomplete_builds")
    return out


def topic_values(rows, metric):
    by=defaultdict(list)
    for r in rows: by[r["topic_id"]].append(r)
    return {topic:quality(rs)[metric] for topic,rs in by.items()}


def paired_boot(a,b):
    keys=sorted(a); diffs=[a[k]-b[k] for k in keys]; obs=sum(diffs)/len(diffs)
    rng=random.Random(BOOT_SEED); draws=[]
    for _ in range(BOOT_N): draws.append(sum(rng.choice(diffs) for _ in diffs)/len(diffs))
    draws.sort(); lo=draws[int(.025*(len(draws)-1))]; hi=draws[int(.975*(len(draws)-1))]
    return obs,lo,hi


def break_even(build,raw_q,comp_q):
    saving=raw_q-comp_q
    return None if saving<=0 else max(1,math.ceil(build/saving))


def dominates(a,b):
    quality_ok=a["strict_rate"]>=b["strict_rate"] and a["signal_rate"]>=b["signal_rate"] and a["prov_rate"]>=b["prov_rate"]
    cost_ok=a["tokens"]<=b["tokens"]
    strict=(a["strict_rate"]>b["strict_rate"] or a["signal_rate"]>b["signal_rate"] or a["prov_rate"]>b["prov_rate"] or a["tokens"]<b["tokens"])
    return quality_ok and cost_ok and strict


def main():
    if not RESULTS.exists(): raise SystemExit("E011-ANALYSIS scored_results_missing")
    rows=json.loads(RESULTS.read_text()); docs,queries=corpus.generate(); builds=build_map()
    if len(rows)!=288: raise SystemExit(f"E011-ANALYSIS expected_288_rows got_{len(rows)}")
    bycond={c:[r for r in rows if r["condition"]==c] for c in CONDS}
    if any(len(v)!=72 for v in bycond.values()): raise SystemExit("E011-ANALYSIS condition_count_mismatch")

    print("E011-STAGE1A-ANALYSIS-HANDOFF-v0")
    print("mode=read-only modelCalls=0 unit=topic bootstrap=12topics freeform=none paths=none")

    qby=defaultdict(list)
    for q in queries: qby[q["topic_id"]].append(q)
    for scale in SCALES:
        sig_hit=sig_total=prov_hit=prov_total=state=rawb=0
        for topic in sorted(qby):
            summary=builds[(scale,topic)]["summary"].lower(); state+=builds[(scale,topic)]["bytes"]
            raw=core.raw_context(core.topic_docs(docs,topic,scale)); rawb+=len(raw.encode())
            for q in qby[topic]:
                sig_hit+=sum(s.lower() in summary for s in q["required_signals"]); sig_total+=len(q["required_signals"])
                prov_hit+=sum(s.lower() in summary for s in q["required_source_ids"]); prov_total+=len(q["required_source_ids"])
        print(f"compiledState scale={scale} signals={sig_hit}/{sig_total} prov={prov_hit}/{prov_total} bytes={state} rawBytes={rawb} ratio={state/rawb:.3f}")

    qcost={}; rawdocs={}; qmetrics={}
    for c in CONDS:
        q=quality(bycond[c]); qmetrics[c]=q; qcost[c]=sum(query_tokens(r) for r in bycond[c]); rawdocs[c]=sum(r["raw_docs_exposed"] for r in bycond[c])
        print(f"{c} strict={q['strict']}/{q['n']} signals={q['signal_hits']}/{q['signal_total']} prov={q['prov_hits']}/{q['prov_total']} invalid={q['invalid']} queryTokens={int(qcost[c])} rawDocs={rawdocs[c]}")
        for scale in SCALES:
            qs=quality([r for r in bycond[c] if r["scale"]==scale])
            print(f"{c} scale={scale} strict={qs['strict']}/{qs['n']} signals={qs['signal_hits']}/{qs['signal_total']} prov={qs['prov_hits']}/{qs['prov_total']} invalid={qs['invalid']}")

    for left,right in (("C0","R1"),("C1","R0")):
        bits=[]
        for metric in ("strict_rate","signal_rate","prov_rate"):
            obs,lo,hi=paired_boot(topic_values(bycond[left],metric),topic_values(bycond[right],metric))
            bits.append(f"{metric}={obs:+.3f}[{lo:+.3f},{hi:+.3f}]")
        print(f"paired {left}-{right} "+" ".join(bits))

    build_total=sum(v["tokens"] for v in builds.values())
    for comp,raw in (("C0","R1"),("C1","R0")):
        bes=[]; none=0
        for scale in SCALES:
            for topic in sorted(qby):
                cq=sum(query_tokens(r) for r in bycond[comp] if r["scale"]==scale and r["topic_id"]==topic)
                rq=sum(query_tokens(r) for r in bycond[raw] if r["scale"]==scale and r["topic_id"]==topic)
                be=break_even(builds[(scale,topic)]["tokens"],rq,cq)
                if be is None: none+=1
                else: bes.append(be)
        agg=break_even(build_total,qcost[raw],qcost[comp])
        if bes:
            s=sorted(bes); med=(s[(len(s)-1)//2]+s[len(s)//2])/2; detail=f"median={med:g} min={min(s)} max={max(s)}"
        else: detail="median=none min=none max=none"
        print(f"breakEven {comp}vs{raw} aggregate={agg if agg is not None else 'none'} topicScaleFinite={len(bes)}/24 none={none} {detail}")

    for n in REUSE:
        points={}
        for c in CONDS:
            build=build_total if c in {"C0","C1"} else 0
            points[c]={**qmetrics[c],"tokens":build+n*qcost[c]}
        frontier=[c for c in CONDS if not any(other!=c and dominates(points[other],points[c]) for other in CONDS)]
        costs=" ".join(f"{c}:{int(points[c]['tokens'])}" for c in CONDS)
        print(f"reuse N={n} lifecycleTokens={costs} frontier={','.join(frontier)}")

    for cls in ("exact_provenance","global_synthesis","decision_rationale"):
        bits=[]
        for c in CONDS:
            q=quality([r for r in bycond[c] if r["query_class"]==cls]); bits.append(f"{c}:{q['strict']}/{q['n']}")
        print(f"class={cls} "+" ".join(bits))

    print("caution=synthetic12;authorGroundTruth;sameModelBuildAnswer;topicRoutingOracle;staticOnly;tokenProxyNotHumanUtility")


if __name__=="__main__": main()
