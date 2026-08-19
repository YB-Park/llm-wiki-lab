from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
G1 = ROOT / "evidence" / "run-32215941344" / "result.json"
G1B = ROOT / "evidence" / "g1b-run-32217824760" / "result.json"
CLAUSES = ROOT / "support-clauses-hypothesis-v0.json"


def clause_ok(clause: dict, selected: set[str]) -> bool:
    source_ids = set(clause["source_ids"])
    kind = clause["type"]
    if kind == "all_of":
        return source_ids <= selected
    if kind == "any_of":
        return bool(source_ids & selected)
    if kind == "min_count":
        return len(source_ids & selected) >= int(clause["min_count"])
    raise AssertionError(f"unknown_clause_type:{kind}")


def evaluate(qspec: dict, selected_ids: list[str]) -> dict:
    selected = set(selected_ids)
    rows = []
    for clause in qspec["clauses"]:
        rows.append(
            {
                "clause_id": clause["clause_id"],
                "satisfied": clause_ok(clause, selected),
            }
        )
    forbidden = sorted(set(qspec.get("forbidden_conflation_sources", [])) & selected)
    return {
        "support_complete": all(row["satisfied"] for row in rows),
        "clauses": rows,
        "forbidden_sources_present": forbidden,
    }


def main() -> int:
    g1 = json.loads(G1.read_text(encoding="utf-8"))
    g1b = json.loads(G1B.read_text(encoding="utf-8"))
    spec = json.loads(CLAUSES.read_text(encoding="utf-8"))
    assert spec["status"] == "POSTHOC_ZERO_MODEL_HYPOTHESIS_NOT_PRIMARY_GROUND_TRUTH"

    a = {row["question_id"]: row for row in g1["arms"]["A"]}
    c = {row["question_id"]: row for row in g1["arms"]["C"]}
    b = {row["question_id"]: row for row in g1b["targets"]}

    output = {
        "model_calls": 0,
        "status": "POSTHOC_HYPOTHESIS_ANALYSIS_ONLY",
        "A": {},
        "C": {},
        "G1b": {},
    }
    for qid, qspec in spec["questions"].items():
        output["A"][qid] = evaluate(qspec, a[qid]["selected_source_ids"])
        output["C"][qid] = evaluate(qspec, c[qid]["selected_source_ids"])
        if qid in b:
            output["G1b"][qid] = evaluate(qspec, b[qid]["selected_source_ids"])

    output["complete_counts"] = {
        "A": sum(int(row["support_complete"]) for row in output["A"].values()),
        "C": sum(int(row["support_complete"]) for row in output["C"].values()),
        "G1b_targets": sum(int(row["support_complete"]) for row in output["G1b"].values()),
    }

    # The hypothesis should isolate Q001 as the unique support-incomplete G1a case.
    assert output["complete_counts"] == {"A": 9, "C": 9, "G1b_targets": 4}, output["complete_counts"]
    assert output["A"]["Q001"]["support_complete"] is False
    assert output["C"]["Q001"]["support_complete"] is False
    assert output["G1b"]["Q001"]["support_complete"] is True
    assert all(
        output["A"][qid]["support_complete"]
        for qid in output["A"]
        if qid != "Q001"
    )
    assert all(
        output["C"][qid]["support_complete"]
        for qid in output["C"]
        if qid != "Q001"
    )

    # Q008 demonstrates composition omission despite support-complete context.
    assert output["A"]["Q008"]["support_complete"] is True
    assert output["C"]["Q008"]["support_complete"] is True

    print("E023 posthoc support-clause analysis: PASS")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
