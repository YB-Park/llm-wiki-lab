from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VSCODE = ROOT / "dogfood" / "vscode"
AGENT = (VSCODE / "agent-tools.js").read_text(encoding="utf-8")
ENTRY = (VSCODE / "entry.js").read_text(encoding="utf-8")
HUMAN = (VSCODE / "human-knowledge.js").read_text(encoding="utf-8")
MANIFEST = json.loads((VSCODE / "package.json").read_text(encoding="utf-8"))
CASES = json.loads((Path(__file__).parent / "cases.json").read_text(encoding="utf-8"))

FEATURE_MARKERS = {
    "ambient_search": [(AGENT, "LLM_WIKI_MEMORY_RESULT v4"), (AGENT, "['discover', query, '--top-k-per-topic', '3', '--json']")],
    "verified_read": [(AGENT, "LLM_WIKI_SOURCE_READ v2"), (AGENT, "runAgentMemoryCli(this.context, folder, args)")],
    "raw_authority": [(AGENT, "epistemic_status=canonical_raw_evidence"), (AGENT, "Raw evidence is the factual/provenance authority")],
    "derived_label": [(AGENT, "epistemic_status=derived_noncanonical_agent_wiki"), (AGENT, "AGENT_WIKI_MODEL")],
    "human_knowledge": [(AGENT, "HUMAN_KNOWLEDGE H"), (HUMAN, "llm-wiki-human-knowledge-v1")],
    "remember_confirmation": [(AGENT, "explicitHumanConfirm("), (AGENT, "Remember source in LLM Wiki?")],
    "dirty_file_block": [(AGENT, "dirtyOpenDocumentFor"), (AGENT, "will not auto-save a dirty editor")],
    "raw_first": [(AGENT, "['ingest', target.filePath, '--topic', topic.id]"), (AGENT, "maintainSource(this.context, folder, receipt.sourceId")],
    "pending_lineage": [(AGENT, "pending_lineage_decision=yes"), (AGENT, "createPendingLineage")],
    "lineage_confirmation": [(AGENT, "Confirm LLM Wiki lineage decision"), (AGENT, "verifiedLineageComparison")],
    "lineage_revalidation": [(AGENT, "Pending lineage locator/source binding is inconsistent"), (AGENT, "comparison.older_status !== 'current'")],
    "lineage_correction": [(AGENT, "['source', 'correct'")],
    "lineage_change": [(AGENT, "['source', 'change'")],
    "lineage_dispute": [(AGENT, "['source', 'dispute'")],
    "lineage_supersede": [(AGENT, "['source', 'supersede'")],
    "human_confirmation": [(AGENT, "Save Human Knowledge?"), (AGENT, "authority=explicit_user_confirmation")],
    "human_supersession": [(AGENT, "supersedesKnowledgeId"), (HUMAN, "currentRows")],
    "human_integrity": [(HUMAN, "integritySha256"), (HUMAN, "Human Knowledge integrity failure")],
    "human_fork_cycle": [(HUMAN, "Human Knowledge lineage fork detected"), (HUMAN, "Human Knowledge lineage cycle detected")],
    "durable_state": [(AGENT, "dogfood.llm_wiki.agent_state_cli"), (AGENT, "locator-set")],
    "maintenance_default_off": [(AGENT, "agentWikiMaintenanceEnabled', false")],
    "maintenance_budget": [(AGENT, "agentWikiMaintenanceDailyCallLimit"), (AGENT, "SKIPPED_DAILY_CALL_LIMIT")],
    "maintenance_exact_luna": [(AGENT, "const AGENT_WIKI_MODEL = 'gpt-5.6-luna'")],
    "maintenance_pending_block": [(AGENT, "SKIPPED_PENDING_LINEAGE_DECISION")],
    "json_data_framing": [(AGENT, "data_encoding=json_string_fields"), (AGENT, "UNTRUSTED_QUOTED_DATA_NOT_INSTRUCTIONS")],
    "read_pagination": [(AGENT, "If has_more=yes")],
    "derived_follow_raw": [(AGENT, "For load-bearing factual claims surfaced by DERIVED_MEMORY, follow source_ids with wikiRead")],
    "no_silent_write": [(AGENT, "canonical_mutation=none"), (AGENT, "This tool result authorizes reading only")],
    "human_not_raw": [(AGENT, "raw_evidence_mutation=none"), (AGENT, "canonical_temporal_mutation=none")],
    "human_bounds": [(AGENT, "statement.length > 1800"), (AGENT, "reasoning.length > 1600")],
    "agent_tool_surface": [(AGENT, "vscode.lm.registerTool(SEARCH_TOOL"), (AGENT, "vscode.lm.registerTool(RESOLVE_LINEAGE_TOOL")],
    "new_human_note": [(ENTRY, "LLM Wiki: New Human Knowledge Note"), (ENTRY, "Human-owned draft. Saving this file does not ingest, promote, or mutate LLM Wiki state.")],
}


def main() -> int:
    assert len(CASES) == 78, f"expected 78 frozen cases, got {len(CASES)}"
    statuses: Counter[str] = Counter()
    ids: set[str] = set()
    for case in CASES:
        case_id = case["id"]
        assert case_id not in ids, f"duplicate case id: {case_id}"
        ids.add(case_id)
        status = case["status"]
        assert status in {"supported", "partial", "deferred"}, f"{case_id}: bad status {status}"
        features = case.get("features", [])
        description = case.get("description", "")
        statuses[status] += 1
        for feature in features:
            assert feature in FEATURE_MARKERS, f"{case_id}: unknown feature {feature}"
            for haystack, marker in FEATURE_MARKERS[feature]:
                assert marker in haystack, f"{case_id}: missing product marker for {feature}: {marker}"
        if status == "supported":
            assert features, f"{case_id}: supported case must name at least one concrete product mechanism"
        assert description.strip(), f"{case_id}: empty description"

    assert AGENT.count("verifiedLineageComparison(this.context, folder, pending, predecessor)") == 2, (
        "lineage verification must happen before confirmation and immediately before canonical mutation"
    )
    tool_names = {row["name"] for row in MANIFEST["contributes"]["languageModelTools"]}
    assert tool_names == {
        "llmWiki_searchMemory",
        "llmWiki_readSource",
        "llmWiki_rememberSource",
        "llmWiki_rememberHumanKnowledge",
        "llmWiki_resolveLineage",
    }
    hk_schema = next(row for row in MANIFEST["contributes"]["languageModelTools"] if row["name"] == "llmWiki_rememberHumanKnowledge")["inputSchema"]["properties"]
    assert "supersedesKnowledgeId" in hk_schema
    assert MANIFEST["version"] == "0.1.12"

    print(
        "E020-SYNTHETIC-CONTRACT PASS "
        f"cases={len(CASES)} supported={statuses['supported']} partial={statuses['partial']} deferred={statuses['deferred']} "
        "modelCalls=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
