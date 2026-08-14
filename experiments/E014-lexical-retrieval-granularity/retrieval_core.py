from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
HEADING_RE = re.compile(r"^#{1,6}\s+\S")
BM25_K1 = 1.5
BM25_B = 0.75
CONTEXT_CHARS_PER_HIT = 320


@dataclass(frozen=True)
class Unit:
    unit_id: str
    doc_id: str
    object_id: str
    source_ids: tuple[str, ...]
    start: int
    end: int
    locator: str
    text: str


@dataclass(frozen=True)
class ObjectHit:
    doc_id: str
    object_id: str
    source_ids: tuple[str, ...]
    score: float
    unit: Unit
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


def _unit(doc: dict, start: int, end: int, locator: str, suffix: str) -> Unit:
    text = doc["text"][start:end]
    return Unit(
        unit_id=f"{doc['doc_id']}#{suffix}",
        doc_id=doc["doc_id"],
        object_id=doc["object_id"],
        source_ids=tuple(doc["source_ids"]),
        start=start,
        end=end,
        locator=locator,
        text=text,
    )


def units_w0(doc: dict) -> list[Unit]:
    return [_unit(doc, 0, len(doc["text"]), "whole", "whole")]


def units_g1(doc: dict) -> list[Unit]:
    sections = section_spans(doc["text"])
    if sections:
        return [_unit(doc, s, e, f"section:{i}", f"s{i}") for i, (s, e) in enumerate(sections)]
    paragraphs = paragraph_spans(doc["text"])
    if len(paragraphs) <= 2:
        return units_w0(doc)
    return [_unit(doc, s, e, f"paragraph:{i}", f"p{i}") for i, (s, e) in enumerate(paragraphs)]


def units_g2(doc: dict) -> list[Unit]:
    sections = section_spans(doc["text"])
    if sections:
        return [_unit(doc, s, e, f"section:{i}", f"s{i}") for i, (s, e) in enumerate(sections)]
    paragraphs = paragraph_spans(doc["text"])
    if len(paragraphs) <= 2:
        return units_w0(doc)
    units = [_unit(doc, s, e, f"paragraph:{i}", f"p{i}") for i, (s, e) in enumerate(paragraphs)]
    for i in range(len(paragraphs) - 1):
        start = paragraphs[i][0]
        end = paragraphs[i + 1][1]
        units.append(_unit(doc, start, end, f"paragraphs:{i}-{i+1}", f"w{i}"))
    return units


def condition_units(documents: list[dict], condition: str) -> list[Unit]:
    fn = {"W0": units_w0, "G1": units_g1, "G2": units_g2}[condition]
    out: list[Unit] = []
    for doc in documents:
        out.extend(fn(doc))
    return out


def _bm25(units: list[Unit], query: str) -> list[tuple[float, Unit]]:
    qtokens = tokenize(query)
    if not units or not qtokens:
        return []
    tokenized = {u.unit_id: tokenize(u.text) for u in units}
    n = len(units)
    avgdl = sum(len(v) for v in tokenized.values()) / n
    dfs: Counter[str] = Counter()
    for toks in tokenized.values():
        dfs.update(set(toks))

    scored: list[tuple[float, Unit]] = []
    for unit in units:
        toks = tokenized[unit.unit_id]
        tf = Counter(toks)
        dl = len(toks)
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


def _best_w0_context(doc: dict, query: str) -> str:
    qset = set(tokenize(query))
    spans = paragraph_spans(doc["text"])
    if not spans:
        return ""
    ranked = []
    for i, (start, end) in enumerate(spans):
        text = doc["text"][start:end]
        overlap = sum(1 for token in tokenize(text) if token in qset)
        ranked.append((-overlap, i, text))
    _, _, text = sorted(ranked)[0]
    if len(text) <= CONTEXT_CHARS_PER_HIT:
        return text
    return text[: CONTEXT_CHARS_PER_HIT - 1].rstrip() + "…"


def rank_objects(documents: list[dict], query: str, condition: str) -> list[ObjectHit]:
    units = condition_units(documents, condition)
    scored = _bm25(units, query)
    best: dict[str, tuple[float, Unit]] = {}
    for score, unit in scored:
        if unit.object_id not in best:
            best[unit.object_id] = (score, unit)

    docs = {doc["object_id"]: doc for doc in documents}
    hits: list[ObjectHit] = []
    for object_id, (score, unit) in best.items():
        doc = docs[object_id]
        if condition == "W0":
            context = _best_w0_context(doc, query)
        else:
            context = unit.text
            if len(context) > CONTEXT_CHARS_PER_HIT:
                context = context[: CONTEXT_CHARS_PER_HIT - 1].rstrip() + "…"
        hits.append(
            ObjectHit(
                doc_id=unit.doc_id,
                object_id=object_id,
                source_ids=unit.source_ids,
                score=score,
                unit=unit,
                context_text=context,
            )
        )
    hits.sort(key=lambda hit: (-hit.score, hit.object_id, hit.doc_id))
    return hits


def provenance_reversible(documents: list[dict], condition: str) -> bool:
    docs = {doc["doc_id"]: doc for doc in documents}
    for unit in condition_units(documents, condition):
        doc = docs[unit.doc_id]
        if not (0 <= unit.start <= unit.end <= len(doc["text"])):
            return False
        if doc["text"][unit.start:unit.end] != unit.text:
            return False
        if tuple(doc["source_ids"]) != unit.source_ids:
            return False
        if doc["object_id"] != unit.object_id:
            return False
    return True


def index_stats(documents: list[dict], condition: str) -> dict:
    units = condition_units(documents, condition)
    return {
        "units": len(units),
        "indexed_chars": sum(len(unit.text) for unit in units),
        "source_chars": sum(len(doc["text"]) for doc in documents),
    }
