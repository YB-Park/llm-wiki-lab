from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic, record_ingest, record_query
from dogfood.llm_wiki.provenance import bind_exact_raw_span
from dogfood.llm_wiki.shadow_calibration import record_retrieval_shadow_failure
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


@unittest.skipUnless(os.name == "posix", "POSIX mode-bit contract")
class PrivateStoragePermissionsTests(unittest.TestCase):
    def _mode(self, path: Path) -> int:
        return stat.S_IMODE(path.stat().st_mode)

    def _build_private_workspace(self, base: Path) -> tuple[Path, list[Path]]:
        root = base / "wiki"
        ensure_workspace(root)
        topic = create_topic(root, "private topic")["topic_id"]
        note = base / "evidence.md"
        note.write_text("private cedar evidence", encoding="utf-8")
        source, _ = ingest_file(root, note, topic_id=topic)
        record_ingest(root, topic)
        record_query(root, topic, "search", "exact_provenance")
        record_retrieval_shadow_failure(root, topic, "search", "exact_provenance")
        bind_exact_raw_span(
            root,
            topic_id=topic,
            source_id=source.source_id,
            start=0,
            end=7,
            local_label="private",
        )
        files = [
            root / "config.json",
            root / "manifest.jsonl",
            root / "provenance.jsonl",
            source.raw_path,
            root / "topics.json",
            root / "workload-events.jsonl",
            root / "retrieval-shadow-events.jsonl",
        ]
        return root, files

    def test_new_private_workspace_ignores_permissive_umask_for_wiki_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            old_umask = os.umask(0o022)
            try:
                root, files = self._build_private_workspace(base)
            finally:
                os.umask(old_umask)

            self.assertEqual(self._mode(root), 0o700)
            self.assertEqual(self._mode(root / "raw"), 0o700)
            for path in files:
                self.assertEqual(self._mode(path), 0o600, path.name)

    def test_ensure_workspace_tightens_known_existing_artifacts_without_content_changes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root, files = self._build_private_workspace(base)
            before = {path: path.read_bytes() for path in files}

            root.chmod(0o755)
            (root / "raw").chmod(0o755)
            for path in files:
                path.chmod(0o644)

            ensure_workspace(root)

            self.assertEqual(self._mode(root), 0o700)
            self.assertEqual(self._mode(root / "raw"), 0o700)
            for path in files:
                self.assertEqual(self._mode(path), 0o600, path.name)
                self.assertEqual(path.read_bytes(), before[path], path.name)


if __name__ == "__main__":
    unittest.main()
