#!/usr/bin/env python3
"""Generate deterministic E012 maintenance waves from the frozen E011 large corpus."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E011 = ROOT.parent / "E011-persistent-compilation-value-gate"

spec = importlib.util.spec_from_file_location("e011_corpus", E011 / "generate_corpus.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load E011 corpus generator")
e011 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e011)

VERSION = "E012-CORPUS-GEN-v0"
WAVES = (0, 1, 2)
REVISED_FACTORS = [
    "silver cadence", "river checksum", "linen horizon", "cinder waypoint",
    "opal cadence", "moss circuit", "fern threshold", "dawn ledger",
    "anvil cadence", "saffron boundary", "pearl reserve", "coral cadence",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows) + "\n").encode("utf-8")


def _number_values(value: str, index: int) -> tuple[str, str]:
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)(.*)$", value)
    if not m:
        raise ValueError(value)
    raw, suffix = m.groups()
    if "." in raw:
        base = float(raw)
        w1 = max(0.01, base - 0.03)
        w2 = w1 + 0.01
        return f"{w1:.2f}{suffix}", f"{w2:.2f}{suffix}"
    base = int(raw)
    delta = 2 + (index % 4)
    w1 = base + delta
    w2 = w1 - 1
    return f"{w1}{suffix}", f"{w2}{suffix}"


def _baseline_maps() -> tuple[dict[str, list[dict]], dict[str, dict], dict[str, dict]]:
    docs, queries = e011.generate()
    by_topic: dict[str, list[dict]] = {}
    qmap: dict[str, dict] = {}
    for d in docs:
        by_topic.setdefault(d["topic_id"], []).append({**d, "wave": 0})
    for q in queries:
        qmap[q["query_id"]] = q
    scenarios = {e011.scenario_dict(row)["topic_id"]: e011.scenario_dict(row) for row in e011.SCENARIOS}
    return by_topic, qmap, scenarios


def _role_source(docs: list[dict], role: str) -> str:
    rows = [d for d in docs if d.get("role") == role]
    if len(rows) != 1:
        raise AssertionError((role, len(rows)))
    return rows[0]["source_id"]


def generate() -> tuple[list[dict], list[dict]]:
    baseline, _, scenarios = _baseline_maps()
    all_docs: list[dict] = []
    all_queries: list[dict] = []

    for topic_index, topic in enumerate(sorted(baseline), start=1):
        s = scenarios[topic]
        docs = sorted(baseline[topic], key=lambda d: d["source_id"])
        if len(docs) != 32:
            raise AssertionError((topic, len(docs)))
        w1_value, w2_value = _number_values(s["current_value"], topic_index)
        revised = REVISED_FACTORS[topic_index - 1]
        old_factor = s["factors"][0]
        current_factors = [revised] + list(s["factors"][1:])
        old_rationale = list(s["rationale_indices"])
        omitted = next(iter({0, 1, 2, 3} - set(old_rationale)))
        new_rationale = sorted((set(old_rationale) - {old_rationale[0]}) | {omitted})

        w1_exact_sid = f"{topic}-S33"
        w1_decision_sid = f"{topic}-S34"
        w2_exact_sid = f"{topic}-S35"
        w2_decision_sid = f"{topic}-S36"

        updates = [
            {
                "source_id": w1_exact_sid, "topic_id": topic, "topic_name": s["name"],
                "role": "w1_supersession", "min_scale": "large", "wave": 1,
                "title": "Wave 1 approved update",
                "text": (
                    f"{s['name']} wave 1 approved update. Effective now, the current {s['exact_label']} is {w1_value}, "
                    f"superseding the previously approved {s['current_value']}. Constraint Alpha is now {revised}; "
                    f"the earlier Constraint Alpha value {old_factor} is historical. Constraints Beta, Gamma, and Delta remain unchanged."
                ),
            },
            {
                "source_id": w1_decision_sid, "topic_id": topic, "topic_name": s["name"],
                "role": "w1_decision_review", "min_scale": "large", "wave": 1,
                "title": "Wave 1 decision review",
                "text": (
                    f"{s['name']} wave 1 decision review. The current selected option remains {s['chosen']} rather than {s['rejected']}. "
                    f"The current decision rationale cites Constraint {e011.CONSTRAINT_KEYS[old_rationale[0]]}, "
                    f"Constraint {e011.CONSTRAINT_KEYS[old_rationale[1]]}, and Constraint {e011.CONSTRAINT_KEYS[old_rationale[2]]}; "
                    "interpret those keys using the current constraint definitions."
                ),
            },
            {
                "source_id": w2_exact_sid, "topic_id": topic, "topic_name": s["name"],
                "role": "w2_correction", "min_scale": "large", "wave": 2,
                "title": "Wave 2 correction",
                "text": (
                    f"{s['name']} wave 2 correction. The wave 1 exact value {w1_value} was a transcription error. "
                    f"The corrected current {s['exact_label']} is {w2_value}. The wave 1 Constraint Alpha update to {revised} remains valid. "
                    f"Older exact values, including {s['current_value']} and {w1_value}, are not current."
                ),
            },
            {
                "source_id": w2_decision_sid, "topic_id": topic, "topic_name": s["name"],
                "role": "w2_decision_supersession", "min_scale": "large", "wave": 2,
                "title": "Wave 2 decision supersession",
                "text": (
                    f"{s['name']} wave 2 decision update. The current selected option is now {s['rejected']}, superseding {s['chosen']}. "
                    f"The earlier selection of {s['chosen']} remains historical. The current decision cites Constraint "
                    f"{e011.CONSTRAINT_KEYS[new_rationale[0]]}, Constraint {e011.CONSTRAINT_KEYS[new_rationale[1]]}, and "
                    f"Constraint {e011.CONSTRAINT_KEYS[new_rationale[2]]}; use current constraint definitions for their names."
                ),
            },
        ]
        all_docs.extend(docs + updates)

        baseline_decision_source = _role_source(docs, "decision")
        wave_specs = {
            0: {
                "value": s["current_value"], "exact_source": _role_source(docs, "exact_current"),
                "factors": list(s["factors"]), "choice": s["chosen"], "prior": s["rejected"],
                "rationale": old_rationale, "decision_source": baseline_decision_source, "superseded": False,
            },
            1: {
                "value": w1_value, "exact_source": w1_exact_sid,
                "factors": current_factors, "choice": s["chosen"], "prior": s["rejected"],
                "rationale": old_rationale, "decision_source": w1_decision_sid, "superseded": False,
            },
            2: {
                "value": w2_value, "exact_source": w2_exact_sid,
                "factors": current_factors, "choice": s["rejected"], "prior": s["chosen"],
                "rationale": new_rationale, "decision_source": w2_decision_sid, "superseded": True,
            },
        }

        exact_values = (s["current_value"], w1_value, w2_value)
        for wave in WAVES:
            x = wave_specs[wave]
            qprefix = f"{topic}-W{wave}"
            all_queries.append({
                "query_id": f"{qprefix}-Q1", "topic_id": topic, "wave": wave, "class": "current_exact",
                "question": f"At wave {wave}, what is the current {s['exact_label']} for {s['name']}, and which source states the current value?",
                "required_signals": [x["value"].lower()], "required_source_ids": [x["exact_source"]],
                "forbidden_current_signals": [v.lower() for v in exact_values if v != x["value"]],
            })
            all_queries.append({
                "query_id": f"{qprefix}-Q2", "topic_id": topic, "wave": wave, "class": "current_synthesis",
                "question": f"At wave {wave}, what are the four current named architecture constraints for {s['name']}? Name all four.",
                "required_signals": [v.lower() for v in x["factors"]], "required_source_ids": [],
                "forbidden_current_signals": ([old_factor.lower()] if wave >= 1 else [revised.lower()]),
            })
            rationale_names = [x["factors"][i].lower() for i in x["rationale"]]
            if x["superseded"]:
                question = (
                    f"At wave {wave}, what option is currently selected for {s['name']}, which earlier selected option did it supersede, "
                    "and which three current constraints support the current decision?"
                )
                required = [x["choice"].lower(), x["prior"].lower()] + rationale_names
            else:
                question = (
                    f"At wave {wave}, what option is currently selected for {s['name']} rather than the alternative, "
                    "and which three current constraints support that decision?"
                )
                required = [x["choice"].lower()] + rationale_names
            all_queries.append({
                "query_id": f"{qprefix}-Q3", "topic_id": topic, "wave": wave, "class": "decision_history",
                "question": question, "required_signals": required, "required_source_ids": [x["decision_source"]],
                "forbidden_current_signals": [],
            })

    all_docs.sort(key=lambda x: (x["topic_id"], x["source_id"]))
    all_queries.sort(key=lambda x: x["query_id"])
    return all_docs, all_queries


def docs_through_wave(docs: list[dict], topic_id: str, wave: int) -> list[dict]:
    return sorted([d for d in docs if d["topic_id"] == topic_id and int(d["wave"]) <= wave], key=lambda d: d["source_id"])


def main() -> None:
    docs, queries = generate()
    dbytes = jsonl_bytes(docs)
    qbytes = (json.dumps(queries, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    print("E012-CORPUS-GENERATED-v0")
    print(f"topics=12 finalDocs={len(docs)} queries={len(queries)} waves=3")
    print(f"docsSha={sha256_bytes(dbytes)}")
    print(f"queriesSha={sha256_bytes(qbytes)}")


if __name__ == "__main__":
    main()
