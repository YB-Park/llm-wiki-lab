from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
ADJUDICATION = ROOT / "g2-adjudication-v0.json"
RESULT_DOC = ROOT / "g2-results-v0.md"
CLOSURE = ROOT / "g2-closure-decision-v0.md"
README = ROOT / "README.md"
HANDOFF = REPO / "HANDOFF.md"
DESIGN = REPO / "docs" / "14-generality-and-semantic-projections.md"


def main() -> int:
    adjudication = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    result_doc = RESULT_DOC.read_text(encoding="utf-8")
    closure = CLOSURE.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    design = DESIGN.read_text(encoding="utf-8")

    assert adjudication["semantic_summary"]["Q"] == {
        "PASS": 9, "PARTIAL": 0, "FAIL_RETRIEVAL": 1, "FAIL_COMPOSITION": 0, "CRITICAL_ERROR": 2
    }
    assert adjudication["semantic_summary"]["P"] == {
        "PASS": 8, "PARTIAL": 0, "FAIL_RETRIEVAL": 1, "FAIL_COMPOSITION": 0, "CRITICAL_ERROR": 3
    }
    assert adjudication["semantic_summary"]["P_paired_semantic_improvements_vs_Q"] == 2
    assert adjudication["semantic_summary"]["P_paired_semantic_regressions_vs_Q"] == 3
    assert adjudication["semantic_summary"]["P_new_critical_errors_vs_Q"] == 3
    assert adjudication["semantic_summary"]["frozen_final_promotion"] == "NOT_EARNED"
    assert adjudication["evidence_efficiency"]["criterion_passed"] is True
    assert adjudication["projection_lifecycle"]["stale_bypass_guard_passed"] is True
    assert adjudication["authority_summary"]["required_opportunity_PQ008_improved"] is False
    assert adjudication["authority_summary"]["P_authority_regressions_vs_Q"] == ["PQ009", "PQ012"]

    for phrase in [
        "G2 PERSISTENCE NOT EARNED",
        "G3 NOT OPENED",
        "Snapshot freshness guard is credible",
        "P/Q: 68.3%",
        "G2 is parked",
        "diagnostic history, not a tuning set",
        "Paid E023 semantic calls pause",
        "Dogfood 0.1.16 natural installed use on Issue #141 returns to the primary product-evidence position",
    ]:
        assert phrase in closure, phrase

    assert "G2 fixed-identity persistence promotion is NOT_EARNED" in result_doc
    assert "G2 FIXED-IDENTITY PERSISTENCE NOT EARNED AND PARKED" in readme
    assert "G3 NOT OPENED" in readme

    # HANDOFF.md is a living continuation checkpoint. Validate current decision
    # boundaries, not historical section titles or experiment narration.
    for phrase in [
        "## NOW",
        "current product decision: **GO for installed self-dogfood / Alpha use**",
        "primary product-evidence track: **Issue #141 natural installed dogfood**",
        "paid E023 semantic calls: **paused**",
        "**G2 Persistence: NOT_EARNED; parked.**",
        "**G3 Identity / Routing: NOT_OPENED.**",
        "same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning",
        "## NEXT ACTION",
        "Run the Day-0 installed smoke on the exact 0.1.16 VSIX",
    ]:
        assert phrase in handoff, phrase

    assert "G2 PERSISTENCE NOT EARNED AND PARKED" in design
    assert "Query-time reconstruction is the default architecture posture" in design
    assert "paid E023 semantic calls pause" in design

    output = {
        "model_calls": 0,
        "g1_exploratory_search": "CLOSED",
        "g2_persistence": "NOT_EARNED_PARKED",
        "g3_identity_routing": "NOT_OPENED",
        "stale_snapshot_guard_signal": "EARNED",
        "fresh_evidence_ratio": adjudication["evidence_efficiency"]["P_over_Q_ratio"],
        "same_slice_pq_rerun_authorized": False,
        "product_persistence_authorized": False,
        "paid_e023_semantic_calls_authorized": False,
        "next_primary_track": "ISSUE_141_NATURAL_DOGFOOD",
        "issue_132_reliability": "EVIDENCE_GATED",
    }
    print("E023 G2 closure validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
