from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

from g1d_common import bm25_ranking, evaluate_context

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V2 = ROOT / "authority-sufficiency-v2"
V1 = ROOT / "authority-sufficiency-v1"
V0 = ROOT / "authority-sufficiency-v0"
PREREG = ROOT / "g1e-preregistration-v0.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def status_counts(rows: list[dict]) -> dict[str, int]:
    counts = Counter(row["authority_status"] for row in rows)
    return {
        "SUFFICIENT_CLEAN": counts["SUFFICIENT_CLEAN"],
        "SUFFICIENT_WITH_CONFLATION_RISK": counts["SUFFICIENT_WITH_CONFLATION_RISK"],
        "INSUFFICIENT_AUTHORITY": counts["INSUFFICIENT_AUTHORITY"],
    }


def rank_prefix_rows(anchors, questions, contract, anchor_map, k: int) -> list[dict]:
    rows = []
    for question in questions:
        ranking = bm25_ranking(anchors, question["question"])
        selected = [anchor_id for anchor_id, _ in ranking[:k]]
        authority = evaluate_context(question["question_id"], selected, contract, anchor_map)
        rows.append({
            "question_id": question["question_id"],
            "selected_anchor_ids": selected,
            "newest_rank_anchor_id": selected[-1],
            "authority_status": authority["status"],
            "missing_clause_ids": authority["missing_clause_ids"],
            "forbidden_conflation_anchor_ids_present": authority["forbidden_conflation_anchor_ids_present"],
            "selected_evidence_chars": sum(len(anchor_map[anchor_id]["text"]) for anchor_id in selected),
        })
    return rows


def main() -> int:
    anchors = load_jsonl(V2 / "anchors.jsonl")
    questions_doc = load_json(V2 / "questions.json")
    questions = questions_doc["questions"]
    contract = load_json(V2 / "contract.json")
    references = load_json(V2 / "reference-contexts.json")["contexts"]
    manifest = load_json(V2 / "manifest.json")
    prereg = PREREG.read_text(encoding="utf-8")
    anchor_map = {row["anchor_id"]: row for row in anchors}

    assert len(anchors) == 35
    assert len(anchor_map) == 35
    assert sorted(anchor_map) == [f"C{i:03d}" for i in range(1, 36)]
    assert len(questions) == 8
    assert [row["question_id"] for row in questions] == [f"CQ00{i}" for i in range(1, 9)]
    assert set(contract["questions"]) == {row["question_id"] for row in questions}
    assert manifest["anchor_count"] == 35
    assert manifest["question_count"] == 8
    assert manifest["authority_type_counts"] == {"RAW_MEMORY": 32, "HUMAN_KNOWLEDGE": 3}
    assert Counter(row["authority_type"] for row in anchors) == Counter(manifest["authority_type_counts"])
    assert {row["anchor_id"] for row in anchors if row["authority_type"] == "HUMAN_KNOWLEDGE"} == {"C013", "C021", "C034"}

    # v2 must be materially separated from both prior prospective slices.
    old_anchors = load_jsonl(V0 / "anchors.jsonl") + load_jsonl(V1 / "anchors.jsonl")
    old_ids = {row["anchor_id"] for row in old_anchors}
    old_texts = {row["text"].strip() for row in old_anchors}
    assert not (old_ids & set(anchor_map))
    assert not (old_texts & {row["text"].strip() for row in anchors})

    # Every clause must resolve to an explicitly allowed terminal authority type.
    for question_id, spec in contract["questions"].items():
        for clause in spec["clauses"]:
            assert clause["type"] in {"all_of", "any_of", "min_count"}
            assert clause["anchor_ids"]
            assert set(clause["terminal_authority_types"]) <= {"RAW_MEMORY", "HUMAN_KNOWLEDGE"}
            for anchor_id in clause["anchor_ids"]:
                assert anchor_id in anchor_map
                assert anchor_map[anchor_id]["authority_type"] in clause["terminal_authority_types"]
        for anchor_id in spec["corroborating_optional_anchor_ids"] + spec["forbidden_conflation_anchor_ids"]:
            assert anchor_id in anchor_map

    # Reference contexts exercise all evaluator states.
    observed = Counter()
    for row in references:
        actual = evaluate_context(row["question_id"], row["selected_anchor_ids"], contract, anchor_map)
        assert actual["status"] == row["expected_status"], (row, actual)
        observed[actual["status"]] += 1
    assert set(observed) == {"SUFFICIENT_CLEAN", "SUFFICIENT_WITH_CONFLATION_RISK", "INSUFFICIENT_AUTHORITY"}

    # Optional corroboration must not secretly become required.
    for question_id, spec in contract["questions"].items():
        relevant = sorted({anchor_id for clause in spec["clauses"] for anchor_id in clause["anchor_ids"]})
        clean_minima = []
        for size in range(1, len(relevant) + 1):
            for subset in itertools.combinations(relevant, size):
                if evaluate_context(question_id, list(subset), contract, anchor_map)["status"] == "SUFFICIENT_CLEAN":
                    clean_minima.append(set(subset))
            if clean_minima:
                break
        assert clean_minima, question_id
        for optional in spec["corroborating_optional_anchor_ids"]:
            assert any(optional not in subset for subset in clean_minima), (question_id, optional)

    a5 = rank_prefix_rows(anchors, questions, contract, anchor_map, 5)
    b6 = rank_prefix_rows(anchors, questions, contract, anchor_map, 6)
    a_by_q = {row["question_id"]: row for row in a5}
    b_by_q = {row["question_id"]: row for row in b6}

    assert status_counts(a5) == {
        "SUFFICIENT_CLEAN": 2,
        "SUFFICIENT_WITH_CONFLATION_RISK": 4,
        "INSUFFICIENT_AUTHORITY": 2,
    }
    assert status_counts(b6) == {
        "SUFFICIENT_CLEAN": 3,
        "SUFFICIENT_WITH_CONFLATION_RISK": 5,
        "INSUFFICIENT_AUTHORITY": 0,
    }

    order = {"INSUFFICIENT_AUTHORITY": 0, "SUFFICIENT_WITH_CONFLATION_RISK": 1, "SUFFICIENT_CLEAN": 2}
    improvements = sum(order[b_by_q[q]["authority_status"]] > order[a_by_q[q]["authority_status"]] for q in a_by_q)
    regressions = sum(order[b_by_q[q]["authority_status"]] < order[a_by_q[q]["authority_status"]] for q in a_by_q)
    assert improvements == 2
    assert regressions == 0
    assert a_by_q["CQ001"]["authority_status"] == "INSUFFICIENT_AUTHORITY"
    assert b_by_q["CQ001"]["authority_status"] == "SUFFICIENT_WITH_CONFLATION_RISK"
    assert b_by_q["CQ001"]["newest_rank_anchor_id"] == "C003"
    assert a_by_q["CQ008"]["authority_status"] == "INSUFFICIENT_AUTHORITY"
    assert b_by_q["CQ008"]["authority_status"] == "SUFFICIENT_CLEAN"
    assert b_by_q["CQ008"]["newest_rank_anchor_id"] == "C033"

    evidence_size = {}
    for qid in a_by_q:
        a_chars = a_by_q[qid]["selected_evidence_chars"]
        b_chars = b_by_q[qid]["selected_evidence_chars"]
        evidence_size[qid] = {
            "A5_chars": a_chars,
            "B6_chars": b_chars,
            "B6_over_A5": b_chars / a_chars,
            "rank6_anchor_id": b_by_q[qid]["newest_rank_anchor_id"],
        }

    # Freeze the two-phase gate and call budget in prose.
    for phrase in [
        "Phase 0 — zero-model authority gate",
        "0 `INSUFFICIENT_AUTHORITY`",
        "at least **2 / 8** questions",
        "regressions versus A5 on **0 / 8** questions",
        "A5 composer: **8** calls",
        "B6 composer: **8** calls",
        "total semantic attempts: **16**",
        "rerolls: **0**",
        "at least **7 / 8 PASS**",
        "at least **1 semantic improvement**",
        "0 semantic regressions",
        "hard-coded top-6 product policy",
    ]:
        assert phrase in prereg, phrase

    # Prereg only: execution artifacts must not exist yet.
    assert not (ROOT / "run_g1e.py").exists()
    assert not (REPO / "remote-lab" / "e023-g1e-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g1e.yml").exists()

    # Prospective package must contain no model answers/adjudication.
    forbidden_keys = {"answer", "composer", "semantic_verdict", "adjudication", "gold_answer"}
    for path in [V2 / "questions.json", V2 / "contract.json", V2 / "reference-contexts.json", V2 / "manifest.json"]:
        text = path.read_text(encoding="utf-8")
        for key in forbidden_keys:
            assert f'"{key}"' not in text, (path, key)

    phase0_pass = (
        status_counts(b6)["INSUFFICIENT_AUTHORITY"] == 0
        and improvements >= 2
        and regressions == 0
    )
    assert phase0_pass is True

    output = {
        "model_calls": 0,
        "anchor_count": len(anchors),
        "question_count": len(questions),
        "authority_type_counts": dict(sorted(Counter(row["authority_type"] for row in anchors).items())),
        "reference_status_counts": dict(sorted(observed.items())),
        "A5_counts": status_counts(a5),
        "B6_counts": status_counts(b6),
        "B6_authority_improvements": improvements,
        "B6_authority_regressions": regressions,
        "evidence_size": evidence_size,
        "phase0_authority_gate": "PASS",
        "phase1_semantic_execution_prerequisite_satisfied": True,
        "semantic_calls_authorized_on_this_pr": False,
        "planned_semantic_calls_if_separately_executed": 16,
        "planner_calls": 0,
        "selector_calls": 0,
        "top6_product_policy_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1e prereg Phase 0 validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
