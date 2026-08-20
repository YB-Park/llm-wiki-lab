from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = HERE / "evidence" / "q1-v2-run-32379189525" / "result.json"
ADJ = HERE / "q1-v2-adjudication-v0.json"
CONTRACT = HERE / "q1-evaluation-contract-v0.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    result = load(RESULT)
    adj = load(ADJ)
    contract = load(CONTRACT)
    gate = contract["primary_promotion"]

    assert result["format"] == "E024-Q1-v2"
    assert result["execute_model"] is True
    assert result["execution_complete"] is True
    assert result["paired_context_identity"] is True
    assert result["model_call_attempts"] == gate["model_call_attempts"] == 18
    assert result["request"]["model"] == "gpt-5.6-luna"
    assert result["request"]["rerolls"] == gate["rerolls"] == 0
    assert result["request"]["planner_calls"] == 0
    assert result["request"]["selector_calls"] == 0
    assert result["request"]["retrieval_model_calls"] == 0

    signal = result["execution_signal"]
    assert signal["frozen_parent_sha"] == "499958ec5263a41f6ab28a2448c4c0608c0046f9"
    assert signal["execution_head_sha"] == "435dae2b89aeddc62a4470db1a043ee331fa93ff"
    assert signal["changed_paths"] == ["remote-lab/e024-q1-v2-execute.json"]
    assert signal["adapters_blob"] == "fc62367ab929349a6be13e83258957ba1714265e"

    summary = result["structural_summary"]
    assert summary["all_attempts_completed"] is True
    assert summary["q_contract_valid_count"] == 9
    assert summary["q_contract_invalid_count"] == 0
    assert summary["q_external_char_ratio_median"] <= gate["median_external_char_ratio_max"]
    assert summary["q_external_char_ratio_max"] <= gate["max_external_char_ratio_max"]
    assert summary["q_serialized_brief_chars_max"] <= gate["all_query_plane_outputs_bounded_chars_max"]

    terminal_types = {"RAW_MEMORY", "HUMAN_KNOWLEDGE"}
    for qid, pair in result["pairs"].items():
        assert pair["arms"]["M"]["contract_ok"] is True, qid
        q = pair["arms"]["Q"]
        assert q["contract_ok"] is True, qid
        refs = q["result"]["terminal_refs"]
        assert len({ref["id"] for ref in refs}) == len(refs), qid
        for ref in refs:
            assert ref["authority_type"] in terminal_types, (qid, ref)
            assert pair["allowed_terminal_types"][ref["id"]] == ref["authority_type"], (qid, ref)
        assert q["serialized_result_chars"] <= gate["all_query_plane_outputs_bounded_chars_max"], qid
        assert q["external_char_ratio"] <= gate["max_external_char_ratio_max"], qid

    semantic = adj["summary"]
    assert semantic["Q_PASS"] >= gate["query_plane_min_pass"]
    assert semantic["Q_CRITICAL_ERROR"] <= gate["query_plane_max_critical"]
    assert semantic["Q_new_critical_vs_M"] == gate["query_plane_new_critical_vs_main"]
    assert semantic["Q_paired_semantic_regressions_vs_M"] == gate["query_plane_paired_regressions_vs_main"]
    assert semantic == {
        "M_PASS": 9,
        "M_PARTIAL": 0,
        "M_CRITICAL_ERROR": 0,
        "Q_PASS": 9,
        "Q_PARTIAL": 0,
        "Q_CRITICAL_ERROR": 0,
        "Q_new_critical_vs_M": 0,
        "Q_paired_semantic_regressions_vs_M": 0,
    }

    assert result["pairs"]["Q001"]["arms"]["Q"]["result"]["answer"].find("99 attempts") == -1
    assert all(ref["id"] != "D001" for ref in result["pairs"]["Q007"]["arms"]["Q"]["result"]["terminal_refs"])
    assert result["pairs"]["Q009"]["arms"]["Q"]["result"]["insufficient_authority"] is True

    print("E024 Q1 v2 result gate validation: PASS")
    print(json.dumps({
        "model_calls": result["model_call_attempts"],
        "Q_PASS": semantic["Q_PASS"],
        "Q_CRITICAL_ERROR": semantic["Q_CRITICAL_ERROR"],
        "paired_regressions": semantic["Q_paired_semantic_regressions_vs_M"],
        "median_external_char_ratio": summary["q_external_char_ratio_median"],
        "max_external_char_ratio": summary["q_external_char_ratio_max"],
        "max_brief_chars": summary["q_serialized_brief_chars_max"],
        "q1_l0_promotion": "EARNED",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
