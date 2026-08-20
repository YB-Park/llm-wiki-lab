from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
REQUEST = REPO / "remote-lab" / "e023-g1d-request.json"
RUNNER = ROOT / "run_g1d.py"
COMMON = ROOT / "g1d_common.py"
ADDENDUM = ROOT / "g1d-execution-addendum-v0.md"
WORKFLOW = REPO / ".github" / "workflows" / "e023-generality-g1d.yml"
PREREG_BASE = "b0042a87cf871070b334a6c5bef79f390b5a6434"
EXECUTION_SOURCE_SHA = "c74673a83744789f271fa54c43b20212160007a2"
COMMON_BLOB = "14da368b74c214a9a7c2b041b8d5a09e10a0a097"


def main() -> int:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e023-g1d-deterministic-selection-v0",
        "model": "gpt-5.6-luna",
        "question_count": 8,
        "initial_top_k": 5,
        "max_followup_queries": 2,
        "candidate_followup_top_k": 3,
        "rrf_k": 60,
        "final_top_k": 4,
        "planner_snippet_chars": 320,
        "a_composer_calls": 8,
        "d_planner_calls": 8,
        "d_composer_calls": 8,
        "d_selector_calls": 0,
        "max_model_call_attempts": 24,
        "max_ai_credits_per_call": 30,
    }
    assert request == expected, request

    runner = RUNNER.read_text(encoding="utf-8")
    common = COMMON.read_text(encoding="utf-8")
    addendum = ADDENDUM.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert subprocess.check_output(["git", "hash-object", str(COMMON)], text=True).strip() == COMMON_BLOB
    assert "RRF_K = 60" in common
    assert "FINAL_TOP_K = 4" in common
    assert "def rrf_select(" in common

    assert '"d_selector_calls": 0' in runner
    assert "selector_prompt(" not in runner
    assert "parse_selector(" not in runner
    assert 'return G1C.planner_prompt(question, initial_view).replace("Axxx", "Bxxx")' in runner
    assert 'return G1C.composer_prompt(question, context).replace("Axxx", "Bxxx")' in runner
    assert "EARNED_PENDING_SEMANTIC_SAFETY" in runner
    assert "metrics[\"d_insufficient\"] == 0" in runner
    assert "metrics[\"d_clean\"] >= 7" in runner
    assert "metrics[\"authority_improvements\"] >= 2" in runner
    assert "metrics[\"authority_regressions\"] == 0" in runner

    for phrase in [
        "exact/max semantic attempts: **24**",
        "model selector calls: **0**",
        "RRF `k=60`",
        "final budget `4`",
        PREREG_BASE,
    ]:
        assert phrase in addendum, phrase

    assert "copilot-requests: write" in workflow
    assert "github.event_name == 'push'" in workflow
    assert f"github.sha == '{EXECUTION_SOURCE_SHA}'" in workflow
    assert "github.event_name == 'pull_request'" in workflow
    assert "--execute-model" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "result.sha256" in workflow

    output = {
        "model_calls": 0,
        "model": request["model"],
        "question_count": request["question_count"],
        "max_semantic_calls": request["max_model_call_attempts"],
        "model_selector_calls": request["d_selector_calls"],
        "rrf_k": request["rrf_k"],
        "final_top_k": request["final_top_k"],
        "common_blob_locked": COMMON_BLOB,
        "prereg_base_sha": PREREG_BASE,
        "execution_source_sha_locked": EXECUTION_SOURCE_SHA,
        "stage_persistence_required": True,
        "semantic_calls_authorized_on_pr": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 G1d execution contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
