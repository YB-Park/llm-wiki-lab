from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.remote_helper import HELPER_PROTOCOL
from dogfood.llm_wiki.remote_snapshot import SnapshotError, read_snapshot, snapshot_manifest, write_snapshot
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file
from dogfood.llm_wiki.private_fs import write_private_text


class RemoteAuthorityTests(unittest.TestCase):
    def _fixture(self, base: Path, name: str = "wiki") -> tuple[Path, str, str]:
        root = base / name
        source = base / f"{name}.md"
        source.write_text("remote authority evidence\ncedar quota\n", encoding="utf-8")
        ensure_workspace(root)
        topic = create_topic(root, "Remote")
        admitted, _ = ingest_file(root, source, topic_id=topic["topic_id"])
        write_private_text(root / "workspace-opt-in.json", '{"host_local":true}\n')
        write_private_text(root / "agent-wiki" / "source-notes" / "fixture.md", "derived fixture\n")
        return root, topic["topic_id"], admitted.source_id

    def _helper(self, remote_home: Path, request: dict, payload: bytes = b"") -> subprocess.CompletedProcess[bytes]:
        env = dict(os.environ)
        env["LLM_WIKI_REMOTE_HOME"] = str(remote_home)
        body = (json.dumps({"protocol": HELPER_PROTOCOL, **request}, separators=(",", ":")) + "\n").encode("utf-8") + payload
        return subprocess.run(
            [sys.executable, "-m", "dogfood.llm_wiki.remote_helper"],
            input=body,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def _helper_json(self, remote_home: Path, request: dict, payload: bytes = b"") -> dict:
        proc = self._helper(remote_home, request, payload)
        self.assertIn(proc.returncode, (0, 2), proc.stderr.decode("utf-8", errors="replace"))
        row = json.loads(proc.stdout.decode("utf-8"))
        return row

    def test_snapshot_roundtrip_excludes_host_local_and_preserves_destination_opt_in(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-snapshot-") as tmp:
            base = Path(tmp)
            source_root, _, _ = self._fixture(base, "source")
            destination_root, _, _ = self._fixture(base, "destination")
            destination_opt_in = (destination_root / "workspace-opt-in.json").read_bytes()

            stream = io.BytesIO()
            original = write_snapshot(source_root, stream)
            self.assertNotIn("workspace-opt-in.json", [row["path"] for row in original["entries"]])
            self.assertNotIn(".writer.lock", [row["path"] for row in original["entries"]])

            stream.seek(0)
            imported = read_snapshot(stream, destination_root, preserve_host_local=True)
            self.assertEqual(imported["snapshot_id"], original["snapshot_id"])
            self.assertEqual((destination_root / "workspace-opt-in.json").read_bytes(), destination_opt_in)
            self.assertTrue(audit_alpha_integrity(destination_root)["ok"])
            self.assertEqual(snapshot_manifest(destination_root)["snapshot_id"], original["snapshot_id"])

    def test_corrupt_snapshot_never_replaces_last_verified_replica(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-corrupt-") as tmp:
            base = Path(tmp)
            source_root, _, _ = self._fixture(base, "source")
            destination_root, _, _ = self._fixture(base, "destination")
            before_manifest = (destination_root / "manifest.jsonl").read_bytes()

            stream = io.BytesIO()
            write_snapshot(source_root, stream)
            payload = bytearray(stream.getvalue())
            payload[-1] ^= 0x01
            with self.assertRaises(SnapshotError):
                read_snapshot(io.BytesIO(bytes(payload)), destination_root, preserve_host_local=True)

            self.assertEqual((destination_root / "manifest.jsonl").read_bytes(), before_manifest)
            self.assertTrue(audit_alpha_integrity(destination_root)["ok"])

    def test_authority_creates_distinct_project_stores_even_with_same_display_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-identity-") as tmp:
            home = Path(tmp) / "authority"
            first = self._helper_json(home, {"op": "create_store", "display_name": "same-repo", "bootstrap": False})
            second = self._helper_json(home, {"op": "create_store", "display_name": "same-repo", "bootstrap": False})
            self.assertTrue(first["ok"])
            self.assertTrue(second["ok"])
            self.assertNotEqual(first["store"]["store_id"], second["store"]["store_id"])

            listed = self._helper_json(home, {"op": "list_stores"})
            self.assertEqual(len(listed["stores"]), 2)
            self.assertEqual({row["display_name"] for row in listed["stores"]}, {"same-repo"})

    def test_existing_store_bootstrap_preserves_bytes_and_never_transports_opt_in(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-bootstrap-") as tmp:
            base = Path(tmp)
            local_root, _, _ = self._fixture(base, "local")
            home = base / "authority"
            created = self._helper_json(home, {"op": "create_store", "display_name": "project-z", "bootstrap": True})
            store_id = created["store"]["store_id"]

            stream = io.BytesIO()
            local_manifest = write_snapshot(local_root, stream)
            bootstrapped = self._helper_json(home, {"op": "bootstrap_store", "store_id": store_id}, stream.getvalue())
            self.assertTrue(bootstrapped["ok"])
            self.assertEqual(bootstrapped["snapshot_id"], local_manifest["snapshot_id"])

            exported = self._helper(home, {"op": "snapshot_export", "store_id": store_id})
            self.assertEqual(exported.returncode, 0, exported.stderr.decode("utf-8", errors="replace"))
            replica = base / "replica"
            imported = read_snapshot(io.BytesIO(exported.stdout), replica, preserve_host_local=False)
            self.assertEqual(imported["snapshot_id"], local_manifest["snapshot_id"])
            self.assertFalse((replica / "workspace-opt-in.json").exists())
            self.assertEqual(history(replica), history(local_root))

    def test_remote_core_ingest_accepts_uploaded_bytes_without_remote_workspace_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-ingest-") as tmp:
            base = Path(tmp)
            home = base / "authority"
            created = self._helper_json(home, {"op": "create_store", "display_name": "project-y", "bootstrap": False})
            store_id = created["store"]["store_id"]

            topic = self._helper_json(
                home,
                {"op": "run_core", "store_id": store_id, "module": "dogfood.llm_wiki.cli", "args": ["topic", "add", "Remote Inbox"]},
            )
            self.assertTrue(topic["ok"], topic)
            topic_id = re.search(r"TOPIC id=(\S+)", topic["stdout"]).group(1)  # type: ignore[union-attr]

            evidence = b"unrelated workspace file\nremote-only admission\n"
            upload = {
                "token": "__LLM_WIKI_UPLOAD_0__",
                "name": "note.md",
                "size": len(evidence),
                "sha256": __import__("hashlib").sha256(evidence).hexdigest(),
            }
            admitted = self._helper_json(
                home,
                {
                    "op": "run_core",
                    "store_id": store_id,
                    "module": "dogfood.llm_wiki.cli",
                    "args": ["ingest", upload["token"], "--topic", topic_id],
                    "uploads": [upload],
                },
                evidence,
            )
            self.assertTrue(admitted["ok"], admitted)
            self.assertIn("remote-only admission", evidence.decode("utf-8"))

            exported = self._helper(home, {"op": "snapshot_export", "store_id": store_id})
            replica = base / "replica"
            read_snapshot(io.BytesIO(exported.stdout), replica, preserve_host_local=False)
            self.assertTrue(audit_alpha_integrity(replica)["ok"])
            raw_payloads = [path.read_bytes() for path in (replica / "raw").glob("*.txt")]
            self.assertIn(evidence, raw_payloads)

    def test_remote_human_knowledge_is_written_only_to_exact_store(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-hk-") as tmp:
            base = Path(tmp)
            home = base / "authority"
            created = self._helper_json(home, {"op": "create_store", "display_name": "project-a", "bootstrap": False})
            other = self._helper_json(home, {"op": "create_store", "display_name": "project-b", "bootstrap": False})
            store_id = created["store"]["store_id"]
            other_id = other["store"]["store_id"]

            topic = self._helper_json(home, {"op": "run_core", "store_id": store_id, "module": "dogfood.llm_wiki.cli", "args": ["topic", "add", "HK"]})
            topic_id = re.search(r"TOPIC id=(\S+)", topic["stdout"]).group(1)  # type: ignore[union-attr]
            evidence = b"human knowledge supporting evidence\n"
            sha = __import__("hashlib").sha256(evidence).hexdigest()
            admitted = self._helper_json(
                home,
                {
                    "op": "run_core",
                    "store_id": store_id,
                    "module": "dogfood.llm_wiki.cli",
                    "args": ["ingest", "__LLM_WIKI_UPLOAD_0__", "--topic", topic_id],
                    "uploads": [{"token": "__LLM_WIKI_UPLOAD_0__", "name": "hk.md", "size": len(evidence), "sha256": sha}],
                },
                evidence,
            )
            source_match = re.search(r"source=(src-[0-9A-Za-z-]+)", admitted["stdout"])
            if source_match is None:
                source_match = re.search(r"source_id=(src-[0-9A-Za-z-]+)", admitted["stdout"])
            self.assertIsNotNone(source_match, admitted)
            source_id = source_match.group(1)  # type: ignore[union-attr]

            saved = self._helper_json(
                home,
                {
                    "op": "save_human_knowledge",
                    "store_id": store_id,
                    "title": "Decision",
                    "statement": "Project A owns this decision.",
                    "reasoning": "Explicitly confirmed.",
                    "source_ids": [source_id],
                    "supersedes_knowledge_id": "",
                },
            )
            self.assertTrue(saved["ok"], saved)

            exported_a = self._helper(home, {"op": "snapshot_export", "store_id": store_id})
            exported_b = self._helper(home, {"op": "snapshot_export", "store_id": other_id})
            replica_a = base / "replica-a"
            replica_b = base / "replica-b"
            read_snapshot(io.BytesIO(exported_a.stdout), replica_a, preserve_host_local=False)
            read_snapshot(io.BytesIO(exported_b.stdout), replica_b, preserve_host_local=False)
            self.assertTrue(list((replica_a / "human-knowledge").glob("*.json")))
            self.assertFalse(list((replica_b / "human-knowledge").glob("*.json")))

    def test_remote_helper_rejects_model_call_and_arbitrary_module(self) -> None:
        with tempfile.TemporaryDirectory(prefix="remote-deny-") as tmp:
            home = Path(tmp) / "authority"
            created = self._helper_json(home, {"op": "create_store", "display_name": "deny", "bootstrap": False})
            store_id = created["store"]["store_id"]
            ask = self._helper_json(home, {"op": "run_core", "store_id": store_id, "module": "dogfood.llm_wiki.cli", "args": ["ask", "hello"]})
            arbitrary = self._helper_json(home, {"op": "run_core", "store_id": store_id, "module": "os", "args": ["system", "id"]})
            self.assertFalse(ask["ok"])
            self.assertIn("not_allowed", ask["error"])
            self.assertFalse(arbitrary["ok"])
            self.assertIn("not_allowed", arbitrary["error"])


if __name__ == "__main__":
    unittest.main()
