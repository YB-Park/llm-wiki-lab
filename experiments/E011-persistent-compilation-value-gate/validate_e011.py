#!/usr/bin/env python3
"""Validate E011 frozen fixtures and raw-retrieval diagnostics before scored calls."""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from pathlib import Path

import generate_corpus as corpus
import lexical

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
LOCK=ROOT/"fixture-lock-v0.json"
EXPECTED_LOCK_BLOB="32ed6136b1daee6bb20f65c8e6c766df853dfe68"
EXPECTED_DOCS_SHA="356ee876645e306a1a875211f2a2e9a3831d46ec11c75323d51f56e4427ed48d"
EXPECTED_QUERIES_SHA="41fd6241483207f02a83a954d788d54ad60e98dc90dc6a7591d39457bcf99c71"


def git_blob(path: str) -> str:
    return subprocess.check_output(["git","hash-object",path],cwd=REPO,text=True).strip()


def verify_fixture_lock() -> None:
    rel=str(LOCK.relative_to(REPO))
    actual=git_blob(rel)
    assert actual==EXPECTED_LOCK_BLOB,(actual,EXPECTED_LOCK_BLOB)
    data=json.loads(LOCK.read_text(encoding="utf-8"))
    assert data["scored_results_observed_at_lock"] is False
    for path,expected in data["files"].items():
        actual=git_blob(path)
        assert actual==expected,(path,actual,expected)
    print(f"fixtureLock=PASS files={len(data['files'])} manifest={EXPECTED_LOCK_BLOB[:12]}")


def topic_docs(docs: list[dict], topic_id: str, scale: str) -> list[dict]:
    return [d for d in docs if d["topic_id"]==topic_id and (scale=="large" or d["min_scale"]=="small")]


def signal_coverage(query: dict, docs: list[dict]) -> float:
    text="\n".join(d["title"]+"\n"+d["text"] for d in docs).lower()
    required=query["required_signals"]
    return sum(signal in text for signal in required)/len(required)


def main() -> None:
    verify_fixture_lock()
    docs,queries=corpus.generate()
    assert len(docs)==384 and len(queries)==36
    assert len({d["source_id"] for d in docs})==384
    assert len({q["query_id"] for q in queries})==36
    assert {q["class"] for q in queries}=={"exact_provenance","global_synthesis","decision_rationale"}

    docs_data=corpus.jsonl_bytes(docs)
    queries_data=(json.dumps(queries,indent=2,sort_keys=True)+"\n").encode("utf-8")
    docs_sha=corpus.sha256_bytes(docs_data); queries_sha=corpus.sha256_bytes(queries_data)
    assert docs_sha==EXPECTED_DOCS_SHA,(docs_sha,EXPECTED_DOCS_SHA)
    assert queries_sha==EXPECTED_QUERIES_SHA,(queries_sha,EXPECTED_QUERIES_SHA)

    topics=sorted({d["topic_id"] for d in docs}); assert len(topics)==12
    query_by_topic=defaultdict(list)
    for q in queries: query_by_topic[q["topic_id"]].append(q)

    for topic in topics:
        small=topic_docs(docs,topic,"small"); large=topic_docs(docs,topic,"large")
        assert len(small)==8 and len(large)==32
        assert {d["source_id"] for d in small}<={d["source_id"] for d in large}
        assert len(query_by_topic[topic])==3
        small_text="\n".join(d["text"] for d in small).lower()
        for q in query_by_topic[topic]:
            assert all(signal in small_text for signal in q["required_signals"]),(topic,q["query_id"])
            assert all(source_id in {d["source_id"] for d in small} for source_id in q["required_source_ids"])

    print("E011-PRESCORE-VALIDATION-v0")
    print(f"topics={len(topics)} docs={len(docs)} smallDocs={sum(d['min_scale']=='small' for d in docs)} queries={len(queries)} topK={lexical.TOP_K}")

    for scale in ("small","large"):
        by_class=defaultdict(list); strict=defaultdict(int); exact_source=0
        for q in queries:
            scoped=topic_docs(docs,q["topic_id"],scale); retrieved=lexical.top_k(q["question"],scoped)
            cov=signal_coverage(q,retrieved); by_class[q["class"]].append(cov); strict[q["class"]]+=int(cov==1.0)
            if q["class"]=="exact_provenance": exact_source+=int(set(q["required_source_ids"])<={d["source_id"] for d in retrieved})
        bits=[]
        for cls in ("exact_provenance","global_synthesis","decision_rationale"):
            values=by_class[cls]; bits.append(f"{cls}:signalMean={sum(values)/len(values):.3f},strict={strict[cls]}/{len(values)}")
        print(f"retrieval scale={scale} "+" ".join(bits)+f" exactSource={exact_source}/12")

    print(f"docsSha={docs_sha}")
    print(f"queriesSha={queries_sha}")
    print("status=PASS modelCalls=0 frozen=yes")


if __name__=="__main__": main()
