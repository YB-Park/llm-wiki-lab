from __future__ import annotations

import io
import os
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.private_fs import write_private_text
from dogfood.llm_wiki.remote_attach_import import RemoteAttachError, import_attached_snapshot
from dogfood.llm_wiki.remote_snapshot import write_snapshot
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


@unittest.skipUnless(os.name == "posix", "S1 attach importer is Linux/POSIX only")
class RemoteAttachImportTests(unittest.TestCase):
    def _snapshot(self, base: Path) -> tuple[bytes, str]:
        root = base / "source"
        evidence = base / "evidence.md"
        evidence.write_bytes(b"remote attached evidence\r\ncedar quota=21\r\n")
        ensure_workspace(root)
        topic = create_topic(root, "Attach")
        ingest_file(root, evidence, topic_id=topic["topic_id"])
        stream = io.BytesIO()
        manifest = write_snapshot(root, stream)
        return stream.getvalue(), str(manifest["snapshot_id"])

    def _fresh_destination(self, base: Path) -> tuple[Path, bytes]:
        root = base / "destination"
        ensure_workspace(root)
        opt_in = b'{"pc":"fresh-b","epoch":"host-local"}\n'
        write_private_text(root / "workspace-opt-in.json", opt_in.decode("utf-8"))
        return root, opt_in

    def test_attach_preserves_host_local_opt_in_and_materializes_exact_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-attach-import-") as tmp:
            base = Path(tmp)
            payload, snapshot_id = self._snapshot(base)
            destination, opt_in = self._fresh_destination(base)

            imported = import_attached_snapshot(io.BytesIO(payload), destination)

            self.assertEqual(imported["snapshot_id"], snapshot_id)
            self.assertEqual((destination / "workspace-opt-in.json").read_bytes(), opt_in)
            self.assertTrue(any((destination / "raw").glob("*.txt")))
            self.assertFalse((destination / ".writer.lock").exists())

    def test_nonempty_local_memory_fails_closed_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-attach-nonempty-") as tmp:
            base = Path(tmp)
            payload, _ = self._snapshot(base)
            destination, _ = self._fresh_destination(base)
            before = b'{"event":"local-memory-exists"}\n'
            (destination / "manifest.jsonl").write_bytes(before)

            with self.assertRaisesRegex(RemoteAttachError, "remote_attach_requires_empty_local_memory"):
                import_attached_snapshot(io.BytesIO(payload), destination)

            self.assertEqual((destination / "manifest.jsonl").read_bytes(), before)

    def test_extra_portable_state_fails_closed_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-attach-extra-") as tmp:
            base = Path(tmp)
            payload, _ = self._snapshot(base)
            destination, _ = self._fresh_destination(base)
            (destination / "agent-state.json").write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(RemoteAttachError, "remote_attach_requires_empty_local_memory"):
                import_attached_snapshot(io.BytesIO(payload), destination)

            self.assertTrue((destination / "agent-state.json").exists())


if __name__ == "__main__":
    unittest.main()
