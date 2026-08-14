from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from dogfood.llm_wiki.provenance import bind_exact_raw_span, resolve_exact_raw_span
from dogfood.llm_wiki.retrieval import search
from dogfood.llm_wiki.store import (
    Source,
    ensure_workspace,
    find_source,
    ingest_file,
    read_bytes_verified,
    read_text,
    sources,
    supersede_source,
    verify_raw_integrity,
)


class VerifiedRawIntegrityTests(unittest.TestCase):
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

    def test_valid_ascii_and_korean_reads_verify_and_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            text = "원본 증거🙂를 검증해서 읽는다.\nalpha evidence"
            source = self._ingest(base, root, "topic", "note.md", text, "origin-a")

            self.assertEqual(read_bytes_verified(source), text.encode("utf-8"))
            self.assertEqual(read_text(source), text)
            report = verify_raw_integrity(root)
            self.assertTrue(report.ok)
            self.assertEqual(report.source_records, 1)
            self.assertEqual(report.unique_objects, 1)
            self.assertEqual(report.verified_objects, 1)
            self.assertEqual(report.missing_objects, 0)
            self.assertEqual(report.corrupt_objects, 0)
            self.assertEqual(report.invalid_utf8_objects, 0)
            self.assertEqual(report.invalid_source_records, 0)

    def test_existing_raw_byte_tamper_fails_read_and_default_search_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            source = self._ingest(base, root, topic, "a.md", "alpha quota decision forty two", "origin-a")
            source.raw_path.write_text("alpha quota decision tampered", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "raw_object_integrity_mismatch"):
                read_text(source)
            with self.assertRaisesRegex(RuntimeError, "raw_object_integrity_mismatch"):
                search(root, "alpha quota decision", topic_id=topic)

            report = verify_raw_integrity(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.corrupt_objects, 1)
            self.assertEqual(report.verified_objects, 0)

    def test_missing_raw_object_fails_captured_source_and_projected_search(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            source = self._ingest(base, root, topic, "a.md", "alpha evidence", "origin-a")
            source.raw_path.unlink()

            with self.assertRaisesRegex(RuntimeError, "raw_object_missing"):
                read_text(source)
            with self.assertRaisesRegex(RuntimeError, "missing_raw_object"):
                search(root, "alpha", topic_id=topic)

            report = verify_raw_integrity(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.missing_objects, 1)
            self.assertEqual(report.verified_objects, 0)

    def test_manifest_object_identity_mismatch_fails_before_semantic_read(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            self._ingest(base, root, "topic", "a.md", "alpha evidence", "origin-a")
            manifest = root / "manifest.jsonl"
            rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
            ingest = next(row for row in rows if row.get("event") == "ingest")
            ingest["object_id"] = "obj-" + "0" * 64
            manifest.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "source_record_object_identity_mismatch"):
                sources(root, topic_id="topic")
            report = verify_raw_integrity(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.source_records, 1)
            self.assertEqual(report.invalid_source_records, 1)
            self.assertEqual(report.unique_objects, 0)

    def test_manifest_sha_format_fails_before_raw_path_construction(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            self._ingest(base, root, "topic", "a.md", "alpha evidence", "origin-a")
            manifest = root / "manifest.jsonl"
            rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
            ingest = next(row for row in rows if row.get("event") == "ingest")
            ingest["sha256"] = "../../outside"
            ingest["object_id"] = "obj-../../outside"
            manifest.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "source_record_sha_invalid"):
                sources(root, topic_id="topic")
            report = verify_raw_integrity(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.invalid_source_records, 1)
            self.assertEqual(report.unique_objects, 0)

    def test_invalid_utf8_with_self_consistent_hash_fails_text_read_and_is_counted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            data = b"\xff\xfe\xfd"
            sha = hashlib.sha256(data).hexdigest()
            raw = root / "raw" / f"{sha}.txt"
            raw.write_bytes(data)
            source = Source(
                source_id="src-invalid-utf8",
                object_id=f"obj-{sha}",
                sha256=sha,
                name="opaque",
                size_bytes=len(data),
                raw_path=raw,
            )
            self.assertEqual(read_bytes_verified(source), data)
            with self.assertRaisesRegex(RuntimeError, "raw_object_not_utf8"):
                read_text(source)

            event = {
                "event": "ingest",
                "record_schema": "llm-wiki-source-v1",
                "recorded_at": "2026-01-01T00:00:00+00:00",
                "source_id": source.source_id,
                "object_id": source.object_id,
                "sha256": source.sha256,
                "origin_id": None,
                "name": "opaque",
                "size_bytes": len(data),
                "duplicate_content": False,
            }
            (root / "manifest.jsonl").write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")
            report = verify_raw_integrity(root)
            self.assertFalse(report.ok)
            self.assertEqual(report.invalid_utf8_objects, 1)
            self.assertEqual(report.corrupt_objects, 0)

    def test_integrity_audit_deduplicates_shared_objects_and_exposes_counts_only(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            text = "shared immutable evidence"
            self._ingest(base, root, topic, "a.md", text, "origin-a")
            self._ingest(base, root, topic, "b.md", text, "origin-b")

            before_manifest = (root / "manifest.jsonl").read_bytes()
            before_raw = {path.name: path.read_bytes() for path in (root / "raw").glob("*.txt")}
            report = verify_raw_integrity(root)
            after_manifest = (root / "manifest.jsonl").read_bytes()
            after_raw = {path.name: path.read_bytes() for path in (root / "raw").glob("*.txt")}

            self.assertTrue(report.ok)
            self.assertEqual(report.source_records, 2)
            self.assertEqual(report.unique_objects, 1)
            self.assertEqual(report.verified_objects, 1)
            self.assertEqual(before_manifest, after_manifest)
            self.assertEqual(before_raw, after_raw)

            safe = json.dumps(asdict(report), sort_keys=True)
            self.assertEqual(set(asdict(report)), {
                "source_records", "unique_objects", "verified_objects", "missing_objects",
                "corrupt_objects", "invalid_utf8_objects", "invalid_source_records", "ok",
            })
            self.assertNotIn("src-", safe)
            self.assertNotIn("origin", safe)
            self.assertNotIn("raw/", safe)
            self.assertNotIn(text, safe)

    def test_historical_superseded_source_remains_verified_and_readable(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            a = self._ingest(base, root, topic, "a.md", "state A", "origin-a")
            b = self._ingest(base, root, topic, "b.md", "state B", "origin-b")
            supersede_source(root, a.source_id, b.source_id, topic_id=topic)

            historical = find_source(root, a.source_id, topic_id=topic)
            self.assertEqual(read_text(historical), "state A")
            report = verify_raw_integrity(root)
            self.assertTrue(report.ok)
            self.assertEqual(report.source_records, 2)
            self.assertEqual(report.unique_objects, 2)
            self.assertEqual(report.verified_objects, 2)

    def test_exact_provenance_still_resolves_and_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            text = "prefix exact source span suffix"
            source = self._ingest(base, root, topic, "a.md", text, "origin-a")
            target = "exact source span"
            start = text.index(target)
            record, _ = bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=source.source_id,
                start=start,
                end=start + len(target),
                local_label="claim.integrity",
            )
            self.assertEqual(resolve_exact_raw_span(root, record.record_id, topic_id=topic).text, target)

            source.raw_path.write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "provenance_raw_object_integrity_mismatch"):
                resolve_exact_raw_span(root, record.record_id, topic_id=topic)

    def test_integrity_audit_is_read_only_and_does_not_change_valid_retrieval_signature(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            self._ingest(base, root, topic, "a.md", "alpha quota decision forty two", "origin-a")
            self._ingest(base, root, topic, "b.md", "beta calendar archive", "origin-b")

            before = search(root, "alpha quota decision", topic_id=topic, top_k=8)
            signature_before = [(h.object_id, h.score, h.source_ids, h.snippet) for h in before]
            report = verify_raw_integrity(root)
            after = search(root, "alpha quota decision", topic_id=topic, top_k=8)
            signature_after = [(h.object_id, h.score, h.source_ids, h.snippet) for h in after]

            self.assertTrue(report.ok)
            self.assertEqual(signature_after, signature_before)


if __name__ == "__main__":
    unittest.main()
