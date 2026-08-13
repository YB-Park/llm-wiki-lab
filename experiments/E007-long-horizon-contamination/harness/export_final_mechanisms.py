#!/usr/bin/env python3
"""Final existing-artifact diagnostics for E007 Family N.

No LLM calls and no run mutation. This exporter separates literal state-anchor coverage
from answer outcomes, measures verifier issue reduction, inspects C4 regression-trigger
state coverage, and characterizes the C4-r01 state-growth outlier without printing wiki
or answer text.

All state coverage measures are diagnostic literal proxies based on preregistered rules;
they are not semantic truth labels.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from answer_contract_a2 import parse_answer_batch_a2
from export_mechanisms import (
    anchor_coverage,
    queries,
    rule_coverage,
    rules,
    score_rows,
    transition_state_text,
    wiki_state,
)
from run_e007 import RUNS

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "run-plan-v0.json"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def coverage_complete(cov: dict[str, Any]) -> bool:
    if cov["signal_hit"] != cov["signal_total"]:
        return False
    if cov["source_hit"] != cov["source_total"]:
        return False
    if cov["any_ok"] is False:
        return False
    return True


def fmt_cov(cov: dict[str, Any]) -> str:
    any_part = "-" if cov["any_ok"] is None else ("Y" if cov["any_ok"] else "N")
    return f"sig={cov['signal_hit']}/{cov['signal_total']},src={cov['source_hit']}/{cov['source_total']},any={any_part}"


def parse_call_answers(run_dir: Path, call_name: str) -> tuple[dict[str, dict[str, Any]], int]:
    path = run_dir / "calls" / call_name / "response.txt"
    if not path.exists():
        return {}, 1
    parsed, violations = parse_answer_batch_a2(path.read_text(encoding="utf-8"))
    return parsed, len(violations)


def issue_count(report: dict[str, Any]) -> int:
    return sum(len(report.get(key, []) or []) for key in (
        "coverage_issues", "preservation_issues", "faithfulness_issues"
    ))


def norm_block(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def structure_metrics(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    nonempty = [line.strip() for line in lines if line.strip()]
    paragraphs = [norm_block(p) for p in re.split(r"\n\s*\n", text) if norm_block(p)]
    headings = [norm_block(line.lstrip("#").strip()) for line in nonempty if line.startswith("#")]
    source_ids = re.findall(r"\bS\d{3}\b", text, flags=re.IGNORECASE)
    unique_paras = len(set(paragraphs))
    return {
        "bytes": len(text.encode("utf-8")),
        "lines": len(lines),
        "nonempty": len(nonempty),
        "paras": len(paragraphs),
        "dup_paras": max(0, len(paragraphs) - unique_paras),
        "unique_para_pct": (100.0 * unique_paras / len(paragraphs)) if paragraphs else 100.0,
        "headings": len(headings),
        "dup_headings": max(0, len(headings) - len(set(headings))),
        "source_mentions": len(source_ids),
        "unique_sources": len(set(v.upper() for v in source_ids)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export final E007 mechanism diagnostics")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    args = parser.parse_args()

    plan = load_json(args.plan, {}) or {}
    qmeta = queries()
    checks = rules()
    entries = plan.get("runs", [])

    print("E007-FINAL-MECHANISM-HANDOFF-v0")
    print(f"runs={len(entries)} model={plan.get('model')}")

    # 1) Literal state-anchor completeness vs deterministic answer outcome.
    print("[ANCHOR-VS-ANSWER] excludes=C0; Q025 reported separately")
    for condition in ("C1", "C2", "C3", "C4"):
        buckets: Counter[str] = Counter()
        complete_fail: list[str] = []
        incomplete_fail: list[str] = []
        q025: list[str] = []
        for entry in entries:
            if entry["condition"] != condition:
                continue
            run_dir = args.run_root / entry["run_id"]
            for qid, rule in checks.items():
                wave = int(qmeta[qid]["ask_after_wave"])
                row = score_rows(run_dir, wave).get(qid)
                if row is None:
                    continue
                state = wiki_state(run_dir, wave)
                cov = rule_coverage(state, rule)
                complete = coverage_complete(cov)
                passed = bool(row.get("passed"))
                key = ("complete" if complete else "incomplete") + ("_pass" if passed else "_fail")
                if qid == "Q025":
                    q025.append(f"{entry['run_id']}:{key}:{fmt_cov(cov)}")
                    continue
                buckets[key] += 1
                if not passed:
                    target = complete_fail if complete else incomplete_fail
                    target.append(f"{entry['run_id']}:{qid}")
        print(
            f"{condition} completePass={buckets['complete_pass']} completeFail={buckets['complete_fail']} "
            f"incompletePass={buckets['incomplete_pass']} incompleteFail={buckets['incomplete_fail']}"
        )
        print(f"  completeFailIDs={','.join(complete_fail) if complete_fail else '-'}")
        print(f"  incompleteFailIDs={','.join(incomplete_fail) if incomplete_fail else '-'}")
        print(f"  Q025={';'.join(q025) if q025 else '-'}")

    # 2) Did verifier issue burden actually decrease after repair?
    print("[VERIFIER-ISSUE-REDUCTION]")
    for condition in ("C3", "C4"):
        agg: Counter[str] = Counter()
        detail: list[str] = []
        for entry in entries:
            if entry["condition"] != condition:
                continue
            run_dir = args.run_root / entry["run_id"]
            summary = load_json(run_dir / "summary.json") or load_json(run_dir / "summary.partial.json", {}) or {}
            for wave_row in summary.get("waves", []):
                transition = wave_row.get("transition") or {}
                if not transition.get("repair_used"):
                    continue
                before = issue_count(transition.get("initial") or {})
                after = issue_count(transition.get("final") or {})
                agg["repairs"] += 1
                agg["before"] += before
                agg["after"] += after
                if after < before:
                    direction = "reduced"
                elif after > before:
                    direction = "increased"
                else:
                    direction = "same"
                agg[direction] += 1
                if (transition.get("final") or {}).get("decision") == "revise":
                    agg["final_revise"] += 1
                detail.append(
                    f"{entry['run_id']}:W{wave_row['wave']}:{before}->{after}:{direction}:"
                    f"{(transition.get('final') or {}).get('decision','?')}"
                )
        print(
            f"{condition} repairs={agg['repairs']} issues={agg['before']}->{agg['after']} "
            f"reduced={agg['reduced']} same={agg['same']} increased={agg['increased']} finalRev={agg['final_revise']}"
        )
        print("  " + (" ".join(detail) if detail else "-"))

    # 3) Inspect whether each C4 regression trigger reflected missing literal state anchors.
    print("[C4-REGRESSION-TRIGGER-STATE]")
    for entry in entries:
        if entry["condition"] != "C4":
            continue
        run_dir = args.run_root / entry["run_id"]
        summary = load_json(run_dir / "summary.json") or load_json(run_dir / "summary.partial.json", {}) or {}
        for wave_row in summary.get("waves", []):
            if not wave_row.get("regression_repair_used"):
                continue
            wave = int(wave_row["wave"])
            before_rows = score_rows(run_dir, wave, "regression-before")
            failed = sorted(qid for qid, row in before_rows.items() if not row.get("passed"))
            transition = wave_row.get("transition") or {}
            pre_state = transition_state_text(run_dir, wave, bool(transition.get("repair_used"))) or ""
            post_path = run_dir / "calls" / f"W{wave:02d}-regression-repair" / "response.txt"
            post_state = post_path.read_text(encoding="utf-8") if post_path.exists() else ""
            before_answers, before_viol = parse_call_answers(run_dir, f"W{wave:02d}-regression-before")
            after_answers, after_viol = parse_call_answers(run_dir, f"W{wave:02d}-regression-after")
            for qid in failed:
                pre_cov = rule_coverage(pre_state, checks[qid])
                post_cov = rule_coverage(post_state, checks[qid])
                ba = before_answers.get(qid) or {}
                aa = after_answers.get(qid) or {}
                print(
                    f"{entry['run_id']} W{wave} trigger={qid} suspectQ025={int(qid=='Q025')} "
                    f"pre={fmt_cov(pre_cov)} post={fmt_cov(post_cov)} "
                    f"beforeSrc={','.join(ba.get('source_ids',[])) or '-'} beforeUnc={ba.get('uncertainty','MISSING')} "
                    f"afterSrc={','.join(aa.get('source_ids',[])) or '-'} afterUnc={aa.get('uncertainty','MISSING')} "
                    f"contract={before_viol}->{after_viol}"
                )

    # 4) Characterize the C4-r01 growth path without exposing text.
    print("[C4-R01-STRUCTURE-GROWTH]")
    run_dir = args.run_root / "C4-r01"
    previous_bytes: int | None = None
    for wave in range(int(plan.get("max_wave", 5)) + 1):
        state = wiki_state(run_dir, wave)
        if state is None:
            continue
        m = structure_metrics(state)
        anchors = anchor_coverage(state, wave, qmeta, checks)
        delta = m["bytes"] - previous_bytes if previous_bytes is not None else 0
        density = (1000.0 * anchors[0] / m["bytes"]) if m["bytes"] else 0.0
        print(
            f"W{wave} bytes={m['bytes']} delta={delta:+d} lines={m['lines']} paras={m['paras']} "
            f"dupParas={m['dup_paras']} uniqueParaPct={m['unique_para_pct']:.1f} "
            f"headings={m['headings']} dupHeadings={m['dup_headings']} "
            f"srcMentions={m['source_mentions']} uniqueSrc={m['unique_sources']} "
            f"anchors={anchors[0]}/{anchors[1]} anchorPerKB={density:.2f}"
        )
        previous_bytes = m["bytes"]


if __name__ == "__main__":
    main()
