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
CPYTHON_SHA = "07624ef11b924b39da97e978536f34f740e39575"
TOPIC = "cpython documentation"
QUESTION = (
    "In the current CPython documentation, what is the default multiprocessing start method on POSIX, why "
    "was the default changed away from fork, and what warning or caveat applies if I explicitly use fork from "
    "a multithreaded process?"
)
SRC_RE = re.compile(r"\bsrc-[0-9a-f-]+\b")


def load_e017_module():
    path = ROOT / "experiments/E017-external-real-user-corpora/run_external_corpora.py"
    spec = importlib.util.spec_from_file_location("e017_external", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("e017_module_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_request() -> dict:
    row = json.loads((ROOT / "remote-lab/e017-cpython-d2-request.json").read_text(encoding="utf-8"))
    expected = {
        "request_id": "e017-d2-cpython-x1-20260815-1",
        "model": MODEL,
        "max_model_calls": 1,
        "max_ai_credits": 30,
    }
    if row != expected:
        raise SystemExit(f"E017-D2-STOP request_mismatch actual={row}")
    return row


def text_checks(answer: str) -> dict[str, bool]:
    low = answer.lower()
    return {
        "answer_says_forkserver_default": "forkserver" in low and "default" in low,
        "answer_says_314_change": "3.14" in low,
        "answer_explains_multithread_rationale": "thread" in low and any(
            word in low for word in ["incompatib", "safer", "safe", "avoid", "problematic"]
        ),
        "answer_gives_supported_fork_caveat": "fork" in low and "thread" in low and any(
            word in low for word in ["problem", "unsafe", "deadlock", "incompatib", "avoid", "caution", "warning"]
        ),
        # D2 context intentionally lacks the exact 3.12 DeprecationWarning paragraph.
        # Mentioning that exact runtime class would therefore be unsupported by the supplied context.
        "answer_does_not_invent_deprecationwarning": "deprecationwarning" not in low and "deprecation warning" not in low,
    }


def build_wiki(e017, temp: Path):
    corpus = e017.prepare_git_corpus(
        temp,
        corpus_id="cpython-d2",
        repo_url="https://github.com/python/cpython.git",
        sha=CPYTHON_SHA,
        sparse_path="Doc",
        suffix=".rst",
    )
    wiki = temp / "wiki"
    e017.run_cli(wiki, ["init"])
    e017.run_cli(wiki, ["topic", "add", TOPIC])
    for chunk in e017.batched(corpus["files"]):
        e017.run_cli(wiki, ["ingest", *[str(path) for path in chunk], "--topic", TOPIC], timeout=1200)
    return wiki, corpus


def make_context(wiki: Path) -> str:
    topic_id = resolve_topic(wiki, TOPIC)["topic_id"]
    return render_context(
        wiki,
        QUESTION,
        top_k=8,
        max_chars_per_source=1200,
        topic_id=topic_id,
        mode=RETRIEVAL_STRUCTURAL_EXPAND_V1,
    )


def precondition_checks(context: str) -> dict[str, bool]:
    low = context.lower()
    return {
        "x1_has_forkserver": "forkserver" in low,
        "x1_has_posix_default_change": "on posix platforms the default start method was changed from" in low,
        "x1_has_multithread_rationale": "multithreaded" in low and "incompatibilities" in low,
        "x1_lacks_exact_deprecationwarning": "deprecationwarning" not in low and "deprecation warning" not in low,
    }


def main() -> int:
    request = load_request()
    e017 = load_e017_module()
    out = ROOT / "remote-lab/out/e017-cpython-d2"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*"):
        if old.is_file():
            old.unlink()

    result = {
        "format": "E017-D2-CPYTHON-X1-v0",
        "request": request,
        "question": QUESTION,
        "revision": CPYTHON_SHA,
        "model_calls": 0,
    }

    execute_model = os.environ.get("E017_D2_EXECUTE_MODEL") == "1"
    try:
        with tempfile.TemporaryDirectory(prefix="e017-cpython-d2-") as td:
            wiki, corpus = build_wiki(e017, Path(td))
            context = make_context(wiki)
            pre = precondition_checks(context)
            if not all(pre.values()):
                raise RuntimeError(f"x1_precondition_failed:{pre}")

            result.update({
                "corpus_files": corpus["file_count"],
                "corpus_bytes": corpus["bytes"],
                "x1_context": context,
                "preconditions": pre,
            })

            if execute_model:
                result["model_calls"] = 1
                os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
                os.environ["OTEL_SERVICE_NAME"] = "llm-wiki-e017-d2"
                os.environ["COPILOT_MCP_TOOL_CACHE"] = "false"
                os.environ["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(out / "otel.jsonl")

                started = time.monotonic()
                answer = ask_copilot(answer_prompt(QUESTION, context), model=MODEL, max_ai_credits=30)
                elapsed = round(time.monotonic() - started, 3)
                cited = list(dict.fromkeys(SRC_RE.findall(answer.text)))
                source_checks = []
                for source_id in cited:
                    shown = e017.run_cli(wiki, ["source", "show", source_id, "--topic", TOPIC], check=False)
                    source_checks.append({
                        "source_id": source_id,
                        "resolved": shown.returncode == 0 and shown.stdout.startswith("SOURCE "),
                        "preview": shown.stdout[:2400],
                    })
                checks = text_checks(answer.text)
                checks["citations_resolve"] = bool(cited) and all(row["resolved"] for row in source_checks)
                checks["exact_model"] = (answer.model or MODEL) == MODEL
                integrity = json.loads(e017.run_cli(wiki, ["integrity"]).stdout)
                checks["integrity_clean"] = integrity.get("overall_status") == "ok" or integrity.get("ok") is True
                result.update({
                    "status": "PASS" if all(checks.values()) else "FAIL",
                    "elapsed_seconds": elapsed,
                    "answer": answer.text,
                    "answer_model": answer.model,
                    "cited_source_ids": cited,
                    "source_checks": source_checks,
                    "checks": checks,
                    "integrity": integrity,
                })
            else:
                result["status"] = "PREFLIGHT_PASS"
    except Exception as exc:
        result.update({"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"})

    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "format": result["format"],
        "status": result["status"],
        "model_calls": result["model_calls"],
        "corpus_files": result.get("corpus_files"),
        "preconditions": result.get("preconditions"),
        "checks": result.get("checks"),
        "error": result.get("error"),
    }, ensure_ascii=False, indent=2))

    if execute_model:
        return 0 if result.get("status") == "PASS" else 2
    return 0 if result.get("status") == "PREFLIGHT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
