from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

from dogfood.llm_wiki.calibration import resolve_topic
from dogfood.llm_wiki.retrieval import (
    RETRIEVAL_STRUCTURAL_EXPAND_V1,
    RETRIEVAL_WHOLE_OBJECT_V0,
    render_context,
    search,
)

REPO = Path(__file__).resolve().parents[2]
MODEL = "gpt-5.6-luna"
K8S_SHA = "551b56f979e1e020bd5ebd6ca1b8da7f32d02ae0"
CPYTHON_SHA = "07624ef11b924b39da97e978536f34f740e39575"
MAX_FILE_BYTES = 900_000
SRC_RE = re.compile(r"\bsrc-[0-9a-f-]+\b")

NASA_URLS = [
    "https://www.nasa.gov/news-release/nasa-adds-mission-to-artemis-lunar-program-updates-architecture/",
    "https://www.nasa.gov/news-release/nasa-to-share-artemis-ii-flight-readiness-review-update/",
    "https://www.nasa.gov/blogs/missions/2026/04/01/live-artemis-ii-launch-day-updates/",
    "https://www.nasa.gov/blogs/missions/2026/04/01/artemis-ii-flight-update-apogee-raise-burn-complete-crew-looks-ahead-to-proximity-operations/",
    "https://www.nasa.gov/blogs/missions/2026/04/01/artemis-ii-flight-update-proximity-operations-complete-perigee-raise-burn-up-next/",
    "https://www.nasa.gov/blogs/missions/2026/04/02/artemis-ii-flight-update-perigee-raise-burn-complete/",
    "https://www.nasa.gov/news-release/nasas-artemis-ii-mission-leaves-earth-orbit-for-flight-around-moon/",
    "https://www.nasa.gov/news-release/nasa-welcomes-record-setting-artemis-ii-moonfarers-back-to-earth/",
    "https://www.nasa.gov/centers-and-facilities/johnson/artemis-ii-mission-milestones-an-image-and-video-recap/",
    "https://science.nasa.gov/missions/artemis/artemis-2/nasas-artemis-ii-moon-mission-research-continues-on-earth/",
]

CASES = [
    {
        "id": "kubernetes-pdb",
        "expected_topic": "kubernetes official docs",
        "query": (
            "I set a PodDisruptionBudget with maxUnavailable: 0. Does that guarantee zero downtime even if a node "
            "crashes or another involuntary disruption happens? Explain what a PDB actually protects against, what it "
            "cannot prevent, and any important caveats about voluntary disruptions."
        ),
        "query_class": "synthesis",
        "answer_groups": [
            ["voluntary eviction", "voluntary disruptions", "voluntary disruption"],
            ["involuntary", "node crash", "node failure", "hardware failure"],
            ["not guarantee", "does not guarantee", "cannot guarantee", "doesn't guarantee"],
        ],
        "context_needles": [
            "voluntary",
            "involuntary",
            "does not truly guarantee",
        ],
    },
    {
        "id": "cpython-multiprocessing",
        "expected_topic": "cpython documentation",
        "query": (
            "In the current CPython documentation, what is the default multiprocessing start method on POSIX, why "
            "was the default changed away from fork, and what warning or caveat applies if I explicitly use fork from "
            "a multithreaded process?"
        ),
        "query_class": "synthesis",
        "answer_groups": [
            ["forkserver"],
            ["3.14", "python 3.14"],
            ["multithread", "multiple threads", "threaded"],
            ["deprecationwarning", "deprecation warning"],
        ],
        "context_needles": [
            "forkserver",
            "Changed in version 3.14",
            "DeprecationWarning",
        ],
    },
    {
        "id": "nasa-artemis-ii",
        "expected_topic": "nasa artemis ii articles",
        "query": (
            "Reconstruct the Artemis II timeline from launch through leaving Earth orbit to splashdown. Give dates "
            "and times only where the captured NASA articles support them, and identify any later editor correction "
            "or update in the corpus without turning that update into a different mission event."
        ),
        "query_class": "synthesis",
        "answer_groups": [
            ["april 1", "apr 1"],
            ["april 2", "apr 2", "translunar injection"],
            ["april 10", "apr 10", "splashdown"],
            ["may 7", "editor", "updated"],
        ],
        "context_needles": [
            "April 1, 2026",
            "April 10, 2026",
            "updated on May 7, 2026",
        ],
    },
]


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command_failed rc={proc.returncode} cmd={cmd[:5]} stderr={proc.stderr[-1200:]} stdout={proc.stdout[-1200:]}"
        )
    return proc


def run_cli(root: Path, args: list[str], *, otel: Path | None = None, timeout: int = 900, check: bool = True):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    if otel is not None:
        env["COPILOT_OTEL_FILE_EXPORTER_PATH"] = str(otel)
        env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
        env["OTEL_SERVICE_NAME"] = "llm-wiki-e017-external"
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
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"cli_failed rc={proc.returncode} args={args[:4]} stderr={proc.stderr[-1600:]} stdout={proc.stdout[-1600:]}"
        )
    return proc


def parse_json_lines(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def batched(values: list[Path], size: int = 40):
    for i in range(0, len(values), size):
        yield values[i : i + size]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_copy_name(rel: Path, index: int) -> str:
    tail = "__".join(rel.parts[-5:])
    tail = re.sub(r"[^0-9A-Za-z._-]+", "_", tail)
    digest = hashlib.sha1(rel.as_posix().encode("utf-8")).hexdigest()[:10]
    if len(tail) > 180:
        tail = tail[-180:]
    return f"{index:05d}__{digest}__{tail}"


def clone_sparse(repo_url: str, sha: str, sparse_path: str, target: Path) -> None:
    run(["git", "init", str(target)])
    run(["git", "-C", str(target), "remote", "add", "origin", repo_url])
    run(["git", "-C", str(target), "sparse-checkout", "init", "--cone"])
    run(["git", "-C", str(target), "sparse-checkout", "set", sparse_path])
    run(
        [
            "git",
            "-C",
            str(target),
            "-c",
            "protocol.version=2",
            "fetch",
            "--depth",
            "1",
            "--filter=blob:none",
            "origin",
            sha,
        ],
        timeout=1200,
    )
    run(["git", "-C", str(target), "checkout", "--detach", "FETCH_HEAD"], timeout=1200)
    actual = run(["git", "-C", str(target), "rev-parse", "HEAD"]).stdout.strip()
    if actual != sha:
        raise RuntimeError(f"pinned_commit_mismatch expected={sha} actual={actual}")


def prepare_git_corpus(
    temp: Path,
    *,
    corpus_id: str,
    repo_url: str,
    sha: str,
    sparse_path: str,
    suffix: str,
    exclude_prefixes: tuple[str, ...] = (),
) -> dict[str, Any]:
    checkout = temp / f"{corpus_id}-checkout"
    clone_sparse(repo_url, sha, sparse_path, checkout)
    out = temp / f"{corpus_id}-evidence"
    out.mkdir()
    rows = []
    skipped_large = 0
    candidates = sorted(p for p in (checkout / sparse_path).rglob(f"*{suffix}") if p.is_file())
    index = 0
    for src in candidates:
        rel = src.relative_to(checkout)
        rel_text = rel.as_posix()
        if any(rel_text.startswith(prefix) for prefix in exclude_prefixes):
            continue
        data = src.read_bytes()
        if b"\0" in data:
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if len(data) > MAX_FILE_BYTES:
            skipped_large += 1
            continue
        index += 1
        dest = out / safe_copy_name(rel, index)
        dest.write_bytes(data)
        rows.append(
            {
                "evidence_name": dest.name,
                "origin_path": rel_text,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    if not rows:
        raise RuntimeError(f"empty_git_corpus:{corpus_id}")
    return {
        "id": corpus_id,
        "kind": "git",
        "repo_url": repo_url,
        "revision": sha,
        "sparse_path": sparse_path,
        "files": [out / row["evidence_name"] for row in rows],
        "manifest_rows": rows,
        "file_count": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
        "skipped_large": skipped_large,
    }


def fetch_url(url: str, *, attempts: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; LLM-Wiki-Lab-E017/1.0; +https://github.com/YB-Park/llm-wiki-lab)"
                },
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read()
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"fetch_failed url={url} error={last}")


def normalize_nasa_html(raw: bytes, url: str) -> tuple[str, str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "svg", "noscript"]):
        tag.decompose()
    title_node = soup.find("h1") or soup.find("title")
    title = " ".join(title_node.get_text(" ", strip=True).split()) if title_node else url
    main = soup.find("main") or soup.find("article") or soup.body or soup
    lines: list[str] = []
    for raw_line in main.get_text("\n").splitlines():
        line = " ".join(raw_line.split())
        if line:
            lines.append(line)
    body = "\n".join(lines)
    normalized = (
        f"TITLE: {title}\n"
        f"ORIGIN URL: {url}\n"
        f"RAW HTML SHA256: {sha256_bytes(raw)}\n"
        f"CAPTURE TYPE: normalized visible text from official NASA page\n\n"
        f"{body}\n"
    )
    return title, normalized


def prepare_nasa_corpus(temp: Path) -> dict[str, Any]:
    out = temp / "nasa-evidence"
    out.mkdir()
    rows = []
    files = []
    for index, url in enumerate(NASA_URLS, start=1):
        raw = fetch_url(url)
        title, normalized = normalize_nasa_html(raw, url)
        data = normalized.encode("utf-8")
        slug = re.sub(r"[^0-9A-Za-z]+", "-", title).strip("-").lower()[:100] or f"article-{index}"
        dest = out / f"{index:02d}__{slug}.txt"
        dest.write_bytes(data)
        files.append(dest)
        rows.append(
            {
                "evidence_name": dest.name,
                "origin_url": url,
                "title": title,
                "raw_html_bytes": len(raw),
                "raw_html_sha256": sha256_bytes(raw),
                "normalized_bytes": len(data),
                "normalized_sha256": sha256_bytes(data),
            }
        )
    return {
        "id": "nasa",
        "kind": "web_capture",
        "revision": "captured-at-run",
        "files": files,
        "manifest_rows": rows,
        "file_count": len(files),
        "bytes": sum(row["normalized_bytes"] for row in rows),
        "raw_html_bytes": sum(row["raw_html_bytes"] for row in rows),
    }


def prepare_corpora(temp: Path) -> dict[str, dict[str, Any]]:
    return {
        "kubernetes": prepare_git_corpus(
            temp,
            corpus_id="kubernetes",
            repo_url="https://github.com/kubernetes/website.git",
            sha=K8S_SHA,
            sparse_path="content/en/docs",
            suffix=".md",
            exclude_prefixes=("content/en/docs/reference/kubernetes-api/",),
        ),
        "cpython": prepare_git_corpus(
            temp,
            corpus_id="cpython",
            repo_url="https://github.com/python/cpython.git",
            sha=CPYTHON_SHA,
            sparse_path="Doc",
            suffix=".rst",
        ),
        "nasa": prepare_nasa_corpus(temp),
    }


def concept_groups_pass(answer: str, groups: list[list[str]]) -> tuple[bool, list[bool]]:
    lower = answer.lower()
    checks = [any(term.lower() in lower for term in group) for group in groups]
    return all(checks), checks


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


def _resolve_topic_id(root: Path, label: str) -> str:
    return str(resolve_topic(root, label)["topic_id"])


def context_diagnostic(root: Path, query: str, topic: str, needles: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, mode in (
        ("w0", RETRIEVAL_WHOLE_OBJECT_V0),
        ("x1", RETRIEVAL_STRUCTURAL_EXPAND_V1),
    ):
        topic_id = _resolve_topic_id(root, topic)
        hits = search(root, query, top_k=8, snippet_chars=1200, topic_id=topic_id, mode=mode)
        context = render_context(
            root,
            query,
            top_k=8,
            max_chars_per_source=1200,
            topic_id=topic_id,
            mode=mode,
        )
        lower = context.lower()
        result[key] = {
            "hits": [
                {
                    "rank": i + 1,
                    "name": hit.source.name,
                    "score": hit.score,
                    "source_ids": list(hit.source_ids),
                    "retrieval_mode": hit.retrieval_mode,
                    "ranking_locator": hit.ranking_locator,
                    "context_locator": hit.context_locator,
                    "snippet": hit.snippet,
                }
                for i, hit in enumerate(hits)
            ],
            "context": context,
            "needle_checks": [needle.lower() in lower for needle in needles],
            "needles_all": all(needle.lower() in lower for needle in needles),
        }
    return result


def ingest_topic(root: Path, topic: str, files: list[Path]) -> None:
    run_cli(root, ["topic", "add", topic])
    for chunk in batched(files):
        run_cli(root, ["ingest", *[str(p) for p in chunk], "--topic", topic], timeout=1200)


def discover_topic(root: Path, query: str) -> dict[str, Any]:
    rows = parse_json_lines(run_cli(root, ["discover", query, "--json", "--top-k-per-topic", "4"], timeout=1200).stdout)
    rows.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)
    return {"chosen": rows[0] if rows else None, "top_rows": rows[:10]}


def run_model_ask(root: Path, out_dir: Path, case: dict[str, Any], topic: str) -> dict[str, Any]:
    otel = out_dir / f"otel-{case['id']}.jsonl"
    started = time.monotonic()
    proc = run_cli(
        root,
        [
            "ask",
            case["query"],
            "--topic",
            topic,
            "--class",
            case["query_class"],
            "--allow-model-call",
            "--model",
            MODEL,
            "--max-ai-credits",
            "30",
        ],
        otel=otel,
        timeout=1200,
        check=False,
    )
    elapsed = round(time.monotonic() - started, 3)
    answer = ""
    model_receipt_ok = False
    if proc.stdout:
        lines = proc.stdout.splitlines()
        if lines and lines[0].strip() == f"MODEL {MODEL}":
            model_receipt_ok = True
            answer = "\n".join(lines[1:]).strip()
    cited = source_ids_from_answer(answer)
    checks = []
    for source_id in cited[:8]:
        shown = run_cli(root, ["source", "show", source_id, "--topic", topic], check=False)
        checks.append(
            {
                "source_id": source_id,
                "resolved": shown.returncode == 0 and shown.stdout.startswith("SOURCE "),
                "preview": shown.stdout[:2400],
            }
        )
    concepts_ok, concept_checks = concept_groups_pass(answer, case["answer_groups"])
    tele = otel_summary(otel)
    exact_model = (not tele["models"]) or MODEL in tele["models"]
    return {
        "attempted": True,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-1800:],
        "stderr_tail": proc.stderr[-1800:],
        "elapsed_seconds": elapsed,
        "model_receipt_ok": model_receipt_ok,
        "answer": answer,
        "cited_source_ids": cited,
        "citation_count": len(cited),
        "citations_resolve": bool(cited) and all(row["resolved"] for row in checks),
        "source_checks": checks,
        "concept_groups": case["answer_groups"],
        "concept_group_checks": concept_checks,
        "concepts_pass": concepts_ok,
        "otel": tele,
        "exact_model_observed": exact_model,
        "automatic_pass": (
            proc.returncode == 0
            and model_receipt_ok
            and bool(answer)
            and bool(cited)
            and all(row["resolved"] for row in checks)
            and concepts_ok
            and exact_model
        ),
    }


def load_request() -> dict[str, Any]:
    path = REPO / "remote-lab" / "e017-external-request.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "request_id": "e017-external-real-user-v0",
        "model": MODEL,
        "max_ai_credits_per_call": 30,
        "max_model_calls": 3,
    }
    if data != expected:
        raise SystemExit(f"E017-STOP request_mismatch actual={data}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-model", action="store_true")
    args = parser.parse_args()
    request = load_request()
    out_dir = REPO / "remote-lab" / "out" / "e017-external"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*"):
        if old.is_file():
            old.unlink()

    with tempfile.TemporaryDirectory(prefix="llm-wiki-e017-") as td:
        temp = Path(td)
        corpora = prepare_corpora(temp)
        wiki = temp / "wiki"
        run_cli(wiki, ["init"])
        topic_to_corpus = {
            "kubernetes official docs": corpora["kubernetes"],
            "cpython documentation": corpora["cpython"],
            "nasa artemis ii articles": corpora["nasa"],
        }
        for topic, corpus in topic_to_corpus.items():
            ingest_topic(wiki, topic, corpus["files"])

        case_results = []
        model_attempts = 0
        for case in CASES:
            discovery = discover_topic(wiki, case["query"])
            chosen = discovery["chosen"]
            chosen_topic = chosen["topic_label"] if chosen else case["expected_topic"]
            diagnostics = context_diagnostic(wiki, case["query"], chosen_topic, case["context_needles"])
            row: dict[str, Any] = {
                "id": case["id"],
                "query": case["query"],
                "expected_topic": case["expected_topic"],
                "chosen_topic": chosen_topic,
                "discovery_expected_topic": chosen_topic == case["expected_topic"],
                "discovery": discovery,
                "context_needles": case["context_needles"],
                "retrieval": diagnostics,
            }
            if args.execute_model:
                model_attempts += 1
                row["ask"] = run_model_ask(wiki, out_dir, case, chosen_topic)
            case_results.append(row)

        if args.execute_model and model_attempts != request["max_model_calls"]:
            raise RuntimeError(f"model_attempt_guard:{model_attempts}")

        integrity = json.loads(run_cli(wiki, ["integrity"]).stdout)
        calibration = json.loads(run_cli(wiki, ["calibration", "export"]).stdout)

    corpus_summary = {}
    corpus_manifest = {}
    for key, corpus in corpora.items():
        corpus_summary[key] = {
            "kind": corpus["kind"],
            "revision": corpus["revision"],
            "file_count": corpus["file_count"],
            "bytes": corpus["bytes"],
            **({"raw_html_bytes": corpus["raw_html_bytes"]} if "raw_html_bytes" in corpus else {}),
            **({"repo_url": corpus["repo_url"], "skipped_large": corpus["skipped_large"]} if corpus["kind"] == "git" else {}),
        }
        corpus_manifest[key] = corpus["manifest_rows"]

    usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "copilot_cost_raw": 0.0,
        "copilot_aiu_raw": 0.0,
    }
    if args.execute_model:
        for row in case_results:
            tele = row.get("ask", {}).get("otel", {})
            usage["input_tokens"] += int(float(tele.get("gen_ai.usage.input_tokens", 0.0)))
            usage["output_tokens"] += int(float(tele.get("gen_ai.usage.output_tokens", 0.0)))
            usage["cache_read_input_tokens"] += int(float(tele.get("gen_ai.usage.cache_read.input_tokens", 0.0)))
            usage["copilot_cost_raw"] += float(tele.get("github.copilot.cost", 0.0))
            usage["copilot_aiu_raw"] += float(tele.get("github.copilot.aiu", 0.0))

    result = {
        "format": "E017-EXTERNAL-REAL-USER-v0",
        "repo_commit": run(["git", "rev-parse", "HEAD"], cwd=REPO).stdout.strip(),
        "execute_model": args.execute_model,
        "model": MODEL if args.execute_model else None,
        "model_call_attempts": model_attempts,
        "request": request,
        "corpora": corpus_summary,
        "cases": case_results,
        "usage": usage,
        "integrity": integrity,
        "calibration": calibration,
        "interpretation_boundary": (
            "Three bounded public-corpus user-like cases. Automatic concept checks are diagnostics only; manual answer/context review is required."
        ),
    }
    (out_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "corpus-manifest.json").write_text(
        json.dumps(corpus_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md = [
        "# E017 external-corpus real-user dogfood",
        "",
        f"Commit: `{result['repo_commit']}`",
        f"Mode: `{'real Luna' if args.execute_model else 'zero-model preflight'}`",
        f"Model-call attempts: **{model_attempts}**",
        "",
        "## Corpora",
        "",
        "| corpus | files | bytes | revision |",
        "|---|---:|---:|---|",
    ]
    for key, row in corpus_summary.items():
        md.append(f"| {key} | {row['file_count']} | {row['bytes']} | {row['revision']} |")
    md.extend(
        [
            "",
            "## Cases",
            "",
            "| case | discovered topic | W0 needles | X1 needles | Ask auto | citations |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in case_results:
        ask = row.get("ask")
        md.append(
            f"| {row['id']} | {row['chosen_topic']} | "
            f"{sum(row['retrieval']['w0']['needle_checks'])}/{len(row['context_needles'])} | "
            f"{sum(row['retrieval']['x1']['needle_checks'])}/{len(row['context_needles'])} | "
            f"{('PASS' if ask and ask['automatic_pass'] else 'FAIL') if args.execute_model else 'n/a'} | "
            f"{ask['citation_count'] if ask else 0} |"
        )
    if args.execute_model:
        md.extend(
            [
                "",
                "## Usage",
                "",
                f"- input tokens: {usage['input_tokens']}",
                f"- output tokens: {usage['output_tokens']}",
                f"- cache-read input tokens: {usage['cache_read_input_tokens']}",
                f"- Copilot cost raw: {usage['copilot_cost_raw']}",
                f"- Copilot AIU raw: {usage['copilot_aiu_raw']}",
            ]
        )
    md.extend(
        [
            "",
            "## Boundary",
            "",
            result["interpretation_boundary"],
            "",
            "Full W0/X1 contexts, answers, citation previews, and corpus manifests are in `result.json` and `corpus-manifest.json`.",
        ]
    )
    (out_dir / "result.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "format": result["format"],
                "execute_model": args.execute_model,
                "model_call_attempts": model_attempts,
                "corpora": corpus_summary,
                "cases": [
                    {
                        "id": row["id"],
                        "chosen_topic": row["chosen_topic"],
                        "expected_topic": row["expected_topic"],
                        "w0_needles": row["retrieval"]["w0"]["needle_checks"],
                        "x1_needles": row["retrieval"]["x1"]["needle_checks"],
                        "ask_auto": row.get("ask", {}).get("automatic_pass"),
                    }
                    for row in case_results
                ],
                "usage": usage,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.execute_model and any(not row.get("ask", {}).get("automatic_pass", False) for row in case_results):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
