from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any

from .private_fs import write_private_text
from .store import ensure_workspace
from .writer_lock import store_writer_lock

STATE_FILE = "agent-state.json"
STATE_FORMAT = "llm-wiki-agent-state-v0"
ALLOWED_RELATIONS = {"correction", "change", "dispute", "supersede", "independent"}


def _path(root: Path) -> Path:
    return root / STATE_FILE


def _empty() -> dict[str, Any]:
    return {
        "format": STATE_FORMAT,
        "pending_lineage": [],
        "maintenance_usage": {"day": "", "reserved_calls": 0},
        "source_locators": {},
    }


def _validate(state: object) -> dict[str, Any]:
    if not isinstance(state, dict) or state.get("format") != STATE_FORMAT:
        raise RuntimeError("agent_state_format_invalid")
    if set(state) != {"format", "pending_lineage", "maintenance_usage", "source_locators"}:
        raise RuntimeError("agent_state_shape_invalid")
    pending = state["pending_lineage"]
    usage = state["maintenance_usage"]
    locators = state["source_locators"]
    if not isinstance(pending, list) or not isinstance(usage, dict) or not isinstance(locators, dict):
        raise RuntimeError("agent_state_shape_invalid")
    if set(usage) != {"day", "reserved_calls"}:
        raise RuntimeError("agent_state_usage_invalid")
    if not isinstance(usage["day"], str) or not isinstance(usage["reserved_calls"], int) or usage["reserved_calls"] < 0:
        raise RuntimeError("agent_state_usage_invalid")
    for row in pending:
        if not isinstance(row, dict):
            raise RuntimeError("agent_state_pending_invalid")
        required = {
            "id", "status", "created_at", "resolved_at", "topic_id", "topic_label",
            "workspace_file", "predecessor_source_ids", "successor_source_id", "relation",
            "predecessor_source_id",
        }
        if set(row) != required:
            raise RuntimeError("agent_state_pending_invalid")
        if row["status"] not in {"open", "resolved"}:
            raise RuntimeError("agent_state_pending_invalid")
        if not isinstance(row["predecessor_source_ids"], list) or not row["predecessor_source_ids"]:
            raise RuntimeError("agent_state_pending_invalid")
    for source_id, locator in locators.items():
        if not isinstance(source_id, str) or not isinstance(locator, dict):
            raise RuntimeError("agent_state_locator_invalid")
        if set(locator) != {"relative_path", "sha256"}:
            raise RuntimeError("agent_state_locator_invalid")
        if not isinstance(locator["relative_path"], str) or not isinstance(locator["sha256"], str):
            raise RuntimeError("agent_state_locator_invalid")
    return state


def read_agent_state(root: Path) -> dict[str, Any]:
    ensure_workspace(root)
    path = _path(root)
    if not path.exists():
        return _empty()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("agent_state_unreadable") from exc
    return _validate(value)


def _write(root: Path, state: dict[str, Any]) -> None:
    _validate(state)
    write_private_text(_path(root), json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def set_source_locator(root: Path, source_id: str, *, relative_path: str, sha256: str) -> None:
    if not source_id.startswith("src-") or not relative_path or relative_path.startswith("/") or ".." in Path(relative_path).parts:
        raise ValueError("agent_state_locator_invalid")
    if len(sha256) != 64 or any(ch not in "0123456789abcdef" for ch in sha256):
        raise ValueError("agent_state_locator_invalid")
    ensure_workspace(root)
    with store_writer_lock(root):
        state = read_agent_state(root)
        state["source_locators"][source_id] = {"relative_path": relative_path, "sha256": sha256}
        _write(root, state)


def source_locators(root: Path) -> dict[str, dict[str, str]]:
    return dict(read_agent_state(root)["source_locators"])


def add_pending_lineage(
    root: Path,
    *,
    created_at: str,
    topic_id: str,
    topic_label: str,
    workspace_file: str,
    predecessor_source_ids: list[str],
    successor_source_id: str,
) -> dict[str, Any]:
    predecessors = sorted(set(predecessor_source_ids))
    if not predecessors or successor_source_id in predecessors:
        raise ValueError("agent_state_pending_invalid")
    ensure_workspace(root)
    with store_writer_lock(root):
        state = read_agent_state(root)
        # Exact retry of an already-open decision reuses it instead of creating
        # approval spam for the same admitted revision relationship.
        for row in state["pending_lineage"]:
            if (
                row["status"] == "open"
                and row["topic_id"] == topic_id
                and row["successor_source_id"] == successor_source_id
                and sorted(row["predecessor_source_ids"]) == predecessors
            ):
                return dict(row)
        row = {
            "id": f"pd-{secrets.token_hex(8)}",
            "status": "open",
            "created_at": created_at,
            "resolved_at": "",
            "topic_id": topic_id,
            "topic_label": topic_label,
            "workspace_file": workspace_file,
            "predecessor_source_ids": predecessors,
            "successor_source_id": successor_source_id,
            "relation": "",
            "predecessor_source_id": "",
        }
        # Never evict unresolved decisions to cap file size. A safety-relevant
        # decision may be old and still matter. Future compaction may remove
        # resolved rows only, under an explicit migration/maintenance contract.
        state["pending_lineage"].append(row)
        _write(root, state)
        return dict(row)


def open_pending_lineage(root: Path) -> list[dict[str, Any]]:
    return [dict(row) for row in read_agent_state(root)["pending_lineage"] if row["status"] == "open"]


def resolve_pending_lineage(
    root: Path,
    decision_id: str,
    *,
    relation: str,
    predecessor_source_id: str,
    resolved_at: str,
) -> dict[str, Any]:
    if relation not in ALLOWED_RELATIONS:
        raise ValueError("agent_state_relation_invalid")
    ensure_workspace(root)
    with store_writer_lock(root):
        state = read_agent_state(root)
        for index, row in enumerate(state["pending_lineage"]):
            if row["id"] != decision_id:
                continue
            if row["status"] != "open":
                raise RuntimeError("agent_state_pending_already_resolved")
            if predecessor_source_id not in row["predecessor_source_ids"]:
                raise ValueError("agent_state_predecessor_invalid")
            updated = dict(row)
            updated.update(
                {
                    "status": "resolved",
                    "resolved_at": resolved_at,
                    "relation": relation,
                    "predecessor_source_id": predecessor_source_id,
                }
            )
            state["pending_lineage"][index] = updated
            _write(root, state)
            return dict(updated)
    raise RuntimeError("agent_state_pending_not_found")


def maintenance_usage(root: Path, *, day: str) -> dict[str, Any]:
    usage = read_agent_state(root)["maintenance_usage"]
    count = usage["reserved_calls"] if usage["day"] == day else 0
    return {"day": day, "reserved_calls": count}


def reserve_maintenance_call(root: Path, *, day: str, limit: int) -> dict[str, Any]:
    if limit < 0 or limit > 100:
        raise ValueError("agent_state_maintenance_limit_invalid")
    ensure_workspace(root)
    with store_writer_lock(root):
        state = read_agent_state(root)
        usage = state["maintenance_usage"]
        count = usage["reserved_calls"] if usage["day"] == day else 0
        if limit == 0 or count >= limit:
            return {"allowed": False, "day": day, "limit": limit, "reserved_calls": count, "remaining": 0}
        count += 1
        state["maintenance_usage"] = {"day": day, "reserved_calls": count}
        _write(root, state)
        return {
            "allowed": True,
            "day": day,
            "limit": limit,
            "reserved_calls": count,
            "remaining": max(0, limit - count),
        }
