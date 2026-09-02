from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.private_fs import write_private_text
from dogfood.llm_wiki.remote_helper import HELPER_PROTOCOL
from dogfood.llm_wiki.remote_snapshot import read_snapshot, snapshot_manifest, write_snapshot
from dogfood.llm_wiki.store import ensure_workspace, ingest_file

HELPER_COMMAND = 'set -eu; root="${XDG_DATA_HOME:-$HOME/.local/share}/llm-wiki/remote-runtime/current"; PYTHONPATH="$root" python3 -m dogfood.llm_wiki.remote_helper'


def ssh_target() -> str:
    value = os.environ.get("LLM_WIKI_SSH_TARGET", "").strip()
    if not value or any(ch.isspace() for ch in value):
        raise RuntimeError("LLM_WIKI_SSH_TARGET must be one configured OpenSSH target alias")
    return value


def helper(request: dict, payload: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    body = (json.dumps({"protocol": HELPER_PROTOCOL, **request}, separators=(",", ":")) + "\n").encode("utf-8") + payload
    return subprocess.run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=5",
            "-T",
            ssh_target(),
            HELPER_COMMAND,
        ],
        input=body,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )


def helper_json(request: dict, payload: bytes = b"") -> dict:
    proc = helper(request, payload)
    if proc.returncode not in (0, 2):
        raise RuntimeError(f"ssh helper failed rc={proc.returncode}: {proc.stderr.decode('utf-8', errors='replace')[-400:]}")
    try:
        row = json.loads(proc.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("ssh helper returned invalid JSON") from exc
    return row


def fixture(base: Path) -> tuple[Path, str, bytes]:
    root = base / "local-wiki"
    source = base / "initial.md"
    initial = "초기 원격 메모리\r\ncedar quota=10\r\n".encode("utf-8")
    source.write_bytes(initial)
    ensure_workspace(root)
    topic = create_topic(root, "SSH S1")
    ingest_file(root, source, topic_id=topic["topic_id"])
    write_private_text(root / "workspace-opt-in.json", '{"host_local":true}\n')
    return root, str(topic["topic_id"]), initial


def bootstrap(store_id: str, snapshot: bytes) -> dict:
    row = helper_json({"op": "bootstrap_store", "store_id": store_id}, snapshot)
    if row.get("ok") is not True:
        raise RuntimeError(f"bootstrap failed: {row}")
    return row


def export_store(store_id: str) -> bytes:
    proc = helper({"op": "snapshot_export", "store_id": store_id})
    if proc.returncode != 0:
        raise RuntimeError(f"snapshot export failed: {proc.stderr.decode('utf-8', errors='replace')[-400:]}")
    return proc.stdout


def remote_ingest(store_id: str, topic_id: str, name: str, payload: bytes) -> dict:
    token = "__LLM_WIKI_UPLOAD_0__"
    upload = {
        "token": token,
        "name": name,
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    row = helper_json(
        {
            "op": "run_core",
            "store_id": store_id,
            "module": "dogfood.llm_wiki.cli",
            "args": ["ingest", token, "--topic", topic_id],
            "uploads": [upload],
        },
        payload,
    )
    if row.get("ok") is not True:
        raise RuntimeError(f"remote ingest failed: {row}")
    match = re.search(r"source=(src-[0-9A-Za-z-]+)", str(row.get("stdout", "")))
    if match is None:
        raise RuntimeError("remote ingest returned no source identity")
    return row


def main() -> int:
    health = helper_json({"op": "health"})
    if health.get("ok") is not True or health.get("protocol") != HELPER_PROTOCOL or not str(health.get("platform", "")).startswith("linux"):
        raise RuntimeError(f"incompatible SSH authority helper: {health}")

    with tempfile.TemporaryDirectory(prefix="e026-s1-ssh-") as tmp:
        base = Path(tmp)
        local_root, topic_id, initial_bytes = fixture(base)
        stream = io.BytesIO()
        local_manifest = write_snapshot(local_root, stream)
        snapshot_bytes = stream.getvalue()

        a = helper_json({"op": "create_store", "display_name": "same-project-bytes", "bootstrap": True})
        b = helper_json({"op": "create_store", "display_name": "same-project-bytes", "bootstrap": True})
        if a.get("ok") is not True or b.get("ok") is not True:
            raise RuntimeError(f"store creation failed: {a} {b}")
        store_a = str(a["store"]["store_id"])
        store_b = str(b["store"]["store_id"])
        if store_a == store_b:
            raise RuntimeError("opaque project stores collapsed to one identity")

        bootstrap_a = bootstrap(store_a, snapshot_bytes)
        bootstrap_b = bootstrap(store_b, snapshot_bytes)
        if bootstrap_a["snapshot_id"] != local_manifest["snapshot_id"] or bootstrap_b["snapshot_id"] != local_manifest["snapshot_id"]:
            raise RuntimeError("bootstrap snapshot identity mismatch")

        changed_bytes = "PC A 원격 전용 변경\r\ncedar quota=12\r\n".encode("utf-8")
        remote_ingest(store_a, topic_id, "changed.md", changed_bytes)

        replica_a = base / "replica-a"
        replica_b = base / "replica-b"
        manifest_a = read_snapshot(io.BytesIO(export_store(store_a)), replica_a, preserve_host_local=False)
        manifest_b = read_snapshot(io.BytesIO(export_store(store_b)), replica_b, preserve_host_local=False)
        if manifest_a["snapshot_id"] == manifest_b["snapshot_id"]:
            raise RuntimeError("independent project stores did not diverge after A-only write")
        if snapshot_manifest(replica_b)["snapshot_id"] != local_manifest["snapshot_id"]:
            raise RuntimeError("B changed after A-only write")
        if not audit_alpha_integrity(replica_a)["ok"] or not audit_alpha_integrity(replica_b)["ok"]:
            raise RuntimeError("replica integrity failed")
        if (replica_a / "workspace-opt-in.json").exists() or (replica_b / "workspace-opt-in.json").exists():
            raise RuntimeError("host-local workspace authority crossed SSH transport")

        raw_a = [path.read_bytes() for path in (replica_a / "raw").glob("*.txt")]
        raw_b = [path.read_bytes() for path in (replica_b / "raw").glob("*.txt")]
        if initial_bytes not in raw_a or initial_bytes not in raw_b:
            raise RuntimeError("initial CRLF bytes changed across SSH transport")
        if changed_bytes not in raw_a:
            raise RuntimeError("A remote write bytes missing after SSH transport")
        if changed_bytes in raw_b:
            raise RuntimeError("A remote write leaked into B project store")

        # Explicit multi-PC attach proof: PC B starts with a fresh local authority
        # epoch, selects store A exactly, materializes its verified snapshot, and
        # keeps its own host-local workspace opt-in. No content/repo auto-linking.
        pc_b_attached = base / "pc-b-attached"
        ensure_workspace(pc_b_attached)
        pc_b_opt_in = b'{"pc":"B","fresh_authority_epoch":true}\n'
        write_private_text(pc_b_attached / "workspace-opt-in.json", pc_b_opt_in.decode("utf-8"))
        if (pc_b_attached / "manifest.jsonl").read_bytes() != b"":
            raise RuntimeError("PC B attach fixture was not locally empty")
        attached_manifest = read_snapshot(
            io.BytesIO(export_store(store_a)),
            pc_b_attached,
            preserve_host_local=True,
        )
        if attached_manifest["snapshot_id"] != manifest_a["snapshot_id"]:
            raise RuntimeError("PC B explicit attach did not materialize exact store A snapshot")
        if (pc_b_attached / "workspace-opt-in.json").read_bytes() != pc_b_opt_in:
            raise RuntimeError("PC B host-local authority epoch was replaced during attach")
        attached_raw = [path.read_bytes() for path in (pc_b_attached / "raw").glob("*.txt")]
        if changed_bytes not in attached_raw:
            raise RuntimeError("PC B attached copy is missing PC A remote evidence")

        pc_b_write = "PC B attach 후 원격 저장\r\ncedar quota=14\r\n".encode("utf-8")
        remote_ingest(store_a, topic_id, "pc-b-write.md", pc_b_write)

        # PC A explicitly refreshes the same exact remote store and sees PC B's
        # write. Independent store B remains untouched.
        pc_a_refreshed = base / "pc-a-refreshed"
        latest_a = read_snapshot(io.BytesIO(export_store(store_a)), pc_a_refreshed, preserve_host_local=False)
        latest_b = base / "independent-b-refreshed"
        read_snapshot(io.BytesIO(export_store(store_b)), latest_b, preserve_host_local=False)
        pc_a_raw = [path.read_bytes() for path in (pc_a_refreshed / "raw").glob("*.txt")]
        independent_b_raw = [path.read_bytes() for path in (latest_b / "raw").glob("*.txt")]
        if pc_b_write not in pc_a_raw:
            raise RuntimeError("PC A refresh did not observe PC B write to the attached project")
        if pc_b_write in independent_b_raw or changed_bytes in independent_b_raw:
            raise RuntimeError("attached project writes leaked into independent store B")
        if latest_a["snapshot_id"] == manifest_a["snapshot_id"]:
            raise RuntimeError("PC B write did not advance exact attached project snapshot")

        listed = helper_json({"op": "list_stores"})
        ids = {str(row.get("store_id", "")) for row in listed.get("stores", [])}
        if store_a not in ids or store_b not in ids:
            raise RuntimeError("remote catalog lost project store identity")

        result = {
            "E026_S1_REAL_SSH_TRANSPORT": "PASS",
            "model_calls": 0,
            "transport": "openssh",
            "host_key_verification": "client_config_strict",
            "batch_mode": True,
            "opaque_store_identity": "distinct",
            "same_bytes_auto_link": False,
            "crlf_byte_preservation": True,
            "host_local_workspace_authority_transported": False,
            "cross_store_write_leak": False,
            "explicit_pc_b_attach_to_exact_store": True,
            "pc_b_host_local_authority_preserved": True,
            "pc_b_write_visible_after_pc_a_refresh": True,
            "independent_store_b_unchanged": True,
        }
        print("E026 S1 real SSH transport: PASS")
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
