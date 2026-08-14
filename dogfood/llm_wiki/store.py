from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .eventlog import append_jsonl_record, read_jsonl_records

ORIGIN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SOURCE_RECORD_SCHEMA = "llm-wiki-source-v1"


@dataclass(frozen=True)
class Source:
    source_id: str
    object_id: str
    sha256: str
    name: str
    size_bytes: int
    raw_path: Path
    origin_id: str | None = None
    legacy: bool = False


@dataclass(frozen=True)
class RawIntegrityReport:
    source_records: int
    unique_objects: int
    verified_objects: int
    missing_objects: int
    corrupt_objects: int
    invalid_utf8_objects: int
    invalid_source_records: int
    ok: bool


def ensure_workspace(root: Path) -> None:
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "manifest.jsonl").touch(exist_ok=True)
    config = root / "config.json"
    if not config.exists():
        config.write_text(
            json.dumps({"format": "llm-wiki-dogfood-v0", "compiled_provider": "disabled"}, indent=2) + "\n",
            encoding="utf-8",
        )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object_id(sha256: str) -> str:
    return f"obj-{sha256}"


def _validate_origin_id(origin_id: str | None) -> str | None:
    if origin_id is None:
        return None
    value = origin_id.strip()
    if not ORIGIN_ID_RE.fullmatch(value):
        raise ValueError("origin_id_must_be_opaque_ascii_token")
    return value


def _append_event(root: Path, event: dict) -> None:
    append_jsonl_record(root / "manifest.jsonl", event, log_label="manifest")


def history(root: Path) -> list[dict]:
    return read_jsonl_records(root / "manifest.jsonl", log_label="manifest")


def _normalize_ingest(event: dict) -> dict:
    if event.get("event") != "ingest":
        raise ValueError("not_ingest_event")
    normalized = dict(event)
    sha = str(normalized["sha256"])
    normalized.setdefault("object_id", _object_id(sha))
    normalized.setdefault("origin_id", None)
    normalized["legacy_source_record"] = normalized.get("record_schema") != SOURCE_RECORD_SCHEMA
    return normalized


def _source_rows(root: Path, *, topic_id: str | None = None) -> dict[str, dict]:
    """Return immutable source-record metadata keyed by source_id.

    Repeated ingest observations may reuse one source ID. The first ingest defines
    that source record; later observations must not silently rewrite its metadata.
    """
    records: dict[str, dict] = {}
    for event in history(root):
        if event.get("event") != "ingest":
            continue
        if topic_id is not None and event.get("topic_id") != topic_id:
            continue
        row = _normalize_ingest(event)
        sid = row["source_id"]
        existing = records.get(sid)
        if existing is None:
            records[sid] = row
            continue
        immutable = ("object_id", "sha256", "origin_id")
        if any(existing.get(key) != row.get(key) for key in immutable):
            raise RuntimeError(f"source_record_identity_mutated:{sid}")
    return records


def _all_source_ids(root: Path) -> set[str]:
    return set(_source_rows(root))


def _new_source_id(root: Path) -> str:
    existing = _all_source_ids(root)
    for _ in range(16):
        sid = f"src-{uuid.uuid4().hex}"
        if sid not in existing:
            return sid
    raise RuntimeError("source_id_generation_exhausted")


def _topic_state(root: Path, *, topic_id: str) -> tuple[dict[str, dict], set[str], dict[str, str]]:
    """Fold append-only topic events into source metadata and current membership.

    New source-v1 IDs identify evidence revisions, not bytes, so a deliberate
    A -> B -> A reversion creates a new source ID for the second A occurrence.
    Legacy content-derived IDs remain readable; `reactivates_source` is retained
    only for compatibility with source-lineage-v1 histories written before v2.
    """
    records: dict[str, dict] = {}
    active: set[str] = set()
    superseded_by: dict[str, str] = {}
    seen: set[str] = set()

    for event in history(root):
        if event.get("topic_id") != topic_id:
            continue
        kind = event.get("event")
        if kind == "ingest":
            row = _normalize_ingest(event)
            sid = row["source_id"]
            existing = records.get(sid)
            if existing is None:
                records[sid] = row
            else:
                immutable = ("object_id", "sha256", "origin_id")
                if any(existing.get(key) != row.get(key) for key in immutable):
                    raise RuntimeError(f"source_record_identity_mutated:{sid}")
            first_in_topic = sid not in seen
            seen.add(sid)
            if first_in_topic or event.get("reactivates_source") is True:
                active.add(sid)
                superseded_by.pop(sid, None)
            continue
        if kind != "supersede":
            continue

        predecessor = event["predecessor_source_id"]
        successor = event["successor_source_id"]
        if predecessor not in active:
            raise RuntimeError(f"invalid_supersession_history_predecessor_not_current:{predecessor}")
        if successor not in active:
            raise RuntimeError(f"invalid_supersession_history_successor_not_current:{successor}")
        active.remove(predecessor)
        superseded_by[predecessor] = successor

    return records, active, superseded_by


def _source_from_row(root: Path, row: dict) -> Source:
    sid = str(row["source_id"])
    sha = str(row["sha256"])
    object_id = str(row["object_id"])
    if not SHA256_RE.fullmatch(sha):
        raise RuntimeError("source_record_sha_invalid")
    if object_id != _object_id(sha):
        raise RuntimeError("source_record_object_identity_mismatch")
    raw = root / "raw" / f"{sha}.txt"
    if not raw.exists():
        raise RuntimeError(f"missing_raw_object:{sid}")
    return Source(
        source_id=sid,
        object_id=object_id,
        sha256=sha,
        name=row["name"],
        size_bytes=int(row["size_bytes"]),
        raw_path=raw,
        origin_id=row.get("origin_id"),
        legacy=bool(row.get("legacy_source_record")),
    )


def _identity_matches(row: dict, *, object_id: str, origin_id: str | None) -> bool:
    return row["object_id"] == object_id and row.get("origin_id") == origin_id


def _find_topic_identity_matches(
    root: Path,
    *,
    topic_id: str,
    object_id: str,
    origin_id: str | None,
) -> tuple[list[str], list[str], dict[str, dict], dict[str, str]]:
    records, active, superseded_by = _topic_state(root, topic_id=topic_id)
    matching = [
        sid for sid, row in records.items()
        if _identity_matches(row, object_id=object_id, origin_id=origin_id)
    ]
    current = sorted(sid for sid in matching if sid in active)
    historical = sorted(sid for sid in matching if sid not in active)
    return current, historical, records, superseded_by


def _find_unscoped_identity_match(
    root: Path,
    *,
    object_id: str,
    origin_id: str | None,
) -> tuple[str | None, dict[str, dict]]:
    records = _source_rows(root)
    matching = sorted(
        sid for sid, row in records.items()
        if row.get("topic_id") is None and _identity_matches(row, object_id=object_id, origin_id=origin_id)
    )
    if len(matching) > 1:
        raise RuntimeError("ambiguous_unscoped_source_identity")
    return (matching[0] if matching else None), records


def _validate_standalone_supersession(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str,
) -> bool:
    if predecessor_source_id == successor_source_id:
        raise ValueError("supersession_self_reference")

    records, active, superseded_by = _topic_state(root, topic_id=topic_id)
    if predecessor_source_id not in records:
        raise ValueError(f"supersession_predecessor_not_found:{predecessor_source_id}")
    if successor_source_id not in records:
        raise ValueError(f"supersession_successor_not_found:{successor_source_id}")

    if predecessor_source_id not in active:
        if superseded_by.get(predecessor_source_id) == successor_source_id and successor_source_id in active:
            return False
        raise ValueError(f"supersession_predecessor_not_current:{predecessor_source_id}")
    if successor_source_id not in active:
        raise ValueError(f"supersession_successor_not_current:{successor_source_id}")
    return True


def _record_supersession(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str,
) -> None:
    _append_event(
        root,
        {
            "event": "supersede",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "topic_id": topic_id,
            "predecessor_source_id": predecessor_source_id,
            "successor_source_id": successor_source_id,
        },
    )


def supersede_source(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str,
) -> bool:
    """Append an explicit topic-scoped supersession event between current sources."""
    ensure_workspace(root)
    should_write = _validate_standalone_supersession(
        root,
        predecessor_source_id,
        successor_source_id,
        topic_id=topic_id,
    )
    if not should_write:
        return False
    _record_supersession(root, predecessor_source_id, successor_source_id, topic_id=topic_id)
    return True


def ingest_file(
    root: Path,
    file_path: Path,
    *,
    topic_id: str | None = None,
    supersedes_source_id: str | None = None,
    origin_id: str | None = None,
) -> tuple[Source, bool]:
    """Ingest UTF-8 evidence while separating content and provenance identity.

    `origin_id` is optional and caller-asserted. It must be an opaque token; the
    core deliberately does not derive it from filenames or paths.
    """
    ensure_workspace(root)
    origin_id = _validate_origin_id(origin_id)
    if supersedes_source_id is not None and topic_id is None:
        raise ValueError("supersession_requires_topic")

    data = file_path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"not_utf8_text:{file_path.name}") from exc

    sha = _sha256(data)
    object_id = _object_id(sha)

    retry_source_id: str | None = None
    existing_current_successor_id: str | None = None
    if topic_id is not None and supersedes_source_id is not None:
        records, active, superseded_by = _topic_state(root, topic_id=topic_id)
        predecessor_row = records.get(supersedes_source_id)
        if predecessor_row is None:
            raise ValueError(f"supersession_predecessor_not_found:{supersedes_source_id}")
        if supersedes_source_id not in active:
            successor_id = superseded_by.get(supersedes_source_id)
            successor = records.get(successor_id) if successor_id else None
            if (
                successor_id in active
                and successor is not None
                and _identity_matches(successor, object_id=object_id, origin_id=origin_id)
            ):
                retry_source_id = successor_id
            else:
                raise ValueError(f"supersession_predecessor_not_current:{supersedes_source_id}")
        else:
            if _identity_matches(predecessor_row, object_id=object_id, origin_id=origin_id):
                raise ValueError("supersession_no_identity_change")
            current_matches = sorted(
                sid for sid, row in records.items()
                if sid != supersedes_source_id
                and sid in active
                and _identity_matches(row, object_id=object_id, origin_id=origin_id)
            )
            if len(current_matches) > 1:
                raise RuntimeError("ambiguous_current_successor_identity")
            if current_matches:
                existing_current_successor_id = current_matches[0]

    if retry_source_id is not None:
        records, _, _ = _topic_state(root, topic_id=topic_id)  # type: ignore[arg-type]
        return _source_from_row(root, records[retry_source_id]), True

    source_id: str | None = existing_current_successor_id
    if supersedes_source_id is None:
        if topic_id is None:
            source_id, _ = _find_unscoped_identity_match(root, object_id=object_id, origin_id=origin_id)
        else:
            current, historical, _, _ = _find_topic_identity_matches(
                root,
                topic_id=topic_id,
                object_id=object_id,
                origin_id=origin_id,
            )
            if len(current) > 1:
                raise RuntimeError("ambiguous_current_source_identity")
            if current:
                source_id = current[0]
            elif historical:
                if len(historical) == 1:
                    raise ValueError(f"stale_source_requires_supersedes:{historical[0]}")
                raise ValueError("ambiguous_stale_source_requires_supersedes")

    if source_id is None:
        source_id = _new_source_id(root)

    raw = root / "raw" / f"{sha}.txt"
    duplicate_content = raw.exists()
    if duplicate_content:
        if raw.read_bytes() != data:
            raise RuntimeError("content_address_collision")
    else:
        raw.write_bytes(data)

    event = {
        "event": "ingest",
        "record_schema": SOURCE_RECORD_SCHEMA,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "source_id": source_id,
        "object_id": object_id,
        "sha256": sha,
        "origin_id": origin_id,
        "name": file_path.name,
        "size_bytes": len(data),
        "duplicate_content": duplicate_content,
    }
    if topic_id is not None:
        event["topic_id"] = topic_id
    _append_event(root, event)

    if supersedes_source_id is not None:
        assert topic_id is not None
        _record_supersession(root, supersedes_source_id, source_id, topic_id=topic_id)

    if existing_current_successor_id is not None:
        records, _, _ = _topic_state(root, topic_id=topic_id)  # type: ignore[arg-type]
        return _source_from_row(root, records[source_id]), duplicate_content

    row = _normalize_ingest(event)
    return _source_from_row(root, row), duplicate_content


def sources(
    root: Path,
    *,
    topic_id: str | None = None,
    include_superseded: bool = False,
) -> list[Source]:
    if topic_id is None:
        records = _source_rows(root)
        visible = set(records)
    else:
        records, active, _ = _topic_state(root, topic_id=topic_id)
        visible = set(records) if include_superseded else active

    return [
        _source_from_row(root, records[sid])
        for sid in sorted(visible)
    ]


def source_status(root: Path, source_id: str, *, topic_id: str) -> dict:
    records, active, superseded_by = _topic_state(root, topic_id=topic_id)
    row = records.get(source_id)
    if row is None:
        raise ValueError(f"source_not_found:{source_id}:scope={topic_id}")
    return {
        "source_id": source_id,
        "object_id": row["object_id"],
        "status": "current" if source_id in active else "superseded",
        "superseded_by": superseded_by.get(source_id),
    }


def find_source(root: Path, source_id: str, *, topic_id: str | None = None) -> Source:
    matches = [src for src in sources(root, topic_id=topic_id, include_superseded=True) if src.source_id == source_id]
    if len(matches) != 1:
        scope = topic_id if topic_id is not None else "all"
        raise ValueError(f"source_not_found:{source_id}:scope={scope}")
    return matches[0]


def read_bytes_verified(source: Source) -> bytes:
    """Read immutable raw bytes only after verifying their declared identity."""
    if not SHA256_RE.fullmatch(source.sha256):
        raise RuntimeError("raw_source_sha_invalid")
    if source.object_id != _object_id(source.sha256):
        raise RuntimeError("raw_source_object_identity_mismatch")
    if source.raw_path.name != f"{source.sha256}.txt":
        raise RuntimeError("raw_source_path_identity_mismatch")
    try:
        data = source.raw_path.read_bytes()
    except FileNotFoundError as exc:
        raise RuntimeError("raw_object_missing") from exc
    if _sha256(data) != source.sha256:
        raise RuntimeError("raw_object_integrity_mismatch")
    return data


def read_text(source: Source) -> str:
    data = read_bytes_verified(source)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("raw_object_not_utf8") from exc


def verify_raw_integrity(root: Path) -> RawIntegrityReport:
    """Read-only aggregate audit of every unique raw object referenced by history.

    The report deliberately contains counts/status only: no source IDs, paths,
    filenames, content, hashes, or local provenance metadata.
    """
    records = _source_rows(root)
    valid_shas: set[str] = set()
    invalid_source_records = 0
    for row in records.values():
        sha = str(row.get("sha256", ""))
        object_id = str(row.get("object_id", ""))
        if not SHA256_RE.fullmatch(sha) or object_id != _object_id(sha):
            invalid_source_records += 1
            continue
        valid_shas.add(sha)

    verified_objects = 0
    missing_objects = 0
    corrupt_objects = 0
    invalid_utf8_objects = 0
    for sha in sorted(valid_shas):
        raw = root / "raw" / f"{sha}.txt"
        try:
            data = raw.read_bytes()
        except FileNotFoundError:
            missing_objects += 1
            continue
        if _sha256(data) != sha:
            corrupt_objects += 1
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            invalid_utf8_objects += 1
            continue
        verified_objects += 1

    ok = (
        invalid_source_records == 0
        and missing_objects == 0
        and corrupt_objects == 0
        and invalid_utf8_objects == 0
        and verified_objects == len(valid_shas)
    )
    return RawIntegrityReport(
        source_records=len(records),
        unique_objects=len(valid_shas),
        verified_objects=verified_objects,
        missing_objects=missing_objects,
        corrupt_objects=corrupt_objects,
        invalid_utf8_objects=invalid_utf8_objects,
        invalid_source_records=invalid_source_records,
        ok=ok,
    )
