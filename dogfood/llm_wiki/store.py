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


def supersession_map(root: Path, *, topic_id: str) -> dict[str, str]:
    """Return the explicit predecessor -> successor graph for one topic.

    Supersession is deliberately topic-scoped in v1. A content-addressed source can
    participate in multiple topics, so a relation in one topic must not silently
    hide evidence in another topic or in the unscoped all-evidence view.
    """
    graph: dict[str, str] = {}
    for event in history(root):
        if event.get("event") != "supersede" or event.get("topic_id") != topic_id:
            continue
        predecessor = event["predecessor_source_id"]
        successor = event["successor_source_id"]
        existing = graph.get(predecessor)
        if existing is not None and existing != successor:
            raise RuntimeError(f"conflicting_supersession_history:{predecessor}")
        graph[predecessor] = successor
    return graph


def _validate_supersession(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str | None,
    successor_may_be_pending: bool,
) -> bool:
    if topic_id is None:
        raise ValueError("supersession_requires_topic")
    if predecessor_source_id == successor_source_id:
        raise ValueError("supersession_self_reference")

    scoped = _ingest_rows(root, topic_id=topic_id)
    if predecessor_source_id not in scoped:
        raise ValueError(f"supersession_predecessor_not_found:{predecessor_source_id}")
    if not successor_may_be_pending and successor_source_id not in scoped:
        raise ValueError(f"supersession_successor_not_found:{successor_source_id}")

    graph = supersession_map(root, topic_id=topic_id)
    existing = graph.get(predecessor_source_id)
    if existing is not None:
        if existing == successor_source_id:
            return False
        raise ValueError(
            f"supersession_conflict:{predecessor_source_id}:existing={existing}:requested={successor_source_id}"
        )

    if successor_source_id in graph:
        raise ValueError(f"supersession_successor_already_superseded:{successor_source_id}")

    cursor = successor_source_id
    seen: set[str] = set()
    while cursor in graph:
        if cursor in seen:
            raise RuntimeError("supersession_history_cycle")
        seen.add(cursor)
        cursor = graph[cursor]
        if cursor == predecessor_source_id:
            raise ValueError("supersession_cycle")
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
    """Append an explicit topic-scoped supersession relation.

    Returns True when a new relation is written and False when the exact relation
    already exists. Historical raw objects and ingest events are never changed.
    """
    ensure_workspace(root)
    should_write = _validate_supersession(
        root,
        predecessor_source_id,
        successor_source_id,
        topic_id=topic_id,
        successor_may_be_pending=False,
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
            successor_may_be_pending=True,
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
    latest = _ingest_rows(root, topic_id=topic_id)

    hidden: set[str] = set()
    if topic_id is not None and not include_superseded:
        hidden = set(supersession_map(root, topic_id=topic_id))

    out = []
    for sid, event in sorted(latest.items()):
        if sid in hidden:
            continue
        raw = root / "raw" / f"{event['sha256']}.txt"
        if not raw.exists():
            raise RuntimeError(f"missing_raw_object:{sid}")
        out.append(Source(sid, event["sha256"], event["name"], int(event["size_bytes"]), raw))
    return out


def source_status(root: Path, source_id: str, *, topic_id: str) -> dict:
    scoped = _ingest_rows(root, topic_id=topic_id)
    if source_id not in scoped:
        raise ValueError(f"source_not_found:{source_id}:scope={topic_id}")
    successor = supersession_map(root, topic_id=topic_id).get(source_id)
    return {
        "source_id": source_id,
        "status": "superseded" if successor else "current",
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
