#!/usr/bin/env python3
"""Validate Corpus C v0 cross-references without invoking an LLM."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"


def load_json(name: str):
    return json.loads((CORPUS / name).read_text(encoding="utf-8"))


def load_jsonl(name: str):
    rows = []
    for lineno, line in enumerate((CORPUS / name).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{lineno}: invalid JSON: {exc}") from exc
    return rows


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def main() -> None:
    manifest = load_json("manifest.json")
    ground = load_json("ground-truth.json")
    query_doc = load_json("queries.json")
    deterministic = load_json("deterministic-checks.json")
    sources = load_jsonl("sources.jsonl")

    require(manifest["corpus_id"] == ground["corpus_id"] == query_doc["corpus_id"], "corpus_id mismatch")
    require(len(sources) == manifest["source_count"], "source_count mismatch")
    require(len(query_doc["queries"]) == manifest["query_count"], "query_count mismatch")

    source_ids = [row["source_id"] for row in sources]
    require(len(source_ids) == len(set(source_ids)), "duplicate source_id")
    source_by_id = {row["source_id"]: row for row in sources}

    wave_sources = defaultdict(list)
    for row in sources:
        wave_sources[row["wave"]].append(row["source_id"])

    require(set(wave_sources) == set(range(manifest["wave_count"])), "source wave set mismatch")

    manifest_source_ids = []
    for wave in manifest["waves"]:
        wid = wave["wave"]
        expected = wave["sources"]
        manifest_source_ids.extend(expected)
        require(sorted(expected) == sorted(wave_sources[wid]), f"manifest/source mismatch for W{wid}")
        require(len(expected) == 3, f"W{wid} must contain exactly 3 sources in C-v0")

    require(sorted(manifest_source_ids) == sorted(source_ids), "manifest does not enumerate every source exactly once")

    facts = ground["facts"]
    fact_ids = [fact["fact_id"] for fact in facts]
    require(len(fact_ids) == len(set(fact_ids)), "duplicate fact_id")
    fact_by_id = {fact["fact_id"]: fact for fact in facts}

    for fact in facts:
        for source_id in fact.get("source_ids", []):
            require(source_id in source_by_id, f"{fact['fact_id']} references missing source {source_id}")
        if "known_from_wave" in fact:
            require(0 <= fact["known_from_wave"] < manifest["wave_count"], f"bad known_from_wave for {fact['fact_id']}")
        if "invalidated_from_wave" in fact:
            require(fact["invalidated_from_wave"] >= fact.get("known_from_wave", 0), f"bad invalidation order for {fact['fact_id']}")

    queries = query_doc["queries"]
    query_ids = [query["query_id"] for query in queries]
    require(len(query_ids) == len(set(query_ids)), "duplicate query_id")
    query_by_id = {query["query_id"]: query for query in queries}

    class_counts = Counter(query["class"] for query in queries)
    expected_classes = set(manifest["query_classes"])
    require(set(class_counts) == expected_classes, "query class set mismatch")
    require(all(count == 5 for count in class_counts.values()), f"expected 5 queries per class, got {class_counts}")

    for query in queries:
        ask_wave = query["ask_after_wave"]
        require(0 <= ask_wave < manifest["wave_count"], f"bad ask_after_wave for {query['query_id']}")

        for fact_id in query.get("required_fact_ids", []):
            require(fact_id in fact_by_id, f"{query['query_id']} references missing fact {fact_id}")
            known = fact_by_id[fact_id].get("known_from_wave", 0)
            require(known <= ask_wave, f"{query['query_id']} asks for {fact_id} before it is knowable")

        for source_id in query.get("required_source_ids", []):
            require(source_id in source_by_id, f"{query['query_id']} references missing source {source_id}")
            require(source_by_id[source_id]["wave"] <= ask_wave, f"{query['query_id']} asks for source {source_id} before arrival")

    # C4 v0 deliberately gates only query classes with sufficiently stable deterministic checks.
    deterministic_checks = deterministic.get("checks")
    require(isinstance(deterministic_checks, dict), "deterministic-checks.json must contain a checks object")
    eligible_classes = {"local_exact", "temporal", "provenance", "negative_uncertainty_delayed"}
    eligible_query_ids = {query["query_id"] for query in queries if query["class"] in eligible_classes}
    require(set(deterministic_checks) == eligible_query_ids, "deterministic check set must equal the 20 regression-eligible queries")

    allowed_rule_keys = {"answer_all", "answer_any", "answer_none", "required_source_ids", "uncertainty_in"}
    for query_id, rule in deterministic_checks.items():
        require(query_id in query_by_id, f"deterministic rule references missing query {query_id}")
        require(isinstance(rule, dict), f"deterministic rule for {query_id} must be an object")
        unknown_keys = set(rule) - allowed_rule_keys
        require(not unknown_keys, f"unknown deterministic rule keys for {query_id}: {sorted(unknown_keys)}")
        for source_id in rule.get("required_source_ids", []):
            require(source_id in source_by_id, f"deterministic rule {query_id} references missing source {source_id}")

    print("Corpus C v0 validation: PASS")
    print(f"  sources: {len(sources)}")
    print(f"  facts:   {len(facts)}")
    print(f"  queries: {len(queries)}")
    print(f"  deterministic regression checks: {len(deterministic_checks)}")
    print(f"  classes: {dict(sorted(class_counts.items()))}")


if __name__ == "__main__":
    main()
