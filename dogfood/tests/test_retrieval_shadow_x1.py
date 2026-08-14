from __future__ import annotations

import importlib.util
import math
import sys
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.retrieval import (
    RETRIEVAL_STRUCTURAL_EXPAND_V1,
    RETRIEVAL_WHOLE_OBJECT_V0,
    search,
)
from dogfood.llm_wiki.store import ingest_file


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable_to_load:{path}")
    module = importlib.util.module_from_spec(spec)
    # Needed by dataclasses under Python 3.12 while the isolated module body
    # executes. This is test plumbing only.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REPO_ROOT = Path(__file__).resolve().parents[2]
E014_R1 = REPO_ROOT / "experiments" / "E014-r1-rank-expand"
FROZEN_GENERATOR = _load_module("e014_r1_frozen_generator_for_core_test", E014_R1 / "generate_corpus.py")
FROZEN_RETRIEVAL = _load_module("e014_r1_frozen_retrieval_for_core_test", E014_R1 / "retrieval_r1.py")


class StructuralExpandShadowTests(unittest.TestCase):
    def _ingest(self, root: Path, base: Path, topic: str, name: str, text: str, origin: str):
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return ingest_file(root, path, topic_id=topic, origin_id=origin)[0]

    def test_shadow_mode_is_explicit_and_default_dispatch_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            self._ingest(root, base, topic, "a.md", "cedar quota alpha", "origin-a")
            self._ingest(root, base, topic, "b.md", "cedar archive", "origin-b")

            implicit = search(root, "cedar quota", topic_id=topic, top_k=8)
            explicit_default = search(
                root,
                "cedar quota",
                topic_id=topic,
                top_k=8,
                mode=RETRIEVAL_WHOLE_OBJECT_V0,
            )
            self.assertEqual(
                [(h.object_id, h.score, h.snippet, h.source_ids) for h in implicit],
                [(h.object_id, h.score, h.snippet, h.source_ids) for h in explicit_default],
            )
            self.assertTrue(all(h.retrieval_mode == RETRIEVAL_WHOLE_OBJECT_V0 for h in implicit))

            shadow = search(
                root,
                "cedar quota",
                topic_id=topic,
                top_k=8,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            self.assertTrue(shadow)
            self.assertTrue(all(h.retrieval_mode == RETRIEVAL_STRUCTURAL_EXPAND_V1 for h in shadow))

            with self.assertRaises(ValueError):
                search(root, "cedar", topic_id=topic, mode="not-a-mode")

    def test_duplicate_provenance_does_not_change_structural_bm25(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            shared = base / "shared.md"
            shared.write_text("alpha\n\ncedar quota cedar quota\n\nsentinel evidence", encoding="utf-8")
            first, _ = ingest_file(root, shared, topic_id=topic, origin_id="origin-a")
            other = base / "other.md"
            other.write_text("cedar unrelated", encoding="utf-8")
            ingest_file(root, other, topic_id=topic, origin_id="origin-other")

            before = search(
                root,
                "cedar quota sentinel",
                topic_id=topic,
                top_k=8,
                snippet_chars=10000,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            before_hit = next(hit for hit in before if hit.object_id == first.object_id)

            second, _ = ingest_file(root, shared, topic_id=topic, origin_id="origin-b")
            after = search(
                root,
                "cedar quota sentinel",
                topic_id=topic,
                top_k=8,
                snippet_chars=10000,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            after_hit = next(hit for hit in after if hit.object_id == first.object_id)

            self.assertEqual(before_hit.score, after_hit.score)
            self.assertEqual(before_hit.snippet, after_hit.snippet)
            self.assertEqual(set(after_hit.source_ids), {first.source_id, second.source_id})
            self.assertEqual(sum(hit.object_id == first.object_id for hit in after), 1)

    def test_structural_shadow_respects_topic_current_and_history_views(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic_a = "topic-a"
            topic_b = "topic-b"

            old_path = base / "old.md"
            old_path.write_text("legacy\n\ncedar old quota\n\nseventeen units", encoding="utf-8")
            old, _ = ingest_file(root, old_path, topic_id=topic_a, origin_id="origin-a")
            new_path = base / "new.md"
            new_path.write_text("current\n\ncedar new quota\n\nforty one units", encoding="utf-8")
            new, _ = ingest_file(
                root,
                new_path,
                topic_id=topic_a,
                origin_id="origin-a",
                supersedes_source_id=old.source_id,
            )
            other_topic_path = base / "other-topic.md"
            other_topic_path.write_text("legacy\n\ncedar old quota\n\nseventeen units", encoding="utf-8")
            other, _ = ingest_file(root, other_topic_path, topic_id=topic_b, origin_id="origin-b")

            current = search(
                root,
                "legacy seventeen",
                topic_id=topic_a,
                top_k=8,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            self.assertNotIn(old.object_id, [hit.object_id for hit in current])
            self.assertIn(new.object_id, [hit.object_id for hit in search(
                root,
                "current forty",
                topic_id=topic_a,
                top_k=8,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )])

            history = search(
                root,
                "legacy seventeen",
                topic_id=topic_a,
                top_k=8,
                include_superseded=True,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            self.assertIn(old.object_id, [hit.object_id for hit in history])

            topic_b_hits = search(
                root,
                "legacy seventeen",
                topic_id=topic_b,
                top_k=8,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            self.assertEqual([hit.object_id for hit in topic_b_hits], [other.object_id])

    def test_expanded_context_metadata_reverses_to_exact_raw_span(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            text = (
                "archive only\n\n"
                "cedar quota cedar quota concentrated evidence\n\n"
                "sentinel completes the required span\n\n"
                "release only"
            )
            source = self._ingest(root, base, topic, "flat.md", text, "origin-flat")
            hit = search(
                root,
                "cedar quota sentinel",
                topic_id=topic,
                top_k=8,
                snippet_chars=10000,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )[0]

            self.assertEqual(hit.object_id, source.object_id)
            self.assertEqual(hit.ranking_locator, "paragraph:1")
            self.assertEqual(hit.context_locator, "expanded-paragraphs:1-2")
            self.assertIsNotNone(hit.context_start)
            self.assertIsNotNone(hit.context_end)
            expected = text[hit.context_start : hit.context_end]
            self.assertEqual(hit.snippet, expected)
            self.assertIn("cedar quota", expected)
            self.assertIn("sentinel completes", expected)

    def test_whole_frozen_e014_r1_corpus_matches_production_shadow_x1(self):
        corpus = FROZEN_GENERATOR.build_corpus()
        self.assertEqual(
            FROZEN_GENERATOR.corpus_sha256(corpus),
            "f3126cc8e61455c4b962a7f2efb7505003ec92767f342a4eefb43f105348b442",
        )

        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            for topic in corpus["topics"]:
                topic_id = topic["topic_id"]
                root = base / topic_id / "wiki"
                files = base / topic_id / "files"
                files.mkdir(parents=True, exist_ok=True)

                for doc in topic["documents"]:
                    path = files / doc["doc_id"]
                    path.write_text(doc["text"], encoding="utf-8")
                    for synthetic_source_id in doc["source_ids"]:
                        ingested, _ = ingest_file(
                            root,
                            path,
                            topic_id=topic_id,
                            origin_id=synthetic_source_id,
                        )
                        self.assertEqual(ingested.object_id, doc["object_id"])
                        self.assertEqual(ingested.sha256, doc["sha256"])

                for query in topic["queries"]:
                    frozen = FROZEN_RETRIEVAL.rank_objects(topic["documents"], query["query"], "X1")
                    core = search(
                        root,
                        query["query"],
                        topic_id=topic_id,
                        top_k=len(topic["documents"]) + 5,
                        snippet_chars=10_000_000,
                        mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
                    )

                    self.assertEqual(
                        [hit.object_id for hit in core],
                        [hit.object_id for hit in frozen],
                        f"object order mismatch topic={topic_id} query={query['query_id']}",
                    )
                    self.assertEqual(len(core), len(frozen))
                    for actual, expected in zip(core, frozen):
                        self.assertTrue(
                            math.isclose(actual.score, expected.score, rel_tol=0.0, abs_tol=1e-12),
                            f"score mismatch topic={topic_id} query={query['query_id']} object={actual.object_id}",
                        )
                        self.assertEqual(actual.ranking_locator, expected.ranking_unit.locator)
                        self.assertEqual(actual.context_locator, expected.context_locator)
                        self.assertEqual(actual.context_start, expected.context_start)
                        self.assertEqual(actual.context_end, expected.context_end)
                        self.assertEqual(actual.snippet, expected.context_text)


if __name__ == "__main__":
    unittest.main()
