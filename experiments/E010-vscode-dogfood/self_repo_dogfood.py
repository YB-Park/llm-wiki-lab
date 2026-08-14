from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.retrieval import render_context, search
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file


# Stage A retrieval questions/expected sources are frozen from E010 result v0.
QUERY_CASES = [
    {"id": "north-star", "query": "proper VS Code-first LLM Wiki research experiments are means not the product North Star", "expected": ["HANDOFF.md", "README.md"]},
    {"id": "initial-research-question", "query": "minimum architecture and operating discipline compound useful understanding faster than error and maintenance debt", "expected": ["docs/00-project-charter.md"]},
    {"id": "convergence-rule", "query": "Stop adding core infrastructure by default actual dogfood failure E013 E015 reproducible data-loss trust failure", "expected": ["docs/09-alpha-core-readiness-gate.md", "HANDOFF.md"]},
    {"id": "e013-minima", "query": "10 topics 20 completed maintenance cycles 30 sessionized visits INSUFFICIENT_CALIBRATION_DATA", "expected": ["dogfood/README.md", "dogfood/llm_wiki/calibration.py"]},
    {"id": "retrieval-shadow", "query": "whole_object_v0 structural_expand_v1 X1 shadow non-default realistic E015", "expected": ["docs/09-alpha-core-readiness-gate.md", "HANDOFF.md", "dogfood/llm_wiki/retrieval.py"]},
    {"id": "temporal-semantics", "query": "correction change dispute effective_at recorded_at unresolved disagreement no hidden winner", "expected": ["decisions/ADR-0005-minimum-explicit-temporal-and-dispute-semantics.md", "dogfood/llm_wiki/temporal.py"]},
    {"id": "exact-provenance", "query": "exact raw-span provenance local pointer not claim graph historical pointer successor", "expected": ["decisions/ADR-0006-local-exact-raw-span-provenance-not-claim-graph.md", "dogfood/llm_wiki/provenance.py"]},
    {"id": "canonical-log", "query": "canonical JSONL newline terminated torn_tail corrupt_prefix O_APPEND fsync no automatic repair", "expected": ["decisions/ADR-0008-canonical-jsonl-crash-containment.md", "dogfood/llm_wiki/jsonl_log.py"]},
    {"id": "vscode-first", "query": "VS Code-first not VS Code-only editor-agnostic core CLI fallback first-class interaction surface", "expected": ["decisions/ADR-0002-vscode-first-editor-agnostic-core.md", "docs/00-project-charter.md"]},
    {"id": "answer-authority", "query": "model answer read-only raw evidence authoritative never written canonical state explicit consent", "expected": ["dogfood/README.md", "docs/09-alpha-core-readiness-gate.md"]},
    {"id": "manifest-loss", "query": "missing canonical manifest surviving raw provenance prior state fail closed do not recreate empty history", "expected": ["dogfood/llm_wiki/workspace_loss.py", "HANDOFF.md", "dogfood/tests/test_manifest_loss_surviving_raw.py"]},
    {"id": "luna-discovery", "query": "Discover Copilot Models exact gpt-5.6-luna fuzzy reject no fallback zero generation", "expected": ["dogfood/vscode/lm-discovery.js", "dogfood/vscode/package.json"]},
]


def tracked_paths(repo: Path) -> list[Path]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=repo)
    return [repo / item.decode("utf-8") for item in out.split(b"\0") if item]


def accepted_text_files(repo: Path) -> tuple[list[Path], list[dict]]:
    accepted: list[Path] = []
    skipped: list[dict] = []
    for path in tracked_paths(repo):
        if not path.is_file():
            continue
        rel = path.relative_to(repo).as_posix()
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
    commands = {row.get("command", "") for row in package.get("contributes", {}).get("commands", [])}
    extension = (repo / "dogfood/vscode/extension.js").read_text(encoding="utf-8")
    helpers_path = repo / "dogfood/vscode/product-helpers.js"
    helpers = helpers_path.read_text(encoding="utf-8") if helpers_path.exists() else ""
    backup_path = repo / "docs/11-local-backup-restore.md"
    backup = backup_path.read_text(encoding="utf-8") if backup_path.exists() else ""

    duplicate_names = {name: count for name, count in basename_counts.items() if count > 1}
    original_path_fields = {key for row in manifest_rows for key in row if key in {"path", "relative_path", "workspace_path", "uri"}}

    # P1 deliberately does NOT add workspace paths to canonical evidence identity.
    # The customer navigation fix is a VS Code-local hint guarded by evidence SHA,
    # with immutable raw provenance as the fallback when the workspace file changed.
    local_locator = all(token in extension for token in (
        "SOURCE_LOCATORS_KEY",
        "rememberSourceLocator",
        "sha256(fs.readFileSync(target))",
        "opening immutable evidence snapshot instead",
    )) and all(token in helpers for token in ("workspaceRelativePath", "resolveWorkspaceRelative", "locatorForRow"))
    safe_original_navigation = bool(local_locator and not original_path_fields)

    backup_story = all(token in backup for token in (
        "entire directory",
        "LLM Wiki: Doctor",
        "detection is not backup",
        "Do not resume normal ingest/update work",
    ))

    return {
        "vscode_command_count": len(commands),
        "vscode_commands": sorted(commands),
        "canonical_manifest_keeps_workspace_paths_out": not bool(original_path_fields),
        "manifest_path_fields_seen": sorted(original_path_fields),
        "vscode_local_sha_guarded_source_locator": local_locator,
        "vscode_original_source_navigation_safe": safe_original_navigation,
        "vscode_exposes_correction": "llmWiki.markCorrection" in commands,
        "vscode_exposes_change_semantics": "llmWiki.markChange" in commands,
        "vscode_exposes_dispute": "llmWiki.markDispute" in commands,
        "vscode_exposes_feedback": "llmWiki.feedback" in commands,
        "vscode_has_cross_topic_current_discovery": "llmWiki.discoverAcrossTopics" in commands and "['discover', query.trim(), '--json']" in extension,
        "backup_restore_guide_present": backup_story,
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
        topic_id = create_topic(wiki, "llm-wiki-lab self dogfood")["topic_id"]
        source_paths: dict[str, set[str]] = defaultdict(set)
        total_bytes = 0
        for path in files:
            source, _ = ingest_file(wiki, path, topic_id=topic_id)
            source_paths[source.source_id].add(path.relative_to(repo).as_posix())
            total_bytes += path.stat().st_size

        cases = []
        reciprocal_ranks: list[float] = []
        context_nonempty = 0
        for case in QUERY_CASES:
            hits = search(wiki, case["query"], top_k=5, topic_id=topic_id)
            first_rank = None
            hit_rows = []
            for rank, hit in enumerate(hits, 1):
                paths = sorted({value for sid in hit.source_ids for value in source_paths.get(sid, set())})
                if first_rank is None and any(expected in paths for expected in case["expected"]):
                    first_rank = rank
                hit_rows.append({
                    "rank": rank,
                    "score": hit.score,
                    "name": hit.source.name,
                    "source_ids": list(hit.source_ids),
                    "tracked_paths": paths,
                    "snippet": " ".join(hit.snippet.split())[:500],
                })
            context = render_context(wiki, case["query"], top_k=5, topic_id=topic_id)
            context_ok = bool(context.strip())
            context_nonempty += int(context_ok)
            rr = 0.0 if first_rank is None else 1.0 / first_rank
            reciprocal_ranks.append(rr)
            cases.append({**case, "pass_top5": first_rank is not None, "first_relevant_rank": first_rank, "reciprocal_rank": rr, "context_nonempty": context_ok, "hits": hit_rows})

        manifest_rows = history(wiki)
        collapsed_sources = {sid: sorted(paths) for sid, paths in source_paths.items() if len(paths) > 1}
        surface = inspect_product_surface(repo, basename_counts, collapsed_sources, manifest_rows)

    hit_count = sum(1 for row in cases if row["pass_top5"])
    hit_rate = hit_count / len(cases)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
    stage_a_pass = hit_rate >= 0.90 and mrr >= 0.60 and context_nonempty == len(cases)

    blockers: list[str] = []
    if not stage_a_pass:
        blockers.append("self_repo_retrieval_signal_below_preregistered_threshold")
    if surface["duplicate_basename_groups"] and not surface["vscode_original_source_navigation_safe"]:
        blockers.append("ambiguous_basename_only_original_source_navigation")
    if not (surface["vscode_exposes_correction"] and surface["vscode_exposes_change_semantics"] and surface["vscode_exposes_dispute"]):
        blockers.append("vscode_does_not_expose_full_temporal_trust_semantics")
    if not surface["vscode_exposes_feedback"]:
        blockers.append("vscode_customer_feedback_not_first_class")
    if not surface["vscode_has_cross_topic_current_discovery"]:
        blockers.append("forgotten_topic_recovery_has_no_first_class_vscode_path")
    if not surface["backup_restore_guide_present"]:
        blockers.append("valuable_local_wiki_backup_restore_story_missing")
    blockers.extend(["real_vscode_copilot_exact_luna_gate_pending", "repeated_customer_like_multisession_use_pending"])

    result = {
        "format": "E010-SELF-REPO-DOGFOOD-v1",
        "repo_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "model_calls": 0,
        "corpus": {"tracked_files": len(tracked_paths(repo)), "ingested_utf8_files": len(files), "ingested_bytes": total_bytes, "skipped_files": skipped},
        "retrieval": {"queries": len(cases), "top5_hits": hit_count, "top5_hit_rate": hit_rate, "mean_reciprocal_rank": mrr, "contexts_nonempty": context_nonempty, "stage_a_pass": stage_a_pass, "cases": cases},
        "product_surface": surface,
        "customer_readiness": {"customer_ready_candidate": False, "blockers": blockers, "note": "Real Copilot and repeated customer-like use are deliberately not inferable from CI."},
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# E010 self-repo dogfood result", "", f"Commit: `{result['repo_commit']}`", f"Model calls: **{result['model_calls']}**", "",
        "## Corpus", "", f"- tracked files: {result['corpus']['tracked_files']}", f"- ingested UTF-8 text files: {result['corpus']['ingested_utf8_files']}", f"- skipped binary/non-UTF8 files: {len(result['corpus']['skipped_files'])}", "",
        "## Retrieval", "", f"- top-5 target hit rate: **{hit_rate:.3f}** ({hit_count}/{len(cases)})", f"- mean reciprocal rank: **{mrr:.3f}**", f"- non-empty contexts: **{context_nonempty}/{len(cases)}**", f"- Stage A: **{'PASS' if stage_a_pass else 'FAIL'}**", "",
        "| case | pass | first rank |", "|---|---:|---:|",
    ]
    for row in cases:
        lines.append(f"| {row['id']} | {'yes' if row['pass_top5'] else 'no'} | {row['first_relevant_rank'] or '-'} |")
    lines.extend(["", "## Product blockers / pending gates", "", *[f"- {item}" for item in blockers], "", "This result is intentionally not a customer-readiness claim. See `README.md` in this experiment for the full gate."])
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
