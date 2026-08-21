from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.agent_memory_cli import main
from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class RelevantRegionReadTests(unittest.TestCase):
    def _run_json(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(args)
        self.assertEqual(code, 0)
        return json.loads(stdout.getvalue())

    def test_relevant_read_finds_load_bearing_text_beyond_first_six_thousand_chars(self):
        temp = tempfile.TemporaryDirectory(prefix="agent-memory-relevant-")
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        root = base / "wiki"
        source_path = base / "long.md"
        prefix = "intro filler paragraph\n\n" + ("x" * 7200) + "\n\n"
        decision = "Nimbus ownership decision\n\nMateo Ruiz is the current Nimbus owner because the service roster is authoritative.\n"
        source_path.write_text(prefix + decision, encoding="utf-8")
        ensure_workspace(root)
        topic = create_topic(root, "Nimbus")
        source, _ = ingest_file(root, source_path, topic_id=topic["topic_id"])

        row = self._run_json([
            "--root", str(root), "relevant", source.source_id,
            "--topic", topic["topic_id"],
            "--query", "Who is the current Nimbus owner?",
            "--max-chars", "6000",
        ])
        self.assertEqual(row["format"], "llm-wiki-agent-relevant-read-v0")
        self.assertEqual(row["source_id"], source.source_id)
        self.assertGreater(row["start_char"], 0)
        self.assertIn("Mateo Ruiz is the current Nimbus owner", row["text"])
        self.assertTrue(row["has_more_before"])
        self.assertFalse(row["has_more_after"])

    def test_relevant_read_is_bounded_and_reports_omitted_sides(self):
        temp = tempfile.TemporaryDirectory(prefix="agent-memory-relevant-bounds-")
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        root = base / "wiki"
        source_path = base / "long.md"
        source_path.write_text(
            ("a" * 5000) + "\n\nTarget policy says cobalt timeout is 15 seconds.\n\n" + ("z" * 5000),
            encoding="utf-8",
        )
        ensure_workspace(root)
        topic = create_topic(root, "Timeout")
        source, _ = ingest_file(root, source_path, topic_id=topic["topic_id"])

        row = self._run_json([
            "--root", str(root), "relevant", source.source_id,
            "--topic", topic["topic_id"],
            "--query", "cobalt timeout",
            "--max-chars", "1000",
        ])
        self.assertLessEqual(len(row["text"]), 1000)
        self.assertIn("cobalt timeout is 15 seconds", row["text"])
        self.assertTrue(row["has_more_before"])
        self.assertTrue(row["has_more_after"])


if __name__ == "__main__":
    unittest.main()
