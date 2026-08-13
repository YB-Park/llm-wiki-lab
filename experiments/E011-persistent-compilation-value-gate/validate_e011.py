#!/usr/bin/env python3
"""Validate E011 fixtures and raw-retrieval diagnostics before scored calls."""

from __future__ import annotations

import json
from collections import defaultdict

import generate_corpus as corpus
import lexical


def topic_docs(docs: list[dict], topic_id: str, scale: str) -> list[dict]:
    return [
        d for d in docs
        if d["topic_id"] == topic_id and (scale == "large" or d["min_scale"] == "small")
    ]


def signal_coverage(query: dict, docs: list[dict]) -> float:
    text = "\n".join(d["title"] + "\n" + d["text"] for d in docs).lower()
    required = query["required_signals"]
    return sum(signal in text for signal in required) / len(required)


def main() -> None:
    docs, queries = corpus.generate()
    assert len(docs) == 384
    assert len(queries) == 36
    assert len({d["source_id"] for d in docs}) == 384
    assert len({q["query_id"] for q in queries}) == 36
    assert {q["class"] for q in queries} == {"exact_provenance", "global_synthesis", "decision_rationale"}

    topics = sorted({d["topic_id"] for d in docs})
    assert len(topics) == 12
    query_by_topic = defaultdict(list)
    for q in queries:
        query_by_topic[q["topic_id"]].append(q)

    for topic in topics:
        small = topic_docs(docs, topic, "small")
        large = topic_docs(docs, topic, "large")
        assert len(small) == 8
        assert len(large) == 32
        assert {d["source_id"] for d in small} <= {d["source_id"] for d in large}
        assert len(query_by_topic[topic]) == 3
        small_text = "\n".join(d["text"] for d in small).lower()
        for q in query_by_topic[topic]:
            assert all(signal in small_text for signal in q["required_signals"]), (topic, q["query_id"])
            assert all(source_id in {d["source_id"] for d in small} for source_id in q["required_source_ids"])

    print("E011-PRESCORE-VALIDATION-v0")
    print(f"topics={len(topics)} docs={len(docs)} smallDocs={sum(d['min_scale']=='small' for d in docs)} queries={len(queries)} topK={lexical.TOP_K}")

    for scale in ("small", "large"):
        by_class = defaultdict(list)
        strict = defaultdict(int)
        exact_source = 0
        for q in queries:
            scoped = topic_docs(docs, q["topic_id"], scale)
            retrieved = lexical.top_k(q["question"], scoped)
            cov = signal_coverage(q, retrieved)
            by_class[q["class"]].append(cov)
            strict[q["class"]] += int(cov == 1.0)
            if q["class"] == "exact_provenance":
                exact_source += int(set(q["required_source_ids"]) <= {d["source_id"] for d in retrieved})
        bits = []
        for cls in ("exact_provenance", "global_synthesis", "decision_rationale"):
            values = by_class[cls]
            mean = sum(values) / len(values)
            bits.append(f"{cls}:signalMean={mean:.3f},strict={strict[cls]}/{len(values)}")
        print(f"retrieval scale={scale} " + " ".join(bits) + f" exactSource={exact_source}/12")

    docs_data = corpus.jsonl_bytes(docs)
    queries_data = (json.dumps(queries, indent=2, sort_keys=True) + "\n").encode("utf-8")
    print(f"docsSha={corpus.sha256_bytes(docs_data)}")
    print(f"queriesSha={corpus.sha256_bytes(queries_data)}")
    print("status=PASS modelCalls=0")


if __name__ == "__main__":
    main()
