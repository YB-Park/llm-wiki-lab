from __future__ import annotations

import argparse
import json
from pathlib import Path

from .retrieval import render_context, search
from .store import ensure_workspace, history, ingest_file


def _root(value: str) -> Path:
    return Path(value).expanduser()


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-dogfood")
    p.add_argument("--root", default=".wiki-lab", help="local workspace (default: .wiki-lab)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init")

    ingest = sub.add_parser("ingest")
    ingest.add_argument("files", nargs="+")

    srch = sub.add_parser("search")
    srch.add_argument("query")
    srch.add_argument("--top-k", type=int, default=8)
    srch.add_argument("--json", action="store_true")

    ctx = sub.add_parser("context")
    ctx.add_argument("query")
    ctx.add_argument("--top-k", type=int, default=8)
    ctx.add_argument("--max-chars", type=int, default=1200)

    hist = sub.add_parser("history")
    hist.add_argument("--limit", type=int, default=20)
    hist.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = _root(args.root)

    if args.command == "init":
        ensure_workspace(root)
        print(f"WIKI-INIT root={root} compiledProvider=disabled network=none")
        return 0

    if args.command == "ingest":
        ensure_workspace(root)
        for value in args.files:
            src, duplicate = ingest_file(root, Path(value))
            print(
                f"INGEST source={src.source_id} sha256={src.sha256} bytes={src.size_bytes} "
                f"duplicate={'yes' if duplicate else 'no'} name={json.dumps(src.name, ensure_ascii=False)}"
            )
        return 0

    if args.command == "search":
        rows = search(root, args.query, top_k=args.top_k)
        if args.json:
            for h in rows:
                print(json.dumps({
                    "source_id": h.source.source_id,
                    "sha256": h.source.sha256,
                    "name": h.source.name,
                    "score": h.score,
                    "snippet": h.snippet,
                }, ensure_ascii=False, sort_keys=True))
        else:
            for i, h in enumerate(rows, 1):
                snippet = " ".join(h.snippet.split())
                print(f"{i:02d} score={h.score:.6f} source={h.source.source_id} name={h.source.name}")
                print(f"   {snippet}")
        return 0

    if args.command == "context":
        text = render_context(root, args.query, top_k=args.top_k, max_chars_per_source=args.max_chars)
        print(text)
        return 0

    if args.command == "history":
        rows = history(root)[-max(0, args.limit):]
        for row in rows:
            if args.json:
                print(json.dumps(row, ensure_ascii=False, sort_keys=True))
            else:
                print(
                    f"{row['recorded_at']} event={row['event']} source={row['source_id']} "
                    f"duplicate={'yes' if row.get('duplicate_content') else 'no'} name={row['name']}"
                )
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
