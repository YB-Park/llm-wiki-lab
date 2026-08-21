from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.federation_read_cli import _manifest_authority_anchor, main as federation_read_main
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class FederationReadCliTests(unittest.TestCase):
    def _run(self, *args: str) -> str:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = federation_read_main(list(args))
        self.assertEqual(code, 0)
        return stream.getvalue()

    def _snapshot(self, root: Path) -> list[tuple[str, str, int, str]]:
        rows: list[tuple[str, str, int, str]] = []
        for path in sorted([root, *root.rglob("*")], key=lambda value: str(value.relative_to(root)) if value != root else ""):
            relative = "." if path == root else path.relative_to(root).as_posix()
            mode = path.stat().st_mode & 0o777
            if path.is_dir():
                rows.append((relative, "dir", mode, ""))
            elif path.is_file():
                rows.append((relative, "file", mode, hashlib.sha256(path.read_bytes()).hexdigest()))
        return rows

    def _base_args(self, root: Path, anchor: str) -> tuple[str, ...]:
        return ("--root", str(root), "--expected-authority-anchor", anchor)

    def test_uninitialized_root_fails_without_creating_anything(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "missing-wiki"
            with self.assertRaises(SystemExit):
                self._run(*self._base_args(root, "0" * 64), "integrity")
            self.assertFalse(root.exists())

    def test_all_federation_read_operations_leave_external_tree_and_modes_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / ".wiki-lab"
            evidence = parent / "external.md"
            evidence.write_text("Project A decided the orchid retry budget is 914.\n", encoding="utf-8")
            ensure_workspace(root)
            topic = create_topic(root, "external")
            source, _ = ingest_file(root, evidence, topic_id=topic["topic_id"])
            anchor = _manifest_authority_anchor(root)

            if os.name != "nt":
                os.chmod(root, 0o755)
                os.chmod(root / "raw", 0o755)
                os.chmod(root / "config.json", 0o644)
                os.chmod(root / "manifest.jsonl", 0o644)
                os.chmod(root / "topics.json", 0o644)

            before = self._snapshot(root)
            base = self._base_args(root, anchor)
            integrity = self._run(*base, "integrity")
            self.assertIn('"ok": true', integrity)
            discovery = self._run(
                *base, "discover", "orchid retry budget", "--top-k-per-topic", "3", "--json"
            )
            self.assertIn(source.source_id, discovery)
            raw = self._run(
                *base, "read", source.source_id, "--topic", topic["topic_id"], "--max-chars", "1000"
            )
            self.assertIn("orchid retry budget is 914", raw)
            relevant = self._run(
                *base, "relevant", source.source_id, "--topic", topic["topic_id"],
                "--query", "orchid retry budget", "--max-chars", "1000"
            )
            self.assertIn("orchid retry budget is 914", relevant)
            self.assertEqual(self._run(*base, "pending-list"), "")
            self.assertEqual(self._run(*base, "agent-wiki-search", "orchid", "--top-k", "3", "--json"), "")
            with self.assertRaises(SystemExit):
                self._run(*base, "agent-wiki-show", source.source_id)

            after = self._snapshot(root)
            self.assertEqual(after, before, "strict federation reads must not create, rewrite, chmod, or delete external store artifacts")

    def test_registered_continuity_witness_is_rechecked_before_each_bridge_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / ".wiki-lab"
            evidence = parent / "external.md"
            evidence.write_text("registered authority\n", encoding="utf-8")
            ensure_workspace(root)
            ingest_file(root, evidence)
            anchor = _manifest_authority_anchor(root)

            manifest = root / "manifest.jsonl"
            lines = manifest.read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            first["source_id"] = "src-replacement-authority"
            lines[0] = json.dumps(first, ensure_ascii=False, sort_keys=True)
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "library_store_identity_changed"):
                self._run(*self._base_args(root, anchor), "integrity")


if __name__ == "__main__":
    unittest.main()
