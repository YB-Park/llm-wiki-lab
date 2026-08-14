from __future__ import annotations

import json
import statistics
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

SESSION_GAP = timedelta(minutes=30)
QUERY_CLASSES = ("exact_provenance", "synthesis", "decision_history", "other")
EVENTS_FILE = "workload-events.jsonl"
TOPICS_FILE = "topics.json"
FORMAT = "llm-wiki-e013-calibration-v0"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    dt = value or _now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _parse(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _registry_path(root: Path) -> Path:
    return root / TOPICS_FILE


def _events_path(root: Path) -> Path:
    return root / EVENTS_FILE


def _load_registry(root: Path) -> dict:
    path = _registry_path(root)
    if not path.exists():
        return {"format": FORMAT, "topics": []}
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("format") != FORMAT or not isinstance(obj.get("topics"), list):
        raise RuntimeError("calibration_topic_registry_format_mismatch")
    return obj


def _save_registry(root: Path, obj: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _registry_path(root).write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def create_topic(root: Path, label: str) -> dict:
    label = label.strip()
    if not label:
        raise ValueError("topic_label_empty")
    obj = _load_registry(root)
    for row in obj["topics"]:
        if row["label"] == label:
            return row
    row = {"topic_id": f"topic-{uuid.uuid4().hex[:12]}", "label": label, "created_at": _iso()}
    obj["topics"].append(row)
    obj["topics"].sort(key=lambda x: x["topic_id"])
    _save_registry(root, obj)
    return row


def topics(root: Path) -> list[dict]:
    return list(_load_registry(root)["topics"])


def resolve_topic(root: Path, value: str) -> dict:
    matches = [row for row in topics(root) if row["topic_id"] == value or row["label"] == value]
    if not matches:
        raise ValueError(f"unknown_topic:{value}")
    if len(matches) != 1:
        raise RuntimeError(f"ambiguous_topic:{value}")
    return matches[0]


def _append(root: Path, event: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with _events_path(root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")


def events(root: Path) -> list[dict]:
    path = _events_path(root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _has_cycle(root: Path, topic_id: str) -> bool:
    return any(e.get("event") == "cycle_start" and e.get("topic_id") == topic_id for e in events(root))


def record_ingest(
    root: Path,
    topic_id: str,
    *,
    authoritative_update: bool = False,
    recorded_at: datetime | None = None,
) -> str:
    if not _has_cycle(root, topic_id):
        kind = "baseline"
        _append(root, {"event": "cycle_start", "kind": kind, "topic_id": topic_id, "recorded_at": _iso(recorded_at)})
        return kind
    if authoritative_update:
        kind = "authoritative_update"
        _append(root, {"event": "cycle_start", "kind": kind, "topic_id": topic_id, "recorded_at": _iso(recorded_at)})
        return kind
    _append(root, {"event": "evidence_ingest", "topic_id": topic_id, "recorded_at": _iso(recorded_at)})
    return "evidence_ingest"


def record_query(
    root: Path,
    topic_id: str,
    operation: str,
    query_class: str | None = None,
    *,
    recorded_at: datetime | None = None,
) -> None:
    if operation not in {"search", "context", "ask"}:
        raise ValueError(f"unsupported_query_operation:{operation}")
    if query_class is not None and query_class not in QUERY_CLASSES:
        raise ValueError(f"unsupported_query_class:{query_class}")
    row = {"event": "query", "topic_id": topic_id, "operation": operation, "recorded_at": _iso(recorded_at)}
    if query_class is not None:
        row["query_class"] = query_class
    _append(root, row)


def record_source_open(root: Path, topic_id: str, *, recorded_at: datetime | None = None) -> None:
    _append(root, {"event": "source_open", "topic_id": topic_id, "recorded_at": _iso(recorded_at)})


def record_feedback(
    root: Path,
    topic_id: str,
    outcome: str,
    reason: str | None = None,
    *,
    recorded_at: datetime | None = None,
) -> None:
    if outcome not in {"helpful", "not_helpful"}:
        raise ValueError(f"unsupported_feedback:{outcome}")
    allowed_reasons = {"correct", "found_source", "missing_source", "wrong", "incomplete", "other"}
    if reason is not None and reason not in allowed_reasons:
        raise ValueError(f"unsupported_feedback_reason:{reason}")
    row = {"event": "feedback", "topic_id": topic_id, "outcome": outcome, "recorded_at": _iso(recorded_at)}
    if reason:
        row["reason"] = reason
    _append(root, row)


def _percentile(values: list[int], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def _visits_for_queries(query_events: list[dict]) -> list[dict]:
    rows = sorted(query_events, key=lambda e: _parse(e["recorded_at"]))
    visits: list[dict] = []
    for event in rows:
        ts = _parse(event["recorded_at"])
        if not visits or ts - visits[-1]["last_query"] > SESSION_GAP:
            visits.append({"start": ts, "last_query": ts, "queries": [event], "followed": False})
        else:
            visits[-1]["last_query"] = ts
            visits[-1]["queries"].append(event)
    return visits


def _decorate_follows(visits: list[dict], source_opens: list[dict], cycle_end: datetime | None) -> None:
    opens = sorted((_parse(e["recorded_at"]) for e in source_opens))
    for i, visit in enumerate(visits):
        next_start = visits[i + 1]["start"] if i + 1 < len(visits) else None
        end = visit["last_query"] + SESSION_GAP
        if next_start is not None:
            end = min(end, next_start)
        if cycle_end is not None:
            end = min(end, cycle_end)
        visit["followed"] = any(visit["start"] <= ts <= end for ts in opens)


def summarize(root: Path) -> dict:
    rows = events(root)
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        tid = row.get("topic_id")
        if isinstance(tid, str):
            by_topic[tid].append(row)

    completed_cycle_visit_counts: list[int] = []
    active_cycles = 0
    completed_cycles = 0
    topic_completed_cycle_counts: Counter[str] = Counter()
    topic_visit_counts: Counter[str] = Counter()
    all_visits: list[dict] = []
    query_counts: Counter[str] = Counter()
    follow_by_class: Counter[str] = Counter()
    visit_class_denoms: Counter[str] = Counter()

    topics_with_queries = 0
    for tid, topic_rows in by_topic.items():
        cycles = sorted(
            [e for e in topic_rows if e.get("event") == "cycle_start"],
            key=lambda e: _parse(e["recorded_at"]),
        )
        queries = [e for e in topic_rows if e.get("event") == "query"]
        opens = [e for e in topic_rows if e.get("event") == "source_open"]
        if queries:
            topics_with_queries += 1
        for q in queries:
            query_counts[q.get("query_class") or "unknown"] += 1

        if not cycles:
            continue
        active_cycles += 1
        for i, cycle in enumerate(cycles):
            start = _parse(cycle["recorded_at"])
            end = _parse(cycles[i + 1]["recorded_at"]) if i + 1 < len(cycles) else None
            cycle_queries = [
                q for q in queries
                if _parse(q["recorded_at"]) >= start and (end is None or _parse(q["recorded_at"]) < end)
            ]
            cycle_opens = [
                e for e in opens
                if _parse(e["recorded_at"]) >= start and (end is None or _parse(e["recorded_at"]) < end)
            ]
            visits = _visits_for_queries(cycle_queries)
            _decorate_follows(visits, cycle_opens, end)
            all_visits.extend(visits)
            topic_visit_counts[tid] += len(visits)
            for visit in visits:
                classes = {q.get("query_class") or "unknown" for q in visit["queries"]}
                if len(classes) == 1:
                    cls = next(iter(classes))
                    visit_class_denoms[cls] += 1
                    if visit["followed"]:
                        follow_by_class[cls] += 1
            if end is not None:
                completed_cycles += 1
                topic_completed_cycle_counts[tid] += 1
                completed_cycle_visit_counts.append(len(visits))

    feedback = Counter(
        e.get("outcome") for e in rows if e.get("event") == "feedback" and e.get("outcome") in {"helpful", "not_helpful"}
    )
    total_queries = sum(query_counts.values())
    total_visits = len(all_visits)
    followed_visits = sum(int(v["followed"]) for v in all_visits)

    def frac_ge(n: int) -> float | None:
        if not completed_cycle_visit_counts:
            return None
        return sum(v >= n for v in completed_cycle_visit_counts) / len(completed_cycle_visit_counts)

    max_cycle_share = (
        max(topic_completed_cycle_counts.values()) / completed_cycles
        if completed_cycles and topic_completed_cycle_counts else None
    )
    max_visit_share = (
        max(topic_visit_counts.values()) / total_visits
        if total_visits and topic_visit_counts else None
    )

    sufficient = topics_with_queries >= 10 and completed_cycles >= 20 and total_visits >= 30
    result = {
        "format": "E013-SANITIZED-AGGREGATE-v0",
        "privacy": "aggregate_only_no_ids_labels_queries_paths_sources_timestamps",
        "session_gap_minutes": 30,
        "topics_with_query_activity": topics_with_queries,
        "topics_with_completed_cycles": len(topic_completed_cycle_counts),
        "completed_cycles": completed_cycles,
        "right_censored_active_cycles": active_cycles,
        "total_visits": total_visits,
        "completed_cycle_revisits": {
            "min": min(completed_cycle_visit_counts) if completed_cycle_visit_counts else None,
            "p25": _percentile(completed_cycle_visit_counts, 0.25),
            "median": statistics.median(completed_cycle_visit_counts) if completed_cycle_visit_counts else None,
            "p75": _percentile(completed_cycle_visit_counts, 0.75),
            "max": max(completed_cycle_visit_counts) if completed_cycle_visit_counts else None,
            "fraction_ge_3": frac_ge(3),
            "fraction_ge_6": frac_ge(6),
            "fraction_ge_10": frac_ge(10),
            "fraction_ge_20": frac_ge(20),
        },
        "query_events": {
            "total": total_queries,
            "counts": {k: query_counts.get(k, 0) for k in (*QUERY_CLASSES, "unknown")},
            "fractions": {
                k: (query_counts.get(k, 0) / total_queries if total_queries else None)
                for k in (*QUERY_CLASSES, "unknown")
            },
        },
        "provenance_follow": {
            "visits_followed": followed_visits,
            "visit_rate": followed_visits / total_visits if total_visits else None,
            "by_unambiguous_visit_class": {
                k: {
                    "visits": visit_class_denoms.get(k, 0),
                    "followed": follow_by_class.get(k, 0),
                    "rate": (
                        follow_by_class.get(k, 0) / visit_class_denoms[k]
                        if visit_class_denoms.get(k, 0) else None
                    ),
                }
                for k in (*QUERY_CLASSES, "unknown")
            },
        },
        "feedback": {
            "helpful": feedback.get("helpful", 0),
            "not_helpful": feedback.get("not_helpful", 0),
        },
        "concentration": {
            "max_topic_completed_cycle_share": max_cycle_share,
            "max_topic_visit_share": max_visit_share,
        },
        "sample_minima": {"topics": 10, "completed_cycles": 20, "visits": 30},
        "status": "CALIBRATION_READY" if sufficient else "INSUFFICIENT_CALIBRATION_DATA",
    }
    return result


def sanitized_json(root: Path) -> str:
    return json.dumps(summarize(root), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
