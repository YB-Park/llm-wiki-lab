from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from dogfood.llm_wiki.cli import main as cli_main
from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class AlphaIntegrityStatusTests(unittest.TestCase):
    def test_clean_initialized_workspace_is_ready(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            note = base / "note.md"
            note.write_text("clean cedar evidence", encoding="utf-8")
            ingest_file(root, note, topic_id="topic-clean")

            report = audit_alpha_integrity(root)

            self.assertTrue(report["workspace_initialized"])
            self.assertTrue(report["canonical_logs"]["ok"])
            self.assertEqual(report["raw"]["status"], "clean")
            self.assertTrue(report["raw"]["ok"])
            self.assertTrue(report["ok"])

    def test_missing_raw_object_fails_without_exposing_evidence_identity(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            ensure_workspace(root)
            note = base / "private-name.md"
            note.write_text("private cedar token", encoding="utf-8")
            source, _ = ingest_file(root, note, topic_id="topic-private", origin_id="origin-private")
            source.raw_path.unlink()

            report = audit_alpha_integrity(root)
            encoded = json.dumps(report, sort_keys=True)

            self.assertFalse(report["ok"])
            self.assertTrue(report["canonical_logs"]["ok"])
            self.assertEqual(report["raw"]["status"], "failed")
            self.assertEqual(report["raw"]["missing_objects"], 1)
            for forbidden in (
                source.source_id,
                source.object_id,
                source.sha256,
                "private-name.md",
                "topic-private",
                "origin-private",
                "private cedar token",
            ):
                self.assertNotIn(forbidden, encoded)

    def test_torn_manifest_blocks_raw_audit_without_prefix_fallback_or_repair(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            manifest = root / "manifest.jsonl"
            manifest.write_bytes(b'{"event":"partial"')
            before = manifest.read_bytes()

            report = audit_alpha_integrity(root)

            self.assertFalse(report["ok"])
            self.assertEqual(report["canonical_logs"]["manifest"]["status"], "torn_tail")
            self.assertEqual(report["raw"], {"status": "not_checked_manifest_damaged", "ok": False})
            self.assertEqual(manifest.read_bytes(), before)

    def test_cli_integrity_emits_one_aggregate_json_object_and_never_repairs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            manifest = root / "manifest.jsonl"
            manifest.write_bytes(b'{"event":"partial"')
            before = manifest.read_bytes()
            output = StringIO()

            with redirect_stdout(output):
                code = cli_main(["--root", str(root), "integrity"])

            self.assertEqual(code, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["format"], "LLM-WIKI-ALPHA-INTEGRITY-v0")
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["canonical_logs"]["manifest"]["status"], "torn_tail")
            self.assertEqual(manifest.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
