from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import answer_prompt, ask_copilot
from .calibration import (
    QUERY_CLASSES,
    create_topic,
    record_feedback,
    record_ingest,
    record_query,
    record_source_open,
    resolve_topic,
    sanitized_json,
    topics,
)
from .retrieval import render_context, search
from .store import (
    ensure_workspace,
    find_source,
    history,
    ingest_file,
    read_text,
    source_status,
    supersede_source,
)


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _resolved_topic_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return resolve_topic(root, value)["topic_id"]
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"TOPIC-STOP {exc}") from None


def _add_topic_and_class_args(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument("--topic", help="local topic label or opaque topic ID; enables local-only E013 calibration")
    cmd.add_argument("--class", dest="query_class", choices=QUERY_CLASSES, help="optional explicit E013 query class")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-dogfood")
    p.add_argument("--root", default=".wiki-lab", help="local workspace (default: .wiki-lab)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init")

    topic = sub.add_parser("topic")
    topic_sub = topic.add_subparsers(dest="topic_command", required=True)
    topic_add = topic_sub.add_parser("add")
    topic_add.add_argument("label")
    topic_sub.add_parser("list")

    ingest = sub.add_parser("ingest")
    ingest.add_argument("files", nargs="+")
    ingest.add_argument("--topic", help="associate evidence with a local topic")
    ingest.add_argument(
        "--authoritative-update",
        action="store_true",
        help="explicitly start a new E013 maintenance cycle; requires --topic",
    )
    ingest.add_argument(
        "--supersedes",
        metavar="SOURCE_ID",
        help="explicitly mark the single ingested source as replacing SOURCE_ID in the same topic; independent of --authoritative-update",
    )

    srch = sub.add_parser("search")
    srch.add_argument("query")
    srch.add_argument("--top-k", type=int, default=8)
    srch.add_argument("--json", action="store_true")
    srch.add_argument(
        "--include-superseded",
        action="store_true",
        help="include historical superseded evidence; default topic search uses current evidence only",
    )
    _add_topic_and_class_args(srch)

    ctx = sub.add_parser("context")
    ctx.add_argument("query")
    ctx.add_argument("--top-k", type=int, default=8)
    ctx.add_argument("--max-chars", type=int, default=1200)
    ctx.add_argument(
        "--include-superseded",
        action="store_true",
        help="include historical superseded evidence; intended for inspection/debugging",
    )
    _add_topic_and_class_args(ctx)

    ask = sub.add_parser("ask")
    ask.add_argument("query")
    ask.add_argument("--top-k", type=int, default=8)
    ask.add_argument("--max-chars", type=int, default=1200)
    ask.add_argument("--model", default="gpt-5.6-luna")
    ask.add_argument("--max-ai-credits", type=int, default=30)
    ask.add_argument(
        "--allow-model-call",
        action="store_true",
        help="required opt-in: sends rendered current-evidence context to the configured Copilot model",
    )
    _add_topic_and_class_args(ask)

    source = sub.add_parser("source")
    source_sub = source.add_subparsers(dest="source_command", required=True)
    source_show = source_sub.add_parser("show")
    source_show.add_argument("source_id")
    source_show.add_argument("--topic", help="scope source and record a local provenance-follow event")

    source_status_cmd = source_sub.add_parser("status")
    source_status_cmd.add_argument("source_id")
    source_status_cmd.add_argument("--topic", required=True, help="topic label or opaque topic ID")

    source_supersede = source_sub.add_parser("supersede")
    source_supersede.add_argument("predecessor_source_id")
    source_supersede.add_argument("successor_source_id")
    source_supersede.add_argument("--topic", required=True, help="topic label or opaque topic ID")

    feedback = sub.add_parser("feedback")
    feedback.add_argument("outcome", choices=("helpful", "not_helpful"))
    feedback.add_argument("--topic", required=True)
    feedback.add_argument(
        "--reason",
        choices=("correct", "found_source", "missing_source", "wrong", "incomplete", "other"),
    )

    calibration = sub.add_parser("calibration")
    calibration_sub = calibration.add_subparsers(dest="calibration_command", required=True)
    calibration_sub.add_parser("export")

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

    if args.command == "topic":
        ensure_workspace(root)
        if args.topic_command == "add":
            row = create_topic(root, args.label)
            print(f"TOPIC id={row['topic_id']} label={json.dumps(row['label'], ensure_ascii=False)} telemetry=local-only")
            return 0
        if args.topic_command == "list":
            for row in topics(root):
                print(f"{row['topic_id']} {row['label']}")
            return 0
        raise AssertionError(args.topic_command)

    if args.command == "ingest":
        ensure_workspace(root)
        if args.authoritative_update and not args.topic:
            raise SystemExit("INGEST-STOP --authoritative-update requires --topic")
        if args.supersedes and not args.topic:
            raise SystemExit("INGEST-STOP --supersedes requires --topic")
        if args.supersedes and len(args.files) != 1:
            raise SystemExit("INGEST-STOP --supersedes requires exactly one input file")

        topic_id = _resolved_topic_id(root, args.topic)
        completed = []
        for value in args.files:
            try:
                src, duplicate = ingest_file(
                    root,
                    Path(value),
                    topic_id=topic_id,
                    supersedes_source_id=args.supersedes,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"INGEST-STOP {exc}") from None
            completed.append((src, duplicate))
            print(
                f"INGEST source={src.source_id} sha256={src.sha256} bytes={src.size_bytes} "
                f"duplicate={'yes' if duplicate else 'no'} name={json.dumps(src.name, ensure_ascii=False)}"
            )
            if args.supersedes:
                print(f"SUPERSEDE predecessor={args.supersedes} successor={src.source_id} scope=topic")

        if topic_id is not None and completed:
            kind = record_ingest(root, topic_id, authoritative_update=args.authoritative_update)
            print(f"CALIBRATION ingest={kind} telemetry=local-only rawQueryStored=no")
        return 0

    if args.command == "search":
        topic_id = _resolved_topic_id(root, args.topic)
        if topic_id is not None:
            record_query(root, topic_id, "search", args.query_class)
        rows = search(
            root,
            args.query,
            top_k=args.top_k,
            topic_id=topic_id,
            include_superseded=args.include_superseded,
        )
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
        topic_id = _resolved_topic_id(root, args.topic)
        if topic_id is not None:
            record_query(root, topic_id, "context", args.query_class)
        text = render_context(
            root,
            args.query,
            top_k=args.top_k,
            max_chars_per_source=args.max_chars,
            topic_id=topic_id,
            include_superseded=args.include_superseded,
        )
        print(text)
        return 0

    if args.command == "ask":
        if not args.allow_model_call:
            raise SystemExit(
                "ASK-STOP model_call_not_authorized: rerun with --allow-model-call only for evidence you are permitted to send"
            )
        topic_id = _resolved_topic_id(root, args.topic)
        if topic_id is not None:
            record_query(root, topic_id, "ask", args.query_class)
        context = render_context(
            root,
            args.query,
            top_k=args.top_k,
            max_chars_per_source=args.max_chars,
            topic_id=topic_id,
            include_superseded=False,
        )
        if not context.strip():
            raise SystemExit("ASK-STOP no_retrieved_evidence")
        answer = ask_copilot(
            answer_prompt(args.query, context),
            model=args.model,
            max_ai_credits=args.max_ai_credits,
        )
        print(f"MODEL {answer.model or args.model}")
        print(answer.text)
        return 0

    if args.command == "source":
        if args.source_command == "show":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                src = find_source(root, args.source_id, topic_id=topic_id)
            except ValueError as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            if topic_id is not None:
                record_source_open(root, topic_id)
                state = source_status(root, src.source_id, topic_id=topic_id)
                if state["status"] == "superseded":
                    print(
                        f"SOURCE {src.source_id} name={src.name} sha256={src.sha256} "
                        f"status=superseded supersededBy={state['superseded_by']}"
                    )
                else:
                    print(f"SOURCE {src.source_id} name={src.name} sha256={src.sha256} status=current")
            else:
                print(f"SOURCE {src.source_id} name={src.name} sha256={src.sha256} status=unscoped")
            print(read_text(src))
            return 0

        if args.source_command == "status":
            topic_id = _resolved_topic_id(root, args.topic)
            assert topic_id is not None
            try:
                state = source_status(root, args.source_id, topic_id=topic_id)
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            print(json.dumps(state, sort_keys=True))
            return 0

        if args.source_command == "supersede":
            topic_id = _resolved_topic_id(root, args.topic)
            assert topic_id is not None
            try:
                created = supersede_source(
                    root,
                    args.predecessor_source_id,
                    args.successor_source_id,
                    topic_id=topic_id,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            print(
                f"SUPERSEDE predecessor={args.predecessor_source_id} successor={args.successor_source_id} "
                f"scope=topic created={'yes' if created else 'no'}"
            )
            return 0
        raise AssertionError(args.source_command)

    if args.command == "feedback":
        topic_id = _resolved_topic_id(root, args.topic)
        assert topic_id is not None
        record_feedback(root, topic_id, args.outcome, args.reason)
        print(f"FEEDBACK outcome={args.outcome} telemetry=local-only")
        return 0

    if args.command == "calibration":
        if args.calibration_command == "export":
            print(sanitized_json(root), end="")
            return 0
        raise AssertionError(args.calibration_command)

    if args.command == "history":
        rows = history(root)[-max(0, args.limit):]
        for row in rows:
            if args.json:
                print(json.dumps(row, ensure_ascii=False, sort_keys=True))
                continue
            if row.get("event") == "ingest":
                print(
                    f"{row['recorded_at']} event=ingest source={row['source_id']} "
                    f"duplicate={'yes' if row.get('duplicate_content') else 'no'} name={row['name']}"
                )
            elif row.get("event") == "supersede":
                print(
                    f"{row['recorded_at']} event=supersede predecessor={row['predecessor_source_id']} "
                    f"successor={row['successor_source_id']} topic={row['topic_id']}"
                )
            else:
                print(f"{row.get('recorded_at', '?')} event={row.get('event', 'unknown')}")
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
