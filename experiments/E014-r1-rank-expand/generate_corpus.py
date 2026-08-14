from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

FORMAT = "llm-wiki-e014-r1-corpus-v0"
SEED = 20260823
SHAPES = ("short", "structured", "flat_contained", "flat_cross", "monolithic")
TOPICS_PER_SHAPE = 8
FILLER_WORDS = (
    "audit", "batch", "capacity", "deploy", "event", "handoff", "index", "journal",
    "latency", "monitor", "network", "operation", "policy", "queue", "release", "review",
    "schedule", "storage", "testing", "version", "window", "archive", "backup", "runtime",
)
TERM_FAMILIES = (
    ("ash", "limit", "sentinel"),
    ("fir", "balance", "register"),
    ("elm", "cause", "token"),
)


def _filler(doc_id: str, index: int, words: int = 38) -> str:
    rng = random.Random(f"{SEED}:{doc_id}:{index}")
    return " ".join(rng.choices(FILLER_WORDS, k=words)) + "."


def _object(doc_id: str, text: str, *, duplicate_provenance: bool = False) -> dict:
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    source_ids = [f"src-r1-{doc_id}-a"]
    if duplicate_provenance:
        source_ids.append(f"src-r1-{doc_id}-b")
    return {
        "doc_id": doc_id,
        "object_id": f"obj-{sha}",
        "sha256": sha,
        "source_ids": source_ids,
        "text": text,
    }


def _terms(family: tuple[str, str, str], topic_index: int) -> tuple[str, str, str]:
    return family[0], f"{family[1]}{topic_index}", f"{family[2]}{topic_index}"


def _short(doc_id: str, parts: list[str]) -> str:
    return "\n\n".join(parts + [_filler(doc_id, 99, words=12)])


def _structured(doc_id: str, parts: list[str], filler_sections: int) -> str:
    sections = ["# Overview\nSynthetic structural preamble with no query terms."]
    for j in range(filler_sections):
        sections.append(f"## Record {j}\n{_filler(doc_id, j)}")
    position = 1 + filler_sections // 2
    sections.insert(position, "## Relevant record\n" + "\n\n".join(parts))
    return "\n\n".join(sections)


def _flat_contained(doc_id: str, parts: list[str], filler_paragraphs: int) -> str:
    paragraphs = [_filler(doc_id, j) for j in range(filler_paragraphs)]
    paragraphs.insert(filler_paragraphs // 2, " ".join(parts))
    return "\n\n".join(paragraphs)


def _flat_cross(
    doc_id: str,
    terms: tuple[str, str, str],
    gold_signal: str,
    filler_paragraphs: int,
    *,
    direction: str,
    semantic_tail: str,
) -> str:
    paragraphs = [_filler(doc_id, j) for j in range(filler_paragraphs)]
    strong = f"{terms[0]} {terms[1]} {terms[0]} {terms[1]} concentrated lexical evidence {semantic_tail}."
    weak_gold = f"{terms[2]} completes the evidence span {semantic_tail}. {gold_signal}."
    pos = filler_paragraphs // 2
    if direction == "forward":
        paragraphs[pos:pos] = [strong, weak_gold]
    elif direction == "backward":
        paragraphs[pos:pos] = [weak_gold, strong]
    else:
        raise ValueError(f"bad_direction:{direction}")
    return "\n\n".join(paragraphs)


def _monolithic(doc_id: str, parts: list[str], filler_chunks: int) -> str:
    chunks = [_filler(doc_id, j, words=35).rstrip(".") for j in range(filler_chunks)]
    midpoint = len(chunks) // 2
    chunks[midpoint:midpoint] = parts
    return " ".join(chunks) + "."


def _make_relevant(
    shape: str,
    doc_id: str,
    terms: tuple[str, str, str],
    signal: str,
    filler_count: int,
    *,
    direction: str,
    tail: str,
) -> str:
    contained = f"{' '.join(terms)} {tail}. {signal}."
    if shape == "short":
        return _short(doc_id, [contained])
    if shape == "structured":
        return _structured(doc_id, [contained], filler_count)
    if shape == "flat_contained":
        return _flat_contained(doc_id, [contained], filler_count)
    if shape == "flat_cross":
        return _flat_cross(
            doc_id,
            terms,
            signal,
            filler_count,
            direction=direction,
            semantic_tail=tail,
        )
    if shape == "monolithic":
        return _monolithic(doc_id, [contained], filler_count)
    raise ValueError(shape)


def _lure_text(terms: tuple[str, str, str], lure_index: int, class_tag: str) -> str:
    # Alternate which required term is omitted; every lure repeats the retained
    # lexical terms but contains no gold signal.
    missing = lure_index % 3
    kept = [term for idx, term in enumerate(terms) if idx != missing]
    return (
        f"{kept[0]} {kept[1]} {kept[0]} {kept[1]} {kept[0]} "
        f"draft {class_tag} rumor without authoritative completion. LURE_R1_{class_tag}_{lure_index}."
    )


def build_corpus() -> dict:
    topics = []
    topic_index = 0
    filler_pattern = (9, 13, 7, 15, 11, 17, 8, 14)
    lure_pattern = (4, 2, 5, 3, 6, 2, 4, 5)

    for shape in SHAPES:
        for within_shape in range(TOPICS_PER_SHAPE):
            i = topic_index
            topic_index += 1
            filler_count = filler_pattern[within_shape]
            lure_count = lure_pattern[within_shape]
            exact_terms = _terms(TERM_FAMILIES[0], i)
            synthesis_terms = _terms(TERM_FAMILIES[1], i)
            decision_terms = _terms(TERM_FAMILIES[2], i)

            # Alternate direction by topic and query class so X1 must handle both
            # previous- and next-paragraph expansion.
            directions = {
                "exact_provenance": "forward" if within_shape % 2 == 0 else "backward",
                "synthesis_a": "backward" if within_shape % 2 == 0 else "forward",
                "synthesis_b": "forward" if within_shape % 3 == 0 else "backward",
                "decision_history": "backward" if within_shape % 3 == 0 else "forward",
            }

            docs = [
                _object(
                    f"t{i}-exact",
                    _make_relevant(
                        shape,
                        f"t{i}-exact",
                        exact_terms,
                        f"R1_GOLD_EX_{i}",
                        filler_count,
                        direction=directions["exact_provenance"],
                        tail="approved exact value is forty two",
                    ),
                    duplicate_provenance=(i % 5 == 0),
                ),
                _object(
                    f"t{i}-syn-a",
                    _make_relevant(
                        shape,
                        f"t{i}-syn-a",
                        synthesis_terms,
                        f"R1_GOLD_SYA_{i}",
                        filler_count,
                        direction=directions["synthesis_a"],
                        tail="latency observation favors bounded operation",
                    ),
                ),
                _object(
                    f"t{i}-syn-b",
                    _make_relevant(
                        shape,
                        f"t{i}-syn-b",
                        synthesis_terms,
                        f"R1_GOLD_SYB_{i}",
                        filler_count,
                        direction=directions["synthesis_b"],
                        tail="memory observation rejects unbounded operation",
                    ),
                ),
                _object(
                    f"t{i}-dec",
                    _make_relevant(
                        shape,
                        f"t{i}-dec",
                        decision_terms,
                        f"R1_GOLD_DE_{i}",
                        filler_count,
                        direction=directions["decision_history"],
                        tail="final decision preferred reversible bounded growth",
                    ),
                ),
            ]

            for j in range(lure_count):
                for class_tag, terms in (
                    ("EX", exact_terms),
                    ("SY", synthesis_terms),
                    ("DE", decision_terms),
                ):
                    lure_id = f"t{i}-lure-{class_tag.lower()}-{j}"
                    docs.append(_object(lure_id, _short(lure_id, [_lure_text(terms, j, class_tag)])))

            docs.append(_object(f"t{i}-noise-a", _make_relevant(
                shape,
                f"t{i}-noise-a",
                ("neutral", f"archive{i}", f"memo{i}"),
                f"NOISE_R1_A_{i}",
                filler_count,
                direction="forward",
                tail="unrelated operational archive",
            )))
            docs.append(_object(f"t{i}-noise-b", _make_relevant(
                shape,
                f"t{i}-noise-b",
                ("generic", f"schedule{i}", f"note{i}"),
                f"NOISE_R1_B_{i}",
                filler_count,
                direction="backward",
                tail="unrelated scheduling material",
            )))

            queries = [
                {
                    "query_id": f"t{i}-q-ex",
                    "query_class": "exact_provenance",
                    "query": " ".join(exact_terms),
                    "required_doc_ids": [f"t{i}-exact"],
                    "required_signals": [f"R1_GOLD_EX_{i}"],
                },
                {
                    "query_id": f"t{i}-q-sy",
                    "query_class": "synthesis",
                    "query": " ".join(synthesis_terms),
                    "required_doc_ids": [f"t{i}-syn-a", f"t{i}-syn-b"],
                    "required_signals": [f"R1_GOLD_SYA_{i}", f"R1_GOLD_SYB_{i}"],
                },
                {
                    "query_id": f"t{i}-q-de",
                    "query_class": "decision_history",
                    "query": " ".join(decision_terms),
                    "required_doc_ids": [f"t{i}-dec"],
                    "required_signals": [f"R1_GOLD_DE_{i}"],
                },
            ]

            topics.append(
                {
                    "topic_id": f"e014-r1-topic-{i:02d}",
                    "shape": shape,
                    "cross_boundary": shape == "flat_cross",
                    "lure_count_per_class": lure_count,
                    "documents": docs,
                    "queries": queries,
                }
            )

    return {
        "format": FORMAT,
        "seed": SEED,
        "topic_count": len(topics),
        "query_count": sum(len(topic["queries"]) for topic in topics),
        "topics": topics,
    }


def canonical_bytes(corpus: dict) -> bytes:
    return (json.dumps(corpus, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def corpus_sha256(corpus: dict) -> str:
    return hashlib.sha256(canonical_bytes(corpus)).hexdigest()


def main() -> int:
    corpus = build_corpus()
    print(
        f"E014-R1-CORPUS format={FORMAT} seed={SEED} topics={corpus['topic_count']} "
        f"queries={corpus['query_count']} sha256={corpus_sha256(corpus)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
