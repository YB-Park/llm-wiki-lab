from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import BinaryIO

from .integrity import audit_alpha_integrity
from .remote_snapshot import read_snapshot
from .writer_lock import LOCK_FILE, store_writer_lock

_ALLOWED_ATTACH_ENTRIES = {
    "config.json",
    "manifest.jsonl",
    "raw",
    "workspace-opt-in.json",
    LOCK_FILE,
}


class RemoteAttachError(RuntimeError):
    pass


def _regular_file(path: Path) -> bool:
    return path.exists() and not path.is_symlink() and path.is_file()


def _regular_dir(path: Path) -> bool:
    return path.exists() and not path.is_symlink() and path.is_dir()


def assert_empty_attach_destination(root: Path) -> None:
    root = Path(root)
    if os.name != "posix":
        raise RemoteAttachError("remote_attach_linux_workspace_host_required")
    if not _regular_dir(root):
        raise RemoteAttachError("remote_attach_requires_initialized_empty_local_memory")
    config = root / "config.json"
    manifest = root / "manifest.jsonl"
    raw = root / "raw"
    opt_in = root / "workspace-opt-in.json"
    if not _regular_file(config) or not _regular_file(manifest) or not _regular_dir(raw) or not _regular_file(opt_in):
        raise RemoteAttachError("remote_attach_requires_initialized_empty_local_memory")
    if manifest.stat().st_size != 0 or any(raw.iterdir()):
        raise RemoteAttachError("remote_attach_requires_empty_local_memory")
    if any(child.name not in _ALLOWED_ATTACH_ENTRIES for child in root.iterdir()):
        raise RemoteAttachError("remote_attach_requires_empty_local_memory")
    if audit_alpha_integrity(root).get("ok") is not True:
        raise RemoteAttachError("remote_attach_local_integrity_failed")


def import_attached_snapshot(stream: BinaryIO, root: Path) -> dict:
    root = Path(root)
    # The stable writer rendezvous is acquired before the final emptiness check.
    # On POSIX the root may then be atomically exchanged while this descriptor
    # remains locked on the old inode; no pre-existing core writer can overlap
    # the attach. Once the new root is visible, attach has no further Wiki write.
    with store_writer_lock(root):
        assert_empty_attach_destination(root)
        return read_snapshot(stream, root, preserve_host_local=True)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-remote-attach-import")
    p.add_argument("--root", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    manifest = import_attached_snapshot(sys.stdin.buffer, Path(args.root).expanduser())
    print(json.dumps({"status": "IMPORTED", "snapshot_id": manifest["snapshot_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
