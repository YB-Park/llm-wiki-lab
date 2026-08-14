from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
HEADING_RE = re.compile(r"^#{1,6}\s+\S")
BM25_K1 = 1.5
BM25_B = 0.75


@dataclass(frozen=True)
class Unit:
    unit_id: str
    doc_id: str
    object_id: str
    source_ids: tuple[str, ...]
    start: int
    end: int
    locator: str
    kind: str
    ordinal: int | None
    text: str


@dataclass(frozen=True)
class ObjectHit:
    doc_id: str
    object_id: str
    source_ids: tuple[str, ...]
    score: float
    ranking_unit: Unit
    context_start: int
    context_end: int
    context_locator: str
    context_text: str


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in TOKEN_RE.finditer(text)]


def paragraph_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    for part in text.split("\n\n"):
        start = cursor
        end = start + len(part)
        if part.strip():
            spans.append((start, end))
        cursor = end + 2
    return spans


def section_spans(text: str) -> list[tuple[int, int]]:
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


def _unit(
    doc: dict,
    start: int,
    end: int,
    locator: str,
    suffix: str,
    *,
    kind: str,
    ordinal: int | None,
) -> Unit:
    return Unit(
        unit_id=f"{doc['doc_id']}#{suffix}",
        doc_id=doc["doc_id"],
        object_id=doc["object_id"],
        source_ids=tuple(doc["source_ids"]),
        start=start,
        end=end,
        locator=locator,
        kind=kind,
        ordinal=ordinal,
        text=doc["text"][start:end],
    )


def units_w0(doc: dict) -> list[Unit]:
    return [_unit(doc, 0, len(doc["text"]), "whole", "whole", kind="whole", ordinal=None)]


def units_g1(doc: dict) -> list[Unit]:
    sections = section_spans(doc["text"])
    if sections:
        return [
            _unit(doc, start, end, f"section:{i}", f"s{i}", kind="section", ordinal=i)
            for i, (start, end) in enumerate(sections)
        ]
    paragraphs = paragraph_spans(doc["text"])
    if len(paragraphs) <= 2:
        return units_w0(doc)
    return [
        _unit(doc, start, end, f"paragraph:{i}", f"p{i}", kind="paragraph", ordinal=i)
        for i, (start, end) in enumerate(paragraphs)
    ]


def units_g2(doc: dict) -> list[Unit]:
    sections = section_spans(doc["text"])
    if sections:
        return [
            _unit(doc, start, end, f"section:{i}", f"s{i}", kind="section", ordinal=i)
            for i, (start, end) in enumerate(sections)
        ]
    paragraphs = paragraph_spans(doc["text"])
    if len(paragraphs) <= 2:
        return units_w0(doc)
    units = [
        _unit(doc, start, end, f"paragraph:{i}", f"p{i}", kind="paragraph", ordinal=i)
        for i, (start, end) in enumerate(paragraphs)
    ]
    for i in range(len(paragraphs) - 1):
        start = paragraphs[i][0]
        end = paragraphs[i + 1][1]
        units.append(
            _unit(
                doc,
                start,
                end,
                f"paragraphs:{i}-{i + 1}",
                f"w{i}",
                kind="window2",
                ordinal=i,
            )
        )
    return units


def condition_units(documents: list[dict], condition: str) -> list[Unit]:
    if condition == "W0":
        fn = units_w0
    elif condition in {"G1", "X1"}:
        fn = units_g1
    elif condition == "G2":
        fn = units_g2
    else:
        raise ValueError(f"unknown_condition:{condition}")
    out: list[Unit] = []
    for doc in documents:
        out.extend(fn(doc))
    return out


def _bm25(units: list[Unit], query: str) -> list[tuple[float, Unit]]:
    qtokens = tokenize(query)
    if not qtokens or not units:
        return []
    tokenized = {unit.unit_id: tokenize(unit.text) for unit in units}
    n = len(units)
    avgdl = sum(len(tokens) for tokens in tokenized.values()) / n
    dfs: Counter[str] = Counter()
    for tokens in tokenized.values():
        dfs.update(set(tokens))

    scored: list[tuple[float, Unit]] = []
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


def _best_w0_context(doc: dict, query: str) -> tuple[int, int, str]:
    spans = paragraph_spans(doc["text"])
    if len(spans) <= 1:
        return 0, len(doc["text"]), "whole"
    qset = set(tokenize(query))
    ranked = []
    for i, (start, end) in enumerate(spans):
        paragraph = doc["text"][start:end]
        count = sum(token in qset for token in tokenize(paragraph))
        ranked.append((-count, i, start, end))
    _, i, start, end = sorted(ranked)[0]
    return start, end, f"best-paragraph:{i}"


def _expand_x1(doc: dict, query: str, unit: Unit) -> tuple[int, int, str]:
    if unit.kind != "paragraph" or unit.ordinal is None:
        return unit.start, unit.end, unit.locator

    paragraphs = paragraph_spans(doc["text"])
    i = unit.ordinal
    qset = set(tokenize(query))
    candidates: list[tuple[int, int, str]] = []
    if i > 0:
        start, end = paragraphs[i - 1]
        count = sum(token in qset for token in tokenize(doc["text"][start:end]))
        candidates.append((count, i - 1, "previous"))
    if i + 1 < len(paragraphs):
        start, end = paragraphs[i + 1]
        count = sum(token in qset for token in tokenize(doc["text"][start:end]))
        candidates.append((count, i + 1, "next"))
    if not candidates:
        return unit.start, unit.end, unit.locator

    # Highest query-token count wins. On a tie choose next when available,
    # otherwise previous, exactly as preregistered.
    max_count = max(row[0] for row in candidates)
    tied = [row for row in candidates if row[0] == max_count]
    next_rows = [row for row in tied if row[2] == "next"]
    chosen = next_rows[0] if next_rows else tied[0]
    neighbor_index = chosen[1]
    start = min(paragraphs[i][0], paragraphs[neighbor_index][0])
    end = max(paragraphs[i][1], paragraphs[neighbor_index][1])
    lo, hi = sorted((i, neighbor_index))
    return start, end, f"expanded-paragraphs:{lo}-{hi}"


def rank_objects(documents: list[dict], query: str, condition: str) -> list[ObjectHit]:
    units = condition_units(documents, condition)
    scored = _bm25(units, query)
    best: dict[str, tuple[float, Unit]] = {}
    for score, unit in scored:
        if unit.object_id not in best:
            best[unit.object_id] = (score, unit)

    docs_by_object = {doc["object_id"]: doc for doc in documents}
    hits: list[ObjectHit] = []
    for object_id, (score, unit) in best.items():
        doc = docs_by_object[object_id]
        if condition == "W0":
            start, end, locator = _best_w0_context(doc, query)
        elif condition == "X1":
            start, end, locator = _expand_x1(doc, query, unit)
        else:
            start, end, locator = unit.start, unit.end, unit.locator
        hits.append(
            ObjectHit(
                doc_id=unit.doc_id,
                object_id=unit.object_id,
                source_ids=unit.source_ids,
                score=score,
                ranking_unit=unit,
                context_start=start,
                context_end=end,
                context_locator=locator,
                context_text=doc["text"][start:end],
            )
        )
    hits.sort(key=lambda hit: (-hit.score, hit.object_id, hit.doc_id))
    return hits


def provenance_reversible(documents: list[dict], condition: str, query: str) -> bool:
    docs_by_id = {doc["doc_id"]: doc for doc in documents}
    for unit in condition_units(documents, condition):
        doc = docs_by_id[unit.doc_id]
        if tuple(doc["source_ids"]) != unit.source_ids:
            return False
        if doc["object_id"] != unit.object_id:
            return False
        if doc["text"][unit.start:unit.end] != unit.text:
            return False
    for hit in rank_objects(documents, query, condition):
        doc = docs_by_id[hit.doc_id]
        if doc["text"][hit.context_start:hit.context_end] != hit.context_text:
            return False
        if hit.context_start < 0 or hit.context_end > len(doc["text"]):
            return False
    return True


def index_stats(documents: list[dict], condition: str) -> dict:
    units = condition_units(documents, condition)
    return {
        "units": len(units),
        "indexed_chars": sum(len(unit.text) for unit in units),
        "source_chars": sum(len(doc["text"]) for doc in documents),
    }


def ranking_identity(documents: list[dict], query: str) -> bool:
    g1 = rank_objects(documents, query, "G1")
    x1 = rank_objects(documents, query, "X1")
    if len(g1) != len(x1):
        return False
    for left, right in zip(g1, x1):
        if left.object_id != right.object_id or left.doc_id != right.doc_id:
            return False
        if abs(left.score - right.score) >= 1e-15:
            return False
        if left.ranking_unit.unit_id != right.ranking_unit.unit_id:
            return False
    return True
