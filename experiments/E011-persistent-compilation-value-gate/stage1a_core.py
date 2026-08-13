#!/usr/bin/env python3
"""Pure semantic/context helpers for E011 Stage 1A."""

import json
from pathlib import Path
import lexical

ROOT = Path(__file__).resolve().parent
VALID_UNCERTAINTY = {"none", "partial", "unknown"}


def topic_docs(docs, topic_id, scale):
    return sorted([d for d in docs if d["topic_id"] == topic_id and (scale == "large" or d["min_scale"] == "small")], key=lambda d: d["source_id"])


def raw_context(docs):
    return "\n\n".join(f"### SOURCE {d['source_id']} — {d['title']}\n{d['text']}" for d in sorted(docs, key=lambda d: d["source_id"]))


def compiler_prompt(docs):
    text = (ROOT / "compiler-prompt.md").read_text(encoding="utf-8").replace("{{SOURCES}}", raw_context(docs))
    if "{{" in text: raise ValueError("compiler placeholder")
    return text


def answer_prompt(question, context):
    text = (ROOT / "answer-prompt.md").read_text(encoding="utf-8").replace("{{QUESTION}}", question).replace("{{CONTEXT}}", context)
    if "{{" in text: raise ValueError("answer placeholder")
    return text


def context_for(condition, query, scale, docs, summary):
    scoped = topic_docs(docs, query["topic_id"], scale)
    retrieved = sorted(lexical.top_k(query["question"], scoped), key=lambda d: d["source_id"])
    if condition == "R0": return raw_context(retrieved), len(retrieved)
    if condition == "R1": return raw_context(scoped), len(scoped)
    if condition == "C0": return "### COMPILED TOPIC NOTE\n" + summary, 0
    if condition == "C1": return "### COMPILED TOPIC NOTE\n" + summary + "\n\n### RAW EVIDENCE\n" + raw_context(retrieved), len(retrieved)
    raise ValueError(condition)


def parse_answer(text):
    try: obj = json.loads(text.strip())
    except Exception: return {"valid":False,"answer":"","source_ids":[],"uncertainty":None}
    ok = isinstance(obj, dict) and isinstance(obj.get("answer"), str) and bool(obj.get("answer", "").strip()) and isinstance(obj.get("source_ids"), list) and all(isinstance(x, str) and x for x in obj.get("source_ids", [])) and obj.get("uncertainty") in VALID_UNCERTAINTY
    return {"valid":bool(ok),"answer":obj.get("answer","") if isinstance(obj,dict) else "","source_ids":obj.get("source_ids",[]) if isinstance(obj,dict) and isinstance(obj.get("source_ids"),list) else [],"uncertainty":obj.get("uncertainty") if isinstance(obj,dict) else None}


def score(query, parsed):
    answer = parsed["answer"].lower() if parsed["valid"] else ""
    hits = sum(s.lower() in answer for s in query["required_signals"])
    req = set(query["required_source_ids"]); got = set(parsed["source_ids"])
    src_hits = len(req & got)
    strict = parsed["valid"] and hits == len(query["required_signals"]) and req <= got
    return {"valid":parsed["valid"],"signal_hits":hits,"signal_total":len(query["required_signals"]),"source_hits":src_hits,"source_total":len(req),"strict_pass":bool(strict),"uncertainty":parsed["uncertainty"]}
