from __future__ import annotations

import argparse
import json
from pathlib import Path

from .calibration import resolve_topic
from .store import ensure_workspace, find_source, read_text
from .temporal import temporal_source_status

DEFAULT_MAX_CHARS = 6000
HARD_MAX_CHARS = 12000


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _resolved_topic_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return resolve_topic(root, value)["topic_id"]
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"AGENT-MEMORY-STOP {exc}") from None


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-agent-memory")
    p.add_argument("--root", default=".wiki-lab")
    sub = p.add_subparsers(dest="command", required=True)

    read = sub.add_parser("read")
    read.add_argument("source_id")
    read.add_argument("--topic")
    read.add_argument("--start-char", type=int, default=0)
    read.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = _root(args.root)
    ensure_workspace(root)

    if args.command == "read":
        if args.start_char < 0:
            raise SystemExit("AGENT-MEMORY-STOP start_char_must_be_nonnegative")
        if args.max_chars < 1 or args.max_chars > HARD_MAX_CHARS:
            raise SystemExit(f"AGENT-MEMORY-STOP max_chars_must_be_1_to_{HARD_MAX_CHARS}")
        topic_id = _resolved_topic_id(root, args.topic)
        try:
            source = find_source(root, args.source_id, topic_id=topic_id)
            text = read_text(source)
            status = temporal_source_status(root, source.source_id, topic_id=topic_id) if topic_id else {
                "status": "unscoped",
                "contested": False,
            }
        except (ValueError, RuntimeError) as exc:
            raise SystemExit(f"AGENT-MEMORY-STOP {exc}") from None

        start = min(args.start_char, len(text))
        end = min(len(text), start + args.max_chars)
        row = {
            "format": "llm-wiki-agent-raw-read-v0",
            "source_id": source.source_id,
            "object_id": source.object_id,
            "sha256": source.sha256,
            "name": source.name,
            "topic_id": topic_id,
            "status": status.get("status", "unknown"),
            "contested": bool(status.get("contested", False)),
            "start_char": start,
            "end_char": end,
            "total_chars": len(text),
            "has_more": end < len(text),
            "text": text[start:end],
        }
        if status.get("superseded_by"):
            row["superseded_by"] = status["superseded_by"]
        print(json.dumps(row, ensure_ascii=False, sort_keys=True))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
