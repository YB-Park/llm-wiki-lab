from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .eventlog import append_jsonl_record
from .store import ensure_workspace, history

RELATION_GENERIC = "generic"
RELATION_CORRECTION = "correction"
RELATION_CHANGE = "change"
REPLACEMENT_KINDS = frozenset({RELATION_GENERIC, RELATION_CORRECTION, RELATION_CHANGE})


@dataclass(frozen=True)
class ReplacementRelation:
    predecessor_source_id: str
    successor_source_id: str
    relation_kind: str
    recorded_at: str
    effective_at: str | None = None


@dataclass(frozen=True)
class TemporalProjection:
    source_ids: frozenset[str]
    current_source_ids: frozenset[str]
    replacements: dict[str, ReplacementRelation]
    active_disputes: frozenset[tuple[str, str]]

    def disputes_for(self, source_id: str) -> tuple[str, ...]:
        peers = {
            right if left == source_id else left
            for left, right in self.active_disputes
            if source_id in (left, right)
        }
        return tuple(sorted(peers))


def _parse_recorded_at(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("invalid_temporal_history_recorded_at") from exc
    if dt.tzinfo is None:
        raise RuntimeError("naive_temporal_history_recorded_at")
    return dt.astimezone(timezone.utc)


def _normalize_effective_at(value: str, *, recorded_at: datetime) -> str:
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("change_effective_at_invalid") from exc
    if dt.tzinfo is None:
        raise ValueError("change_effective_at_must_be_timezone_aware")
    dt = dt.astimezone(timezone.utc)
    if dt > recorded_at.astimezone(timezone.utc):
        raise ValueError("future_change_not_supported")
    return dt.isoformat()


def _normalize_stored_replacement(event: dict) -> ReplacementRelation:
    relation_kind = str(event.get("relation_kind") or RELATION_GENERIC)
    if relation_kind not in REPLACEMENT_KINDS:
        raise RuntimeError(f"invalid_temporal_history_relation_kind:{relation_kind}")
    recorded_at = str(event["recorded_at"])
    recorded_dt = _parse_recorded_at(recorded_at)
    raw_effective = event.get("effective_at")
    if relation_kind == RELATION_CHANGE:
        if not isinstance(raw_effective, str):
            raise RuntimeError("change_history_missing_effective_at")
        try:
            normalized_effective = _normalize_effective_at(raw_effective, recorded_at=recorded_dt)
        except ValueError as exc:
            raise RuntimeError(f"invalid_change_history:{exc}") from exc
    else:
        if raw_effective is not None:
            raise RuntimeError("non_change_history_has_effective_at")
        normalized_effective = None
    return ReplacementRelation(
        predecessor_source_id=str(event["predecessor_source_id"]),
        successor_source_id=str(event["successor_source_id"]),
        relation_kind=relation_kind,
        recorded_at=recorded_dt.isoformat(),
        effective_at=normalized_effective,
    )


def _canonical_dispute_pair(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise ValueError("dispute_self_reference")
    return tuple(sorted((left, right)))  # type: ignore[return-value]


def _stored_dispute_pair(event: dict) -> tuple[str, str]:
    source_ids = event.get("source_ids")
    if not isinstance(source_ids, list) or len(source_ids) != 2 or not all(isinstance(v, str) for v in source_ids):
        raise RuntimeError("invalid_dispute_history_source_ids")
    try:
        pair = _canonical_dispute_pair(source_ids[0], source_ids[1])
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc
    if tuple(source_ids) != pair:
        raise RuntimeError("dispute_history_pair_not_canonical")
    _parse_recorded_at(str(event["recorded_at"]))
    return pair


def temporal_projection(root: Path, *, topic_id: str) -> TemporalProjection:
    """Fold temporal semantics over the same append-only topic history.

    The existing store remains the membership authority. This projection mirrors
    that fold while retaining typed replacement metadata and active dispute
    pairs. Any malformed temporal history fails closed.
    """
    records: set[str] = set()
    active: set[str] = set()
    seen: set[str] = set()
    replacements: dict[str, ReplacementRelation] = {}
    disputes: set[tuple[str, str]] = set()

    for event in history(root):
        if event.get("topic_id") != topic_id:
            continue
        kind = event.get("event")
        if kind == "ingest":
            source_id = str(event["source_id"])
            records.add(source_id)
            first_in_topic = source_id not in seen
            seen.add(source_id)
            if first_in_topic or event.get("reactivates_source") is True:
                active.add(source_id)
                replacements.pop(source_id, None)
            continue

        if kind == "supersede":
            relation = _normalize_stored_replacement(event)
            predecessor = relation.predecessor_source_id
            successor = relation.successor_source_id
            if predecessor not in active:
                raise RuntimeError(f"invalid_temporal_history_predecessor_not_current:{predecessor}")
            if successor not in active:
                raise RuntimeError(f"invalid_temporal_history_successor_not_current:{successor}")
            active.remove(predecessor)
            replacements[predecessor] = relation
            disputes = {pair for pair in disputes if predecessor not in pair}
            continue

        if kind == "dispute":
            pair = _stored_dispute_pair(event)
            if pair[0] not in active or pair[1] not in active:
                raise RuntimeError("invalid_dispute_history_endpoint_not_current")
            disputes.add(pair)
            continue

    return TemporalProjection(
        source_ids=frozenset(records),
        current_source_ids=frozenset(active),
        replacements=dict(replacements),
        active_disputes=frozenset(disputes),
    )


def _append_manifest(root: Path, event: dict) -> None:
    append_jsonl_record(root / "manifest.jsonl", event, log_label="manifest")


def _prepare_replacement(
    relation_kind: str,
    effective_at: str | None,
) -> tuple[str, str, str | None]:
    if relation_kind not in REPLACEMENT_KINDS:
        raise ValueError(f"unsupported_replacement_kind:{relation_kind}")
    recorded_dt = datetime.now(timezone.utc)
    recorded_at = recorded_dt.isoformat()
    if relation_kind == RELATION_CHANGE:
        if effective_at is None:
            raise ValueError("change_effective_at_required")
        normalized_effective = _normalize_effective_at(effective_at, recorded_at=recorded_dt)
    else:
        if effective_at is not None:
            raise ValueError("effective_at_only_valid_for_change")
        normalized_effective = None
    return recorded_at, relation_kind, normalized_effective


def replace_source(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str,
    relation_kind: str = RELATION_GENERIC,
    effective_at: str | None = None,
) -> bool:
    """Append an explicit typed replacement between topic-current revisions.

    Exact retries are idempotent while the recorded successor remains current.
    A different semantic request against an already-replaced predecessor fails
    rather than retroactively relabeling history.
    """
    ensure_workspace(root)
    if predecessor_source_id == successor_source_id:
        raise ValueError("replacement_self_reference")

    recorded_at, relation_kind, normalized_effective = _prepare_replacement(relation_kind, effective_at)
    projection = temporal_projection(root, topic_id=topic_id)

    if predecessor_source_id not in projection.source_ids:
        raise ValueError(f"replacement_predecessor_not_found:{predecessor_source_id}")
    if successor_source_id not in projection.source_ids:
        raise ValueError(f"replacement_successor_not_found:{successor_source_id}")

    existing = projection.replacements.get(predecessor_source_id)
    if predecessor_source_id not in projection.current_source_ids:
        if existing is not None:
            exact = (
                existing.successor_source_id == successor_source_id
                and existing.relation_kind == relation_kind
                and existing.effective_at == normalized_effective
            )
            if exact and successor_source_id in projection.current_source_ids:
                return False
            raise ValueError(f"replacement_semantics_conflict:{predecessor_source_id}")
        raise ValueError(f"replacement_predecessor_not_current:{predecessor_source_id}")

    if successor_source_id not in projection.current_source_ids:
        raise ValueError(f"replacement_successor_not_current:{successor_source_id}")

    event = {
        "event": "supersede",
        "recorded_at": recorded_at,
        "relation_kind": relation_kind,
        "topic_id": topic_id,
        "predecessor_source_id": predecessor_source_id,
        "successor_source_id": successor_source_id,
    }
    if normalized_effective is not None:
        event["effective_at"] = normalized_effective
    _append_manifest(root, event)
    return True


def correct_source(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str,
) -> bool:
    return replace_source(
        root,
        predecessor_source_id,
        successor_source_id,
        topic_id=topic_id,
        relation_kind=RELATION_CORRECTION,
    )


def change_source(
    root: Path,
    predecessor_source_id: str,
    successor_source_id: str,
    *,
    topic_id: str,
    effective_at: str,
) -> bool:
    return replace_source(
        root,
        predecessor_source_id,
        successor_source_id,
        topic_id=topic_id,
        relation_kind=RELATION_CHANGE,
        effective_at=effective_at,
    )


def dispute_sources(
    root: Path,
    left_source_id: str,
    right_source_id: str,
    *,
    topic_id: str,
) -> bool:
    """Mark a symmetric unresolved disagreement without changing membership."""
    ensure_workspace(root)
    pair = _canonical_dispute_pair(left_source_id, right_source_id)
    projection = temporal_projection(root, topic_id=topic_id)
    for source_id in pair:
        if source_id not in projection.source_ids:
            raise ValueError(f"dispute_source_not_found:{source_id}")
        if source_id not in projection.current_source_ids:
            raise ValueError(f"dispute_source_not_current:{source_id}")
    if pair in projection.active_disputes:
        return False
    _append_manifest(
        root,
        {
            "event": "dispute",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "topic_id": topic_id,
            "source_ids": list(pair),
        },
    )
    return True


def temporal_source_status(root: Path, source_id: str, *, topic_id: str) -> dict:
    projection = temporal_projection(root, topic_id=topic_id)
    if source_id not in projection.source_ids:
        raise ValueError(f"source_not_found:{source_id}:scope={topic_id}")

    replacement = projection.replacements.get(source_id)
    disputes_with = projection.disputes_for(source_id) if source_id in projection.current_source_ids else ()
    incoming_changes = [
        relation
        for relation in projection.replacements.values()
        if relation.successor_source_id == source_id and relation.relation_kind == RELATION_CHANGE
    ]
    valid_from = incoming_changes[0].effective_at if len(incoming_changes) == 1 else None

    return {
        "source_id": source_id,
        "status": "current" if source_id in projection.current_source_ids else "superseded",
        "superseded_by": replacement.successor_source_id if replacement else None,
        "replacement_kind": replacement.relation_kind if replacement else None,
        "replacement_recorded_at": replacement.recorded_at if replacement else None,
        "effective_at": replacement.effective_at if replacement and replacement.relation_kind == RELATION_CHANGE else None,
        "valid_from": valid_from,
        "contested": bool(disputes_with),
        "disputes_with": list(disputes_with),
    }


def active_disputes(root: Path, *, topic_id: str) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(temporal_projection(root, topic_id=topic_id).active_disputes))
