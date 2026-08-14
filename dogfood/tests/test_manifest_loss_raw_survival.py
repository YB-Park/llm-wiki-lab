from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from dogfood.llm_wiki.cli import main as cli_main
from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.provenance import bind_exact_raw_span
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file


class ManifestLossRawSurvivalTests(unittest.TestCase):
    def test_surviving_raw_prevents_reinitialization_when_config_and_manifest_are_both_lost(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "note.md"
            note.write_text("surviving cedar evidence", encoding="utf-8")
            source, _ = ingest_file(root, note, topic_id="topic-loss")
            raw_before = source.raw_path.read_bytes()

            (root / "config.json").unlink()
            (root / "manifest.jsonl").unlink()
            self.assertTrue(source.raw_path.exists())

            report = audit_alpha_integrity(root)
            self.assertFalse(report["workspace_initialized"])
            self.assertFalse(report["ok"])
            self.assertEqual(report["canonical_logs"]["manifest"]["status"], "missing")
            self.assertEqual(report["raw"], {"status": "not_checked_manifest_missing", "ok": False})

            with self.assertRaisesRegex(RuntimeError, "^canonical_manifest_missing$"):
                history(root)
            with self.assertRaisesRegex(RuntimeError, "^canonical_manifest_missing$"):
                ensure_workspace(root)

            self.assertFalse((root / "config.json").exists())
            self.assertFalse((root / "manifest.jsonl").exists())
            self.assertEqual(source.raw_path.read_bytes(), raw_before)

            output = StringIO()
            with redirect_stdout(output):
                code = cli_main(["--root", str(root), "integrity"])
            self.assertEqual(code, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["canonical_logs"]["manifest"]["status"], "missing")
            self.assertEqual(payload["raw"]["status"], "not_checked_manifest_missing")
            self.assertFalse((root / "config.json").exists())
            self.assertFalse((root / "manifest.jsonl").exists())
            self.assertEqual(source.raw_path.read_bytes(), raw_before)

    def test_surviving_provenance_alone_prevents_reinitialization_after_other_state_is_lost(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "note.md"
            note.write_text("precise cedar evidence", encoding="utf-8")
            source, _ = ingest_file(root, note, topic_id="topic-provenance-loss")
            record, created = bind_exact_raw_span(
                root,
                topic_id="topic-provenance-loss",
                source_id=source.source_id,
                start=0,
                end=7,
                local_label="cedar",
            )
            self.assertTrue(created)
            provenance = root / "provenance.jsonl"
            provenance_before = provenance.read_bytes()
            self.assertIn(record.record_id.encode("utf-8"), provenance_before)

            (root / "config.json").unlink()
            (root / "manifest.jsonl").unlink()
            source.raw_path.unlink()
            self.assertEqual(list((root / "raw").iterdir()), [])

            report = audit_alpha_integrity(root)
            self.assertFalse(report["workspace_initialized"])
            self.assertFalse(report["ok"])
            self.assertEqual(report["canonical_logs"]["manifest"]["status"], "missing")
            self.assertEqual(report["raw"], {"status": "not_checked_manifest_missing", "ok": False})

            with self.assertRaisesRegex(RuntimeError, "^canonical_manifest_missing$"):
                history(root)
            with self.assertRaisesRegex(RuntimeError, "^canonical_manifest_missing$"):
                ensure_workspace(root)

            self.assertFalse((root / "config.json").exists())
            self.assertFalse((root / "manifest.jsonl").exists())
            self.assertEqual(provenance.read_bytes(), provenance_before)

    def test_brand_new_or_empty_raw_workspace_remains_initializable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            (root / "raw").mkdir(parents=True)

            ensure_workspace(root)

            self.assertTrue((root / "config.json").is_file())
            self.assertTrue((root / "manifest.jsonl").is_file())
            self.assertEqual(history(root), [])
            self.assertTrue(audit_alpha_integrity(root)["ok"])


if __name__ == "__main__":
    unittest.main()
