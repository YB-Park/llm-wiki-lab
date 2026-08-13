#!/usr/bin/env python3
"""E007 semantic evaluator with A3 contract containment.

A3 is post-primary only. It preserves raw evaluator responses, reuses an existing
response.txt when present, normalizes only exact string booleans, and excludes
ambiguous malformed evaluator items from automatic aggregation rather than guessing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import evaluate_semantic as base
from answer_contract_a2 import parse_answer_batch_valid_only
from copilot_cli import run_prompt
from score_deterministic import extract_json_object

ALL_FLAGS = base.ALL_FLAGS
MAJOR_FLAGS = base.MAJOR_FLAGS


def normalize_bool(value: Any) -> tuple[bool | None, str | None]:
    if isinstance(value, bool):
        return value, None
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered == "true":
            return True, "string_boolean_normalized"
        if lowered == "false":
            return False, "string_boolean_normalized"
    return None, f"ambiguous_boolean:{value!r}"


def parse_evaluations_a3(text: str, expected_ids: list[str]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    payload = extract_json_object(text)
    rows = payload.get("evaluations")
    if not isinstance(rows, list):
        return {}, [{"type": "invalid_root", "reason": "evaluations must be an array"}]

    expected = set(expected_ids)
    valid: dict[str, dict[str, Any]] = {}
    violations: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append({"type": "invalid_item", "index": index, "reason": "item must be an object"})
            continue
        query_id = row.get("query_id")
        if not isinstance(query_id, str) or not query_id.strip():
            violations.append({"type": "invalid_item", "index": index, "reason": "missing query_id"})
            continue
        query_id = query_id.strip()
        if query_id not in expected:
            violations.append({"type": "extra_query_id", "index": index, "query_id": query_id})
            continue
        if query_id in valid:
            violations.append({"type": "duplicate_query_id", "index": index, "query_id": query_id})
            continue

        reasons: list[str] = []
        normalizations: list[str] = []
        correctness = row.get("correctness")
        # bool is a subclass of int in Python; reject it explicitly.
        if isinstance(correctness, bool) or correctness not in {0, 1, 2}:
            reasons.append(f"invalid_correctness:{correctness!r}")

        normalized_flags: dict[str, bool] = {}
        for flag in ALL_FLAGS:
            normalized, note = normalize_bool(row.get(flag))
            if normalized is None:
                reasons.append(f"{flag}:{note}")
            else:
                normalized_flags[flag] = normalized
                if note:
                    normalizations.append(f"{flag}:{note}")

        rationale_values: dict[str, list[str]] = {}
        for key in ("rationale_fact_ids", "rationale_source_ids"):
            value = row.get(key)
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                reasons.append(f"{key}:must_be_string_array")
            else:
                rationale_values[key] = value

        if reasons:
            violations.append(
                {
                    "type": "invalid_evaluation_item",
                    "index": index,
                    "query_id": query_id,
                    "reasons": reasons,
                }
            )
            continue

        normalized_row = dict(row)
        normalized_row["query_id"] = query_id
        normalized_row["correctness"] = int(correctness)
        normalized_row.update(normalized_flags)
        normalized_row.update(rationale_values)
        if normalizations:
            normalized_row["_a3_normalizations"] = normalizations
        valid[query_id] = normalized_row

    for missing in sorted(expected - set(valid)):
        violations.append({"type": "missing_valid_evaluation", "query_id": missing})

    return valid, violations


def stable_human_sample(run_id: str, query_id: str) -> bool:
    digest = hashlib.sha256(f"{run_id}:{query_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 5 == 0


def aggregate_a3(
    run_id: str,
    expected_ids: list[str],
    pass_rows: list[dict[str, dict[str, Any]]],
    violations_by_pass: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    valid_scores: list[int] = []
    consensus_flags = {flag: 0 for flag in ALL_FLAGS}
    any_flags = {flag: 0 for flag in ALL_FLAGS}
    needs_human: list[str] = []
    major_disagreement: list[str] = []

    for query_id in sorted(expected_ids):
        rows = [rows_by_id.get(query_id) for rows_by_id in pass_rows]
        valid = [row for row in rows if row is not None]
        stable_sample = stable_human_sample(run_id, query_id)
        item: dict[str, Any] = {
            "query_id": query_id,
            "valid_pass_count": len(valid),
            "stable_human_sample": stable_sample,
        }

        if len(valid) < 2:
            item.update(
                {
                    "automatic_semantic_result": "invalid_or_incomplete",
                    "correctness_pair": [row["correctness"] if row else None for row in rows],
                    "needs_human_audit": True,
                }
            )
            needs_human.append(query_id)
            items.append(item)
            continue

        first, second = valid[0], valid[1]
        pair = [int(first["correctness"]), int(second["correctness"])]
        valid_scores.extend(pair)
        correctness_gap = abs(pair[0] - pair[1])
        major = [flag for flag in MAJOR_FLAGS if first[flag] != second[flag]]
        omission_disagreement = first["omission"] != second["omission"]
        audit = stable_sample or correctness_gap > 1 or bool(major)
        if audit:
            needs_human.append(query_id)
        if correctness_gap > 1 or major:
            major_disagreement.append(query_id)

        for flag in ALL_FLAGS:
            consensus_flags[flag] += int(first[flag] and second[flag])
            any_flags[flag] += int(first[flag] or second[flag])

        item.update(
            {
                "automatic_semantic_result": "valid",
                "correctness_pair": pair,
                "correctness_mean": round(sum(pair) / 2, 3),
                "correctness_gap": correctness_gap,
                "major_flag_disagreements": major,
                "omission_disagreement": omission_disagreement,
                "needs_human_audit": audit,
            }
        )
        items.append(item)

    return {
        "format": "E007-SEMANTIC-EVAL-A3-v0",
        "run_id": run_id,
        "expected_item_count": len(expected_ids),
        "fully_valid_item_count": sum(item["valid_pass_count"] == 2 for item in items),
        "invalid_or_incomplete_item_count": sum(item["valid_pass_count"] < 2 for item in items),
        "mean_correctness_across_valid_passes": (
            round(sum(valid_scores) / len(valid_scores), 3) if valid_scores else None
        ),
        "consensus_flags_among_fully_valid_items": consensus_flags,
        "any_pass_flags_among_fully_valid_items": any_flags,
        "items": items,
        "needs_human_audit_query_ids": sorted(set(needs_human)),
        "major_disagreement_query_ids": sorted(set(major_disagreement)),
        "evaluator_contract_violations": violations_by_pass,
    }


def call_or_reuse(*, prompt: str, model: str, call_dir: Path) -> str:
    response_path = call_dir / "response.txt"
    if response_path.exists():
        return response_path.read_text(encoding="utf-8")
    result = run_prompt(prompt=prompt, model=model, run_dir=call_dir)
    return str(result["response"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run E007 blinded semantic evaluation with A3 containment")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.6-luna")
    args = parser.parse_args()

    query_doc = base.load_json(base.CORPUS / "queries.json")
    ground_truth = base.load_json(base.CORPUS / "ground-truth.json")
    sources = base.load_jsonl(base.CORPUS / "sources.jsonl")
    facts_by_id = {fact["fact_id"]: fact for fact in ground_truth["facts"]}

    # Reuse A2 containment for candidate primary-answer parsing.
    base.parse_answer_batch = parse_answer_batch_valid_only
    semantic_queries = [q for q in query_doc["queries"] if q["class"] in base.SEMANTIC_CLASSES]
    answers = base.load_primary_answers(args.run_dir, query_doc["queries"])

    by_wave: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for query in semantic_queries:
        by_wave[int(query["ask_after_wave"])].append(query)

    evaluation_root = args.run_dir / "evaluation"
    all_passes: list[dict[str, dict[str, Any]]] = []
    all_violations: list[list[dict[str, Any]]] = []
    expected_all = sorted(q["query_id"] for q in semantic_queries)

    for pass_number in (1, 2):
        pass_rows: dict[str, dict[str, Any]] = {}
        pass_violations: list[dict[str, Any]] = []
        for wave, wave_queries in sorted(by_wave.items()):
            items = base.build_wave_items(
                wave=wave,
                queries=wave_queries,
                answers=answers,
                facts_by_id=facts_by_id,
                sources=sources,
            )
            prompt = base.render_template(
                "semantic-evaluate.md",
                EVALUATOR_ITEMS=json.dumps(items, indent=2, ensure_ascii=False),
            )
            call_dir = evaluation_root / f"pass-{pass_number}" / f"W{wave:02d}"
            raw = call_or_reuse(prompt=prompt, model=args.model, call_dir=call_dir)
            expected_ids = [q["query_id"] for q in sorted(wave_queries, key=lambda row: row["query_id"])]
            parsed, violations = parse_evaluations_a3(raw, expected_ids)
            for violation in violations:
                violation = dict(violation)
                violation["pass"] = pass_number
                violation["wave"] = wave
                pass_violations.append(violation)
            pass_rows.update(parsed)

        base.write_json(evaluation_root / f"semantic-pass-{pass_number}-a3.json", pass_rows)
        base.write_json(evaluation_root / f"semantic-contract-violations-pass-{pass_number}-a3.json", pass_violations)
        all_passes.append(pass_rows)
        all_violations.append(pass_violations)

    summary = aggregate_a3(args.run_dir.name, expected_all, all_passes, all_violations)
    base.write_json(evaluation_root / "semantic-summary.json", summary)

    invalid = summary["invalid_or_incomplete_item_count"]
    audit = ",".join(summary["needs_human_audit_query_ids"]) or "-"
    text = "\n".join(
        [
            "E007-SEMANTIC-EVAL-A3-v0",
            (
                f"run={args.run_dir.name} valid={summary['fully_valid_item_count']}/{summary['expected_item_count']} "
                f"invalid={invalid} mean={summary['mean_correctness_across_valid_passes']}"
            ),
            f"evaluator_contract_violations={sum(len(v) for v in all_violations)}",
            f"human_audit={audit}",
        ]
    ) + "\n"
    (evaluation_root / "semantic-handoff.txt").write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
