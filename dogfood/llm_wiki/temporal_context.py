from __future__ import annotations

from pathlib import Path

from .temporal import temporal_source_status


def evidence_temporal_metadata(root: Path, topic_id: str | None, source_ids: tuple[str, ...]) -> list[str]:
    """Return context-header metadata only for explicit temporal/epistemic state.

    Absence of a dispute assertion is *not* rendered as agreement. This helper
    runs after retrieval and therefore cannot affect BM25 scoring or ranking.
    """
    if topic_id is None or not source_ids:
        return []

    statuses = [temporal_source_status(root, source_id, topic_id=topic_id) for source_id in source_ids]
    memberships = {status["status"] for status in statuses}
    if memberships == {"current"}:
        membership = "current"
    elif memberships == {"superseded"}:
        membership = "historical"
    else:
        membership = "mixed"

    lines = [f"temporal_membership: {membership}"]
    contested = sorted(status["source_id"] for status in statuses if status["contested"])
    if contested:
        peers = sorted({peer for status in statuses for peer in status["disputes_with"]})
        lines.extend(
            [
                "epistemic_status: contested",
                f"contested_source_ids: {', '.join(contested)}",
                f"disputes_with: {', '.join(peers)}",
            ]
        )
    return lines
