#!/usr/bin/env python3
"""E007 semantic evaluator with A4 missing-primary containment.

A4 builds on A3. It never re-runs a missing primary answer. Semantic queries whose
primary answer is absent are excluded from judge prompts and recorded as invalid/incomplete.
Existing evaluator response.txt files are reused by A3's call_or_reuse path.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import evaluate_semantic_amendment3 as a3
from answer_contract_a2 import parse_answer_batch_valid_only


def load_primary_answers_a4(run_dir, queries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_wave: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        by_wave[int(query["ask_after_wave"])].append(query)

    answers: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for wave, wave_queries in sorted(by_wave.items()):
        response_path = run_dir / "calls" / f"W{wave:02d}-primary" / "response.txt"
        if not response_path.exists():
            raise FileNotFoundError(f"missing primary response artifact: {response_path}")
        parsed = parse_answer_batch_valid_only(response_path.read_text(encoding="utf-8"))
        for query in wave_queries:
            qid = query["query_id"]
            if qid in parsed:
                answers[qid] = parsed[qid]
            else:
                missing.append(qid)

    # Exposed only for deterministic audit; A3 aggregation will mark missing semantic IDs
    # invalid because no evaluator row can exist for them.
    audit_path = run_dir / "evaluation" / "primary-answer-missing-a4.json"
    a3.base.write_json(audit_path, {"type": "primary_answer_missing", "query_ids": sorted(missing)})
    return answers


def build_wave_items_a4(*, wave, queries, answers, facts_by_id, sources):
    # Never invent a candidate answer. Only judge queries with an observed valid primary answer.
    present_queries = [query for query in queries if query["query_id"] in answers]
    if not present_queries:
        return []
    return a3.base.build_wave_items(
        wave=wave,
        queries=present_queries,
        answers=answers,
        facts_by_id=facts_by_id,
        sources=sources,
    )


def parse_evaluations_a4(text: str, expected_ids: list[str]):
    # expected_ids is narrowed by main wrapper below to only queries actually sent to the judge.
    return a3.parse_evaluations_a3(text, expected_ids)


def main() -> None:
    # Patch only post-hoc evaluator data plumbing; A3 aggregation and raw-response reuse stay intact.
    a3.base.load_primary_answers = load_primary_answers_a4
    a3.base.build_wave_items = build_wave_items_a4

    original_parser = a3.parse_evaluations_a3

    # A3 main constructs expected IDs from all wave queries. Narrow expectation to judge-present
    # queries by deriving IDs from the serialized prompt is invasive, so instead parse all returned
    # rows and allow missing IDs to flow into A3 invalid/incomplete aggregation. This preserves the
    # primary omission without inventing an evaluator result.
    a3.parse_evaluations_a3 = original_parser
    a3.main()


if __name__ == "__main__":
    main()
