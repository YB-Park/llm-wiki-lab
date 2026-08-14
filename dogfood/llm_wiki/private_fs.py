from __future__ import annotations

import os
from pathlib import Path

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


def write_private_bytes(path: Path, payload: bytes) -> None:
    ensure_private_directory(path.parent)
    restrict_private_file(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, PRIVATE_FILE_MODE)
    try:
        _write_all(fd, payload)
    finally:
        os.close(fd)
    restrict_private_file(path)


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
    ):
        restrict_private_file(root / name)
