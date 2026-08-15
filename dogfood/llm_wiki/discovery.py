from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .calibration import topics
from .retrieval import BM25_B, BM25_K1, tokenize
from .store import Source, read_text, sources


@dataclass(frozen=True)
class DiscoveryHit:
    """One globally scored current-evidence hit associated with one topic."""

    topic_id: str
    topic_label: str
    source: Source
    evidence_sources: tuple[Source, ...]
    score: float
    snippet: str

    @property
    def source_ids(self) -> tuple[str, ...]:
        return tuple(src.source_id for src in self.evidence_sources)

    @property
    def object_id(self) -> str:
        return self.source.object_id


def _best_snippet(text: str, query_tokens: set[str], max_chars: int) -> str:
    """Keep whole-object discovery snippets compatible with W0 display behavior."""
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    if not blocks or max_chars <= 0:
        return ""
    ranked = []
    for index, block in enumerate(blocks):
        tokens = tokenize(block)
        overlap = sum(1 for token in tokens if token in query_tokens)
        ranked.append((-overlap, index, block))
    block = sorted(ranked)[0][2]
    if len(block) <= max_chars:
        return block
    if max_chars == 1:
        return "…"
    return block[: max_chars - 1].rstrip() + "…"


def _topic_object_groups(root: Path) -> tuple[dict[str, dict[str, tuple[Source, ...]]], dict[str, str]]:
    """Collect only each topic's current evidence, grouped by immutable object."""
    memberships: dict[str, dict[str, tuple[Source, ...]]] = defaultdict(dict)
    labels: dict[str, str] = {}
    for topic in topics(root):
        topic_id = str(topic["topic_id"])
        labels[topic_id] = str(topic["label"])
        grouped: dict[str, list[Source]] = defaultdict(list)
        for source in sources(root, topic_id=topic_id, include_superseded=False):
            grouped[source.object_id].append(source)
        for object_id, rows in grouped.items():
            ordered = tuple(sorted(rows, key=lambda source: source.source_id))
            shas = {source.sha256 for source in ordered}
            if len(shas) != 1:
                raise RuntimeError(f"object_identity_collision:{object_id}")
            memberships[object_id][topic_id] = ordered
    return dict(memberships), labels


def discover_current(
    root: Path,
    query: str,
    *,
    top_k_per_topic: int = 3,
    snippet_chars: int = 320,
) -> list[DiscoveryHit]:
    """Rank all topic-current objects in one BM25 space, then attach topic membership.

    Topic-scoped search computes BM25 statistics independently per topic, so its
    raw scores are not comparable across topics of very different sizes. Global
    discovery must therefore score the union of current immutable content
    objects once. It deliberately does *not* call unscoped ``sources()`` because
    that view includes historical/superseded evidence.
    """
    if top_k_per_topic <= 0:
        return []
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    memberships, labels = _topic_object_groups(root)
    if not memberships:
        return []

    representatives: dict[str, Source] = {}
    texts: dict[str, str] = {}
    tokenized: dict[str, list[str]] = {}
    for object_id in sorted(memberships):
        topic_map = memberships[object_id]
        first_topic_id = sorted(topic_map)[0]
        source = topic_map[first_topic_id][0]
        representatives[object_id] = source
        text = read_text(source)
        texts[object_id] = text
        tokenized[object_id] = tokenize(text)

    document_count = len(tokenized)
    avgdl = sum(len(tokens) for tokens in tokenized.values()) / document_count
    dfs: Counter[str] = Counter()
    for tokens in tokenized.values():
        dfs.update(set(tokens))

    scored: list[tuple[float, str]] = []
    for object_id, tokens in tokenized.items():
        tf = Counter(tokens)
        dl = len(tokens)
        score = 0.0
        for term in query_tokens:
            if tf[term] == 0:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (document_count - df + 0.5) / (df + 0.5))
            denom = tf[term] + BM25_K1 * (1 - BM25_B + BM25_B * dl / avgdl)
            score += idf * (tf[term] * (BM25_K1 + 1)) / denom
        if score > 0:
            scored.append((score, object_id))
    scored.sort(key=lambda row: (-row[0], row[1]))

    qset = set(query_tokens)
    counts: Counter[str] = Counter()
    hits: list[DiscoveryHit] = []
    for score, object_id in scored:
        text = texts[object_id]
        snippet = _best_snippet(text, qset, snippet_chars)
        for topic_id in sorted(memberships[object_id]):
            if counts[topic_id] >= top_k_per_topic:
                continue
            evidence_sources = memberships[object_id][topic_id]
            hits.append(
                DiscoveryHit(
                    topic_id=topic_id,
                    topic_label=labels[topic_id],
                    source=evidence_sources[0],
                    evidence_sources=evidence_sources,
                    score=score,
                    snippet=snippet,
                )
            )
            counts[topic_id] += 1

    hits.sort(key=lambda hit: (-hit.score, hit.object_id, hit.topic_id, hit.source.source_id))
    return hits
