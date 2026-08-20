from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
BM25_K1 = 1.5
BM25_B = 0.75
RRF_K = 60
INITIAL_TOP_K = 5
FOLLOWUP_TOP_K = 3
FINAL_TOP_K = 4


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(text)]


def bm25_ranking(anchors: list[dict[str, Any]], query: str) -> list[tuple[str, float]]:
    docs = {row["anchor_id"]: tokenize(row["text"]) for row in anchors}
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    count = len(docs)
    avgdl = sum(len(tokens) for tokens in docs.values()) / count
    dfs: Counter[str] = Counter()
    for tokens in docs.values():
        dfs.update(set(tokens))
    scored = []
    for anchor_id, tokens in docs.items():
        tf = Counter(tokens)
        dl = len(tokens)
        score = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            df = dfs[term]
            idf = math.log(1 + (count - df + 0.5) / (df + 0.5))
            denom = tf[term] + BM25_K1 * (1 - BM25_B + BM25_B * dl / avgdl)
            score += idf * (tf[term] * (BM25_K1 + 1)) / denom
        if score > 0:
            scored.append((anchor_id, score))
    scored.sort(key=lambda row: (-row[1], row[0]))
    return scored


def rrf_select(
    initial_ranking: list[tuple[str, float]],
    followup_rankings: list[list[tuple[str, float]]],
    candidate_anchor_ids: list[str],
    *,
    rrf_k: int = RRF_K,
    final_top_k: int = FINAL_TOP_K,
) -> tuple[list[str], list[dict[str, Any]]]:
    candidate_set = set(candidate_anchor_ids)
    score: Counter[str] = Counter()
    appearances: Counter[str] = Counter()
    initial_rank = {anchor_id: rank for rank, (anchor_id, _) in enumerate(initial_ranking, start=1)}

    for ranking in [initial_ranking, *followup_rankings]:
        for rank, (anchor_id, _) in enumerate(ranking, start=1):
            if anchor_id not in candidate_set:
                continue
            score[anchor_id] += 1.0 / (rrf_k + rank)
            appearances[anchor_id] += 1

    ordered = sorted(
        candidate_set,
        key=lambda anchor_id: (
            -score[anchor_id],
            initial_rank.get(anchor_id, 10**9),
            anchor_id,
        ),
    )
    trace = [
        {
            "anchor_id": anchor_id,
            "rrf_score": score[anchor_id],
            "retrieval_list_appearances": appearances[anchor_id],
            "initial_rank": initial_rank.get(anchor_id),
        }
        for anchor_id in ordered
    ]
    return ordered[:final_top_k], trace


def evaluate_context(
    question_id: str,
    selected_anchor_ids: list[str],
    contract: dict[str, Any],
    anchor_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    question = contract["questions"][question_id]
    selected = set(selected_anchor_ids)
    missing_clause_ids: list[str] = []
    clauses = []

    for clause in question["clauses"]:
        allowed_types = set(clause["terminal_authority_types"])
        eligible = {
            anchor_id
            for anchor_id in clause["anchor_ids"]
            if anchor_map[anchor_id]["authority_type"] in allowed_types
        }
        if clause["type"] == "all_of":
            satisfied = eligible <= selected
        elif clause["type"] == "any_of":
            satisfied = bool(eligible & selected)
        elif clause["type"] == "min_count":
            satisfied = len(eligible & selected) >= int(clause["min_count"])
        else:
            raise AssertionError(f"unknown_clause_type:{clause['type']}")
        clauses.append({"clause_id": clause["clause_id"], "satisfied": satisfied})
        if not satisfied:
            missing_clause_ids.append(clause["clause_id"])

    forbidden = sorted(set(question["forbidden_conflation_anchor_ids"]) & selected)
    if missing_clause_ids:
        status = "INSUFFICIENT_AUTHORITY"
    elif forbidden:
        status = "SUFFICIENT_WITH_CONFLATION_RISK"
    else:
        status = "SUFFICIENT_CLEAN"

    return {
        "status": status,
        "clauses": clauses,
        "missing_clause_ids": missing_clause_ids,
        "forbidden_conflation_anchor_ids_present": forbidden,
    }
