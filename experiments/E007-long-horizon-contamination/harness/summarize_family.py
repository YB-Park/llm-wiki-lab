#!/usr/bin/env python3
"""Create a compact cross-run E007 Family N summary for manual transfer.

The output is intentionally small enough for a screenshot or short transcription in a
restricted-network environment. It summarizes sanitized run artifacts only; raw wiki
states, prompts, answers, and telemetry remain local.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from run_e007 import RUNS

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "run-plan-v0.json"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float | int | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    value = float(value)
    if value.is_integer():
        return str(int(value))
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def condition_summary(condition: str, run_dirs: list[Path]) -> dict[str, Any]:
    handoffs = [load_json(run_dir / "handoff.json", {}) or {} for run_dir in run_dirs]
    costs = [load_json(run_dir / "cost-metrics.json", {}) or {} for run_dir in run_dirs]
    semantics = [load_json(run_dir / "evaluation" / "semantic-summary.json") for run_dir in run_dirs]

    deterministic_passes = [int(h["deterministic"]["passed_count"]) for h in handoffs]
    deterministic_scored = [int(h["deterministic"]["scored_count"]) for h in handoffs]
    failed_counter: Counter[str] = Counter()
    for handoff in handoffs:
        failed_counter.update(handoff["deterministic"]["failed_query_ids"])

    input_tokens = [float(h["telemetry"]["totals"]["gen_ai.usage.input_tokens"]) for h in handoffs]
    calls = [int(h["telemetry"]["call_count"]) for h in handoffs]
    prompt_bytes = [int(h["telemetry"]["payload"]["prompt_utf8_bytes"]) for h in handoffs]

    maintenance_input = [
        float(c.get("headline_split", {}).get("maintenance_input_tokens", 0)) for c in costs
    ]
    answer_input = [
        float(c.get("headline_split", {}).get("primary_answer_input_tokens", 0)) for c in costs
    ]

    ratios = [
        h.get("structure", {}).get("final_wiki_to_raw_byte_ratio")
        for h in handoffs
        if h.get("structure", {}).get("final_wiki_to_raw_byte_ratio") is not None
    ]
    churn = [
        h.get("structure", {}).get("cumulative_changed_lines")
        for h in handoffs
        if h.get("structure", {}).get("cumulative_changed_lines") is not None
    ]

    transition_repairs = sum(int(h["guards"]["transition_repairs"]) for h in handoffs)
    transition_flags = sum(int(h["guards"]["transition_final_flags"]) for h in handoffs)
    regression_repairs = sum(int(h["guards"]["regression_repairs"]) for h in handoffs)

    semantic_available = [s for s in semantics if s is not None]
    semantic_mean = (
        mean(float(s["mean_correctness_across_passes"]) for s in semantic_available)
        if semantic_available
        else None
    )
    semantic_major_disagreements = sum(
        len(s.get("major_disagreement_query_ids", [])) for s in semantic_available
    )
    semantic_human_audits = sum(
        len(s.get("needs_human_audit_query_ids", [])) for s in semantic_available
    )

    return {
        "condition": condition,
        "runs": len(run_dirs),
        "det_passes": deterministic_passes,
        "det_scored": deterministic_scored,
        "det_pass_total": sum(deterministic_passes),
        "det_scored_total": sum(deterministic_scored),
        "failed_counter": failed_counter,
        "mean_input_tokens": mean(input_tokens),
        "mean_calls": mean(calls),
        "mean_prompt_bytes": mean(prompt_bytes),
        "mean_maintenance_input_tokens": mean(maintenance_input),
        "mean_answer_input_tokens": mean(answer_input),
        "mean_state_ratio": mean(float(v) for v in ratios) if ratios else None,
        "mean_churn_lines": mean(float(v) for v in churn) if churn else None,
        "transition_repairs": transition_repairs,
        "transition_flags": transition_flags,
        "regression_repairs": regression_repairs,
        "semantic_runs": len(semantic_available),
        "semantic_mean": semantic_mean,
        "semantic_major_disagreements": semantic_major_disagreements,
        "semantic_human_audits": semantic_human_audits,
    }


def family_fingerprint(run_dirs: list[Path]) -> str:
    digest = hashlib.sha256()
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        for relative in ("handoff.json", "cost-metrics.json", "structural-metrics.json"):
            path = run_dir / relative
            if path.exists():
                digest.update(run_dir.name.encode("utf-8"))
                digest.update(relative.encode("utf-8"))
                digest.update(path.read_bytes())
        semantic = run_dir / "evaluation" / "semantic-summary.json"
        if semantic.exists():
            digest.update(run_dir.name.encode("utf-8"))
            digest.update(b"semantic-summary.json")
            digest.update(semantic.read_bytes())
    return digest.hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize E007 Family N runs compactly")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    plan = load_json(args.plan)
    planned = [args.run_root / row["run_id"] for row in plan["runs"]]
    complete = [run_dir for run_dir in planned if (run_dir / "handoff.json").exists()]
    missing = [run_dir.name for run_dir in planned if run_dir not in complete]

    if missing and not args.allow_partial:
        raise SystemExit(
            "Family block is incomplete. Missing handoffs: " + ",".join(missing) +
            ". Use --allow-partial only for infrastructure inspection, not headline analysis."
        )

    by_condition: dict[str, list[Path]] = defaultdict(list)
    for run_dir in complete:
        handoff = load_json(run_dir / "handoff.json", {}) or {}
        by_condition[str(handoff.get("condition", "?"))].append(run_dir)

    print("E007-FAMILY-HANDOFF-v0")
    print(f"complete={len(complete)}/{len(planned)} model={plan['model']} fingerprint={family_fingerprint(complete)}")
    if missing:
        print(f"missing={','.join(missing)}")

    for condition in plan["conditions"]:
        run_dirs = sorted(by_condition.get(condition, []), key=lambda p: p.name)
        if not run_dirs:
            print(f"{condition} runs=0")
            continue
        s = condition_summary(condition, run_dirs)
        det_runs = ",".join(str(v) for v in s["det_passes"])
        print(
            f"{condition} runs={s['runs']} det={s['det_pass_total']}/{s['det_scored_total']} "
            f"perRun={det_runs} inMean={fmt(s['mean_input_tokens'])} "
            f"maintIn={fmt(s['mean_maintenance_input_tokens'])} ansIn={fmt(s['mean_answer_input_tokens'])} "
            f"calls={fmt(s['mean_calls'])} stateRatio={fmt(s['mean_state_ratio'])} churn={fmt(s['mean_churn_lines'])}"
        )
        failures = ",".join(f"{qid}x{count}" for qid, count in sorted(s["failed_counter"].items())) or "-"
        semantic = (
            f"{fmt(s['semantic_mean'])}/{s['semantic_runs']}runs"
            if s["semantic_runs"]
            else "pending"
        )
        print(
            f"  fail={failures} guards=tRepair:{s['transition_repairs']} tFlag:{s['transition_flags']} "
            f"rRepair:{s['regression_repairs']} semantic={semantic} "
            f"semDisagree:{s['semantic_major_disagreements']} audit:{s['semantic_human_audits']}"
        )


if __name__ == "__main__":
    main()
