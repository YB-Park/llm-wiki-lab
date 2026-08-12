#!/usr/bin/env python3
"""Run E007 post-hoc semantic evaluation in blinded, time-safe packets.

This evaluator never changes an E007 run. Semantic queries are grouped by the wave
when they first become answerable so no evaluator call sees future evidence for an
earlier item.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from copilot_cli import run_prompt
from score_deterministic import extract_json_object, parse_answer_batch

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
PROMPTS = ROOT / "prompts"
SEMANTIC_CLASSES = {"global_synthesis", "multi_hop"}
MAJOR_FLAGS = ("unsupported_claim", "temporal_error", "entity_conflation")
ALL_FLAGS = ("omission",) + MAJOR_FLAGS


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_sources(sources: list[dict[str, Any]]) -> str:
    blocks = []
    for source in sources:
        blocks.append(
            "\n".join(
                [
                    f"### {source['source_id']} — {source['title']}",
                    f"Date: {source['date']}",
                    f"Publisher: {source['publisher']}",
                    "",
                    source["text"],
                ]
            )
        )
    return "\n\n".join(blocks) if blocks else "(none)"


def render_template(name: str, **values: str) -> str:
    text = (PROMPTS / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def load_primary_answers(run_dir: Path, queries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_wave: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        by_wave[int(query["ask_after_wave"])].append(query)

    answers: dict[str, dict[str, Any]] = {}
    for wave, wave_queries in sorted(by_wave.items()):
        response_path = run_dir / "calls" / f"W{wave:02d}-primary" / "response.txt"
        if not response_path.exists():
            raise FileNotFoundError(f"missing primary response: {response_path}")
        parsed = parse_answer_batch(response_path.read_text(encoding="utf-8"))
        expected = {q["query_id"] for q in wave_queries}
        missing = expected - set(parsed)
        if missing:
            raise ValueError(f"primary response W{wave:02d} missing queries: {sorted(missing)}")
        for query in wave_queries:
            answers[query["query_id"]] = parsed[query["query_id"]]
    return answers


def build_wave_items(
    *,
    wave: int,
    queries: list[dict[str, Any]],
    answers: dict[str, dict[str, Any]],
    facts_by_id: dict[str, dict[str, Any]],
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    available_sources = sorted(
        [source for source in sources if int(source["wave"]) <= wave],
        key=lambda row: row["source_id"],
    )
    rendered_sources = render_sources(available_sources)

    items: list[dict[str, Any]] = []
    for query in sorted(queries, key=lambda row: row["query_id"]):
        required_facts = []
        for fact_id in query.get("required_fact_ids", []):
            fact = facts_by_id[fact_id]
            if int(fact.get("known_from_wave", 0)) > wave:
                raise ValueError(
                    f"{query['query_id']} requires future fact {fact_id} at evaluation wave {wave}"
                )
            required_facts.append(fact)

        items.append(
            {
                "query_id": query["query_id"],
                "question": query["question"],
                "candidate_answer": answers[query["query_id"]],
                "rubric": query["rubric"],
                "required_facts": required_facts,
                "authoritative_raw_sources_available_through_wave": rendered_sources,
            }
        )
    return items


def parse_evaluations(text: str, expected_ids: list[str]) -> dict[str, dict[str, Any]]:
    payload = extract_json_object(text)
    rows = payload.get("evaluations")
    if not isinstance(rows, list):
        raise ValueError("semantic evaluator output must contain an evaluations array")

    parsed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each semantic evaluation must be an object")
        query_id = row.get("query_id")
        if not isinstance(query_id, str) or query_id in parsed:
            raise ValueError(f"invalid or duplicate query_id in semantic evaluation: {query_id!r}")
        correctness = row.get("correctness")
        if correctness not in {0, 1, 2}:
            raise ValueError(f"{query_id}: correctness must be 0, 1, or 2")
        for flag in ALL_FLAGS:
            if not isinstance(row.get(flag), bool):
                raise ValueError(f"{query_id}: {flag} must be boolean")
        for key in ("rationale_fact_ids", "rationale_source_ids"):
            if not isinstance(row.get(key), list) or not all(isinstance(v, str) for v in row[key]):
                raise ValueError(f"{query_id}: {key} must be an array of strings")
        parsed[query_id] = row

    if set(parsed) != set(expected_ids):
        raise ValueError(
            f"semantic evaluator query IDs mismatch: expected {sorted(expected_ids)}, got {sorted(parsed)}"
        )
    return parsed


def stable_human_sample(run_id: str, query_id: str) -> bool:
    digest = hashlib.sha256(f"{run_id}:{query_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 5 == 0


def disagreement_record(
    query_id: str,
    first: dict[str, Any],
    second: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    correctness_gap = abs(int(first["correctness"]) - int(second["correctness"]))
    major_disagreements = [flag for flag in MAJOR_FLAGS if first[flag] != second[flag]]
    omission_disagreement = first["omission"] != second["omission"]
    stable_sample = stable_human_sample(run_id, query_id)
    needs_human = correctness_gap > 1 or bool(major_disagreements)
    return {
        "query_id": query_id,
        "correctness_pair": [first["correctness"], second["correctness"]],
        "correctness_mean": round((first["correctness"] + second["correctness"]) / 2, 3),
        "correctness_gap": correctness_gap,
        "major_flag_disagreements": major_disagreements,
        "omission_disagreement": omission_disagreement,
        "stable_human_sample": stable_sample,
        "needs_human_audit": needs_human or stable_sample,
    }


def aggregate_summary(
    run_id: str,
    pass1: dict[str, dict[str, Any]],
    pass2: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    items = [
        disagreement_record(query_id, pass1[query_id], pass2[query_id], run_id)
        for query_id in sorted(pass1)
    ]
    all_scores = [score for item in items for score in item["correctness_pair"]]
    consensus_flags: dict[str, int] = {}
    any_flags: dict[str, int] = {}
    for flag in ALL_FLAGS:
        consensus_flags[flag] = sum(1 for qid in pass1 if pass1[qid][flag] and pass2[qid][flag])
        any_flags[flag] = sum(1 for qid in pass1 if pass1[qid][flag] or pass2[qid][flag])

    return {
        "format": "E007-SEMANTIC-EVAL-v0",
        "run_id": run_id,
        "item_count": len(items),
        "pass_count": 2,
        "mean_correctness_across_passes": round(sum(all_scores) / max(len(all_scores), 1), 3),
        "consensus_flags": consensus_flags,
        "any_pass_flags": any_flags,
        "items": items,
        "needs_human_audit_query_ids": [item["query_id"] for item in items if item["needs_human_audit"]],
        "major_disagreement_query_ids": [
            item["query_id"]
            for item in items
            if item["correctness_gap"] > 1 or item["major_flag_disagreements"]
        ],
    }


def compact_summary(summary: dict[str, Any]) -> str:
    flags = summary["consensus_flags"]
    audit = ",".join(summary["needs_human_audit_query_ids"]) or "-"
    disagree = ",".join(summary["major_disagreement_query_ids"]) or "-"
    return "\n".join(
        [
            "E007-SEMANTIC-EVAL-v0",
            f"run={summary['run_id']} items={summary['item_count']} passes=2 mean={summary['mean_correctness_across_passes']}",
            (
                "consensus_flags="
                f"omission:{flags['omission']} unsupported:{flags['unsupported_claim']} "
                f"temporal:{flags['temporal_error']} conflation:{flags['entity_conflation']}"
            ),
            f"major_disagree={disagree}",
            f"human_audit={audit}",
        ]
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run blinded two-pass E007 semantic evaluation")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--passes", type=int, default=2, choices=[2], help="v0 is frozen to exactly two passes")
    args = parser.parse_args()

    query_doc = load_json(CORPUS / "queries.json")
    ground_truth = load_json(CORPUS / "ground-truth.json")
    sources = load_jsonl(CORPUS / "sources.jsonl")
    facts_by_id = {fact["fact_id"]: fact for fact in ground_truth["facts"]}

    semantic_queries = [q for q in query_doc["queries"] if q["class"] in SEMANTIC_CLASSES]
    answers = load_primary_answers(args.run_dir, query_doc["queries"])

    by_wave: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for query in semantic_queries:
        by_wave[int(query["ask_after_wave"])].append(query)

    all_passes: list[dict[str, dict[str, Any]]] = []
    evaluation_root = args.run_dir / "evaluation"

    for pass_number in (1, 2):
        pass_rows: dict[str, dict[str, Any]] = {}
        for wave, wave_queries in sorted(by_wave.items()):
            items = build_wave_items(
                wave=wave,
                queries=wave_queries,
                answers=answers,
                facts_by_id=facts_by_id,
                sources=sources,
            )
            prompt = render_template(
                "semantic-evaluate.md",
                EVALUATOR_ITEMS=json.dumps(items, indent=2, ensure_ascii=False),
            )
            call_dir = evaluation_root / f"pass-{pass_number}" / f"W{wave:02d}"
            result = run_prompt(prompt=prompt, model=args.model, run_dir=call_dir)
            expected_ids = [q["query_id"] for q in sorted(wave_queries, key=lambda row: row["query_id"])]
            parsed = parse_evaluations(str(result["response"]), expected_ids)
            pass_rows.update(parsed)

        write_json(evaluation_root / f"semantic-pass-{pass_number}.json", pass_rows)
        all_passes.append(pass_rows)

    summary = aggregate_summary(args.run_dir.name, all_passes[0], all_passes[1])
    write_json(evaluation_root / "semantic-summary.json", summary)
    text = compact_summary(summary)
    (evaluation_root / "semantic-handoff.txt").write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
