from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file


class ManifestLossSurvivingRawTests(unittest.TestCase):
    def test_config_and_manifest_loss_over_surviving_raw_fails_closed_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "evidence.md"
            note.write_text("cedar evidence survives canonical loss", encoding="utf-8")

            source, _ = ingest_file(root, note, topic_id="topic-loss")
            raw_path = source.raw_path
            raw_before = raw_path.read_bytes()

            (root / "config.json").unlink()
            (root / "manifest.jsonl").unlink()

            report = audit_alpha_integrity(root)
            self.assertFalse(report["ok"])
            self.assertFalse(report["workspace_initialized"])
            self.assertEqual(report["canonical_logs"]["manifest"]["status"], "missing")
            self.assertEqual(report["raw"]["status"], "not_checked_manifest_missing")

            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                history(root)
            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                ensure_workspace(root)

            self.assertEqual(raw_path.read_bytes(), raw_before)
            self.assertFalse((root / "config.json").exists())
            self.assertFalse((root / "manifest.jsonl").exists())

    def test_brand_new_and_empty_raw_workspace_can_still_initialize(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "brand-new"
            ensure_workspace(root)
            self.assertTrue((root / "config.json").is_file())
            self.assertTrue((root / "manifest.jsonl").is_file())

        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "empty-raw"
            (root / "raw").mkdir(parents=True)
            ensure_workspace(root)
            self.assertTrue((root / "config.json").is_file())
            self.assertTrue((root / "manifest.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
