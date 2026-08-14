from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from dogfood.llm_wiki.jsonl_log import (
    append_jsonl_object,
    audit_canonical_logs,
    audit_jsonl,
    read_jsonl_objects,
)
from dogfood.llm_wiki.provenance import bind_exact_raw_span, provenance_history
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file, sources


class JsonlCrashContainmentTests(unittest.TestCase):
    def test_shared_append_is_newline_terminated_replayable_and_fsyncs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            with patch("dogfood.llm_wiki.jsonl_log.os.fsync") as fsync:
                append_jsonl_object(path, {"event": "alpha", "value": 1})
            self.assertTrue(path.read_bytes().endswith(b"\n"))
            self.assertEqual(read_jsonl_objects(path, log_name="fixture"), [{"event": "alpha", "value": 1}])
            fsync.assert_called_once()

    def test_manifest_torn_tail_preserves_prefix_count_but_blocks_semantic_replay_and_append(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "note.md"
            note.write_text("cedar evidence", encoding="utf-8")
            ingest_file(root, note, topic_id="topic")

            manifest = root / "manifest.jsonl"
            with manifest.open("ab") as handle:
                handle.write(b'{"event":"ingest"')

            report = audit_canonical_logs(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.manifest.status, "torn_tail")
            self.assertEqual(report.manifest.durable_records, 1)
            self.assertGreater(report.manifest.torn_tail_bytes, 0)
            self.assertEqual(report.manifest.corrupt_durable_records, 0)

            with self.assertRaisesRegex(RuntimeError, "^manifest_torn_tail$"):
                history(root)
            with self.assertRaisesRegex(RuntimeError, "^manifest_torn_tail$"):
                sources(root, topic_id="topic")
            with self.assertRaisesRegex(RuntimeError, "^jsonl_append_blocked_torn_tail$"):
                append_jsonl_object(manifest, {"event": "later"})

    def test_complete_json_without_final_newline_is_still_torn_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.jsonl"
            path.write_bytes(b'{"event":"one"}\n{"event":"two"}')
            report = audit_jsonl(path)
            self.assertEqual(report.status, "torn_tail")
            self.assertEqual(report.durable_records, 1)
            self.assertGreater(report.torn_tail_bytes, 0)
            with self.assertRaisesRegex(RuntimeError, "^manifest_torn_tail$"):
                read_jsonl_objects(path, log_name="manifest")

    def test_newline_terminated_invalid_json_inside_prefix_is_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.jsonl"
            path.write_bytes(b'{"event":"one"}\nnot-json\n{"event":"two"}\n')
            report = audit_jsonl(path)
            self.assertEqual(report.status, "corrupt_prefix")
            self.assertEqual(report.durable_records, 2)
            self.assertEqual(report.invalid_json_records, 1)
            self.assertEqual(report.corrupt_durable_records, 1)
            with self.assertRaisesRegex(RuntimeError, "^manifest_durable_prefix_corrupt$"):
                read_jsonl_objects(path, log_name="manifest")
            with self.assertRaisesRegex(RuntimeError, "^jsonl_append_blocked_corrupt_prefix$"):
                append_jsonl_object(path, {"event": "later"})

    def test_invalid_utf8_and_non_object_durable_records_are_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            utf8_path = base / "utf8.jsonl"
            utf8_path.write_bytes(b'{"event":"one"}\n\xff\n')
            utf8 = audit_jsonl(utf8_path)
            self.assertEqual(utf8.status, "corrupt_prefix")
            self.assertEqual(utf8.invalid_utf8_records, 1)

            object_path = base / "object.jsonl"
            object_path.write_bytes(b'[]\n')
            obj = audit_jsonl(object_path)
            self.assertEqual(obj.status, "corrupt_prefix")
            self.assertEqual(obj.non_object_records, 1)

    def test_prefix_corruption_has_priority_if_torn_tail_also_exists(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_bytes(b'{"event":"one"}\nnot-json\n{"event":"partial"')
            report = audit_jsonl(path)
            self.assertEqual(report.status, "corrupt_prefix")
            self.assertEqual(report.invalid_json_records, 1)
            self.assertGreater(report.torn_tail_bytes, 0)
            with self.assertRaisesRegex(RuntimeError, "^fixture_durable_prefix_corrupt$"):
                read_jsonl_objects(path, log_name="fixture")

    def test_provenance_torn_tail_blocks_history_without_hiding_durable_record(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "note.md"
            note.write_text("alpha cedar evidence omega", encoding="utf-8")
            source, _ = ingest_file(root, note, topic_id="topic")
            record, created = bind_exact_raw_span(
                root,
                topic_id="topic",
                source_id=source.source_id,
                start=6,
                end=11,
                local_label="claim-a",
            )
            self.assertTrue(created)
            self.assertEqual(len(provenance_history(root)), 1)

            path = root / "provenance.jsonl"
            with path.open("ab") as handle:
                handle.write(b'{"event":"bind_exact_raw_span"')

            report = audit_canonical_logs(root)
            self.assertEqual(report.provenance.status, "torn_tail")
            self.assertEqual(report.provenance.durable_records, 1)
            self.assertEqual(report.manifest.status, "clean")
            with self.assertRaisesRegex(RuntimeError, "^provenance_torn_tail$"):
                provenance_history(root)
            self.assertTrue(record.record_id.startswith("prov-"))

    def test_provenance_durable_prefix_corruption_is_distinct_from_tail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            path = root / "provenance.jsonl"
            path.write_bytes(b'{"event":"x"}\nnot-json\n')
            report = audit_canonical_logs(root)
            self.assertEqual(report.provenance.status, "corrupt_prefix")
            self.assertEqual(report.provenance.invalid_json_records, 1)
            self.assertEqual(report.provenance.torn_tail_bytes, 0)
            with self.assertRaisesRegex(RuntimeError, "^provenance_durable_prefix_corrupt$"):
                provenance_history(root)

    def test_legacy_manifest_blank_lines_and_source_replay_remain_compatible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            (root / "raw").mkdir(parents=True)
            data = b"legacy cedar evidence"
            sha = hashlib.sha256(data).hexdigest()
            (root / "raw" / f"{sha}.txt").write_bytes(data)
            event = {
                "event": "ingest",
                "recorded_at": "2026-08-14T00:00:00+00:00",
                "source_id": "src-legacy-evidence",
                "sha256": sha,
                "name": "legacy.md",
                "size_bytes": len(data),
            }
            (root / "manifest.jsonl").write_text(
                json.dumps(event, sort_keys=True) + "\n\n",
                encoding="utf-8",
            )

            self.assertEqual(history(root), [event])
            report = audit_canonical_logs(root)
            self.assertTrue(report.ok)
            self.assertEqual(report.manifest.blank_records, 1)
            visible = sources(root)
            self.assertEqual(len(visible), 1)
            self.assertTrue(visible[0].legacy)
            self.assertEqual(visible[0].object_id, f"obj-{sha}")
            self.assertEqual(visible[0].source_id, "src-legacy-evidence")

    def test_aggregate_audit_is_count_status_only(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "private-name.md"
            note.write_text("sensitive content token", encoding="utf-8")
            source, _ = ingest_file(root, note, topic_id="topic-private", origin_id="origin-private")
            bind_exact_raw_span(
                root,
                topic_id="topic-private",
                source_id=source.source_id,
                start=0,
                end=9,
                local_label="private-label",
            )

            payload = json.dumps(asdict(audit_canonical_logs(root)), sort_keys=True)
            for forbidden in (
                source.source_id,
                source.object_id,
                source.sha256,
                "private-name.md",
                "topic-private",
                "origin-private",
                "private-label",
                "sensitive content token",
            ):
                self.assertNotIn(forbidden, payload)
            self.assertIn('"status": "clean"', payload)
            self.assertIn('"durable_records"', payload)


if __name__ == "__main__":
    unittest.main()
