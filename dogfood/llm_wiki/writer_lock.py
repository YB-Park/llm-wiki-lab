from __future__ import annotations

import errno
import functools
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, ParamSpec, TypeVar

from .private_fs import PRIVATE_FILE_MODE, ensure_private_directory, restrict_private_file

LOCK_FILE = ".writer.lock"
DEFAULT_TIMEOUT_SECONDS = 5.0
POLL_SECONDS = 0.025

P = ParamSpec("P")
R = TypeVar("R")


def _open_lock_file(root: Path) -> int:
    ensure_private_directory(root)
    path = root / LOCK_FILE
    restrict_private_file(path)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, PRIVATE_FILE_MODE)
    try:
        if os.fstat(fd).st_size == 0:
            # Windows byte-range locking needs at least one byte. The byte has
            # no semantic meaning; lock ownership lives in the OS, not here.
            os.write(fd, b"\0")
            os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        restrict_private_file(path)
        return fd
    except Exception:
        os.close(fd)
        raise


def _try_lock(fd: int) -> bool:
    if os.name == "posix":
        import fcntl

        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            return False

    if os.name == "nt":
        import msvcrt

        os.lseek(fd, 0, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return True
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                return False
            raise

    raise RuntimeError("writer_lock_unsupported_platform")


def _unlock(fd: int) -> None:
    if os.name == "posix":
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_UN)
        return

    if os.name == "nt":
        import msvcrt

        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        return

    raise RuntimeError("writer_lock_unsupported_platform")


@contextmanager
def store_writer_lock(root: Path, *, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> Iterator[None]:
    """Serialize one Wiki read/validate/write semantic mutation.

    The lock file is only a stable rendezvous point. Lock ownership is held by
    the operating system and is released automatically when the process/file
    descriptor dies, so a leftover file is not stale lock state.
    """
    if timeout_seconds < 0:
        raise ValueError("writer_lock_timeout_negative")

    fd = _open_lock_file(root)
    deadline = time.monotonic() + timeout_seconds
    acquired = False
    try:
        while True:
            if _try_lock(fd):
                acquired = True
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("wiki_writer_busy")
            time.sleep(POLL_SECONDS)
        yield
    finally:
        try:
            if acquired:
                _unlock(fd)
        finally:
            os.close(fd)


def serialized_writer(fn: Callable[P, R]) -> Callable[P, R]:
    """Decorate a public mutation whose first argument is the Wiki root Path."""

    @functools.wraps(fn)
    def wrapped(root: Path, *args: P.args, **kwargs: P.kwargs) -> R:
        with store_writer_lock(root):
            return fn(root, *args, **kwargs)

    return wrapped
