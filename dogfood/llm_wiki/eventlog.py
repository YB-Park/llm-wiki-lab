from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JsonlIntegrity:
    complete_records: int
    torn_tail: bool
    corrupt_records: int
    ok: bool


@dataclass(frozen=True)
class CanonicalLogIntegrityReport:
    manifest_records: int
    manifest_torn_tail: bool
    manifest_corrupt_records: int
    provenance_records: int
    provenance_torn_tail: bool
    provenance_corrupt_records: int
    ok: bool


def _inspect_jsonl(path: Path) -> tuple[JsonlIntegrity, list[dict]]:
    if not path.exists():
        return JsonlIntegrity(complete_records=0, torn_tail=False, corrupt_records=0, ok=True), []

    data = path.read_bytes()
    if not data:
        return JsonlIntegrity(complete_records=0, torn_tail=False, corrupt_records=0, ok=True), []

    parts = data.split(b"\n")
    if data.endswith(b"\n"):
        complete_lines = parts[:-1]
        tail = b""
    else:
        complete_lines = parts[:-1]
        tail = parts[-1]

    records: list[dict] = []
    corrupt_records = 0
    for raw_line in complete_lines:
        if not raw_line:
            corrupt_records += 1
            continue
        try:
            text = raw_line.decode("utf-8")
            value = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            corrupt_records += 1
            continue
        if not isinstance(value, dict):
            corrupt_records += 1
            continue
        records.append(value)

    torn_tail = bool(tail)
    integrity = JsonlIntegrity(
        complete_records=len(records),
        torn_tail=torn_tail,
        corrupt_records=corrupt_records,
        ok=(not torn_tail and corrupt_records == 0),
    )
    return integrity, records


def inspect_jsonl(path: Path) -> JsonlIntegrity:
    """Return counts/status only; never expose record bodies or mutate the log."""
    integrity, _ = _inspect_jsonl(path)
    return integrity


def read_jsonl_records(path: Path, *, log_label: str) -> list[dict]:
    """Strict canonical replay.

    A valid durable prefix may be diagnosed by `inspect_jsonl`, but semantic
    replay never continues past a torn/corrupt log. A final JSON value without
    its terminating newline is deliberately considered uncommitted/torn.
    """
    integrity, records = _inspect_jsonl(path)
    if integrity.torn_tail:
        raise RuntimeError(f"{log_label}_torn_tail")
    if integrity.corrupt_records:
        raise RuntimeError(f"{log_label}_corrupt_record")
    return records


def append_jsonl_record(path: Path, row: dict, *, log_label: str) -> None:
    """Append one canonical newline-terminated JSON object and fsync it.

    This is not a multi-writer transaction protocol. It only prevents the core
    from appending on top of a log already known to be torn/corrupt and makes a
    completed single append durable before success is returned.
    """
    if not isinstance(row, dict):
        raise TypeError("canonical_log_record_must_be_object")
    existing = inspect_jsonl(path)
    if existing.torn_tail:
        raise RuntimeError(f"{log_label}_torn_tail")
    if existing.corrupt_records:
        raise RuntimeError(f"{log_label}_corrupt_record")

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    with path.open("ab", buffering=0) as handle:
        written = handle.write(payload)
        if written != len(payload):
            try:
                os.fsync(handle.fileno())
            finally:
                raise RuntimeError(f"{log_label}_partial_append")
        os.fsync(handle.fileno())


def verify_canonical_log_integrity(root: Path) -> CanonicalLogIntegrityReport:
    manifest = inspect_jsonl(root / "manifest.jsonl")
    provenance = inspect_jsonl(root / "provenance.jsonl")
    return CanonicalLogIntegrityReport(
        manifest_records=manifest.complete_records,
        manifest_torn_tail=manifest.torn_tail,
        manifest_corrupt_records=manifest.corrupt_records,
        provenance_records=provenance.complete_records,
        provenance_torn_tail=provenance.torn_tail,
        provenance_corrupt_records=provenance.corrupt_records,
        ok=manifest.ok and provenance.ok,
    )
