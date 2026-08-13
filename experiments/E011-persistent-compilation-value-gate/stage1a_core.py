#!/usr/bin/env python3
"""Pure semantic/context helpers for E011 Stage 1A."""

import json
import re
from pathlib import Path
import lexical

ROOT = Path(__file__).resolve().parent
VALID_UNCERTAINTY = {"none", "partial", "unknown"}
SOURCE_ID_RE = re.compile(r"\bT\d{2}-S\d{2}\b")


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


def parse_answer(text, context, allowed_source_ids=None):
    try: obj = json.loads(text.strip())
    except Exception: return {"valid":False,"answer":"","source_ids":[],"uncertainty":None,"violation":"json"}
    if not isinstance(obj, dict): return {"valid":False,"answer":"","source_ids":[],"uncertainty":None,"violation":"object"}
    answer=obj.get("answer"); ids=obj.get("source_ids"); uncertainty=obj.get("uncertainty")
    shape_ok=isinstance(answer,str) and bool(answer.strip()) and isinstance(ids,list) and all(isinstance(x,str) and x for x in ids) and uncertainty in VALID_UNCERTAINTY
    visible=set(SOURCE_ID_RE.findall(context)); allowed=visible if allowed_source_ids is None else visible & set(allowed_source_ids)
    provenance_ok=isinstance(ids,list) and set(ids) <= allowed
    valid=bool(shape_ok and provenance_ok)
    violation=None if valid else ("source_visibility_or_existence" if shape_ok and not provenance_ok else "schema")
    return {"valid":valid,"answer":answer if isinstance(answer,str) else "","source_ids":ids if isinstance(ids,list) else [],"uncertainty":uncertainty,"violation":violation}


def score(query, parsed):
    answer = parsed["answer"].lower() if parsed["valid"] else ""
    hits = sum(s.lower() in answer for s in query["required_signals"])
    req = set(query["required_source_ids"]); got = set(parsed["source_ids"])
    src_hits = len(req & got)
    strict = parsed["valid"] and hits == len(query["required_signals"]) and req <= got
    return {"valid":parsed["valid"],"signal_hits":hits,"signal_total":len(query["required_signals"]),"source_hits":src_hits,"source_total":len(req),"strict_pass":bool(strict),"uncertainty":parsed["uncertainty"],"violation":parsed.get("violation")}
