#!/usr/bin/env python3
"""Parse E009A verifier output without semantic repair or reroll.

A malformed verifier response is a measurable invalid judgment, not an infrastructure
exception. The only parsing tolerance is a literal control character inside an otherwise
valid quoted JSON string, matching the narrow transport lesson from E007.
"""

from __future__ import annotations

import json
from typing import Any

ISSUE_KEYS = (
    "coverage_issues",
    "preservation_issues",
    "faithfulness_issues",
    "provenance_issues",
    "temporal_epistemic_issues",
)


def _loads(candidate: str) -> Any:
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        if not exc.msg.startswith("Invalid control character"):
            raise
        return json.loads(candidate, strict=False)


def extract_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            stripped = "\n".join(lines[1:-1]).strip()
    try:
        obj = _loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("no parseable JSON object")
        try:
            obj = _loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError("root must be an object")
    return obj


def parse_judgment(text: str) -> dict[str, Any]:
    violations: list[str] = []
    try:
        obj = extract_object(text)
    except ValueError as exc:
        return {"valid": False, "decision": None, "violations": [str(exc)], "report": None}

    decision = obj.get("decision")
    if decision not in {"accept", "revise"}:
        violations.append("decision_not_accept_or_revise")

    normalized: dict[str, list[dict[str, str]]] = {}
    for key in ISSUE_KEYS:
        value = obj.get(key)
        if not isinstance(value, list):
            violations.append(f"{key}_not_array")
            normalized[key] = []
            continue
        items: list[dict[str, str]] = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                violations.append(f"{key}[{index}]_not_object")
                continue
            issue_id = item.get("id")
            description = item.get("description")
            if not isinstance(issue_id, str) or not issue_id.strip():
                violations.append(f"{key}[{index}]_invalid_id")
                continue
            if not isinstance(description, str) or not description.strip():
                violations.append(f"{key}[{index}]_invalid_description")
                continue
            items.append({"id": issue_id.strip(), "description": description.strip()})
        normalized[key] = items

    issue_count = sum(len(v) for v in normalized.values())
    if decision == "accept" and issue_count:
        violations.append("accept_with_material_issues")
    if decision == "revise" and issue_count == 0:
        violations.append("revise_without_material_issue")

    valid = not violations
    return {
        "valid": valid,
        "decision": decision if decision in {"accept", "revise"} else None,
        "violations": violations,
        "report": {"decision": decision, **normalized},
        "issue_count": issue_count,
        "issue_counts": {key: len(normalized[key]) for key in ISSUE_KEYS},
    }


def self_test() -> None:
    good = '{"decision":"accept","coverage_issues":[],"preservation_issues":[],"faithfulness_issues":[],"provenance_issues":[],"temporal_epistemic_issues":[]}'
    assert parse_judgment(good)["valid"]
    bad = '{"decision":"revise","coverage_issues":[],"preservation_issues":[],"faithfulness_issues":[],"provenance_issues":[],"temporal_epistemic_issues":[]}'
    assert not parse_judgment(bad)["valid"]
    control = '{"decision":"revise","coverage_issues":[{"id":"x","description":"line1\nline2"}],"preservation_issues":[],"faithfulness_issues":[],"provenance_issues":[],"temporal_epistemic_issues":[]}'
    assert parse_judgment(control)["valid"]
    print("E009A-VERIFIER-CONTRACT-SELF-TEST PASS")


if __name__ == "__main__":
    self_test()
