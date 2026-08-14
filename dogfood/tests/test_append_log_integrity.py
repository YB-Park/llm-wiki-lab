from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dogfood.llm_wiki.append_log import (
    LOG_CLEAN,
    LOG_CORRUPT_PREFIX,
    LOG_TORN_TAIL,
    JsonlCorruptPrefixError,
    JsonlTornTailError,
    append_jsonl_record,
    discard_torn_tail,
    inspect_jsonl,
    read_committed_jsonl,
    verify_canonical_log_integrity,
)
from dogfood.llm_wiki.provenance import bind_exact_raw_span, provenance_history
from dogfood.llm_wiki.store import history, ingest_file, sources


class AppendLogIntegrityTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def _ingest(self, base: Path, root: Path, name: str, text: str):
        return ingest_file(
            root,
            self._write(base, name, text),
            topic_id="topic",
            origin_id=f"origin-{name.replace('.', '-')}",
        )[0]

    def test_shared_writer_newline_commits_and_fsyncs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            with patch("dogfood.llm_wiki.append_log.os.fsync") as fsync:
                append_jsonl_record(path, {"event": "one", "value": "한글"})
            self.assertTrue(path.read_bytes().endswith(b"\n"))
            self.assertGreaterEqual(fsync.call_count, 1)
            self.assertEqual(read_committed_jsonl(path), [{"event": "one", "value": "한글"}])
            self.assertEqual(inspect_jsonl(path).status, LOG_CLEAN)

    def test_blank_legacy_lines_remain_ignored_without_changing_replay(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_bytes(b'{"event":"a"}\n\n  \n{"event":"b"}\n')
            report = inspect_jsonl(path)
            self.assertEqual(report.status, LOG_CLEAN)
            self.assertEqual(report.committed_records, 2)
            self.assertEqual(report.blank_lines, 2)
            self.assertEqual(read_committed_jsonl(path), [{"event": "a"}, {"event": "b"}])

    def test_manifest_partial_final_append_fails_closed_until_explicit_discard(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            first = self._ingest(base, root, "a.md", "alpha evidence")
            prefix = history(root)
            manifest = root / "manifest.jsonl"
            before = manifest.read_bytes()
            with manifest.open("ab") as handle:
                handle.write(b'{"event":"supersede","topic_id":"topic"')

            report = inspect_jsonl(manifest)
            self.assertEqual(report.status, LOG_TORN_TAIL)
            self.assertEqual(report.committed_records, len(prefix))
            self.assertGreater(report.torn_tail_bytes, 0)
            with self.assertRaises(JsonlTornTailError):
                history(root)
            with self.assertRaises(JsonlTornTailError):
                sources(root, topic_id="topic")
            with self.assertRaises(JsonlTornTailError):
                append_jsonl_record(manifest, {"event": "must-not-append"})

            discarded = discard_torn_tail(manifest)
            self.assertGreater(discarded, 0)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertEqual(history(root), prefix)
            self.assertEqual(inspect_jsonl(manifest).status, LOG_CLEAN)

            retried, _ = ingest_file(
                root,
                self._write(base, "a-retry.md", "alpha evidence"),
                topic_id="topic",
                origin_id="origin-a-md",
            )
            self.assertEqual(retried.source_id, first.source_id)

    def test_complete_json_without_newline_is_still_uncommitted_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            append_jsonl_record(path, {"event": "committed"})
            committed = path.read_bytes()
            with path.open("ab") as handle:
                handle.write(json.dumps({"event": "looks-complete"}, sort_keys=True).encode("utf-8"))

            report = inspect_jsonl(path)
            self.assertEqual(report.status, LOG_TORN_TAIL)
            self.assertEqual(report.committed_records, 1)
            with self.assertRaises(JsonlTornTailError):
                read_committed_jsonl(path)

            discard_torn_tail(path)
            self.assertEqual(path.read_bytes(), committed)
            self.assertEqual(read_committed_jsonl(path), [{"event": "committed"}])

    def test_invalid_utf8_tail_is_torn_but_committed_invalid_utf8_is_corrupt_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            tail_path = base / "tail.jsonl"
            tail_path.write_bytes(b'{"event":"good"}\n\xff\xfe')
            self.assertEqual(inspect_jsonl(tail_path).status, LOG_TORN_TAIL)
            with self.assertRaises(JsonlTornTailError):
                read_committed_jsonl(tail_path)

            prefix_path = base / "prefix.jsonl"
            prefix_path.write_bytes(b'{"event":"good"}\n\xff\xfe\n')
            report = inspect_jsonl(prefix_path)
            self.assertEqual(report.status, LOG_CORRUPT_PREFIX)
            self.assertEqual(report.corrupt_line, 2)
            with self.assertRaises(JsonlCorruptPrefixError):
                read_committed_jsonl(prefix_path)

    def test_newline_committed_corruption_inside_prefix_is_never_auto_truncated(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            original = b'{"event":"a"}\nnot-json\n{"event":"b"}\n'
            path.write_bytes(original)
            report = inspect_jsonl(path)
            self.assertEqual(report.status, LOG_CORRUPT_PREFIX)
            self.assertEqual(report.committed_records, 1)
            self.assertEqual(report.corrupt_line, 2)

            with self.assertRaises(JsonlCorruptPrefixError):
                read_committed_jsonl(path)
            with self.assertRaises(JsonlCorruptPrefixError):
                append_jsonl_record(path, {"event": "c"})
            with self.assertRaises(JsonlCorruptPrefixError):
                discard_torn_tail(path)
            self.assertEqual(path.read_bytes(), original)

    def test_newline_committed_non_object_json_is_corrupt_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            path.write_bytes(b'[]\n')
            self.assertEqual(inspect_jsonl(path).status, LOG_CORRUPT_PREFIX)
            with self.assertRaises(JsonlCorruptPrefixError):
                read_committed_jsonl(path)

    def test_provenance_torn_tail_blocks_retry_then_recovers_idempotently(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            text = "prefix exact evidence suffix"
            source = self._ingest(base, root, "p.md", text)
            target = "exact evidence"
            start = text.index(target)
            first, created = bind_exact_raw_span(
                root,
                topic_id="topic",
                source_id=source.source_id,
                start=start,
                end=start + len(target),
                local_label="claim.alpha",
            )
            self.assertTrue(created)
            provenance = root / "provenance.jsonl"
            committed = provenance.read_bytes()
            with provenance.open("ab") as handle:
                handle.write(b'{"event":"bind_exact_raw_span"')

            self.assertEqual(inspect_jsonl(provenance).status, LOG_TORN_TAIL)
            with self.assertRaises(JsonlTornTailError):
                provenance_history(root)
            with self.assertRaises(JsonlTornTailError):
                bind_exact_raw_span(
                    root,
                    topic_id="topic",
                    source_id=source.source_id,
                    start=start,
                    end=start + len(target),
                    local_label="claim.alpha",
                )

            discard_torn_tail(provenance)
            self.assertEqual(provenance.read_bytes(), committed)
            second, created_again = bind_exact_raw_span(
                root,
                topic_id="topic",
                source_id=source.source_id,
                start=start,
                end=start + len(target),
                local_label="claim.alpha",
            )
            self.assertFalse(created_again)
            self.assertEqual(second.record_id, first.record_id)

    def test_canonical_integrity_report_is_read_only_and_identity_free(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            source = self._ingest(base, root, "secret-name.md", "secret-content-token")
            bind_exact_raw_span(
                root,
                topic_id="topic",
                source_id=source.source_id,
                start=0,
                end=6,
                local_label="claim.secret",
            )
            provenance = root / "provenance.jsonl"
            with provenance.open("ab") as handle:
                handle.write(b'{"partial":')

            before_manifest = (root / "manifest.jsonl").read_bytes()
            before_provenance = provenance.read_bytes()
            report = verify_canonical_log_integrity(root)
            safe = json.dumps(report.as_safe_dict(), sort_keys=True)
            self.assertFalse(report.ok)
            self.assertEqual(report.manifest.status, LOG_CLEAN)
            self.assertEqual(report.provenance.status, LOG_TORN_TAIL)
            self.assertEqual((root / "manifest.jsonl").read_bytes(), before_manifest)
            self.assertEqual(provenance.read_bytes(), before_provenance)

            for forbidden in (
                "src-", "obj-", "origin-", "secret-name", "secret-content-token",
                "claim.secret", "manifest.jsonl", "provenance.jsonl", "sha256", "raw/",
            ):
                self.assertNotIn(forbidden, safe)

    def test_clean_discard_is_idempotent_noop(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            append_jsonl_record(path, {"event": "a"})
            before = path.read_bytes()
            self.assertEqual(discard_torn_tail(path), 0)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
