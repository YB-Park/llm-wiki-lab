from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dogfood.llm_wiki.calibration import (
    create_topic,
    events,
    record_ingest,
    record_query,
    record_source_open,
    sanitized_json,
    summarize,
)
from dogfood.llm_wiki.retrieval import search
from dogfood.llm_wiki.store import ingest_file


UTC = timezone.utc


def ts(hour: int, minute: int) -> datetime:
    return datetime(2026, 8, 14, hour, minute, tzinfo=UTC)


class E013CalibrationTests(unittest.TestCase):
    def test_sessionizes_commands_into_visits_and_excludes_active_cycle_from_primary_distribution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            topic = create_topic(root, "Secret Project Name")
            tid = topic["topic_id"]

            self.assertEqual(record_ingest(root, tid, recorded_at=ts(0, 0)), "baseline")
            record_query(root, tid, "search", "exact_provenance", recorded_at=ts(0, 5))
            record_query(root, tid, "context", "exact_provenance", recorded_at=ts(0, 20))
            record_source_open(root, tid, recorded_at=ts(0, 25))
            record_query(root, tid, "ask", "synthesis", recorded_at=ts(0, 51))  # >30m after prior query
            self.assertEqual(
                record_ingest(root, tid, authoritative_update=True, recorded_at=ts(2, 0)),
                "authoritative_update",
            )
            record_query(root, tid, "search", "decision_history", recorded_at=ts(2, 10))

            out = summarize(root)
            self.assertEqual(out["completed_cycles"], 1)
            self.assertEqual(out["right_censored_active_cycles"], 1)
            self.assertEqual(out["total_visits"], 3)
            self.assertEqual(out["completed_cycle_revisits"]["median"], 2)
            self.assertEqual(out["completed_cycle_revisits"]["fraction_ge_3"], 0.0)
            self.assertEqual(out["provenance_follow"]["visits_followed"], 1)
            self.assertEqual(out["query_events"]["counts"]["exact_provenance"], 2)
            self.assertEqual(out["query_events"]["counts"]["synthesis"], 1)
            self.assertEqual(out["query_events"]["counts"]["decision_history"], 1)
            self.assertEqual(out["status"], "INSUFFICIENT_CALIBRATION_DATA")

    def test_exactly_30_minutes_stays_one_visit_but_more_than_30_starts_another(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            tid = create_topic(root, "Topic A")["topic_id"]
            record_ingest(root, tid, recorded_at=ts(0, 0))
            record_query(root, tid, "search", recorded_at=ts(0, 5))
            record_query(root, tid, "context", recorded_at=ts(0, 35))
            record_query(root, tid, "search", recorded_at=ts(1, 6))
            record_ingest(root, tid, authoritative_update=True, recorded_at=ts(2, 0))

            out = summarize(root)
            self.assertEqual(out["completed_cycle_revisits"]["median"], 2)

    def test_sanitized_export_contains_no_topic_or_provenance_identity_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            row = create_topic(root, "Highly Sensitive Human Label")
            tid = row["topic_id"]
            evidence = base / "private-note.md"
            evidence.write_text("private evidence text", encoding="utf-8")
            source, _ = ingest_file(root, evidence, topic_id=tid, origin_id="origin-secret-token")
            record_ingest(root, tid, recorded_at=ts(0, 0))
            record_query(root, tid, "search", "other", recorded_at=ts(0, 5))

            raw_events_text = json.dumps(events(root), ensure_ascii=False)
            self.assertNotIn("query_text", raw_events_text)
            self.assertNotIn("Highly Sensitive Human Label", raw_events_text)

            exported = sanitized_json(root)
            for forbidden in (
                "Highly Sensitive Human Label",
                tid,
                source.source_id,
                source.object_id,
                source.sha256,
                "origin-secret-token",
                "private-note.md",
                "private evidence text",
                "source_id",
                "object_id",
                "origin_id",
                "sha256",
                "recorded_at",
            ):
                self.assertNotIn(forbidden, exported)

    def test_topic_scoped_retrieval_never_crosses_topic_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            t1 = create_topic(root, "one")["topic_id"]
            t2 = create_topic(root, "two")["topic_id"]
            a = base / "a.md"
            b = base / "b.md"
            a.write_text("amber cache decision", encoding="utf-8")
            b.write_text("amber cache unrelated other topic", encoding="utf-8")
            sa, _ = ingest_file(root, a, topic_id=t1)
            sb, _ = ingest_file(root, b, topic_id=t2)

            one = search(root, "amber cache", topic_id=t1)
            two = search(root, "amber cache", topic_id=t2)
            self.assertEqual([h.source.source_id for h in one], [sa.source_id])
            self.assertEqual([h.source.source_id for h in two], [sb.source_id])

    def test_ordinary_ingest_does_not_create_fake_maintenance_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            tid = create_topic(root, "Topic B")["topic_id"]
            self.assertEqual(record_ingest(root, tid, recorded_at=ts(0, 0)), "baseline")
            self.assertEqual(record_ingest(root, tid, recorded_at=ts(0, 10)), "evidence_ingest")
            self.assertEqual(record_ingest(root, tid, recorded_at=ts(0, 20)), "evidence_ingest")
            out = summarize(root)
            self.assertEqual(out["completed_cycles"], 0)
            self.assertEqual(out["right_censored_active_cycles"], 1)


if __name__ == "__main__":
    unittest.main()
