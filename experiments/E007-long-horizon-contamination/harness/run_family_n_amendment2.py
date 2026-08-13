#!/usr/bin/env python3
"""Run E007 Family N with protocol amendments A1+A2.

A1: batch-level answer-ID mismatch is recorded, not process-fatal.
A2: malformed individual answer items are isolated and recorded; no semantic repair/retry.
"""

from __future__ import annotations

from typing import Any

import run_e007
import score_deterministic
from answer_contract_a2 import parse_answer_batch_a2, parse_answer_batch_valid_only


def answer_queries_a2(
    *,
    run_dir,
    call_name: str,
    evidence: str,
    queries: list[dict[str, Any]],
    model: str,
):
    prompt = run_e007.render_template(
        "answer-batch.md",
        EVIDENCE=evidence,
        QUESTIONS=run_e007.render_questions(queries),
    )
    raw = run_e007.make_call(
        run_dir=run_dir,
        call_name=call_name,
        prompt=prompt,
        model=model,
    )
    parsed, item_violations = parse_answer_batch_a2(raw)
    expected_set = {q["query_id"] for q in queries}
    actual_set = set(parsed)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)

    if item_violations or missing or extra:
        run_e007.write_json(
            run_dir / "contract-violations" / f"{call_name}.json",
            {
                "type": "answer_contract_violation",
                "call_name": call_name,
                "item_violations": item_violations,
                "expected_ids": sorted(expected_set),
                "valid_actual_ids": sorted(actual_set),
                "missing_ids": missing,
                "extra_ids": extra,
                "policy": {
                    "retry": False,
                    "infer_missing_query_ids": False,
                    "repair_malformed_items": False,
                    "invent_missing_answers": False,
                    "score_extra_answers": False,
                    "missing_requested_answers_count_as_failures": True,
                },
            },
        )

    return raw, parsed


def self_test() -> None:
    # Scorer compatibility: malformed item disappears; requested missing Q2 becomes failure.
    raw = '''{"answers":[
      {"query_id":"Q002","answer":"The limit is 4 GB and the flag is batch_prefetch.","source_ids":[],"uncertainty":"none"},
      {"answer":"malformed","source_ids":[],"uncertainty":"none"}
    ]}'''
    score_deterministic.parse_answer_batch = parse_answer_batch_valid_only
    result = score_deterministic.score_batch(raw, ["Q002", "Q023"])
    assert result["passed_count"] == 1
    assert result["failed_count"] == 1
    assert result["scores"][1]["failures"] == ["missing answer object"]
    print("A2-RUNNER-SELF-TEST PASS")


def main() -> None:
    # Patch only transport/contract handling. Frozen prompts, conditions, scorer rules,
    # run plan, model, and retry policy remain unchanged.
    run_e007.answer_queries = answer_queries_a2
    run_e007.parse_answer_batch = parse_answer_batch_valid_only
    score_deterministic.parse_answer_batch = parse_answer_batch_valid_only

    import run_family_n

    run_family_n.main()


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
