from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Source:
    source_id: str
    sha256: str
    name: str
    size_bytes: int
    raw_path: Path


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


def _source_id(sha256: str) -> str:
    return f"src-{sha256[:16]}"


def _append_event(root: Path, event: dict) -> None:
    with (root / "manifest.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")


def history(root: Path) -> list[dict]:
    manifest = root / "manifest.jsonl"
    if not manifest.exists():
        return []
    rows = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _ingest_rows(root: Path, *, topic_id: str | None = None) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for event in history(root):
        if event.get("event") != "ingest":
            continue
        if topic_id is not None and event.get("topic_id") != topic_id:
            continue
        latest[event["source_id"]] = event
    return latest


def _topic_state(root: Path, *, topic_id: str) -> tuple[dict[str, dict], set[str], dict[str, str]]:
    """Fold append-only topic events into historical metadata and current membership.

    Source IDs are content-addressed, so the same bytes can legitimately recur later.
    A plain re-ingest of previously superseded bytes does not reactivate them. Only
    an ingest event explicitly marked `reactivates_source=true` can do that.
    """
    latest: dict[str, dict] = {}
    active: set[str] = set()
    superseded_by: dict[str, str] = {}
    seen: set[str] = set()

    for event in history(root):
        if event.get("topic_id") != topic_id:
            continue
        kind = event.get("event")
        if kind == "ingest":
            sid = event["source_id"]
            latest[sid] = event
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

    return latest, active, superseded_by


def _validate_supersession(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str | None,
    successor_will_be_ingested: bool,
) -> bool:
    if topic_id is None:
        raise ValueError("supersession_requires_topic")
    if predecessor_source_id == successor_source_id:
        raise ValueError("supersession_self_reference")

    latest, active, superseded_by = _topic_state(root, topic_id=topic_id)
    if predecessor_source_id not in latest:
        raise ValueError(f"supersession_predecessor_not_found:{predecessor_source_id}")

    if predecessor_source_id not in active:
        if superseded_by.get(predecessor_source_id) == successor_source_id:
            return False
        raise ValueError(f"supersession_predecessor_not_current:{predecessor_source_id}")

    if successor_will_be_ingested:
        return True

    if successor_source_id not in latest:
        raise ValueError(f"supersession_successor_not_found:{successor_source_id}")
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
    should_write = _validate_supersession(
        root,
        predecessor_source_id,
        successor_source_id,
        topic_id=topic_id,
        successor_will_be_ingested=False,
    )
    if not should_write:
        return False
    _record_supersession(
        root,
        predecessor_source_id,
        successor_source_id,
        topic_id=topic_id,
    )
    return True


def ingest_file(
    root: Path,
    file_path: Path,
    *,
    topic_id: str | None = None,
    supersedes_source_id: str | None = None,
) -> tuple[Source, bool]:
    ensure_workspace(root)
    data = file_path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"not_utf8_text:{file_path.name}") from exc

    sha = _sha256(data)
    sid = _source_id(sha)

    should_record_supersession = False
    if supersedes_source_id is not None:
        should_record_supersession = _validate_supersession(
            root,
            supersedes_source_id,
            sid,
            topic_id=topic_id,
            successor_will_be_ingested=True,
        )

    raw = root / "raw" / f"{sha}.txt"
    duplicate = raw.exists()
    if duplicate:
        if raw.read_bytes() != data:
            raise RuntimeError("content_address_collision")
    else:
        raw.write_bytes(data)

    event = {
        "event": "ingest",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "source_id": sid,
        "sha256": sha,
        "name": file_path.name,
        "size_bytes": len(data),
        "duplicate_content": duplicate,
    }
    if topic_id is not None:
        event["topic_id"] = topic_id
    if supersedes_source_id is not None:
        # This flag matters only when the same content-addressed source had been
        # superseded earlier. Plain duplicate ingest never resurrects stale bytes.
        event["reactivates_source"] = True
    _append_event(root, event)

    if supersedes_source_id is not None and should_record_supersession:
        assert topic_id is not None
        # If an I/O failure occurs between ingest and this append, both versions
        # remain visible. That conservative failure mode is safer than hiding the
        # predecessor without a durable successor relation.
        _record_supersession(root, supersedes_source_id, sid, topic_id=topic_id)

    return Source(sid, sha, file_path.name, len(data), raw), duplicate


def sources(
    root: Path,
    *,
    topic_id: str | None = None,
    include_superseded: bool = False,
) -> list[Source]:
    if topic_id is None:
        # Unscoped retrieval cannot safely apply topic-local supersession semantics.
        # It therefore remains an all-evidence view.
        latest = _ingest_rows(root)
        visible = set(latest)
    else:
        latest, active, _ = _topic_state(root, topic_id=topic_id)
        visible = set(latest) if include_superseded else active

    out = []
    for sid, event in sorted(latest.items()):
        if sid not in visible:
            continue
        raw = root / "raw" / f"{event['sha256']}.txt"
        if not raw.exists():
            raise RuntimeError(f"missing_raw_object:{sid}")
        out.append(Source(sid, event["sha256"], event["name"], int(event["size_bytes"]), raw))
    return out


def source_status(root: Path, source_id: str, *, topic_id: str) -> dict:
    latest, active, superseded_by = _topic_state(root, topic_id=topic_id)
    if source_id not in latest:
        raise ValueError(f"source_not_found:{source_id}:scope={topic_id}")
    successor = superseded_by.get(source_id)
    return {
        "source_id": source_id,
        "status": "current" if source_id in active else "superseded",
        "superseded_by": successor,
    }


def find_source(root: Path, source_id: str, *, topic_id: str | None = None) -> Source:
    # Direct provenance lookup intentionally includes superseded evidence. A source
    # ID that was once cited must remain resolvable after later updates.
    matches = [src for src in sources(root, topic_id=topic_id, include_superseded=True) if src.source_id == source_id]
    if len(matches) != 1:
        scope = topic_id if topic_id is not None else "all"
        raise ValueError(f"source_not_found:{source_id}:scope={scope}")
    return matches[0]


def read_text(source: Source) -> str:
    return source.raw_path.read_text(encoding="utf-8")
