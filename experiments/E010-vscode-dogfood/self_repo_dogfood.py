from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.retrieval import render_context, search
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file


QUERY_CASES = [
    {
        "id": "north-star",
        "query": "proper VS Code-first LLM Wiki research experiments are means not the product North Star",
        "expected": ["HANDOFF.md", "README.md"],
    },
    {
        "id": "initial-research-question",
        "query": "minimum architecture and operating discipline compound useful understanding faster than error and maintenance debt",
        "expected": ["docs/00-project-charter.md"],
    },
    {
        "id": "convergence-rule",
        "query": "Stop adding core infrastructure by default actual dogfood failure E013 E015 reproducible data-loss trust failure",
        "expected": ["docs/09-alpha-core-readiness-gate.md", "HANDOFF.md"],
    },
    {
        "id": "e013-minima",
        "query": "10 topics 20 completed maintenance cycles 30 sessionized visits INSUFFICIENT_CALIBRATION_DATA",
        "expected": ["dogfood/README.md", "dogfood/llm_wiki/calibration.py"],
    },
    {
        "id": "retrieval-shadow",
        "query": "whole_object_v0 structural_expand_v1 X1 shadow non-default realistic E015",
        "expected": ["docs/09-alpha-core-readiness-gate.md", "HANDOFF.md", "dogfood/llm_wiki/retrieval.py"],
    },
    {
        "id": "temporal-semantics",
        "query": "correction change dispute effective_at recorded_at unresolved disagreement no hidden winner",
        "expected": ["decisions/ADR-0005-minimum-explicit-temporal-and-dispute-semantics.md", "dogfood/llm_wiki/temporal.py"],
    },
    {
        "id": "exact-provenance",
        "query": "exact raw-span provenance local pointer not claim graph historical pointer successor",
        "expected": ["decisions/ADR-0006-local-exact-raw-span-provenance-not-claim-graph.md", "dogfood/llm_wiki/provenance.py"],
    },
    {
        "id": "canonical-log",
        "query": "canonical JSONL newline terminated torn_tail corrupt_prefix O_APPEND fsync no automatic repair",
        "expected": ["decisions/ADR-0008-canonical-jsonl-crash-containment.md", "dogfood/llm_wiki/jsonl_log.py"],
    },
    {
        "id": "vscode-first",
        "query": "VS Code-first not VS Code-only editor-agnostic core CLI fallback first-class interaction surface",
        "expected": ["decisions/ADR-0002-vscode-first-editor-agnostic-core.md", "docs/00-project-charter.md"],
    },
    {
        "id": "answer-authority",
        "query": "model answer read-only raw evidence authoritative never written canonical state explicit consent",
        "expected": ["dogfood/README.md", "docs/09-alpha-core-readiness-gate.md"],
    },
    {
        "id": "manifest-loss",
        "query": "missing canonical manifest surviving raw provenance prior state fail closed do not recreate empty history",
        "expected": ["dogfood/llm_wiki/workspace_loss.py", "HANDOFF.md", "dogfood/tests/test_manifest_loss_surviving_raw.py"],
    },
    {
        "id": "luna-discovery",
        "query": "Discover Copilot Models exact gpt-5.6-luna fuzzy reject no fallback zero generation",
        "expected": ["dogfood/vscode/lm-discovery.js", "dogfood/vscode/package.json"],
    },
]


def tracked_paths(repo: Path) -> list[Path]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=repo)
    return [repo / item.decode("utf-8") for item in out.split(b"\0") if item]


def accepted_text_files(repo: Path) -> tuple[list[Path], list[dict]]:
    accepted: list[Path] = []
    skipped: list[dict] = []
    for path in tracked_paths(repo):
        rel = path.relative_to(repo).as_posix()
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data:
            skipped.append({"path": rel, "reason": "nul_byte"})
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            skipped.append({"path": rel, "reason": "not_utf8"})
            continue
        accepted.append(path)
    return accepted, skipped


def inspect_product_surface(repo: Path, basename_counts: Counter[str], collapsed_sources: dict[str, list[str]], manifest_rows: list[dict]) -> dict:
    package = json.loads((repo / "dogfood/vscode/package.json").read_text(encoding="utf-8"))
    commands = [row.get("command", "") for row in package.get("contributes", {}).get("commands", [])]
    titles = [row.get("title", "") for row in package.get("contributes", {}).get("commands", [])]
    command_text = "\n".join([*commands, *titles]).casefold()
    extension = (repo / "dogfood/vscode/extension.js").read_text(encoding="utf-8")
    docs_text = "\n".join(
        (repo / path).read_text(encoding="utf-8")
        for path in ("README.md", "HANDOFF.md", "dogfood/README.md")
        if (repo / path).exists()
    ).casefold()

    duplicate_names = {name: count for name, count in basename_counts.items() if count > 1}
    original_path_fields = {key for row in manifest_rows for key in row if key in {"path", "relative_path", "workspace_path", "uri"}}

    return {
        "vscode_command_count": len(commands),
        "vscode_commands": commands,
        "temporal_core_exists": (repo / "dogfood/llm_wiki/temporal.py").exists(),
        "vscode_exposes_correction": "correct" in command_text or "correction" in command_text,
        "vscode_exposes_change_semantics": "effective" in command_text or "change source" in command_text,
        "vscode_exposes_dispute": "dispute" in command_text or "contested" in command_text,
        "vscode_exposes_feedback": "feedback" in command_text or "helpful" in command_text,
        "vscode_search_requires_selected_topic": "async function searchTopic" in extension and "const topic = await selectTopic" in extension,
        "vscode_has_explicit_global_search_command": any("global" in value.casefold() and "search" in value.casefold() for value in [*commands, *titles]),
        "backup_restore_documented_in_primary_user_docs": "backup" in docs_text and "restore" in docs_text,
        "manifest_preserves_original_relative_path": bool(original_path_fields),
        "manifest_path_fields_seen": sorted(original_path_fields),
        "duplicate_basename_groups": len(duplicate_names),
        "duplicate_basename_examples": sorted(duplicate_names.items(), key=lambda row: (-row[1], row[0]))[:12],
        "source_ids_representing_multiple_tracked_paths": len(collapsed_sources),
        "collapsed_source_examples": list(collapsed_sources.items())[:8],
    }


def run(repo: Path, output_dir: Path) -> dict:
    files, skipped = accepted_text_files(repo)
    basename_counts: Counter[str] = Counter(path.name for path in files)

    with tempfile.TemporaryDirectory(prefix="llm-wiki-selfdogfood-") as td:
        wiki = Path(td) / "wiki"
        ensure_workspace(wiki)
        topic = create_topic(wiki, "llm-wiki-lab self dogfood")
        topic_id = topic["topic_id"]

        source_paths: dict[str, set[str]] = defaultdict(set)
        total_bytes = 0
        for path in files:
            source, _ = ingest_file(wiki, path, topic_id=topic_id)
            rel = path.relative_to(repo).as_posix()
            source_paths[source.source_id].add(rel)
            total_bytes += path.stat().st_size

        query_results = []
        reciprocal_ranks = []
        context_nonempty = 0
        for case in QUERY_CASES:
            hits = search(wiki, case["query"], top_k=5, topic_id=topic_id)
            hit_rows = []
            first_rank = None
            for rank, hit in enumerate(hits, 1):
                paths = sorted({path for sid in hit.source_ids for path in source_paths.get(sid, set())})
                if first_rank is None and any(expected in paths for expected in case["expected"]):
                    first_rank = rank
                hit_rows.append(
                    {
                        "rank": rank,
                        "score": hit.score,
                        "name": hit.source.name,
                        "source_ids": list(hit.source_ids),
                        "tracked_paths": paths,
                        "snippet": " ".join(hit.snippet.split())[:500],
                    }
                )
            context = render_context(wiki, case["query"], top_k=5, topic_id=topic_id)
            if context.strip():
                context_nonempty += 1
            rr = 0.0 if first_rank is None else 1.0 / first_rank
            reciprocal_ranks.append(rr)
            query_results.append(
                {
                    **case,
                    "pass_top5": first_rank is not None,
                    "first_relevant_rank": first_rank,
                    "reciprocal_rank": rr,
                    "context_nonempty": bool(context.strip()),
                    "hits": hit_rows,
                }
            )

        manifest_rows = history(wiki)
        collapsed_sources = {
            source_id: sorted(paths)
            for source_id, paths in source_paths.items()
            if len(paths) > 1
        }
        surface = inspect_product_surface(repo, basename_counts, collapsed_sources, manifest_rows)

    hit_count = sum(1 for row in query_results if row["pass_top5"])
    hit_rate = hit_count / len(query_results)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
    stage_a_pass = hit_rate >= 0.90 and mrr >= 0.60 and context_nonempty == len(query_results)

    blockers = []
    if not stage_a_pass:
        blockers.append("self_repo_retrieval_signal_below_preregistered_threshold")
    if not surface["manifest_preserves_original_relative_path"] and surface["duplicate_basename_groups"]:
        blockers.append("ambiguous_basename_only_original_source_navigation")
    if not (surface["vscode_exposes_correction"] and surface["vscode_exposes_change_semantics"] and surface["vscode_exposes_dispute"]):
        blockers.append("vscode_does_not_expose_full_temporal_trust_semantics")
    if not surface["vscode_exposes_feedback"]:
        blockers.append("vscode_customer_feedback_not_first_class")
    if surface["vscode_search_requires_selected_topic"] and not surface["vscode_has_explicit_global_search_command"]:
        blockers.append("forgotten_topic_recovery_has_no_first_class_vscode_path")
    if not surface["backup_restore_documented_in_primary_user_docs"]:
        blockers.append("valuable_local_wiki_backup_restore_story_missing")
    blockers.extend(["real_vscode_copilot_exact_luna_gate_pending", "repeated_customer_like_multisession_use_pending"])

    result = {
        "format": "E010-SELF-REPO-DOGFOOD-v0",
        "repo_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "model_calls": 0,
        "corpus": {
            "tracked_files": len(tracked_paths(repo)),
            "ingested_utf8_files": len(files),
            "ingested_bytes": total_bytes,
            "skipped_files": skipped,
        },
        "retrieval": {
            "queries": len(query_results),
            "top5_hits": hit_count,
            "top5_hit_rate": hit_rate,
            "mean_reciprocal_rank": mrr,
            "contexts_nonempty": context_nonempty,
            "stage_a_pass": stage_a_pass,
            "cases": query_results,
        },
        "product_surface": surface,
        "customer_readiness": {
            "customer_ready_candidate": False,
            "blockers": blockers,
            "note": "Real Copilot and repeated customer-like use are deliberately not inferable from CI.",
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# E010 self-repo dogfood result",
        "",
        f"Commit: `{result['repo_commit']}`",
        f"Model calls: **{result['model_calls']}**",
        "",
        "## Corpus",
        "",
        f"- tracked files: {result['corpus']['tracked_files']}",
        f"- ingested UTF-8 text files: {result['corpus']['ingested_utf8_files']}",
        f"- skipped binary/non-UTF8 files: {len(result['corpus']['skipped_files'])}",
        "",
        "## Retrieval",
        "",
        f"- top-5 target hit rate: **{hit_rate:.3f}** ({hit_count}/{len(query_results)})",
        f"- mean reciprocal rank: **{mrr:.3f}**",
        f"- non-empty contexts: **{context_nonempty}/{len(query_results)}**",
        f"- Stage A: **{'PASS' if stage_a_pass else 'FAIL'}**",
        "",
        "| case | pass | first rank |",
        "|---|---:|---:|",
    ]
    for row in query_results:
        lines.append(f"| {row['id']} | {'yes' if row['pass_top5'] else 'no'} | {row['first_relevant_rank'] or '-'} |")
    lines.extend([
        "",
        "## Product blockers / pending gates",
        "",
        *[f"- {item}" for item in blockers],
        "",
        "This result is intentionally not a customer-readiness claim. See `README.md` in this experiment for the full gate.",
    ])
    (output_dir / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output", default="/tmp/e010-self-dogfood")
    args = parser.parse_args()
    result = run(Path(args.repo).resolve(), Path(args.output).resolve())
    print(json.dumps({
        "format": result["format"],
        "stage_a_pass": result["retrieval"]["stage_a_pass"],
        "top5_hit_rate": result["retrieval"]["top5_hit_rate"],
        "mrr": result["retrieval"]["mean_reciprocal_rank"],
        "ingested_utf8_files": result["corpus"]["ingested_utf8_files"],
        "customer_ready_candidate": result["customer_readiness"]["customer_ready_candidate"],
        "blockers": result["customer_readiness"]["blockers"],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
