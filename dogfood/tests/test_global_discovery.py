from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.cli import main
from dogfood.llm_wiki.retrieval import search
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class GlobalDiscoveryTests(unittest.TestCase):
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

    def test_global_discovery_does_not_compare_topic_local_bm25_scores(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            large = create_topic(root, "large distractor corpus")
            small = create_topic(root, "small correct corpus")

            for index in range(80):
                self.make_source(
                    base,
                    root,
                    large["topic_id"],
                    f"large-{index:03d}.md",
                    f"background filler document number {index}",
                )
            self.make_source(base, root, large["topic_id"], "large-special.md", "splashdown")
            self.make_source(base, root, small["topic_id"], "small-answer.md", "launch orbit splashdown")

            query = "launch orbit splashdown"
            large_local = search(root, query, top_k=1, topic_id=large["topic_id"])
            small_local = search(root, query, top_k=1, topic_id=small["topic_id"])
            self.assertTrue(large_local and small_local)
            self.assertGreater(
                large_local[0].score,
                small_local[0].score,
                "fixture must reproduce the old cross-topic raw-score trap",
            )

            code, stdout = self.call(
                "--root",
                str(root),
                "discover",
                query,
                "--json",
                "--top-k-per-topic",
                "3",
            )
            self.assertEqual(code, 0)
            rows = [json.loads(line) for line in stdout.splitlines() if line.strip()]
            self.assertTrue(rows)
            self.assertEqual(rows[0]["topic_id"], small["topic_id"])
            self.assertEqual(rows[0]["name"], "small-answer.md")
            self.assertGreater(rows[0]["score"], rows[1]["score"])

    def test_global_discovery_stays_current_only_and_does_not_record_query_telemetry(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            alpha = create_topic(root, "alpha")
            beta = create_topic(root, "beta")
            old = self.make_source(base, root, alpha["topic_id"], "old.md", "obsolete zephyr marker")
            new = self.make_source(base, root, alpha["topic_id"], "new.md", "current cedar marker")
            self.call(
                "--root",
                str(root),
                "source",
                "supersede",
                old.source_id,
                new.source_id,
                "--topic",
                alpha["topic_id"],
            )
            self.make_source(base, root, beta["topic_id"], "beta.md", "current zephyr marker in beta")

            code, stdout = self.call("--root", str(root), "discover", "zephyr", "--json")
            self.assertEqual(code, 0)
            rows = [json.loads(line) for line in stdout.splitlines() if line.strip()]
            self.assertTrue(rows)
            self.assertTrue(all(row["topic_id"] == beta["topic_id"] for row in rows))
            self.assertTrue(all(row["source_id"] != old.source_id for row in rows))
            self.assertFalse((root / "workload-events.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
