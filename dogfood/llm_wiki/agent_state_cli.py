from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_state import (
    add_pending_lineage,
    maintenance_usage,
    open_pending_lineage,
    reserve_maintenance_call,
    resolve_pending_lineage,
    set_source_locator,
    source_locators,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-agent-state")
    p.add_argument("--root", default=".wiki-lab")
    sub = p.add_subparsers(dest="command", required=True)

    locator = sub.add_parser("locator-set")
    locator.add_argument("source_id")
    locator.add_argument("--relative-path", required=True)
    locator.add_argument("--sha256", required=True)
    sub.add_parser("locator-list")

    pending_add = sub.add_parser("pending-add")
    pending_add.add_argument("--created-at", required=True)
    pending_add.add_argument("--topic-id", required=True)
    pending_add.add_argument("--topic-label", required=True)
    pending_add.add_argument("--workspace-file", required=True)
    pending_add.add_argument("--predecessor", action="append", required=True)
    pending_add.add_argument("--successor", required=True)
    sub.add_parser("pending-list")

    pending_resolve = sub.add_parser("pending-resolve")
    pending_resolve.add_argument("decision_id")
    pending_resolve.add_argument("--relation", required=True)
    pending_resolve.add_argument("--predecessor", required=True)
    pending_resolve.add_argument("--resolved-at", required=True)

    usage_status = sub.add_parser("usage-status")
    usage_status.add_argument("--day", required=True)
    usage_reserve = sub.add_parser("usage-reserve")
    usage_reserve.add_argument("--day", required=True)
    usage_reserve.add_argument("--limit", type=int, required=True)
    return p


def _print(value) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = Path(args.root).expanduser()
    try:
        if args.command == "locator-set":
            set_source_locator(root, args.source_id, relative_path=args.relative_path, sha256=args.sha256)
            _print({"status": "OK"})
        elif args.command == "locator-list":
            _print(source_locators(root))
        elif args.command == "pending-add":
            _print(
                add_pending_lineage(
                    root,
                    created_at=args.created_at,
                    topic_id=args.topic_id,
                    topic_label=args.topic_label,
                    workspace_file=args.workspace_file,
                    predecessor_source_ids=args.predecessor,
                    successor_source_id=args.successor,
                )
            )
        elif args.command == "pending-list":
            for row in open_pending_lineage(root):
                _print(row)
        elif args.command == "pending-resolve":
            _print(
                resolve_pending_lineage(
                    root,
                    args.decision_id,
                    relation=args.relation,
                    predecessor_source_id=args.predecessor,
                    resolved_at=args.resolved_at,
                )
            )
        elif args.command == "usage-status":
            _print(maintenance_usage(root, day=args.day))
        elif args.command == "usage-reserve":
            _print(reserve_maintenance_call(root, day=args.day, limit=args.limit))
        else:
            raise AssertionError(args.command)
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"AGENT-STATE-STOP {exc}") from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
