from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
DECISION = ROOT / "g1-closure-decision-v0.md"
G1E = ROOT / "g1e-adjudication-v0.json"
G1F = ROOT / "g1f-adjudication-v0.json"
G1F_RESULT = ROOT / "g1f-results-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "validate-e023-g1-closure.yml"


def main() -> int:
    decision = DECISION.read_text(encoding="utf-8")
    g1e = json.loads(G1E.read_text(encoding="utf-8"))
    g1f = json.loads(G1F.read_text(encoding="utf-8"))
    g1f_result = G1F_RESULT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert g1e["semantic_summary"]["frozen_final_promotion"] == "NOT_EARNED"
    assert g1e["semantic_summary"]["B6_semantic_regressions_vs_A5"] == 0
    assert g1e["semantic_summary"]["B6_new_critical_errors_vs_A5"] == 0
    assert g1e["authority_summary"]["B6"]["INSUFFICIENT_AUTHORITY"] == 0

    assert g1f["semantic_summary"]["O"] == {"PASS": 7, "PARTIAL": 1, "CRITICAL_ERROR": 0}
    assert g1f["semantic_summary"]["N"] == {"PASS": 7, "PARTIAL": 1, "CRITICAL_ERROR": 0}
    assert g1f["semantic_summary"]["N_semantic_improvements_vs_O"] == 0
    assert g1f["semantic_summary"]["N_semantic_regressions_vs_O"] == 0
    assert g1f["semantic_summary"]["N_new_critical_errors_vs_O"] == 0
    assert g1f["semantic_summary"]["DQ003_negative_control_N"] == "PASS"
    assert g1f["semantic_summary"]["frozen_final_promotion"] == "NOT_EARNED"
    assert "G1f composition candidate promotion is NOT_EARNED" in g1f_result

    for phrase in [
        "G1 QUERY-TIME BASELINE EARNED FOR G2 RESEARCH COMPARATOR",
        "exact whole-object BM25 top-6 + the frozen old composer",
        "`composition_prompt_v1` is not promoted",
        "G2 preregistration/design work only",
        "fixed, prospectively supplied identities/subjects",
        "rebuildable `DERIVED_MEMORY`-like semantic projection",
        "source addition, correction/supersession, and a stale-view hazard",
        "negative control where persistence would be harmful if stale authority were trusted",
        "zero semantic calls in the preregistration PR",
        "A persistence arm that improves latency/call count but introduces a stale load-bearing claim must fail",
        "Dogfood 0.1.16 remains the product baseline",
        "Issue #141 natural installed dogfood",
        "Issue #132 reliability follow-ups remain evidence-gated",
        "no product top-6 default",
        "no graph/entity/KU schema",
        "fresh G2 fixed-identity persistence preregistration",
    ]:
        assert phrase in decision, phrase

    assert not (ROOT / "run_g2.py").exists()
    assert not (REPO / "remote-lab" / "e023-g2-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g2.yml").exists()
    assert "copilot-requests: write" not in workflow

    output = {
        "model_calls": 0,
        "g1_query_time_baseline_for_g2_comparator": "EARNED",
        "g1e_strict_promotion": "NOT_EARNED",
        "g1f_composition_candidate_promotion": "NOT_EARNED",
        "g1f_old_composer_PASS": 7,
        "g1f_old_composer_CRITICAL_ERROR": 0,
        "g1f_new_composer_PASS": 7,
        "g1f_new_composer_CRITICAL_ERROR": 0,
        "g2_preregistration_design_authorized": True,
        "g2_semantic_execution_authorized": False,
        "g2_product_persistence_authorized": False,
        "top6_product_default_authorized": False,
        "graph_entity_ku_authorized": False,
        "vector_default_authorized": False,
        "automatic_identity_routing_authorized": False,
        "dogfood_runtime_change_authorized": False,
    }
    print("E023 G1 closure validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
