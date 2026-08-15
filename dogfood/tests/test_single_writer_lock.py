import os
import stat
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from dogfood.llm_wiki import temporal
from dogfood.llm_wiki.store import ingest_file
from dogfood.llm_wiki.temporal import correct_source, temporal_projection
from dogfood.llm_wiki.writer_lock import store_writer_lock


class SingleWriterLockTests(unittest.TestCase):
    def test_competing_lock_times_out_without_exposing_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            outcome = []

            def contender():
                try:
                    with store_writer_lock(root, timeout_seconds=0.05):
                        outcome.append("acquired")
                except Exception as exc:  # noqa: BLE001 - assert exact public failure below
                    outcome.append(str(exc))

            with store_writer_lock(root, timeout_seconds=0.5):
                thread = threading.Thread(target=contender)
                thread.start()
                thread.join(timeout=1.0)
                self.assertFalse(thread.is_alive())

            self.assertEqual(outcome, ["wiki_writer_busy"])
            self.assertNotIn(str(root), outcome[0])

            lock_path = root / ".writer.lock"
            self.assertTrue(lock_path.exists())
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(lock_path.stat().st_mode), 0o600)

            # The file may remain, but OS ownership is gone after the context.
            with store_writer_lock(root, timeout_seconds=0.1):
                pass

    def test_temporal_read_validate_append_is_one_serialized_writer_operation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic_id = "topic-race"

            paths = []
            sources = []
            for name, body in (("a.md", "A"), ("b.md", "B"), ("c.md", "C")):
                path = base / name
                path.write_text(body, encoding="utf-8")
                paths.append(path)
                source, _ = ingest_file(root, path, topic_id=topic_id)
                sources.append(source)
            predecessor, successor_b, successor_c = sources

            original_append = temporal._append_manifest
            first_at_append = threading.Event()
            release_first = threading.Event()
            results = {}

            def gated_append(root_arg, event):
                if threading.current_thread().name == "writer-b":
                    first_at_append.set()
                    if not release_first.wait(timeout=2.0):
                        raise RuntimeError("test_release_timeout")
                return original_append(root_arg, event)

            def run(name, successor):
                try:
                    results[name] = correct_source(
                        root,
                        predecessor.source_id,
                        successor.source_id,
                        topic_id=topic_id,
                    )
                except Exception as exc:  # noqa: BLE001 - competing writer must be rejected
                    results[name] = exc

            with mock.patch.object(temporal, "_append_manifest", side_effect=gated_append):
                first = threading.Thread(target=run, args=("first", successor_b), name="writer-b")
                second = threading.Thread(target=run, args=("second", successor_c), name="writer-c")
                first.start()
                self.assertTrue(first_at_append.wait(timeout=1.0))
                second.start()

                # First writer has already validated but has not appended yet.
                # The second writer must still be blocked outside semantic replay.
                time.sleep(0.1)
                self.assertTrue(second.is_alive())
                self.assertNotIn("second", results)

                release_first.set()
                first.join(timeout=2.0)
                second.join(timeout=2.0)

            self.assertFalse(first.is_alive())
            self.assertFalse(second.is_alive())
            self.assertIs(results["first"], True)
            self.assertIsInstance(results["second"], ValueError)
            self.assertIn("replacement_semantics_conflict", str(results["second"]))

            projection = temporal_projection(root, topic_id=topic_id)
            self.assertNotIn(predecessor.source_id, projection.current_source_ids)
            self.assertIn(successor_b.source_id, projection.current_source_ids)
            self.assertIn(successor_c.source_id, projection.current_source_ids)
            self.assertEqual(
                projection.replacements[predecessor.source_id].successor_source_id,
                successor_b.source_id,
            )


if __name__ == "__main__":
    unittest.main()
