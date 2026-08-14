from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .jsonl_log import append_jsonl_object, read_jsonl_objects
from .store import ensure_workspace, find_source, read_text

PROVENANCE_FILE = "provenance.jsonl"
PROVENANCE_SCHEMA = "llm-wiki-exact-provenance-v1"
LOCAL_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass(frozen=True)
class ExactProvenanceRecord:
    record_id: str
    topic_id: str
    source_id: str
    object_id: str
    sha256: str
    start: int
    end: int
    local_label: str | None
    recorded_at: str


@dataclass(frozen=True)
class ResolvedExactProvenance:
    record: ExactProvenanceRecord
    text: str


def _path(root: Path) -> Path:
    return root / PROVENANCE_FILE


def _validate_topic_id(topic_id: str) -> str:
    value = topic_id.strip()
    if not value:
        raise ValueError("provenance_topic_id_required")
    if "/" in value or "\\" in value or "\x00" in value:
        raise ValueError("provenance_topic_id_must_be_opaque_token")
    return value


def _validate_local_label(local_label: str | None) -> str | None:
    if local_label is None:
        return None
    value = local_label.strip()
    if not LOCAL_LABEL_RE.fullmatch(value):
        raise ValueError("provenance_local_label_must_be_opaque_ascii_token")
    return value


def _canonical_identity(
    *,
    topic_id: str,
    local_label: str | None,
    source_id: str,
    object_id: str,
    sha256: str,
    start: int,
    end: int,
) -> dict:
    return {
        "topic_id": topic_id,
        "local_label": local_label,
        "source_id": source_id,
        "object_id": object_id,
        "sha256": sha256,
        "start": start,
        "end": end,
    }


def _record_id(identity: dict) -> str:
    payload = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "prov-" + hashlib.sha256(payload).hexdigest()[:32]


def _row_to_record(row: dict) -> ExactProvenanceRecord:
    if row.get("record_schema") != PROVENANCE_SCHEMA or row.get("event") != "bind_exact_raw_span":
        raise RuntimeError("provenance_record_schema_mismatch")
    try:
        topic_id = _validate_topic_id(str(row["topic_id"]))
        local_label = _validate_local_label(row.get("local_label"))
        source_id = str(row["source_id"])
        object_id = str(row["object_id"])
        sha256 = str(row["sha256"])
        start = int(row["start"])
        end = int(row["end"])
        recorded_at = str(row["recorded_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("provenance_record_invalid_fields") from exc
    if start < 0 or end <= start:
        raise RuntimeError("provenance_record_span_invalid")
    if not source_id.startswith("src-") or not object_id.startswith("obj-") or len(sha256) != 64:
        raise RuntimeError("provenance_record_identity_format_invalid")
    try:
        recorded = datetime.fromisoformat(recorded_at)
    except ValueError as exc:
        raise RuntimeError("provenance_recorded_at_invalid") from exc
    if recorded.tzinfo is None:
        raise RuntimeError("provenance_recorded_at_naive")

    identity = _canonical_identity(
        topic_id=topic_id,
        local_label=local_label,
        source_id=source_id,
        object_id=object_id,
        sha256=sha256,
        start=start,
        end=end,
    )
    record_id = str(row["record_id"])
    if record_id != _record_id(identity):
        raise RuntimeError("provenance_record_identity_digest_mismatch")
    return ExactProvenanceRecord(
        record_id=record_id,
        topic_id=topic_id,
        source_id=source_id,
        object_id=object_id,
        sha256=sha256,
        start=start,
        end=end,
        local_label=local_label,
        recorded_at=recorded.astimezone(timezone.utc).isoformat(),
    )


def provenance_history(root: Path) -> list[ExactProvenanceRecord]:
    return [_row_to_record(row) for row in read_jsonl_objects(_path(root), log_name="provenance")]


def _record_identity(record: ExactProvenanceRecord) -> dict:
    return _canonical_identity(
        topic_id=record.topic_id,
        local_label=record.local_label,
        source_id=record.source_id,
        object_id=record.object_id,
        sha256=record.sha256,
        start=record.start,
        end=record.end,
    )


def bind_exact_raw_span(
    root: Path,
    *,
    topic_id: str,
    source_id: str,
    start: int,
    end: int,
    local_label: str | None = None,
) -> tuple[ExactProvenanceRecord, bool]:
    """Append one local exact pointer to an immutable raw evidence revision.

    Returns `(record, created)` where an exact retry returns the existing record
    with `created=False`. This API never follows a successor or repairs a span.
    """
    ensure_workspace(root)
    topic_id = _validate_topic_id(topic_id)
    local_label = _validate_local_label(local_label)
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("provenance_span_must_use_integer_character_offsets")
    if start < 0 or end <= start:
        raise ValueError("provenance_span_invalid")

    # Historical resolution is deliberate: precise provenance is a pointer to
    # one evidence revision, not a request to follow whichever revision is now current.
    source = find_source(root, source_id, topic_id=topic_id)
    raw_bytes = source.raw_path.read_bytes()
    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha != source.sha256 or source.object_id != f"obj-{actual_sha}":
        raise RuntimeError("provenance_target_raw_identity_mismatch")
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("provenance_target_raw_not_utf8") from exc
    if end > len(text):
        raise ValueError("provenance_span_out_of_range")

    identity = _canonical_identity(
        topic_id=topic_id,
        local_label=local_label,
        source_id=source.source_id,
        object_id=source.object_id,
        sha256=source.sha256,
        start=start,
        end=end,
    )
    record_id = _record_id(identity)

    for existing in provenance_history(root):
        if existing.record_id != record_id:
            continue
        if _record_identity(existing) != identity:
            raise RuntimeError(f"provenance_record_id_collision:{record_id}")
        resolve_exact_raw_span(root, existing.record_id, topic_id=topic_id)
        return existing, False

    row = {
        "event": "bind_exact_raw_span",
        "record_schema": PROVENANCE_SCHEMA,
        "record_id": record_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **identity,
    }
    append_jsonl_object(_path(root), row)
    return _row_to_record(row), True


def find_exact_provenance(
    root: Path,
    record_id: str,
    *,
    topic_id: str,
) -> ExactProvenanceRecord:
    topic_id = _validate_topic_id(topic_id)
    matches = [row for row in provenance_history(root) if row.record_id == record_id and row.topic_id == topic_id]
    if len(matches) != 1:
        raise ValueError(f"provenance_record_not_found:{record_id}:scope={topic_id}")
    return matches[0]


def list_exact_provenance(
    root: Path,
    *,
    topic_id: str,
    local_label: str | None = None,
) -> list[ExactProvenanceRecord]:
    topic_id = _validate_topic_id(topic_id)
    local_label = _validate_local_label(local_label)
    rows = [row for row in provenance_history(root) if row.topic_id == topic_id]
    if local_label is not None:
        rows = [row for row in rows if row.local_label == local_label]
    return sorted(rows, key=lambda row: (row.local_label or "", row.record_id))


def resolve_exact_raw_span(
    root: Path,
    record_id: str,
    *,
    topic_id: str,
) -> ResolvedExactProvenance:
    record = find_exact_provenance(root, record_id, topic_id=topic_id)
    source = find_source(root, record.source_id, topic_id=record.topic_id)
    if source.object_id != record.object_id or source.sha256 != record.sha256:
        raise RuntimeError("provenance_source_snapshot_mismatch")

    raw_bytes = source.raw_path.read_bytes()
    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha != record.sha256 or source.object_id != f"obj-{actual_sha}":
        raise RuntimeError("provenance_raw_object_integrity_mismatch")
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("provenance_raw_object_not_utf8") from exc
    if record.end > len(text):
        raise RuntimeError("provenance_record_span_invalid")
    if read_text(source) != text:
        raise RuntimeError("provenance_raw_read_path_mismatch")
    return ResolvedExactProvenance(record=record, text=text[record.start:record.end])
