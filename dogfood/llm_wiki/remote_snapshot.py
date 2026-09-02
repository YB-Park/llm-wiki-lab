from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from .integrity import audit_alpha_integrity
from .private_fs import ensure_private_directory, tighten_workspace_permissions, write_private_bytes

SNAPSHOT_FORMAT = "LLM-WIKI-PORTABLE-SNAPSHOT-v1"
SNAPSHOT_MAGIC = (SNAPSHOT_FORMAT + "\n").encode("ascii")
MAX_HEADER_BYTES = 8 * 1024 * 1024
MAX_ENTRY_COUNT = 200_000

# Frozen by E026 S0-A. Additions require explicit portability evidence.
PORTABLE_FILES = (
    "config.json",
    "manifest.jsonl",
    "provenance.jsonl",
    "topics.json",
    "agent-state.json",
    "workload-events.jsonl",
    "retrieval-shadow-events.jsonl",
)
PORTABLE_DIRS = (
    "raw",
    "human-knowledge",
    "agent-wiki",
)

# Host-local authority/runtime. These are deliberately absent from snapshots.
HOST_LOCAL_FILES = (
    "workspace-opt-in.json",
)
EPHEMERAL_FILES = (
    ".writer.lock",
)


class SnapshotError(RuntimeError):
    pass


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _entry_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise SnapshotError("snapshot_path_invalid")
    if any(not part or "\\" in part or "\x00" in part for part in path.parts):
        raise SnapshotError("snapshot_path_invalid")
    return path


def _portable_file_paths(root: Path) -> list[Path]:
    rows: list[Path] = []
    for name in PORTABLE_FILES:
        path = root / name
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise SnapshotError(f"portable_file_not_regular:{name}")
            rows.append(path)

    for name in PORTABLE_DIRS:
        directory = root / name
        if not directory.exists():
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise SnapshotError(f"portable_directory_invalid:{name}")
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise SnapshotError(f"portable_symlink_forbidden:{path.relative_to(root).as_posix()}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise SnapshotError(f"portable_entry_not_regular:{path.relative_to(root).as_posix()}")
            rows.append(path)
    return sorted(rows, key=lambda item: item.relative_to(root).as_posix())


def snapshot_manifest(root: Path) -> dict:
    root = Path(root)
    report = audit_alpha_integrity(root)
    if report.get("ok") is not True:
        raise SnapshotError("snapshot_source_integrity_failed")

    entries = []
    for path in _portable_file_paths(root):
        payload = path.read_bytes()
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": len(payload),
                "sha256": _sha256_bytes(payload),
            }
        )
    identity_payload = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "format": SNAPSHOT_FORMAT,
        "snapshot_id": hashlib.sha256(identity_payload).hexdigest(),
        "entries": entries,
    }


def write_snapshot(root: Path, stream: BinaryIO) -> dict:
    root = Path(root)
    manifest = snapshot_manifest(root)
    stream.write(SNAPSHOT_MAGIC)
    stream.write(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    stream.write(b"\n")
    for row in manifest["entries"]:
        stream.write((root / PurePosixPath(row["path"])).read_bytes())
    if hasattr(stream, "flush"):
        stream.flush()
    return manifest


def _read_header(stream: BinaryIO) -> dict:
    magic = stream.readline(len(SNAPSHOT_MAGIC) + 1)
    if magic != SNAPSHOT_MAGIC:
        raise SnapshotError("snapshot_magic_invalid")
    header = stream.readline(MAX_HEADER_BYTES + 1)
    if not header.endswith(b"\n") or len(header) > MAX_HEADER_BYTES:
        raise SnapshotError("snapshot_header_invalid")
    try:
        manifest = json.loads(header.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotError("snapshot_header_invalid") from exc
    if not isinstance(manifest, dict) or manifest.get("format") != SNAPSHOT_FORMAT:
        raise SnapshotError("snapshot_format_invalid")
    entries = manifest.get("entries")
    snapshot_id = str(manifest.get("snapshot_id") or "")
    if not isinstance(entries, list) or len(entries) > MAX_ENTRY_COUNT or len(snapshot_id) != 64:
        raise SnapshotError("snapshot_manifest_invalid")

    normalized = []
    seen: set[str] = set()
    for row in entries:
        if not isinstance(row, dict) or set(row) != {"path", "size", "sha256"}:
            raise SnapshotError("snapshot_entry_invalid")
        rel = _entry_path(str(row["path"]))
        rel_text = rel.as_posix()
        if rel_text in seen:
            raise SnapshotError("snapshot_entry_duplicate")
        seen.add(rel_text)
        if rel.parts[0] not in set(PORTABLE_FILES) | set(PORTABLE_DIRS):
            raise SnapshotError("snapshot_entry_outside_allowlist")
        if rel.parts[0] in PORTABLE_FILES and len(rel.parts) != 1:
            raise SnapshotError("snapshot_entry_outside_allowlist")
        try:
            size = int(row["size"])
        except (TypeError, ValueError) as exc:
            raise SnapshotError("snapshot_entry_invalid") from exc
        sha = str(row["sha256"])
        if size < 0 or len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
            raise SnapshotError("snapshot_entry_invalid")
        normalized.append({"path": rel_text, "size": size, "sha256": sha})

    identity_payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected_id = hashlib.sha256(identity_payload).hexdigest()
    if snapshot_id != expected_id:
        raise SnapshotError("snapshot_identity_mismatch")
    return {"format": SNAPSHOT_FORMAT, "snapshot_id": snapshot_id, "entries": normalized}


def _copy_host_local_files(source: Path, destination: Path) -> None:
    if not source.exists() or source.is_symlink() or not source.is_dir():
        return
    for name in HOST_LOCAL_FILES:
        path = source / name
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            raise SnapshotError(f"host_local_file_invalid:{name}")
        write_private_bytes(destination / name, path.read_bytes())


def _activate_tree(staged: Path, destination: Path) -> None:
    ensure_private_directory(destination.parent)
    backup = destination.parent / f".{destination.name}.remote-backup-{os.getpid()}"
    if backup.exists():
        shutil.rmtree(backup, ignore_errors=True)
    moved_old = False
    try:
        if destination.exists():
            if destination.is_symlink() or not destination.is_dir():
                raise SnapshotError("snapshot_destination_invalid")
            os.replace(destination, backup)
            moved_old = True
        os.replace(staged, destination)
    except Exception:
        if moved_old and backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup)


def read_snapshot(
    stream: BinaryIO,
    destination: Path,
    *,
    preserve_host_local: bool = True,
    activate: bool = True,
) -> dict:
    destination = Path(destination)
    manifest = _read_header(stream)
    ensure_private_directory(destination.parent)
    staged = Path(tempfile.mkdtemp(prefix=f".{destination.name}.remote-stage-", dir=destination.parent))
    published = False
    try:
        # Directories are part of the store shape even when they are empty.
        # In particular, an initialized empty Wiki has an empty private raw/
        # directory; a file-only stream must reconstruct that shape before the
        # integrity gate so a brand-new remote project remains portable.
        for name in PORTABLE_DIRS:
            ensure_private_directory(staged / name)

        for row in manifest["entries"]:
            remaining = int(row["size"])
            chunks: list[bytes] = []
            while remaining:
                chunk = stream.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise SnapshotError("snapshot_truncated")
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
            if _sha256_bytes(payload) != row["sha256"]:
                raise SnapshotError(f"snapshot_entry_hash_mismatch:{row['path']}")
            target = staged.joinpath(*PurePosixPath(row["path"]).parts)
            write_private_bytes(target, payload)

        trailing = stream.read(1)
        if trailing:
            raise SnapshotError("snapshot_trailing_bytes")

        tighten_workspace_permissions(staged)
        report = audit_alpha_integrity(staged)
        if report.get("ok") is not True:
            raise SnapshotError("snapshot_materialized_integrity_failed")

        if preserve_host_local:
            _copy_host_local_files(destination, staged)
            tighten_workspace_permissions(staged)

        if activate:
            _activate_tree(staged, destination)
            published = True
        return manifest
    finally:
        if not published and staged.exists():
            shutil.rmtree(staged, ignore_errors=True)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-remote-snapshot")
    sub = p.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export")
    export.add_argument("--root", required=True)
    imp = sub.add_parser("import")
    imp.add_argument("--root", required=True)
    imp.add_argument("--replace-host-local", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "export":
        write_snapshot(Path(args.root).expanduser(), sys.stdout.buffer)
        return 0
    if args.command == "import":
        manifest = read_snapshot(
            sys.stdin.buffer,
            Path(args.root).expanduser(),
            preserve_host_local=not args.replace_host_local,
        )
        print(json.dumps({"status": "IMPORTED", "snapshot_id": manifest["snapshot_id"]}, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
