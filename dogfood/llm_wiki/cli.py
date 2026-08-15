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
from .discovery import discover_current
from .integrity import audit_alpha_integrity
from .retrieval import render_context, search
from .shadow import compare_retrieval_modes
from .shadow_calibration import (
    record_retrieval_shadow,
    record_retrieval_shadow_failure,
    summarize_shadow,
)
from .store import (
    ensure_workspace,
    find_source,
    history,
    ingest_file,
    read_text,
    source_status,
    sources,
    supersede_source,
)
from .temporal import change_source, correct_source, dispute_sources, temporal_source_status


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _resolved_topic_id(root: Path, value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return resolve_topic(root, value)["topic_id"]
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"TOPIC-STOP {exc}") from None


def _safe_record_retrieval_shadow(
    root: Path,
    topic_id: str | None,
    operation: str,
    query: str,
    query_class: str | None,
    *,
    top_k: int,
    snippet_chars: int,
    include_superseded: bool,
) -> None:
    """Run E015 shadow comparison without allowing it to break W0 behavior."""
    if topic_id is None:
        return
    try:
        observation = compare_retrieval_modes(
            root,
            query,
            topic_id=topic_id,
            top_k=top_k,
            snippet_chars=snippet_chars,
            include_superseded=include_superseded,
        )
        record_retrieval_shadow(root, topic_id, operation, observation, query_class)
    except Exception:
        # Shadow is explicitly non-authoritative. Never persist exception text,
        # query/content/IDs, and never fail the user-visible W0 operation.
        try:
            record_retrieval_shadow_failure(root, topic_id, operation, query_class)
        except Exception:
            pass


def _add_topic_and_class_args(cmd: argparse.ArgumentParser, *, topic_required: bool = False) -> None:
    cmd.add_argument(
        "--topic",
        required=topic_required,
        help=(
            "local topic label or opaque topic ID; required for model-backed Ask so only topic-current evidence is sent"
            if topic_required
            else "local topic label or opaque topic ID; enables local-only E013 calibration"
        ),
    )
    cmd.add_argument("--class", dest="query_class", choices=QUERY_CLASSES, help="optional explicit E013 query class")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-dogfood")
    p.add_argument("--root", default=".wiki-lab", help="local workspace (default: .wiki-lab)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("integrity")

    topic = sub.add_parser("topic")
    topic_sub = topic.add_subparsers(dest="topic_command", required=True)
    topic_add = topic_sub.add_parser("add")
    topic_add.add_argument("label")
    topic_sub.add_parser("list")

    ingest = sub.add_parser("ingest")
    ingest.add_argument("files", nargs="+")
    ingest.add_argument("--topic", help="associate evidence with a local topic")
    ingest.add_argument(
        "--origin-id",
        help=(
            "optional caller-asserted opaque origin token; use only a non-sensitive stable ID, "
            "never a raw path/username. Core does not infer origin identity"
        ),
    )
    ingest.add_argument(
        "--authoritative-update",
        action="store_true",
        help="explicitly start a new E013 maintenance cycle; requires --topic",
    )
    ingest.add_argument(
        "--supersedes",
        metavar="SOURCE_ID",
        help="explicitly mark the single ingested source revision as replacing SOURCE_ID in the same topic; independent of --authoritative-update",
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

    discover = sub.add_parser("discover")
    discover.add_argument("query")
    discover.add_argument("--top-k-per-topic", type=int, default=3)
    discover.add_argument("--json", action="store_true")

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

    source_list = source_sub.add_parser("list")
    source_list.add_argument("--topic", required=True, help="topic label or opaque topic ID")
    source_list.add_argument("--json", action="store_true")
    source_list.add_argument("--include-superseded", action="store_true")

    source_status_cmd = source_sub.add_parser("status")
    source_status_cmd.add_argument("source_id")
    source_status_cmd.add_argument("--topic", required=True, help="topic label or opaque topic ID")

    source_supersede = source_sub.add_parser("supersede")
    source_supersede.add_argument("predecessor_source_id")
    source_supersede.add_argument("successor_source_id")
    source_supersede.add_argument("--topic", required=True, help="topic label or opaque topic ID")

    source_correct = source_sub.add_parser("correct")
    source_correct.add_argument("predecessor_source_id")
    source_correct.add_argument("successor_source_id")
    source_correct.add_argument("--topic", required=True, help="topic label or opaque topic ID")

    source_change = source_sub.add_parser("change")
    source_change.add_argument("predecessor_source_id")
    source_change.add_argument("successor_source_id")
    source_change.add_argument("--topic", required=True, help="topic label or opaque topic ID")
    source_change.add_argument("--effective-at", required=True, help="timezone-aware ISO-8601 effective instant")

    source_dispute = source_sub.add_parser("dispute")
    source_dispute.add_argument("left_source_id")
    source_dispute.add_argument("right_source_id")
    source_dispute.add_argument("--topic", required=True, help="topic label or opaque topic ID")

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

    if args.command == "integrity":
        print(json.dumps(audit_alpha_integrity(root), sort_keys=True, ensure_ascii=False))
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
        calibration_kind: str | None = None
        for value in args.files:
            try:
                src, duplicate = ingest_file(
                    root,
                    Path(value),
                    topic_id=topic_id,
                    supersedes_source_id=args.supersedes,
                    origin_id=args.origin_id,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"INGEST-STOP {exc}") from None
            print(
                f"INGEST source={src.source_id} object={src.object_id} sha256={src.sha256} bytes={src.size_bytes} "
                f"duplicateObject={'yes' if duplicate else 'no'} name={json.dumps(src.name, ensure_ascii=False)}"
            )
            if args.supersedes:
                print(f"SUPERSEDE predecessor={args.supersedes} successor={src.source_id} scope=topic")
            if topic_id is not None and calibration_kind is None:
                calibration_kind = record_ingest(root, topic_id, authoritative_update=args.authoritative_update)
                print(f"CALIBRATION ingest={calibration_kind} telemetry=local-only rawQueryStored=no")
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
        _safe_record_retrieval_shadow(
            root,
            topic_id,
            "search",
            args.query,
            args.query_class,
            top_k=args.top_k,
            snippet_chars=320,
            include_superseded=args.include_superseded,
        )
        if args.json:
            for h in rows:
                print(json.dumps({
                    "source_id": h.source.source_id,
                    "source_ids": list(h.source_ids),
                    "object_id": h.object_id,
                    "provenance_count": len(h.evidence_sources),
                    "sha256": h.source.sha256,
                    "name": h.source.name,
                    "names": sorted({src.name for src in h.evidence_sources}),
                    "score": h.score,
                    "snippet": h.snippet,
                }, ensure_ascii=False, sort_keys=True))
        else:
            for i, h in enumerate(rows, 1):
                snippet = " ".join(h.snippet.split())
                print(
                    f"{i:02d} score={h.score:.6f} object={h.object_id} "
                    f"sources={','.join(h.source_ids)} name={h.source.name}"
                )
                print(f"   {snippet}")
        return 0

    if args.command == "discover":
        ensure_workspace(root)
        rows = discover_current(
            root,
            args.query,
            top_k_per_topic=max(0, args.top_k_per_topic),
            snippet_chars=320,
        )
        if not rows and not args.json:
            print("DISCOVER no_current_topic_hits")
            return 0
        for hit in rows:
            row = {
                "topic_id": hit.topic_id,
                "topic_label": hit.topic_label,
                "source_id": hit.source.source_id,
                "source_ids": list(hit.source_ids),
                "object_id": hit.object_id,
                "sha256": hit.source.sha256,
                "name": hit.source.name,
                "names": sorted({src.name for src in hit.evidence_sources}),
                "score": hit.score,
                "snippet": hit.snippet,
            }
            if args.json:
                print(json.dumps(row, ensure_ascii=False, sort_keys=True))
            else:
                print(
                    f"topic={json.dumps(hit.topic_label, ensure_ascii=False)} "
                    f"source={hit.source.source_id} score={hit.score:.6f} name={hit.source.name}"
                )
                print(f"   {' '.join(hit.snippet.split())}")
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
        _safe_record_retrieval_shadow(
            root,
            topic_id,
            "context",
            args.query,
            args.query_class,
            top_k=args.top_k,
            snippet_chars=args.max_chars,
            include_superseded=args.include_superseded,
        )
        print(text)
        return 0

    if args.command == "ask":
        if not args.allow_model_call:
            raise SystemExit(
                "ASK-STOP model_call_not_authorized: rerun with --allow-model-call only for evidence you are permitted to send"
            )
        if not args.topic:
            raise SystemExit("ASK-STOP topic_required: model-backed Ask is topic-scoped and uses current evidence only")
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
        _safe_record_retrieval_shadow(
            root,
            topic_id,
            "ask",
            args.query,
            args.query_class,
            top_k=args.top_k,
            snippet_chars=args.max_chars,
            include_superseded=False,
        )
        prompt = answer_prompt(context, args.query)
        try:
            answer = ask_copilot(
                prompt,
                model=args.model,
                max_ai_credits=args.max_ai_credits,
            )
        except RuntimeError as exc:
            raise SystemExit(f"ASK-STOP {exc}") from None
        print(f"MODEL {args.model}")
        print(answer)
        return 0

    if args.command == "source":
        ensure_workspace(root)
        if args.source_command == "show":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                src = find_source(root, args.source_id, topic_id=topic_id)
                text = read_text(src)
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            if topic_id is not None:
                record_source_open(root, topic_id)
            print(
                f"SOURCE id={src.source_id} object={src.object_id} sha256={src.sha256} "
                f"bytes={src.size_bytes} name={json.dumps(src.name, ensure_ascii=False)}"
            )
            print(text)
            return 0

        if args.source_command == "list":
            topic_id = _resolved_topic_id(root, args.topic)
            rows = sources(root, topic_id=topic_id, include_superseded=args.include_superseded)
            if args.json:
                for src in rows:
                    temporal = temporal_source_status(root, topic_id, src.source_id)
                    print(json.dumps({
                        "source_id": src.source_id,
                        "object_id": src.object_id,
                        "sha256": src.sha256,
                        "name": src.name,
                        "size_bytes": src.size_bytes,
                        "status": temporal["status"],
                        "replacement_kind": temporal["replacement_kind"],
                        "superseded_by": temporal["superseded_by"],
                        "effective_at": temporal["effective_at"],
                        "contested": temporal["contested"],
                    }, ensure_ascii=False, sort_keys=True))
            else:
                for src in rows:
                    temporal = temporal_source_status(root, topic_id, src.source_id)
                    print(
                        f"{src.source_id} {temporal['status']} {src.name} sha256={src.sha256} "
                        f"replacement={temporal['replacement_kind'] or '-'} contested={'yes' if temporal['contested'] else 'no'}"
                    )
            return 0

        if args.source_command == "status":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                print(json.dumps(temporal_source_status(root, topic_id, args.source_id), sort_keys=True, ensure_ascii=False))
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            return 0

        if args.source_command == "supersede":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                written = supersede_source(
                    root,
                    args.predecessor_source_id,
                    args.successor_source_id,
                    topic_id=topic_id,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            print(
                f"SUPERSEDE predecessor={args.predecessor_source_id} successor={args.successor_source_id} "
                f"scope=topic written={'yes' if written else 'no'}"
            )
            return 0

        if args.source_command == "correct":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                written = correct_source(
                    root,
                    args.predecessor_source_id,
                    args.successor_source_id,
                    topic_id=topic_id,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            print(
                f"CORRECTION predecessor={args.predecessor_source_id} successor={args.successor_source_id} "
                f"scope=topic written={'yes' if written else 'no'}"
            )
            return 0

        if args.source_command == "change":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                written = change_source(
                    root,
                    args.predecessor_source_id,
                    args.successor_source_id,
                    topic_id=topic_id,
                    effective_at=args.effective_at,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            print(
                f"CHANGE predecessor={args.predecessor_source_id} successor={args.successor_source_id} "
                f"scope=topic effective_at={args.effective_at} written={'yes' if written else 'no'}"
            )
            return 0

        if args.source_command == "dispute":
            topic_id = _resolved_topic_id(root, args.topic)
            try:
                written = dispute_sources(
                    root,
                    args.left_source_id,
                    args.right_source_id,
                    topic_id=topic_id,
                )
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"SOURCE-STOP {exc}") from None
            print(
                f"DISPUTE left={args.left_source_id} right={args.right_source_id} "
                f"scope=topic written={'yes' if written else 'no'}"
            )
            return 0

    if args.command == "feedback":
        topic_id = _resolved_topic_id(root, args.topic)
        record_feedback(root, topic_id, args.outcome, args.reason)
        print(f"FEEDBACK outcome={args.outcome} reason={args.reason or '-'} telemetry=local-only freeTextStored=no")
        return 0

    if args.command == "calibration":
        if args.calibration_command == "export":
            payload = sanitized_json(root)
            payload["retrieval_shadow"] = summarize_shadow(root)
            print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
            return 0
        raise AssertionError(args.calibration_command)

    if args.command == "history":
        rows = history(root, limit=max(args.limit, 0))
        if args.json:
            for row in rows:
                print(json.dumps(row, sort_keys=True, ensure_ascii=False))
        else:
            for row in rows:
                print(json.dumps(row, sort_keys=True, ensure_ascii=False))
        return 0

    raise AssertionError(args.command)
