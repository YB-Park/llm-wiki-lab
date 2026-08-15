from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.integrity import audit_alpha_integrity
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "remote-lab/out/e019-product-path-smoke"
REQUEST_PATH = ROOT / "remote-lab/e019-product-path-smoke-request.json"
MODEL = "gpt-5.6-luna"


def load_request() -> dict:
    row = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e019-product-path-smoke-20260816-1",
        "model": MODEL,
        "max_model_calls": 1,
        "max_ai_credits": 30,
        "source_path": "docs/12-autonomy-ux-philosophy.md",
        "source_git_blob": "ce68a3860066a0e795fb196b3b1cf7abc93ad4dc",
    }
    if row != expected:
        raise RuntimeError(f"request_mismatch:{row}")
    return row


def git_blob(path: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git_hash_object_failed:{proc.returncode}")
    return proc.stdout.strip()


def run_agent_cli(wiki: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["python", "-m", "dogfood.llm_wiki.agent_wiki_cli", "--root", str(wiki), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=900,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"agent_wiki_cli_failed:{proc.returncode}:{proc.stderr.strip() or proc.stdout.strip()}")
    return proc


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for child in OUT.iterdir():
        if child.is_file():
            child.unlink()

    execute_model = os.environ.get("E019_PRODUCT_SMOKE_EXECUTE_MODEL") == "1"
    result = {
        "format": "E019-PRODUCT-PATH-SMOKE-v0",
        "status": "STARTED",
        "model_calls": 0,
    }

    try:
        request = load_request()
        result["request"] = request
        source_path = ROOT / request["source_path"]
        actual_blob = git_blob(source_path)
        if actual_blob != request["source_git_blob"]:
            raise RuntimeError(f"source_blob_mismatch:{actual_blob}")

        preflight = {
            "source_git_blob": actual_blob,
            "product_module_exists": (ROOT / "dogfood/llm_wiki/agent_wiki.py").exists(),
            "product_cli_exists": (ROOT / "dogfood/llm_wiki/agent_wiki_cli.py").exists(),
            "model_calls_if_executed": 1,
        }
        if not all([preflight["product_module_exists"], preflight["product_cli_exists"]]):
            raise RuntimeError(f"product_path_missing:{preflight}")
        result["preflight"] = preflight

        if not execute_model:
            result["status"] = "PREFLIGHT_PASS"
        else:
            os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
            os.environ["OTEL_SERVICE_NAME"] = "llm-wiki-e019-product-smoke"
            os.environ["COPILOT_MCP_TOOL_CACHE"] = "false"
            os.environ["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(OUT / "otel.jsonl")

            with tempfile.TemporaryDirectory(prefix="e019-product-smoke-") as td:
                temp = Path(td)
                wiki = temp / "wiki"
                ensure_workspace(wiki)
                topic = create_topic(wiki, "E019 product smoke")
                source, _ = ingest_file(wiki, source_path, topic_id=topic["topic_id"])
                canonical_before = history(wiki)

                result["model_calls"] = 1
                first = run_agent_cli(
                    wiki,
                    [
                        "build",
                        source.source_id,
                        "--topic",
                        topic["topic_id"],
                        "--model",
                        request["model"],
                        "--max-ai-credits",
                        str(request["max_ai_credits"]),
                        "--allow-model-call",
                    ],
                )
                first_row = json.loads(first.stdout.strip())

                # The product's idempotent fast path must not need model authorization
                # and therefore must make zero additional model calls.
                second = run_agent_cli(
                    wiki,
                    ["build", source.source_id, "--topic", topic["topic_id"]],
                )
                second_row = json.loads(second.stdout.strip())

                search = run_agent_cli(wiki, ["search", "human admission agent wiki rebuildable", "--top-k", "3", "--json"])
                search_rows = [json.loads(line) for line in search.stdout.splitlines() if line.strip()]
                note_path = wiki / "agent-wiki" / "source-notes" / f"{source.source_id}.md"
                note_text = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
                integrity = audit_alpha_integrity(wiki)
                canonical_after = history(wiki)

                checks = {
                    "first_created": first_row.get("status") == "CREATED",
                    "first_exact_model": first_row.get("model") == MODEL,
                    "first_one_model_call": first_row.get("model_calls") == 1,
                    "second_reused": second_row.get("status") == "REUSED",
                    "second_zero_model_calls": second_row.get("model_calls") == 0,
                    "derived_search_returns_source": any(row.get("source_id") == source.source_id for row in search_rows),
                    "derived_search_is_noncanonical": all(row.get("epistemic_status") == "derived_noncanonical_agent_wiki" for row in search_rows),
                    "note_noncanonical_banner": "AGENT WIKI — NONCANONICAL / REBUILDABLE" in note_text,
                    "note_preserves_source_id": source.source_id in note_text,
                    "canonical_history_unchanged_by_maintenance": canonical_after == canonical_before,
                    "integrity_clean": integrity.get("ok") is True,
                    "exactly_one_real_model_call": result["model_calls"] == 1,
                }
                result.update(
                    {
                        "status": "PASS" if all(checks.values()) else "FAIL",
                        "source_id": source.source_id,
                        "first_receipt": first_row,
                        "second_receipt": second_row,
                        "search_rows": search_rows,
                        "checks": checks,
                        "integrity": integrity,
                        "note_preview": note_text[:5000],
                    }
                )
    except Exception as exc:
        result.update({
            "status": "INFRA_FAIL" if execute_model else "PREFLIGHT_FAIL",
            "error": f"{type(exc).__name__}:{exc}",
        })

    (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "format": result["format"],
        "status": result["status"],
        "model_calls": result["model_calls"],
        "preflight": result.get("preflight"),
        "checks": result.get("checks"),
        "error": result.get("error"),
    }, ensure_ascii=False, indent=2))

    if execute_model:
        return 0 if result["status"] in {"PASS", "FAIL"} else 2
    return 0 if result["status"] == "PREFLIGHT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
