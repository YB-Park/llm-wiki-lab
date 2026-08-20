from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
EVIDENCE = ROOT / "evidence" / "g1f-run-32349241403"
RESULT = EVIDENCE / "result.json"
RESULT_SHA = EVIDENCE / "result.sha256"
SOURCE = EVIDENCE / "source.json"
RUN_FINAL = EVIDENCE / "run-final.json"
ADJUDICATION = ROOT / "g1f-adjudication-v0.json"
RESULT_DOC = ROOT / "g1f-results-v0.md"
EVALUATION = ROOT / "g1f-evaluation-contract-v0.json"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1f.yml"

RUN_ID = 32349241403
PREREG_MERGE_SHA = "1e5a3f991d0c3b76552725933149702ff6e53d15"
EXECUTION_SOURCE = "eab8c9e4f5ebbe5f43b93a1558fd3f9cc295f772"
EVIDENCE_COMMIT = "fdae1b5ce645d6951db0d6b703947405c3c3fa78"
EXPECTED_SHA256 = "de65721f1e127f9dd2d24f1c1ef33dd1a42740fee6f755ef9cf411b476a0b45a"


def counts(rows: dict[str, dict]) -> dict[str, int]:
    c = Counter(row["verdict"] for row in rows.values())
    return {"PASS": c["PASS"], "PARTIAL": c["PARTIAL"], "CRITICAL_ERROR": c["CRITICAL_ERROR"]}


def main() -> int:
    raw = RESULT.read_bytes()
    result = json.loads(raw)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    run_final = json.loads(RUN_FINAL.read_text(encoding="utf-8"))
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    evaluation = json.loads(EVALUATION.read_text(encoding="utf-8"))
    result_doc = RESULT_DOC.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    assert RESULT_SHA.read_text(encoding="utf-8").split()[0] == EXPECTED_SHA256

    assert source == {
        "execution_source_sha": EXECUTION_SOURCE,
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "request_id": "e023-g1f-composition-comparison-v0",
        "run_id": RUN_ID,
        "workflow": "E023 generality G1f",
    }

    assert result["format"] == "E023-G1f-v0"
    assert result["execute_model"] is True
    assert result["execution_complete"] is True
    assert result["execution_source_sha"] == EXECUTION_SOURCE
    assert result["prereg_merge_sha"] == PREREG_MERGE_SHA
    assert result["model"] == "gpt-5.6-luna"
    assert result["model_call_attempts"] == 16
    assert result["usage"]["model_calls"] == 16
    assert result["request"]["old_composer_calls"] == 8
    assert result["request"]["new_composer_calls"] == 8
    assert result["request"]["planner_calls"] == 0
    assert result["request"]["selector_calls"] == 0
    assert result["request"]["retrieval_model_calls"] == 0
    assert result["request"]["rerolls"] == 0
    assert result["context_identity_contract"] is True
    assert result["semantic_promotion"] == "PENDING_FROZEN_ADJUDICATION"
    assert len(result["call_schedule"]) == 16

    qids = [f"DQ00{i}" for i in range(1, 9)]
    assert sorted(result["pairs"]) == qids
    for qid in qids:
        pair = result["pairs"][qid]
        assert set(pair["arms"]) == {"O", "N"}
        assert len(pair["selected_anchor_ids"]) == 6
        for arm in ("O", "N"):
            row = pair["arms"][arm]
            assert row["contract_ok"] is True
            assert row["model_receipt"]["model"] == "gpt-5.6-luna"
            assert row["input_context_sha256"] == pair["context_sha256"]
            assert row["input_question_sha256"] == pair["question_sha256"]
            assert isinstance(row["raw_model_text"], str) and row["raw_model_text"]
            assert set(row["composer"]) == {"answer", "cited_anchor_ids", "insufficient_authority"}
            assert set(row["composer"]["cited_anchor_ids"]) <= set(pair["selected_anchor_ids"])

    assert result["pairs"]["DQ003"]["negative_control"] is True
    assert result["pairs"]["DQ003"]["frozen_authority_status"] == "INSUFFICIENT_AUTHORITY"
    for arm in ("O", "N"):
        assert result["pairs"]["DQ003"]["arms"][arm]["composer"]["insufficient_authority"] is True
    for arm in ("O", "N"):
        assert result["pairs"]["DQ004"]["arms"][arm]["composer"]["insufficient_authority"] is False
        assert {"D020", "D021", "D022", "D023"} <= set(
            result["pairs"]["DQ004"]["arms"][arm]["composer"]["cited_anchor_ids"]
        )
    for arm in ("O", "N"):
        assert {"D038", "D039", "D040"} <= set(
            result["pairs"]["DQ007"]["arms"][arm]["composer"]["cited_anchor_ids"]
        )

    assert "D033" in result["pairs"]["DQ006"]["selected_anchor_ids"]
    assert "D033" not in result["pairs"]["DQ006"]["arms"]["O"]["composer"]["cited_anchor_ids"]
    assert "D033" not in result["pairs"]["DQ006"]["arms"]["N"]["composer"]["cited_anchor_ids"]

    o_counts = counts(adjudication["O_semantic_verdicts"])
    n_counts = counts(adjudication["N_semantic_verdicts"])
    assert o_counts == {"PASS": 7, "PARTIAL": 1, "CRITICAL_ERROR": 0}
    assert n_counts == {"PASS": 7, "PARTIAL": 1, "CRITICAL_ERROR": 0}
    assert adjudication["O_semantic_verdicts"]["DQ006"]["root_cause"] == "COMPOSITION_CORROBORATION_OMISSION"
    assert adjudication["N_semantic_verdicts"]["DQ006"]["root_cause"] == "COMPOSITION_CORROBORATION_OMISSION"
    for qid in set(qids) - {"DQ006"}:
        assert adjudication["O_semantic_verdicts"][qid]["verdict"] == "PASS"
        assert adjudication["N_semantic_verdicts"][qid]["verdict"] == "PASS"

    summary = adjudication["semantic_summary"]
    assert summary["N_semantic_improvements_vs_O"] == 0
    assert summary["N_semantic_regressions_vs_O"] == 0
    assert summary["N_new_critical_errors_vs_O"] == 0
    assert summary["DQ003_negative_control_N"] == "PASS"
    assert summary["DQ004_proposition_scope_N"] == "PASS"
    assert summary["DQ001_user_owned_authority_N"] == "PASS"
    assert summary["DQ007_user_owned_authority_N"] == "PASS"
    assert summary["N_all_load_bearing_citations_supported"] is True
    assert summary["frozen_final_promotion"] == "NOT_EARNED"

    promotion = adjudication["promotion_arithmetic"]
    assert promotion["N_PASS_count"] == 7
    assert promotion["required_N_PASS_count"] == 7
    assert promotion["paired_semantic_improvements"] == 0
    assert promotion["required_paired_semantic_improvements"] == 1
    assert promotion["semantic_regressions"] == 0
    assert promotion["new_critical_errors"] == 0
    assert promotion["promotion"] == "NOT_EARNED"
    assert promotion["binding_failure"] == "N_PAIRED_IMPROVEMENTS_0_LT_REQUIRED_1"

    frozen = evaluation["promotion"]["all_required"]
    assert "N_PASS_count >= 7 of 8" in frozen
    assert "N_paired_semantic_improvements_vs_O >= 1" in frozen

    assert run_final == {
        "artifact": {
            "digest": "sha256:902f4f0ee0dcba73ad9ffcb56146e489a10900539f0d4bc8c123de09859b11b2",
            "id": 9399246019,
            "name": "e023-g1f-32349241403",
        },
        "conclusion": "success",
        "created_at": "2026-08-20T08:31:30Z",
        "execution_source_sha": EXECUTION_SOURCE,
        "prereg_merge_sha": PREREG_MERGE_SHA,
        "run_attempt": 1,
        "run_id": RUN_ID,
        "status": "completed",
        "updated_at": "2026-08-20T08:33:16Z",
        "workflow": "E023 generality G1f",
    }

    for phrase in [
        "G1f composition candidate promotion is NOT_EARNED",
        "N improvements vs O: **0**",
        "7/8 PASS",
        "DQ003 — authority-incomplete identity negative control",
        "DQ004 — proposition-scoped sufficiency",
        "COMPOSITION_CORROBORATION_OMISSION",
        "zero-model G1 closure decision",
        "G2 is not authorized by this result alone",
    ]:
        assert phrase in result_doc, phrase

    assert f"github.sha == '{EXECUTION_SOURCE}'" in workflow
    assert "github.event.before ==" not in workflow
    assert "workflow_dispatch" not in workflow

    output = {
        "model_calls": 0,
        "run_id": RUN_ID,
        "execution_source_sha": EXECUTION_SOURCE,
        "evidence_commit_sha": EVIDENCE_COMMIT,
        "result_sha256": EXPECTED_SHA256,
        "frozen_semantic_calls": 16,
        "O_semantic": o_counts,
        "N_semantic": n_counts,
        "N_semantic_improvements": 0,
        "N_semantic_regressions": 0,
        "N_new_critical_errors": 0,
        "negative_control_passed": True,
        "proposition_scope_passed": True,
        "user_owned_authority_hard_cases_passed": True,
        "composition_candidate_promotion": "NOT_EARNED",
        "binding_failure": "N_PAIRED_IMPROVEMENTS_0_LT_REQUIRED_1",
        "execution_source_locked": True,
        "semantic_calls_authorized": False,
        "top6_product_policy_authorized": False,
        "g2_persistence_authorized": False,
        "graph_entity_ku_authorized": False,
        "vector_default_authorized": False,
        "automatic_identity_routing_authorized": False,
    }
    print("E023 G1f frozen result validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
