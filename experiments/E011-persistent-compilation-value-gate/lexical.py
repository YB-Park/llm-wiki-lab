#!/usr/bin/env python3
"""Deterministic topic-scoped BM25 used by E011 R0/C1."""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")
K1 = 1.5
B = 0.75
TOP_K = 12


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def rank(query: str, docs: list[dict]) -> list[dict]:
    if not docs:
        return []
    query_terms = tokenize(query)
    doc_tokens = [tokenize(d["title"] + " " + d["text"]) for d in docs]
    lengths = [len(x) for x in doc_tokens]
    avg_len = sum(lengths) / len(lengths)
    dfs = Counter()
    for tokens in doc_tokens:
        dfs.update(set(tokens))

    scored = []
    n = len(docs)
    for doc, tokens, dl in zip(docs, doc_tokens, lengths):
        tf = Counter(tokens)
        score = 0.0
        for term in query_terms:
            freq = tf.get(term, 0)
            if not freq:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            denom = freq + K1 * (1.0 - B + B * dl / avg_len)
            score += idf * (freq * (K1 + 1.0)) / denom
        scored.append((score, doc["source_id"], doc))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return [row[2] for row in scored]


def top_k(query: str, docs: list[dict]) -> list[dict]:
    return rank(query, docs)[:TOP_K]
