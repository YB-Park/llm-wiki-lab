from __future__ import annotations

import copy
import hashlib
import re
from collections import Counter

from generate_corpus import (
    CLAIMS_PER_TOPIC,
    FAMILIES,
    FORMAT,
    SECTIONS_PER_TOPIC,
    SEED,
    SOURCES_PER_TOPIC,
    TOPIC_COUNT,
    build_corpus,
    canonical_json,
    corpus_sha256,
)
from provenance_v0 import (
    CONDITIONS,
    FACT_RE,
    audit_claim,
    build_condition,
    exact_raw_reversible,
)

EXPECTED_CORPUS_SHA256 = "FREEZE_PENDING"
FORBIDDEN_RAW_MARKERS = (
    "gold",
    "fault",
    "wrong_value",
    "wrong_source",
    "derived_only",
    "within_source_conflict",
    "multi_source_misownership",
    "condition=p0",
    "condition=p1",
    "condition=p2",
    "condition=p3",
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_lookup(topic: dict, wave: str = "W0") -> dict[str, dict]:
    key = "w0_sources" if wave == "W0" else "w1_sources"
    return {source["source_id"]: source for source in topic[key]}


def _assert_ref_reversible(topic: dict, ref: dict, *, wave: str = "W0") -> None:
    if ref["kind"] == "derived":
        text = topic["derived"]["text"]
        assert ref["source_id"] == topic["derived"]["source_id"]
        assert 0 <= ref["start"] < ref["end"] <= len(text)
        assert text[ref["start"]:ref["end"]].strip()
        return

    source = _source_lookup(topic, wave)[ref["source_id"]]
    assert 0 <= ref["start"] < ref["end"] <= len(source["text"])
    exact = source["text"][ref["start"]:ref["end"]]
    assert FACT_RE.fullmatch(exact)
    if ref.get("fact_key"):
        canonical = source["fact_refs"][ref["fact_key"]]
        assert canonical["start"] == ref["start"]
        assert canonical["end"] == ref["end"]
        assert canonical["unit_id"] == ref["unit_id"]


def _assert_source_structure(source: dict) -> None:
    assert source["sha256"] == _sha(source["text"])
    lower = source["text"].casefold()
    for marker in FORBIDDEN_RAW_MARKERS:
        assert marker not in lower
    unit_ids = set()
    for unit in source["units"]:
        assert unit["unit_id"] not in unit_ids
        unit_ids.add(unit["unit_id"])
        assert 0 <= unit["start"] < unit["end"] <= len(source["text"])
        assert source["text"][unit["start"]:unit["end"]].strip()
        for fact_key in unit["fact_keys"]:
            ref = source["fact_refs"][fact_key]
            assert ref["unit_id"] == unit["unit_id"]
            assert unit["start"] <= ref["start"] < ref["end"] <= unit["end"]
            assert FACT_RE.fullmatch(source["text"][ref["start"]:ref["end"]])
    assert set(source["fact_refs"]) == {
        fact_key for unit in source["units"] for fact_key in unit["fact_keys"]
    }


def _fact_values(source: dict, unit_id: str, subject: str, predicate: str) -> set[str]:
    unit = next(unit for unit in source["units"] if unit["unit_id"] == unit_id)
    text = source["text"][unit["start"]:unit["end"]]
    return {
        match.group(3)
        for match in FACT_RE.finditer(text)
        if match.group(1) == subject and match.group(2) == predicate
    }


def validate_heldout_structure_only() -> str:
    corpus = build_corpus()
    assert corpus["format"] == FORMAT
    assert corpus["seed"] == SEED
    assert corpus["topic_count"] == TOPIC_COUNT == 24
    assert corpus["claim_count"] == TOPIC_COUNT * CLAIMS_PER_TOPIC == 288

    actual_sha = corpus_sha256(corpus)
    if EXPECTED_CORPUS_SHA256 != "FREEZE_PENDING":
        assert actual_sha == EXPECTED_CORPUS_SHA256

    global_family = Counter()
    global_risk = Counter()
    global_cross = Counter()

    for topic in corpus["topics"]:
        assert len(topic["w0_sources"]) == SOURCES_PER_TOPIC == 6
        assert len(topic["w1_sources"]) == SOURCES_PER_TOPIC == 6
        assert len(topic["claims"]) == CLAIMS_PER_TOPIC == 12
        assert len(topic["derived"]["sections"]) == SECTIONS_PER_TOPIC == 3
        assert topic["derived"]["sha256"] == _sha(topic["derived"]["text"])

        family = Counter(claim["fault_family"] for claim in topic["claims"])
        risk = Counter(claim["risk"] for claim in topic["claims"])
        cross = Counter((claim["fault_family"], claim["risk"]) for claim in topic["claims"])
        assert family == Counter({name: 2 for name in FAMILIES})
        assert risk == Counter({"high": 6, "low": 6})
        assert cross == Counter({(name, level): 1 for name in FAMILIES for level in ("high", "low")})
        global_family.update(family)
        global_risk.update(risk)
        global_cross.update(cross)

        w0 = _source_lookup(topic, "W0")
        w1 = _source_lookup(topic, "W1")
        assert len(w0) == 6 and len(w1) == 6
        for source in topic["w0_sources"]:
            _assert_source_structure(source)
        for source in topic["w1_sources"]:
            _assert_source_structure(source)

        assert len(topic["w1_source_map"]) == 6
        changed = sum(old != new for old, new in topic["w1_source_map"].items())
        assert changed == 3
        w0_fact_keys = {key for source in topic["w0_sources"] for key in source["fact_refs"]}
        w1_fact_keys = {key for source in topic["w1_sources"] for key in source["fact_refs"]}
        assert w0_fact_keys == w1_fact_keys == set(topic["w1_fact_refs"])

        old_order = [claim["claim_id"] for claim in topic["claims"]]
        new_order = topic["derived"]["d1_claim_order"]
        assert len(new_order) == len(old_order)
        assert set(new_order) == set(old_order)
        assert new_order != old_order

        before = canonical_json(topic)
        for claim in topic["claims"]:
            assert claim["risk"] in {"high", "low"}
            assert claim["fault_family"] in FAMILIES
            assert claim["gold_outcome"] in {
                "verified", "invalid_or_unsupported", "contested", "unresolved_budget"
            }
            assert claim["atoms"]
            assert claim["cited_exact_refs"]
            assert claim["intended_exact_refs"]
            for ref in claim["cited_exact_refs"]:
                _assert_ref_reversible(topic, ref, wave="W0")
            for ref in claim["intended_exact_refs"]:
                _assert_ref_reversible(topic, ref, wave="W0")

            family_name = claim["fault_family"]
            cited_raw = [ref for ref in claim["cited_exact_refs"] if ref["kind"] == "raw"]
            intended_raw = claim["intended_exact_refs"]
            if family_name == "clean":
                assert [ref["source_id"] for ref in cited_raw] == [ref["source_id"] for ref in intended_raw]
            elif family_name == "wrong_source":
                assert len(cited_raw) == len(intended_raw) == 1
                assert cited_raw[0]["source_id"] != intended_raw[0]["source_id"]
            elif family_name == "derived_only":
                assert all(ref["kind"] == "derived" for ref in claim["cited_exact_refs"])
                assert all(ref["kind"] == "raw" for ref in intended_raw)
            elif family_name == "wrong_value":
                assert len(claim["atoms"]) == 1 and len(cited_raw) == 1
                source = w0[cited_raw[0]["source_id"]]
                observed = FACT_RE.fullmatch(source["text"][cited_raw[0]["start"]:cited_raw[0]["end"]])
                assert observed is not None
                assert observed.group(3) != claim["atoms"][0]["value"]
            elif family_name == "within_source_conflict":
                assert len(claim["atoms"]) == 1 and len(cited_raw) == 1
                ref = cited_raw[0]
                source = w0[ref["source_id"]]
                atom = claim["atoms"][0]
                values = _fact_values(source, ref["unit_id"], atom["subject"], atom["predicate"])
                assert atom["value"] in values and len(values) == 2
            elif family_name == "multi_source_misownership":
                assert len(claim["atoms"]) == len(cited_raw) == len(intended_raw) == 2
                assert cited_raw[0]["source_id"] == intended_raw[0]["source_id"]
                assert cited_raw[1]["source_id"] != intended_raw[1]["source_id"]

        # P3 must not depend on fault-family/gold fields. Remove them entirely
        # and require construction to stay byte-deterministic from risk + refs.
        stripped = copy.deepcopy(topic)
        for claim in stripped["claims"]:
            claim.pop("fault_family", None)
            claim.pop("gold_outcome", None)
        p3_a = build_condition(stripped, "P3", "W0")
        p3_b = build_condition(stripped, "P3", "W0")
        assert p3_a == p3_b

        for condition in CONDITIONS:
            state = build_condition(topic, condition, "W0")
            if condition in {"P2", "P3"}:
                assert exact_raw_reversible(topic, state)
        assert canonical_json(topic) == before

    assert global_family == Counter({name: 48 for name in FAMILIES})
    assert global_risk == Counter({"high": 144, "low": 144})
    assert global_cross == Counter({(name, level): 24 for name in FAMILIES for level in ("high", "low")})
    return actual_sha


def _manual_fixture() -> dict:
    sentence_a = "Record alpha quota 10."
    sentence_b = "Record alpha quota 20."
    prefix = "# Fixture\n\n## Evidence\nContext material.\n"
    text = prefix + sentence_a + "\n" + sentence_b + "\n"
    a_start = len(prefix)
    b_start = a_start + len(sentence_a) + 1
    unit = {"unit_id": "u-evidence", "start": len("# Fixture\n\n"), "end": len(text), "fact_keys": ["a", "b"]}
    source = {
        "source_id": "src-fixture-r0", "kind": "raw", "revision": 0,
        "sha256": _sha(text), "text": text, "units": [unit],
        "fact_refs": {
            "a": {"kind": "raw", "source_id": "src-fixture-r0", "unit_id": "u-evidence", "start": a_start, "end": a_start + len(sentence_a), "fact_key": "a"},
            "b": {"kind": "raw", "source_id": "src-fixture-r0", "unit_id": "u-evidence", "start": b_start, "end": b_start + len(sentence_b), "fact_key": "b"},
        },
    }
    derived_text = "# Digest\n\n## Summary\nalpha quota is 10.\n"
    claim_start = derived_text.index("alpha")
    claim_end = claim_start + len("alpha quota is 10.")
    claim = {
        "claim_id": "fixture-claim", "section_id": "fixture-section", "risk": "high",
        "fault_family": "within_source_conflict", "gold_outcome": "contested",
        "text": "alpha quota is 10.",
        "atoms": [{"subject": "alpha", "predicate": "quota", "value": "10"}],
        "derived_start": claim_start, "derived_end": claim_end,
        "cited_exact_refs": [dict(source["fact_refs"]["a"])],
        "intended_exact_refs": [dict(source["fact_refs"]["a"])],
        "intended_fact_keys": ["a"],
    }
    return {
        "topic_id": "fixture-topic",
        "w0_sources": [source], "w1_sources": [source],
        "w1_source_map": {source["source_id"]: source["source_id"]},
        "w1_fact_refs": dict(source["fact_refs"]),
        "derived": {
            "source_id": "derived-fixture", "kind": "derived", "text": derived_text,
            "sha256": _sha(derived_text),
            "sections": [{"section_id": "fixture-section", "start": derived_text.index("## Summary"), "end": len(derived_text)}],
            "d1_claim_order": ["fixture-claim"],
        },
        "claims": [claim],
    }


def validate_nonheldout_audit_contract() -> None:
    topic = _manual_fixture()
    claim = topic["claims"][0]
    outcomes = {}
    for condition in CONDITIONS:
        state = build_condition(topic, condition, "W0")
        row = audit_claim(topic, claim, state, budget=1200)
        outcomes[condition] = row["outcome"]
    # All four representations have enough fixture evidence to see both
    # passages. This checks conflict-preserving precision without revealing any
    # held-out result.
    assert outcomes == {condition: "contested" for condition in CONDITIONS}
    p2 = build_condition(topic, "P2", "W0")
    assert exact_raw_reversible(topic, p2)


def main() -> int:
    heldout_sha = validate_heldout_structure_only()
    validate_nonheldout_audit_contract()
    print(
        "E004-PRESCORE-VALIDATION PASS "
        f"topics={TOPIC_COUNT} claims={TOPIC_COUNT * CLAIMS_PER_TOPIC} families=6 risk=144+144 "
        f"heldoutSha={heldout_sha} expectedSha={EXPECTED_CORPUS_SHA256} "
        "spanReversibility=verified p3RiskOnly=verified nonheldoutAudit=verified "
        "heldoutScoring=no modelCalls=0 aiCredits=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
