from __future__ import annotations

import os
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from dogfood.llm_wiki.private_fs import (
    PRIVATE_DIR_MODE,
    PRIVATE_FILE_MODE,
    tighten_workspace_permissions,
)
from dogfood.llm_wiki.store import ensure_workspace


@unittest.skipUnless(os.name == "posix", "POSIX permission mode regression")
class PrivateFsPortabilityTests(unittest.TestCase):
    def test_tighten_rehardens_known_private_subtrees_without_changing_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / ".wiki-lab"
            ensure_workspace(root)

            human = root / "human-knowledge"
            derived = root / "agent-wiki" / "source-notes"
            human.mkdir(parents=True)
            derived.mkdir(parents=True)
            human_file = human / "hk-test.json"
            derived_file = derived / "src-deadbeef.json"
            human_file.write_bytes(b'{"private":"human knowledge"}\n')
            derived_file.write_bytes(b'{"private":"derived note"}\n')

            paths = [
                root / "config.json",
                root / "manifest.jsonl",
                human_file,
                derived_file,
            ]
            before = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest() for path in paths}

            root.chmod(0o755)
            for path in sorted(root.rglob("*")):
                if path.is_symlink():
                    continue
                if path.is_dir():
                    path.chmod(0o755)
                elif path.is_file():
                    path.chmod(0o644)

            tighten_workspace_permissions(root)

            self.assertEqual(root.stat().st_mode & 0o777, PRIVATE_DIR_MODE)
            for directory in (root / "raw", human, root / "agent-wiki", derived):
                self.assertEqual(directory.stat().st_mode & 0o777, PRIVATE_DIR_MODE)
            for path in paths:
                self.assertEqual(path.stat().st_mode & 0o777, PRIVATE_FILE_MODE)

            after = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest() for path in paths}
            self.assertEqual(before, after, "permission recovery must not mutate Wiki bytes")

    def test_tighten_never_follows_private_subtree_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / ".wiki-lab"
            ensure_workspace(root)

            human = root / "human-knowledge"
            human.mkdir()
            outside = base / "outside"
            outside.mkdir()
            outside_file = outside / "do-not-touch.txt"
            outside_file.write_bytes(b"external bytes\n")
            outside.chmod(0o755)
            outside_file.chmod(0o644)
            (human / "escape").symlink_to(outside, target_is_directory=True)

            before_digest = sha256(outside_file.read_bytes()).hexdigest()
            before_dir_mode = outside.stat().st_mode & 0o777
            before_file_mode = outside_file.stat().st_mode & 0o777

            tighten_workspace_permissions(root)

            self.assertEqual(outside.stat().st_mode & 0o777, before_dir_mode)
            self.assertEqual(outside_file.stat().st_mode & 0o777, before_file_mode)
            self.assertEqual(sha256(outside_file.read_bytes()).hexdigest(), before_digest)


if __name__ == "__main__":
    unittest.main()
