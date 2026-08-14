#!/usr/bin/env python3
"""Reparse existing E011 Stage 1A responses under post-score transport amendment A3.

No model calls. Never overwrites original response.txt, parsed.json, telemetry, or logical results.
"""

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
MODEL = "gpt-5.6-luna"
ANSWER_SEED = 20260815
CONDS = ("R0", "R1", "C0", "C1")
SCALES = ("small", "large")


def h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def tasks(queries):
    rows = [(s, q["query_id"], c) for s in SCALES for q in queries for c in CONDS]
    random.Random(ANSWER_SEED).shuffle(rows)
    return rows


def summaries():
    out = {}
    root = RUN / "build"
    for d in sorted(root.iterdir()):
        parts = d.name.split("-", 2)
        if len(parts) != 3:
            continue
        _, scale, topic = parts
        p = d / "summary.md"
        if p.exists():
            out[(scale, topic)] = p.read_text(encoding="utf-8")
    if len(out) != 24:
        raise SystemExit(f"E011-A3 incomplete_builds got={len(out)} expected=24")
    return out


def answer_dirs():
    out = {}
    root = RUN / "answers"
    for d in sorted(root.iterdir()):
        if not d.is_dir() or "-" not in d.name:
            continue
        suffix = d.name.split("-", 1)[1]
        if suffix in out:
            raise SystemExit("E011-A3 duplicate_prompt_prefix")
        out[suffix] = d
    return out


def decode_a3(text):
    s = text.strip()
    first, last = s.find("{"), s.rfind("}")
    if first < 0 or last <= first or s[last + 1:].strip():
        return None, "transport_residual"
    candidate = s[first:last + 1]
    try:
        return json.loads(candidate), "strict_inner"
    except json.JSONDecodeError as e:
        if not e.msg.startswith("Invalid control character"):
            return None, "transport_residual"
    try:
        return json.loads(candidate, strict=False), "control_char_strict_false"
    except json.JSONDecodeError:
        return None, "transport_residual"


def invalid(mode):
    return {"valid":False,"answer":"","source_ids":[],"uncertainty":None,
            "violation":"json","normalization":None,"transport_mode":mode}


def parse_existing(text, context):
    obj, mode = decode_a3(text)
    if obj is None:
        return invalid(mode)
    canonical = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    parsed = core.parse_answer(canonical, context)
    parsed = dict(parsed)
    parsed["transport_mode"] = mode
    return parsed


def main():
    docs, queries = corpus.generate()
    qmap = {q["query_id"]: q for q in queries}
    sums = summaries()
    dirs = answer_dirs()
    cache = {}
    call_dir = {}
    transport = Counter()
    rows = []

    for scale, qid, cond in tasks(queries):
        q = qmap[qid]
        ctx, rawn = core.context_for(cond, q, scale, docs, sums[(scale, q["topic_id"])])
        prompt = core.answer_prompt(q["question"], ctx)
        ph = h(prompt)
        if ph not in cache:
            key = ph[:12]
            d = dirs.get(key)
            if d is None or not (d / "response.txt").exists():
                raise SystemExit(f"E011-A3 missing_response prompt={key}")
            parsed = parse_existing((d / "response.txt").read_text(encoding="utf-8", errors="replace"), ctx)
            (d / "parsed.transport-a3.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            cache[ph] = parsed
            call_dir[ph] = d
            transport[parsed["transport_mode"]] += 1

        score = core.score(q, cache[ph])
        rows.append({"scale":scale,"topic_id":q["topic_id"],"query_id":qid,"query_class":q["class"],
                     "condition":cond,"prompt_hash":ph,
                     "call_dir":str(call_dir[ph].relative_to(RUN)),"raw_docs_exposed":rawn,
                     "score":score,"transport_mode":cache[ph]["transport_mode"]})

    if len(cache) != 252 or len(rows) != 288:
        raise SystemExit(f"E011-A3 count_mismatch actual={len(cache)} logical={len(rows)}")

    out = RUN / "logical-results.transport-a3.local.json"
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    by = defaultdict(list)
    for r in rows:
        by[r["condition"]].append(r)

    print("E011-STAGE1A-A3-SAFE-HANDOFF-v0")
    print("mode=read-only-reparse modelCalls=0 originalResponses=252 originalArtifacts=unchanged")
    print("transport " + " ".join(f"{k}={transport[k]}" for k in ("strict_inner","control_char_strict_false","transport_residual")))
    for cond in CONDS:
        c = Counter()
        for r in by[cond]:
            s = r["score"]
            c["strict"] += int(s["strict_pass"])
            c["hit"] += s["signal_hits"]; c["total"] += s["signal_total"]
            c["sh"] += s["source_hits"]; c["st"] += s["source_total"]
            c["invalid"] += int(not s["valid"])
        print(f"{cond} strict={c['strict']}/{len(by[cond])} signals={c['hit']}/{c['total']} prov={c['sh']}/{c['st']} invalid={c['invalid']}")
    print("amendment=A3 priorParserPrecedent=E009A rerun=none freeform=none paths=none")


if __name__ == "__main__":
    main()
