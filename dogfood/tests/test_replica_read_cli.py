from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.agent_state import add_pending_lineage, set_source_locator
from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.remote_snapshot import snapshot_manifest
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class ReplicaReadCliTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, str, str, str]:
        root = base / "replica"
        first_file = base / "first.md"
        second_file = base / "second.md"
        first_file.write_text("cedar quota is ten\nfirst revision\n", encoding="utf-8")
        second_file.write_text("cedar quota is twelve\nsecond revision\n", encoding="utf-8")
        ensure_workspace(root)
        topic = create_topic(root, "Remote Replica")
        first, _ = ingest_file(root, first_file, topic_id=topic["topic_id"])
        second, _ = ingest_file(root, second_file, topic_id=topic["topic_id"])
        set_source_locator(root, first.source_id, relative_path="first.md", sha256=first.sha256)
        set_source_locator(root, second.source_id, relative_path="second.md", sha256=second.sha256)
        add_pending_lineage(
            root,
            created_at="2026-09-02T00:00:00+00:00",
            topic_id=topic["topic_id"],
            topic_label="Remote Replica",
            workspace_file="first.md",
            predecessor_source_ids=[first.source_id],
            successor_source_id=second.source_id,
        )
        return root, topic["topic_id"], first.source_id, second.source_id

    def _tree_signature(self, root: Path) -> tuple[tuple[object, ...], ...]:
        rows: list[tuple[object, ...]] = []
        for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
            rel = path.relative_to(root).as_posix()
            stat = path.lstat()
            mode = stat.st_mode & 0o7777
            if path.is_symlink():
                rows.append((rel, "symlink", mode, os.readlink(path)))
            elif path.is_dir():
                rows.append((rel, "dir", mode))
            elif path.is_file():
                payload = path.read_bytes()
                rows.append((rel, "file", mode, len(payload), hashlib.sha256(payload).hexdigest()))
            else:
                rows.append((rel, "other", mode))
        return tuple(rows)

    def _run(self, root: Path, snapshot_id: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "dogfood.llm_wiki.replica_read_cli",
                "--root",
                str(root),
                "--expected-snapshot-id",
                snapshot_id,
                *args,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def test_supported_remote_replica_reads_leave_entire_tree_and_modes_unchanged(self) -> None:
        with tempfile.TemporaryDirectory(prefix="replica-read-zero-write-") as tmp:
            root, topic_id, first_id, second_id = self._fixture(Path(tmp))
            snapshot_id = snapshot_manifest(root)["snapshot_id"]
            before = self._tree_signature(root)
            commands = [
                ("integrity",),
                ("topic-list",),
                ("locator-list",),
                ("pending-list",),
                ("usage-status", "--day", "2026-09-02"),
                ("search", "cedar quota", "--topic", topic_id, "--json"),
                ("discover", "cedar quota", "--json"),
                ("source-list", "--topic", topic_id, "--json"),
                ("source-status", first_id, "--topic", topic_id),
                ("source-show", first_id, "--topic", topic_id),
                ("history", "--json"),
                ("read", first_id, "--topic", topic_id, "--max-chars", "40"),
                ("relevant", first_id, "--topic", topic_id, "--query", "quota", "--max-chars", "40"),
                (
                    "compare",
                    first_id,
                    second_id,
                    "--topic",
                    topic_id,
                    "--context-chars",
                    "20",
                    "--max-change-chars",
                    "80",
                ),
            ]
            for command in commands:
                with self.subTest(command=command):
                    proc = self._run(root, snapshot_id, *command)
                    self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
                    self.assertEqual(self._tree_signature(root), before)
                    self.assertEqual(snapshot_manifest(root)["snapshot_id"], snapshot_id)

    def test_snapshot_identity_change_fails_closed_before_read_success(self) -> None:
        with tempfile.TemporaryDirectory(prefix="replica-read-tamper-") as tmp:
            root, _, _, _ = self._fixture(Path(tmp))
            snapshot_id = snapshot_manifest(root)["snapshot_id"]
            topics_path = root / "topics.json"
            topics_path.write_bytes(topics_path.read_bytes() + b" ")
            before = self._tree_signature(root)

            proc = self._run(root, snapshot_id, "topic-list")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("REPLICA-READ-STOP", proc.stderr)
            self.assertEqual(self._tree_signature(root), before)


if __name__ == "__main__":
    unittest.main()
