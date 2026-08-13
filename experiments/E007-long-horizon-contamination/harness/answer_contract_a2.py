#!/usr/bin/env python3
"""Protocol amendment A2: isolate malformed answer items without semantic repair.

A2 was introduced after the frozen E007 Family N block had started and a model response
contained an `answers[]` item with an empty/missing query_id. The original strict parser
aborted the whole run. A1 had already established that batch-level ID mismatch is a
measurable reliability failure rather than an infrastructure exception.

A2 generalizes that boundary one level lower: each answer item is validated independently.
Valid items are preserved exactly. Invalid items are skipped and reported as contract
violations. No retry, query-ID inference, answer repair, or synthetic replacement occurs.
Any expected query that consequently has no valid answer remains missing and is scored as
a failure by the pre-existing deterministic scorer.
"""

from __future__ import annotations

from typing import Any

from score_deterministic import extract_json_object


def parse_answer_batch_a2(text: str) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    payload = extract_json_object(text)
    answers = payload.get("answers")
    if not isinstance(answers, list):
        raise ValueError("response must contain an 'answers' array")

    result: dict[str, dict[str, Any]] = {}
    violations: list[dict[str, Any]] = []

    for index, item in enumerate(answers):
        if not isinstance(item, dict):
            violations.append({"index": index, "reason": "answer_item_not_object"})
            continue

        query_id = item.get("query_id")
        if not isinstance(query_id, str) or not query_id.strip():
            violations.append({"index": index, "reason": "missing_or_empty_query_id"})
            continue
        query_id = query_id.strip()

        if query_id in result:
            violations.append({"index": index, "reason": "duplicate_query_id", "query_id": query_id})
            continue

        answer = item.get("answer")
        if not isinstance(answer, str):
            violations.append({"index": index, "reason": "answer_not_string", "query_id": query_id})
            continue

        source_ids = item.get("source_ids", [])
        if source_ids is None:
            source_ids = []
        if not isinstance(source_ids, list) or not all(isinstance(v, str) for v in source_ids):
            violations.append({"index": index, "reason": "source_ids_not_string_array", "query_id": query_id})
            continue

        uncertainty = item.get("uncertainty", "none")
        if not isinstance(uncertainty, str):
            violations.append({"index": index, "reason": "uncertainty_not_string", "query_id": query_id})
            continue

        result[query_id] = {
            "query_id": query_id,
            "answer": answer,
            "source_ids": source_ids,
            "uncertainty": uncertainty,
        }

    return result, violations


def parse_answer_batch_valid_only(text: str) -> dict[str, dict[str, Any]]:
    """Compatibility adapter for existing scorer/evaluator call sites."""
    parsed, _violations = parse_answer_batch_a2(text)
    return parsed


def self_test() -> None:
    text = '''{
      "answers": [
        {"query_id":"Q1","answer":"ok","source_ids":[],"uncertainty":"none"},
        {"answer":"missing id","source_ids":[],"uncertainty":"none"},
        {"query_id":"Q1","answer":"duplicate","source_ids":[],"uncertainty":"none"},
        {"query_id":"Q2","answer":"ok2","source_ids":[],"uncertainty":"none"}
      ]
    }'''
    parsed, violations = parse_answer_batch_a2(text)
    assert sorted(parsed) == ["Q1", "Q2"]
    assert [v["reason"] for v in violations] == ["missing_or_empty_query_id", "duplicate_query_id"]
    print("A2-ANSWER-CONTRACT-SELF-TEST PASS")


if __name__ == "__main__":
    self_test()
