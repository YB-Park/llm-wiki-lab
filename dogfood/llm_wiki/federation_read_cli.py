from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .agent_state import STATE_FILE, STATE_FORMAT, _validate
from .agent_wiki import read_agent_source_note, search_agent_notes
from .agent_memory_cli import HARD_MAX_CHARS, _relevant_region
from .calibration import resolve_topic
from .discovery import discover_current
from .integrity import audit_alpha_integrity
from .store import find_source, read_text
from .temporal import temporal_source_status

SOURCE_ID_RE = re.compile(r"^src-[0-9A-Za-z-]+$")
AUTHORITY_ANCHOR_RE = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_ANCHOR_READ_LIMIT = 64 * 1024


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _require_initialized(root: Path) -> None:
    if not (
        (root / "config.json").is_file()
        and (root / "manifest.jsonl").is_file()
        and (root / "raw").is_dir()
    ):
        raise RuntimeError("federation_store_not_initialized")


def _manifest_authority_anchor(root: Path) -> str:
    manifest = root / "manifest.jsonl"
    with manifest.open("rb") as handle:
        text = handle.read(MANIFEST_ANCHOR_READ_LIMIT).decode("utf-8")
    first = next((line for line in text.splitlines() if line.strip()), "")
    if not first:
        raise RuntimeError("library_store_identity_changed")
    event = json.loads(first)
    source_id = event.get("source_id") if isinstance(event, dict) else None
    sha256 = event.get("sha256") if isinstance(event, dict) else None
    if (
        not isinstance(event, dict)
        or event.get("event") != "ingest"
        or not isinstance(source_id, str)
        or not source_id.startswith("src-")
        or not isinstance(sha256, str)
        or not AUTHORITY_ANCHOR_RE.fullmatch(sha256)
    ):
        raise RuntimeError("library_store_identity_changed")
    return hashlib.sha256(first.strip().encode("utf-8")).hexdigest()


def _require_authority_anchor(root: Path, expected: str) -> None:
    if not AUTHORITY_ANCHOR_RE.fullmatch(expected):
        raise RuntimeError("library_store_identity_changed")
    if _manifest_authority_anchor(root) != expected:
        raise RuntimeError("library_store_identity_changed")


def _topic_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    return str(resolve_topic(root, value)["topic_id"])


def _source_row(root: Path, source_id: str, topic_id: str | None) -> tuple[object, str, dict]:
    source = find_source(root, source_id, topic_id=topic_id)
    text = read_text(source)
    status = temporal_source_status(root, source.source_id, topic_id=topic_id) if topic_id else {
        "status": "unscoped",
        "contested": False,
    }
    return source, text, status


def _read_agent_state_readonly(root: Path) -> dict:
    path = root / STATE_FILE
    if not path.exists():
        return {
            "format": STATE_FORMAT,
            "pending_lineage": [],
            "maintenance_usage": {"day": "", "reserved_calls": 0},
            "source_locators": {},
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    return _validate(value)


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _raw_read(root: Path, source_id: str, *, topic: str | None, start_char: int, max_chars: int) -> dict:
    if start_char < 0:
        raise ValueError("start_char_must_be_nonnegative")
    if max_chars < 1 or max_chars > HARD_MAX_CHARS:
        raise ValueError("max_chars_out_of_range")
    topic_id = _topic_id(root, topic)
    source, text, status = _source_row(root, source_id, topic_id)
    start = min(start_char, len(text))
    end = min(len(text), start + max_chars)
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
    return row


def _relevant_read(root: Path, source_id: str, *, topic: str | None, query: str, max_chars: int) -> dict:
    if not query.strip():
        raise ValueError("query_required")
    if max_chars < 1 or max_chars > HARD_MAX_CHARS:
        raise ValueError("max_chars_out_of_range")
    topic_id = _topic_id(root, topic)
    source, text, status = _source_row(root, source_id, topic_id)
    start, end, excerpt, has_more_before, has_more_after = _relevant_region(text, query, max_chars=max_chars)
    row = {
        "format": "llm-wiki-agent-relevant-read-v0",
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
        "has_more_before": has_more_before,
        "has_more_after": has_more_after,
        "text": excerpt,
    }
    if status.get("superseded_by"):
        row["superseded_by"] = status["superseded_by"]
    return row


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-federation-read")
    p.add_argument("--root", required=True)
    p.add_argument("--expected-authority-anchor", required=True)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("integrity")

    discover = sub.add_parser("discover")
    discover.add_argument("query")
    discover.add_argument("--top-k-per-topic", type=int, default=3)
    discover.add_argument("--json", action="store_true")

    derived = sub.add_parser("agent-wiki-search")
    derived.add_argument("query")
    derived.add_argument("--top-k", type=int, default=3)
    derived.add_argument("--json", action="store_true")

    show = sub.add_parser("agent-wiki-show")
    show.add_argument("source_id")

    sub.add_parser("pending-list")

    read = sub.add_parser("read")
    read.add_argument("source_id")
    read.add_argument("--topic")
    read.add_argument("--start-char", type=int, default=0)
    read.add_argument("--max-chars", type=int, default=6000)

    relevant = sub.add_parser("relevant")
    relevant.add_argument("source_id")
    relevant.add_argument("--topic")
    relevant.add_argument("--query", required=True)
    relevant.add_argument("--max-chars", type=int, default=6000)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = _root(args.root)
    expected_anchor = args.expected_authority_anchor
    try:
        _require_initialized(root)
        _require_authority_anchor(root, expected_anchor)

        if args.command == "integrity":
            row = audit_alpha_integrity(root)
            _require_authority_anchor(root, expected_anchor)
            _print(row)
            return 0

        if args.command == "discover":
            rows = []
            for hit in discover_current(root, args.query, top_k_per_topic=max(0, args.top_k_per_topic), snippet_chars=320):
                rows.append({
                    "topic_id": hit.topic_id,
                    "topic_label": hit.topic_label,
                    "source_id": hit.source.source_id,
                    "source_ids": list(hit.source_ids),
                    "object_id": hit.object_id,
                    "sha256": hit.source.sha256,
                    "name": hit.source.name,
                    "names": sorted({source.name for source in hit.evidence_sources}),
                    "score": hit.score,
                    "snippet": hit.snippet,
                })
            _require_authority_anchor(root, expected_anchor)
            for row in rows:
                _print(row)
            return 0

        if args.command == "agent-wiki-search":
            rows = [{
                "source_id": hit.source_id,
                "topic_id": hit.topic_id,
                "title": hit.title,
                "score": hit.score,
                "snippet": hit.snippet,
                "epistemic_status": "derived_noncanonical_agent_wiki",
            } for hit in search_agent_notes(root, args.query, top_k=max(0, args.top_k))]
            _require_authority_anchor(root, expected_anchor)
            for row in rows:
                _print(row)
            return 0

        if args.command == "agent-wiki-show":
            if not SOURCE_ID_RE.fullmatch(args.source_id):
                raise ValueError("source_id_invalid")
            record = read_agent_source_note(root, args.source_id)
            if record is None:
                raise RuntimeError("derived_note_not_found")
            markdown = root / "agent-wiki" / "source-notes" / f"{args.source_id}.md"
            if not markdown.is_file():
                raise RuntimeError("derived_markdown_missing")
            text = markdown.read_text(encoding="utf-8")
            _require_authority_anchor(root, expected_anchor)
            print(text, end="")
            return 0

        if args.command == "pending-list":
            state = _read_agent_state_readonly(root)
            rows = [row for row in state["pending_lineage"] if row["status"] == "open"]
            _require_authority_anchor(root, expected_anchor)
            for row in rows:
                _print(row)
            return 0

        if args.command == "read":
            row = _raw_read(
                root,
                args.source_id,
                topic=args.topic,
                start_char=args.start_char,
                max_chars=args.max_chars,
            )
            _require_authority_anchor(root, expected_anchor)
            _print(row)
            return 0

        if args.command == "relevant":
            row = _relevant_read(
                root,
                args.source_id,
                topic=args.topic,
                query=args.query,
                max_chars=args.max_chars,
            )
            _require_authority_anchor(root, expected_anchor)
            _print(row)
            return 0

        raise AssertionError(args.command)
    except (ValueError, RuntimeError, OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        if str(exc) == "library_store_identity_changed":
            raise SystemExit("FEDERATION-READ-STOP library_store_identity_changed") from None
        raise SystemExit("FEDERATION-READ-STOP federation_read_failed") from None


if __name__ == "__main__":
    raise SystemExit(main())
