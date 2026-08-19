from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_ID = 32215941344
RESULT = ROOT / "evidence" / f"run-{RUN_ID}" / "result.json"


def required_recall(row: dict, k: int, *, arm: str) -> tuple[int, int, list[str]]:
    if arm == "A":
        ranking = [item["source_id"] for item in row["retrieval_ranking"]]
    else:
        ranking = [item["source_id"] for item in row["rrf_ranking"]]
    selected = set(ranking[:k])
    required = set(row["required_sources"])
    return len(required & selected), len(required), sorted(required - selected)


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    by_arm = {
        arm: {row["question_id"]: row for row in result["arms"][arm]}
        for arm in ("A", "C")
    }
    qids = sorted(by_arm["A"])
    output = {"model_calls": 0, "note": "posthoc retrieval-only counterfactual; no semantic rerun", "rows": []}
    complete = {"A@5": 0, "A@6": 0, "C@5": 0, "C@6": 0}
    for qid in qids:
        row = {"question_id": qid}
        for arm in ("A", "C"):
            for k in (5, 6):
                got, total, missing = required_recall(by_arm[arm][qid], k, arm=arm)
                key = f"{arm}@{k}"
                row[key] = {"recall": got / total, "missing": missing}
                if not missing:
                    complete[key] += 1
        output["rows"].append(row)

    output["complete_question_counts"] = complete
    assert complete == {"A@5": 6, "A@6": 7, "C@5": 6, "C@6": 10}, complete

    # Every source missing from C@5 sits exactly at fused rank 6.
    for qid in ("Q001", "Q002", "Q004", "Q010"):
        row = by_arm["C"][qid]
        ranking = [item["source_id"] for item in row["rrf_ranking"]]
        missing = row["missing_required_sources"]
        assert len(missing) == 1, (qid, missing)
        assert ranking.index(missing[0]) + 1 == 6, (qid, missing[0], ranking.index(missing[0]) + 1)

    print("E023 zero-model selection counterfactual: PASS")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
