from __future__ import annotations

import argparse
import json
from pathlib import Path

from .calibration import resolve_topic
from .store import ensure_workspace, find_source, read_text
from .temporal import temporal_source_status

DEFAULT_MAX_CHARS = 6000
HARD_MAX_CHARS = 12000
DEFAULT_DIFF_CONTEXT_CHARS = 500
DEFAULT_DIFF_CHANGE_CHARS = 1200
HARD_DIFF_CONTEXT_CHARS = 2000
HARD_DIFF_CHANGE_CHARS = 4000


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _resolved_topic_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return resolve_topic(root, value)["topic_id"]
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"AGENT-MEMORY-STOP {exc}") from None


def _source_row(root: Path, source_id: str, *, topic_id: str | None) -> tuple[object, str, dict]:
    try:
        source = find_source(root, source_id, topic_id=topic_id)
        text = read_text(source)
        status = temporal_source_status(root, source.source_id, topic_id=topic_id) if topic_id else {
            "status": "unscoped",
            "contested": False,
        }
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"AGENT-MEMORY-STOP {exc}") from None
    return source, text, status


def _bounded_change_excerpt(text: str, start: int, end: int, *, context_chars: int, max_change_chars: int) -> tuple[str, bool]:
    before_start = max(0, start - context_chars)
    after_end = min(len(text), end + context_chars)
    changed = text[start:end]
    truncated = len(changed) > max_change_chars
    if not truncated:
        return text[before_start:after_end], False

    head_chars = max_change_chars // 2
    tail_chars = max_change_chars - head_chars
    marker = "\n… [CHANGED REGION TRUNCATED] …\n"
    excerpt = (
        text[before_start:start]
        + changed[:head_chars]
        + marker
        + changed[-tail_chars:]
        + text[end:after_end]
    )
    return excerpt, True


def _comparison(old_text: str, new_text: str, *, context_chars: int, max_change_chars: int) -> dict:
    shared = min(len(old_text), len(new_text))
    prefix = 0
    while prefix < shared and old_text[prefix] == new_text[prefix]:
        prefix += 1

    old_remaining = len(old_text) - prefix
    new_remaining = len(new_text) - prefix
    suffix_limit = min(old_remaining, new_remaining)
    suffix = 0
    while suffix < suffix_limit and old_text[len(old_text) - 1 - suffix] == new_text[len(new_text) - 1 - suffix]:
        suffix += 1

    old_end = len(old_text) - suffix if suffix else len(old_text)
    new_end = len(new_text) - suffix if suffix else len(new_text)
    old_excerpt, old_truncated = _bounded_change_excerpt(
        old_text,
        prefix,
        old_end,
        context_chars=context_chars,
        max_change_chars=max_change_chars,
    )
    new_excerpt, new_truncated = _bounded_change_excerpt(
        new_text,
        prefix,
        new_end,
        context_chars=context_chars,
        max_change_chars=max_change_chars,
    )
    return {
        "identical": old_text == new_text,
        "common_prefix_chars": prefix,
        "common_suffix_chars": suffix,
        "old_changed_chars": max(0, old_end - prefix),
        "new_changed_chars": max(0, new_end - prefix),
        "old_excerpt": old_excerpt,
        "new_excerpt": new_excerpt,
        "excerpt_truncated": old_truncated or new_truncated,
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-agent-memory")
    p.add_argument("--root", default=".wiki-lab")
    sub = p.add_subparsers(dest="command", required=True)

    read = sub.add_parser("read")
    read.add_argument("source_id")
    read.add_argument("--topic")
    read.add_argument("--start-char", type=int, default=0)
    read.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)

    compare = sub.add_parser("compare")
    compare.add_argument("older_source_id")
    compare.add_argument("newer_source_id")
    compare.add_argument("--topic", required=True)
    compare.add_argument("--context-chars", type=int, default=DEFAULT_DIFF_CONTEXT_CHARS)
    compare.add_argument("--max-change-chars", type=int, default=DEFAULT_DIFF_CHANGE_CHARS)
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
        source, text, status = _source_row(root, args.source_id, topic_id=topic_id)

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

    if args.command == "compare":
        if args.context_chars < 0 or args.context_chars > HARD_DIFF_CONTEXT_CHARS:
            raise SystemExit(f"AGENT-MEMORY-STOP context_chars_must_be_0_to_{HARD_DIFF_CONTEXT_CHARS}")
        if args.max_change_chars < 1 or args.max_change_chars > HARD_DIFF_CHANGE_CHARS:
            raise SystemExit(f"AGENT-MEMORY-STOP max_change_chars_must_be_1_to_{HARD_DIFF_CHANGE_CHARS}")
        topic_id = _resolved_topic_id(root, args.topic)
        assert topic_id is not None
        old_source, old_text, old_status = _source_row(root, args.older_source_id, topic_id=topic_id)
        new_source, new_text, new_status = _source_row(root, args.newer_source_id, topic_id=topic_id)
        comparison = _comparison(
            old_text,
            new_text,
            context_chars=args.context_chars,
            max_change_chars=args.max_change_chars,
        )
        row = {
            "format": "llm-wiki-agent-raw-compare-v0",
            "topic_id": topic_id,
            "older_source_id": old_source.source_id,
            "older_sha256": old_source.sha256,
            "older_name": old_source.name,
            "older_status": old_status.get("status", "unknown"),
            "newer_source_id": new_source.source_id,
            "newer_sha256": new_source.sha256,
            "newer_name": new_source.name,
            "newer_status": new_status.get("status", "unknown"),
            **comparison,
        }
        print(json.dumps(row, ensure_ascii=False, sort_keys=True))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
