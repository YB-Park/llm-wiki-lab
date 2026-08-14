from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.eventlog import verify_canonical_log_integrity
from dogfood.llm_wiki.provenance import PROVENANCE_FILE, bind_exact_raw_span
from dogfood.llm_wiki.store import ingest_file
from dogfood.llm_wiki.temporal import correct_source, dispute_sources


class CanonicalWriterIntegrationTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_source_temporal_dispute_and_provenance_writers_leave_committed_logs(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"

            a_text = "State alpha with exact evidence."
            a, _ = ingest_file(
                root,
                self._write(base, "a.md", a_text),
                topic_id=topic,
                origin_id="origin-a",
            )
            b, _ = ingest_file(
                root,
                self._write(base, "b.md", "State beta."),
                topic_id=topic,
                origin_id="origin-b",
            )
            c, _ = ingest_file(
                root,
                self._write(base, "c.md", "Independent state gamma."),
                topic_id=topic,
                origin_id="origin-c",
            )

            correct_source(root, a.source_id, b.source_id, topic_id=topic)
            dispute_sources(root, b.source_id, c.source_id, topic_id=topic)

            target = "exact evidence"
            start = a_text.index(target)
            bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=a.source_id,
                start=start,
                end=start + len(target),
                local_label="historical.a",
            )

            manifest = root / "manifest.jsonl"
            provenance = root / PROVENANCE_FILE
            self.assertTrue(manifest.read_bytes().endswith(b"\n"))
            self.assertTrue(provenance.read_bytes().endswith(b"\n"))

            report = verify_canonical_log_integrity(root)
            self.assertTrue(report.ok)
            self.assertEqual(report.manifest_records, 5)  # 3 ingest + correction + dispute
            self.assertEqual(report.provenance_records, 1)
            self.assertFalse(report.manifest_torn_tail)
            self.assertFalse(report.provenance_torn_tail)
            self.assertEqual(report.manifest_corrupt_records, 0)
            self.assertEqual(report.provenance_corrupt_records, 0)


if __name__ == "__main__":
    unittest.main()
