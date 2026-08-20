from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
from collections import Counter
from pathlib import Path

from g1d_common import bm25_ranking, evaluate_context

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PKG = ROOT / "persistence-comparison-v0"
PREREG = ROOT / "g2-preregistration-v0.md"
EVAL = ROOT / "g2-evaluation-contract-v0.json"
PROMPT = ROOT / "projection_prompt_v0.py"
CLOSURE = ROOT / "g1-closure-decision-v0.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_prompt_module():
    spec = importlib.util.spec_from_file_location("e023_projection_prompt_v0", PROMPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("projection_prompt_import_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def active_anchors(all_anchors: list[dict], subject_id: str, state: str) -> list[dict]:
    assert state in {"S0", "S1"}
    return sorted(
        [
            row for row in all_anchors
            if row["subject_id"] == subject_id
            and (row["active_from_state"] == "S0" or state == "S1")
        ],
        key=lambda row: row["anchor_id"],
    )


def snapshot_sha(rows: list[dict]) -> str:
    text = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evidence_context(anchor_map: dict[str, dict], anchor_ids: list[str]) -> str:
    chunks = []
    for anchor_id in anchor_ids:
        row = anchor_map[anchor_id]
        chunks.extend([
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
        ])
    return "\n".join(chunks).rstrip()


def main() -> int:
    anchors = load_jsonl(PKG / "anchors.jsonl")
    questions_doc = load_json(PKG / "questions.json")
    questions = questions_doc["questions"]
    contract = load_json(PKG / "authority-contract.json")
    lifecycle = load_json(PKG / "lifecycle.json")
    control_rows = load_json(PKG / "control-contexts.json")["contexts"]
    manifest = load_json(PKG / "manifest.json")
    evaluation = load_json(EVAL)
    prereg = PREREG.read_text(encoding="utf-8")
    closure = CLOSURE.read_text(encoding="utf-8")
    prompt_source = PROMPT.read_text(encoding="utf-8")
    prompt_module = load_prompt_module()
    rendered_prompt = prompt_module.projection_prompt_v0("dummy-subject", "dummy-authority")

    anchor_map = {row["anchor_id"]: row for row in anchors}
    question_map = {row["question_id"]: row for row in questions}
    control_map = {row["question_id"]: row for row in control_rows}

    assert questions_doc["status"] == "PROSPECTIVE_G2_SEPARATED_QUESTIONS"
    assert manifest["status"] == "PROSPECTIVE_G2_SEPARATED_MATERIAL_NO_MODEL_OUTPUTS"
    assert len(anchors) == len(anchor_map) == manifest["anchor_count"] == 36
    assert sorted(anchor_map) == [f"P{i:03d}" for i in range(1, 37)]
    assert len(questions) == len(question_map) == manifest["question_count"] == 12
    assert [row["question_id"] for row in questions] == [f"PQ{i:03d}" for i in range(1, 13)]
    assert set(contract["questions"]) == set(question_map) == set(control_map)
    assert manifest["subject_count"] == 3
    assert Counter(row["subject_id"] for row in anchors) == Counter({"iris": 12, "juniper": 12, "keystone": 12})
    assert Counter(row["authority_type"] for row in anchors) == Counter({"RAW_MEMORY": 32, "HUMAN_KNOWLEDGE": 4})
    assert {row["anchor_id"] for row in anchors if row["authority_type"] == "HUMAN_KNOWLEDGE"} == {"P001", "P013", "P025", "P034"}

    # Separated from all prior G1 prospective corpora.
    prior_dirs = [
        ROOT / "authority-sufficiency-v0",
        ROOT / "authority-sufficiency-v1",
        ROOT / "authority-sufficiency-v2",
        ROOT / "composition-comparison-v0",
    ]
    prior_anchors = []
    prior_questions = []
    for prior in prior_dirs:
        prior_anchors.extend(load_jsonl(prior / "anchors.jsonl"))
        prior_questions.extend(load_json(prior / "questions.json")["questions"])
    assert not ({row["anchor_id"] for row in prior_anchors} & set(anchor_map))
    assert not ({row["text"].strip() for row in prior_anchors} & {row["text"].strip() for row in anchors})
    assert not ({row["question"].strip() for row in prior_questions} & {row["question"].strip() for row in questions})

    # Evaluation clauses terminate only in terminal authority.
    for qid, spec in contract["questions"].items():
        for clause in spec["clauses"]:
            assert clause["type"] in {"all_of", "any_of", "min_count"}
            assert clause["anchor_ids"]
            assert set(clause["terminal_authority_types"]) <= {"RAW_MEMORY", "HUMAN_KNOWLEDGE"}
            for anchor_id in clause["anchor_ids"]:
                assert anchor_id in anchor_map
                assert anchor_map[anchor_id]["authority_type"] in clause["terminal_authority_types"]
        for anchor_id in spec["corroborating_optional_anchor_ids"] + spec["forbidden_conflation_anchor_ids"]:
            assert anchor_id in anchor_map

    # Fixed subject scope and lifecycle are prospective and deterministic.
    assert lifecycle["fixed_subject_scope"] is True
    assert lifecycle["automatic_identity_routing"] is False
    assert lifecycle["projection_builds_planned"] == 5
    assert len(lifecycle["events"]) == 19
    assert [row["event_index"] for row in lifecycle["events"]] == list(range(1, 20))
    assert sum(row["event"] in {"BUILD_PROJECTION", "REBUILD_PROJECTION"} for row in lifecycle["events"]) == 5
    assert {row["question_id"] for row in lifecycle["events"] if row["event"] == "QUERY_PAIR"} == set(question_map)
    for subject_id, subject in lifecycle["subjects"].items():
        for state, state_doc in subject["states"].items():
            active = active_anchors(anchors, subject_id, state)
            assert state_doc["active_anchor_ids"] == [row["anchor_id"] for row in active]
            assert state_doc["snapshot_sha256"] == snapshot_sha(active)

    # Full current authority is sufficient for all questions.
    for question in questions:
        active = active_anchors(anchors, question["subject_id"], question["state"])
        full_eval = evaluate_context(question["question_id"], [row["anchor_id"] for row in active], contract, anchor_map)
        assert full_eval["status"] != "INSUFFICIENT_AUTHORITY", (question["question_id"], full_eval)

    # Freeze subject-scoped exact-BM25 top-6 Q contexts.
    observed = Counter()
    ranks = {}
    for question in questions:
        qid = question["question_id"]
        active = active_anchors(anchors, question["subject_id"], question["state"])
        ranking = bm25_ranking(active, question["question"])
        ranking_ids = [anchor_id for anchor_id, _ in ranking]
        selected = ranking_ids[:6]
        frozen = control_map[qid]
        assert selected == frozen["selected_anchor_ids"], (qid, selected, frozen["selected_anchor_ids"])
        assert ranking_ids[:9] == frozen["ranking_prefix_9"]
        actual = evaluate_context(qid, selected, contract, anchor_map)
        assert actual["status"] == frozen["authority_status"], (qid, actual, frozen)
        assert actual["missing_clause_ids"] == frozen["missing_clause_ids"]
        assert actual["forbidden_conflation_anchor_ids_present"] == frozen["forbidden_conflation_anchor_ids_present"]
        ctx = evidence_context(anchor_map, selected)
        assert len(ctx) == frozen["selected_context_chars"]
        assert hashlib.sha256(ctx.encode("utf-8")).hexdigest() == frozen["selected_context_sha256"]
        assert sum(len(anchor_map[anchor_id]["text"]) for anchor_id in selected) == frozen["selected_raw_evidence_chars"]
        observed[actual["status"]] += 1
        ranks[qid] = ranking_ids

    assert observed == Counter({
        "SUFFICIENT_CLEAN": 3,
        "SUFFICIENT_WITH_CONFLATION_RISK": 6,
        "INSUFFICIENT_AUTHORITY": 3,
    })
    assert [qid for qid in question_map if control_map[qid]["authority_status"] == "INSUFFICIENT_AUTHORITY"] == ["PQ004", "PQ007", "PQ008"]
    assert ranks["PQ004"].index("P004") + 1 == 12
    assert ranks["PQ007"].index("P021") + 1 == 8
    assert ranks["PQ008"].index("P021") + 1 == 8
    assert manifest["fresh_projection_opportunity_question_ids"] == ["PQ004", "PQ008"]
    assert manifest["stale_gap_question_ids"] == ["PQ007", "PQ011"]
    assert manifest["primary_stale_negative_control"] == "PQ011"

    # Primary stale negative control genuinely flips current authority.
    ks0 = lifecycle["subjects"]["keystone"]["states"]["S0"]
    ks1 = lifecycle["subjects"]["keystone"]["states"]["S1"]
    assert ks0["snapshot_sha256"] != ks1["snapshot_sha256"]
    assert {"P033", "P034"} <= set(ks1["active_anchor_ids"])
    assert {"P033", "P034", "P025"} <= set(control_map["PQ011"]["selected_anchor_ids"])
    assert control_map["PQ011"]["authority_status"] == "SUFFICIENT_CLEAN"

    # Projection compiler is generic, query-blind, and evaluator-blind.
    assert list(inspect.signature(prompt_module.projection_prompt_v0).parameters) == ["subject_id", "authority_context"]
    for phrase in [
        "rebuildable DERIVED retrieval projection",
        "Do not answer any user question",
        "Do not infer or discover a different subject identity",
        "The projection is noncanonical working state and never becomes terminal authority",
        "Never synthesize an identity, attribution, policy, authorization, project, or temporal bridge",
        "Reference every supplied anchor at least once",
        "Do not include expected answers, evaluation rules, promotion criteria, future questions",
    ]:
        assert phrase in rendered_prompt, phrase
    assert "dummy-subject" in rendered_prompt and "dummy-authority" in rendered_prompt
    for forbidden in [
        "PQ004", "PQ007", "PQ008", "PQ011", "P004", "P021", "P033", "P034",
        "85 percent", "10 / 12", "G2_PERSISTENCE_CANDIDATE_EARNED",
        "expected_control_authority_status", "stale_negative_control",
    ]:
        assert forbidden not in prompt_source, forbidden

    assert evaluation["status"] == "PROSPECTIVE_G2_EVALUATION_ONLY_NOT_RUNTIME"
    assert evaluation["projection_selection"] == {
        "fresh_projection_entry_top_k": 2,
        "maximum_terminal_anchor_count": 6,
        "minimum_terminal_anchor_count": 4,
        "no_projection_text_to_composer": True,
        "raw_bm25_fill_to_minimum": True,
        "stale_snapshot_behavior": "EXACT_Q_CONTROL_BYPASS",
    }
    planned = evaluation["planned_execution"]
    assert planned["candidate_model"] == "gpt-5.6-luna"
    assert planned["Q_composer_calls"] == 12
    assert planned["P_composer_calls"] == 12
    assert planned["P_projection_build_or_rebuild_calls"] == 5
    assert planned["max_semantic_call_attempts"] == 29
    assert planned["planner_calls"] == planned["selector_calls"] == planned["vector_calls"] == planned["rerolls"] == 0

    promotion = evaluation["promotion"]["all_required"]
    for phrase in [
        "fresh P selected contexts improve authority status versus Q on both PQ004 and PQ008",
        "PQ007 and PQ011 stale guards bypass projection and reproduce the exact Q selected terminal anchors",
        "P semantic PASS count >= 10 of 12",
        "P paired semantic improvements versus Q >= 2",
        "P paired semantic regressions versus Q == 0",
        "P new CRITICAL_ERROR versus Q == 0",
        "P selected raw terminal evidence characters across the 10 fresh-projection queries <= 85 percent of Q on the same queries",
        "projection build/rebuild calls == 5 and no projection compiler call occurs inside a query event",
    ]:
        assert phrase in promotion, phrase

    for phrase in [
        "PREREGISTRATION / ZERO-MODEL FIRST / NO SEMANTIC EXECUTION AUTHORIZED BY THIS FILE",
        "STALE_PROJECTION_BYPASS",
        "Projection statements themselves never enter the final composer context",
        "P004 broader portfolio evidence is exact rank **12**",
        "P021 second month-close observation is exact rank **8**",
        "total semantic attempts: **29**",
        "P semantic verdicts contain at least **10 / 12 PASS**",
        "at least **2 paired semantic improvements**",
        "total P selected raw terminal-evidence characters are at most **85%** of Q",
        "This PR authorizes **0 semantic calls**",
        "fresh G2 execution-contract branch",
    ]:
        assert phrase in prereg, phrase

    assert "G1 QUERY-TIME BASELINE EARNED FOR G2 RESEARCH COMPARATOR" in closure
    assert "G2 preregistration/design work only" in closure

    # Prospective only: no model outputs or execution artifacts.
    forbidden_keys = {"\"answer\"", "\"composer\"", "\"projection_output\"", "\"semantic_verdict\"", "\"adjudication\"", "\"gold_answer\"", "\"model_receipt\""}
    for path in [
        PKG / "questions.json", PKG / "authority-contract.json", PKG / "lifecycle.json",
        PKG / "control-contexts.json", PKG / "manifest.json", EVAL,
    ]:
        text = path.read_text(encoding="utf-8")
        for key in forbidden_keys:
            assert key not in text, (path, key)

    assert evaluation["semantic_calls_authorized_on_this_pr"] is False
    assert manifest["semantic_calls_authorized_on_this_pr"] is False
    assert not (ROOT / "run_g2.py").exists()
    assert not (REPO / "remote-lab" / "e023-g2-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g2.yml").exists()

    output = {
        "model_calls": 0,
        "anchor_count": len(anchors),
        "question_count": len(questions),
        "subject_count": manifest["subject_count"],
        "authority_type_counts": dict(sorted(Counter(row["authority_type"] for row in anchors).items())),
        "Q_control_status_counts": dict(sorted(observed.items())),
        "Q_control_insufficient_question_ids": ["PQ004", "PQ007", "PQ008"],
        "PQ004_missing_anchor_rank": 12,
        "PQ007_PQ008_missing_anchor_rank": 8,
        "fresh_projection_opportunities": ["PQ004", "PQ008"],
        "stale_gap_questions": ["PQ007", "PQ011"],
        "primary_stale_negative_control": "PQ011",
        "planned_projection_build_rebuild_calls": 5,
        "planned_Q_composer_calls": 12,
        "planned_P_composer_calls": 12,
        "planned_total_semantic_attempts_if_separately_executed": 29,
        "semantic_calls_authorized_on_this_pr": False,
        "g2_execution_authorized_on_this_pr": False,
        "g2_product_persistence_authorized": False,
        "top6_product_default_authorized": False,
        "graph_entity_ku_authorized": False,
        "vector_default_authorized": False,
        "automatic_identity_routing_authorized": False,
        "dogfood_runtime_change_authorized": False,
    }
    print("E023 G2 prereg zero-model validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
