#!/usr/bin/env python3
"""Run E007 Family N with protocol amendment A1.

A1 changes only one infrastructure behavior discovered after seq=1 completed:
answer-batch query-ID mismatch no longer aborts the whole run. The exact raw model
response remains untouched under calls/<call>/response.txt; missing/extra IDs are
recorded as a contract violation and existing scoring logic treats missing requested
answers as failures.

No retry is performed. No missing answer is invented. No extra answer is scored.
"""

from __future__ import annotations

import json
from typing import Any

import run_e007


def answer_queries_a1(
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
    parsed = run_e007.parse_answer_batch(raw)
    expected = [q["query_id"] for q in queries]
    expected_set = set(expected)
    actual_set = set(parsed)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)

    if missing or extra:
        run_e007.write_json(
            run_dir / "contract-violations" / f"{call_name}.json",
            {
                "type": "answer_id_mismatch",
                "call_name": call_name,
                "expected_ids": sorted(expected_set),
                "actual_ids": sorted(actual_set),
                "missing_ids": missing,
                "extra_ids": extra,
                "policy": {
                    "retry": False,
                    "invent_missing_answers": False,
                    "score_extra_answers": False,
                    "missing_requested_answers_count_as_failures": True,
                },
            },
        )

    return raw, parsed


def self_test() -> None:
    """Deterministic policy sanity test; performs no model calls."""
    expected = {"Q1", "Q2", "Q3"}
    actual = {"Q1", "QX"}
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    assert missing == ["Q2", "Q3"]
    assert extra == ["QX"]
    print("A1-SELF-TEST PASS")


def main() -> None:
    # Patch only the module-global function used by the already-frozen run_condition.
    run_e007.answer_queries = answer_queries_a1

    import run_family_n

    run_family_n.main()


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
