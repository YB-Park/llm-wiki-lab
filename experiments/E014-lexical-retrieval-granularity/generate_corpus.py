from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

FORMAT = "llm-wiki-e014-corpus-v0"
FILLER_WORDS = (
    "meeting", "calendar", "deployment", "testing", "interface", "storage", "network",
    "review", "schedule", "archive", "metrics", "rotation", "backup", "queue", "monitor",
    "handoff", "policy", "release", "capacity", "incident",
)
SPLITS = {
    "development": {
        "seed": 20260814,
        "terms": (("cedar", "quota", "anchor"), ("pine", "tradeoff", "matrix"), ("oak", "rationale", "checkpoint")),
        "lures": (1, 2, 3, 4, 5),
        "filler_counts": (10, 10, 10, 10, 10),
        "cross_flat": {1, 3, 4},
        "lure_missing_term": 2,
    },
    "heldout": {
        "seed": 20260819,
        "terms": (("birch", "cap", "beacon"), ("spruce", "compromise", "ledger"), ("maple", "reason", "marker")),
        "lures": (5, 2, 4, 1, 3),
        "filler_counts": (12, 8, 14, 9, 11),
        "cross_flat": {0, 2, 4},
        "lure_missing_term": 1,
    },
}
SHAPES = ("short", "structured", "flat", "monolithic")


def _filler(seed: int, doc_id: str, index: int, count: int = 45) -> str:
    rng = random.Random(f"{seed}:{doc_id}:{index}")
    return " ".join(rng.choices(FILLER_WORDS, k=count))


def _make_doc(seed: int, doc_id: str, shape: str, target_parts: list[str], filler_count: int) -> str:
    if shape == "short":
        return "\n\n".join(target_parts + [" ".join(FILLER_WORDS[:7]) + "."])
    if shape == "structured":
        sections = [f"## Section {j}\n{_filler(seed, doc_id, j)}." for j in range(filler_count)]
        sections.insert(filler_count // 2, "### Evidence detail\n" + "\n\n".join(target_parts))
        if seed != SPLITS["development"]["seed"]:
            sections.insert(0, "# Overview\nSynthetic held-out preamble with no query signal.")
        return "\n\n".join(sections)
    if shape == "flat":
        paragraphs = [_filler(seed, doc_id, j) + "." for j in range(filler_count)]
        pos = filler_count // 2
        for part in reversed(target_parts):
            paragraphs.insert(pos, part)
        return "\n\n".join(paragraphs)
    if shape == "monolithic":
        chunks = [_filler(seed, doc_id, j) for j in range(filler_count // 2)]
        chunks.extend(target_parts)
        chunks.extend(_filler(seed, doc_id, j) for j in range(filler_count // 2, filler_count))
        return " ".join(chunks) + "."
    raise ValueError(f"unknown_shape:{shape}")


def _object(split: str, doc_id: str, text: str, *, extra_provenance: bool = False) -> dict:
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    source_ids = [f"src-e014-{split[:3]}-{doc_id}-a"]
    if extra_provenance:
        source_ids.append(f"src-e014-{split[:3]}-{doc_id}-b")
    return {
        "doc_id": doc_id,
        "object_id": f"obj-{sha}",
        "sha256": sha,
        "source_ids": source_ids,
        "text": text,
    }


def _lure_text(terms: tuple[str, str, str], missing: int, tail: str) -> str:
    kept = [term for idx, term in enumerate(terms) if idx != missing]
    return f"{kept[0]} {kept[1]} {kept[0]} {kept[1]} {tail}"


def build_corpus(split: str = "heldout") -> dict:
    if split not in SPLITS:
        raise ValueError(f"unknown_split:{split}")
    spec = SPLITS[split]
    seed = int(spec["seed"])
    term_families = spec["terms"]
    topics = []
    topic_index = 0
    for shape in SHAPES:
        for within_shape in range(5):
            i = topic_index
            topic_index += 1
            lure_count = spec["lures"][within_shape]
            filler_count = spec["filler_counts"][within_shape]
            exact_terms = (term_families[0][0], f"{term_families[0][1]}{i}", f"{term_families[0][2]}{i}")
            synthesis_terms = (term_families[1][0], f"{term_families[1][1]}{i}", f"{term_families[1][2]}{i}")
            decision_terms = (term_families[2][0], f"{term_families[2][1]}{i}", f"{term_families[2][2]}{i}")
            cross_boundary = shape == "flat" and within_shape in spec["cross_flat"]
            decision_parts = (
                [
                    f"{decision_terms[0]} {decision_terms[1]} decision background.",
                    f"{decision_terms[2]} final choice bounded growth because rollback risk was lower. GOLD_DE_{i}.",
                ]
                if cross_boundary
                else [
                    f"{' '.join(decision_terms)} final choice bounded growth because rollback risk was lower. GOLD_DE_{i}."
                ]
            )

            def make(doc_id: str, shape_: str, parts: list[str]) -> str:
                return _make_doc(seed, doc_id, shape_, parts, filler_count)

            docs = [
                _object(
                    split,
                    f"t{i}-exact",
                    make(f"t{i}-exact", shape, [f"{' '.join(exact_terms)} approved value forty one. GOLD_EX_{i}."]),
                    extra_provenance=i % 4 == 0,
                ),
                _object(
                    split,
                    f"t{i}-syn-a",
                    make(f"t{i}-syn-a", shape, [f"{' '.join(synthesis_terms)} latency evidence favors bounded cache. GOLD_SYA_{i}."]),
                ),
                _object(
                    split,
                    f"t{i}-syn-b",
                    make(f"t{i}-syn-b", shape, [f"{' '.join(synthesis_terms)} memory evidence warns against unbounded cache. GOLD_SYB_{i}."]),
                ),
                _object(split, f"t{i}-dec", make(f"t{i}-dec", shape, decision_parts)),
            ]

            for j in range(lure_count):
                docs.extend(
                    [
                        _object(
                            split,
                            f"t{i}-lure-ex-{j}",
                            make(
                                f"t{i}-lure-ex-{j}",
                                "short",
                                [_lure_text(exact_terms, int(spec["lure_missing_term"]), f"draft discussion only. LURE_EX_{i}_{j}.")],
                            ),
                        ),
                        _object(
                            split,
                            f"t{i}-lure-sy-{j}",
                            make(
                                f"t{i}-lure-sy-{j}",
                                "short",
                                [_lure_text(synthesis_terms, int(spec["lure_missing_term"]), f"incomplete rumor. LURE_SY_{i}_{j}.")],
                            ),
                        ),
                        _object(
                            split,
                            f"t{i}-lure-de-{j}",
                            make(
                                f"t{i}-lure-de-{j}",
                                "short",
                                [_lure_text(decision_terms, int(spec["lure_missing_term"]), f"superseded speculation. LURE_DE_{i}_{j}.")],
                            ),
                        ),
                    ]
                )

            docs.extend(
                [
                    _object(split, f"t{i}-noise1", make(f"t{i}-noise1", shape, ["general housekeeping and operational notes."])),
                    _object(split, f"t{i}-noise2", make(f"t{i}-noise2", shape, ["unrelated archive and calendar material."])),
                ]
            )

            queries = [
                {
                    "query_id": f"t{i}-q-ex",
                    "query_class": "exact_provenance",
                    "query": " ".join(exact_terms),
                    "required_doc_ids": [f"t{i}-exact"],
                    "required_signals": [f"GOLD_EX_{i}"],
                },
                {
                    "query_id": f"t{i}-q-sy",
                    "query_class": "synthesis",
                    "query": " ".join(synthesis_terms),
                    "required_doc_ids": [f"t{i}-syn-a", f"t{i}-syn-b"],
                    "required_signals": [f"GOLD_SYA_{i}", f"GOLD_SYB_{i}"],
                },
                {
                    "query_id": f"t{i}-q-de",
                    "query_class": "decision_history",
                    "query": " ".join(decision_terms),
                    "required_doc_ids": [f"t{i}-dec"],
                    "required_signals": [f"GOLD_DE_{i}"],
                },
            ]
            topics.append(
                {
                    "topic_id": f"e014-{split}-topic-{i:02d}",
                    "shape": shape,
                    "lure_count_per_query": lure_count,
                    "cross_boundary_decision": cross_boundary,
                    "documents": docs,
                    "queries": queries,
                }
            )

    return {
        "format": FORMAT,
        "split": split,
        "seed": seed,
        "topic_count": len(topics),
        "query_count": sum(len(t["queries"]) for t in topics),
        "topics": topics,
    }


def canonical_bytes(corpus: dict) -> bytes:
    return (json.dumps(corpus, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def corpus_sha256(corpus: dict) -> str:
    return hashlib.sha256(canonical_bytes(corpus)).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=tuple(SPLITS), default="heldout")
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    corpus = build_corpus(args.split)
    payload = json.dumps(corpus, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    print(
        f"E014-CORPUS split={args.split} format={FORMAT} topics={corpus['topic_count']} queries={corpus['query_count']} "
        f"sha256={corpus_sha256(corpus)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
