#!/usr/bin/env python3
"""Non-scored end-to-end rehearsal for the E007 harness.

This script deliberately does NOT use Corpus C. It exercises the real frozen prompt
shapes and Copilot adapter against a tiny unrelated fictional micro-world so parsing,
verifier, repair, regression-repair, answer JSON, and OTel paths are checked before
the first scored Family N block.

Nothing produced here is a quality result. The rehearsal must not be used to tune
E007 prompts, repetition count, or condition design.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from copilot_cli import cli_version, run_prompt
from run_e007 import normalize_markdown_response, parse_verification, render_sources, render_template
from score_deterministic import parse_answer_batch

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = ROOT / ".local"


SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "RZ001",
        "wave": 0,
        "title": "Zephyr deployment note",
        "date": "2026-07-01",
        "publisher": "Cedar Labs",
        "text": (
            "Project Zephyr is owned by Cedar Labs. Production does not use Redis. "
            "The default document window is 512 tokens. The optional feature flag is "
            "delta_prefetch. Before July 10 the cache TTL is 20 minutes."
        ),
    },
    {
        "source_id": "RZ002",
        "wave": 1,
        "title": "Zephyr cache change",
        "date": "2026-07-10",
        "publisher": "Cedar Labs",
        "text": (
            "Effective 2026-07-10, Zephyr changes its cache TTL from 20 minutes to "
            "8 minutes. The earlier 20-minute value remains historically correct before "
            "the effective date. Ownership and the 512-token default are unchanged."
        ),
    },
]


def call(*, root: Path, name: str, prompt: str, model: str) -> tuple[str, dict[str, Any]]:
    result = run_prompt(prompt=prompt, model=model, run_dir=root / "calls" / name)
    return str(result["response"]), result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run non-scored full E007 harness rehearsal")
    parser.add_argument("--model", default="gpt-5.6-luna")
    args = parser.parse_args()

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = LOCAL_ROOT / f"full-harness-preflight-{stamp}"
    root.mkdir(parents=True, exist_ok=False)

    calls = 0
    otel_files = 0

    def tracked(name: str, prompt: str) -> str:
        nonlocal calls, otel_files
        text, _meta = call(root=root, name=name, prompt=prompt, model=args.model)
        calls += 1
        if (root / "calls" / name / "otel.jsonl").exists():
            otel_files += 1
        return text

    # 1) Naive update path.
    c1_prompt = render_template(
        "C1-update.md",
        CURRENT_WIKI="(empty — rehearsal)",
        NEW_SOURCES=render_sources([SOURCES[0]]),
    )
    wiki1 = normalize_markdown_response(tracked("01-c1-update", c1_prompt))
    if not wiki1.strip():
        raise RuntimeError("C1 rehearsal returned empty Markdown")

    # 2) Source-grounded update path.
    c2_prompt = render_template(
        "C2-update.md",
        CURRENT_WIKI=wiki1,
        NEW_SOURCES=render_sources([SOURCES[1]]),
        ALL_SOURCES=render_sources(SOURCES),
    )
    wiki2 = normalize_markdown_response(tracked("02-c2-update", c2_prompt))
    if not wiki2.strip():
        raise RuntimeError("C2 rehearsal returned empty Markdown")

    # 3) Verifier JSON path. The candidate contains a deliberate unrelated false claim
    # so the prompt sees a realistic integrity problem, but we only require valid JSON.
    flawed_candidate = wiki2.rstrip() + "\n\n- Zephyr uses Redis in production. [RZ001]\n"
    verify_prompt = render_template(
        "C3-verify.md",
        CURRENT_WIKI=wiki1,
        NEW_SOURCES=render_sources([SOURCES[1]]),
        CANDIDATE_WIKI=flawed_candidate,
        ALL_SOURCES=render_sources(SOURCES),
    )
    verifier_text = tracked("03-c3-verify", verify_prompt)
    _verifier_report = parse_verification(verifier_text)

    # 4) Repair path is exercised with a deterministic synthetic verifier report rather
    # than depending on whether the model happened to notice the seeded flaw above.
    forced_report = {
        "decision": "revise",
        "coverage_issues": [],
        "preservation_issues": [],
        "faithfulness_issues": [
            {
                "description": "Candidate says Zephyr uses Redis, but RZ001 says production does not use Redis.",
                "source_ids": ["RZ001"],
            }
        ],
    }
    repair_prompt = render_template(
        "C3-repair.md",
        CURRENT_WIKI=wiki1,
        CANDIDATE_WIKI=flawed_candidate,
        VERIFICATION_REPORT=json.dumps(forced_report, indent=2),
        ALL_SOURCES=render_sources(SOURCES),
    )
    repaired = normalize_markdown_response(tracked("04-c3-repair", repair_prompt))
    if not repaired.strip():
        raise RuntimeError("C3 repair rehearsal returned empty Markdown")

    # 5) Final verifier path after repair.
    reverify_prompt = render_template(
        "C3-verify.md",
        CURRENT_WIKI=wiki1,
        NEW_SOURCES=render_sources([SOURCES[1]]),
        CANDIDATE_WIKI=repaired,
        ALL_SOURCES=render_sources(SOURCES),
    )
    reverify_text = tracked("05-c3-reverify", reverify_prompt)
    _reverify_report = parse_verification(reverify_text)

    # 6) C4 regression-repair prompt path. The diagnostic is not evidence; the prompt
    # must re-derive the fact from raw sources. We only validate transport/contract here.
    regression_failures = [
        {
            "query_id": "RZQ1",
            "question": "What optional feature flag is documented for Zephyr?",
            "current_answer": "unknown",
            "current_source_ids": [],
            "note": "This rehearsal diagnostic says a previously answerable fact was missed; verify against raw evidence.",
        }
    ]
    regression_prompt = render_template(
        "C4-regression-repair.md",
        CANDIDATE_WIKI=repaired,
        REGRESSION_FAILURES=json.dumps(regression_failures, indent=2),
        ALL_SOURCES=render_sources(SOURCES),
    )
    final_wiki = normalize_markdown_response(tracked("06-c4-regression-repair", regression_prompt))
    if not final_wiki.strip():
        raise RuntimeError("C4 regression-repair rehearsal returned empty Markdown")

    # 7) Answer-batch JSON path.
    questions = [
        {"query_id": "RZQ1", "question": "Who owns Project Zephyr?"},
        {"query_id": "RZQ2", "question": "What cache TTL is effective after 2026-07-10?"},
    ]
    answer_prompt = render_template(
        "answer-batch.md",
        EVIDENCE=final_wiki,
        QUESTIONS=json.dumps(questions, indent=2),
    )
    answer_text = tracked("07-answer-batch", answer_prompt)
    parsed = parse_answer_batch(answer_text)
    if set(parsed) != {"RZQ1", "RZQ2"}:
        raise RuntimeError(f"answer-batch rehearsal IDs mismatch: {sorted(parsed)}")

    summary = {
        "format": "FULL-HARNESS-PREFLIGHT-v0",
        "status": "PASS",
        "model": args.model,
        "cli": cli_version(),
        "calls": calls,
        "otel_files": otel_files,
        "contracts": [
            "c1_update",
            "c2_update",
            "c3_verify",
            "c3_repair",
            "c3_reverify",
            "c4_regression_repair",
            "answer_batch_json",
        ],
        "uses_corpus_c": False,
    }
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    cli_line = summary["cli"].splitlines()[0] if summary["cli"] else "?"
    print("FULL-HARNESS-PREFLIGHT-v0")
    print(f"status=PASS model={args.model} cli={cli_line}")
    print(f"calls={calls} otel={otel_files}/{calls}")
    print("contracts=c1,c2,verify,repair,reverify,regression_repair,answer_json")
    print("corpus_c=NOT_USED quality_result=NONE")


if __name__ == "__main__":
    main()
