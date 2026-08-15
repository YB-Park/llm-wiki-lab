from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_wiki import build_agent_source_note, read_agent_source_note, search_agent_notes
from .calibration import resolve_topic


def _root(value: str) -> Path:
    return Path(value).expanduser()


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-agent-wiki")
    p.add_argument("--root", default=".wiki-lab")
    sub = p.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("source_id")
    build.add_argument("--topic", required=True)
    build.add_argument("--model", default="gpt-5.6-luna")
    build.add_argument("--max-ai-credits", type=int, default=30)
    build.add_argument("--allow-model-call", action="store_true")

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=3)
    search.add_argument("--json", action="store_true")

    show = sub.add_parser("show")
    show.add_argument("source_id")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = _root(args.root)

    if args.command == "build":
        topic_id = resolve_topic(root, args.topic)["topic_id"]
        result = build_agent_source_note(
            root,
            args.source_id,
            topic_id=topic_id,
            model=args.model,
            max_ai_credits=args.max_ai_credits,
            allow_model_call=args.allow_model_call,
        )
        record = result["record"]
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "model_calls": result["model_calls"],
                    "source_id": record["source_id"],
                    "topic_id": record["topic_id"],
                    "model": record["model"],
                    "policy": record["policy"],
                    "markdown_path": result["markdown_path"],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "search":
        hits = search_agent_notes(root, args.query, top_k=args.top_k)
        for hit in hits:
            row = {
                "source_id": hit.source_id,
                "topic_id": hit.topic_id,
                "title": hit.title,
                "score": hit.score,
                "snippet": hit.snippet,
                "markdown_path": str(hit.markdown_path),
                "epistemic_status": "derived_noncanonical_agent_wiki",
            }
            if args.json:
                print(json.dumps(row, ensure_ascii=False, sort_keys=True))
            else:
                print(f"{hit.source_id} score={hit.score:.6f} title={json.dumps(hit.title, ensure_ascii=False)}")
        return 0

    if args.command == "show":
        record = read_agent_source_note(root, args.source_id)
        if record is None:
            raise SystemExit(f"AGENT-WIKI-STOP note_not_found:{args.source_id}")
        markdown = root / "agent-wiki" / "source-notes" / f"{args.source_id}.md"
        if not markdown.exists():
            raise SystemExit(f"AGENT-WIKI-STOP markdown_missing:{args.source_id}")
        print(markdown.read_text(encoding="utf-8"), end="")
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
