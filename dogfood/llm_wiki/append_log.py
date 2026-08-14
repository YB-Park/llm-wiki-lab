from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LOG_CLEAN = "clean"
LOG_TORN_TAIL = "torn_tail"
LOG_CORRUPT_PREFIX = "corrupt_prefix"


class JsonlLogError(RuntimeError):
    """Base class for canonical JSONL integrity failures."""


class JsonlTornTailError(JsonlLogError):
    """The durable prefix is valid but final uncommitted bytes are present."""


class JsonlCorruptPrefixError(JsonlLogError):
    """A newline-committed record in the durable prefix is structurally corrupt."""


@dataclass(frozen=True)
class JsonlIntegrityReport:
    status: str
    committed_records: int
    blank_lines: int
    durable_bytes: int
    torn_tail_bytes: int
    corrupt_line: int | None

    @property
    def ok(self) -> bool:
        return self.status == LOG_CLEAN

    def as_safe_dict(self) -> dict[str, int | str | bool | None]:
        """Return aggregate-only diagnostics suitable for a Doctor-style surface."""
        return {
            "status": self.status,
            "committed_records": self.committed_records,
            "blank_lines": self.blank_lines,
            "durable_bytes": self.durable_bytes,
            "torn_tail_bytes": self.torn_tail_bytes,
            "corrupt_line": self.corrupt_line,
            "ok": self.ok,
        }


@dataclass(frozen=True)
class CanonicalLogIntegrityReport:
    manifest: JsonlIntegrityReport
    provenance: JsonlIntegrityReport

    @property
    def ok(self) -> bool:
        return self.manifest.ok and self.provenance.ok

    def as_safe_dict(self) -> dict[str, Any]:
        return {
            "manifest": self.manifest.as_safe_dict(),
            "provenance": self.provenance.as_safe_dict(),
            "ok": self.ok,
        }


def _scan_jsonl(path: Path) -> tuple[JsonlIntegrityReport, list[dict]]:
    if not path.exists():
        return (
            JsonlIntegrityReport(
                status=LOG_CLEAN,
                committed_records=0,
                blank_lines=0,
                durable_bytes=0,
                torn_tail_bytes=0,
                corrupt_line=None,
            ),
            [],
        )

    data = path.read_bytes()
    if not data:
        return (
            JsonlIntegrityReport(
                status=LOG_CLEAN,
                committed_records=0,
                blank_lines=0,
                durable_bytes=0,
                torn_tail_bytes=0,
                corrupt_line=None,
            ),
            [],
        )

    if data.endswith(b"\n"):
        durable = data
        tail = b""
    else:
        last_newline = data.rfind(b"\n")
        if last_newline < 0:
            durable = b""
            tail = data
        else:
            durable = data[: last_newline + 1]
            tail = data[last_newline + 1 :]

    rows: list[dict] = []
    blank_lines = 0
    committed_records = 0
    # `durable` always ends in newline, so the final split segment is empty.
    for line_number, raw_line in enumerate(durable.split(b"\n")[:-1], start=1):
        if not raw_line.strip():
            blank_lines += 1
            continue
        try:
            text = raw_line.decode("utf-8", errors="strict")
            row = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return (
                JsonlIntegrityReport(
                    status=LOG_CORRUPT_PREFIX,
                    committed_records=committed_records,
                    blank_lines=blank_lines,
                    durable_bytes=len(durable),
                    torn_tail_bytes=len(tail),
                    corrupt_line=line_number,
                ),
                [],
            )
        if not isinstance(row, dict):
            return (
                JsonlIntegrityReport(
                    status=LOG_CORRUPT_PREFIX,
                    committed_records=committed_records,
                    blank_lines=blank_lines,
                    durable_bytes=len(durable),
                    torn_tail_bytes=len(tail),
                    corrupt_line=line_number,
                ),
                [],
            )
        rows.append(row)
        committed_records += 1

    status = LOG_TORN_TAIL if tail else LOG_CLEAN
    return (
        JsonlIntegrityReport(
            status=status,
            committed_records=committed_records,
            blank_lines=blank_lines,
            durable_bytes=len(durable),
            torn_tail_bytes=len(tail),
            corrupt_line=None,
        ),
        rows,
    )


def inspect_jsonl(path: Path) -> JsonlIntegrityReport:
    """Read-only structural integrity classification with no content exposure."""
    report, _ = _scan_jsonl(path)
    return report


def read_committed_jsonl(path: Path) -> list[dict]:
    """Replay only fully newline-committed JSON object records.

    Any final bytes without a newline are intentionally *not* treated as a
    durable event, even when they happen to form valid JSON. Semantic readers
    fail closed so a torn append is never silently accepted or repaired.
    """
    report, rows = _scan_jsonl(path)
    if report.status == LOG_TORN_TAIL:
        raise JsonlTornTailError("canonical_jsonl_torn_tail")
    if report.status == LOG_CORRUPT_PREFIX:
        raise JsonlCorruptPrefixError("canonical_jsonl_corrupt_prefix")
    return rows


def _fsync_parent_if_supported(path: Path) -> None:
    if os.name != "posix" or not hasattr(os, "O_DIRECTORY"):
        return
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def append_jsonl_record(path: Path, row: dict) -> None:
    """Append one newline-committed JSON object and flush it before return.

    Existing torn/corrupt logs are never appended through. This function does
    not truncate, repair, or invent semantic events.
    """
    if not isinstance(row, dict):
        raise TypeError("canonical_jsonl_record_must_be_object")
    report = inspect_jsonl(path)
    if report.status == LOG_TORN_TAIL:
        raise JsonlTornTailError("canonical_jsonl_torn_tail")
    if report.status == LOG_CORRUPT_PREFIX:
        raise JsonlCorruptPrefixError("canonical_jsonl_corrupt_prefix")

    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    payload = (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o666)
    try:
        view = memoryview(payload)
        written = 0
        while written < len(payload):
            count = os.write(fd, view[written:])
            if count <= 0:
                raise OSError("canonical_jsonl_append_short_write")
            written += count
        os.fsync(fd)
    finally:
        os.close(fd)
    if not existed:
        _fsync_parent_if_supported(path)


def discard_torn_tail(path: Path) -> int:
    """Explicitly discard only an uncommitted final tail.

    This is recovery, not normal replay. Corruption in the newline-committed
    prefix is never truncated by this API. Returns the number of discarded
    bytes; a clean log is an idempotent no-op.
    """
    report = inspect_jsonl(path)
    if report.status == LOG_CORRUPT_PREFIX:
        raise JsonlCorruptPrefixError("canonical_jsonl_corrupt_prefix")
    if report.status == LOG_CLEAN:
        return 0

    discarded = report.torn_tail_bytes
    with path.open("r+b") as handle:
        handle.truncate(report.durable_bytes)
        handle.flush()
        os.fsync(handle.fileno())
    return discarded


def verify_canonical_log_integrity(root: Path) -> CanonicalLogIntegrityReport:
    """Audit canonical append logs without exposing identities or content."""
    return CanonicalLogIntegrityReport(
        manifest=inspect_jsonl(root / "manifest.jsonl"),
        provenance=inspect_jsonl(root / "provenance.jsonl"),
    )
