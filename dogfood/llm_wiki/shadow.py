from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .retrieval import (
    RETRIEVAL_STRUCTURAL_EXPAND_V1,
    RETRIEVAL_WHOLE_OBJECT_V0,
    search,
)


@dataclass(frozen=True)
class RetrievalShadowObservation:
    """Non-identifying W0/X1 comparison features for realistic calibration.

    Raw query text and evidence identities are deliberately absent. Object IDs
    exist only transiently inside `compare_retrieval_modes` and are immediately
    reduced to counts/booleans.
    """

    default_count: int
    candidate_count: int
    top1_same: bool
    ordered_same: bool
    overlap_count: int
    default_only_count: int
    candidate_only_count: int
    default_context_chars: int
    candidate_context_chars: int

    def as_telemetry_fields(self) -> dict[str, int | bool]:
        return {
            "default_count": self.default_count,
            "candidate_count": self.candidate_count,
            "top1_same": self.top1_same,
            "ordered_same": self.ordered_same,
            "overlap_count": self.overlap_count,
            "default_only_count": self.default_only_count,
            "candidate_only_count": self.candidate_only_count,
            "default_context_chars": self.default_context_chars,
            "candidate_context_chars": self.candidate_context_chars,
        }


def compare_retrieval_modes(
    root: Path,
    query: str,
    *,
    topic_id: str,
    top_k: int = 8,
    snippet_chars: int = 320,
    include_superseded: bool = False,
) -> RetrievalShadowObservation:
    """Run W0 and X1 locally and return only identity-free comparison features."""

    default = search(
        root,
        query,
        top_k=top_k,
        snippet_chars=snippet_chars,
        topic_id=topic_id,
        include_superseded=include_superseded,
        mode=RETRIEVAL_WHOLE_OBJECT_V0,
    )
    candidate = search(
        root,
        query,
        top_k=top_k,
        snippet_chars=snippet_chars,
        topic_id=topic_id,
        include_superseded=include_superseded,
        mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
    )

    default_ids = [hit.object_id for hit in default]
    candidate_ids = [hit.object_id for hit in candidate]
    default_set = set(default_ids)
    candidate_set = set(candidate_ids)

    if default_ids and candidate_ids:
        top1_same = default_ids[0] == candidate_ids[0]
    else:
        top1_same = not default_ids and not candidate_ids

    return RetrievalShadowObservation(
        default_count=len(default_ids),
        candidate_count=len(candidate_ids),
        top1_same=top1_same,
        ordered_same=default_ids == candidate_ids,
        overlap_count=len(default_set & candidate_set),
        default_only_count=len(default_set - candidate_set),
        candidate_only_count=len(candidate_set - default_set),
        default_context_chars=sum(len(hit.snippet) for hit in default),
        candidate_context_chars=sum(len(hit.snippet) for hit in candidate),
    )
