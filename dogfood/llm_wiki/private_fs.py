from __future__ import annotations

import errno
import os
import tempfile
from pathlib import Path

from .workspace_loss import missing_manifest_is_state_loss

PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


def _is_posix() -> bool:
    return os.name == "posix"


def ensure_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if _is_posix():
        path.chmod(PRIVATE_DIR_MODE)


def restrict_private_file(path: Path) -> None:
    if _is_posix() and path.exists():
        path.chmod(PRIVATE_FILE_MODE)


def ensure_private_file(path: Path) -> None:
    ensure_private_directory(path.parent)
    if path.name == "manifest.jsonl" and not path.exists() and missing_manifest_is_state_loss(path.parent):
        raise RuntimeError("canonical_manifest_missing")
    restrict_private_file(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, PRIVATE_FILE_MODE)
    os.close(fd)
    restrict_private_file(path)


def _write_all(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(fd, payload[offset:])
        if written <= 0:
            raise OSError("private_file_zero_write")
        offset += written


def _fsync_directory(path: Path) -> None:
    """Request durability for a same-directory atomic replacement where supported."""
    if not _is_posix():
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        if exc.errno in {errno.EINVAL, errno.ENOTSUP, getattr(errno, "EOPNOTSUPP", errno.ENOTSUP)}:
            return
        raise
    try:
        try:
            os.fsync(fd)
        except OSError as exc:
            if exc.errno not in {errno.EINVAL, errno.ENOTSUP, getattr(errno, "EOPNOTSUPP", errno.ENOTSUP)}:
                raise
    finally:
        os.close(fd)


def write_private_bytes(path: Path, payload: bytes) -> None:
    """Replace a private file without exposing a partially written final path.

    Bytes are completed and fsynced in a same-directory temporary file before
    `os.replace` publishes them. This is not a multi-writer transaction or a
    cross-file WAL; it only prevents a failed pre-publication write from
    poisoning the final private/content-addressed path.
    """
    ensure_private_directory(path.parent)
    restrict_private_file(path)

    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    temp_path = Path(temp_name)
    published = False
    try:
        if _is_posix():
            os.fchmod(fd, PRIVATE_FILE_MODE)
        _write_all(fd, payload)
        os.fsync(fd)
        os.close(fd)
        fd = -1

        os.replace(temp_path, path)
        published = True
        restrict_private_file(path)
        _fsync_directory(path.parent)
    finally:
        if fd >= 0:
            os.close(fd)
        if not published:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def write_private_text(path: Path, text: str) -> None:
    write_private_bytes(path, text.encode("utf-8"))


def append_private_text(path: Path, text: str) -> None:
    ensure_private_directory(path.parent)
    restrict_private_file(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, PRIVATE_FILE_MODE)
    try:
        _write_all(fd, text.encode("utf-8"))
    finally:
        os.close(fd)
    restrict_private_file(path)


def tighten_workspace_permissions(root: Path) -> None:
    """Tighten known private Wiki artifacts without changing their contents."""
    if not root.exists():
        return
    ensure_private_directory(root)
    raw = root / "raw"
    if raw.exists():
        ensure_private_directory(raw)
        for child in raw.iterdir():
            if child.is_file():
                restrict_private_file(child)
    for name in (
        "config.json",
        "manifest.jsonl",
        "provenance.jsonl",
        "topics.json",
        "workload-events.jsonl",
        "retrieval-shadow-events.jsonl",
        "agent-state.json",
        ".writer.lock",
    ):
        restrict_private_file(root / name)
