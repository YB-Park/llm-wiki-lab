#!/usr/bin/env python3
"""Export mechanism-level diagnostics from completed E007 artifacts only.

No LLM calls. No run mutation. No raw answer/wiki text is printed. The exporter reports
only query IDs, source IDs, literal-rule coverage counts, verifier decisions, state sizes,
and regression score transitions so a restricted-network run can be inspected safely.

This is a post-hoc diagnostic aid, not a replacement scorer. In particular, `anchors`
means literal coverage of preregistered deterministic rule signals/source IDs in a wiki
artifact; it is not a semantic quality score.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from answer_contract_a2 import parse_answer_batch_a2
from score_deterministic import contains_signal
from run_e007 import RUNS

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
DEFAULT_PLAN = ROOT / "run-plan-v0.json"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def rules() -> dict[str, dict[str, Any]]:
    return (load_json(CORPUS / "deterministic-checks.json", {}) or {}).get("checks", {})


def queries() -> dict[str, dict[str, Any]]:
    return {q["query_id"]: q for q in (load_json(CORPUS / "queries.json", {}) or {}).get("queries", [])}


def primary_answers(run_dir: Path, wave: int) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    path = run_dir / "calls" / f"W{wave:02d}-primary" / "response.txt"
    if not path.exists():
        return {}, [{"reason": "missing_response_file"}]
    return parse_answer_batch_a2(path.read_text(encoding="utf-8"))


def score_rows(run_dir: Path, wave: int, kind: str = "primary-deterministic") -> dict[str, dict[str, Any]]:
    path = run_dir / "scores" / f"W{wave:02d}-{kind}.json"
    payload = load_json(path, {}) or {}
    return {str(row["query_id"]): row for row in payload.get("scores", [])}


def wiki_state(run_dir: Path, wave: int) -> str | None:
    path = run_dir / "states" / f"W{wave:02d}-wiki.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def source_id_present(text: str, source_id: str) -> bool:
    # C2+ prompts ask for compact forms such as [S007]. Be slightly tolerant to bare IDs.
    return source_id.casefold() in text.casefold()


def rule_coverage(text: str | None, rule: dict[str, Any]) -> dict[str, Any]:
    if text is None:
        return {"signal_hit": 0, "signal_total": 0, "source_hit": 0, "source_total": 0, "any_ok": None}
    all_signals = list(rule.get("answer_all", []))
    req_sources = [str(v) for v in rule.get("required_source_ids", [])]
    any_signals = list(rule.get("answer_any", []))
    return {
        "signal_hit": sum(contains_signal(text, s) for s in all_signals),
        "signal_total": len(all_signals),
        "source_hit": sum(source_id_present(text, sid) for sid in req_sources),
        "source_total": len(req_sources),
        "any_ok": (any(contains_signal(text, s) for s in any_signals) if any_signals else None),
    }


def anchor_coverage(text: str, wave: int, qmeta: dict[str, dict[str, Any]], checks: dict[str, dict[str, Any]]) -> tuple[int, int]:
    hit = 0
    total = 0
    for qid, rule in checks.items():
        if int(qmeta.get(qid, {}).get("ask_after_wave", 99)) > wave:
            continue
        for signal in rule.get("answer_all", []):
            total += 1
            hit += int(contains_signal(text, signal))
        for sid in rule.get("required_source_ids", []):
            total += 1
            hit += int(source_id_present(text, str(sid)))
        any_signals = list(rule.get("answer_any", []))
        if any_signals:
            total += 1
            hit += int(any(contains_signal(text, s) for s in any_signals))
    return hit, total


def short_sources(answer: dict[str, Any] | None) -> str:
    if not answer:
        return "MISSING"
    vals = sorted(str(v) for v in answer.get("source_ids", []))
    return ",".join(vals) if vals else "-"


def fmt_cov(cov: dict[str, Any]) -> str:
    any_part = "-" if cov["any_ok"] is None else ("Y" if cov["any_ok"] else "N")
    return f"sig={cov['signal_hit']}/{cov['signal_total']} src={cov['source_hit']}/{cov['source_total']} any={any_part}"


def transition_state_text(run_dir: Path, wave: int, repair_used: bool) -> str | None:
    name = f"W{wave:02d}-transition-repair" if repair_used else f"W{wave:02d}-candidate"
    path = run_dir / "calls" / name / "response.txt"
    return path.read_text(encoding="utf-8") if path.exists() else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Export E007 mechanism-level forensic handoff")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=RUNS)
    args = parser.parse_args()

    plan = load_json(args.plan, {}) or {}
    qmeta = queries()
    checks = rules()
    run_entries = plan.get("runs", [])

    print("E007-MECHANISM-HANDOFF-v0")
    print(f"runs={len(run_entries)} model={plan.get('model')}")

    # 1) Diagnose every observed deterministic primary failure as state-vs-answer.
    print("[FAILED-QUERY-STATE-DIAGNOSIS]")
    for entry in run_entries:
        run_dir = args.run_root / entry["run_id"]
        condition = entry["condition"]
        for qid, query in sorted(qmeta.items()):
            if qid not in checks:
                continue
            wave = int(query["ask_after_wave"])
            rows = score_rows(run_dir, wave)
            row = rows.get(qid)
            if not row or row.get("passed"):
                continue
            answers, violations = primary_answers(run_dir, wave)
            answer = answers.get(qid)
            if condition == "C0":
                state = "RAW-CONTEXT"
            else:
                cov = rule_coverage(wiki_state(run_dir, wave), checks[qid])
                state = fmt_cov(cov)
            unc = answer.get("uncertainty", "-") if answer else "MISSING"
            print(
                f"{entry['run_id']} {qid} W{wave} state={state} ansSources={short_sources(answer)} "
                f"unc={unc} contractViol={len(violations)}"
            )

    # 2) Q025 provenance sensitivity: show exactly what was cited in all 15 primary answers.
    print("[Q025-CITATIONS]")
    q025_wave = int(qmeta["Q025"]["ask_after_wave"])
    required_q025 = set(str(v) for v in checks["Q025"].get("required_source_ids", []))
    for entry in run_entries:
        run_dir = args.run_root / entry["run_id"]
        answers, violations = primary_answers(run_dir, q025_wave)
        answer = answers.get("Q025")
        cited = set(str(v) for v in answer.get("source_ids", [])) if answer else set()
        missing = sorted(required_q025 - cited)
        print(
            f"{entry['run_id']} cited={','.join(sorted(cited)) if cited else '-'} "
            f"missing={','.join(missing) if missing else '-'} contractViol={len(violations)}"
        )

    # 3) Transition repair mechanism: literal anchor coverage and bytes before/after repair.
    print("[TRANSITION-REPAIR-MECHANISM]")
    aggregates: dict[str, Counter[str]] = defaultdict(Counter)
    unresolved_lines: list[str] = []
    for entry in run_entries:
        if entry["condition"] not in {"C3", "C4"}:
            continue
        run_dir = args.run_root / entry["run_id"]
        summary = load_json(run_dir / "summary.json") or load_json(run_dir / "summary.partial.json", {}) or {}
        for wave_row in summary.get("waves", []):
            transition = wave_row.get("transition") or {}
            if not transition or not transition.get("repair_used"):
                continue
            wave = int(wave_row["wave"])
            candidate_path = run_dir / "calls" / f"W{wave:02d}-candidate" / "response.txt"
            repair_path = run_dir / "calls" / f"W{wave:02d}-transition-repair" / "response.txt"
            if not candidate_path.exists() or not repair_path.exists():
                continue
            candidate = candidate_path.read_text(encoding="utf-8")
            repaired = repair_path.read_text(encoding="utf-8")
            before = anchor_coverage(candidate, wave, qmeta, checks)
            after = anchor_coverage(repaired, wave, qmeta, checks)
            if after[0] > before[0]:
                direction = "improved"
            elif after[0] < before[0]:
                direction = "worsened"
            else:
                direction = "same"
            aggregates[entry["condition"]][direction] += 1
            aggregates[entry["condition"]]["repairs"] += 1
            initial = (transition.get("initial") or {}).get("decision", "?")
            final = (transition.get("final") or {}).get("decision", "?")
            if final == "revise" or direction == "worsened":
                unresolved_lines.append(
                    f"{entry['run_id']} W{wave} init={initial} final={final} anchors={before[0]}/{before[1]}->{after[0]}/{after[1]} "
                    f"bytes={len(candidate.encode('utf-8'))}->{len(repaired.encode('utf-8'))}"
                )
    for condition in ("C3", "C4"):
        a = aggregates[condition]
        print(
            f"{condition} repairs={a['repairs']} anchorImproved={a['improved']} "
            f"anchorSame={a['same']} anchorWorsened={a['worsened']}"
        )
    print("[UNRESOLVED-OR-WORSENED-TRANSITIONS]")
    for line in unresolved_lines:
        print(line)

    # 4) C4 regression repairs: exact trigger IDs, immediate result, state-size/anchor effects.
    print("[C4-REGRESSION-REPAIRS]")
    for entry in run_entries:
        if entry["condition"] != "C4":
            continue
        run_dir = args.run_root / entry["run_id"]
        summary = load_json(run_dir / "summary.json") or load_json(run_dir / "summary.partial.json", {}) or {}
        for wave_row in summary.get("waves", []):
            if not wave_row.get("regression_repair_used"):
                continue
            wave = int(wave_row["wave"])
            before_rows = score_rows(run_dir, wave, "regression-before")
            after_rows = score_rows(run_dir, wave, "regression-after")
            failed_before = sorted(qid for qid, row in before_rows.items() if not row.get("passed"))
            failed_after = sorted(qid for qid, row in after_rows.items() if not row.get("passed"))
            transition = wave_row.get("transition") or {}
            pre = transition_state_text(run_dir, wave, bool(transition.get("repair_used"))) or ""
            post_path = run_dir / "calls" / f"W{wave:02d}-regression-repair" / "response.txt"
            post = post_path.read_text(encoding="utf-8") if post_path.exists() else ""
            pre_anchor = anchor_coverage(pre, wave, qmeta, checks)
            post_anchor = anchor_coverage(post, wave, qmeta, checks)
            primary_fail = sorted(
                qid for qid, row in score_rows(run_dir, wave).items() if not row.get("passed")
            )
            print(
                f"{entry['run_id']} W{wave} trigger={','.join(failed_before) if failed_before else '-'} "
                f"after={','.join(failed_after) if failed_after else '-'} primaryFail={','.join(primary_fail) if primary_fail else '-'} "
                f"anchors={pre_anchor[0]}/{pre_anchor[1]}->{post_anchor[0]}/{post_anchor[1]} "
                f"bytes={len(pre.encode('utf-8'))}->{len(post.encode('utf-8'))}"
            )

    # 5) Trace the C4-r01 state-inflation outlier by wave and repair activity.
    print("[C4-R01-STATE-GROWTH]")
    outlier = args.run_root / "C4-r01"
    summary = load_json(outlier / "summary.json") or load_json(outlier / "summary.partial.json", {}) or {}
    waves_by_id = {int(row["wave"]): row for row in summary.get("waves", [])}
    for wave in range(int(plan.get("max_wave", 5)) + 1):
        state = wiki_state(outlier, wave)
        if state is None:
            continue
        row = waves_by_id.get(wave, {})
        transition = row.get("transition") or {}
        print(
            f"W{wave} bytes={len(state.encode('utf-8'))} tRepair={int(bool(transition.get('repair_used')))} "
            f"tFinal={(transition.get('final') or {}).get('decision','-')} rRepair={int(bool(row.get('regression_repair_used')))}"
        )


if __name__ == "__main__":
    main()
