#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "corpus" / "cases.jsonl"
MANIFEST = ROOT / "corpus" / "manifest.json"


def load_cases():
    rows = []
    for lineno, line in enumerate(CASES.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"invalid JSONL line {lineno}: {exc}") from exc
    return rows


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = load_cases()
    assert len(rows) == manifest["case_count"] == 40
    assert len({r["case_id"] for r in rows}) == 40
    counts = Counter(r["gold_label"] for r in rows)
    assert counts == Counter({"safe_commit": 20, "unsafe_commit": 20})

    groups = defaultdict(list)
    for row in rows:
        assert row["risk"] in {"low", "elevated", "high"}
        assert isinstance(row["previous_state"], str) and row["previous_state"].strip()
        assert isinstance(row["candidate_state"], str) and row["candidate_state"].strip()
        assert isinstance(row["new_evidence"], list) and row["new_evidence"]
        groups[row["scenario_group"]].append(row)

    assert len(groups) == 20
    for group, pair in groups.items():
        assert len(pair) == 2, group
        assert {r["gold_label"] for r in pair} == {"safe_commit", "unsafe_commit"}, group
        assert len({r["risk"] for r in pair}) == 1, group
        assert len({r["previous_state"] for r in pair}) == 1, group
        evidence = {json.dumps(r["new_evidence"], sort_keys=True) for r in pair}
        assert len(evidence) == 1, group
        assert len({r["candidate_state"] for r in pair}) == 2, group

    classes = {r["primary_class"] for r in rows}
    assert set(manifest["required_safe_classes"]) <= classes
    assert set(manifest["required_unsafe_classes"]) <= classes

    digest = hashlib.sha256(CASES.read_bytes()).hexdigest()
    print("E009A-CORPUS-VALID-v0")
    print(f"cases=40 groups=20 safe=20 unsafe=20 sha256={digest}")


if __name__ == "__main__":
    main()
