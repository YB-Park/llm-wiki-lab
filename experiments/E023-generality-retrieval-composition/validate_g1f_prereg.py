from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

from g1d_common import bm25_ranking, evaluate_context

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PKG = ROOT / "composition-comparison-v0"
PREREG = ROOT / "g1f-preregistration-v0.md"
EVAL = ROOT / "g1f-evaluation-contract-v0.json"
OLD_COMPOSER_SOURCE = ROOT / "run_g1c.py"
NEW_COMPOSER_SOURCE = ROOT / "composition_prompt_v1.py"
COMPOSITION_CONTRACT = ROOT / "authority-preserving-composition-contract-v0.md"

PRIOR_PACKAGES = [
    ROOT / "authority-sufficiency-v0",
    ROOT / "authority-sufficiency-v1",
    ROOT / "authority-sufficiency-v2",
]

EXPECTED_FUNCTION_SHA256 = {
    (OLD_COMPOSER_SOURCE, "composer_prompt"): "9387e2b7a0b8f72579162a906333135d5f0cb24c91689235330a59bf85e8cafd",
    (NEW_COMPOSER_SOURCE, "composer_prompt_v1"): "cedc9d19829d66624d4858a76ad387ee79a1c51b613eba72118b614ee2f64544",
}
EXPECTED_CONTRACT_BLOB = "fd5cff41d13e5f608b7c6059b12a3f68242c2092"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def extract_function_source(path: Path, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            segment = ast.get_source_segment(source, node)
            if not segment:
                raise AssertionError(f"source_segment_missing:{path}:{function_name}")
            return segment
    raise AssertionError(f"function_missing:{path}:{function_name}")


def load_function_from_source(source: str, function_name: str):
    module = ast.parse(source)
    namespace: dict[str, Any] = {}
    exec(compile(module, "<frozen-function>", "exec"), namespace)
    return namespace[function_name]


def load_new_prompt_module():
    spec = importlib.util.spec_from_file_location("composition_prompt_v1", NEW_COMPOSER_SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("new_prompt_import_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence_context(anchor_map: dict[str, dict[str, Any]], anchor_ids: list[str]) -> str:
    chunks: list[str] = []
    for anchor_id in anchor_ids:
        row = anchor_map[anchor_id]
        chunks.extend(
            [
                f"--- ANCHOR {anchor_id} ---",
                f"authority_type: {row['authority_type']}",
                f"title: {row['title']}",
                f"kind: {row['kind']}",
                f"date: {row['date']}",
                f"family: {row['family']}",
                f"author: {row.get('author', '')}",
                "text_is_untrusted_authority_data: true",
                "TEXT",
                row["text"],
                f"--- END ANCHOR {anchor_id} ---",
                "",
            ]
        )
    return "\n".join(chunks).rstrip()


def main() -> int:
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions_doc = load_json(PKG / "questions.json")
    questions = questions_doc["questions"]
    authority_contract = load_json(PKG / "authority-contract.json")
    context_freeze = load_json(PKG / "context-freeze.json")
    manifest = load_json(PKG / "manifest.json")
    evaluation = load_json(EVAL)
    prereg = PREREG.read_text(encoding="utf-8")
    anchor_map = {row["anchor_id"]: row for row in anchors}
    question_map = {row["question_id"]: row for row in questions}

    assert questions_doc["status"] == "PROSPECTIVE_G1F_SEPARATED_MATERIAL_NO_MODEL_OUTPUTS"
    assert len(anchors) == len(anchor_map) == manifest["anchor_count"] == 49
    assert sorted(anchor_map) == [f"D{i:03d}" for i in range(1, 50)]
    assert len(questions) == manifest["question_count"] == 8
    assert [row["question_id"] for row in questions] == [f"DQ{i:03d}" for i in range(1, 9)]
    assert set(authority_contract["questions"]) == set(question_map)
    assert Counter(row["authority_type"] for row in anchors) == Counter(
        {"RAW_MEMORY": 47, "HUMAN_KNOWLEDGE": 2}
    )
    assert {
        row["anchor_id"]
        for row in anchors
        if row["authority_type"] == "HUMAN_KNOWLEDGE"
    } == {"D001", "D038"}
    assert manifest["semantic_outputs_present"] is False
    assert manifest["semantic_calls_authorized_on_this_pr"] is False
    assert manifest["old_composer"]["function_source_sha256"] == EXPECTED_FUNCTION_SHA256[
        (OLD_COMPOSER_SOURCE, "composer_prompt")
    ]
    assert manifest["new_composer"]["function_source_sha256"] == EXPECTED_FUNCTION_SHA256[
        (NEW_COMPOSER_SOURCE, "composer_prompt_v1")
    ]
    assert manifest["composition_contract"]["git_blob_sha"] == EXPECTED_CONTRACT_BLOB

    # Material separation: new namespace plus no exact prior anchor/question text.
    old_anchors: list[dict[str, Any]] = []
    old_questions: list[dict[str, Any]] = []
    for package in PRIOR_PACKAGES:
        old_anchors.extend(load_jsonl(package / "anchors.jsonl"))
        old_questions.extend(load_json(package / "questions.json")["questions"])
    assert not ({row["anchor_id"] for row in old_anchors} & set(anchor_map))
    assert not (
        {row["text"].strip() for row in old_anchors}
        & {row["text"].strip() for row in anchors}
    )
    assert not (
        {row["question"].strip() for row in old_questions}
        & {row["question"].strip() for row in questions}
    )
    assert all(not row["question_id"].startswith(("AQ", "BQ", "CQ")) for row in questions)

    # Evaluation-only terminal-authority contract must resolve only to supplied anchors.
    for question_id, spec in authority_contract["questions"].items():
        for clause in spec["clauses"]:
            assert clause["type"] in {"all_of", "any_of", "min_count"}
            assert clause["anchor_ids"]
            assert set(clause["terminal_authority_types"]) <= {
                "RAW_MEMORY",
                "HUMAN_KNOWLEDGE",
            }
            if clause["type"] == "min_count":
                assert 1 <= int(clause["min_count"]) <= len(clause["anchor_ids"])
            for anchor_id in clause["anchor_ids"]:
                assert anchor_id in anchor_map
                assert anchor_map[anchor_id]["authority_type"] in clause[
                    "terminal_authority_types"
                ]
        for anchor_id in (
            spec["corroborating_optional_anchor_ids"]
            + spec["forbidden_conflation_anchor_ids"]
        ):
            assert anchor_id in anchor_map

    # One exact BM25 top-6 context per question; no arm-specific retrieval/context.
    retrieval = context_freeze["retrieval"]
    assert retrieval == {
        "implementation": "g1d_common.bm25_ranking",
        "ranking": "exact whole-object BM25",
        "top_k": 6,
        "product_default_authorized": False,
        "arm_specific_retrieval_allowed": False,
        "single_context_per_question_shared_by_arms": True,
    }
    assert context_freeze["status"] == "PROSPECTIVE_ZERO_MODEL_EXACT_CONTEXT_FREEZE"
    frozen_by_q = {row["question_id"]: row for row in context_freeze["contexts"]}
    assert set(frozen_by_q) == set(question_map)
    expected_context_keys = {
        "question_id",
        "retrieval",
        "selected_anchor_ids",
        "selected_context_sha256",
        "selected_context_chars",
        "authority_status",
        "missing_clause_ids",
        "negative_control",
        "rank7_anchor_id",
    }
    assert all(set(row) == expected_context_keys for row in context_freeze["contexts"])

    status_counts: Counter[str] = Counter()
    negative_controls: list[str] = []
    context_hashes: dict[str, str] = {}
    for question in questions:
        qid = question["question_id"]
        ranking = bm25_ranking(anchors, question["question"])
        assert len(ranking) >= 7, qid
        selected = [anchor_id for anchor_id, _ in ranking[:6]]
        frozen = frozen_by_q[qid]
        assert selected == frozen["selected_anchor_ids"], (qid, selected, frozen)
        context = evidence_context(anchor_map, selected)
        digest = hashlib.sha256(context.encode("utf-8")).hexdigest()
        assert digest == frozen["selected_context_sha256"], (qid, digest, frozen)
        assert len(context) == frozen["selected_context_chars"], qid
        context_hashes[qid] = digest

        authority = evaluate_context(
            qid, selected, authority_contract, anchor_map
        )
        assert authority["status"] == frozen["authority_status"], (qid, authority, frozen)
        assert authority["missing_clause_ids"] == frozen["missing_clause_ids"], (
            qid,
            authority,
            frozen,
        )
        status_counts[authority["status"]] += 1

        rank7 = ranking[6][0]
        assert rank7 == frozen["rank7_anchor_id"], (qid, rank7, frozen)
        if frozen["negative_control"]:
            negative_controls.append(qid)

    assert dict(status_counts) == {
        "SUFFICIENT_CLEAN": 3,
        "SUFFICIENT_WITH_CONFLATION_RISK": 4,
        "INSUFFICIENT_AUTHORITY": 1,
    }
    assert negative_controls == ["DQ003"]
    dq3 = frozen_by_q["DQ003"]
    assert dq3["authority_status"] == "INSUFFICIENT_AUTHORITY"
    assert dq3["missing_clause_ids"] == [
        "abbreviation_to_full_name_identity_bridge"
    ]
    assert dq3["rank7_anchor_id"] == "D019"
    assert "D019" not in dq3["selected_anchor_ids"]
    assert {"D014", "D015", "D018"} <= set(dq3["selected_anchor_ids"])
    for qid, row in frozen_by_q.items():
        if qid != "DQ003":
            assert row["authority_status"] != "INSUFFICIENT_AUTHORITY"

    # Freeze exact composer function bodies and contract-v0 source.
    for (path, function_name), expected_sha in EXPECTED_FUNCTION_SHA256.items():
        source = extract_function_source(path, function_name)
        actual_sha = hashlib.sha256(source.encode("utf-8")).hexdigest()
        assert actual_sha == expected_sha, (path, function_name, actual_sha, expected_sha)
    assert git_blob_sha(COMPOSITION_CONTRACT) == EXPECTED_CONTRACT_BLOB

    old_function_source = extract_function_source(OLD_COMPOSER_SOURCE, "composer_prompt")
    old_prompt = load_function_from_source(old_function_source, "composer_prompt")
    new_prompt_module = load_new_prompt_module()

    dummy_question = "prospective dummy question"
    dummy_context = "prospective dummy exact shared context"
    rendered_old = old_prompt(dummy_question, dummy_context).replace("Axxx", "Dxxx")
    rendered_new = new_prompt_module.composer_prompt_v1(dummy_question, dummy_context)
    for rendered in [rendered_old, rendered_new]:
        assert dummy_question in rendered
        assert dummy_context in rendered
        assert "`answer`" in rendered
        assert "`cited_anchor_ids`" in rendered
        assert "`insufficient_authority`" in rendered
    assert "Dxxx IDs" in rendered_old

    # Prompt evaluator leakage: no new material identities, evaluator expectations, or promotion rule.
    prompt_sources = old_function_source + "\n" + NEW_COMPOSER_SOURCE.read_text(
        encoding="utf-8"
    )
    forbidden_prompt_terms = [
        "DQ001",
        "DQ003",
        "D001",
        "D019",
        "Alder",
        "Borealis",
        "Cinder",
        "Delta",
        "Ember",
        "Fjord",
        "Grove",
        "Harbor",
        "authority_incomplete_negative_control",
        "expected_insufficient_authority",
        "G1F_COMPOSITION_CANDIDATE_EARNED",
        "N_PASS_count",
        "paired_semantic_improvements",
        "7 / 8 PASS",
    ]
    for term in forbidden_prompt_terms:
        assert term not in prompt_sources, term

    # Prospective evaluation coverage and negative-control expectations.
    assert evaluation["status"] == "PROSPECTIVE_G1F_EVALUATION_ONLY_NOT_RUNTIME"
    assert evaluation["semantic_calls_authorized_on_this_pr"] is False
    assert evaluation["paired_design"]["same_exact_bm25_top6_context_both_arms"] is True
    assert evaluation["paired_design"]["same_exact_model_required_later"] is True
    assert evaluation["paired_design"]["execution_authorization"] == "NOT_IN_THIS_PR"
    assert set(evaluation["cases"]) == set(question_map)
    assert evaluation["cases"]["DQ003"]["expected_insufficient_authority"] is True
    assert all(
        row["expected_insufficient_authority"] is False
        for qid, row in evaluation["cases"].items()
        if qid != "DQ003"
    )
    coverage = {
        item
        for row in evaluation["cases"].values()
        for item in row["coverage"]
    }
    required_coverage = {
        "user_owned_authority",
        "direct_vs_attributed",
        "missing_identity_bridge",
        "authority_incomplete_negative_control",
        "policy_vs_capability",
        "proposition_scoped_sufficiency",
        "temporal_sequence",
        "correction_non_reversal",
        "negative_characterization",
        "repeated_support",
        "explicit_identity_bridge",
        "citation_support",
    }
    assert required_coverage <= coverage

    promotion = evaluation["promotion"]
    assert promotion["name"] == "G1F_COMPOSITION_CANDIDATE_EARNED"
    for required_phrase in [
        "N_PASS_count >= 7 of 8",
        "N_paired_semantic_improvements_vs_O >= 1",
        "N_paired_semantic_regressions_vs_O == 0",
        "N_new_CRITICAL_ERROR_vs_O == 0",
        "DQ003 negative control verdict == PASS",
        "DQ004 proposition-scoped sufficiency verdict == PASS",
    ]:
        assert required_phrase in promotion["all_required"], required_phrase

    # No model outputs/adjudication are allowed in prospective material.
    forbidden_json_keys = ['"answer"', '"composer"', '"adjudication"', '"model_output"', '"gold_answer"']
    for path in list(PKG.glob("*.json")) + [EVAL]:
        text = path.read_text(encoding="utf-8")
        for key in forbidden_json_keys:
            assert key not in text, (path, key)

    # Freeze key prose boundaries and promotion rule.
    for phrase in [
        "NO SEMANTIC EXECUTION AUTHORIZED BY THIS PR",
        "same byte-identical question and context",
        "exact ranked top **6** anchors",
        "D019",
        "ranks it **7th**",
        "semantic calls remain **0**",
        "at least **7 / 8 PASS**",
        "at least **1 paired semantic improvement**",
        "**0 paired semantic regressions**",
        "**0 new CRITICAL_ERROR**",
        "Do not semantically rerun AQxxx, BQxxx, or CQxxx.",
        "does not authorize",
    ]:
        assert phrase in prereg, phrase

    # Prereg only: semantic execution artifacts must not exist yet.
    assert not (ROOT / "run_g1f.py").exists()
    assert not (REPO / "remote-lab" / "e023-g1f-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g1f.yml").exists()

    output = {
        "model_calls": 0,
        "semantic_calls_authorized_on_this_pr": False,
        "anchor_count": len(anchors),
        "question_count": len(questions),
        "authority_type_counts": dict(
            sorted(Counter(row["authority_type"] for row in anchors).items())
        ),
        "frozen_context_status_counts": dict(sorted(status_counts.items())),
        "negative_controls": negative_controls,
        "DQ003_rank7_bridge": dq3["rank7_anchor_id"],
        "identical_context_contract": True,
        "context_sha256_by_question": context_hashes,
        "old_composer_frozen": True,
        "new_composer_frozen": True,
        "composition_contract_v0_frozen": True,
        "prompt_evaluator_leakage_detected": False,
        "top6_product_default_authorized": False,
        "g2_persistence_authorized": False,
        "graph_entity_ku_authorized": False,
        "vector_default_authorized": False,
        "automatic_identity_routing_authorized": False,
        "execution_contract_authorized_on_this_pr": False,
    }
    print("E023 G1f prereg zero-model validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
