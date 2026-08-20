from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

from g1d_common import INITIAL_TOP_K, bm25_ranking, evaluate_context

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V1 = ROOT / "authority-sufficiency-v1"
V0 = ROOT / "authority-sufficiency-v0"
PREREG = ROOT / "g1d-preregistration-v0.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def status_counts(statuses: list[str]) -> dict[str, int]:
    counts = Counter(statuses)
    return {
        "SUFFICIENT_CLEAN": counts["SUFFICIENT_CLEAN"],
        "SUFFICIENT_WITH_CONFLATION_RISK": counts["SUFFICIENT_WITH_CONFLATION_RISK"],
        "INSUFFICIENT_AUTHORITY": counts["INSUFFICIENT_AUTHORITY"],
    }


def main() -> int:
    anchors = load_jsonl(V1 / "anchors.jsonl")
    questions_doc = load_json(V1 / "questions.json")
    contract = load_json(V1 / "contract.json")
    references = load_json(V1 / "reference-contexts.json")["contexts"]
    manifest = load_json(V1 / "manifest.json")
    prereg = PREREG.read_text(encoding="utf-8")

    anchor_map = {row["anchor_id"]: row for row in anchors}
    questions = questions_doc["questions"]
    question_map = {row["question_id"]: row for row in questions}

    assert len(anchors) == 23
    assert len(anchor_map) == 23
    assert sorted(anchor_map) == [f"B{i:03d}" for i in range(1, 24)]
    assert len(questions) == 8
    assert sorted(question_map) == [f"BQ{i:03d}" for i in range(1, 9)]
    assert set(contract["questions"]) == set(question_map)
    assert manifest["anchor_count"] == 23
    assert manifest["question_count"] == 8
    assert manifest["authority_type_counts"] == {"RAW_MEMORY": 21, "HUMAN_KNOWLEDGE": 2}
    assert Counter(row["authority_type"] for row in anchors) == Counter(manifest["authority_type_counts"])
    assert {row["anchor_id"] for row in anchors if row["authority_type"] == "HUMAN_KNOWLEDGE"} == {"B007", "B018"}

    # Separation from the previously inspected authority-sufficiency-v0 slice.
    old_anchors = load_jsonl(V0 / "anchors.jsonl")
    old_ids = {row["anchor_id"] for row in old_anchors}
    old_text = {row["text"].strip() for row in old_anchors}
    assert not (old_ids & set(anchor_map))
    assert not (old_text & {row["text"].strip() for row in anchors})

    # Contract references must resolve to correctly typed terminal authority.
    for question_id, spec in contract["questions"].items():
        assert question_id in question_map
        for clause in spec["clauses"]:
            assert clause["type"] in {"all_of", "any_of", "min_count"}
            assert clause["anchor_ids"]
            assert set(clause["terminal_authority_types"]) <= {"RAW_MEMORY", "HUMAN_KNOWLEDGE"}
            for anchor_id in clause["anchor_ids"]:
                assert anchor_id in anchor_map
                assert anchor_map[anchor_id]["authority_type"] in clause["terminal_authority_types"]
        for anchor_id in spec["corroborating_optional_anchor_ids"] + spec["forbidden_conflation_anchor_ids"]:
            assert anchor_id in anchor_map

    # Reference contexts verify all three evaluator states without a model call.
    observed_reference_statuses = Counter()
    for row in references:
        actual = evaluate_context(row["question_id"], row["selected_anchor_ids"], contract, anchor_map)
        assert actual["status"] == row["expected_status"], (row, actual)
        observed_reference_statuses[actual["status"]] += 1
    assert set(observed_reference_statuses) == {
        "SUFFICIENT_CLEAN",
        "SUFFICIENT_WITH_CONFLATION_RISK",
        "INSUFFICIENT_AUTHORITY",
    }

    # Optional corroboration must not secretly be required for a minimal clean context.
    for question_id, spec in contract["questions"].items():
        relevant = sorted({a for c in spec["clauses"] for a in c["anchor_ids"]})
        clean_subsets = []
        for size in range(1, len(relevant) + 1):
            for subset in itertools.combinations(relevant, size):
                if evaluate_context(question_id, list(subset), contract, anchor_map)["status"] == "SUFFICIENT_CLEAN":
                    clean_subsets.append(set(subset))
            if clean_subsets:
                break
        assert clean_subsets, question_id
        for optional in spec["corroborating_optional_anchor_ids"]:
            assert any(optional not in subset for subset in clean_subsets), (question_id, optional, clean_subsets)

    # Prospective exact-query baseline diagnostic. It is intentionally computed before semantic answers.
    baseline_rows = []
    for question in questions:
        ranking = bm25_ranking(anchors, question["question"])
        selected = [anchor_id for anchor_id, _ in ranking[:INITIAL_TOP_K]]
        authority = evaluate_context(question["question_id"], selected, contract, anchor_map)
        baseline_rows.append(
            {
                "question_id": question["question_id"],
                "selected_anchor_ids": selected,
                "authority_status": authority["status"],
                "missing_clause_ids": authority["missing_clause_ids"],
                "forbidden_conflation_anchor_ids_present": authority["forbidden_conflation_anchor_ids_present"],
            }
        )

    baseline_counts = status_counts([row["authority_status"] for row in baseline_rows])
    # The slice must have real selection headroom before any paid call is allowed.
    assert baseline_counts["INSUFFICIENT_AUTHORITY"] >= 1, baseline_rows
    assert baseline_counts["SUFFICIENT_CLEAN"] < 8, baseline_rows

    # Freeze the intended causal comparison and call budget in prose.
    for phrase in [
        "Arm A — strong simple baseline",
        "Arm D — evidence-follow + deterministic selection",
        "Reciprocal Rank Fusion with **k=60**",
        "choose exactly the top **4** anchors",
        "D model selector: **0** calls",
        "total semantic call attempts: **24**",
        "rerolls: **0**",
        "at least **7/8** questions",
        "at least **2/8** questions",
        "regresses authority status versus A on **0/8** questions",
    ]:
        assert phrase in prereg, phrase

    # This PR is preregistration only. Execution assets are forbidden until a later addendum PR.
    assert not (ROOT / "run_g1d.py").exists()
    assert not (REPO / "remote-lab" / "e023-g1d-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g1d.yml").exists()

    # No model answers or semantic adjudication may be hidden in the prospective material.
    forbidden_keys = {"answer", "composer", "semantic_verdict", "adjudication", "gold_answer"}
    for path in [V1 / "questions.json", V1 / "contract.json", V1 / "reference-contexts.json", V1 / "manifest.json"]:
        text = path.read_text(encoding="utf-8")
        for key in forbidden_keys:
            assert f'"{key}"' not in text, (path, key)

    output = {
        "model_calls": 0,
        "anchor_count": len(anchors),
        "question_count": len(questions),
        "authority_type_counts": dict(sorted(Counter(row["authority_type"] for row in anchors).items())),
        "reference_status_counts": dict(sorted(observed_reference_statuses.items())),
        "baseline_exact_bm25_top5_counts": baseline_counts,
        "baseline_exact_bm25_top5_rows": baseline_rows,
        "g1d_rrf_k": 60,
        "g1d_final_top_k": 4,
        "planned_semantic_calls": 24,
        "model_selector_calls": 0,
        "semantic_calls_authorized_on_this_pr": False,
        "promotion_authorized_on_this_pr": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1d prereg validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
