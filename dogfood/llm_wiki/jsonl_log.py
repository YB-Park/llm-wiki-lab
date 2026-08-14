from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JsonlIntegrityReport:
    durable_records: int
    blank_records: int
    torn_tail_bytes: int
    corrupt_durable_records: int
    invalid_utf8_records: int
    invalid_json_records: int
    non_object_records: int
    status: str
    ok: bool


@dataclass(frozen=True)
class CanonicalLogsIntegrityReport:
    manifest: JsonlIntegrityReport
    provenance: JsonlIntegrityReport
    ok: bool


def _clean_report() -> JsonlIntegrityReport:
    return JsonlIntegrityReport(
        durable_records=0,
        blank_records=0,
        torn_tail_bytes=0,
        corrupt_durable_records=0,
        invalid_utf8_records=0,
        invalid_json_records=0,
        non_object_records=0,
        status="clean",
        ok=True,
    )


def _scan(path: Path) -> tuple[list[dict], JsonlIntegrityReport]:
    if not path.exists():
        return [], _clean_report()

    data = path.read_bytes()
    if not data:
        return [], _clean_report()

    # A canonical record is durable/replayable only after its terminating LF is
    # present. Anything after the final LF is an incomplete append, even when
    # those bytes happen to form valid JSON. This avoids guessing whether a
    # process died after writing payload bytes but before committing the record
    # boundary.
    if data.endswith(b"\n"):
        durable = data
        tail = b""
    else:
        last_lf = data.rfind(b"\n")
        if last_lf < 0:
            durable = b""
            tail = data
        else:
            durable = data[: last_lf + 1]
            tail = data[last_lf + 1 :]

    rows: list[dict] = []
    blank_records = 0
    invalid_utf8_records = 0
    invalid_json_records = 0
    non_object_records = 0

    # `durable` always ends with LF, so the final split item is empty.
    for raw_line in durable.split(b"\n")[:-1]:
        if not raw_line.strip():
            # Preserve compatibility with legacy logs whose readers ignored
            # blank lines. They are not semantic records and do not make the
            # log corrupt.
            blank_records += 1
            continue
        try:
            text = raw_line.decode("utf-8")
        except UnicodeDecodeError:
            invalid_utf8_records += 1
            continue
        try:
            row = json.loads(text)
        except json.JSONDecodeError:
            invalid_json_records += 1
            continue
        if not isinstance(row, dict):
            non_object_records += 1
            continue
        rows.append(row)

    corrupt = invalid_utf8_records + invalid_json_records + non_object_records
    torn_tail_bytes = len(tail)
    if corrupt:
        status = "corrupt_prefix"
    elif torn_tail_bytes:
        status = "torn_tail"
    else:
        status = "clean"

    report = JsonlIntegrityReport(
        durable_records=len(rows),
        blank_records=blank_records,
        torn_tail_bytes=torn_tail_bytes,
        corrupt_durable_records=corrupt,
        invalid_utf8_records=invalid_utf8_records,
        invalid_json_records=invalid_json_records,
        non_object_records=non_object_records,
        status=status,
        ok=status == "clean",
    )
    return rows, report


def audit_jsonl(path: Path) -> JsonlIntegrityReport:
    """Return count/status-only integrity information without record contents."""
    return _scan(path)[1]


def audit_canonical_logs(root: Path) -> CanonicalLogsIntegrityReport:
    """Audit canonical append logs without exposing local provenance details."""
    manifest = audit_jsonl(root / "manifest.jsonl")
    provenance = audit_jsonl(root / "provenance.jsonl")
    return CanonicalLogsIntegrityReport(
        manifest=manifest,
        provenance=provenance,
        ok=manifest.ok and provenance.ok,
    )


def read_jsonl_objects(path: Path, *, log_name: str) -> list[dict]:
    """Strict semantic replay of one canonical append log.

    Durable-prefix corruption has priority over a simultaneous torn tail because
    replaying any prefix that already contains a corrupt committed record is
    unsafe. No repair/truncation is attempted here.
    """
    rows, report = _scan(path)
    if report.corrupt_durable_records:
        raise RuntimeError(f"{log_name}_durable_prefix_corrupt")
    if report.torn_tail_bytes:
        raise RuntimeError(f"{log_name}_torn_tail")
    return rows


def append_jsonl_object(path: Path, row: dict) -> None:
    """Append one newline-terminated JSON object and request durable flush.

    The reader contract, not an assumption of magical filesystem atomicity,
    contains failures: a crash during this append may leave a torn final tail,
    which strict replay will detect and reject. Existing damaged logs are never
    extended automatically.
    """
    if not isinstance(row, dict):
        raise TypeError("jsonl_record_must_be_object")
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = audit_jsonl(path)
    if existing.corrupt_durable_records:
        raise RuntimeError("jsonl_append_blocked_corrupt_prefix")
    if existing.torn_tail_bytes:
        raise RuntimeError("jsonl_append_blocked_torn_tail")

    payload = (json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(path, flags, 0o600)
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(fd, payload[offset:])
            if written <= 0:
                raise OSError("jsonl_append_zero_write")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)
