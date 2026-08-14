from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.cli import main as cli_main
from dogfood.llm_wiki.shadow import RetrievalShadowObservation, compare_retrieval_modes
from dogfood.llm_wiki.shadow_calibration import (
    SHADOW_EVENTS_FILE,
    record_retrieval_shadow,
    record_retrieval_shadow_failure,
    summarize_shadow,
)
from dogfood.llm_wiki.store import ingest_file


class E015ShadowCalibrationTests(unittest.TestCase):
    def _seed_topic(self, base: Path, root: Path, label: str = "Topic") -> tuple[str, Path]:
        topic = create_topic(root, label)
        note = base / f"{label}.md"
        note.write_text(
            "archive filler\n\ncedar quota cedar quota concentrated evidence\n\nsentinel completes the span\n\nrelease filler",
            encoding="utf-8",
        )
        ingest_file(root, note, topic_id=topic["topic_id"], origin_id=f"origin-{label.lower()}")
        return topic["topic_id"], note

    def test_comparison_object_contains_only_nonidentifying_features(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic_id, _ = self._seed_topic(base, root)
            obs = compare_retrieval_modes(
                root,
                "cedar quota sentinel",
                topic_id=topic_id,
                top_k=8,
                snippet_chars=1200,
            )
            fields = obs.as_telemetry_fields()
            self.assertEqual(
                set(fields),
                {
                    "default_count",
                    "candidate_count",
                    "top1_same",
                    "ordered_same",
                    "overlap_count",
                    "default_only_count",
                    "candidate_only_count",
                    "default_context_chars",
                    "candidate_context_chars",
                },
            )
            self.assertNotIn("query", fields)
            self.assertNotIn("source_id", fields)
            self.assertNotIn("object_id", fields)
            self.assertNotIn("path", fields)

    def test_shadow_event_schema_never_persists_query_or_evidence_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            obs = RetrievalShadowObservation(
                default_count=3,
                candidate_count=4,
                top1_same=False,
                ordered_same=False,
                overlap_count=2,
                default_only_count=1,
                candidate_only_count=2,
                default_context_chars=333,
                candidate_context_chars=444,
            )
            record_retrieval_shadow(root, "topic-opaque", "search", obs, "synthesis")
            row = json.loads((root / SHADOW_EVENTS_FILE).read_text(encoding="utf-8").strip())
            self.assertEqual(row["event"], "retrieval_shadow")
            forbidden = {
                "query",
                "query_text",
                "query_hash",
                "source_id",
                "source_ids",
                "object_id",
                "origin_id",
                "name",
                "path",
                "sha256",
                "snippet",
                "answer",
                "error",
                "exception",
                "stack",
            }
            self.assertTrue(forbidden.isdisjoint(row.keys()))

    def test_shadow_failure_is_detail_free_and_does_not_count_toward_readiness(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            record_retrieval_shadow_failure(root, "topic-opaque", "context", "other")
            row = json.loads((root / SHADOW_EVENTS_FILE).read_text(encoding="utf-8").strip())
            self.assertEqual(
                set(row),
                {"event", "format", "topic_id", "operation", "recorded_at", "query_class"},
            )
            summary = summarize_shadow(root)
            self.assertEqual(summary["shadow_query_events"], 0)
            self.assertEqual(summary["shadow_failures"]["total"], 1)
            self.assertEqual(summary["status"], "INSUFFICIENT_SHADOW_DATA")

    def test_cli_shadow_failure_cannot_break_visible_w0_or_persist_exception_text(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic_id, _ = self._seed_topic(base, root)

            output = io.StringIO()
            with patch(
                "dogfood.llm_wiki.cli.compare_retrieval_modes",
                side_effect=RuntimeError("SECRET_QUERY_TEXT /Users/alice/private/source.md obj-secret"),
            ):
                with redirect_stdout(output):
                    rc = cli_main([
                        "--root",
                        str(root),
                        "search",
                        "cedar quota sentinel",
                        "--topic",
                        topic_id,
                    ])
            self.assertEqual(rc, 0)
            self.assertIn("score=", output.getvalue())

            raw_shadow = (root / SHADOW_EVENTS_FILE).read_text(encoding="utf-8")
            self.assertNotIn("SECRET_QUERY_TEXT", raw_shadow)
            self.assertNotIn("/Users/alice", raw_shadow)
            self.assertNotIn("obj-secret", raw_shadow)
            self.assertEqual(summarize_shadow(root)["shadow_failures"]["total"], 1)

    def test_readiness_requires_events_topics_and_independent_visits(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            obs = RetrievalShadowObservation(3, 3, True, True, 3, 0, 0, 300, 330)
            start = datetime(2026, 8, 1, tzinfo=timezone.utc)

            # 50 events across 10 topics and exactly 30 visits. Within-visit
            # repeats are five minutes apart; new visits are >30 minutes apart.
            event_count = 0
            for topic_index in range(10):
                tid = f"topic-{topic_index}"
                for visit_index in range(3):
                    visit_start = start + timedelta(days=topic_index, hours=visit_index * 2)
                    repeats = 2 if event_count < 20 else 1
                    for repeat in range(repeats):
                        record_retrieval_shadow(
                            root,
                            tid,
                            "search",
                            obs,
                            recorded_at=visit_start + timedelta(minutes=5 * repeat),
                        )
                        event_count += 1
            # The construction above yields 50 events: 20 visits with two
            # events, then 10 visits with one event.
            self.assertEqual(event_count, 50)
            summary = summarize_shadow(root)
            self.assertEqual(summary["shadow_query_events"], 50)
            self.assertEqual(summary["topics_with_shadow_activity"], 10)
            self.assertEqual(summary["shadow_topic_visits"], 30)
            self.assertEqual(summary["status"], "SHADOW_CALIBRATION_READY")

    def test_calibration_export_adds_shadow_aggregate_without_ids_or_queries(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic_id, _ = self._seed_topic(base, root)
            with redirect_stdout(io.StringIO()):
                cli_main([
                    "--root",
                    str(root),
                    "search",
                    "cedar quota sentinel",
                    "--topic",
                    topic_id,
                    "--class",
                    "decision_history",
                ])

            output = io.StringIO()
            with redirect_stdout(output):
                rc = cli_main(["--root", str(root), "calibration", "export"])
            self.assertEqual(rc, 0)
            aggregate = json.loads(output.getvalue())
            self.assertIn("retrieval_shadow", aggregate)
            shadow = aggregate["retrieval_shadow"]
            self.assertEqual(shadow["shadow_query_events"], 1)
            serialized = json.dumps(shadow, sort_keys=True)
            self.assertNotIn(topic_id, serialized)
            self.assertNotIn("cedar quota sentinel", serialized)
            self.assertNotIn("source_id", serialized)
            self.assertNotIn("object_id", serialized)
            self.assertNotIn("sha256", serialized)


if __name__ == "__main__":
    unittest.main()
