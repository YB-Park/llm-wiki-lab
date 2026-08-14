from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from generate_corpus import build_corpus, canonical_json, corpus_sha256
from provenance_v0 import (
    CONDITIONS,
    audit_claim,
    build_condition,
    d1_reattachment_actions,
    exact_raw_reversible,
    ownership_exact,
    serialized_metadata_bytes,
    w1_stale_refs_before_repair,
    w1_update_actions,
)

PRIMARY_BUDGET = 1200
SENSITIVITY_BUDGETS = (600, 2400)
BOOTSTRAP_REPS = 20000
BOOTSTRAP_SEED = 20260831
CRITICAL_FAMILIES = {
    "wrong_value",
    "wrong_source",
    "derived_only",
    "within_source_conflict",
    "multi_source_misownership",
}


def _claim_row(topic: dict, claim: dict, condition: str, state: dict, budget: int) -> dict:
    audit = audit_claim(topic, claim, state, budget=budget)
    clean_false_accusation = int(
        claim["fault_family"] == "clean"
        and audit["outcome"] in {"invalid_or_unsupported", "contested"}
    )
    return {
        "topic_id": topic["topic_id"],
        "claim_id": claim["claim_id"],
        "section_id": claim["section_id"],
        "condition": condition,
        "budget": budget,
        "risk": claim["risk"],
        "fault_family": claim["fault_family"],
        "critical": claim["fault_family"] in CRITICAL_FAMILIES,
        "gold_outcome": claim["gold_outcome"],
        "audit_outcome": audit["outcome"],
        "audit_correct": float(audit["outcome"] == claim["gold_outcome"]),
        "ownership_exact": ownership_exact(topic, claim, state),
        "clean_false_accusation": float(clean_false_accusation),
        "conflict_detected": float(
            claim["fault_family"] == "within_source_conflict"
            and audit["outcome"] == "contested"
        ),
        "derived_only_accepted": float(
            claim["fault_family"] == "derived_only"
            and audit["outcome"] == "verified"
        ),
        "inspected_chars": audit["inspected_chars"],
        "visited_sources": audit["visited_sources"],
        "visited_units": audit["visited_units"],
    }


def _rows_for(corpus: dict) -> tuple[list[dict], dict]:
    rows = []
    condition_costs = {
        condition: {
            "metadata_bytes": 0,
            "w1_update_actions": 0,
            "w1_stale_refs_before_repair": 0,
            "d1_reattachment_actions": 0,
            "raw_reversible": True,
        }
        for condition in CONDITIONS
    }

    for topic in corpus["topics"]:
        for condition in CONDITIONS:
            state = build_condition(topic, condition, "W0")
            cost = condition_costs[condition]
            cost["metadata_bytes"] += serialized_metadata_bytes(state)
            cost["w1_update_actions"] += w1_update_actions(topic, condition)
            cost["w1_stale_refs_before_repair"] += w1_stale_refs_before_repair(topic, condition)
            cost["d1_reattachment_actions"] += d1_reattachment_actions(topic, condition)
            cost["raw_reversible"] = cost["raw_reversible"] and exact_raw_reversible(topic, state)
            for claim in topic["claims"]:
                rows.append(_claim_row(topic, claim, condition, state, PRIMARY_BUDGET))
                for budget in SENSITIVITY_BUDGETS:
                    rows.append(_claim_row(topic, claim, condition, state, budget))
    return rows, condition_costs


def _filter_rows(
    rows: list[dict],
    *,
    condition: str,
    budget: int = PRIMARY_BUDGET,
    critical: bool | None = None,
    risk: str | None = None,
    family: str | None = None,
) -> list[dict]:
    out = []
    for row in rows:
        if row["condition"] != condition or row["budget"] != budget:
            continue
        if critical is not None and row["critical"] != critical:
            continue
        if risk is not None and row["risk"] != risk:
            continue
        if family is not None and row["fault_family"] != family:
            continue
        out.append(row)
    return out


def _topic_means(rows: list[dict], metric: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["topic_id"]].append(float(row[metric]))
    return {topic: statistics.mean(values) for topic, values in grouped.items()}


def paired_bootstrap(
    rows: list[dict],
    left: str,
    right: str,
    metric: str,
    *,
    critical: bool | None = None,
    risk: str | None = None,
    family: str | None = None,
) -> dict:
    a = _topic_means(
        _filter_rows(rows, condition=left, critical=critical, risk=risk, family=family), metric
    )
    b = _topic_means(
        _filter_rows(rows, condition=right, critical=critical, risk=risk, family=family), metric
    )
    topics = sorted(set(a) & set(b))
    if not topics:
        raise RuntimeError(f"no_paired_topics:{left}:{right}:{metric}")
    diffs = [b[topic] - a[topic] for topic in topics]
    point = statistics.mean(diffs)
    rng = random.Random(BOOTSTRAP_SEED)
    reps = []
    for _ in range(BOOTSTRAP_REPS):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        reps.append(statistics.mean(sample))
    reps.sort()
    lo = reps[int(0.025 * BOOTSTRAP_REPS)]
    hi = reps[min(BOOTSTRAP_REPS - 1, int(0.975 * BOOTSTRAP_REPS))]
    return {"topics": len(topics), "difference": point, "ci95": [lo, hi]}


def mean_metric(
    rows: list[dict],
    condition: str,
    metric: str,
    *,
    budget: int = PRIMARY_BUDGET,
    critical: bool | None = None,
    risk: str | None = None,
    family: str | None = None,
) -> float:
    selected = _filter_rows(
        rows,
        condition=condition,
        budget=budget,
        critical=critical,
        risk=risk,
        family=family,
    )
    if not selected:
        return 0.0
    return statistics.mean(float(row[metric]) for row in selected)


def _frontier(means: dict, costs: dict) -> list[str]:
    # High audit/ownership and low chars/metadata/update cost. A condition is
    # dominated only when another is no worse on every dimension and strictly
    # better on at least one. This is descriptive; it does not replace gates.
    dims = {}
    for condition in CONDITIONS:
        dims[condition] = (
            means[condition]["critical_accuracy"],
            means[condition]["ownership_exact"],
            -means[condition]["critical_inspected_chars"],
            -costs[condition]["metadata_bytes"],
            -costs[condition]["w1_update_actions"],
        )
    frontier = []
    for candidate in CONDITIONS:
        dominated = False
        for other in CONDITIONS:
            if other == candidate:
                continue
            no_worse = all(a >= b for a, b in zip(dims[other], dims[candidate]))
            strictly = any(a > b for a, b in zip(dims[other], dims[candidate]))
            if no_worse and strictly:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate)
    return frontier


def analyze() -> dict:
    corpus = build_corpus()
    before = corpus_sha256(corpus)
    before_json = canonical_json(corpus)
    rows, costs = _rows_for(corpus)
    after = corpus_sha256(corpus)
    after_json = canonical_json(corpus)
    corpus_unchanged = before == after and before_json == after_json

    means = {}
    for condition in CONDITIONS:
        means[condition] = {
            "critical_accuracy": mean_metric(rows, condition, "audit_correct", critical=True),
            "all_accuracy": mean_metric(rows, condition, "audit_correct"),
            "ownership_exact": mean_metric(rows, condition, "ownership_exact"),
            "critical_inspected_chars": mean_metric(rows, condition, "inspected_chars", critical=True),
            "clean_false_accusation": mean_metric(rows, condition, "clean_false_accusation", family="clean"),
            "conflict_detection": mean_metric(rows, condition, "conflict_detected", family="within_source_conflict"),
            "derived_only_acceptance": mean_metric(rows, condition, "derived_only_accepted", family="derived_only"),
            "high_risk_accuracy": mean_metric(rows, condition, "audit_correct", risk="high"),
            "low_risk_accuracy": mean_metric(rows, condition, "audit_correct", risk="low"),
            "high_risk_ownership": mean_metric(rows, condition, "ownership_exact", risk="high"),
            "high_risk_conflict": mean_metric(rows, condition, "conflict_detected", risk="high", family="within_source_conflict"),
        }

    critical_accuracy = paired_bootstrap(rows, "P1", "P2", "audit_correct", critical=True)
    ownership = paired_bootstrap(rows, "P1", "P2", "ownership_exact")

    p1_chars = means["P1"]["critical_inspected_chars"]
    p2_chars = means["P2"]["critical_inspected_chars"]
    char_ratio = p2_chars / p1_chars if p1_chars else float("inf")

    gate_a_checks = {
        "p2_p1_critical_accuracy_gain_ge_0_15": critical_accuracy["difference"] >= 0.15,
        "p2_p1_critical_accuracy_ci_lower_gt_0": critical_accuracy["ci95"][0] > 0.0,
        "p2_p1_ownership_gain_ge_0_20": ownership["difference"] >= 0.20,
        "p2_p1_ownership_ci_lower_gt_0": ownership["ci95"][0] > 0.0,
        "p2_critical_chars_le_0_65_p1": char_ratio <= 0.65,
        "p2_clean_false_accusation_no_worse_0_02": means["P2"]["clean_false_accusation"] <= means["P1"]["clean_false_accusation"] + 0.02,
        "p2_conflict_detection_no_worse_0_05": means["P2"]["conflict_detection"] >= means["P1"]["conflict_detection"] - 0.05,
        "p2_raw_span_reversibility_100pct": bool(costs["P2"]["raw_reversible"]),
        "p2_derived_only_acceptance_zero": means["P2"]["derived_only_acceptance"] == 0.0,
        "scoring_is_read_only": corpus_unchanged,
    }
    gate_a = "SURVIVES_E004_PRECISE_GATE" if all(gate_a_checks.values()) else "DOES_NOT_SURVIVE_E004_PRECISE_GATE"

    p3_p2_high_accuracy = means["P3"]["high_risk_accuracy"] - means["P2"]["high_risk_accuracy"]
    p3_p2_high_ownership = means["P3"]["high_risk_ownership"] - means["P2"]["high_risk_ownership"]
    p3_p2_high_conflict = means["P3"]["high_risk_conflict"] - means["P2"]["high_risk_conflict"]
    p2_metadata = costs["P2"]["metadata_bytes"]
    p2_updates = costs["P2"]["w1_update_actions"]
    gate_b_checks = {
        "p3_high_accuracy_within_0_03_p2": p3_p2_high_accuracy >= -0.03,
        "p3_high_ownership_within_0_03_p2": p3_p2_high_ownership >= -0.03,
        "p3_high_conflict_within_0_03_p2": p3_p2_high_conflict >= -0.03,
        "p3_metadata_le_0_75_p2": costs["P3"]["metadata_bytes"] <= 0.75 * p2_metadata,
        "p3_w1_updates_le_0_80_p2": costs["P3"]["w1_update_actions"] <= 0.80 * p2_updates,
        "p3_clean_false_accusation_no_worse_0_02": means["P3"]["clean_false_accusation"] <= means["P2"]["clean_false_accusation"] + 0.02,
        "p3_precise_raw_span_reversibility_100pct": bool(costs["P3"]["raw_reversible"]),
        "p3_derived_only_acceptance_zero": means["P3"]["derived_only_acceptance"] == 0.0,
    }
    gate_b = (
        "SELECTIVE_PRECISION_SURVIVES_E004_V0"
        if gate_a == "SURVIVES_E004_PRECISE_GATE" and all(gate_b_checks.values())
        else "SELECTIVE_PRECISION_NOT_ESTABLISHED_E004_V0"
    )

    sensitivity = {}
    for budget in SENSITIVITY_BUDGETS:
        sensitivity[str(budget)] = {
            condition: {
                "critical_accuracy": mean_metric(rows, condition, "audit_correct", budget=budget, critical=True),
                "critical_inspected_chars": mean_metric(rows, condition, "inspected_chars", budget=budget, critical=True),
            }
            for condition in CONDITIONS
        }

    fault_slices = {
        family: {
            condition: {
                "accuracy": mean_metric(rows, condition, "audit_correct", family=family),
                "ownership": mean_metric(rows, condition, "ownership_exact", family=family),
                "chars": mean_metric(rows, condition, "inspected_chars", family=family),
            }
            for condition in CONDITIONS
        }
        for family in sorted({row["fault_family"] for row in rows})
    }

    summary = {
        "format": "llm-wiki-e004-provenance-results-v0",
        "model_calls": 0,
        "ai_credits": 0,
        "corpus_sha256": before,
        "topic_count": corpus["topic_count"],
        "claim_count": corpus["claim_count"],
        "primary_budget": PRIMARY_BUDGET,
        "conditions": list(CONDITIONS),
        "means": means,
        "costs": costs,
        "primary_paired": {
            "p2_minus_p1_critical_accuracy": critical_accuracy,
            "p2_minus_p1_exact_ownership": ownership,
            "p2_p1_critical_char_ratio": char_ratio,
        },
        "gate_a_checks": gate_a_checks,
        "gate_a": gate_a,
        "gate_b_checks": gate_b_checks,
        "gate_b": gate_b,
        "sensitivity": sensitivity,
        "fault_slices": fault_slices,
        "frontier": _frontier(means, costs),
        "corpus_unchanged": corpus_unchanged,
        "cautions": [
            "fresh synthetic mechanism corpus with structured benchmark claim atoms",
            "oracle lower bounds for W1/D1 provenance maintenance actions",
            "no model generation or answer quality measured",
            "no human verification-time study",
            "P3 risk labels are fixture metadata rather than an evaluated classifier",
            "a positive result cannot justify a global claim graph",
        ],
    }
    return {"summary": summary, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    s = result["summary"]
    print("E004-PROVENANCE-HANDOFF-v0")
    print(
        f"modelCalls=0 aiCredits=0 topics={s['topic_count']} claims={s['claim_count']} "
        f"corpusSha={s['corpus_sha256']} budget={s['primary_budget']}"
    )
    for condition in CONDITIONS:
        m = s["means"][condition]
        c = s["costs"][condition]
        print(
            f"{condition} criticalAcc={m['critical_accuracy']:.3f} ownership={m['ownership_exact']:.3f} "
            f"criticalChars={m['critical_inspected_chars']:.1f} cleanFalse={m['clean_false_accusation']:.3f} "
            f"conflict={m['conflict_detection']:.3f} metadataBytes={c['metadata_bytes']} "
            f"w1Updates={c['w1_update_actions']} d1Actions={c['d1_reattachment_actions']}"
        )
    a = s["primary_paired"]["p2_minus_p1_critical_accuracy"]
    o = s["primary_paired"]["p2_minus_p1_exact_ownership"]
    print(f"paired P2-P1 criticalAcc={a['difference']:+.3f}[{a['ci95'][0]:+.3f},{a['ci95'][1]:+.3f}]")
    print(f"paired P2-P1 ownership={o['difference']:+.3f}[{o['ci95'][0]:+.3f},{o['ci95'][1]:+.3f}]")
    print(f"gateA={s['gate_a']} gateB={s['gate_b']} frontier={','.join(s['frontier'])}")
    print("freeform=none modelCalls=0 aiCredits=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
