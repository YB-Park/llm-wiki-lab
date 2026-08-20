from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SIGNAL = REPO / "remote-lab" / "e024-q1-execute.json"
MANIFEST = HERE / "q1-prereg-manifest.json"
SOURCE_LOCK = HERE / "q1-source-lock-v1.json"
EXECUTE_PATH = "remote-lab/e024-q1-execute.json"


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"E024-Q1-LOCK-STOP git_failed:{' '.join(args)}")
    return proc.stdout.strip()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    if not SIGNAL.exists():
        raise SystemExit("E024-Q1-LOCK-STOP execution_signal_missing")

    signal = json.loads(SIGNAL.read_text(encoding="utf-8"))
    required_signal_keys = {"execute", "frozen_parent_sha", "prereg_manifest_sha256", "request_id"}
    if set(signal) != required_signal_keys:
        raise SystemExit(f"E024-Q1-LOCK-STOP execution_signal_shape:{sorted(signal)}")
    if signal["execute"] is not True or signal["request_id"] != "e024-q1-token-firewall-v0":
        raise SystemExit("E024-Q1-LOCK-STOP execution_signal_invalid")

    head = git("rev-parse", "HEAD")
    parent = git("rev-parse", "HEAD^")
    if parent != signal["frozen_parent_sha"]:
        raise SystemExit(f"E024-Q1-LOCK-STOP frozen_parent_mismatch:{parent}")
    changed = [line for line in git("diff", "--name-only", parent, head).splitlines() if line.strip()]
    if changed != [EXECUTE_PATH]:
        raise SystemExit(f"E024-Q1-LOCK-STOP execution_commit_scope:{changed}")

    manifest_digest = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    if manifest_digest != signal["prereg_manifest_sha256"]:
        raise SystemExit(f"E024-Q1-LOCK-STOP prereg_manifest_mismatch:{manifest_digest}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("format") != "E024-Q1-prereg-manifest-v1":
        raise SystemExit("E024-Q1-LOCK-STOP prereg_manifest_format")
    for rel, expected in manifest["sha256"].items():
        path = REPO / rel
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise SystemExit(f"E024-Q1-LOCK-STOP frozen_asset_mismatch:{rel}:{digest}")

    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    if source_lock.get("format") != "E024-Q1-source-lock-v1":
        raise SystemExit("E024-Q1-LOCK-STOP source_lock_format")
    if source_lock.get("base_main_commit_sha") != "ef8869acc688e6b52b87570376560d7495c77cfa":
        raise SystemExit("E024-Q1-LOCK-STOP base_main_sha")
    for rel, expected_blob in source_lock["imported_git_blobs"].items():
        actual_blob = git_blob_sha1(REPO / rel)
        if actual_blob != expected_blob:
            raise SystemExit(f"E024-Q1-LOCK-STOP imported_blob_mismatch:{rel}:{actual_blob}")

    print("E024 Q1 execution source lock: PASS")
    print(json.dumps({
        "head_sha": head,
        "frozen_parent_sha": parent,
        "changed_paths": changed,
        "prereg_manifest_sha256": manifest_digest,
        "imported_blob_count": len(source_lock["imported_git_blobs"]),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
