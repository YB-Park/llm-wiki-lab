from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTION = "E014-R1 passed. Why is structural_expand_v1 still not the default, and what can E015 actually tell us?"
LITERAL = "E015 is not a quality proof"
EXCLUDE = {
    "remote-lab/e016_context_diagnostic.py",
    ".github/workflows/e016-context-diagnostic.yml",
}


def load_e010_module():
    path = ROOT / "experiments/E010-vscode-dogfood/real_user_dogfood.py"
    spec = importlib.util.spec_from_file_location("e010_real_user", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("e010_module_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    e010 = load_e010_module()
    out_dir = ROOT / "remote-lab/out/e016-context-diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("*"):
        if p.is_file():
            p.unlink()

    with tempfile.TemporaryDirectory(prefix="e016-context-diag-") as td:
        wiki = Path(td) / "wiki"
        e010.run_cli(wiki, ["init"])

        files = [p for p in e010.tracked_utf8_files() if p.relative_to(ROOT).as_posix() not in EXCLUDE]
        topic_files = {
            "project direction and decisions": [],
            "experiments and evidence": [],
            "product implementation": [],
        }
        for path in files:
            topic_files[e010.topic_for(path)].append(path)
        for topic, rows in topic_files.items():
            e010.run_cli(wiki, ["topic", "add", topic])
            for chunk in e010.batched(rows):
                e010.run_cli(wiki, ["ingest", *[str(path) for path in chunk], "--topic", topic], timeout=900)

        discovered = e010.parse_json_lines(
            e010.run_cli(wiki, ["discover", QUESTION, "--json", "--top-k-per-topic", "20"]).stdout
        )
        discovered.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)

        enriched = []
        literal_hits = []
        for rank, row in enumerate(discovered, start=1):
            shown = e010.run_cli(wiki, ["source", "show", row["source_id"], "--topic", row["topic_label"]]).stdout
            entry = {
                "global_rank": rank,
                "topic_label": row["topic_label"],
                "source_id": row["source_id"],
                "name": row["name"],
                "score": row["score"],
                "snippet": row["snippet"],
                "contains_e015_quality_literal": LITERAL in shown,
                "contains_e016": "E016" in shown,
                "contains_results_s1": "structured semantic constraint gate" in shown or "S1 result" in shown,
                "preview": shown[:2400],
            }
            enriched.append(entry)
            if entry["contains_e015_quality_literal"]:
                literal_hits.append(entry)

        selected_topic = discovered[0]["topic_label"] if discovered else None
        default_context = ""
        default_topic_search = []
        expanded_context = ""
        if selected_topic:
            default_topic_search = e010.parse_json_lines(
                e010.run_cli(
                    wiki,
                    ["search", QUESTION, "--topic", selected_topic, "--json", "--top-k", "20"],
                ).stdout
            )
            default_context = e010.run_cli(
                wiki,
                ["context", QUESTION, "--topic", selected_topic, "--class", "decision_history"],
            ).stdout
            expanded_context = e010.run_cli(
                wiki,
                ["context", QUESTION, "--topic", selected_topic, "--class", "decision_history", "--top-k", "12"],
            ).stdout

        result = {
            "format": "E016-CONTEXT-DIAGNOSTIC-v0",
            "model_calls": 0,
            "question": QUESTION,
            "corpus_utf8_files": len(files),
            "topic_counts": {k: len(v) for k, v in topic_files.items()},
            "selected_topic": selected_topic,
            "default_context_contains_literal": LITERAL in default_context,
            "expanded_top12_context_contains_literal": LITERAL in expanded_context,
            "literal_hit_count_in_discovery_top20_per_topic": len(literal_hits),
            "literal_hits": literal_hits,
            "discovery_top20_global": enriched[:20],
            "selected_topic_search_top20": default_topic_search,
            "default_context": default_context,
            "expanded_context_top12": expanded_context,
        }
        (out_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "format": result["format"],
            "model_calls": 0,
            "corpus_utf8_files": result["corpus_utf8_files"],
            "selected_topic": selected_topic,
            "default_context_contains_literal": result["default_context_contains_literal"],
            "expanded_top12_context_contains_literal": result["expanded_top12_context_contains_literal"],
            "literal_hit_count": result["literal_hit_count_in_discovery_top20_per_topic"],
            "literal_hit_ranks": [
                {"rank": x["global_rank"], "topic": x["topic_label"], "name": x["name"], "score": x["score"]}
                for x in literal_hits
            ],
            "top10": [
                {"rank": x["global_rank"], "topic": x["topic_label"], "name": x["name"], "score": x["score"], "e016": x["contains_e016"]}
                for x in enriched[:10]
            ],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
