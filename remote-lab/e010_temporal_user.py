from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt-5.6-luna"
SRC_RE = re.compile(r"\bsrc-[0-9A-Za-z-]+\b")


def run_cli(wiki: Path, args: list[str], *, otel: Path | None = None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    if otel:
        env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel)
        env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
        env["OTEL_SERVICE_NAME"] = "llm-wiki-e010-temporal-user"
        env["COPILOT_MCP_TOOL_CACHE"] = "false"
    return subprocess.run(
        [sys.executable, "-m", "dogfood.llm_wiki.cli", "--root", str(wiki), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=900,
        check=False,
    )


def must(wiki: Path, args: list[str]) -> str:
    proc = run_cli(wiki, args)
    if proc.returncode:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc.stdout


def ingest_id(wiki: Path, path: Path, topic: str) -> str:
    text = must(wiki, ["ingest", str(path), "--topic", topic])
    match = re.search(r"INGEST source=(src-[0-9A-Za-z-]+)", text)
    if not match:
        raise RuntimeError("ingest_receipt_missing")
    return match.group(1)


def ask_task(wiki: Path, out: Path, task_id: str, topic: str, question: str, required: list[list[str]]):
    otel = out / f"otel-{task_id}.jsonl"
    start = time.monotonic()
    proc = run_cli(
        wiki,
        ["ask", question, "--topic", topic, "--class", "exact_provenance", "--allow-model-call", "--model", MODEL, "--max-ai-credits", "30"],
        otel=otel,
    )
    elapsed = round(time.monotonic() - start, 3)
    result = {"task_id": task_id, "question": question, "elapsed_seconds": elapsed, "return_code": proc.returncode}
    if proc.returncode:
        result.update({"automatic_pass": False, "error": (proc.stderr or proc.stdout)[-3000:]})
    else:
        lines = proc.stdout.splitlines()
        answer = "\n".join(lines[1:]).strip() if lines and lines[0].startswith("MODEL ") else proc.stdout.strip()
        cited = list(dict.fromkeys(SRC_RE.findall(answer)))
        checks = []
        for sid in cited:
            shown = run_cli(wiki, ["source", "show", sid, "--topic", topic])
            checks.append({"source_id": sid, "resolved": shown.returncode == 0, "preview": shown.stdout[:1000]})
        low = answer.lower()
        concepts = [any(term.lower() in low for term in group) for group in required]
        result.update({
            "answer": answer,
            "cited_source_ids": cited,
            "source_checks": checks,
            "concept_checks": concepts,
            "automatic_pass": bool(cited) and all(x["resolved"] for x in checks) and all(concepts),
        })
    (out / f"task-{task_id}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    req = json.loads((ROOT / "remote-lab/e010-temporal-request.json").read_text(encoding="utf-8"))
    if req != {"request_id": "assistant-user-eval-temporal-20260815-1", "model": MODEL, "max_model_calls": 2, "max_ai_credits": 30}:
        raise SystemExit("E010-TEMPORAL-STOP request_mismatch")
    out = ROOT / "remote-lab/out/e010-temporal-user"
    out.mkdir(parents=True, exist_ok=True)
    for path in out.glob("*"):
        if path.is_file(): path.unlink()

    with tempfile.TemporaryDirectory(prefix="e010-temporal-user-") as td:
        td = Path(td)
        wiki = td / "wiki"
        topic = "customer-like temporal knowledge"
        must(wiki, ["init"])
        must(wiki, ["topic", "add", topic])

        old = td / "cache-old.md"
        new = td / "cache-corrected.md"
        old.write_text("Approved cache limit: 100 requests per second.\n", encoding="utf-8")
        new.write_text("Correction: the earlier note had a transcription error. The actually approved cache limit is 120 requests per second.\n", encoding="utf-8")
        old_id = ingest_id(wiki, old, topic)
        new_id = ingest_id(wiki, new, topic)
        must(wiki, ["source", "correct", old_id, new_id, "--topic", topic])
        correction = ask_task(
            wiki, out, "correction", topic,
            "What is the approved cache limit now, and is this a correction of an earlier error or a later real-world change?",
            [["120"], ["correction", "corrected"], ["error", "transcription", "not a change", "not a later"]],
        )

        a = td / "launch-a.md"
        b = td / "launch-b.md"
        a.write_text("Release coordination note A: production launch is Monday.\n", encoding="utf-8")
        b.write_text("Release coordination note B: production launch is Tuesday.\n", encoding="utf-8")
        a_id = ingest_id(wiki, a, topic)
        b_id = ingest_id(wiki, b, topic)
        must(wiki, ["source", "dispute", a_id, b_id, "--topic", topic])
        dispute = ask_task(
            wiki, out, "dispute", topic,
            "When is the production launch? Give me the trustworthy answer from the Wiki.",
            [["monday"], ["tuesday"], ["unresolved", "dispute", "conflict", "cannot determine", "uncertain"]],
        )
        integrity = json.loads(must(wiki, ["integrity"]))

    result = {"format": "E010-TEMPORAL-USER-v1", "model": MODEL, "tasks": [correction, dispute], "integrity": integrity}
    result["automatic_pass_count"] = sum(int(x["automatic_pass"]) for x in result["tasks"])
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"model": MODEL, "automatic_pass_count": result["automatic_pass_count"], "tasks": [{"id": x["task_id"], "pass": x["automatic_pass"]} for x in result["tasks"]]}, indent=2))
    return 0 if result["automatic_pass_count"] == 2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
