from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import time
from pathlib import Path

from dogfood.llm_wiki.adapters import answer_prompt, ask_copilot

ROOT = Path(__file__).resolve().parents[2]
MODEL = "gpt-5.6-luna"
QUESTION = "E014-R1 passed. Why is structural_expand_v1 still not the default, and what can E015 actually tell us?"
SRC_RE = re.compile(r"\bsrc-[0-9A-Za-z-]+\b")


def load_e010_module():
    path = ROOT / "experiments/E010-vscode-dogfood/real_user_dogfood.py"
    spec = importlib.util.spec_from_file_location("e010_real_user", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("e010_module_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def structured_prompt(question: str, context: str) -> str:
    contract = (
        "STRUCTURED OUTPUT CONTRACT. Return exactly one valid JSON object and no Markdown or surrounding text. "
        "Use exactly this top-level shape: "
        '{"constraint_check":{"supported":[],"forbidden":[],"insufficient_or_conflicted":[]},"answer":""}. '
        "Populate constraint_check BEFORE forming the answer. "
        "In `supported`, state only conclusions the evidence positively supports. "
        "In `forbidden`, explicitly restate every conclusion the evidence says it cannot establish, is not a proof of, "
        "or may not be used to decide. Do not omit a negative limitation because a positive inference sounds plausible. "
        "In `insufficient_or_conflicted`, record relevant missing or unresolved information. "
        "Then write `answer` so it obeys those extracted constraints. "
        "The `answer` string must include the required Wiki citation handles inline for factual claims. "
        "Do not put unescaped newlines outside JSON strings."
    )
    return contract + "\n\n" + answer_prompt(question, context)


def has_negation(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in ["cannot", "can't", "does not", "doesn't", "not ", "insufficient", "forbidden"])


def main() -> int:
    request_path = ROOT / "remote-lab/e016-request.json"
    req = json.loads(request_path.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e016-s1-e015-20260815-1",
        "stage": "s1_e015",
        "model": MODEL,
        "max_model_calls": 1,
        "max_ai_credits": 30,
    }
    if req != expected:
        raise SystemExit("E016-STOP request_mismatch")

    e010 = load_e010_module()
    out = ROOT / "remote-lab/out/e016-s1"
    out.mkdir(parents=True, exist_ok=True)
    for path in out.glob("*"):
        if path.is_file():
            path.unlink()

    result = {
        "format": "E016-STRUCTURED-CONSTRAINT-S1-v0",
        "request_id": req["request_id"],
        "stage": req["stage"],
        "model": MODEL,
        "question": QUESTION,
    }

    try:
        with tempfile.TemporaryDirectory(prefix="e016-s1-") as td:
            wiki = Path(td) / "wiki"
            e010.run_cli(wiki, ["init"])
            topic_files = {
                "project direction and decisions": [],
                "experiments and evidence": [],
                "product implementation": [],
            }
            files = e010.tracked_utf8_files()
            for path in files:
                topic_files[e010.topic_for(path)].append(path)
            for topic, rows in topic_files.items():
                e010.run_cli(wiki, ["topic", "add", topic])
                for chunk in e010.batched(rows):
                    e010.run_cli(wiki, ["ingest", *[str(path) for path in chunk], "--topic", topic], timeout=900)

            discovered = e010.parse_json_lines(e010.run_cli(wiki, ["discover", QUESTION, "--json"]).stdout)
            discovered.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)
            if not discovered:
                raise RuntimeError("discover_no_hits")
            chosen = discovered[0]
            context = e010.run_cli(
                wiki,
                ["context", QUESTION, "--topic", chosen["topic_label"], "--class", "decision_history"],
            ).stdout.strip()
            if not context:
                raise RuntimeError("empty_context")

            otel = out / "otel.jsonl"
            started = time.monotonic()
            answer = ask_copilot(structured_prompt(QUESTION, context), model=MODEL, max_ai_credits=30)
            elapsed = round(time.monotonic() - started, 3)
            payload = json.loads(answer.text)
            if set(payload) != {"constraint_check", "answer"}:
                raise RuntimeError("structured_top_level_schema")
            check = payload["constraint_check"]
            if not isinstance(check, dict) or set(check) != {"supported", "forbidden", "insufficient_or_conflicted"}:
                raise RuntimeError("structured_constraint_schema")
            for key in ["supported", "forbidden", "insufficient_or_conflicted"]:
                if not isinstance(check[key], list) or not all(isinstance(item, str) for item in check[key]):
                    raise RuntimeError(f"structured_constraint_type:{key}")
            if not isinstance(payload["answer"], str) or not payload["answer"].strip():
                raise RuntimeError("structured_answer_type")

            forbidden = " ".join(check["forbidden"]).lower()
            final = payload["answer"].lower()
            forbidden_quality = "quality" in forbidden and has_negation(forbidden)
            forbidden_default = ("default" in forbidden or "promot" in forbidden) and has_negation(forbidden)
            answer_divergence = any(term in final for term in ["diverg", "disagreement", "differ"])
            answer_quality_limit = "quality" in final and has_negation(final)
            answer_default_limit = ("default" in final or "promot" in final) and has_negation(final)

            cited = list(dict.fromkeys(SRC_RE.findall(payload["answer"])))
            source_checks = []
            for sid in cited:
                shown = e010.run_cli(wiki, ["source", "show", sid, "--topic", chosen["topic_label"]]).stdout
                source_checks.append({"source_id": sid, "resolved": shown.startswith("SOURCE "), "preview": shown[:1400]})

            semantic_checks = {
                "forbidden_quality_captured": forbidden_quality,
                "forbidden_default_promotion_captured": forbidden_default,
                "answer_says_divergence": answer_divergence,
                "answer_limits_quality_claim": answer_quality_limit,
                "answer_limits_default_promotion": answer_default_limit,
                "answer_has_resolvable_citation": bool(cited) and all(row["resolved"] for row in source_checks),
                "exact_model": (answer.model or MODEL) == MODEL,
            }
            status = "PASS" if all(semantic_checks.values()) else "FAIL"
            result.update({
                "status": status,
                "ingested_utf8_files": len(files),
                "chosen_topic": chosen["topic_label"],
                "discovery_top": discovered[:6],
                "elapsed_seconds": elapsed,
                "structured": payload,
                "cited_source_ids": cited,
                "source_checks": source_checks,
                "semantic_checks": semantic_checks,
            })
    except Exception as exc:
        result.update({"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"})

    (out / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "format": result.get("format"),
        "request_id": result.get("request_id"),
        "stage": result.get("stage"),
        "model": result.get("model"),
        "status": result.get("status"),
        "chosen_topic": result.get("chosen_topic"),
        "semantic_checks": result.get("semantic_checks"),
        "error": result.get("error"),
    }, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
