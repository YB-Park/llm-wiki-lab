from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from dogfood.llm_wiki.eventlog import (
    append_jsonl_record,
    inspect_jsonl,
    read_jsonl_records,
    verify_canonical_log_integrity,
)
from dogfood.llm_wiki.provenance import (
    PROVENANCE_FILE,
    bind_exact_raw_span,
    provenance_history,
    resolve_exact_raw_span,
)
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file
from dogfood.llm_wiki.temporal import correct_source, dispute_sources


class CanonicalEventLogIntegrityTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def _ingest(self, base: Path, root: Path, topic: str, name: str, text: str, origin: str):
        return ingest_file(
            root,
            self._write(base, name, text),
            topic_id=topic,
            origin_id=origin,
        )[0]

    def test_valid_append_is_newline_terminated_readable_and_fsynced(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            row = {"event": "fixture", "value": 7}
            with patch("dogfood.llm_wiki.eventlog.os.fsync") as fsync:
                append_jsonl_record(path, row, log_label="fixture")
            self.assertTrue(path.read_bytes().endswith(b"\n"))
            self.assertEqual(read_jsonl_records(path, log_label="fixture"), [row])
            self.assertEqual(inspect_jsonl(path).complete_records, 1)
            fsync.assert_called_once()

    def test_valid_legacy_manifest_replays_unchanged_when_durably_newline_terminated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            row = {
                "event": "ingest",
                "recorded_at": "2025-01-01T00:00:00+00:00",
                "source_id": "src-legacy-fixture",
                "sha256": "0" * 64,
                "name": "legacy.md",
                "size_bytes": 0,
                "duplicate_content": False,
                "topic_id": "topic",
            }
            (root / "manifest.jsonl").write_bytes((json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))
            self.assertEqual(history(root), [row])

    def test_torn_manifest_tail_reports_valid_prefix_but_semantic_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            committed = {"event": "fixture", "value": 1}
            manifest = root / "manifest.jsonl"
            manifest.write_bytes(
                (json.dumps(committed, sort_keys=True) + "\n").encode("utf-8")
                + b'{"event":'
            )

            integrity = inspect_jsonl(manifest)
            self.assertEqual(integrity.complete_records, 1)
            self.assertTrue(integrity.torn_tail)
            self.assertEqual(integrity.corrupt_records, 0)
            self.assertFalse(integrity.ok)
            with self.assertRaisesRegex(RuntimeError, "manifest_torn_tail"):
                history(root)

    def test_valid_json_final_record_without_newline_is_still_uncommitted_torn_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            first = {"event": "first"}
            second = {"event": "second"}
            path.write_bytes(
                (json.dumps(first, sort_keys=True) + "\n").encode("utf-8")
                + json.dumps(second, sort_keys=True).encode("utf-8")
            )
            integrity = inspect_jsonl(path)
            self.assertEqual(integrity.complete_records, 1)
            self.assertTrue(integrity.torn_tail)
            self.assertEqual(integrity.corrupt_records, 0)
            with self.assertRaisesRegex(RuntimeError, "fixture_torn_tail"):
                read_jsonl_records(path, log_label="fixture")

    def test_corrupt_newline_terminated_interior_record_is_not_torn_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_bytes(
                b'{"event":"first"}\n'
                b'{not-json}\n'
                b'{"event":"third"}\n'
            )
            integrity = inspect_jsonl(path)
            self.assertEqual(integrity.complete_records, 2)
            self.assertFalse(integrity.torn_tail)
            self.assertEqual(integrity.corrupt_records, 1)
            self.assertFalse(integrity.ok)
            with self.assertRaisesRegex(RuntimeError, "fixture_corrupt_record"):
                read_jsonl_records(path, log_label="fixture")

    def test_non_object_and_invalid_utf8_complete_lines_are_corrupt_records(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_bytes(b'[]\n\xff\n')
            integrity = inspect_jsonl(path)
            self.assertEqual(integrity.complete_records, 0)
            self.assertFalse(integrity.torn_tail)
            self.assertEqual(integrity.corrupt_records, 2)
            with self.assertRaisesRegex(RuntimeError, "fixture_corrupt_record"):
                read_jsonl_records(path, log_label="fixture")

    def test_append_refuses_torn_or_corrupt_existing_log_without_changing_bytes(self):
        fixtures = (
            (b'{"event":"ok"}\n{"event":', "fixture_torn_tail"),
            (b'{"event":"ok"}\n{bad}\n', "fixture_corrupt_record"),
        )
        for original, error in fixtures:
            with self.subTest(error=error), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "events.jsonl"
                path.write_bytes(original)
                with self.assertRaisesRegex(RuntimeError, error):
                    append_jsonl_record(path, {"event": "new"}, log_label="fixture")
                self.assertEqual(path.read_bytes(), original)

    def test_source_ingest_and_temporal_mutation_refuse_torn_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            a = self._ingest(base, root, topic, "a.md", "state alpha", "origin-a")
            b = self._ingest(base, root, topic, "b.md", "state beta", "origin-b")
            manifest = root / "manifest.jsonl"
            manifest.write_bytes(manifest.read_bytes() + b'{"event":')
            before = manifest.read_bytes()

            with self.assertRaisesRegex(RuntimeError, "manifest_torn_tail"):
                ingest_file(
                    root,
                    self._write(base, "c.md", "state gamma"),
                    topic_id=topic,
                    origin_id="origin-c",
                )
            with self.assertRaisesRegex(RuntimeError, "manifest_torn_tail"):
                correct_source(root, a.source_id, b.source_id, topic_id=topic)
            with self.assertRaisesRegex(RuntimeError, "manifest_torn_tail"):
                dispute_sources(root, a.source_id, b.source_id, topic_id=topic)
            self.assertEqual(manifest.read_bytes(), before)

    def test_torn_and_corrupt_provenance_logs_fail_provenance_semantics_closed(self):
        cases = (
            (lambda data: data + b'{"event":', "provenance_torn_tail"),
            (lambda data: data + b'{bad}\n', "provenance_corrupt_record"),
        )
        for mutate, error in cases:
            with self.subTest(error=error), tempfile.TemporaryDirectory() as td:
                base = Path(td)
                root = base / "wiki"
                topic = "topic"
                text = "prefix exact evidence suffix"
                source = self._ingest(base, root, topic, "a.md", text, "origin-a")
                target = "exact evidence"
                start = text.index(target)
                record, _ = bind_exact_raw_span(
                    root,
                    topic_id=topic,
                    source_id=source.source_id,
                    start=start,
                    end=start + len(target),
                    local_label="claim.a",
                )
                path = root / PROVENANCE_FILE
                path.write_bytes(mutate(path.read_bytes()))
                before = path.read_bytes()

                with self.assertRaisesRegex(RuntimeError, error):
                    provenance_history(root)
                with self.assertRaisesRegex(RuntimeError, error):
                    resolve_exact_raw_span(root, record.record_id, topic_id=topic)
                with self.assertRaisesRegex(RuntimeError, error):
                    bind_exact_raw_span(
                        root,
                        topic_id=topic,
                        source_id=source.source_id,
                        start=start,
                        end=start + len(target),
                        local_label="claim.b",
                    )
                self.assertEqual(path.read_bytes(), before)

    def test_canonical_log_audit_is_read_only_aggregate_and_distinguishes_logs(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "private-topic"
            source = self._ingest(
                base, root, topic, "private.md", "private source material", "private-origin"
            )
            record, _ = bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=source.source_id,
                start=0,
                end=7,
                local_label="PRIVATE_LABEL_91",
            )
            manifest = root / "manifest.jsonl"
            provenance = root / PROVENANCE_FILE
            manifest_before = manifest.read_bytes()
            provenance_before = provenance.read_bytes()

            report = verify_canonical_log_integrity(root)
            payload = json.dumps(asdict(report), sort_keys=True)
            self.assertTrue(report.ok)
            self.assertEqual(report.manifest_records, 1)
            self.assertEqual(report.provenance_records, 1)
            self.assertFalse(report.manifest_torn_tail)
            self.assertFalse(report.provenance_torn_tail)
            self.assertEqual(report.manifest_corrupt_records, 0)
            self.assertEqual(report.provenance_corrupt_records, 0)
            self.assertEqual(manifest.read_bytes(), manifest_before)
            self.assertEqual(provenance.read_bytes(), provenance_before)

            self.assertEqual(
                set(asdict(report)),
                {
                    "manifest_records", "manifest_torn_tail", "manifest_corrupt_records",
                    "provenance_records", "provenance_torn_tail", "provenance_corrupt_records", "ok",
                },
            )
            self.assertNotIn(topic, payload)
            self.assertNotIn(source.source_id, payload)
            self.assertNotIn(record.record_id, payload)
            self.assertNotIn("PRIVATE_LABEL_91", payload)
            self.assertNotIn("private-origin", payload)
            self.assertNotIn("private source material", payload)

    def test_audit_reports_torn_and_corrupt_without_repairing_either_log(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            manifest = root / "manifest.jsonl"
            provenance = root / PROVENANCE_FILE
            manifest.write_bytes(b'{"event":"ok"}\n{"event":')
            provenance.write_bytes(b'{bad}\n')
            manifest_before = manifest.read_bytes()
            provenance_before = provenance.read_bytes()

            report = verify_canonical_log_integrity(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.manifest_records, 1)
            self.assertTrue(report.manifest_torn_tail)
            self.assertEqual(report.manifest_corrupt_records, 0)
            self.assertEqual(report.provenance_records, 0)
            self.assertFalse(report.provenance_torn_tail)
            self.assertEqual(report.provenance_corrupt_records, 1)
            self.assertEqual(manifest.read_bytes(), manifest_before)
            self.assertEqual(provenance.read_bytes(), provenance_before)


if __name__ == "__main__":
    unittest.main()
