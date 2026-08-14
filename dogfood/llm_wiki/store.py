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


def ingest_file(root: Path, file_path: Path, *, topic_id: str | None = None) -> tuple[Source, bool]:
    ensure_workspace(root)
    data = file_path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"not_utf8_text:{file_path.name}") from exc

    sha = _sha256(data)
    sid = _source_id(sha)
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
    with (root / "manifest.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")

    return Source(sid, sha, file_path.name, len(data), raw), duplicate


def history(root: Path) -> list[dict]:
    manifest = root / "manifest.jsonl"
    if not manifest.exists():
        return []
    rows = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def sources(root: Path, *, topic_id: str | None = None) -> list[Source]:
    latest: dict[str, dict] = {}
    for event in history(root):
        if event.get("event") != "ingest":
            continue
        if topic_id is not None and event.get("topic_id") != topic_id:
            continue
        latest[event["source_id"]] = event
    out = []
    for sid, event in sorted(latest.items()):
        raw = root / "raw" / f"{event['sha256']}.txt"
        if not raw.exists():
            raise RuntimeError(f"missing_raw_object:{sid}")
        out.append(Source(sid, event["sha256"], event["name"], int(event["size_bytes"]), raw))
    return out


def find_source(root: Path, source_id: str, *, topic_id: str | None = None) -> Source:
    matches = [src for src in sources(root, topic_id=topic_id) if src.source_id == source_id]
    if len(matches) != 1:
        scope = topic_id if topic_id is not None else "all"
        raise ValueError(f"source_not_found:{source_id}:scope={scope}")
    return matches[0]


def read_text(source: Source) -> str:
    return source.raw_path.read_text(encoding="utf-8")
