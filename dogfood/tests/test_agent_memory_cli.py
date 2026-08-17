from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.agent_memory_cli import HARD_MAX_CHARS, main
from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.store import ensure_workspace, ingest_file, supersede_source


class AgentMemoryCliTests(unittest.TestCase):
    def _wiki(self, text: str):
        temp = tempfile.TemporaryDirectory(prefix="agent-memory-cli-")
        base = Path(temp.name)
        root = base / "wiki"
        source_path = base / "source.md"
        source_path.write_text(text, encoding="utf-8")
        ensure_workspace(root)
        topic = create_topic(root, "agent-memory-topic")
        source, _ = ingest_file(root, source_path, topic_id=topic["topic_id"])
        return temp, base, root, topic, source

    def _run_json(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(args)
        self.assertEqual(code, 0)
        return json.loads(stdout.getvalue())

    def test_read_returns_verified_bounded_raw_text_with_pagination(self):
        temp, _base, root, topic, source = self._wiki("alpha beta gamma delta")
        self.addCleanup(temp.cleanup)
        row = self._run_json([
            "--root", str(root), "read", source.source_id,
            "--topic", topic["topic_id"], "--start-char", "6", "--max-chars", "10",
        ])
        self.assertEqual(row["format"], "llm-wiki-agent-raw-read-v0")
        self.assertEqual(row["source_id"], source.source_id)
        self.assertEqual(row["status"], "current")
        self.assertEqual(row["text"], "beta gamma")
        self.assertEqual(row["start_char"], 6)
        self.assertEqual(row["end_char"], 16)
        self.assertTrue(row["has_more"])
        self.assertEqual(row["total_chars"], len("alpha beta gamma delta"))

    def test_compare_returns_verified_change_window_for_human_lineage_review(self):
        temp, base, root, topic, old_source = self._wiki(
            "# Timeout policy\n\nThe cobalt timeout is 15 seconds.\nKeep retries bounded.\n"
        )
        self.addCleanup(temp.cleanup)
        newer_path = base / "newer.md"
        newer_path.write_text(
            "# Timeout policy\n\nThe cobalt timeout is now 20 seconds.\nKeep retries bounded.\n",
            encoding="utf-8",
        )
        new_source, _ = ingest_file(root, newer_path, topic_id=topic["topic_id"])

        row = self._run_json([
            "--root", str(root), "compare", old_source.source_id, new_source.source_id,
            "--topic", topic["topic_id"], "--context-chars", "24", "--max-change-chars", "80",
        ])
        self.assertEqual(row["format"], "llm-wiki-agent-raw-compare-v0")
        self.assertEqual(row["older_source_id"], old_source.source_id)
        self.assertEqual(row["newer_source_id"], new_source.source_id)
        self.assertEqual(row["older_status"], "current")
        self.assertEqual(row["newer_status"], "current")
        self.assertFalse(row["identical"])
        self.assertIn("15 seconds", row["old_excerpt"])
        self.assertIn("20 seconds", row["new_excerpt"])
        self.assertGreater(row["old_changed_chars"], 0)
        self.assertGreater(row["new_changed_chars"], 0)

    def test_compare_bounds_large_changed_region_without_hiding_that_it_was_truncated(self):
        temp, base, root, topic, old_source = self._wiki("prefix\n" + ("A" * 3000) + "\nsuffix\n")
        self.addCleanup(temp.cleanup)
        newer_path = base / "newer-large.md"
        newer_path.write_text("prefix\n" + ("B" * 3000) + "\nsuffix\n", encoding="utf-8")
        new_source, _ = ingest_file(root, newer_path, topic_id=topic["topic_id"])

        row = self._run_json([
            "--root", str(root), "compare", old_source.source_id, new_source.source_id,
            "--topic", topic["topic_id"], "--context-chars", "10", "--max-change-chars", "100",
        ])
        self.assertTrue(row["excerpt_truncated"])
        self.assertIn("CHANGED REGION TRUNCATED", row["old_excerpt"])
        self.assertIn("CHANGED REGION TRUNCATED", row["new_excerpt"])
        self.assertLess(len(row["old_excerpt"]), 300)
        self.assertLess(len(row["new_excerpt"]), 300)

    def test_read_surfaces_superseded_status_without_hiding_immutable_raw(self):
        temp, base, root, topic, source = self._wiki("old value")
        self.addCleanup(temp.cleanup)
        successor_path = base / "successor.md"
        successor_path.write_text("new value", encoding="utf-8")
        successor, _ = ingest_file(root, successor_path, topic_id=topic["topic_id"])
        supersede_source(root, source.source_id, successor.source_id, topic_id=topic["topic_id"])

        row = self._run_json([
            "--root", str(root), "read", source.source_id, "--topic", topic["topic_id"],
        ])
        self.assertEqual(row["status"], "superseded")
        self.assertEqual(row["superseded_by"], successor.source_id)
        self.assertEqual(row["text"], "old value")

    def test_invalid_bounds_fail_before_read(self):
        temp, _base, root, topic, source = self._wiki("bounded")
        self.addCleanup(temp.cleanup)
        with self.assertRaisesRegex(SystemExit, "start_char_must_be_nonnegative"):
            main(["--root", str(root), "read", source.source_id, "--topic", topic["topic_id"], "--start-char", "-1"])
        with self.assertRaisesRegex(SystemExit, "max_chars_must_be_1_to"):
            main(["--root", str(root), "read", source.source_id, "--topic", topic["topic_id"], "--max-chars", str(HARD_MAX_CHARS + 1)])
        with self.assertRaisesRegex(SystemExit, "context_chars_must_be_0_to"):
            main([
                "--root", str(root), "compare", source.source_id, source.source_id,
                "--topic", topic["topic_id"], "--context-chars", "999999",
            ])


if __name__ == "__main__":
    unittest.main()
