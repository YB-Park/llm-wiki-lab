from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from dogfood.llm_wiki.retrieval import search as production_search
from dogfood.llm_wiki.store import ingest_file
from generate_corpus import SHAPES, build_corpus, corpus_sha256
from retrieval_core import condition_units, provenance_reversible, rank_objects

EXPECTED_HELDOUT_SHA256 = "4dde1977666bf8f7494f5ca688631cfd2bb878272ccc1b7821456127d6778eed"
EXPECTED_TOPICS = 20
EXPECTED_QUERIES = 60
EXPECTED_SHAPE_COUNT = 5


def validate_corpus() -> None:
    corpus = build_corpus("heldout")
    assert corpus_sha256(corpus) == EXPECTED_HELDOUT_SHA256
    assert corpus["topic_count"] == EXPECTED_TOPICS
    assert corpus["query_count"] == EXPECTED_QUERIES
    shape_counts = {shape: 0 for shape in SHAPES}
    cross_boundary = 0
    for topic in corpus["topics"]:
        shape_counts[topic["shape"]] += 1
        cross_boundary += int(topic["cross_boundary_decision"])
        docs = {doc["doc_id"]: doc for doc in topic["documents"]}
        assert len(docs) == len(topic["documents"])
        for doc in docs.values():
            sha = hashlib.sha256(doc["text"].encode("utf-8")).hexdigest()
            assert doc["sha256"] == sha
            assert doc["object_id"] == f"obj-{sha}"
            assert len(doc["source_ids"]) >= 1
            assert all("/" not in sid and "\\" not in sid for sid in doc["source_ids"])
        for query in topic["queries"]:
            assert "GOLD_" not in query["query"] and "LURE_" not in query["query"]
            for required in query["required_doc_ids"]:
                assert required in docs
            all_text = "\n".join(doc["text"] for doc in docs.values())
            for signal in query["required_signals"]:
                assert all_text.count(signal) == 1
                assert any(signal in docs[doc_id]["text"] for doc_id in query["required_doc_ids"])
        for condition in ("W0", "G1", "G2"):
            assert provenance_reversible(topic["documents"], condition)
            units = condition_units(topic["documents"], condition)
            assert units
            for unit in units:
                assert unit.text == docs[unit.doc_id]["text"][unit.start:unit.end]
    assert shape_counts == {shape: EXPECTED_SHAPE_COUNT for shape in SHAPES}
    assert cross_boundary == 3


def validate_w0_equivalence() -> None:
    # Separate non-held-out fixture: prove the experiment W0 order/scores equal
    # the current core baseline when each text is one current content object.
    texts = {
        "a": "cedar cedar quota decision with bounded cache",
        "b": "cedar quota draft discussion",
        "c": "calendar meeting archive",
    }
    docs = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        root = base / "wiki"
        for name, text in texts.items():
            path = base / f"{name}.md"
            path.write_text(text, encoding="utf-8")
            src, _ = ingest_file(root, path, topic_id="topic-equivalence", origin_id=f"origin-{name}")
            docs.append(
                {
                    "doc_id": name,
                    "object_id": src.object_id,
                    "sha256": src.sha256,
                    "source_ids": [src.source_id],
                    "text": text,
                }
            )
        prod = production_search(root, "cedar quota", topic_id="topic-equivalence", top_k=8)
        exp = rank_objects(docs, "cedar quota", "W0")
        assert [hit.object_id for hit in prod] == [hit.object_id for hit in exp]
        assert len(prod) == len(exp)
        for left, right in zip(prod, exp):
            assert abs(left.score - right.score) < 1e-12


def main() -> int:
    validate_corpus()
    validate_w0_equivalence()
    print(
        "E014-PRESCORE-VALIDATION PASS heldoutSha=" + EXPECTED_HELDOUT_SHA256
        + " topics=20 queries=60 shapes=5x4 crossBoundary=3 W0equivalence=yes provenanceReversible=yes modelCalls=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
