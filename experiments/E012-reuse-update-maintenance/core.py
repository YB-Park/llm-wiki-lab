#!/usr/bin/env python3
"""Pure context/scoring helpers for E012."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E011 = ROOT.parent / "E011-persistent-compilation-value-gate"

spec = importlib.util.spec_from_file_location("e012_e011_stage1a_core", E011 / "stage1a_core.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load E011 stage1a core")
e011_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e011_core)


def raw_context(docs: list[dict]) -> str:
    return e011_core.raw_context(docs)


def compiler_prompt(docs: list[dict]) -> str:
    return e011_core.compiler_prompt(docs)


def answer_prompt(question: str, context: str) -> str:
    return e011_core.answer_prompt(question, context)


def context_for(condition: str, docs: list[dict], summary: str) -> tuple[str, int]:
    if condition == "R1":
        return raw_context(docs), len(docs)
    if condition == "C0":
        return "### COMPILED TOPIC NOTE\n" + summary, 0
    raise ValueError(condition)


def parse_answer(text: str, context: str, allowed_source_ids=None) -> dict:
    return e011_core.parse_answer(text, context, allowed_source_ids)


def score(query: dict, parsed: dict) -> dict:
    answer = parsed["answer"].lower() if parsed["valid"] else ""
    hits = sum(signal.lower() in answer for signal in query["required_signals"])
    required_sources = set(query["required_source_ids"])
    got_sources = set(parsed["source_ids"])
    source_hits = len(required_sources & got_sources)
    stale_substitution = bool(
        parsed["valid"]
        and any(signal.lower() in answer for signal in query.get("forbidden_current_signals", []))
        and hits < len(query["required_signals"])
    )
    strict = bool(
        parsed["valid"]
        and hits == len(query["required_signals"])
        and required_sources <= got_sources
        and not stale_substitution
    )
    return {
        "valid": bool(parsed["valid"]),
        "signal_hits": hits,
        "signal_total": len(query["required_signals"]),
        "source_hits": source_hits,
        "source_total": len(required_sources),
        "strict_pass": strict,
        "stale_substitution": stale_substitution,
        "uncertainty": parsed.get("uncertainty"),
        "violation": parsed.get("violation"),
    }
