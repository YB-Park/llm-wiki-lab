from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.store import find_source, ingest_file, sources
from dogfood.llm_wiki.temporal import (
    RELATION_CHANGE,
    RELATION_CORRECTION,
    RELATION_GENERIC,
    replace_source,
    temporal_source_status,
)


class E003TemporalGateMatrixTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_each_replacement_kind_preserves_recurrence_raw_reuse_and_old_citation(self):
        cases = (
            (RELATION_GENERIC, None),
            (RELATION_CORRECTION, None),
            (RELATION_CHANGE, "2025-01-02T03:04:05+00:00"),
        )
        for relation_kind, effective_at in cases:
            with self.subTest(relation_kind=relation_kind), tempfile.TemporaryDirectory() as td:
                base = Path(td)
                root = base / "wiki"
                topic = "topic"
                a_path = self._write(base, "a.md", "STATE=A")
                b_path = self._write(base, "b.md", "STATE=B")

                a1, _ = ingest_file(root, a_path, topic_id=topic, origin_id="origin-state")
                b, _ = ingest_file(root, b_path, topic_id=topic, origin_id="origin-state")
                self.assertTrue(
                    replace_source(
                        root,
                        a1.source_id,
                        b.source_id,
                        topic_id=topic,
                        relation_kind=relation_kind,
                        effective_at=effective_at,
                    )
                )
                self.assertEqual(temporal_source_status(root, a1.source_id, topic_id=topic)["status"], "superseded")
                self.assertEqual(find_source(root, a1.source_id, topic_id=topic).object_id, a1.object_id)

                # Reverting to identical A bytes creates a fresh evidence revision
                # while reusing the immutable content object. The recurrence
                # constructor remains the existing explicit ingest+supersedes path.
                a2, duplicate_object = ingest_file(
                    root,
                    a_path,
                    topic_id=topic,
                    origin_id="origin-state",
                    supersedes_source_id=b.source_id,
                )
                self.assertNotEqual(a2.source_id, a1.source_id)
                self.assertEqual(a2.object_id, a1.object_id)
                self.assertTrue(duplicate_object)
                self.assertEqual({src.source_id for src in sources(root, topic_id=topic)}, {a2.source_id})
                self.assertEqual(
                    {src.source_id for src in sources(root, topic_id=topic, include_superseded=True)},
                    {a1.source_id, b.source_id, a2.source_id},
                )
                self.assertEqual(find_source(root, a1.source_id, topic_id=topic).source_id, a1.source_id)
                self.assertEqual(find_source(root, b.source_id, topic_id=topic).source_id, b.source_id)

    def test_recorded_replacement_cannot_be_retargeted_to_different_successor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            a, _ = ingest_file(root, self._write(base, "a.md", "A"), topic_id=topic, origin_id="origin-a")
            b, _ = ingest_file(root, self._write(base, "b.md", "B"), topic_id=topic, origin_id="origin-b")
            c, _ = ingest_file(root, self._write(base, "c.md", "C"), topic_id=topic, origin_id="origin-c")

            self.assertTrue(
                replace_source(
                    root,
                    a.source_id,
                    b.source_id,
                    topic_id=topic,
                    relation_kind=RELATION_CORRECTION,
                )
            )
            with self.assertRaisesRegex(ValueError, "replacement_semantics_conflict"):
                replace_source(
                    root,
                    a.source_id,
                    c.source_id,
                    topic_id=topic,
                    relation_kind=RELATION_CORRECTION,
                )
            self.assertEqual(temporal_source_status(root, a.source_id, topic_id=topic)["superseded_by"], b.source_id)
            self.assertEqual({src.source_id for src in sources(root, topic_id=topic)}, {b.source_id, c.source_id})

    def test_change_requires_effective_at_before_any_relation_append(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            a, _ = ingest_file(root, self._write(base, "a.md", "A"), topic_id=topic, origin_id="origin-a")
            b, _ = ingest_file(root, self._write(base, "b.md", "B"), topic_id=topic, origin_id="origin-b")
            with self.assertRaisesRegex(ValueError, "change_effective_at_required"):
                replace_source(
                    root,
                    a.source_id,
                    b.source_id,
                    topic_id=topic,
                    relation_kind=RELATION_CHANGE,
                )
            self.assertEqual({src.source_id for src in sources(root, topic_id=topic)}, {a.source_id, b.source_id})


if __name__ == "__main__":
    unittest.main()
