from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .agent_wiki import AGENT_WIKI_POLICY, MAX_SOURCE_CHARS, PREFERRED_SOURCE_CHARS, build_agent_source_note, read_agent_source_note, search_agent_notes
from .calibration import resolve_topic


def _root(value: str) -> Path:
    return Path(value).expanduser()


def _safe_build_failure(error: RuntimeError) -> dict | None:
    detail = str(error)
    too_large = re.fullmatch(r"agent_wiki_source_too_large:(\d+)>(\d+)", detail)
    if too_large:
        source_chars = int(too_large.group(1))
        ceiling = int(too_large.group(2))
        return {
            "status": "SKIPPED_SOURCE_TOO_LARGE",
            "model_calls": 0,
            "failure_code": "SOURCE_TOO_LARGE",
            "maintenance_stage": "preflight",
            "model_call_attempted": "no",
            "source_chars": source_chars,
            "source_preferred_chars": PREFERRED_SOURCE_CHARS,
            "source_hard_ceiling_chars": ceiling,
            "source_size_mode": "too_large",
        }

    exact = {
        "copilot_cli_argument_error": ("FAILED_COPILOT_CLI_ARGUMENT", 0, "COPILOT_CLI_ARGUMENT", "model_call_setup", "no"),
        "copilot_auth_failed": ("FAILED_COPILOT_AUTH", 0, "COPILOT_AUTH", "model_call_setup", "no"),
        "copilot_model_unavailable": ("FAILED_COPILOT_MODEL_UNAVAILABLE", 0, "COPILOT_MODEL_UNAVAILABLE", "model_call_setup", "no"),
        "copilot_cli_not_found": ("FAILED_COPILOT_CLI_NOT_FOUND", 0, "COPILOT_CLI_NOT_FOUND", "model_call_setup", "no"),
        "copilot_jsonl_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "copilot_tool_request_present": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "copilot_source_citation_missing": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_json_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_payload_shape_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_title_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_summary_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_rules_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_boundaries_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_questions_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_load_bearing_citation_missing": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_citation_scope_invalid": ("FAILED_COPILOT_OUTPUT_CONTRACT", 1, "COPILOT_OUTPUT_CONTRACT", "model_output", "yes"),
        "agent_wiki_source_not_current": ("FAILED_SOURCE_NOT_CURRENT", 0, "SOURCE_NOT_CURRENT", "preflight", "no"),
        "agent_wiki_source_changed_during_generation": ("FAILED_SOURCE_CHANGED_DURING_GENERATION", 1, "SOURCE_CHANGED_DURING_GENERATION", "publish", "yes"),
    }
    if detail in exact:
        status, model_calls, failure_code, stage, attempted = exact[detail]
        return {"status": status, "model_calls": model_calls, "failure_code": failure_code, "maintenance_stage": stage, "model_call_attempted": attempted}
    if detail.startswith("copilot_call_failed:"):
        return {"status": "FAILED_COPILOT_CALL", "model_calls": 0, "failure_code": "COPILOT_CALL", "maintenance_stage": "model_call", "model_call_attempted": "unknown"}
    if detail.startswith("copilot_final_message_count:"):
        return {"status": "FAILED_COPILOT_OUTPUT_CONTRACT", "model_calls": 1, "failure_code": "COPILOT_OUTPUT_CONTRACT", "maintenance_stage": "model_output", "model_call_attempted": "yes"}
    if detail.startswith("copilot_model_mismatch:"):
        return {"status": "FAILED_COPILOT_MODEL_MISMATCH", "model_calls": 1, "failure_code": "COPILOT_MODEL_MISMATCH", "maintenance_stage": "model_output", "model_call_attempted": "yes"}
    if detail.startswith("copilot_raw_source_citation_forbidden:") or detail.startswith("copilot_unknown_citation_handle:"):
        return {"status": "FAILED_COPILOT_OUTPUT_CONTRACT", "model_calls": 1, "failure_code": "COPILOT_OUTPUT_CONTRACT", "maintenance_stage": "model_output", "model_call_attempted": "yes"}
    return None


def _status_text(row: dict) -> str:
    status = str(row.get("status", "UNKNOWN"))
    if status == "SKIPPED_SOURCE_TOO_LARGE":
        return (
            f"{status};failure_code=SOURCE_TOO_LARGE;stage=preflight;model_call_attempted=no"
            f";source_chars={int(row.get('source_chars', 0))}"
            f";source_preferred_chars={int(row.get('source_preferred_chars', PREFERRED_SOURCE_CHARS))}"
            f";source_hard_ceiling_chars={int(row.get('source_hard_ceiling_chars', MAX_SOURCE_CHARS))}"
            ";soft_guard_prompted=no"
        )
    if row.get("source_size_mode") == "oversize_single_pass":
        return (
            f"{status};source_size_mode=oversize_single_pass"
            f";source_chars={int(row.get('source_chars', 0))}"
            f";source_preferred_chars={int(row.get('source_preferred_chars', PREFERRED_SOURCE_CHARS))}"
            f";source_hard_ceiling_chars={int(row.get('source_hard_ceiling_chars', MAX_SOURCE_CHARS))}"
        )
    return status


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki-agent-wiki")
    p.add_argument("--root", default=".wiki-lab")
    sub = p.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("source_id")
    build.add_argument("--topic", required=True)
    build.add_argument("--model", default="gpt-5.6-luna")
    build.add_argument("--max-ai-credits", type=int, default=30)
    build.add_argument("--allow-model-call", action="store_true")

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=3)
    search.add_argument("--json", action="store_true")

    show = sub.add_parser("show")
    show.add_argument("source_id")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = _root(args.root)

    if args.command == "build":
        topic_id = resolve_topic(root, args.topic)["topic_id"]
        try:
            result = build_agent_source_note(
                root,
                args.source_id,
                topic_id=topic_id,
                model=args.model,
                max_ai_credits=args.max_ai_credits,
                allow_model_call=args.allow_model_call,
            )
        except RuntimeError as error:
            failure = _safe_build_failure(error)
            if failure is None:
                raise
            print(
                json.dumps(
                    {
                        **failure,
                        "status": _status_text(failure),
                        "source_id": args.source_id,
                        "topic_id": topic_id,
                        "model": args.model,
                        "policy": AGENT_WIKI_POLICY,
                        "markdown_path": "",
                        "source_preferred_chars": failure.get("source_preferred_chars", PREFERRED_SOURCE_CHARS),
                        "source_hard_ceiling_chars": failure.get("source_hard_ceiling_chars", MAX_SOURCE_CHARS),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        record = result["record"]
        print(
            json.dumps(
                {
                    "status": _status_text({"status": result["status"], **result}),
                    "model_calls": result["model_calls"],
                    "source_id": record["source_id"],
                    "topic_id": record["topic_id"],
                    "model": record["model"],
                    "policy": record["policy"],
                    "markdown_path": result["markdown_path"],
                    "failure_code": "",
                    "maintenance_stage": "reuse" if result["status"] == "REUSED" else "completed",
                    "model_call_attempted": "no" if result["status"] == "REUSED" else "yes",
                    "source_chars": result.get("source_chars", 0),
                    "source_preferred_chars": result.get("source_preferred_chars", PREFERRED_SOURCE_CHARS),
                    "source_hard_ceiling_chars": result.get("source_hard_ceiling_chars", MAX_SOURCE_CHARS),
                    "source_size_mode": result.get("source_size_mode", "reused" if result["status"] == "REUSED" else "preferred"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "search":
        hits = search_agent_notes(root, args.query, top_k=args.top_k)
        for hit in hits:
            row = {
                "source_id": hit.source_id,
                "topic_id": hit.topic_id,
                "title": hit.title,
                "score": hit.score,
                "snippet": hit.snippet,
                "markdown_path": str(hit.markdown_path),
                "epistemic_status": "derived_noncanonical_agent_wiki",
            }
            if args.json:
                print(json.dumps(row, ensure_ascii=False, sort_keys=True))
            else:
                print(f"{hit.source_id} score={hit.score:.6f} title={json.dumps(hit.title, ensure_ascii=False)}")
        return 0

    if args.command == "show":
        record = read_agent_source_note(root, args.source_id)
        if record is None:
            raise SystemExit(f"AGENT-WIKI-STOP note_not_found:{args.source_id}")
        markdown = root / "agent-wiki" / "source-notes" / f"{args.source_id}.md"
        if not markdown.exists():
            raise SystemExit(f"AGENT-WIKI-STOP markdown_missing:{args.source_id}")
        print(markdown.read_text(encoding="utf-8"), end="")
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
