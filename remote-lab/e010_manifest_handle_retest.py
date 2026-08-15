from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt-5.6-luna"
QUESTION = (
    "If the canonical manifest disappears while raw evidence or exact-provenance state survives, "
    "should the Wiki recreate an empty history or stop? Explain why."
)
SRC_RE = re.compile(r"\bsrc-[0-9A-Za-z-]+\b")


def load_e010_module():
    path = ROOT / "experiments/E010-vscode-dogfood/real_user_dogfood.py"
    spec = importlib.util.spec_from_file_location("e010_real_user", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("e010_module_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    req = json.loads((ROOT / "remote-lab/e010-manifest-handle-request.json").read_text(encoding="utf-8"))
    expected = {
        "request_id": "manifest-handle-retest-20260815-1",
        "model": MODEL,
        "max_model_calls": 1,
        "max_ai_credits": 30,
    }
    if req != expected:
        raise SystemExit("E010-MANIFEST-STOP request_mismatch")

    e010 = load_e010_module()
    out = ROOT / "remote-lab/out/e010-manifest-handle"
    out.mkdir(parents=True, exist_ok=True)
    for path in out.glob("*"):
        if path.is_file():
            path.unlink()

    result = {
        "format": "E010-MANIFEST-HANDLE-RETEST-v1",
        "request_id": req["request_id"],
        "model": MODEL,
        "question": QUESTION,
    }

    try:
        with tempfile.TemporaryDirectory(prefix="e010-manifest-handle-") as td:
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
            otel = out / "otel.jsonl"
            started = time.monotonic()
            proc = e010.run_cli(
                wiki,
                [
                    "ask", QUESTION,
                    "--topic", chosen["topic_label"],
                    "--class", "exact_provenance",
                    "--allow-model-call",
                    "--model", MODEL,
                    "--max-ai-credits", "30",
                ],
                otel=otel,
            )
            elapsed = round(time.monotonic() - started, 3)
            lines = proc.stdout.splitlines()
            if not lines or lines[0].strip() != f"MODEL {MODEL}":
                raise RuntimeError("unexpected_model_receipt")
            answer = "\n".join(lines[1:]).strip()
            cited = list(dict.fromkeys(SRC_RE.findall(answer)))
            source_checks = []
            for sid in cited:
                shown = e010.run_cli(wiki, ["source", "show", sid, "--topic", chosen["topic_label"]]).stdout
                source_checks.append({"source_id": sid, "resolved": shown.startswith("SOURCE "), "preview": shown[:1200]})
            low = answer.lower()
            concept_checks = {
                "fail_closed": any(term in low for term in ["fail closed", "fail-closed", "stop", "refuse"]),
                "prior_state": any(term in low for term in ["raw", "provenance", "prior state", "state loss"]),
                "no_empty_recreation": any(term in low for term in ["do not recreate", "must not recreate", "not recreate", "empty history", "missing manifest", "state loss"]),
            }
            integrity = json.loads(e010.run_cli(wiki, ["integrity"]).stdout)
            result.update({
                "status": "PASS" if cited and all(x["resolved"] for x in source_checks) and all(concept_checks.values()) else "FAIL",
                "ingested_utf8_files": len(files),
                "chosen_topic": chosen["topic_label"],
                "discovery_top": discovered[:6],
                "elapsed_seconds": elapsed,
                "answer": answer,
                "cited_source_ids": cited,
                "source_checks": source_checks,
                "concept_checks": concept_checks,
                "integrity": integrity,
            })
    except Exception as exc:
        result.update({"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"})

    (out / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result.get(key) for key in ["format", "request_id", "model", "status", "ingested_utf8_files", "chosen_topic", "cited_source_ids", "concept_checks", "error"]}, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
