from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dogfood.llm_wiki.retrieval import search
from dogfood.llm_wiki.store import (
    find_source,
    history,
    ingest_file,
    source_status,
    sources,
    supersede_source,
)
from dogfood.llm_wiki.temporal import (
    RELATION_CHANGE,
    RELATION_CORRECTION,
    RELATION_GENERIC,
    change_source,
    correct_source,
    dispute_sources,
    replace_source,
    temporal_projection,
    temporal_source_status,
)


class E003TemporalSemanticsTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def _two_current_revisions(self, base: Path, root: Path, topic: str, *, origin: str = "origin-a"):
        a, _ = ingest_file(
            root,
            self._write(base, "a.md", "state alpha old value"),
            topic_id=topic,
            origin_id=origin,
        )
        b, _ = ingest_file(
            root,
            self._write(base, "b.md", "state beta new value"),
            topic_id=topic,
            origin_id=origin,
        )
        self.assertNotEqual(a.source_id, b.source_id)
        self.assertEqual({src.source_id for src in sources(root, topic_id=topic)}, {a.source_id, b.source_id})
        return a, b

    def test_legacy_generic_supersede_replays_as_generic_without_changing_old_api(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic")

            self.assertTrue(supersede_source(root, a.source_id, b.source_id, topic_id="topic"))
            self.assertFalse(supersede_source(root, a.source_id, b.source_id, topic_id="topic"))

            coarse = source_status(root, a.source_id, topic_id="topic")
            rich = temporal_source_status(root, a.source_id, topic_id="topic")
            self.assertEqual(coarse["status"], "superseded")
            self.assertEqual(coarse["superseded_by"], b.source_id)
            self.assertEqual(rich["status"], "superseded")
            self.assertEqual(rich["replacement_kind"], RELATION_GENERIC)
            self.assertIsNone(rich["effective_at"])
            self.assertEqual({src.source_id for src in sources(root, topic_id="topic")}, {b.source_id})
            self.assertEqual(
                {src.source_id for src in sources(root, topic_id="topic", include_superseded=True)},
                {a.source_id, b.source_id},
            )

    def test_explicit_generic_is_idempotent_and_cannot_be_relabelled(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic")
            self.assertTrue(replace_source(root, a.source_id, b.source_id, topic_id="topic"))
            before = list(history(root))
            self.assertFalse(replace_source(root, a.source_id, b.source_id, topic_id="topic"))
            self.assertEqual(history(root), before)
            with self.assertRaisesRegex(ValueError, "replacement_semantics_conflict"):
                correct_source(root, a.source_id, b.source_id, topic_id="topic")
            self.assertEqual(history(root), before)

    def test_correction_preserves_audit_but_makes_no_valid_time_claim(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic")
            self.assertTrue(correct_source(root, a.source_id, b.source_id, topic_id="topic"))
            self.assertFalse(correct_source(root, a.source_id, b.source_id, topic_id="topic"))

            old = temporal_source_status(root, a.source_id, topic_id="topic")
            new = temporal_source_status(root, b.source_id, topic_id="topic")
            self.assertEqual(old["status"], "superseded")
            self.assertEqual(old["replacement_kind"], RELATION_CORRECTION)
            self.assertIsNone(old["effective_at"])
            self.assertIsNone(new["valid_from"])
            self.assertEqual(new["status"], "current")
            self.assertEqual(find_source(root, a.source_id, topic_id="topic").source_id, a.source_id)

            relation = [row for row in history(root) if row.get("event") == "supersede"][-1]
            self.assertEqual(relation["relation_kind"], RELATION_CORRECTION)
            self.assertNotIn("effective_at", relation)

    def test_change_separates_effective_and_recorded_time_and_exposes_valid_from(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic")
            effective = "2025-03-04T05:06:07+09:00"
            self.assertTrue(change_source(root, a.source_id, b.source_id, topic_id="topic", effective_at=effective))
            canonical_effective = "2025-03-03T20:06:07+00:00"

            old = temporal_source_status(root, a.source_id, topic_id="topic")
            new = temporal_source_status(root, b.source_id, topic_id="topic")
            self.assertEqual(old["replacement_kind"], RELATION_CHANGE)
            self.assertEqual(old["effective_at"], canonical_effective)
            self.assertEqual(new["valid_from"], canonical_effective)
            recorded = datetime.fromisoformat(old["replacement_recorded_at"])
            valid = datetime.fromisoformat(old["effective_at"])
            self.assertGreater(recorded, valid)
            self.assertEqual(recorded.tzinfo, timezone.utc)
            self.assertEqual(valid.tzinfo, timezone.utc)

            before = list(history(root))
            self.assertFalse(change_source(root, a.source_id, b.source_id, topic_id="topic", effective_at=effective))
            self.assertEqual(history(root), before)
            with self.assertRaisesRegex(ValueError, "replacement_semantics_conflict"):
                change_source(
                    root,
                    a.source_id,
                    b.source_id,
                    topic_id="topic",
                    effective_at="2025-03-05T00:00:00+00:00",
                )
            self.assertEqual(history(root), before)

    def test_invalid_naive_future_and_nonchange_effective_times_fail_before_append(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic")
            baseline = list(history(root))

            bad = (
                ("not-a-time", "change_effective_at_invalid"),
                ("2025-01-01T00:00:00", "change_effective_at_must_be_timezone_aware"),
                ("2999-01-01T00:00:00+00:00", "future_change_not_supported"),
            )
            for value, message in bad:
                with self.assertRaisesRegex(ValueError, message):
                    change_source(root, a.source_id, b.source_id, topic_id="topic", effective_at=value)
                self.assertEqual(history(root), baseline)

            with self.assertRaisesRegex(ValueError, "effective_at_only_valid_for_change"):
                replace_source(
                    root,
                    a.source_id,
                    b.source_id,
                    topic_id="topic",
                    relation_kind=RELATION_CORRECTION,
                    effective_at="2025-01-01T00:00:00+00:00",
                )
            self.assertEqual(history(root), baseline)

    def test_disagreement_is_symmetric_current_and_has_no_hidden_winner(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic", origin="origin-shared")

            self.assertTrue(dispute_sources(root, b.source_id, a.source_id, topic_id="topic"))
            before = list(history(root))
            self.assertFalse(dispute_sources(root, a.source_id, b.source_id, topic_id="topic"))
            self.assertEqual(history(root), before)

            a_status = temporal_source_status(root, a.source_id, topic_id="topic")
            b_status = temporal_source_status(root, b.source_id, topic_id="topic")
            self.assertEqual(a_status["status"], "current")
            self.assertEqual(b_status["status"], "current")
            self.assertTrue(a_status["contested"])
            self.assertTrue(b_status["contested"])
            self.assertEqual(a_status["disputes_with"], [b.source_id])
            self.assertEqual(b_status["disputes_with"], [a.source_id])
            self.assertEqual({src.source_id for src in sources(root, topic_id="topic")}, {a.source_id, b.source_id})

            dispute_event = [row for row in history(root) if row.get("event") == "dispute"][-1]
            self.assertEqual(dispute_event["source_ids"], sorted([a.source_id, b.source_id]))

    def test_dispute_validation_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic")
            with self.assertRaisesRegex(ValueError, "dispute_self_reference"):
                dispute_sources(root, a.source_id, a.source_id, topic_id="topic")
            with self.assertRaisesRegex(ValueError, "dispute_source_not_found"):
                dispute_sources(root, a.source_id, "src-missing", topic_id="topic")

            correct_source(root, a.source_id, b.source_id, topic_id="topic")
            with self.assertRaisesRegex(ValueError, "dispute_source_not_current"):
                dispute_sources(root, a.source_id, b.source_id, topic_id="topic")

    def test_replacing_disputed_endpoint_ends_only_revision_pair_without_inheritance(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic", origin="origin-a")
            c, _ = ingest_file(
                root,
                self._write(base, "c.md", "state gamma corrected value"),
                topic_id="topic",
                origin_id="origin-c",
            )
            dispute_sources(root, a.source_id, b.source_id, topic_id="topic")
            self.assertTrue(temporal_source_status(root, a.source_id, topic_id="topic")["contested"])

            correct_source(root, a.source_id, c.source_id, topic_id="topic")
            projection = temporal_projection(root, topic_id="topic")
            self.assertEqual(projection.active_disputes, frozenset())
            self.assertFalse(temporal_source_status(root, b.source_id, topic_id="topic")["contested"])
            self.assertFalse(temporal_source_status(root, c.source_id, topic_id="topic")["contested"])
            self.assertEqual(projection.current_source_ids, frozenset({b.source_id, c.source_id}))

    def test_temporal_relations_are_topic_scoped(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            shared = self._write(base, "shared.md", "shared alpha state")
            a_a, _ = ingest_file(root, shared, topic_id="topic-a", origin_id="origin-a")
            a_b, _ = ingest_file(root, shared, topic_id="topic-b", origin_id="origin-a")
            # ADR-0004 separates byte identity from evidence-revision identity:
            # topic contexts may have distinct source IDs while sharing object ID.
            self.assertNotEqual(a_a.source_id, a_b.source_id)
            self.assertEqual(a_a.object_id, a_b.object_id)

            successor_path = self._write(base, "new.md", "shared beta state")
            b_a, _ = ingest_file(root, successor_path, topic_id="topic-a", origin_id="origin-b")
            b_b, _ = ingest_file(root, successor_path, topic_id="topic-b", origin_id="origin-b")
            self.assertNotEqual(b_a.source_id, b_b.source_id)
            self.assertEqual(b_a.object_id, b_b.object_id)

            correct_source(root, a_a.source_id, b_a.source_id, topic_id="topic-a")
            self.assertEqual(temporal_source_status(root, a_a.source_id, topic_id="topic-a")["status"], "superseded")
            self.assertEqual(temporal_source_status(root, a_b.source_id, topic_id="topic-b")["status"], "current")
            self.assertEqual(
                {src.source_id for src in sources(root, topic_id="topic-b")},
                {a_b.source_id, b_b.source_id},
            )
            self.assertEqual(temporal_projection(root, topic_id="topic-b").replacements, {})

    def test_recurrence_remains_possible_after_typed_relation_and_reuses_raw_object(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a_path = self._write(base, "state.md", "VALUE=A")
            a1, _ = ingest_file(root, a_path, topic_id="topic", origin_id="origin-state")
            b_path = self._write(base, "state-b.md", "VALUE=B")
            b, _ = ingest_file(root, b_path, topic_id="topic", origin_id="origin-state")
            correct_source(root, a1.source_id, b.source_id, topic_id="topic")

            # Existing ingest+supersedes remains the v1 recurrence constructor.
            a2, duplicate = ingest_file(
                root,
                a_path,
                topic_id="topic",
                origin_id="origin-state",
                supersedes_source_id=b.source_id,
            )
            self.assertNotEqual(a1.source_id, a2.source_id)
            self.assertEqual(a1.object_id, a2.object_id)
            self.assertTrue(duplicate)
            self.assertEqual({src.source_id for src in sources(root, topic_id="topic")}, {a2.source_id})
            self.assertEqual(
                {src.source_id for src in sources(root, topic_id="topic", include_superseded=True)},
                {a1.source_id, b.source_id, a2.source_id},
            )
            self.assertEqual(find_source(root, a1.source_id, topic_id="topic").object_id, a1.object_id)

    def test_default_retrieval_excludes_replacements_but_keeps_both_disputed_sources(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a, b = self._two_current_revisions(base, root, "topic", origin="origin-one")
            hits = search(root, "state value", topic_id="topic", top_k=8)
            self.assertEqual({hit.object_id for hit in hits}, {a.object_id, b.object_id})
            dispute_sources(root, a.source_id, b.source_id, topic_id="topic")
            disputed_hits = search(root, "state value", topic_id="topic", top_k=8)
            self.assertEqual({hit.object_id for hit in disputed_hits}, {a.object_id, b.object_id})

            correct_source(root, a.source_id, b.source_id, topic_id="topic")
            after = search(root, "state value", topic_id="topic", top_k=8)
            self.assertEqual([hit.object_id for hit in after], [b.object_id])


if __name__ == "__main__":
    unittest.main()
