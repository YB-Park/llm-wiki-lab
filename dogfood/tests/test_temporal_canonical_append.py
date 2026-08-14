from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dogfood.llm_wiki.store import history, ingest_file
from dogfood.llm_wiki.temporal import correct_source, dispute_sources


class TemporalCanonicalAppendTests(unittest.TestCase):
    def test_correction_uses_canonical_append_and_fsync(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            old_note = base / "old.md"
            new_note = base / "new.md"
            old_note.write_text("old cedar decision", encoding="utf-8")
            new_note.write_text("corrected cedar decision", encoding="utf-8")
            old_source, _ = ingest_file(root, old_note, topic_id="topic")
            new_source, _ = ingest_file(root, new_note, topic_id="topic")

            with patch("dogfood.llm_wiki.jsonl_log.os.fsync") as fsync:
                created = correct_source(
                    root,
                    old_source.source_id,
                    new_source.source_id,
                    topic_id="topic",
                )

            self.assertTrue(created)
            fsync.assert_called_once()
            self.assertTrue((root / "manifest.jsonl").read_bytes().endswith(b"\n"))
            event = history(root)[-1]
            self.assertEqual(event["event"], "supersede")
            self.assertEqual(event["relation_kind"], "correction")

    def test_dispute_uses_canonical_append_and_fsync(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            left_note = base / "left.md"
            right_note = base / "right.md"
            left_note.write_text("cedar option left", encoding="utf-8")
            right_note.write_text("cedar option right", encoding="utf-8")
            left_source, _ = ingest_file(root, left_note, topic_id="topic")
            right_source, _ = ingest_file(root, right_note, topic_id="topic")

            with patch("dogfood.llm_wiki.jsonl_log.os.fsync") as fsync:
                created = dispute_sources(
                    root,
                    left_source.source_id,
                    right_source.source_id,
                    topic_id="topic",
                )

            self.assertTrue(created)
            fsync.assert_called_once()
            self.assertTrue((root / "manifest.jsonl").read_bytes().endswith(b"\n"))
            event = history(root)[-1]
            self.assertEqual(event["event"], "dispute")
            self.assertEqual(event["source_ids"], sorted([left_source.source_id, right_source.source_id]))


if __name__ == "__main__":
    unittest.main()
