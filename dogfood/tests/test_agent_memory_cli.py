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


if __name__ == "__main__":
    unittest.main()
