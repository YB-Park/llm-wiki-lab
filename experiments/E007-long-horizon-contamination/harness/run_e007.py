#!/usr/bin/env python3
"""Run E007 Family N (natural behavior) using the frozen condition protocol v0.

This runner deliberately implements only the natural-error family. Controlled fault
injection (Family I) will be added only after its mutation boundaries are separately
pre-registered.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from copilot_cli import run_prompt
from score_deterministic import extract_json_object, parse_answer_batch, score_batch

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
PROMPTS = ROOT / "prompts"
RUNS = ROOT / "runs"

VALID_CONDITIONS = {"C0", "C1", "C2", "C3", "C4"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def render_template(name: str, **values: str) -> str:
    text = (PROMPTS / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    leftover = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text)))
    if leftover:
        raise ValueError(f"unresolved placeholders in {name}: {leftover}")
    return text


def render_sources(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "(none)"
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
    return "\n\n".join(blocks)


def render_questions(queries: list[dict[str, Any]]) -> str:
    public = [{"query_id": q["query_id"], "question": q["question"]} for q in queries]
    return json.dumps(public, indent=2, ensure_ascii=False)


def normalize_markdown_response(text: str) -> str:
    """Remove only an outer transport code fence; do not semantically edit content."""
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            first = lines[0].strip()
            last = lines[-1].strip()
            if first.startswith("```") and last == "```":
                stripped = "\n".join(lines[1:-1]).strip()
    return stripped + "\n"


def parse_verification(text: str) -> dict[str, Any]:
    payload = extract_json_object(text)
    if payload.get("decision") not in {"accept", "revise"}:
        raise ValueError("verifier decision must be 'accept' or 'revise'")
    for key in ("coverage_issues", "preservation_issues", "faithfulness_issues"):
        if not isinstance(payload.get(key), list):
            raise ValueError(f"verifier {key} must be an array")
    should_accept = not any(payload[key] for key in ("coverage_issues", "preservation_issues", "faithfulness_issues"))
    if should_accept != (payload["decision"] == "accept"):
        raise ValueError("verifier decision is inconsistent with issue arrays")
    return payload


def make_call(*, run_dir: Path, call_name: str, prompt: str, model: str) -> str:
    call_dir = run_dir / "calls" / call_name
    result = run_prompt(prompt=prompt, model=model, run_dir=call_dir)
    return str(result["response"])


def answer_queries(
    *,
    run_dir: Path,
    call_name: str,
    evidence: str,
    queries: list[dict[str, Any]],
    model: str,
) -> tuple[str, dict[str, dict[str, Any]]]:
    prompt = render_template(
        "answer-batch.md",
        EVIDENCE=evidence,
        QUESTIONS=render_questions(queries),
    )
    raw = make_call(run_dir=run_dir, call_name=call_name, prompt=prompt, model=model)
    parsed = parse_answer_batch(raw)
    expected = [q["query_id"] for q in queries]
    if set(parsed) != set(expected):
        raise ValueError(
            f"{call_name}: answer IDs mismatch; expected {sorted(expected)}, got {sorted(parsed)}"
        )
    return raw, parsed


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def regression_failure_payload(
    queries_by_id: dict[str, dict[str, Any]],
    answers: dict[str, dict[str, Any]],
    score_result: dict[str, Any],
) -> str:
    failures = []
    for item in score_result["scores"]:
        if item["passed"]:
            continue
        query_id = item["query_id"]
        failures.append(
            {
                "query_id": query_id,
                "question": queries_by_id[query_id]["question"],
                "current_answer": answers.get(query_id, {}).get("answer", "(missing)"),
                "current_source_ids": answers.get(query_id, {}).get("source_ids", []),
                "note": "This query previously passed deterministic regression criteria but no longer does. Re-derive the relevant knowledge from raw sources rather than trusting this note as evidence."
            }
        )
    return json.dumps(failures, indent=2, ensure_ascii=False)


def update_c1(
    *,
    run_dir: Path,
    wave: int,
    current_wiki: str,
    new_sources: list[dict[str, Any]],
    model: str,
) -> str:
    prompt = render_template(
        "C1-update.md",
        CURRENT_WIKI=current_wiki or "(empty — initial compilation)",
        NEW_SOURCES=render_sources(new_sources),
    )
    response = make_call(run_dir=run_dir, call_name=f"W{wave:02d}-update", prompt=prompt, model=model)
    return normalize_markdown_response(response)


def update_c2_candidate(
    *,
    run_dir: Path,
    wave: int,
    current_wiki: str,
    new_sources: list[dict[str, Any]],
    all_sources: list[dict[str, Any]],
    model: str,
) -> str:
    prompt = render_template(
        "C2-update.md",
        CURRENT_WIKI=current_wiki or "(empty — initial compilation)",
        NEW_SOURCES=render_sources(new_sources),
        ALL_SOURCES=render_sources(all_sources),
    )
    response = make_call(run_dir=run_dir, call_name=f"W{wave:02d}-candidate", prompt=prompt, model=model)
    return normalize_markdown_response(response)


def verify_transition(
    *,
    run_dir: Path,
    call_name: str,
    current_wiki: str,
    new_sources: list[dict[str, Any]],
    candidate_wiki: str,
    all_sources: list[dict[str, Any]],
    model: str,
) -> dict[str, Any]:
    prompt = render_template(
        "C3-verify.md",
        CURRENT_WIKI=current_wiki or "(empty — initial compilation)",
        NEW_SOURCES=render_sources(new_sources),
        CANDIDATE_WIKI=candidate_wiki,
        ALL_SOURCES=render_sources(all_sources),
    )
    response = make_call(run_dir=run_dir, call_name=call_name, prompt=prompt, model=model)
    report = parse_verification(response)
    write_json(run_dir / "verification" / f"{call_name}.json", report)
    return report


def c3_process(
    *,
    run_dir: Path,
    wave: int,
    current_wiki: str,
    new_sources: list[dict[str, Any]],
    all_sources: list[dict[str, Any]],
    model: str,
) -> tuple[str, dict[str, Any]]:
    candidate = update_c2_candidate(
        run_dir=run_dir,
        wave=wave,
        current_wiki=current_wiki,
        new_sources=new_sources,
        all_sources=all_sources,
        model=model,
    )
    first = verify_transition(
        run_dir=run_dir,
        call_name=f"W{wave:02d}-verify-1",
        current_wiki=current_wiki,
        new_sources=new_sources,
        candidate_wiki=candidate,
        all_sources=all_sources,
        model=model,
    )
    if first["decision"] == "accept":
        return candidate, {"initial": first, "repair_used": False, "final": first}

    repair_prompt = render_template(
        "C3-repair.md",
        CURRENT_WIKI=current_wiki or "(empty — initial compilation)",
        CANDIDATE_WIKI=candidate,
        VERIFICATION_REPORT=json.dumps(first, indent=2, ensure_ascii=False),
        ALL_SOURCES=render_sources(all_sources),
    )
    repair_response = make_call(
        run_dir=run_dir,
        call_name=f"W{wave:02d}-transition-repair",
        prompt=repair_prompt,
        model=model,
    )
    repaired = normalize_markdown_response(repair_response)
    final = verify_transition(
        run_dir=run_dir,
        call_name=f"W{wave:02d}-verify-2",
        current_wiki=current_wiki,
        new_sources=new_sources,
        candidate_wiki=repaired,
        all_sources=all_sources,
        model=model,
    )
    return repaired, {"initial": first, "repair_used": True, "final": final}


def run_condition(*, condition: str, model: str, run_dir: Path, max_wave: int) -> None:
    manifest = load_json(CORPUS / "manifest.json")
    sources = load_jsonl(CORPUS / "sources.jsonl")
    query_doc = load_json(CORPUS / "queries.json")
    queries: list[dict[str, Any]] = query_doc["queries"]
    queries_by_id = {q["query_id"]: q for q in queries}

    by_wave_sources: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for source in sources:
        by_wave_sources[int(source["wave"])].append(source)
    by_wave_queries: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        by_wave_queries[int(query["ask_after_wave"])].append(query)

    run_dir.mkdir(parents=True, exist_ok=False)
    write_json(
        run_dir / "run-config.json",
        {
            "experiment": "E007",
            "protocol": "condition-protocol-v0",
            "family": "N-natural",
            "condition": condition,
            "model": model,
            "corpus_id": manifest["corpus_id"],
            "max_wave": max_wave,
            "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
    )

    current_wiki = ""
    available_sources: list[dict[str, Any]] = []
    regression_passed: set[str] = set()
    run_summary: dict[str, Any] = {"waves": []}

    for wave in range(max_wave + 1):
        new_sources = sorted(by_wave_sources[wave], key=lambda row: row["source_id"])
        available_sources.extend(new_sources)
        primary_queries = sorted(by_wave_queries[wave], key=lambda row: row["query_id"])
        wave_summary: dict[str, Any] = {
            "wave": wave,
            "new_source_ids": [s["source_id"] for s in new_sources],
            "primary_query_ids": [q["query_id"] for q in primary_queries],
        }

        if condition == "C0":
            evidence = render_sources(available_sources)
        elif condition == "C1":
            current_wiki = update_c1(
                run_dir=run_dir,
                wave=wave,
                current_wiki=current_wiki,
                new_sources=new_sources,
                model=model,
            )
            evidence = current_wiki
        elif condition == "C2":
            current_wiki = update_c2_candidate(
                run_dir=run_dir,
                wave=wave,
                current_wiki=current_wiki,
                new_sources=new_sources,
                all_sources=available_sources,
                model=model,
            )
            evidence = current_wiki
        else:
            current_wiki, transition_summary = c3_process(
                run_dir=run_dir,
                wave=wave,
                current_wiki=current_wiki,
                new_sources=new_sources,
                all_sources=available_sources,
                model=model,
            )
            wave_summary["transition"] = transition_summary

            if condition == "C4" and regression_passed:
                regression_queries = [queries_by_id[qid] for qid in sorted(regression_passed)]
                regression_raw, regression_answers = answer_queries(
                    run_dir=run_dir,
                    call_name=f"W{wave:02d}-regression-before",
                    evidence=current_wiki,
                    queries=regression_queries,
                    model=model,
                )
                regression_score = score_batch(regression_raw, [q["query_id"] for q in regression_queries])
                write_json(run_dir / "scores" / f"W{wave:02d}-regression-before.json", regression_score)
                wave_summary["regression_before"] = {
                    "passed": regression_score["passed_count"],
                    "failed": regression_score["failed_count"],
                }

                if not regression_score["all_passed"]:
                    repair_prompt = render_template(
                        "C4-regression-repair.md",
                        CANDIDATE_WIKI=current_wiki,
                        REGRESSION_FAILURES=regression_failure_payload(
                            queries_by_id, regression_answers, regression_score
                        ),
                        ALL_SOURCES=render_sources(available_sources),
                    )
                    repaired_raw = make_call(
                        run_dir=run_dir,
                        call_name=f"W{wave:02d}-regression-repair",
                        prompt=repair_prompt,
                        model=model,
                    )
                    current_wiki = normalize_markdown_response(repaired_raw)
                    after_raw, _after_answers = answer_queries(
                        run_dir=run_dir,
                        call_name=f"W{wave:02d}-regression-after",
                        evidence=current_wiki,
                        queries=regression_queries,
                        model=model,
                    )
                    after_score = score_batch(after_raw, [q["query_id"] for q in regression_queries])
                    write_json(run_dir / "scores" / f"W{wave:02d}-regression-after.json", after_score)
                    wave_summary["regression_repair_used"] = True
                    wave_summary["regression_after"] = {
                        "passed": after_score["passed_count"],
                        "failed": after_score["failed_count"],
                    }
                else:
                    wave_summary["regression_repair_used"] = False

            evidence = current_wiki

        if condition != "C0":
            state_path = run_dir / "states" / f"W{wave:02d}-wiki.md"
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text(current_wiki, encoding="utf-8")

        primary_raw, _primary_answers = answer_queries(
            run_dir=run_dir,
            call_name=f"W{wave:02d}-primary",
            evidence=evidence,
            queries=primary_queries,
            model=model,
        )
        eligible_ids = [
            q["query_id"]
            for q in primary_queries
            if q["class"] in {"local_exact", "temporal", "provenance", "negative_uncertainty_delayed"}
        ]
        if eligible_ids:
            primary_score = score_batch(primary_raw, eligible_ids)
            write_json(run_dir / "scores" / f"W{wave:02d}-primary-deterministic.json", primary_score)
            wave_summary["primary_deterministic"] = {
                "passed": primary_score["passed_count"],
                "failed": primary_score["failed_count"],
            }
            if condition == "C4":
                for item in primary_score["scores"]:
                    if item["passed"]:
                        regression_passed.add(item["query_id"])

        run_summary["waves"].append(wave_summary)
        write_json(run_dir / "summary.partial.json", run_summary)

    run_summary["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    run_summary["regression_passed_query_ids"] = sorted(regression_passed)
    write_json(run_dir / "summary.json", run_summary)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run E007 Family N with Copilot CLI")
    parser.add_argument("--condition", required=True, choices=sorted(VALID_CONDITIONS))
    parser.add_argument("--model", required=True, help="Concrete Copilot model; 'auto' is forbidden")
    parser.add_argument("--run-id", required=True, help="Unique run identifier, e.g. c2-r01")
    parser.add_argument("--run-root", type=Path, default=RUNS)
    parser.add_argument("--max-wave", type=int, default=5, choices=range(0, 6))
    args = parser.parse_args()

    if args.model.casefold() == "auto":
        raise SystemExit("--model=auto is not allowed by E007 protocol v0")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.run_id):
        raise SystemExit("--run-id must contain only letters, digits, dot, underscore, or hyphen")

    run_dir = args.run_root / args.run_id
    run_condition(condition=args.condition, model=args.model, run_dir=run_dir, max_wave=args.max_wave)
    print(f"E007 run complete: {run_dir}")


if __name__ == "__main__":
    main()
