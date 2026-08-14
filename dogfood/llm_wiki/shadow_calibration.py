from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .calibration import QUERY_CLASSES
from .private_fs import append_private_text, ensure_private_directory
from .shadow import RetrievalShadowObservation

SHADOW_EVENTS_FILE = "retrieval-shadow-events.jsonl"
SHADOW_FORMAT = "llm-wiki-e015-shadow-v0"
SESSION_GAP = timedelta(minutes=30)


def _iso(value: datetime | None = None) -> str:
    dt = value or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _parse(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _path(root: Path) -> Path:
    return root / SHADOW_EVENTS_FILE


def _events(root: Path) -> list[dict]:
    path = _path(root)
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _validate_common(operation: str, query_class: str | None) -> None:
    if operation not in {"search", "context", "ask"}:
        raise ValueError(f"unsupported_shadow_operation:{operation}")
    if query_class is not None and query_class not in QUERY_CLASSES:
        raise ValueError(f"unsupported_shadow_query_class:{query_class}")


def _append(root: Path, row: dict) -> None:
    ensure_private_directory(root)
    append_private_text(_path(root), json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def record_retrieval_shadow(
    root: Path,
    topic_id: str,
    operation: str,
    observation: RetrievalShadowObservation,
    query_class: str | None = None,
    *,
    recorded_at: datetime | None = None,
) -> None:
    _validate_common(operation, query_class)

    fields = observation.as_telemetry_fields()
    numeric = (
        "default_count",
        "candidate_count",
        "overlap_count",
        "default_only_count",
        "candidate_only_count",
        "default_context_chars",
        "candidate_context_chars",
    )
    if any(not isinstance(fields[key], int) or fields[key] < 0 for key in numeric):
        raise ValueError("invalid_shadow_numeric_field")
    if fields["overlap_count"] > max(fields["default_count"], fields["candidate_count"]):
        raise ValueError("invalid_shadow_overlap")

    row: dict = {
        "event": "retrieval_shadow",
        "format": SHADOW_FORMAT,
        "topic_id": topic_id,
        "operation": operation,
        "recorded_at": _iso(recorded_at),
        **fields,
    }
    if query_class is not None:
        row["query_class"] = query_class
    _append(root, row)


def record_retrieval_shadow_failure(
    root: Path,
    topic_id: str,
    operation: str,
    query_class: str | None = None,
    *,
    recorded_at: datetime | None = None,
) -> None:
    """Record only that shadow infrastructure failed; never persist details."""
    _validate_common(operation, query_class)
    row: dict = {
        "event": "shadow_failure",
        "format": SHADOW_FORMAT,
        "topic_id": topic_id,
        "operation": operation,
        "recorded_at": _iso(recorded_at),
    }
    if query_class is not None:
        row["query_class"] = query_class
    _append(root, row)


def _topic_visits(rows: list[dict]) -> int:
    by_topic: dict[str, list[datetime]] = defaultdict(list)
    for row in rows:
        by_topic[row["topic_id"]].append(_parse(row["recorded_at"]))
    total = 0
    for timestamps in by_topic.values():
        ordered = sorted(timestamps)
        last: datetime | None = None
        for ts in ordered:
            if last is None or ts - last > SESSION_GAP:
                total += 1
            last = ts
    return total


def summarize_shadow(root: Path) -> dict:
    all_rows = _events(root)
    rows = [row for row in all_rows if row.get("event") == "retrieval_shadow"]
    failures = [row for row in all_rows if row.get("event") == "shadow_failure"]
    total = len(rows)
    topics = {row["topic_id"] for row in rows}
    visits = _topic_visits(rows)

    operations = Counter(row["operation"] for row in rows)
    failure_operations = Counter(row["operation"] for row in failures)
    classes = Counter(row.get("query_class") or "unknown" for row in rows)
    ordered_diff = sum(not bool(row["ordered_same"]) for row in rows)
    top1_diff = sum(not bool(row["top1_same"]) for row in rows)
    candidate_add = sum(int(row["candidate_only_count"] > 0) for row in rows)
    default_only = sum(int(row["default_only_count"] > 0) for row in rows)
    overlap_total = sum(int(row["overlap_count"]) for row in rows)
    overlap_denom = sum(max(int(row["default_count"]), int(row["candidate_count"]), 1) for row in rows)
    default_chars = sum(int(row["default_context_chars"]) for row in rows)
    candidate_chars = sum(int(row["candidate_context_chars"]) for row in rows)

    by_class: dict[str, dict] = {}
    for cls in (*QUERY_CLASSES, "unknown"):
        subset = [row for row in rows if (row.get("query_class") or "unknown") == cls]
        count = len(subset)
        by_class[cls] = {
            "events": count,
            "ordered_divergent": sum(not bool(row["ordered_same"]) for row in subset),
            "top1_divergent": sum(not bool(row["top1_same"]) for row in subset),
            "candidate_addition_events": sum(int(row["candidate_only_count"] > 0) for row in subset),
        }

    ready = total >= 50 and len(topics) >= 10 and visits >= 30
    return {
        "format": "E015-SANITIZED-AGGREGATE-v0",
        "privacy": "aggregate_only_no_ids_queries_paths_sources_text_timestamps_errors",
        "shadow_query_events": total,
        "shadow_failures": {
            "total": len(failures),
            "operations": {key: failure_operations.get(key, 0) for key in ("search", "context", "ask")},
        },
        "topics_with_shadow_activity": len(topics),
        "shadow_topic_visits": visits,
        "operations": {key: operations.get(key, 0) for key in ("search", "context", "ask")},
        "query_classes": {key: classes.get(key, 0) for key in (*QUERY_CLASSES, "unknown")},
        "ordered_divergence": {
            "events": ordered_diff,
            "rate": ordered_diff / total if total else None,
        },
        "top1_divergence": {
            "events": top1_diff,
            "rate": top1_diff / total if total else None,
        },
        "candidate_addition": {
            "events": candidate_add,
            "rate": candidate_add / total if total else None,
        },
        "default_only": {
            "events": default_only,
            "rate": default_only / total if total else None,
        },
        "topk_overlap_fraction": overlap_total / overlap_denom if overlap_denom else None,
        "context_chars": {
            "default_total": default_chars,
            "candidate_total": candidate_chars,
            "candidate_to_default_ratio": (
                candidate_chars / default_chars if default_chars else (1.0 if candidate_chars == 0 and total else None)
            ),
        },
        "by_query_class": by_class,
        "sample_minima": {"events": 50, "topics": 10, "visits": 30},
        "status": "SHADOW_CALIBRATION_READY" if ready else "INSUFFICIENT_SHADOW_DATA",
        "interpretation": "descriptive_disagreement_only_not_quality_or_default_promotion",
    }


def sanitized_shadow_json(root: Path) -> str:
    return json.dumps(summarize_shadow(root), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
