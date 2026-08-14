from __future__ import annotations

import json
import math
import re
from collections import Counter

CONDITIONS = ("P0", "P1", "P2", "P3")
TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
FACT_RE = re.compile(r"Record ([a-z0-9]+) ([a-z_]+) ([a-z0-9-]+)\.")
BM25_K1 = 1.5
BM25_B = 0.75


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in TOKEN_RE.finditer(text)]


def _source_map(topic: dict, wave: str) -> dict[str, dict]:
    key = "w0_sources" if wave == "W0" else "w1_sources"
    return {source["source_id"]: source for source in topic[key]}


def _unit_ref(source: dict, unit_id: str) -> dict:
    for unit in source["units"]:
        if unit["unit_id"] == unit_id:
            return {
                "kind": "raw",
                "source_id": source["source_id"],
                "unit_id": unit["unit_id"],
                "start": unit["start"],
                "end": unit["end"],
            }
    raise KeyError(f"unit_not_found:{source['source_id']}:{unit_id}")


def _derived_section_ref(topic: dict, section_id: str) -> dict:
    for section in topic["derived"]["sections"]:
        if section["section_id"] == section_id:
            return {
                "kind": "derived",
                "source_id": topic["derived"]["source_id"],
                "section_id": section_id,
                "start": section["start"],
                "end": section["end"],
            }
    raise KeyError(f"derived_section_not_found:{section_id}")


def _claim_exact_refs(topic: dict, claim: dict, wave: str) -> list[dict]:
    if wave == "W0":
        return [dict(ref) for ref in claim["cited_exact_refs"]]

    out = []
    for ref in claim["cited_exact_refs"]:
        if ref["kind"] == "derived":
            out.append(dict(ref))
            continue
        fact_key = ref["fact_key"]
        out.append(dict(topic["w1_fact_refs"][fact_key]))
    return out


def _structuralize(topic: dict, claim: dict, ref: dict, wave: str) -> dict:
    if ref["kind"] == "derived":
        return _derived_section_ref(topic, claim["section_id"])
    sources = _source_map(topic, wave)
    return _unit_ref(sources[ref["source_id"]], ref["unit_id"])


def _dedupe_refs(refs: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for ref in refs:
        key = (
            ref["kind"],
            ref["source_id"],
            ref.get("unit_id"),
            ref.get("section_id"),
            ref.get("start"),
            ref.get("end"),
            ref.get("fact_key"),
        )
        if key not in seen:
            seen.add(key)
            out.append(ref)
    out.sort(
        key=lambda ref: (
            ref["kind"], ref["source_id"], str(ref.get("unit_id", "")),
            int(ref.get("start", 0)), int(ref.get("end", 0)),
        )
    )
    return out


def build_condition(topic: dict, condition: str, wave: str = "W0") -> dict:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown_condition:{condition}")
    if wave not in {"W0", "W1"}:
        raise ValueError(f"unknown_wave:{wave}")

    claims = topic["claims"]
    exact_by_claim = {
        claim["claim_id"]: _claim_exact_refs(topic, claim, wave)
        for claim in claims
    }

    page_refs = []
    for claim in claims:
        for ref in exact_by_claim[claim["claim_id"]]:
            page_refs.append({"kind": ref["kind"], "source_id": ref["source_id"]})
    page_refs = _dedupe_refs(page_refs)

    section_refs: dict[str, list[dict]] = {}
    for claim in claims:
        rows = section_refs.setdefault(claim["section_id"], [])
        for ref in exact_by_claim[claim["claim_id"]]:
            rows.append(_structuralize(topic, claim, ref, wave))
    section_refs = {key: _dedupe_refs(rows) for key, rows in section_refs.items()}

    if condition == "P0":
        state = {"condition": condition, "wave": wave, "page_refs": page_refs}
    elif condition == "P1":
        state = {"condition": condition, "wave": wave, "section_refs": section_refs}
    elif condition == "P2":
        state = {
            "condition": condition,
            "wave": wave,
            "claim_refs": {claim_id: _dedupe_refs(rows) for claim_id, rows in exact_by_claim.items()},
        }
    else:
        # P3 is intentionally allowed to read only the frozen risk label to
        # choose precision. It never branches on fault family or gold outcome.
        precise = {
            claim["claim_id"]: _dedupe_refs(exact_by_claim[claim["claim_id"]])
            for claim in claims
            if claim["risk"] == "high"
        }
        state = {
            "condition": condition,
            "wave": wave,
            "section_refs": section_refs,
            "claim_refs": precise,
        }
    return state


def serialized_metadata_bytes(state: dict) -> int:
    return len(json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _claim_refs(topic: dict, claim: dict, state: dict) -> list[dict]:
    condition = state["condition"]
    if condition == "P0":
        return list(state["page_refs"])
    if condition == "P1":
        return list(state["section_refs"][claim["section_id"]])
    if condition == "P2":
        return list(state["claim_refs"][claim["claim_id"]])
    if claim["risk"] == "high":
        return list(state["claim_refs"][claim["claim_id"]])
    return list(state["section_refs"][claim["section_id"]])


def _structural_units_for_sources(topic: dict, source_ids: set[str], wave: str) -> list[dict]:
    sources = _source_map(topic, wave)
    units = []
    for source_id in sorted(source_ids):
        source = sources.get(source_id)
        if not source:
            continue
        for unit in source["units"]:
            units.append(
                {
                    "kind": "raw",
                    "source_id": source_id,
                    "unit_id": unit["unit_id"],
                    "start": unit["start"],
                    "end": unit["end"],
                    "text": source["text"][unit["start"]:unit["end"]],
                }
            )
    return units


def _bm25_rank_units(units: list[dict], claim: dict) -> list[dict]:
    query = " ".join(
        " ".join((atom["subject"], atom["predicate"], atom["value"]))
        for atom in claim["atoms"]
    )
    qtokens = tokenize(query)
    if not units or not qtokens:
        return []
    tokenized = [tokenize(unit["text"]) for unit in units]
    n = len(units)
    avgdl = sum(len(tokens) for tokens in tokenized) / n
    dfs = Counter()
    for tokens in tokenized:
        dfs.update(set(tokens))

    scored = []
    for unit, tokens in zip(units, tokenized):
        tf = Counter(tokens)
        dl = len(tokens)
        score = 0.0
        for term in qtokens:
            if tf[term] == 0:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            denom = tf[term] + BM25_K1 * (1 - BM25_B + BM25_B * dl / avgdl)
            score += idf * (tf[term] * (BM25_K1 + 1)) / denom
        if score > 0:
            scored.append((score, unit))
    scored.sort(key=lambda row: (-row[0], row[1]["source_id"], row[1]["unit_id"]))
    return [row[1] for row in scored]


def _containing_unit(topic: dict, exact_ref: dict, wave: str) -> dict | None:
    if exact_ref["kind"] != "raw":
        return None
    source = _source_map(topic, wave).get(exact_ref["source_id"])
    if source is None:
        return None
    unit_id = exact_ref.get("unit_id")
    if unit_id is not None:
        return _unit_ref(source, unit_id)
    for unit in source["units"]:
        if unit["start"] <= exact_ref["start"] and exact_ref["end"] <= unit["end"]:
            return _unit_ref(source, unit["unit_id"])
    return None


def _inspection_plan(topic: dict, claim: dict, state: dict) -> list[dict]:
    refs = _claim_refs(topic, claim, state)
    condition = state["condition"]
    wave = state["wave"]

    if condition == "P0":
        source_ids = {ref["source_id"] for ref in refs if ref["kind"] == "raw"}
        return _bm25_rank_units(_structural_units_for_sources(topic, source_ids, wave), claim)

    precise = condition == "P2" or (condition == "P3" and claim["risk"] == "high")
    if not precise:
        return sorted(
            refs,
            key=lambda ref: (
                ref["kind"], ref["source_id"], str(ref.get("unit_id", "")), int(ref.get("start", 0))
            ),
        )

    plan = []
    for ref in refs:
        plan.append(ref)
    for ref in refs:
        unit = _containing_unit(topic, ref, wave)
        if unit is not None:
            plan.append(unit)
    return _dedupe_refs(plan)


def _slice_for_ref(topic: dict, ref: dict, wave: str, remaining: int) -> tuple[str, int]:
    if remaining <= 0 or ref["kind"] != "raw":
        return "", 0
    source = _source_map(topic, wave).get(ref["source_id"])
    if source is None:
        return "", 0
    start = int(ref.get("start", 0))
    end = min(int(ref.get("end", start)), start + remaining)
    if end <= start:
        return "", 0
    return source["text"][start:end], end - start


def _observed_statements(texts: list[tuple[str, str]]) -> dict[tuple[str, str], list[tuple[str, str]]]:
    observed: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for source_id, text in texts:
        for match in FACT_RE.finditer(text):
            key = (match.group(1), match.group(2))
            observed.setdefault(key, []).append((match.group(3), source_id))
    return observed


def audit_claim(topic: dict, claim: dict, state: dict, budget: int = 1200) -> dict:
    if budget <= 0:
        raise ValueError("budget_must_be_positive")
    refs = _claim_refs(topic, claim, state)
    raw_ref_count = sum(ref["kind"] == "raw" for ref in refs)
    derived_ref_count = sum(ref["kind"] == "derived" for ref in refs)
    plan = _inspection_plan(topic, claim, state)

    remaining = budget
    inspected: list[tuple[str, str]] = []
    visited_sources: set[str] = set()
    visited_units: set[tuple[str, str]] = set()
    inspected_chars = 0
    seen_intervals: dict[str, list[tuple[int, int]]] = {}

    for ref in plan:
        if remaining <= 0:
            break
        if ref["kind"] != "raw":
            continue
        source_id = ref["source_id"]
        start = int(ref.get("start", 0))
        end = int(ref.get("end", start))
        intervals = seen_intervals.setdefault(source_id, [])
        # If an exact span was already inspected, expanding to its containing
        # unit should charge only newly inspected characters, not overlap twice.
        pieces = [(start, end)]
        for old_start, old_end in intervals:
            next_pieces = []
            for a, b in pieces:
                if b <= old_start or old_end <= a:
                    next_pieces.append((a, b))
                else:
                    if a < old_start:
                        next_pieces.append((a, old_start))
                    if old_end < b:
                        next_pieces.append((old_end, b))
            pieces = next_pieces
        source = _source_map(topic, state["wave"]).get(source_id)
        if source is None:
            continue
        for a, b in pieces:
            if remaining <= 0:
                break
            take_end = min(b, a + remaining)
            if take_end > a:
                text = source["text"][a:take_end]
                inspected.append((source_id, text))
                charged = take_end - a
                inspected_chars += charged
                remaining -= charged
                intervals.append((a, take_end))
        visited_sources.add(source_id)
        if ref.get("unit_id"):
            visited_units.add((source_id, ref["unit_id"]))

    observed = _observed_statements(inspected)
    atom_states = []
    for atom in claim["atoms"]:
        key = (atom["subject"], atom["predicate"])
        rows = observed.get(key, [])
        values = {value for value, _ in rows}
        supporters = {source_id for value, source_id in rows if value == atom["value"]}
        atom_states.append(
            {
                "key": key,
                "values": values,
                "supporters": supporters,
                "asserted_seen": atom["value"] in values,
            }
        )

    if any(len(atom["values"]) > 1 for atom in atom_states):
        outcome = "contested"
    elif atom_states and all(atom["asserted_seen"] for atom in atom_states):
        outcome = "verified"
    elif any(atom["values"] and not atom["asserted_seen"] for atom in atom_states):
        outcome = "invalid_or_unsupported"
    elif raw_ref_count == 0 and derived_ref_count > 0:
        outcome = "invalid_or_unsupported"
    else:
        outcome = "unresolved_budget"

    return {
        "outcome": outcome,
        "inspected_chars": inspected_chars,
        "visited_sources": len(visited_sources),
        "visited_units": len(visited_units),
        "raw_ref_count": raw_ref_count,
        "derived_ref_count": derived_ref_count,
    }


def ownership_exact(topic: dict, claim: dict, state: dict) -> float:
    refs = _claim_refs(topic, claim, state)
    condition = state["condition"]
    precise = condition == "P2" or (condition == "P3" and claim["risk"] == "high")

    intended = [ref["source_id"] for ref in claim["intended_exact_refs"]]
    if precise:
        actual = [ref["source_id"] for ref in refs if ref["kind"] == "raw"]
        if len(actual) != len(claim["atoms"]):
            return 0.0
        return sum(a == b for a, b in zip(actual, intended)) / len(intended)

    raw_sources = {ref["source_id"] for ref in refs if ref["kind"] == "raw"}
    if not intended:
        return 0.0
    return sum(raw_sources == {source_id} for source_id in intended) / len(intended)


def exact_raw_reversible(topic: dict, state: dict) -> bool:
    sources = _source_map(topic, state["wave"])
    refs = []
    if state["condition"] == "P2":
        refs = [ref for rows in state["claim_refs"].values() for ref in rows]
    elif state["condition"] == "P3":
        refs = [ref for rows in state["claim_refs"].values() for ref in rows]
    else:
        return True
    for ref in refs:
        if ref["kind"] != "raw":
            continue
        source = sources.get(ref["source_id"])
        if source is None:
            return False
        start, end = int(ref["start"]), int(ref["end"])
        if not (0 <= start < end <= len(source["text"])):
            return False
        if ref.get("fact_key"):
            expected = source["fact_refs"].get(ref["fact_key"])
            if expected is None or expected["start"] != start or expected["end"] != end:
                return False
    return True


def w1_update_actions(topic: dict, condition: str) -> int:
    state = build_condition(topic, condition, "W0")
    source_map = topic["w1_source_map"]

    def changed(ref: dict) -> int:
        return int(ref["kind"] == "raw" and source_map.get(ref["source_id"], ref["source_id"]) != ref["source_id"])

    if condition == "P0":
        return sum(changed(ref) for ref in state["page_refs"])
    if condition == "P1":
        return sum(changed(ref) for rows in state["section_refs"].values() for ref in rows)
    if condition == "P2":
        return sum(changed(ref) for rows in state["claim_refs"].values() for ref in rows)
    return (
        sum(changed(ref) for rows in state["section_refs"].values() for ref in rows)
        + sum(changed(ref) for rows in state["claim_refs"].values() for ref in rows)
    )


def w1_stale_refs_before_repair(topic: dict, condition: str) -> int:
    return w1_update_actions(topic, condition)


def d1_reattachment_actions(topic: dict, condition: str) -> int:
    claims = topic["claims"]
    old_order = [claim["claim_id"] for claim in claims]
    new_order = topic["derived"]["d1_claim_order"]
    new_pos = {claim_id: i for i, claim_id in enumerate(new_order)}
    moved_claims = {claim_id for i, claim_id in enumerate(old_order) if new_pos[claim_id] != i}

    old_sections = [f"{topic['topic_id'].replace('topic-', 't')}-section-{i}" for i in range(3)]
    # Generator D1 reverses section order, so every non-central section moves.
    moved_sections = {old_sections[0], old_sections[2]}

    if condition == "P0":
        return 0
    if condition == "P1":
        return len(moved_sections)
    if condition == "P2":
        return len(moved_claims)
    high_claims = {claim["claim_id"] for claim in claims if claim["risk"] == "high"}
    return len(moved_sections) + len(moved_claims & high_claims)
