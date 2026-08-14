from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections import Counter
from pathlib import Path

from generate_corpus import FORMAT, SEED, SHAPES, TOPICS_PER_SHAPE, build_corpus, corpus_sha256
from retrieval_r1 import condition_units, paragraph_spans, rank_objects, ranking_identity

EXPECTED_TOPICS = 40
EXPECTED_QUERIES = 120
EXPECTED_CORPUS_SHA256 = "f3126cc8e61455c4b962a7f2efb7505003ec92767f342a4eefb43f105348b442"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_v0_retrieval_module():
    path = _repo_root() / "experiments" / "E014-lexical-retrieval-granularity" / "retrieval_core.py"
    spec = importlib.util.spec_from_file_location("e014_v0_retrieval_frozen_reference", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable_to_load_e014_v0_retrieval_reference")
    module = importlib.util.module_from_spec(spec)
    # Python 3.12 dataclasses resolve cls.__module__ through sys.modules while
    # the module body executes. Register the isolated reference module before
    # exec_module(); this changes prescore plumbing only, not frozen scoring.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _assert_unit_reversibility(topic: dict) -> None:
    docs = {doc["doc_id"]: doc for doc in topic["documents"]}
    g1_units = condition_units(topic["documents"], "G1")
    x1_units = condition_units(topic["documents"], "X1")
    assert [u.unit_id for u in g1_units] == [u.unit_id for u in x1_units]
    assert [(u.start, u.end) for u in g1_units] == [(u.start, u.end) for u in x1_units]

    for condition in ("W0", "G1", "X1", "G2"):
        units = condition_units(topic["documents"], condition)
        assert units
        for unit in units:
            doc = docs[unit.doc_id]
            assert 0 <= unit.start <= unit.end <= len(doc["text"])
            assert doc["text"][unit.start:unit.end] == unit.text
            assert doc["object_id"] == unit.object_id
            assert tuple(doc["source_ids"]) == unit.source_ids


def _assert_cross_boundary_structure(topic: dict) -> None:
    assert topic["shape"] == "flat_cross"
    directions = topic["cross_directions"]
    assert set(directions) == {"exact_provenance", "synthesis_a", "synthesis_b", "decision_history"}
    assert set(directions.values()) <= {"forward", "backward"}

    docs = {doc["doc_id"]: doc for doc in topic["documents"]}
    queries = {query["query_class"]: query for query in topic["queries"]}
    index = int(topic["topic_id"].rsplit("-", 1)[1])

    cases = [
        (f"t{index}-exact", queries["exact_provenance"], f"R1_GOLD_EX_{index}", directions["exact_provenance"]),
        (f"t{index}-syn-a", queries["synthesis"], f"R1_GOLD_SYA_{index}", directions["synthesis_a"]),
        (f"t{index}-syn-b", queries["synthesis"], f"R1_GOLD_SYB_{index}", directions["synthesis_b"]),
        (f"t{index}-dec", queries["decision_history"], f"R1_GOLD_DE_{index}", directions["decision_history"]),
    ]

    for doc_id, query, signal, direction in cases:
        doc = docs[doc_id]
        paragraphs = [doc["text"][start:end] for start, end in paragraph_spans(doc["text"])]
        query_terms = query["query"].split()
        assert len(query_terms) == 3
        gold_indices = [i for i, paragraph in enumerate(paragraphs) if signal in paragraph]
        assert len(gold_indices) == 1
        strong_indices = [
            i
            for i, paragraph in enumerate(paragraphs)
            if paragraph.count(query_terms[0]) >= 2 and paragraph.count(query_terms[1]) >= 2
        ]
        assert len(strong_indices) == 1
        gold_i = gold_indices[0]
        strong_i = strong_indices[0]
        assert abs(gold_i - strong_i) == 1
        if direction == "forward":
            assert gold_i == strong_i + 1
        else:
            assert gold_i == strong_i - 1
        assert query_terms[2] in paragraphs[gold_i]
        assert signal not in paragraphs[strong_i]


def validate_heldout_structure_only() -> str:
    corpus = build_corpus()
    assert corpus["format"] == FORMAT
    assert corpus["seed"] == SEED
    assert corpus["topic_count"] == EXPECTED_TOPICS
    assert corpus["query_count"] == EXPECTED_QUERIES

    actual_sha = corpus_sha256(corpus)
    assert actual_sha == EXPECTED_CORPUS_SHA256

    shape_counts = Counter(topic["shape"] for topic in corpus["topics"])
    assert shape_counts == Counter({shape: TOPICS_PER_SHAPE for shape in SHAPES})

    direction_counts = {
        key: Counter()
        for key in ("exact_provenance", "synthesis_a", "synthesis_b", "decision_history")
    }
    duplicate_provenance_objects = 0
    all_object_ids: set[str] = set()

    for topic in corpus["topics"]:
        docs = {doc["doc_id"]: doc for doc in topic["documents"]}
        assert len(docs) == len(topic["documents"])
        query_classes = Counter(query["query_class"] for query in topic["queries"])
        assert query_classes == Counter({"exact_provenance": 1, "synthesis": 1, "decision_history": 1})

        for doc in docs.values():
            sha = hashlib.sha256(doc["text"].encode("utf-8")).hexdigest()
            assert doc["sha256"] == sha
            assert doc["object_id"] == f"obj-{sha}"
            assert doc["object_id"] not in all_object_ids
            all_object_ids.add(doc["object_id"])
            assert len(doc["source_ids"]) >= 1
            assert len(doc["source_ids"]) == len(set(doc["source_ids"]))
            assert all("/" not in sid and "\\" not in sid for sid in doc["source_ids"])
            duplicate_provenance_objects += int(len(doc["source_ids"]) > 1)

        all_text = "\n".join(doc["text"] for doc in docs.values())
        for query in topic["queries"]:
            assert "R1_GOLD_" not in query["query"]
            assert "LURE_R1_" not in query["query"]
            assert query["required_doc_ids"]
            assert query["required_signals"]
            for required_doc_id in query["required_doc_ids"]:
                assert required_doc_id in docs
            for signal in query["required_signals"]:
                assert all_text.count(signal) == 1
                assert sum(signal in docs[doc_id]["text"] for doc_id in query["required_doc_ids"]) == 1

        if topic["shape"] == "flat_cross":
            assert topic["cross_boundary"] is True
            _assert_cross_boundary_structure(topic)
            for key, direction in topic["cross_directions"].items():
                direction_counts[key][direction] += 1
        else:
            assert topic["cross_boundary"] is False
            assert topic["cross_directions"] == {}

        _assert_unit_reversibility(topic)

    assert direction_counts["exact_provenance"] == Counter({"forward": 4, "backward": 4})
    assert direction_counts["synthesis_a"] == Counter({"forward": 4, "backward": 4})
    assert direction_counts["synthesis_b"] == Counter({"backward": 5, "forward": 3})
    assert direction_counts["decision_history"] == Counter({"forward": 5, "backward": 3})
    assert duplicate_provenance_objects > 0
    return actual_sha


def _fixture_docs() -> list[dict]:
    raw = [
        ("short", "cedar quota decision forty two."),
        (
            "flat",
            "archive calendar notes.\n\ncedar quota cedar quota concentrated evidence.\n\nsentinel completes the span.\n\nrelease notes.",
        ),
        (
            "structured",
            "# Overview\nno signal.\n\n## One\narchive.\n\n## Two\ncedar quota sentinel final evidence.",
        ),
        ("noise", "calendar archive schedule only."),
    ]
    docs = []
    for doc_id, text in raw:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        docs.append(
            {
                "doc_id": f"fixture-{doc_id}",
                "object_id": f"obj-{sha}",
                "sha256": sha,
                "source_ids": [f"src-fixture-{doc_id}"],
                "text": text,
            }
        )
    return docs


def validate_nonheldout_scoring_contracts() -> None:
    docs = _fixture_docs()
    query = "cedar quota sentinel"
    v0 = _load_v0_retrieval_module()

    for condition in ("W0", "G1", "G2"):
        old_hits = v0.rank_objects(docs, query, condition)
        new_hits = rank_objects(docs, query, condition)
        assert [hit.object_id for hit in old_hits] == [hit.object_id for hit in new_hits]
        assert len(old_hits) == len(new_hits)
        for old, new in zip(old_hits, new_hits):
            assert abs(old.score - new.score) < 1e-12
            assert old.unit.unit_id == new.ranking_unit.unit_id

    assert ranking_identity(docs, query)
    g1 = rank_objects(docs, query, "G1")
    x1 = rank_objects(docs, query, "X1")
    assert [hit.object_id for hit in g1] == [hit.object_id for hit in x1]
    assert [hit.score for hit in g1] == [hit.score for hit in x1]

    flat_g1 = next(hit for hit in g1 if hit.doc_id == "fixture-flat")
    flat_x1 = next(hit for hit in x1 if hit.doc_id == "fixture-flat")
    assert flat_g1.context_locator.startswith("paragraph:")
    assert flat_x1.context_locator.startswith("expanded-paragraphs:")
    assert len(flat_x1.context_text) > len(flat_g1.context_text)
    assert "sentinel completes the span" in flat_x1.context_text


def main() -> int:
    heldout_sha = validate_heldout_structure_only()
    validate_nonheldout_scoring_contracts()
    print(
        "E014-R1-PRESCORE-VALIDATION PASS "
        f"topics={EXPECTED_TOPICS} queries={EXPECTED_QUERIES} shapes=8x5 heldoutSha={heldout_sha} "
        f"expectedSha={EXPECTED_CORPUS_SHA256} crossDirections=verified provenance=verified "
        "v0RankingEquivalence=yes x1G1RankingFixture=yes heldoutScoring=no modelCalls=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
