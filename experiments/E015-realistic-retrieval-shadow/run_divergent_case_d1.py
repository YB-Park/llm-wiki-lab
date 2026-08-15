from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
import time
from pathlib import Path

from dogfood.llm_wiki.adapters import answer_prompt, ask_copilot
from dogfood.llm_wiki.calibration import resolve_topic
from dogfood.llm_wiki.retrieval import RETRIEVAL_STRUCTURAL_EXPAND_V1, render_context

ROOT = Path(__file__).resolve().parents[2]
MODEL = "gpt-5.6-luna"
QUESTION = "E014-R1 passed. Why is structural_expand_v1 still not the default, and what can E015 actually tell us?"
QUALITY_LITERAL = "E015 is not a quality proof"
DIVERGENCE_LITERAL = "E015 measures **how often the existing default W0 and candidate X1 actually diverge"
SRC_RE = re.compile(r"\bsrc-[0-9A-Za-z-]+\b")
EXCLUDE = {
    "experiments/E015-realistic-retrieval-shadow/divergent-case-d1-preregistration-v0.md",
    "experiments/E015-realistic-retrieval-shadow/run_divergent_case_d1.py",
    "remote-lab/e015-d1-request.json",
    ".github/workflows/e015-d1-real-user-x1.yml",
}


def load_e010_module():
    path = ROOT / "experiments/E010-vscode-dogfood/real_user_dogfood.py"
    spec = importlib.util.spec_from_file_location("e010_real_user", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("e010_module_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def negates_default(text: str) -> bool:
    low = text.lower()
    return "default" in low and any(term in low for term in ["not", "cannot", "can't", "does not", "doesn't", "insufficient", "should not"])


def limits_quality(text: str) -> bool:
    low = text.lower()
    quality_term = any(term in low for term in ["quality", "better", "correct", "more accurate", "superior"])
    limit_term = any(term in low for term in ["cannot", "can't", "does not", "doesn't", "not enough", "not a quality proof", "cannot tell", "cannot determine"])
    return quality_term and limit_term


def says_divergence(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in ["diverg", "disagreement", "differ", "how often"])


def main() -> int:
    req = json.loads((ROOT / "remote-lab/e015-d1-request.json").read_text(encoding="utf-8"))
    expected = {
        "request_id": "e015-d1-real-user-x1-20260815-1",
        "model": MODEL,
        "max_model_calls": 1,
        "max_ai_credits": 30,
    }
    if req != expected:
        raise SystemExit("E015-D1-STOP request_mismatch")

    e010 = load_e010_module()
    out = ROOT / "remote-lab/out/e015-d1"
    out.mkdir(parents=True, exist_ok=True)
    for path in out.glob("*"):
        if path.is_file():
            path.unlink()

    result = {
        "format": "E015-D1-REAL-USER-X1-v0",
        "request_id": req["request_id"],
        "model": MODEL,
        "question": QUESTION,
    }

    try:
        with tempfile.TemporaryDirectory(prefix="e015-d1-") as td:
            wiki = Path(td) / "wiki"
            e010.run_cli(wiki, ["init"])
            files = [
                p for p in e010.tracked_utf8_files()
                if p.relative_to(ROOT).as_posix() not in EXCLUDE
            ]
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
                e010.run_cli(wiki, ["discover", QUESTION, "--json", "--top-k-per-topic", "8"]).stdout
            )
            discovered.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)
            if not discovered:
                raise RuntimeError("discover_no_hits")
            chosen = discovered[0]
            topic_id = resolve_topic(wiki, chosen["topic_label"])["topic_id"]

            x1_context = render_context(
                wiki,
                QUESTION,
                top_k=8,
                max_chars_per_source=1200,
                topic_id=topic_id,
                mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
            )
            if QUALITY_LITERAL not in x1_context:
                raise RuntimeError("x1_context_missing_quality_limit")
            if DIVERGENCE_LITERAL not in x1_context:
                raise RuntimeError("x1_context_missing_divergence_statement")

            os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
            os.environ["OTEL_SERVICE_NAME"] = "llm-wiki-e015-d1"
            os.environ["COPILOT_MCP_TOOL_CACHE"] = "false"
            os.environ["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(out / "otel.jsonl")

            started = time.monotonic()
            answer = ask_copilot(answer_prompt(QUESTION, x1_context), model=MODEL, max_ai_credits=30)
            elapsed = round(time.monotonic() - started, 3)

            cited = list(dict.fromkeys(SRC_RE.findall(answer.text)))
            source_checks = []
            for source_id in cited:
                shown = e010.run_cli(wiki, ["source", "show", source_id, "--topic", chosen["topic_label"]]).stdout
                source_checks.append({
                    "source_id": source_id,
                    "resolved": shown.startswith("SOURCE "),
                    "preview": shown[:1600],
                })

            checks = {
                "x1_context_has_quality_limit": QUALITY_LITERAL in x1_context,
                "x1_context_has_divergence_statement": DIVERGENCE_LITERAL in x1_context,
                "answer_rejects_default_promotion": negates_default(answer.text),
                "answer_describes_divergence": says_divergence(answer.text),
                "answer_limits_quality_inference": limits_quality(answer.text),
                "citations_resolve": bool(cited) and all(row["resolved"] for row in source_checks),
                "exact_model": (answer.model or MODEL) == MODEL,
            }
            integrity = json.loads(e010.run_cli(wiki, ["integrity"]).stdout)
            integrity_ok = integrity.get("overall_status") == "ok" or integrity.get("ok") is True
            checks["integrity_clean"] = integrity_ok

            result.update({
                "status": "PASS" if all(checks.values()) else "FAIL",
                "corpus_utf8_files": len(files),
                "topic_counts": {key: len(value) for key, value in topic_files.items()},
                "chosen_topic": chosen["topic_label"],
                "discovery_top": discovered[:8],
                "elapsed_seconds": elapsed,
                "x1_context": x1_context,
                "answer": answer.text,
                "answer_model": answer.model,
                "cited_source_ids": cited,
                "source_checks": source_checks,
                "checks": checks,
                "integrity": integrity,
            })
    except Exception as exc:
        result.update({"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"})

    (out / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "format": result.get("format"),
        "request_id": result.get("request_id"),
        "model": result.get("model"),
        "status": result.get("status"),
        "corpus_utf8_files": result.get("corpus_utf8_files"),
        "chosen_topic": result.get("chosen_topic"),
        "checks": result.get("checks"),
        "error": result.get("error"),
    }, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
