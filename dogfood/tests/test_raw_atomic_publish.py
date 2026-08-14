from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dogfood.llm_wiki.store import history, ingest_file


class RawAtomicPublishTests(unittest.TestCase):
    def test_partial_private_write_failure_never_publishes_final_raw_path_and_retry_succeeds(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "evidence.md"
            payload = b"cedar evidence that must publish atomically\n"
            note.write_bytes(payload)
            sha = hashlib.sha256(payload).hexdigest()
            final_raw = root / "raw" / f"{sha}.txt"

            def fail_after_partial_write(fd: int, data: bytes) -> None:
                os.write(fd, data[: max(1, len(data) // 3)])
                raise OSError("injected_partial_write")

            with patch("dogfood.llm_wiki.private_fs._write_all", side_effect=fail_after_partial_write):
                with self.assertRaisesRegex(OSError, "injected_partial_write"):
                    ingest_file(root, note, topic_id="topic-atomic")

            self.assertFalse(final_raw.exists(), "failed pre-publication write must not poison final hash path")
            self.assertEqual(history(root), [], "manifest must not claim an unpublished raw object")
            self.assertEqual(
                [path.name for path in (root / "raw").iterdir()],
                [],
                "temporary raw write must be cleaned after failure",
            )

            source, duplicate = ingest_file(root, note, topic_id="topic-atomic")
            self.assertFalse(duplicate)
            self.assertEqual(source.raw_path, final_raw)
            self.assertEqual(final_raw.read_bytes(), payload)
            self.assertEqual(sum(row.get("event") == "ingest" for row in history(root)), 1)

    def test_private_replacement_leaves_no_temporary_file_after_success(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "evidence.md"
            note.write_text("stable atomic evidence", encoding="utf-8")

            source, _ = ingest_file(root, note, topic_id="topic-success")

            self.assertTrue(source.raw_path.exists())
            self.assertFalse(any(".tmp-" in path.name for path in source.raw_path.parent.iterdir()))


if __name__ == "__main__":
    unittest.main()
