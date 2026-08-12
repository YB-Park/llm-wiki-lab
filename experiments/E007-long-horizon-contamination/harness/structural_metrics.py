#!/usr/bin/env python3
"""Deterministic structural metrics for E007 derived Wiki states.

This is post-hoc measurement only. It never feeds back into maintenance decisions.
The goal is to distinguish genuine knowledge-maintenance gains from degenerate
strategies such as copying nearly the entire raw corpus into the derived artifact.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
SOURCE_ID_RE = re.compile(r"\[(S\d{3})\]")
STATE_RE = re.compile(r"W(\d{2})-wiki\.md$")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def render_sources(sources: list[dict[str, Any]]) -> str:
    """Match the experiment runner's raw-source rendering."""
    if not sources:
        return "(none)"
    blocks = []
    for source in sources:
        blocks.append(
            "\n".join(
                [
                    f"### {source['source_id']} — {source['title']}",
                    f"Date: {source['date']}",
                    f"Publisher: {source['publisher']}",
                    "",
                    source["text"],
                ]
            )
        )
    return "\n\n".join(blocks)


def text_shape(text: str) -> dict[str, int]:
    return {
        "utf8_bytes": len(text.encode("utf-8")),
        "chars": len(text),
        "lines": len(text.splitlines()),
        "nonempty_lines": sum(1 for line in text.splitlines() if line.strip()),
    }


def line_churn(previous: str, current: str) -> dict[str, float | int]:
    prev_lines = previous.splitlines()
    curr_lines = current.splitlines()
    added = 0
    deleted = 0

    matcher = difflib.SequenceMatcher(a=prev_lines, b=curr_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            added += j2 - j1
        elif tag == "delete":
            deleted += i2 - i1
        elif tag == "replace":
            deleted += i2 - i1
            added += j2 - j1

    changed = added + deleted
    return {
        "added_lines": added,
        "deleted_lines": deleted,
        "changed_lines": changed,
        "changed_lines_per_previous_line": round(changed / max(len(prev_lines), 1), 4),
    }


def analyze_run(run_dir: Path) -> dict[str, Any]:
    config_path = run_dir / "run-config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"missing run-config.json in {run_dir}")
    config = json.loads(config_path.read_text(encoding="utf-8"))

    sources = load_jsonl(CORPUS / "sources.jsonl")
    states_dir = run_dir / "states"
    state_paths = sorted(states_dir.glob("W*-wiki.md")) if states_dir.exists() else []

    waves: list[dict[str, Any]] = []
    previous_wiki = ""
    cumulative_changed_lines = 0

    for path in state_paths:
        match = STATE_RE.search(path.name)
        if not match:
            continue
        wave = int(match.group(1))
        available = sorted(
            [source for source in sources if int(source["wave"]) <= wave],
            key=lambda row: row["source_id"],
        )
        raw_text = render_sources(available)
        wiki_text = path.read_text(encoding="utf-8")

        raw_shape = text_shape(raw_text)
        wiki_shape = text_shape(wiki_text)
        churn = line_churn(previous_wiki, wiki_text)
        cumulative_changed_lines += int(churn["changed_lines"])

        cited_ids = sorted(set(SOURCE_ID_RE.findall(wiki_text)))
        available_ids = {str(source["source_id"]) for source in available}
        valid_cited_ids = sorted(set(cited_ids) & available_ids)
        unknown_cited_ids = sorted(set(cited_ids) - available_ids)

        raw_bytes = raw_shape["utf8_bytes"]
        wiki_bytes = wiki_shape["utf8_bytes"]
        waves.append(
            {
                "wave": wave,
                "available_source_count": len(available),
                "raw": raw_shape,
                "wiki": wiki_shape,
                "wiki_to_raw_byte_ratio": round(wiki_bytes / max(raw_bytes, 1), 4),
                "byte_savings_vs_raw": raw_bytes - wiki_bytes,
                "churn": churn,
                "cumulative_changed_lines": cumulative_changed_lines,
                "source_ids": {
                    "referenced_valid": valid_cited_ids,
                    "referenced_unknown": unknown_cited_ids,
                    "valid_reference_count": len(valid_cited_ids),
                    "available_source_count": len(available_ids),
                    "descriptive_source_id_coverage": round(
                        len(valid_cited_ids) / max(len(available_ids), 1), 4
                    ),
                },
            }
        )
        previous_wiki = wiki_text

    final = waves[-1] if waves else None
    max_churn = max((float(w["churn"]["changed_lines_per_previous_line"]) for w in waves), default=0.0)

    return {
        "experiment": config.get("experiment", "E007"),
        "run_id": run_dir.name,
        "condition": config.get("condition", "?"),
        "model": config.get("model", "?"),
        "measurement_role": "post-hoc descriptive; never feeds maintenance",
        "waves": waves,
        "aggregate": {
            "state_count": len(waves),
            "final_wiki_to_raw_byte_ratio": (
                final["wiki_to_raw_byte_ratio"] if final is not None else None
            ),
            "final_wiki_utf8_bytes": final["wiki"]["utf8_bytes"] if final is not None else None,
            "final_raw_utf8_bytes": final["raw"]["utf8_bytes"] if final is not None else None,
            "cumulative_changed_lines": cumulative_changed_lines,
            "max_changed_lines_per_previous_line": round(max_churn, 4),
        },
        "notes": [
            "A lower Wiki/raw ratio is not automatically better; excessive compression can cause omission.",
            "A higher source-ID coverage is not automatically better; this is descriptive, not a score.",
            "Line churn is a deterministic proxy for rewrite/review burden, not semantic edit distance.",
        ],
    }


def compact_text(result: dict[str, Any]) -> str:
    agg = result["aggregate"]
    if not agg["state_count"]:
        return (
            f"STRUCTURE run={result['run_id']} condition={result['condition']} "
            "states=0 ratio=n/a churn=n/a\n"
        )
    return (
        f"STRUCTURE run={result['run_id']} condition={result['condition']} "
        f"states={agg['state_count']} finalB={agg['final_wiki_utf8_bytes']} "
        f"rawB={agg['final_raw_utf8_bytes']} ratio={agg['final_wiki_to_raw_byte_ratio']} "
        f"changedLines={agg['cumulative_changed_lines']} "
        f"maxChurn={agg['max_changed_lines_per_previous_line']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute deterministic structural metrics for one E007 run")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    result = analyze_run(args.run_dir)
    output = args.output or (args.run_dir / "structural-metrics.json")
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.compact:
        print(compact_text(result), end="")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
