from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .store import Source, read_text, sources
from .temporal_context import evidence_temporal_metadata

TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
HEADING_RE = re.compile(r"^#{1,6}\s+\S")

RETRIEVAL_WHOLE_OBJECT_V0 = "whole_object_v0"
RETRIEVAL_STRUCTURAL_EXPAND_V1 = "structural_expand_v1"

BM25_K1 = 1.5
BM25_B = 0.75


@dataclass(frozen=True)
class Hit:
    # `source` is a deterministic representative kept for backwards-compatible
    # consumers. `evidence_sources` contains every active evidence record that
    # points to the same immutable content object.
    source: Source
    score: float
    snippet: str
    evidence_sources: tuple[Source, ...]
    # Optional exact-span metadata is populated by structural retrieval. The
    # snippet can still be display-truncated; start/end describe the full
    # selected context span in the immutable content object.
    context_start: int | None = None
    context_end: int | None = None
    ranking_locator: str | None = None
    context_locator: str | None = None
    retrieval_mode: str = RETRIEVAL_WHOLE_OBJECT_V0

    @property
    def source_ids(self) -> tuple[str, ...]:
        return tuple(src.source_id for src in self.evidence_sources)

    @property
    def object_id(self) -> str:
        return self.source.object_id


@dataclass(frozen=True)
class _StructuralUnit:
    unit_id: str
    object_id: str
    start: int
    end: int
    locator: str
    kind: str
    ordinal: int | None
    text: str


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in TOKEN_RE.finditer(text)]


def _truncate(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    if max_chars == 1:
        return "…"
    return text[: max_chars - 1].rstrip() + "…"


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


def _search_whole_object_v0(
    root: Path,
    query: str,
    top_k: int,
    snippet_chars: int,
    *,
    topic_id: str | None,
    include_superseded: bool,
) -> list[Hit]:
    """Frozen default retrieval behavior.

    Keep this path semantically identical to the pre-E014 production core. New
    retrieval candidates live beside it and must be explicitly selected.
    """
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


def _paragraph_spans(text: str) -> list[tuple[int, int]]:
    # Matches the frozen E014-R1 mechanism exactly: split on literal blank
    # lines, preserve exact character ranges, and ignore whitespace-only parts.
    spans: list[tuple[int, int]] = []
    cursor = 0
    for part in text.split("\n\n"):
        start = cursor
        end = start + len(part)
        if part.strip():
            spans.append((start, end))
        cursor = end + 2
    return spans


def _section_spans(text: str) -> list[tuple[int, int]]:
    lines = text.splitlines(keepends=True)
    starts: list[int] = []
    offset = 0
    for line in lines:
        if HEADING_RE.match(line.rstrip("\r\n")):
            starts.append(offset)
        offset += len(line)
    if len(starts) < 2:
        return []
    starts.append(len(text))
    return [(starts[i], starts[i + 1]) for i in range(len(starts) - 1)]


def _structural_units(object_id: str, text: str) -> list[_StructuralUnit]:
    sections = _section_spans(text)
    if sections:
        return [
            _StructuralUnit(
                unit_id=f"{object_id}#s{i}",
                object_id=object_id,
                start=start,
                end=end,
                locator=f"section:{i}",
                kind="section",
                ordinal=i,
                text=text[start:end],
            )
            for i, (start, end) in enumerate(sections)
        ]

    paragraphs = _paragraph_spans(text)
    if len(paragraphs) <= 2:
        return [
            _StructuralUnit(
                unit_id=f"{object_id}#whole",
                object_id=object_id,
                start=0,
                end=len(text),
                locator="whole",
                kind="whole",
                ordinal=None,
                text=text,
            )
        ]
    return [
        _StructuralUnit(
            unit_id=f"{object_id}#p{i}",
            object_id=object_id,
            start=start,
            end=end,
            locator=f"paragraph:{i}",
            kind="paragraph",
            ordinal=i,
            text=text[start:end],
        )
        for i, (start, end) in enumerate(paragraphs)
    ]


def _score_structural_units(units: list[_StructuralUnit], query: str) -> list[tuple[float, _StructuralUnit]]:
    qtokens = tokenize(query)
    if not qtokens or not units:
        return []

    tokenized = {unit.unit_id: tokenize(unit.text) for unit in units}
    n = len(units)
    avgdl = sum(len(tokens) for tokens in tokenized.values()) / n
    dfs: Counter[str] = Counter()
    for tokens in tokenized.values():
        dfs.update(set(tokens))

    scored: list[tuple[float, _StructuralUnit]] = []
    for unit in units:
        tokens = tokenized[unit.unit_id]
        tf = Counter(tokens)
        dl = len(tokens)
        score = 0.0
        for term in qtokens:
            if tf[term] == 0:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            denom = tf[term] + BM25_K1 * (1 - BM25_B + BM25_B * dl / avgdl)
            score += idf * (tf[term] * (BM25_K1 + 1)) / denom
        if score > 0:
            scored.append((score, unit))
    scored.sort(key=lambda row: (-row[0], row[1].unit_id))
    return scored


def _expand_structural_context(text: str, query: str, unit: _StructuralUnit) -> tuple[int, int, str]:
    if unit.kind != "paragraph" or unit.ordinal is None:
        return unit.start, unit.end, unit.locator

    paragraphs = _paragraph_spans(text)
    i = unit.ordinal
    qset = set(tokenize(query))
    candidates: list[tuple[int, int, str]] = []
    if i > 0:
        start, end = paragraphs[i - 1]
        count = sum(token in qset for token in tokenize(text[start:end]))
        candidates.append((count, i - 1, "previous"))
    if i + 1 < len(paragraphs):
        start, end = paragraphs[i + 1]
        count = sum(token in qset for token in tokenize(text[start:end]))
        candidates.append((count, i + 1, "next"))
    if not candidates:
        return unit.start, unit.end, unit.locator

    max_count = max(row[0] for row in candidates)
    tied = [row for row in candidates if row[0] == max_count]
    next_rows = [row for row in tied if row[2] == "next"]
    chosen = next_rows[0] if next_rows else tied[0]
    neighbor_index = chosen[1]
    start = min(paragraphs[i][0], paragraphs[neighbor_index][0])
    end = max(paragraphs[i][1], paragraphs[neighbor_index][1])
    lo, hi = sorted((i, neighbor_index))
    return start, end, f"expanded-paragraphs:{lo}-{hi}"


def _search_structural_expand_v1(
    root: Path,
    query: str,
    top_k: int,
    snippet_chars: int,
    *,
    topic_id: str | None,
    include_superseded: bool,
) -> list[Hit]:
    evidence = sources(root, topic_id=topic_id, include_superseded=include_superseded)
    if not evidence or not tokenize(query):
        return []

    groups = _object_groups(evidence)
    representatives = {object_id: rows[0] for object_id, rows in groups.items()}
    texts = {object_id: read_text(src) for object_id, src in representatives.items()}

    units: list[_StructuralUnit] = []
    for object_id in sorted(groups):
        units.extend(_structural_units(object_id, texts[object_id]))

    scored = _score_structural_units(units, query)
    best: dict[str, tuple[float, _StructuralUnit]] = {}
    for score, unit in scored:
        if unit.object_id not in best:
            best[unit.object_id] = (score, unit)

    hits: list[Hit] = []
    for object_id, (score, unit) in best.items():
        text = texts[object_id]
        start, end, context_locator = _expand_structural_context(text, query, unit)
        src = representatives[object_id]
        hits.append(
            Hit(
                source=src,
                score=score,
                snippet=_truncate(text[start:end], snippet_chars),
                evidence_sources=groups[object_id],
                context_start=start,
                context_end=end,
                ranking_locator=unit.locator,
                context_locator=context_locator,
                retrieval_mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
        )

    # Object identity, rather than source multiplicity or path/name, defines the
    # semantic tie boundary for the shadow candidate.
    hits.sort(key=lambda h: (-h.score, h.object_id))
    return hits[: max(0, top_k)]


def search(
    root: Path,
    query: str,
    top_k: int = 8,
    snippet_chars: int = 320,
    *,
    topic_id: str | None = None,
    include_superseded: bool = False,
    mode: str = RETRIEVAL_WHOLE_OBJECT_V0,
) -> list[Hit]:
    if mode == RETRIEVAL_WHOLE_OBJECT_V0:
        return _search_whole_object_v0(
            root,
            query,
            top_k,
            snippet_chars,
            topic_id=topic_id,
            include_superseded=include_superseded,
        )
    if mode == RETRIEVAL_STRUCTURAL_EXPAND_V1:
        return _search_structural_expand_v1(
            root,
            query,
            top_k,
            snippet_chars,
            topic_id=topic_id,
            include_superseded=include_superseded,
        )
    raise ValueError(f"unknown_retrieval_mode:{mode}")


def render_context(
    root: Path,
    query: str,
    top_k: int = 8,
    max_chars_per_source: int = 1200,
    *,
    topic_id: str | None = None,
    include_superseded: bool = False,
    mode: str = RETRIEVAL_WHOLE_OBJECT_V0,
) -> str:
    hits = search(
        root,
        query,
        top_k=top_k,
        snippet_chars=max_chars_per_source,
        topic_id=topic_id,
        include_superseded=include_superseded,
        mode=mode,
    )
    parts = []
    for hit in hits:
        source_ids = ", ".join(hit.source_ids)
        names_json = json.dumps(sorted({src.name for src in hit.evidence_sources}), ensure_ascii=False)
        temporal_lines = evidence_temporal_metadata(root, topic_id, hit.source_ids)
        header_lines = [
            f"### EVIDENCE OBJECT {hit.object_id}",
            f"source_ids: {source_ids}",
            f"names_json: {names_json}",
            f"sha256: {hit.source.sha256}",
            f"provenance_records: {len(hit.evidence_sources)}",
            f"bm25: {hit.score:.6f}",
            *temporal_lines,
        ]
        quoted_evidence = "\n".join(f"> {line}" for line in hit.snippet.splitlines())
        parts.append(
            "\n".join(header_lines)
            + "\n\n--- EVIDENCE TEXT (UNTRUSTED QUOTED DATA) ---\n"
            + quoted_evidence
            + "\n--- END EVIDENCE TEXT ---"
        )
    return "\n\n".join(parts)
