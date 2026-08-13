#!/usr/bin/env python3
"""Generate the deterministic fictional E011 Stage 1A corpus locally."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20260813
VERSION = "E011-CORPUS-GEN-v0"

SCENARIOS = [
    ("T01", "Aster Vale", "archive review interval", "43 days", "58 days", ["quartz envelope", "dual ledger", "northstar shelf", "ember budget"], "Kappa catalog", "Sigma catalog", [0, 1, 3]),
    ("T02", "Briar Delta", "note consolidation interval", "17 days", "25 days", ["cedar quota", "mirror lag", "amber window", "audit braid"], "Orchid index", "Pine index", [0, 2, 3]),
    ("T03", "Copper Finch", "sample review cap", "28 entries", "34 entries", ["mist budget", "copper lane", "hinge latency", "violet reserve"], "Nectar board", "Granite board", [1, 2, 3]),
    ("T04", "Drift Harbor", "reference handoff window", "71 minutes", "95 minutes", ["tide window", "harbor braid", "lantern quota", "frost margin"], "Marlin queue", "Beacon queue", [0, 1, 3]),
    ("T05", "Ember Quill", "document cache cap", "312 pages", "448 pages", ["ember budget", "quill trace", "opal branch", "silent rebuild"], "Cinder graph", "Flint table", [0, 2, 3]),
    ("T06", "Fjord Relay", "annotation retention", "19 days", "31 days", ["fjord window", "relay braid", "moss quota", "glacier tax"], "Narwhal spool", "Otter spool", [0, 1, 3]),
    ("T07", "Grove Atlas", "index refresh interval", "11 minutes", "18 minutes", ["grove boundary", "atlas shard", "fern budget", "compass drift"], "Maple route", "Cedar route", [0, 2, 3]),
    ("T08", "Halo Mint", "device reserve floor", "37 percent", "24 percent", ["halo window", "mint ledger", "cobalt draw", "dawn reserve"], "Lumen duty", "Prism duty", [1, 2, 3]),
    ("T09", "Ibis Foundry", "record batch size", "640 rows", "960 rows", ["ibis lock", "foundry window", "slag budget", "anvil replay"], "Forge ladder", "Kiln ladder", [0, 1, 3]),
    ("T10", "Juniper Echo", "classification confidence floor", "0.82", "0.74", ["juniper boundary", "echo ledger", "saffron quota", "winter fallback"], "Canyon scheme", "Meadow scheme", [0, 2, 3]),
    ("T11", "Kestrel Bloom", "note grouping window", "9 minutes", "14 minutes", ["kestrel window", "bloom budget", "pearl channel", "rook delay"], "Petal bundler", "Thorn bundler", [0, 1, 2]),
    ("T12", "Lumen Reef", "merge divergence cap", "14 records", "22 records", ["lumen boundary", "reef ledger", "coral quota", "night drift"], "Tidal merge", "Beacon merge", [0, 1, 3]),
]

CONSTRAINT_KEYS = ["Alpha", "Beta", "Gamma", "Delta"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def scenario_dict(row: tuple) -> dict:
    topic_id, name, exact_label, current, legacy, factors, chosen, rejected, rationale = row
    return {"topic_id": topic_id, "name": name, "exact_label": exact_label, "current_value": current,
            "legacy_value": legacy, "factors": list(factors), "chosen": chosen, "rejected": rejected,
            "rationale_indices": list(rationale)}


def build_topic(s: dict) -> tuple[list[dict], list[dict]]:
    rng = random.Random(SEED + int(s["topic_id"][1:]))
    source_numbers = list(range(1, 33))
    rng.shuffle(source_numbers)
    docs: list[dict] = []
    role_to_source: dict[str, str] = {}

    def add(role: str, title: str, text: str, small: bool) -> None:
        sid = f"{s['topic_id']}-S{source_numbers[len(docs)]:02d}"
        role_to_source[role] = sid
        docs.append({"source_id": sid, "topic_id": s["topic_id"], "topic_name": s["name"], "role": role,
                     "min_scale": "small" if small else "large", "title": title, "text": text})

    add("exact_current", "Approved reference value",
        f"{s['name']} approval note. The {s['exact_label']} is {s['current_value']}. "
        "This is the current approved value and replaces earlier draft values.", True)

    for i, (key, factor) in enumerate(zip(CONSTRAINT_KEYS, s["factors"])):
        add(f"factor_{i+1}", f"Constraint {key}",
            f"{s['name']} architecture constraint {key}: {factor}. The phrase '{factor}' names a current design constraint. "
            f"Constraint {key} must be considered in architecture decisions.", True)

    rationale_keys = [CONSTRAINT_KEYS[i] for i in s["rationale_indices"]]
    add("decision", "Decision note",
        f"{s['name']} decision note. The team selected {s['chosen']} instead of {s['rejected']}. "
        f"The decision cites Constraint {rationale_keys[0]}, Constraint {rationale_keys[1]}, and Constraint {rationale_keys[2]} "
        "as the three deciding constraints. Use the corresponding constraint notes to recover their names.", True)

    add("legacy_exact", "Retired draft value",
        f"{s['name']} retired draft. An earlier proposal listed the {s['exact_label']} as {s['legacy_value']}. "
        "That proposal was rejected; this value is historical only and is not the approved current value.", True)

    add("peripheral_core", "Coordination note",
        f"{s['name']} coordination note about meeting rotation, checklist ownership, and document formatting. "
        "No approved reference value or architecture constraint was changed.", True)

    for i, (key, factor) in enumerate(zip(CONSTRAINT_KEYS, s["factors"])):
        add(f"factor_echo_{i+1}", f"Constraint {key} follow-up",
            f"{s['name']} follow-up on Constraint {key}. The current constraint remains {factor}. "
            "This note adds implementation detail but does not create a new constraint.", False)

    add("decision_aftermath", "Decision follow-up",
        f"{s['name']} follow-up confirms work proceeded with {s['chosen']}; {s['rejected']} remains the rejected alternative. "
        "This note records status rather than the original rationale.", False)

    add("exact_audit", "Reference audit",
        f"{s['name']} audit observed the approved {s['exact_label']} of {s['current_value']} in the current notes. "
        "The approval note remains the authoritative first statement.", False)

    for j, label in enumerate(["Amber", "Birch", "Cobalt", "Dune"], start=1):
        add(f"retired_alt_{j}", f"Retired alternative {j}",
            f"{s['name']} retired architecture memo {j}. It compares {s['rejected']} with experimental path {label}-{j}. "
            "It uses the words decision, rationale, and constraint, but it is not the accepted decision note.", False)

    lexical_phrases = ["architecture constraint inventory", "decision rationale checklist", "approved architecture review",
                       "constraint mapping workshop", "decision history index", "architecture rationale glossary"]
    for j, phrase in enumerate(lexical_phrases, start=1):
        add(f"lexical_noise_{j}", f"Reference index {j}",
            f"{s['name']} {phrase}. This administrative reference discusses how to document constraints and decisions. "
            "It does not state the current reference value, the four named constraints, or the accepted decision rationale.", False)

    peripheral = ["label naming", "meeting rotation", "fixture cleanup", "dashboard layout", "calendar notes",
                  "handoff checklist", "repository labels", "training example inventory"]
    for j, subject in enumerate(peripheral, start=1):
        add(f"peripheral_{j}", f"Peripheral note {j}",
            f"{s['name']} peripheral note about {subject}. This is housekeeping material and does not change the approved topic facts.", False)

    if len(docs) != 32 or sum(d["min_scale"] == "small" for d in docs) != 8:
        raise AssertionError(f"bad document counts for {s['topic_id']}")

    exact = {"query_id": f"{s['topic_id']}-Q1", "topic_id": s["topic_id"], "class": "exact_provenance",
             "question": f"What is the current value of the {s['exact_label']} for {s['name']}, and which approval source first states it?",
             "required_signals": [s["current_value"].lower()], "required_source_ids": [role_to_source["exact_current"]]}
    global_q = {"query_id": f"{s['topic_id']}-Q2", "topic_id": s["topic_id"], "class": "global_synthesis",
                "question": f"What are the four named current architecture constraints for {s['name']}? Name all four.",
                "required_signals": [x.lower() for x in s["factors"]], "required_source_ids": []}
    rationale = [s["factors"][i].lower() for i in s["rationale_indices"]]
    decision = {"query_id": f"{s['topic_id']}-Q3", "topic_id": s["topic_id"], "class": "decision_rationale",
                "question": f"Why did {s['name']} choose {s['chosen']} rather than {s['rejected']}? Name the chosen option and the three deciding constraints.",
                "required_signals": [s["chosen"].lower()] + rationale, "required_source_ids": []}
    return docs, [exact, global_q, decision]


def generate() -> tuple[list[dict], list[dict]]:
    docs: list[dict] = []
    queries: list[dict] = []
    for row in SCENARIOS:
        d, q = build_topic(scenario_dict(row))
        docs.extend(d)
        queries.extend(q)
    docs.sort(key=lambda x: x["source_id"])
    queries.sort(key=lambda x: x["query_id"])
    return docs, queries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(ROOT / "generated"))
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    docs, queries = generate()
    docs_data = jsonl_bytes(docs)
    queries_data = (json.dumps(queries, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (out / "documents.jsonl").write_bytes(docs_data)
    (out / "queries.json").write_bytes(queries_data)
    manifest = {"format": VERSION, "seed": SEED, "topic_count": 12, "documents_total": len(docs),
                "documents_small": sum(d["min_scale"] == "small" for d in docs), "queries": len(queries),
                "documents_sha256": sha256_bytes(docs_data), "queries_sha256": sha256_bytes(queries_data)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E011-CORPUS-GENERATED-v0")
    print(f"topics={manifest['topic_count']} docs={manifest['documents_total']} smallDocs={manifest['documents_small']} queries={manifest['queries']}")
    print(f"docsSha={manifest['documents_sha256']} queriesSha={manifest['queries_sha256']}")


if __name__ == "__main__":
    main()
