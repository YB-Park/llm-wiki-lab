from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.jsonl_log import append_jsonl_object, audit_canonical_logs, read_jsonl_objects
from dogfood.llm_wiki.private_fs import ensure_private_file
from dogfood.llm_wiki.provenance import bind_exact_raw_span
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
            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                read_jsonl_objects(root / "manifest.jsonl", log_name="manifest")
            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                append_jsonl_object(root / "manifest.jsonl", {"event": "probe"})
            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                ensure_private_file(root / "manifest.jsonl")

            canonical = audit_canonical_logs(root)
            self.assertEqual(canonical.manifest.status, "missing")
            self.assertFalse(canonical.ok)
            self.assertEqual(raw_path.read_bytes(), raw_before)
            self.assertFalse((root / "config.json").exists())
            self.assertFalse((root / "manifest.jsonl").exists())

    def test_surviving_provenance_alone_marks_missing_manifest_as_prior_state_loss(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "evidence.md"
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
            self.assertFalse(report["ok"])
            self.assertEqual(report["canonical_logs"]["manifest"]["status"], "missing")
            self.assertEqual(report["raw"]["status"], "not_checked_manifest_missing")
            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                ensure_workspace(root)
            with self.assertRaisesRegex(RuntimeError, "canonical_manifest_missing"):
                history(root)

            self.assertEqual(provenance.read_bytes(), provenance_before)
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
