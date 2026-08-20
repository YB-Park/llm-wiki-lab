from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CONTRACT = ROOT / "authority-preserving-composition-contract-v0.md"
FIXTURES = ROOT / "composition-contract-fixtures-v0.json"
PROMPT = ROOT / "composition_prompt_v1.py"


def load_prompt_module():
    spec = importlib.util.spec_from_file_location("composition_prompt_v1", PROMPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("prompt_import_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    contract = CONTRACT.read_text(encoding="utf-8")
    fixtures_doc = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fixtures = fixtures_doc["fixtures"]
    prompt_source = PROMPT.read_text(encoding="utf-8")
    prompt_module = load_prompt_module()
    rendered = prompt_module.composer_prompt_v1("dummy question", "dummy evidence")

    assert fixtures_doc["status"] == "ZERO_MODEL_ADVERSARIAL_CONTRACT_FIXTURES"
    assert len(fixtures) == 10
    assert len({row["fixture_id"] for row in fixtures}) == 10
    assert [row["fixture_id"] for row in fixtures] == [f"CF{i:03d}" for i in range(1, 11)]

    required_classes = {
        "user_owned_decision",
        "direct_vs_attributed",
        "missing_identity_bridge",
        "resolved_identity_with_distractor",
        "policy_vs_capability",
        "proposition_scoped_sufficiency",
        "temporal_causal_sequence",
        "negative_characterization",
        "repeated_observation_insufficient",
        "repeated_observation_sufficient",
    }
    assert {row["class"] for row in fixtures} == required_classes
    assert {row["expected_insufficient_authority"] for row in fixtures} == {True, False}

    rule_counts: Counter[str] = Counter()
    for row in fixtures:
        assert row["must_preserve"]
        assert row["must_not"]
        assert row["contract_rules"]
        rule_counts.update(row["contract_rules"])
    assert set(rule_counts) == {f"C{i}" for i in range(1, 9)}
    assert all(rule_counts[f"C{i}"] >= 1 for i in range(1, 9))

    # Contract must freeze each normative behavior and the no-jargon/runtime boundary.
    for phrase in [
        "C1 — preserve user-owned epistemic commitment",
        "C2 — preserve direct versus attributed authorship",
        "C3 — do not synthesize a missing bridge",
        "C4 — scope insufficiency to the requested proposition",
        "C5 — preserve explicit negative evidence and scope limits",
        "C6 — preserve temporal state and correction semantics",
        "C7 — citations must terminate in supplied authority",
        "C8 — supported risk is not automatic insufficiency",
        "does **not** need to expose internal storage labels",
        "must **not** see",
        "evaluation clauses",
        "new separated material",
        "hold retrieval/evidence budget fixed",
    ]:
        assert phrase in contract, phrase

    # Prompt candidate must operationalize the generic contract without fixture/domain specialization.
    for phrase in [
        "authority-preserving composer",
        "HUMAN_KNOWLEDGE is an explicit user-owned decision, belief, rationale, or hypothesis",
        "preserve that user ownership naturally",
        "Preserve direct authorship versus third-party attribution",
        "Never synthesize a load-bearing identity, attribution, policy, project, temporal, or authorization bridge",
        "Set insufficient_authority=true if and only if at least one load-bearing part of the user's actual question",
        "Do not set it true merely because the evidence cannot prove a stronger guarantee",
        "The presence of a plausible distractor alone does not make an otherwise supported answer insufficient",
        "Every load-bearing factual statement must cite the supplied terminal authority",
        "Do not provide hidden reasoning or chain-of-thought",
    ]:
        assert phrase in rendered, phrase

    for forbidden in [
        "CQ001",
        "BQ001",
        "AQ001",
        "Rina Singh",
        "Cedar",
        "Redwood",
        "Kafka",
        "RabbitMQ",
        "top-6",
        "RRF",
        "evaluation clause",
        "expected answer",
        "promotion threshold",
    ]:
        assert forbidden not in prompt_source, forbidden

    assert "`answer`" in rendered
    assert "`cited_anchor_ids`" in rendered
    assert "`insufficient_authority`" in rendered
    assert "dummy question" in rendered
    assert "dummy evidence" in rendered

    # This PR is a zero-model composition contract only. No G1f runner/request/workflow is allowed yet.
    assert not (ROOT / "run_g1f.py").exists()
    assert not (REPO / "remote-lab" / "e023-g1f-request.json").exists()
    assert not (REPO / ".github" / "workflows" / "e023-generality-g1f.yml").exists()

    output = {
        "model_calls": 0,
        "fixture_count": len(fixtures),
        "fixture_classes": sorted(required_classes),
        "contract_rule_fixture_counts": dict(sorted(rule_counts.items())),
        "prompt_output_shape_unchanged": True,
        "internal_storage_label_required_in_user_prose": False,
        "evaluation_clauses_available_to_prompt": False,
        "semantic_calls_authorized": False,
        "g1f_execution_authorized": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }
    print("E023 authority-preserving composition contract validation: PASS")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
