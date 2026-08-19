from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_ID = 32215941344
RESULT = ROOT / "evidence" / f"run-{RUN_ID}" / "result.json"
ADJUDICATION = ROOT / "adjudication-v0.json"
CORPUS = ROOT / "corpus"
EXPECTED_QIDS = ["Q001", "Q002", "Q004", "Q010"]
SNIPPET_CHARS = 320
FINAL_SOURCE_LIMIT = 5
MAX_SEMANTIC_CALLS = 12


def load_sources() -> dict[str, dict]:
    rows = {}
    for line in (CORPUS / "sources.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["source_id"]] = row
    return rows


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    sources = load_sources()

    assert result["format"] == "E023-G1-v0"
    assert result["execute_model"] is True
    assert result["model_call_attempts"] == 30

    a = {row["question_id"]: row for row in result["arms"]["A"]}
    c = {row["question_id"]: row for row in result["arms"]["C"]}

    targeted = sorted(
        qid
        for qid in a
        if a[qid]["required_recall_at_5"] < 1.0 and c[qid]["required_recall_at_5"] < 1.0
    )
    assert targeted == EXPECTED_QIDS, targeted

    baseline_verdicts = {
        qid: adjudication["verdicts"]["A"][qid]["verdict"]
        for qid in targeted
    }
    assert baseline_verdicts == {
        "Q001": "CRITICAL_ERROR",
        "Q002": "PASS",
        "Q004": "PASS",
        "Q010": "PASS",
    }, baseline_verdicts

    rows = []
    for qid in targeted:
        initial = a[qid]["selected_source_ids"]
        missing = a[qid]["missing_required_sources"]
        assert len(initial) == FINAL_SOURCE_LIMIT, (qid, initial)
        assert len(missing) == 1, (qid, missing)
        source_chars = {source_id: len(sources[source_id]["text"]) for source_id in initial}
        rows.append(
            {
                "question_id": qid,
                "initial_source_ids": initial,
                "missing_required_source_for_measurement_only": missing[0],
                "forbidden_in_initial_context": a[qid]["forbidden_conflation_sources_in_context"],
                "baseline_semantic_verdict": baseline_verdicts[qid],
                "initial_full_text_chars": sum(source_chars.values()),
                "initial_source_text_chars": source_chars,
                "planner_snippet_chars_per_source": SNIPPET_CHARS,
            }
        )

    output = {
        "experiment": "E023-G1b-prereg",
        "model_calls": 0,
        "target_rule": "A_recall_at_5_lt_1_AND_C_recall_at_5_lt_1",
        "target_question_ids": targeted,
        "final_source_limit": FINAL_SOURCE_LIMIT,
        "max_semantic_calls_if_later_executed": MAX_SEMANTIC_CALLS,
        "rows": rows,
        "authority_boundary": (
            "Gold required/forbidden IDs are evaluator-only and must never be shown to planner, selector, or composer."
        ),
    }
    print("E023 G1b prereg target validation: PASS")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
