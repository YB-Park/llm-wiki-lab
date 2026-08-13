#!/usr/bin/env python3
"""Export sanitized query/run/guard forensics for E007 Family N.

This script is intentionally reporting-only. It does not call an LLM, modify run artifacts,
or inspect raw source/wiki text. It reads scored/summary artifacts and prints a compact
handoff suitable for manual transfer from a restricted network.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from run_e007 import RUNS

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "run-plan-v0.json"
CORPUS = ROOT / "corpus"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def query_metadata() -> dict[str, dict[str, Any]]:
    doc = load_json(CORPUS / "queries.json", {}) or {}
    return {q["query_id"]: q for q in doc.get("queries", [])}


def primary_det_scores(run_dir: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((run_dir / "scores").glob("W*-primary-deterministic.json")):
        payload = load_json(path, {}) or {}
        for row in payload.get("scores", []):
            rows[str(row["query_id"])] = {
                "passed": bool(row.get("passed")),
                "failures": list(row.get("failures", [])),
                "wave_file": path.name,
            }
    return rows


def semantic_rows(run_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    summary = load_json(run_dir / "evaluation" / "semantic-summary.json", {}) or {}
    rows = {str(item["query_id"]): item for item in summary.get("items", [])}
    meta = {
        "invalid": int(summary.get("invalid_or_incomplete_item_count", 0) or 0),
        "fully_valid": int(summary.get("fully_valid_item_count", 0) or 0),
        "contract_violations": sum(
            len(v) for v in summary.get("evaluator_contract_violations", []) if isinstance(v, list)
        ),
    }
    return rows, meta


def run_guard_forensics(run_dir: Path) -> dict[str, Any]:
    summary = load_json(run_dir / "summary.json") or load_json(run_dir / "summary.partial.json", {}) or {}
    transition_repairs = 0
    transition_initial_revise = 0
    transition_final_revise = 0
    transition_issue_counts = Counter()
    regression_events: list[dict[str, Any]] = []

    for wave in summary.get("waves", []):
        transition = wave.get("transition") or {}
        if transition:
            initial = transition.get("initial") or {}
            final = transition.get("final") or {}
            if initial.get("decision") == "revise":
                transition_initial_revise += 1
            if transition.get("repair_used"):
                transition_repairs += 1
            if final.get("decision") == "revise":
                transition_final_revise += 1
            for key in ("coverage_issues", "preservation_issues", "faithfulness_issues"):
                transition_issue_counts[key] += len(initial.get(key, []) or [])

        if "regression_before" in wave:
            before = wave.get("regression_before") or {}
            after = wave.get("regression_after") or {}
            regression_events.append(
                {
                    "wave": wave.get("wave"),
                    "before_failed": int(before.get("failed", 0) or 0),
                    "repair_used": bool(wave.get("regression_repair_used", False)),
                    "after_failed": int(after.get("failed", before.get("failed", 0)) or 0),
                }
            )

    regression_triggered = sum(1 for row in regression_events if row["before_failed"] > 0)
    regression_repairs = sum(1 for row in regression_events if row["repair_used"])
    regression_failures_before = sum(row["before_failed"] for row in regression_events)
    regression_failures_after = sum(row["after_failed"] for row in regression_events if row["repair_used"])

    return {
        "transition_repairs": transition_repairs,
        "transition_initial_revise": transition_initial_revise,
        "transition_final_revise": transition_final_revise,
        "transition_issue_counts": dict(transition_issue_counts),
        "regression_checks": len(regression_events),
        "regression_triggered": regression_triggered,
        "regression_repairs": regression_repairs,
        "regression_failures_before": regression_failures_before,
        "regression_failures_after_after_repair": regression_failures_after,
    }


def fmt(x: float | None, digits: int = 3) -> str:
    if x is None:
        return "n/a"
    if float(x).is_integer():
        return str(int(x))
    return f"{x:.{digits}f}".rstrip("0").rstrip(".")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export E007 sanitized forensic handoff")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    args = parser.parse_args()

    plan = load_json(args.plan)
    qmeta = query_metadata()
    runs = []
    for entry in plan["runs"]:
        run_dir = args.run_root / entry["run_id"]
        if not (run_dir / "handoff.json").exists():
            raise SystemExit(f"missing completed run: {entry['run_id']}")
        det = primary_det_scores(run_dir)
        sem, sem_meta = semantic_rows(run_dir)
        guards = run_guard_forensics(run_dir)
        handoff = load_json(run_dir / "handoff.json", {}) or {}
        structure = handoff.get("structure", {}) or {}
        runs.append(
            {
                "run_id": entry["run_id"],
                "condition": entry["condition"],
                "det": det,
                "sem": sem,
                "sem_meta": sem_meta,
                "guards": guards,
                "state_ratio": structure.get("final_wiki_to_raw_byte_ratio"),
                "churn": structure.get("cumulative_changed_lines"),
            }
        )

    print("E007-FORENSICS-HANDOFF-v0")
    print(f"runs={len(runs)}/{len(plan['runs'])} model={plan['model']}")

    # 1) Query-by-condition deterministic failure matrix.
    det_qids = sorted({qid for run in runs for qid in run["det"]})
    print("[DET-FAIL-MATRIX] count_failed_runs/3")
    for qid in det_qids:
        cells = []
        total = 0
        for condition in plan["conditions"]:
            condition_runs = [r for r in runs if r["condition"] == condition]
            failures = sum(1 for r in condition_runs if qid in r["det"] and not r["det"][qid]["passed"])
            total += failures
            cells.append(f"{condition}:{failures}")
        if total:
            qclass = qmeta.get(qid, {}).get("class", "?")
            wave = qmeta.get(qid, {}).get("ask_after_wave", "?")
            print(f"{qid} class={qclass} wave={wave} " + " ".join(cells) + f" total={total}/15")

    # 2) Failure reasons, sanitized (rules/signals only, no raw answers).
    print("[DET-FAIL-REASONS]")
    reason_counter: dict[str, Counter[str]] = defaultdict(Counter)
    for run in runs:
        for qid, row in run["det"].items():
            if not row["passed"]:
                for reason in row["failures"]:
                    reason_counter[qid][reason] += 1
    for qid in sorted(reason_counter):
        reasons = "; ".join(f"{reason} x{count}" for reason, count in reason_counter[qid].most_common())
        print(f"{qid}: {reasons}")

    # 3) Semantic validity and correctness by condition/query.
    print("[SEMANTIC-BY-CONDITION]")
    semantic_qids = sorted({qid for run in runs for qid in run["sem"]})
    for condition in plan["conditions"]:
        condition_runs = [r for r in runs if r["condition"] == condition]
        invalid = sum(r["sem_meta"]["invalid"] for r in condition_runs)
        contract = sum(r["sem_meta"]["contract_violations"] for r in condition_runs)
        cells = []
        for qid in semantic_qids:
            vals = []
            invalid_count = 0
            for r in condition_runs:
                row = r["sem"].get(qid)
                if not row:
                    continue
                if row.get("automatic_semantic_result") != "valid":
                    invalid_count += 1
                    continue
                if row.get("correctness_mean") is not None:
                    vals.append(float(row["correctness_mean"]))
            if vals or invalid_count:
                cell = f"{qid}={fmt(mean(vals)) if vals else 'n/a'}"
                if invalid_count:
                    cell += f"(inv{invalid_count})"
                cells.append(cell)
        print(f"{condition} invalid={invalid} evalContract={contract} " + " ".join(cells))

    # 4) Guard/intervention yield.
    print("[GUARD-YIELD]")
    for condition in ("C3", "C4"):
        condition_runs = [r for r in runs if r["condition"] == condition]
        if not condition_runs:
            continue
        tr = sum(r["guards"]["transition_repairs"] for r in condition_runs)
        init_rev = sum(r["guards"]["transition_initial_revise"] for r in condition_runs)
        final_rev = sum(r["guards"]["transition_final_revise"] for r in condition_runs)
        coverage = sum(r["guards"]["transition_issue_counts"].get("coverage_issues", 0) for r in condition_runs)
        preservation = sum(r["guards"]["transition_issue_counts"].get("preservation_issues", 0) for r in condition_runs)
        faith = sum(r["guards"]["transition_issue_counts"].get("faithfulness_issues", 0) for r in condition_runs)
        reg_checks = sum(r["guards"]["regression_checks"] for r in condition_runs)
        reg_trig = sum(r["guards"]["regression_triggered"] for r in condition_runs)
        reg_rep = sum(r["guards"]["regression_repairs"] for r in condition_runs)
        reg_before = sum(r["guards"]["regression_failures_before"] for r in condition_runs)
        reg_after = sum(r["guards"]["regression_failures_after_after_repair"] for r in condition_runs)
        print(
            f"{condition} transition initialRev={init_rev} repairs={tr} finalRev={final_rev} "
            f"issues=cov:{coverage},pres:{preservation},faith:{faith} "
            f"regression checks={reg_checks} triggered={reg_trig} repairs={reg_rep} failBefore={reg_before} failAfterRepair={reg_after}"
        )

    # 5) Run-level dispersion/state cost for spotting outliers without raw content.
    print("[RUN-DISPERSION]")
    for condition in plan["conditions"]:
        condition_runs = sorted((r for r in runs if r["condition"] == condition), key=lambda r: r["run_id"])
        chunks = []
        for r in condition_runs:
            det_pass = sum(1 for row in r["det"].values() if row["passed"])
            det_total = len(r["det"])
            sem_valid = [
                float(row["correctness_mean"])
                for row in r["sem"].values()
                if row.get("automatic_semantic_result") == "valid" and row.get("correctness_mean") is not None
            ]
            sem_inv = sum(1 for row in r["sem"].values() if row.get("automatic_semantic_result") != "valid")
            chunks.append(
                f"{r['run_id']} det={det_pass}/{det_total} sem={fmt(mean(sem_valid)) if sem_valid else 'n/a'} inv={sem_inv} "
                f"ratio={fmt(float(r['state_ratio'])) if r['state_ratio'] is not None else 'n/a'} churn={r['churn'] if r['churn'] is not None else 'n/a'}"
            )
        print(condition + " | " + " | ".join(chunks))


if __name__ == "__main__":
    main()
