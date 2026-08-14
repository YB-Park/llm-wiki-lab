from __future__ import annotations

import hashlib
import json
import random
from collections import Counter

FORMAT = "llm-wiki-e004-provenance-corpus-v0"
SEED = 20260830
TOPIC_COUNT = 24
SOURCES_PER_TOPIC = 6
SECTIONS_PER_TOPIC = 3
CLAIMS_PER_SECTION = 4
CLAIMS_PER_TOPIC = SECTIONS_PER_TOPIC * CLAIMS_PER_SECTION

FAMILIES = (
    "clean",
    "wrong_value",
    "wrong_source",
    "derived_only",
    "within_source_conflict",
    "multi_source_misownership",
)
PREDICATES = ("quota", "deadline", "owner", "mode", "limit", "channel")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_date(value: str) -> bool:
    parts = value.split("-")
    return len(parts) == 3 and all(part.isdigit() for part in parts)


def _value(topic_i: int, claim_i: int, atom_i: int) -> str:
    selector = (topic_i + claim_i + atom_i) % 4
    if selector == 0:
        return str(100 + topic_i * 7 + claim_i * 3 + atom_i)
    if selector == 1:
        month = ((topic_i + claim_i) % 9) + 1
        day = ((claim_i * 2 + atom_i + 3) % 24) + 1
        return f"2026-{month:02d}-{day:02d}"
    if selector == 2:
        return f"team{(topic_i + claim_i + atom_i) % 9}"
    return f"mode{(topic_i * 3 + claim_i + atom_i) % 11}"


def _alternate(value: str) -> str:
    if value.isdigit():
        return str(int(value) + 17)
    if _is_date(value):
        year, month, day = [int(x) for x in value.split("-")]
        return f"{year:04d}-{month:02d}-{min(28, day + 2):02d}"
    if value.startswith("team"):
        return f"team{(int(value[4:]) + 4) % 9}"
    if value.startswith("mode"):
        return f"mode{(int(value[4:]) + 5) % 11}"
    return value + "x"


def _fact_sentence(atom: dict) -> str:
    return f"Record {atom['subject']} {atom['predicate']} {atom['value']}."


def _filler(topic_i: int, source_i: int, unit_i: int, revision: int) -> str:
    words = (
        "archive", "review", "context", "meeting", "background", "ledger",
        "planning", "summary", "routine", "reference", "notes", "catalog",
        "history", "workspace", "discussion", "checkpoint",
    )
    offset = (topic_i * 5 + source_i * 3 + unit_i + revision) % len(words)
    seq = [words[(offset + j) % len(words)] for j in range(18)]
    return (
        "Background " + " ".join(seq[:9]) + ". "
        + "Operational notes " + " ".join(seq[9:]) + ". "
        + "This paragraph records ordinary surrounding material without changing the stated record below."
    )


def _render_source(topic_i: int, source_i: int, source_id: str, unit_specs: list[dict], revision: int) -> dict:
    parts: list[str] = []
    units: list[dict] = []
    fact_refs: dict[str, dict] = {}
    cursor = 0

    intro = (
        f"# Notebook {topic_i + 1}-{source_i + 1}\n"
        f"Routine source revision {revision} for a synthetic project notebook.\n\n"
    )
    parts.append(intro)
    cursor += len(intro)

    for unit_i, spec in enumerate(unit_specs):
        heading = f"## Entry {unit_i + 1}\n"
        filler = _filler(topic_i, source_i, unit_i, revision)
        control = ""
        if source_i == 1:
            control_value = "amber" if revision == 0 else "blue"
            control = f" Control register color {control_value}."
        elif source_i == 2:
            if revision == 0:
                control = " Control register state steady."
            else:
                control = " Control register state steady. Control register state disputed."
        prefix = heading + filler + control + "\n"
        unit_start = cursor
        parts.append(prefix)
        cursor += len(prefix)

        local_fact_keys = []
        for fact in spec["facts"]:
            sentence = _fact_sentence(fact["atom"])
            start = cursor
            parts.append(sentence + "\n")
            cursor += len(sentence) + 1
            fact_refs[fact["fact_key"]] = {
                "kind": "raw",
                "source_id": source_id,
                "unit_id": spec["unit_key"],
                "start": start,
                "end": start + len(sentence),
                "fact_key": fact["fact_key"],
            }
            local_fact_keys.append(fact["fact_key"])
        end = cursor
        parts.append("\n")
        cursor += 1
        units.append(
            {
                "unit_id": spec["unit_key"],
                "start": unit_start,
                "end": end,
                "fact_keys": local_fact_keys,
            }
        )

    text = "".join(parts)
    return {
        "source_id": source_id,
        "kind": "raw",
        "revision": revision,
        "sha256": _sha(text),
        "text": text,
        "units": units,
        "fact_refs": fact_refs,
    }


def _claim_text(atoms: list[dict]) -> str:
    return " ".join(
        f"{atom['subject']} {atom['predicate']} is {atom['value']}."
        for atom in atoms
    )


def build_topic(topic_i: int) -> dict:
    rng = random.Random(SEED + topic_i * 101)
    unit_specs: list[list[dict]] = [[] for _ in range(SOURCES_PER_TOPIC)]
    claims: list[dict] = []
    claim_fact_keys: dict[str, dict] = {}

    def add_fact(source_i: int, unit_key: str, fact_key: str, atom: dict) -> None:
        for unit in unit_specs[source_i]:
            if unit["unit_key"] == unit_key:
                unit["facts"].append({"fact_key": fact_key, "atom": atom})
                return
        unit_specs[source_i].append(
            {"unit_key": unit_key, "facts": [{"fact_key": fact_key, "atom": atom}]}
        )

    for claim_i in range(CLAIMS_PER_TOPIC):
        family = FAMILIES[(claim_i + topic_i) % len(FAMILIES)]
        # Each family occurs once in the first six rows and once in the second
        # six rows, so every family is represented once at each frozen risk.
        risk = "high" if claim_i < len(FAMILIES) else "low"
        primary = (claim_i + topic_i) % SOURCES_PER_TOPIC
        wrong = (primary + 1) % SOURCES_PER_TOPIC
        secondary = (primary + 2) % SOURCES_PER_TOPIC

        base1 = {
            "subject": f"item{topic_i:02d}{claim_i:02d}a",
            "predicate": PREDICATES[(topic_i + claim_i) % len(PREDICATES)],
            "value": _value(topic_i, claim_i, 0),
        }
        asserted1 = dict(base1)
        correct1 = f"t{topic_i}-c{claim_i}-a-correct"
        add_fact(primary, f"u-c{claim_i}-a", correct1, base1)

        cited = [correct1]
        intended = [correct1]
        atoms = [asserted1]

        if family == "wrong_value":
            asserted1["value"] = _alternate(base1["value"])
        elif family == "wrong_source":
            decoy_atom = dict(base1)
            decoy_atom["value"] = _alternate(base1["value"])
            decoy = f"t{topic_i}-c{claim_i}-a-decoy"
            add_fact(wrong, f"u-c{claim_i}-decoy", decoy, decoy_atom)
            cited = [decoy]
        elif family == "derived_only":
            cited = ["derived"]
        elif family == "within_source_conflict":
            conflict_atom = dict(base1)
            conflict_atom["value"] = _alternate(base1["value"])
            conflict = f"t{topic_i}-c{claim_i}-a-conflict"
            # Competing passages share one structural unit, so precise audit
            # must expand around its exact span rather than hiding the conflict.
            add_fact(primary, f"u-c{claim_i}-a", conflict, conflict_atom)
        elif family == "multi_source_misownership":
            base2 = {
                "subject": f"item{topic_i:02d}{claim_i:02d}b",
                "predicate": PREDICATES[(topic_i + claim_i + 3) % len(PREDICATES)],
                "value": _value(topic_i, claim_i, 1),
            }
            correct2 = f"t{topic_i}-c{claim_i}-b-correct"
            add_fact(secondary, f"u-c{claim_i}-b", correct2, base2)
            decoy2_atom = dict(base2)
            decoy2_atom["value"] = _alternate(base2["value"])
            decoy2 = f"t{topic_i}-c{claim_i}-b-decoy"
            add_fact(wrong, f"u-c{claim_i}-b-decoy", decoy2, decoy2_atom)
            atoms.append(dict(base2))
            cited = [correct1, decoy2]
            intended = [correct1, correct2]

        claim_id = f"t{topic_i}-claim-{claim_i}"
        claim_fact_keys[claim_id] = {"cited": list(cited), "intended": list(intended)}
        claims.append(
            {
                "claim_id": claim_id,
                "section_id": f"t{topic_i}-section-{claim_i // CLAIMS_PER_SECTION}",
                "risk": risk,
                "fault_family": family,
                "text": _claim_text(atoms),
                "atoms": atoms,
                "gold_outcome": {
                    "clean": "verified",
                    "wrong_value": "invalid_or_unsupported",
                    "wrong_source": "invalid_or_unsupported",
                    "derived_only": "invalid_or_unsupported",
                    "within_source_conflict": "contested",
                    "multi_source_misownership": "invalid_or_unsupported",
                }[family],
            }
        )

    for source_i in range(SOURCES_PER_TOPIC):
        if not unit_specs[source_i]:
            unit_specs[source_i].append({"unit_key": f"u-neutral-{source_i}", "facts": []})
        rng.shuffle(unit_specs[source_i])

    w0_sources: list[dict] = []
    w1_sources: list[dict] = []
    w0_fact_refs: dict[str, dict] = {}
    w1_fact_refs: dict[str, dict] = {}
    w1_source_map: dict[str, str] = {}

    for source_i in range(SOURCES_PER_TOPIC):
        sid0 = f"src-t{topic_i:02d}-s{source_i}-r0"
        src0 = _render_source(topic_i, source_i, sid0, unit_specs[source_i], revision=0)
        w0_sources.append(src0)
        w0_fact_refs.update(src0["fact_refs"])

        if source_i < 3:
            sid1 = f"src-t{topic_i:02d}-s{source_i}-r1"
            src1 = _render_source(topic_i, source_i, sid1, unit_specs[source_i], revision=1)
            w1_sources.append(src1)
            w1_fact_refs.update(src1["fact_refs"])
            w1_source_map[sid0] = sid1
        else:
            w1_sources.append(src0)
            w1_fact_refs.update(src0["fact_refs"])
            w1_source_map[sid0] = sid0

    derived_id = f"derived-t{topic_i:02d}-r0"
    derived_sections = []
    first = f"# Project digest {topic_i + 1}\n\n"
    derived_text_parts = [first]
    cursor = len(first)
    for section_i in range(SECTIONS_PER_TOPIC):
        heading = f"## Summary {section_i + 1}\n"
        start = cursor
        derived_text_parts.append(heading)
        cursor += len(heading)
        section_claims = [c for c in claims if c["section_id"].endswith(str(section_i))]
        for claim in section_claims:
            line = claim["text"] + "\n"
            claim["derived_start"] = cursor
            claim["derived_end"] = cursor + len(line) - 1
            derived_text_parts.append(line)
            cursor += len(line)
        end = cursor
        derived_text_parts.append("\n")
        cursor += 1
        derived_sections.append(
            {"section_id": f"t{topic_i}-section-{section_i}", "start": start, "end": end}
        )
    derived_text = "".join(derived_text_parts)

    for claim in claims:
        keys = claim_fact_keys[claim["claim_id"]]
        cited_refs = []
        for key in keys["cited"]:
            if key == "derived":
                cited_refs.append(
                    {
                        "kind": "derived",
                        "source_id": derived_id,
                        "start": claim["derived_start"],
                        "end": claim["derived_end"],
                    }
                )
            else:
                cited_refs.append(dict(w0_fact_refs[key]))
        claim["cited_exact_refs"] = cited_refs
        claim["intended_exact_refs"] = [dict(w0_fact_refs[key]) for key in keys["intended"]]
        claim["intended_fact_keys"] = list(keys["intended"])

    d1_order = []
    for section_i in reversed(range(SECTIONS_PER_TOPIC)):
        section_claims = [c["claim_id"] for c in claims if c["section_id"].endswith(str(section_i))]
        d1_order.extend(reversed(section_claims))

    return {
        "topic_id": f"topic-{topic_i:02d}",
        "w0_sources": w0_sources,
        "w1_sources": w1_sources,
        "w1_source_map": w1_source_map,
        "w1_fact_refs": w1_fact_refs,
        "derived": {
            "source_id": derived_id,
            "kind": "derived",
            "text": derived_text,
            "sha256": _sha(derived_text),
            "sections": derived_sections,
            "d1_claim_order": d1_order,
        },
        "claims": claims,
    }


def build_corpus() -> dict:
    topics = [build_topic(i) for i in range(TOPIC_COUNT)]
    return {
        "format": FORMAT,
        "seed": SEED,
        "topic_count": TOPIC_COUNT,
        "claim_count": TOPIC_COUNT * CLAIMS_PER_TOPIC,
        "topics": topics,
    }


def canonical_json(corpus: dict) -> str:
    return json.dumps(corpus, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def corpus_sha256(corpus: dict) -> str:
    return hashlib.sha256(canonical_json(corpus).encode("utf-8")).hexdigest()


def shape_summary(corpus: dict) -> dict:
    families = Counter()
    risk = Counter()
    cross = Counter()
    for topic in corpus["topics"]:
        for claim in topic["claims"]:
            families[claim["fault_family"]] += 1
            risk[claim["risk"]] += 1
            cross[(claim["fault_family"], claim["risk"])] += 1
    return {
        "topics": corpus["topic_count"],
        "claims": corpus["claim_count"],
        "families": dict(sorted(families.items())),
        "risk": dict(sorted(risk.items())),
        "family_risk": {f"{k[0]}:{k[1]}": v for k, v in sorted(cross.items())},
        "sha256": corpus_sha256(corpus),
    }


if __name__ == "__main__":
    corpus = build_corpus()
    print(json.dumps(shape_summary(corpus), ensure_ascii=False, sort_keys=True))
