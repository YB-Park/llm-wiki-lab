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
    # `source` is a deterministic representative kept for backwards-compatible
    # consumers. `evidence_sources` contains every active evidence record that
    # points to the same immutable content object.
    source: Source
    score: float
    snippet: str
    evidence_sources: tuple[Source, ...]

    @property
    def source_ids(self) -> tuple[str, ...]:
        return tuple(src.source_id for src in self.evidence_sources)

    @property
    def object_id(self) -> str:
        return self.source.object_id


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


def _object_groups(docs: list[Source]) -> dict[str, tuple[Source, ...]]:
    grouped: dict[str, list[Source]] = {}
    for src in docs:
        grouped.setdefault(src.object_id, []).append(src)

    out: dict[str, tuple[Source, ...]] = {}
    for object_id, rows in grouped.items():
        ordered = tuple(sorted(rows, key=lambda src: src.source_id))
        shas = {src.sha256 for src in ordered}
        if len(shas) != 1:
            raise RuntimeError(f"object_identity_collision:{object_id}")
        out[object_id] = ordered
    return out


def search(
    root: Path,
    query: str,
    top_k: int = 8,
    snippet_chars: int = 320,
    *,
    topic_id: str | None = None,
    include_superseded: bool = False,
) -> list[Hit]:
    evidence = sources(root, topic_id=topic_id, include_superseded=include_superseded)
    if not evidence:
        return []
    qtokens = tokenize(query)
    if not qtokens:
        return []

    groups = _object_groups(evidence)
    representatives = {object_id: rows[0] for object_id, rows in groups.items()}
    tokenized = {
        object_id: tokenize(read_text(src))
        for object_id, src in representatives.items()
    }
    n = len(groups)
    avgdl = sum(len(v) for v in tokenized.values()) / n
    dfs = Counter()
    for toks in tokenized.values():
        for term in set(toks):
            dfs[term] += 1

    k1 = 1.5
    b = 0.75
    hits = []
    qset = set(qtokens)
    for object_id, src in representatives.items():
        toks = tokenized[object_id]
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
            hits.append(
                Hit(
                    source=src,
                    score=score,
                    snippet=_best_snippet(read_text(src), qset, snippet_chars),
                    evidence_sources=groups[object_id],
                )
            )

    hits.sort(key=lambda h: (-h.score, h.object_id, h.source.source_id))
    return hits[: max(0, top_k)]


def render_context(
    root: Path,
    query: str,
    top_k: int = 8,
    max_chars_per_source: int = 1200,
    *,
    topic_id: str | None = None,
    include_superseded: bool = False,
) -> str:
    hits = search(
        root,
        query,
        top_k=top_k,
        snippet_chars=max_chars_per_source,
        topic_id=topic_id,
        include_superseded=include_superseded,
    )
    parts = []
    for hit in hits:
        source_ids = ", ".join(hit.source_ids)
        names = ", ".join(sorted({src.name for src in hit.evidence_sources}))
        parts.append(
            f"### EVIDENCE OBJECT {hit.object_id}\n"
            f"source_ids: {source_ids}\n"
            f"names: {names}\n"
            f"sha256: {hit.source.sha256}\n"
            f"provenance_records: {len(hit.evidence_sources)}\n"
            f"bm25: {hit.score:.6f}\n\n"
            f"{hit.snippet}"
        )
    return "\n\n".join(parts)
