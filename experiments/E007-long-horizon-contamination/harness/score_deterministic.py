#!/usr/bin/env python3
"""Deterministic scorer for E007 regression-eligible query answers.

The scorer deliberately handles only checks that can be expressed as stable text/source
signals. Global synthesis and multi-hop quality remain outside this gate in protocol v0.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
CHECKS_PATH = CORPUS / "deterministic-checks.json"


def normalize_text(value: str) -> str:
    """Case-fold and normalize punctuation/spacing for robust signal matching."""
    value = value.casefold()
    value = re.sub(r"[^0-9a-z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def contains_signal(text: str, signal: str) -> bool:
    return normalize_text(signal) in normalize_text(text)


def _loads_transport_json(candidate: str) -> Any:
    """Parse JSON with one narrowly scoped LLM-transport tolerance.

    Models sometimes emit a literal newline/tab/control character inside a quoted JSON
    string even when instructed to return JSON-only. Python's default JSON decoder rejects
    those characters. Retrying with ``strict=False`` accepts only that class of control
    characters; it does not repair missing quotes, commas, braces, or other malformed
    structure. This prevents a serialization quirk from becoming a semantic failure while
    keeping genuinely malformed JSON loud.
    """
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        if not exc.msg.startswith("Invalid control character"):
            raise
        return json.loads(candidate, strict=False)


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object, tolerating one outer Markdown code fence or light chatter.

    The prompt requires JSON-only output. Tolerance here prevents transport formatting from
    being treated as a semantic failure. A literal control character inside a quoted string
    is accepted as a narrow transport fallback; malformed/ambiguous JSON still fails loudly.
    """
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            stripped = "\n".join(lines[1:-1]).strip()

    try:
        parsed = _loads_transport_json(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("response does not contain a parseable JSON object")
        try:
            parsed = _loads_transport_json(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"response JSON is malformed: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("response root must be a JSON object")
    return parsed


def parse_answer_batch(text: str) -> dict[str, dict[str, Any]]:
    payload = extract_json_object(text)
    answers = payload.get("answers")
    if not isinstance(answers, list):
        raise ValueError("response must contain an 'answers' array")

    result: dict[str, dict[str, Any]] = {}
    for item in answers:
        if not isinstance(item, dict):
            raise ValueError("each answers item must be an object")
        query_id = item.get("query_id")
        if not isinstance(query_id, str) or not query_id:
            raise ValueError("each answer must contain a non-empty query_id")
        if query_id in result:
            raise ValueError(f"duplicate answer for {query_id}")
        answer = item.get("answer")
        if not isinstance(answer, str):
            raise ValueError(f"{query_id}: answer must be a string")
        source_ids = item.get("source_ids", [])
        if source_ids is None:
            source_ids = []
        if not isinstance(source_ids, list) or not all(isinstance(v, str) for v in source_ids):
            raise ValueError(f"{query_id}: source_ids must be a string array")
        uncertainty = item.get("uncertainty", "none")
        if not isinstance(uncertainty, str):
            raise ValueError(f"{query_id}: uncertainty must be a string")
        result[query_id] = {
            "query_id": query_id,
            "answer": answer,
            "source_ids": source_ids,
            "uncertainty": uncertainty,
        }
    return result


@dataclass
class QueryScore:
    query_id: str
    passed: bool
    failures: list[str]


def score_one(answer: dict[str, Any], rule: dict[str, Any]) -> QueryScore:
    query_id = answer["query_id"]
    text = answer["answer"]
    sources = {str(v).upper() for v in answer.get("source_ids", [])}
    uncertainty = str(answer.get("uncertainty", "none")).casefold()
    failures: list[str] = []

    for signal in rule.get("answer_all", []):
        if not contains_signal(text, signal):
            failures.append(f"missing required answer signal: {signal!r}")

    any_signals = rule.get("answer_any", [])
    if any_signals and not any(contains_signal(text, signal) for signal in any_signals):
        failures.append(f"missing any-of answer signal: {any_signals!r}")

    for signal in rule.get("answer_none", []):
        if contains_signal(text, signal):
            failures.append(f"contains forbidden answer signal: {signal!r}")

    required_sources = {str(v).upper() for v in rule.get("required_source_ids", [])}
    missing_sources = sorted(required_sources - sources)
    if missing_sources:
        failures.append(f"missing required source_ids: {missing_sources}")

    allowed_uncertainty = [str(v).casefold() for v in rule.get("uncertainty_in", [])]
    if allowed_uncertainty and uncertainty not in allowed_uncertainty:
        failures.append(
            f"uncertainty={answer.get('uncertainty')!r} not in allowed set {rule.get('uncertainty_in')!r}"
        )

    return QueryScore(query_id=query_id, passed=not failures, failures=failures)


def load_rules() -> dict[str, dict[str, Any]]:
    payload = json.loads(CHECKS_PATH.read_text(encoding="utf-8"))
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("deterministic-checks.json must contain a checks object")
    return checks


def score_batch(text: str, query_ids: list[str] | None = None) -> dict[str, Any]:
    answers = parse_answer_batch(text)
    rules = load_rules()

    if query_ids is None:
        query_ids = sorted(set(answers) & set(rules))

    scores: list[QueryScore] = []
    for query_id in query_ids:
        if query_id not in rules:
            raise ValueError(f"no deterministic rule for {query_id}")
        if query_id not in answers:
            scores.append(QueryScore(query_id=query_id, passed=False, failures=["missing answer object"]))
            continue
        scores.append(score_one(answers[query_id], rules[query_id]))

    return {
        "query_count": len(scores),
        "passed_count": sum(score.passed for score in scores),
        "failed_count": sum(not score.passed for score in scores),
        "all_passed": all(score.passed for score in scores),
        "scores": [asdict(score) for score in scores],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a Copilot answer-batch response deterministically")
    parser.add_argument("answer_file", type=Path)
    parser.add_argument("--query-id", action="append", dest="query_ids", help="Score only this query ID; repeatable")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = score_batch(args.answer_file.read_text(encoding="utf-8"), args.query_ids)
    encoded = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
