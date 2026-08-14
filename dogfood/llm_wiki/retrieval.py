from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .store import Source, read_text, sources

TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)


@dataclass(frozen=True)
class Hit:
    source: Source
    score: float
    snippet: str


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in TOKEN_RE.finditer(text)]


def _best_snippet(text: str, query_tokens: set[str], max_chars: int) -> str:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        return ""
    ranked = []
    for i, block in enumerate(blocks):
        toks = tokenize(block)
        overlap = sum(1 for t in toks if t in query_tokens)
        ranked.append((-overlap, i, block))
    block = sorted(ranked)[0][2]
    if len(block) <= max_chars:
        return block
    return block[: max_chars - 1].rstrip() + "…"


def search(
    root: Path,
    query: str,
    top_k: int = 8,
    snippet_chars: int = 320,
    *,
    topic_id: str | None = None,
) -> list[Hit]:
    docs = sources(root, topic_id=topic_id)
    if not docs:
        return []
    qtokens = tokenize(query)
    if not qtokens:
        return []

    tokenized = {s.source_id: tokenize(read_text(s)) for s in docs}
    n = len(docs)
    avgdl = sum(len(v) for v in tokenized.values()) / n
    dfs = Counter()
    for toks in tokenized.values():
        for term in set(toks):
            dfs[term] += 1

    k1 = 1.5
    b = 0.75
    hits = []
    qset = set(qtokens)
    for src in docs:
        toks = tokenized[src.source_id]
        tf = Counter(toks)
        dl = len(toks)
        score = 0.0
        for term in qtokens:
            if tf[term] == 0:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            denom = tf[term] + k1 * (1 - b + b * dl / avgdl)
            score += idf * (tf[term] * (k1 + 1)) / denom
        if score > 0:
            hits.append(Hit(src, score, _best_snippet(read_text(src), qset, snippet_chars)))

    hits.sort(key=lambda h: (-h.score, h.source.source_id))
    return hits[: max(0, top_k)]


def render_context(
    root: Path,
    query: str,
    top_k: int = 8,
    max_chars_per_source: int = 1200,
    *,
    topic_id: str | None = None,
) -> str:
    hits = search(root, query, top_k=top_k, snippet_chars=max_chars_per_source, topic_id=topic_id)
    parts = []
    for hit in hits:
        parts.append(
            f"### SOURCE {hit.source.source_id} — {hit.source.name}\n"
            f"sha256: {hit.source.sha256}\n"
            f"bm25: {hit.score:.6f}\n\n"
            f"{hit.snippet}"
        )
    return "\n\n".join(parts)
