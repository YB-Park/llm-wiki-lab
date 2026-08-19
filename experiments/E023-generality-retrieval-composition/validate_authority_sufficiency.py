from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "authority-sufficiency-v0"
ANCHORS = PKG / "anchors.jsonl"
QUESTIONS = PKG / "questions.json"
CONTRACT = PKG / "contract.json"
REFERENCE_CONTEXTS = PKG / "reference-contexts.json"
MANIFEST = PKG / "manifest.json"
ORIGINAL_SOURCES = ROOT / "corpus" / "sources.jsonl"

ALLOWED_AUTHORITY_TYPES = {"RAW_MEMORY", "HUMAN_KNOWLEDGE"}
ALLOWED_CLAUSE_TYPES = {"all_of", "any_of", "min_count"}
ALLOWED_CONTEXT_STATUSES = {
    "INSUFFICIENT_AUTHORITY",
    "SUFFICIENT_CLEAN",
    "SUFFICIENT_WITH_CONFLATION_RISK",
}
REQUIRED_SEMANTIC_ROLES = {
    "identity_bridge",
    "repeated_support",
    "direct_attribution",
    "alternative_support",
    "human_knowledge_decision",
    "negative_evidence",
    "temporal_correction",
}
FORBIDDEN_RESULT_KEYS = {
    "model_answer",
    "model_output",
    "observed_answer",
    "semantic_verdict",
    "semantic_result",
    "adjudication",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def walk_keys(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def clause_satisfied(clause: dict, selected: set[str]) -> bool:
    anchors = set(clause["anchor_ids"])
    kind = clause["type"]
    if kind == "all_of":
        return anchors <= selected
    if kind == "any_of":
        return bool(anchors & selected)
    if kind == "min_count":
        return len(anchors & selected) >= int(clause["min_count"])
    raise AssertionError(f"unknown_clause_type:{kind}")


def evaluate_context(question_contract: dict, selected_ids: list[str]) -> dict:
    selected = set(selected_ids)
    clause_rows = []
    for clause in question_contract["clauses"]:
        clause_rows.append(
            {
                "clause_id": clause["clause_id"],
                "satisfied": clause_satisfied(clause, selected),
            }
        )
    missing = [
        row["clause_id"]
        for row in clause_rows
        if not row["satisfied"]
    ]
    forbidden = sorted(
        set(question_contract.get("forbidden_conflation_anchor_ids", []))
        & selected
    )
    if missing:
        status = "INSUFFICIENT_AUTHORITY"
    elif forbidden:
        status = "SUFFICIENT_WITH_CONFLATION_RISK"
    else:
        status = "SUFFICIENT_CLEAN"
    return {
        "status": status,
        "missing_clause_ids": missing,
        "forbidden_conflation_anchor_ids_present": forbidden,
        "clauses": clause_rows,
    }


def positive_anchor_universe(question_contract: dict) -> list[str]:
    return sorted(
        {
            anchor_id
            for clause in question_contract["clauses"]
            for anchor_id in clause["anchor_ids"]
        }
    )


def minimal_sufficient_sets(question_contract: dict) -> list[list[str]]:
    universe = positive_anchor_universe(question_contract)
    sufficient: list[set[str]] = []
    for size in range(len(universe) + 1):
        for combo in itertools.combinations(universe, size):
            selected = set(combo)
            if all(
                clause_satisfied(clause, selected)
                for clause in question_contract["clauses"]
            ):
                sufficient.append(selected)

    minimal: list[set[str]] = []
    for candidate in sufficient:
        if not any(other < candidate for other in sufficient):
            minimal.append(candidate)
    return [sorted(row) for row in minimal]


def main() -> int:
    anchors = load_jsonl(ANCHORS)
    questions_doc = load_json(QUESTIONS)
    contract = load_json(CONTRACT)
    reference = load_json(REFERENCE_CONTEXTS)
    manifest = load_json(MANIFEST)
    original_sources = load_jsonl(ORIGINAL_SOURCES)

    assert contract["status"] == "PROSPECTIVE_ZERO_MODEL_EVALUATION_CONTRACT"
    assert questions_doc["status"] == "SEPARATED_PROSPECTIVE_MATERIAL_NO_MODEL_ANSWERS"
    assert manifest["status"] == "PROSPECTIVE_ZERO_MODEL_EVALUATION_MATERIAL"
    assert set(contract["terminal_authority_types"]) == ALLOWED_AUTHORITY_TYPES
    assert set(contract["context_statuses"]) == ALLOWED_CONTEXT_STATUSES

    anchor_by_id = {row["anchor_id"]: row for row in anchors}
    assert len(anchor_by_id) == len(anchors) == manifest["anchor_count"] == 15
    assert set(anchor_by_id) == set(manifest["anchor_text_sha256"])
    assert all(row["authority_type"] in ALLOWED_AUTHORITY_TYPES for row in anchors)
    assert Counter(row["authority_type"] for row in anchors) == Counter(
        manifest["authority_type_counts"]
    )
    assert Counter(row["family"] for row in anchors) == Counter(
        manifest["family_counts"]
    )
    for anchor_id, row in anchor_by_id.items():
        assert manifest["anchor_text_sha256"][anchor_id] == sha256_text(row["text"])

    # This material is separated from the already-observed E023 G1/G1b corpus.
    old_ids = {row["source_id"] for row in original_sources}
    old_text_hashes = {sha256_text(row["text"]) for row in original_sources}
    assert not (set(anchor_by_id) & old_ids)
    assert not (
        {sha256_text(row["text"]) for row in anchors}
        & old_text_hashes
    )

    question_rows = questions_doc["questions"]
    question_by_id = {row["question_id"]: row for row in question_rows}
    assert len(question_by_id) == len(question_rows) == manifest["question_count"] == 6
    assert set(question_by_id) == set(contract["questions"])
    assert set(question_by_id) == set(manifest["question_spec_sha256"])
    for question_id, row in question_by_id.items():
        assert (
            manifest["question_spec_sha256"][question_id]
            == canonical_json_sha256(row)
        )

    assert canonical_json_sha256(contract) == manifest["contract_canonical_sha256"]
    assert (
        canonical_json_sha256(reference)
        == manifest["reference_contexts_canonical_sha256"]
    )

    # No model answers or semantic adjudication may leak into the prospective freeze.
    observed_keys = set(walk_keys(questions_doc)) | set(walk_keys(contract))
    assert not (observed_keys & FORBIDDEN_RESULT_KEYS), observed_keys & FORBIDDEN_RESULT_KEYS

    roles: set[str] = set()
    clause_type_counts: Counter[str] = Counter()
    human_knowledge_load_bearing_questions: set[str] = set()
    minimal_sets: dict[str, list[list[str]]] = {}
    forbidden_questions = 0

    for question_id, qspec in contract["questions"].items():
        clause_ids = [row["clause_id"] for row in qspec["clauses"]]
        assert len(clause_ids) == len(set(clause_ids))
        assert qspec["clauses"]

        positive_ids: set[str] = set()
        for clause in qspec["clauses"]:
            assert clause["type"] in ALLOWED_CLAUSE_TYPES
            clause_type_counts[clause["type"]] += 1
            roles.add(clause["semantic_role"])
            clause_anchor_ids = clause["anchor_ids"]
            assert clause_anchor_ids
            assert set(clause_anchor_ids) <= set(anchor_by_id)
            positive_ids.update(clause_anchor_ids)

            expected_types = set(clause["terminal_authority_types"])
            assert expected_types
            assert expected_types <= ALLOWED_AUTHORITY_TYPES
            actual_types = {
                anchor_by_id[anchor_id]["authority_type"]
                for anchor_id in clause_anchor_ids
            }
            assert actual_types <= expected_types, (
                question_id,
                clause["clause_id"],
                actual_types,
                expected_types,
            )
            if "HUMAN_KNOWLEDGE" in actual_types:
                human_knowledge_load_bearing_questions.add(question_id)

            if clause["type"] == "min_count":
                minimum = int(clause["min_count"])
                assert 1 <= minimum <= len(set(clause_anchor_ids))
            else:
                assert "min_count" not in clause

        forbidden = set(qspec.get("forbidden_conflation_anchor_ids", []))
        optional = set(qspec.get("corroborating_optional_anchor_ids", []))
        assert forbidden <= set(anchor_by_id)
        assert optional <= set(anchor_by_id)
        assert not (forbidden & positive_ids)
        assert not (optional & positive_ids)
        assert not (forbidden & optional)
        if forbidden:
            forbidden_questions += 1

        minimal = minimal_sufficient_sets(qspec)
        assert minimal, question_id
        minimal_sets[question_id] = minimal
        # Optional corroboration must not sneak into a minimal positive support set.
        assert all(not (set(row) & optional) for row in minimal)

    assert REQUIRED_SEMANTIC_ROLES <= roles, REQUIRED_SEMANTIC_ROLES - roles
    assert set(clause_type_counts) == ALLOWED_CLAUSE_TYPES
    assert human_knowledge_load_bearing_questions == {"AQ003"}
    assert forbidden_questions == 2

    # Reference cases verify the evaluator implementation without model calls.
    case_ids: set[str] = set()
    status_counts: Counter[str] = Counter()
    case_kinds_by_question: dict[str, set[str]] = {
        question_id: set()
        for question_id in question_by_id
    }
    for case in reference["cases"]:
        assert case["case_id"] not in case_ids
        case_ids.add(case["case_id"])
        question_id = case["question_id"]
        assert question_id in contract["questions"]
        assert set(case["selected_anchor_ids"]) <= set(anchor_by_id)
        expected = case["expected_status"]
        assert expected in ALLOWED_CONTEXT_STATUSES
        actual = evaluate_context(
            contract["questions"][question_id],
            case["selected_anchor_ids"],
        )
        assert actual["status"] == expected, (case["case_id"], actual, expected)
        status_counts[actual["status"]] += 1
        if expected == "SUFFICIENT_CLEAN":
            case_kinds_by_question[question_id].add("clean")
        elif expected == "INSUFFICIENT_AUTHORITY":
            case_kinds_by_question[question_id].add("insufficient")
        else:
            case_kinds_by_question[question_id].add("risk")

    for question_id in question_by_id:
        assert {"clean", "insufficient"} <= case_kinds_by_question[question_id]
        has_forbidden = bool(
            contract["questions"][question_id].get(
                "forbidden_conflation_anchor_ids", []
            )
        )
        if has_forbidden:
            assert "risk" in case_kinds_by_question[question_id]

    assert status_counts["INSUFFICIENT_AUTHORITY"] >= 6
    assert status_counts["SUFFICIENT_CLEAN"] >= 6
    assert status_counts["SUFFICIENT_WITH_CONFLATION_RISK"] >= 2

    output = {
        "model_calls": 0,
        "anchor_count": len(anchors),
        "question_count": len(question_rows),
        "authority_type_counts": dict(sorted(Counter(
            row["authority_type"] for row in anchors
        ).items())),
        "clause_type_counts": dict(sorted(clause_type_counts.items())),
        "semantic_roles": sorted(roles),
        "human_knowledge_load_bearing_questions": sorted(
            human_knowledge_load_bearing_questions
        ),
        "forbidden_conflation_question_count": forbidden_questions,
        "reference_case_count": len(reference["cases"]),
        "reference_context_status_counts": dict(sorted(status_counts.items())),
        "minimal_sufficient_context_count_by_question": {
            question_id: len(rows)
            for question_id, rows in sorted(minimal_sets.items())
        },
        "separated_from_frozen_g1_text": True,
        "semantic_calls_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }

    print("E023 authority-sufficiency prereg validation: PASS")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
