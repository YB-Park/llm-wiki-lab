from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic, events
from dogfood.llm_wiki.cli import main as cli_main
from dogfood.llm_wiki.store import history


class E013PartialIngestTests(unittest.TestCase):
    def _invalid_utf8(self, path: Path) -> None:
        path.write_bytes(b"\xff\xfe\xfd")

    def test_first_success_then_failure_still_records_baseline_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = create_topic(root, "partial baseline")["topic_id"]
            good = base / "good.md"
            bad = base / "bad.bin"
            good.write_text("valid cedar evidence", encoding="utf-8")
            self._invalid_utf8(bad)

            with self.assertRaises(SystemExit) as cm:
                cli_main(["--root", str(root), "ingest", str(good), str(bad), "--topic", topic])
            self.assertIn("not_utf8_text", str(cm.exception))

            self.assertEqual(sum(row.get("event") == "ingest" for row in history(root)), 1)
            rows = events(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["event"], "cycle_start")
            self.assertEqual(rows[0]["kind"], "baseline")

    def test_authoritative_update_success_then_failure_records_exactly_one_update_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = create_topic(root, "partial update")["topic_id"]
            initial = base / "initial.md"
            update = base / "update.md"
            bad = base / "bad.bin"
            initial.write_text("initial state", encoding="utf-8")
            update.write_text("updated state", encoding="utf-8")
            self._invalid_utf8(bad)

            cli_main(["--root", str(root), "ingest", str(initial), "--topic", topic])
            with self.assertRaises(SystemExit):
                cli_main([
                    "--root",
                    str(root),
                    "ingest",
                    str(update),
                    str(bad),
                    "--topic",
                    topic,
                    "--authoritative-update",
                ])

            cycles = [row for row in events(root) if row.get("event") == "cycle_start"]
            self.assertEqual([row["kind"] for row in cycles], ["baseline", "authoritative_update"])
            self.assertEqual(sum(row.get("kind") == "authoritative_update" for row in cycles), 1)

    def test_all_success_multi_file_ingest_records_one_e013_event_for_command(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = create_topic(root, "multi success")["topic_id"]
            a = base / "a.md"
            b = base / "b.md"
            a.write_text("alpha evidence", encoding="utf-8")
            b.write_text("beta evidence", encoding="utf-8")

            cli_main(["--root", str(root), "ingest", str(a), str(b), "--topic", topic])

            self.assertEqual(sum(row.get("event") == "ingest" for row in history(root)), 2)
            rows = events(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["event"], "cycle_start")
            self.assertEqual(rows[0]["kind"], "baseline")


if __name__ == "__main__":
    unittest.main()
