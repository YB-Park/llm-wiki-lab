from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.cli import main
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class ProductCliTests(unittest.TestCase):
    def call(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(argv))
        return code, out.getvalue()

    def make_source(self, base: Path, root: Path, topic_id: str, name: str, text: str):
        path = base / name
        path.write_text(text, encoding="utf-8")
        source, _ = ingest_file(root, path, topic_id=topic_id)
        return source

    def test_discover_uses_each_topic_current_view_without_recording_query_telemetry(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            alpha = create_topic(root, "alpha")
            beta = create_topic(root, "beta")
            old = self.make_source(base, root, alpha["topic_id"], "old.md", "obsolete zephyr marker")
            new = self.make_source(base, root, alpha["topic_id"], "new.md", "current cedar marker")
            self.call("--root", str(root), "source", "supersede", old.source_id, new.source_id, "--topic", alpha["topic_id"])
            self.make_source(base, root, beta["topic_id"], "beta.md", "current zephyr marker in beta")

            code, stdout = self.call("--root", str(root), "discover", "zephyr", "--json")
            self.assertEqual(code, 0)
            rows = [json.loads(line) for line in stdout.splitlines() if line.strip()]
            self.assertTrue(rows)
            self.assertTrue(all(row["topic_id"] == beta["topic_id"] for row in rows))
            self.assertTrue(all(row["source_id"] != old.source_id for row in rows))
            events = root / "workload-events.jsonl"
            self.assertFalse(events.exists(), "discovery must not manufacture E013 visits")

    def test_typed_temporal_operations_are_exposed_by_cli(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            topic = create_topic(root, "temporal")
            a = self.make_source(base, root, topic["topic_id"], "a.md", "old incorrect value")
            b = self.make_source(base, root, topic["topic_id"], "b.md", "corrected value")

            code, stdout = self.call("--root", str(root), "source", "correct", a.source_id, b.source_id, "--topic", topic["topic_id"])
            self.assertEqual(code, 0)
            self.assertIn("CORRECTION", stdout)
            _, status = self.call("--root", str(root), "source", "status", a.source_id, "--topic", topic["topic_id"])
            row = json.loads(status)
            self.assertEqual(row["replacement_kind"], "correction")
            self.assertEqual(row["superseded_by"], b.source_id)

        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            topic = create_topic(root, "dispute")
            left = self.make_source(base, root, topic["topic_id"], "left.md", "claim left")
            right = self.make_source(base, root, topic["topic_id"], "right.md", "claim right")
            code, stdout = self.call("--root", str(root), "source", "dispute", left.source_id, right.source_id, "--topic", topic["topic_id"])
            self.assertEqual(code, 0)
            self.assertIn("DISPUTE", stdout)
            _, listed = self.call("--root", str(root), "source", "list", "--topic", topic["topic_id"], "--json")
            rows = [json.loads(line) for line in listed.splitlines() if line.strip()]
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row["contested"] for row in rows))

    def test_change_requires_and_preserves_effective_time(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            topic = create_topic(root, "change")
            a = self.make_source(base, root, topic["topic_id"], "before.md", "before state")
            b = self.make_source(base, root, topic["topic_id"], "after.md", "after state")
            effective = "2026-08-01T00:00:00+00:00"
            code, _ = self.call(
                "--root", str(root), "source", "change", a.source_id, b.source_id,
                "--topic", topic["topic_id"], "--effective-at", effective,
            )
            self.assertEqual(code, 0)
            _, status = self.call("--root", str(root), "source", "status", a.source_id, "--topic", topic["topic_id"])
            row = json.loads(status)
            self.assertEqual(row["replacement_kind"], "change")
            self.assertEqual(row["effective_at"], effective)


if __name__ == "__main__":
    unittest.main()
