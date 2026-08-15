from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MODEL = "gpt-5.6-luna"
SRC_RE = re.compile(r"\bsrc-[0-9a-f-]+\b")

REPO_TASKS = [
    {
        "id": "customer-readiness",
        "query": "Are we actually ready to call this LLM Wiki customer-ready now? What still has to be proven in real use?",
        "query_class": "synthesis",
        "required_groups": [
            ["not ready", "not yet", "alpha", "dogfood"],
            ["luna", "vscode", "copilot"],
            ["multi-session", "multiple sessions", "repeated", "real use", "habitability"],
        ],
    },
    {
        "id": "compiled-wiki",
        "query": "Why is the persistent compiled Wiki still disabled even though E011 and E012 found a useful high-reuse region? What evidence would justify enabling it?",
        "query_class": "decision_history",
        "required_groups": [
            ["e013"],
            ["revisit", "reuse", "realistic workload", "real workload"],
            ["disabled", "raw", "default"],
        ],
    },
    {
        "id": "retrieval-x1",
        "query": "E014-R1 passed. Why is structural_expand_v1 still not the default, and what can E015 actually tell us?",
        "query_class": "decision_history",
        "required_groups": [
            ["e015"],
            ["shadow"],
            ["quality", "better", "promotion", "default"],
        ],
    },
    {
        "id": "manifest-loss",
        "query": "If the canonical manifest disappears while raw evidence or exact-provenance state survives, should the Wiki recreate an empty history or stop? Explain why.",
        "query_class": "exact_provenance",
        "required_groups": [
            ["fail closed", "fail-closed", "stop", "refuse"],
            ["raw", "provenance"],
            ["recreate", "empty history", "missing manifest", "state loss"],
        ],
    },
]


def load_request(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if set(data) != {"request_id", "model", "max_ai_credits", "max_model_calls"}:
        raise SystemExit("E010-USER-STOP request_schema")
    if data["model"] != MODEL:
        raise SystemExit("E010-USER-STOP model_not_luna")
    if data["max_ai_credits"] != 30:
        raise SystemExit("E010-USER-STOP credit_guard_must_equal_30")
    if data["max_model_calls"] != 6:
        raise SystemExit("E010-USER-STOP model_call_guard_must_equal_6")
    if not isinstance(data["request_id"], str) or not data["request_id"].strip():
        raise SystemExit("E010-USER-STOP request_id")
    return data


def run_cli(root: Path, args: list[str], *, otel: Path | None = None, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    if otel is not None:
        env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel)
        env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
        env["OTEL_SERVICE_NAME"] = "llm-wiki-e010-user-dogfood"
        env["COPILOT_MCP_TOOL_CACHE"] = "false"
    proc = subprocess.run(
        [sys.executable, "-m", "dogfood.llm_wiki.cli", "--root", str(root), *args],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"cli_failed rc={proc.returncode} args={args[:3]} stderr={proc.stderr.strip()} stdout={proc.stdout.strip()}"
        )
    return proc


def tracked_utf8_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=REPO)
    rows: list[Path] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        rel = item.decode("utf-8")
        path = REPO / rel
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        rows.append(path)
    return rows


def topic_for(path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    if rel.startswith("experiments/"):
        return "experiments and evidence"
    if rel.startswith("dogfood/") or rel.startswith("remote-lab/") or rel.startswith(".github/"):
        return "product implementation"
    return "project direction and decisions"


def batched(values: list[Path], size: int = 40):
    for i in range(0, len(values), size):
        yield values[i : i + size]


def parse_json_lines(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def parse_ingest_source(text: str) -> str:
    match = re.search(r"\bINGEST source=(src-[0-9a-f-]+)\b", text)
    if not match:
        raise RuntimeError(f"ingest_receipt_missing:{text[:400]}")
    return match.group(1)


def source_ids_from_answer(text: str) -> list[str]:
    return list(dict.fromkeys(SRC_RE.findall(text)))


def unwrap(value: Any) -> Any:
    if isinstance(value, dict):
        for key in ("stringValue", "intValue", "doubleValue", "boolValue", "value"):
            if key in value:
                return unwrap(value[key])
    return value


def walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def otel_summary(path: Path) -> dict[str, Any]:
    totals = {
        "gen_ai.usage.input_tokens": 0.0,
        "gen_ai.usage.output_tokens": 0.0,
        "gen_ai.usage.cache_read.input_tokens": 0.0,
        "github.copilot.cost": 0.0,
        "github.copilot.aiu": 0.0,
    }
    models: set[str] = set()
    if not path.exists():
        return {"present": False, "models": [], **totals}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        for row in walk_dicts(payload):
            key = row.get("key")
            if key == "gen_ai.response.model" and "value" in row:
                models.add(str(unwrap(row["value"])))
            if key in totals and "value" in row:
                try:
                    totals[key] += float(unwrap(row["value"]))
                except (TypeError, ValueError):
                    pass
    return {"present": True, "models": sorted(models), **totals}


def concept_groups_pass(answer: str, groups: list[list[str]]) -> tuple[bool, list[bool]]:
    lower = answer.lower()
    checks = [any(term.lower() in lower for term in group) for group in groups]
    return all(checks), checks


def run_ask(
    root: Path,
    output_dir: Path,
    *,
    task_id: str,
    query: str,
    topic: str,
    query_class: str,
    required_groups: list[list[str]],
) -> dict[str, Any]:
    otel = output_dir / f"otel-{task_id}.jsonl"
    started = time.monotonic()
    proc = run_cli(
        root,
        [
            "ask",
            query,
            "--topic",
            topic,
            "--class",
            query_class,
            "--allow-model-call",
            "--model",
            MODEL,
            "--max-ai-credits",
            "30",
        ],
        otel=otel,
    )
    elapsed = time.monotonic() - started
    lines = proc.stdout.splitlines()
    if not lines or lines[0].strip() != f"MODEL {MODEL}":
        raise RuntimeError(f"unexpected_model_receipt:{proc.stdout[:500]}")
    answer = "\n".join(lines[1:]).strip()
    cited = source_ids_from_answer(answer)
    source_checks = []
    for source_id in cited[:6]:
        shown = run_cli(root, ["source", "show", source_id, "--topic", topic]).stdout
        source_checks.append({"source_id": source_id, "resolved": shown.startswith("SOURCE "), "preview": shown[:1200]})
    concept_ok, concept_checks = concept_groups_pass(answer, required_groups)
    tele = otel_summary(otel)
    exact_model_observed = (not tele["models"]) or MODEL in tele["models"]
    result = {
        "task_id": task_id,
        "query": query,
        "topic": topic,
        "query_class": query_class,
        "model": MODEL,
        "elapsed_seconds": round(elapsed, 3),
        "answer": answer,
        "cited_source_ids": cited,
        "citation_count": len(cited),
        "citations_resolve": bool(cited) and all(row["resolved"] for row in source_checks),
        "source_checks": source_checks,
        "concept_groups": required_groups,
        "concept_group_checks": concept_checks,
        "concepts_pass": concept_ok,
        "otel": tele,
        "exact_model_observed": exact_model_observed,
        "automatic_pass": bool(answer) and bool(cited) and all(row["resolved"] for row in source_checks) and concept_ok and exact_model_observed,
    }
    (output_dir / f"task-{task_id}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def repo_task(root: Path, output_dir: Path, task: dict[str, Any]) -> dict[str, Any]:
    discovered = parse_json_lines(run_cli(root, ["discover", task["query"], "--json"]).stdout)
    discovered.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)
    if not discovered:
        raise RuntimeError(f"discover_no_hits:{task['id']}")
    chosen = discovered[0]
    answer = run_ask(
        root,
        output_dir,
        task_id=task["id"],
        query=task["query"],
        topic=chosen["topic_label"],
        query_class=task["query_class"],
        required_groups=task["required_groups"],
    )
    answer["discovery"] = {
        "chosen_topic": chosen["topic_label"],
        "chosen_source_id": chosen["source_id"],
        "chosen_name": chosen["name"],
        "chosen_score": chosen["score"],
        "top_rows": discovered[:6],
    }
    (output_dir / f"task-{task['id']}.json").write_text(
        json.dumps(answer, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return answer


def scenario_tasks(root: Path, output_dir: Path, scenario_dir: Path) -> list[dict[str, Any]]:
    topic = "real-user temporal scenario"
    run_cli(root, ["topic", "add", topic])

    old = scenario_dir / "cache-limit-old.md"
    corrected = scenario_dir / "cache-limit-corrected.md"
    old.write_text("Approved cache limit: 100 requests per second.\n", encoding="utf-8")
    corrected.write_text(
        "Correction: the earlier cache-limit note contained a transcription error. The actually approved cache limit is 120 requests per second.\n",
        encoding="utf-8",
    )
    old_id = parse_ingest_source(run_cli(root, ["ingest", str(old), "--topic", topic]).stdout)
    new_id = parse_ingest_source(run_cli(root, ["ingest", str(corrected), "--topic", topic]).stdout)
    run_cli(root, ["source", "correct", old_id, new_id, "--topic", topic])
    correction = run_ask(
        root,
        output_dir,
        task_id="correction-scenario",
        query="What is the approved cache limit now, and is this a correction of an earlier error or a later real-world change?",
        topic=topic,
        query_class="exact_provenance",
        required_groups=[["120"], ["correction", "corrected"], ["error", "transcription", "not a later", "not a change"]],
    )

    left = scenario_dir / "launch-monday.md"
    right = scenario_dir / "launch-tuesday.md"
    left.write_text("Release coordination note A: production launch is Monday.\n", encoding="utf-8")
    right.write_text("Release coordination note B: production launch is Tuesday.\n", encoding="utf-8")
    left_id = parse_ingest_source(run_cli(root, ["ingest", str(left), "--topic", topic]).stdout)
    right_id = parse_ingest_source(run_cli(root, ["ingest", str(right), "--topic", topic]).stdout)
    run_cli(root, ["source", "dispute", left_id, right_id, "--topic", topic])
    dispute = run_ask(
        root,
        output_dir,
        task_id="dispute-scenario",
        query="When is the production launch? Give me the trustworthy answer from the Wiki.",
        topic=topic,
        query_class="exact_provenance",
        required_groups=[["monday"], ["tuesday"], ["unresolved", "dispute", "conflict", "cannot determine", "uncertain"]],
    )
    return [correction, dispute]


def main() -> int:
    request_path = REPO / "remote-lab" / "e010-user-request.json"
    req = load_request(request_path)
    output_dir = REPO / "remote-lab" / "out" / "e010-user"
    output_dir.mkdir(parents=True, exist_ok=True)
    for old in output_dir.glob("*"):
        if old.is_file():
            old.unlink()

    with tempfile.TemporaryDirectory(prefix="llm-wiki-e010-user-") as td:
        temp = Path(td)
        root = temp / "wiki"
        scenario_dir = temp / "scenario"
        scenario_dir.mkdir()

        run_cli(root, ["init"])
        topic_files: dict[str, list[Path]] = {
            "project direction and decisions": [],
            "experiments and evidence": [],
            "product implementation": [],
        }
        files = tracked_utf8_files()
        for path in files:
            topic_files[topic_for(path)].append(path)
        for topic, rows in topic_files.items():
            run_cli(root, ["topic", "add", topic])
            for chunk in batched(rows):
                run_cli(root, ["ingest", *[str(path) for path in chunk], "--topic", topic], timeout=900)

        tasks = [repo_task(root, output_dir, task) for task in REPO_TASKS]
        tasks.extend(scenario_tasks(root, output_dir, scenario_dir))
        if len(tasks) != req["max_model_calls"]:
            raise RuntimeError(f"model_call_count_guard:{len(tasks)}")

        integrity = json.loads(run_cli(root, ["integrity"]).stdout)
        calibration = json.loads(run_cli(root, ["calibration", "export"]).stdout)

    total_input = sum(float(task["otel"].get("gen_ai.usage.input_tokens", 0.0)) for task in tasks)
    total_output = sum(float(task["otel"].get("gen_ai.usage.output_tokens", 0.0)) for task in tasks)
    total_cost = sum(float(task["otel"].get("github.copilot.cost", 0.0)) for task in tasks)
    total_aiu = sum(float(task["otel"].get("github.copilot.aiu", 0.0)) for task in tasks)
    all_auto = all(task["automatic_pass"] for task in tasks)
    result = {
        "format": "E010-REAL-USER-LUNA-DOGFOOD-v1",
        "request_id": req["request_id"],
        "repo_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "model": MODEL,
        "model_calls": len(tasks),
        "corpus": {"ingested_utf8_files": len(files), "topics": {key: len(value) for key, value in topic_files.items()}},
        "tasks": tasks,
        "automatic_pass_count": sum(int(task["automatic_pass"]) for task in tasks),
        "automatic_all_pass": all_auto,
        "usage": {
            "input_tokens": int(total_input),
            "output_tokens": int(total_output),
            "copilot_cost_raw": total_cost,
            "copilot_aiu_raw": total_aiu,
        },
        "integrity": integrity,
        "calibration": calibration,
        "interpretation_boundary": "One bounded assistant-run user-like session. This is real Wiki + real Luna evidence, but it is not a substitute for repeated natural multi-session use in the user's own VS Code workspace.",
    }
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    md = [
        "# E010 real-user Luna dogfood", "",
        f"Commit: `{result['repo_commit']}`", f"Model: `{MODEL}`", f"Model calls: **{len(tasks)}**", "",
        f"Corpus: **{len(files)} UTF-8 tracked files** across 3 natural topics, plus one temporary temporal-semantics topic.", "",
        "| task | chosen topic | automatic | citations | seconds |",
        "|---|---|---:|---:|---:|",
    ]
    for task in tasks:
        md.append(
            f"| {task['task_id']} | {task['topic']} | {'PASS' if task['automatic_pass'] else 'FAIL'} | {task['citation_count']} | {task['elapsed_seconds']:.3f} |"
        )
    md.extend([
        "", f"Automatic checks: **{result['automatic_pass_count']}/{len(tasks)}**", "",
        "## Usage", "",
        f"- input tokens: {result['usage']['input_tokens']}",
        f"- output tokens: {result['usage']['output_tokens']}",
        f"- Copilot cost raw: {result['usage']['copilot_cost_raw']}",
        f"- Copilot AIU raw: {result['usage']['copilot_aiu_raw']}", "",
        "## Boundary", "",
        result["interpretation_boundary"], "",
        "Full answers, discovery rows, cited-source previews, and per-call OTEL summaries are in `result.json` and the per-task JSON files.",
    ])
    (output_dir / "result.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({
        "format": result["format"],
        "request_id": result["request_id"],
        "model": result["model"],
        "model_calls": result["model_calls"],
        "ingested_utf8_files": result["corpus"]["ingested_utf8_files"],
        "automatic_pass_count": result["automatic_pass_count"],
        "automatic_all_pass": result["automatic_all_pass"],
        "usage": result["usage"],
    }, indent=2, ensure_ascii=False))
    return 0 if all_auto else 2


if __name__ == "__main__":
    raise SystemExit(main())
