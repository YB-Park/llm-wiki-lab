from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki import agent_wiki, agent_wiki_cli
from dogfood.llm_wiki.adapters import Answer
from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.store import ensure_workspace, ingest_file


class AgentWikiSourceSizeTests(unittest.TestCase):
    @staticmethod
    def _payload(source_id: str) -> dict:
        return {
            "title": "Oversize source note",
            "summary": f"This admitted source remains usable for derived maintenance [{source_id}]",
            "operational_rules": [
                f"Preserve raw provenance while deriving navigation aids [{source_id}]",
                f"Keep generated notes noncanonical and rebuildable [{source_id}]",
                f"Do not infer Human Knowledge from the source note [{source_id}]",
                f"Keep lineage decisions behind explicit human confirmation [{source_id}]",
                f"Use only the admitted source as evidence for this note [{source_id}]",
            ],
            "boundaries": [
                f"This note is not raw evidence [{source_id}]",
                f"This note cannot resolve temporal lineage [{source_id}]",
                f"This note does not authorize new user beliefs [{source_id}]",
            ],
            "open_questions": [],
        }

    def _wiki_with_source(self, chars: int):
        temp = tempfile.TemporaryDirectory(prefix="agent-wiki-size-test-")
        base = Path(temp.name)
        root = base / "wiki"
        source_path = base / "source.md"
        source_path.write_text("x" * chars, encoding="utf-8")
        ensure_workspace(root)
        topic = create_topic(root, "source size topic")
        source, _ = ingest_file(root, source_path, topic_id=topic["topic_id"])
        return temp, root, topic, source

    def test_source_size_policy_has_preferred_target_and_higher_hard_ceiling(self):
        self.assertEqual(agent_wiki.PREFERRED_SOURCE_CHARS, 40_000)
        self.assertEqual(agent_wiki.MAX_SOURCE_CHARS, 80_000)
        self.assertGreater(agent_wiki.MAX_SOURCE_CHARS, agent_wiki.PREFERRED_SOURCE_CHARS)

    def test_source_just_over_old_40k_cliff_runs_one_single_pass(self):
        chars = agent_wiki.PREFERRED_SOURCE_CHARS + 491
        temp, root, topic, source = self._wiki_with_source(chars)
        self.addCleanup(temp.cleanup)
        calls = []

        def fake_ask(_prompt: str, model: str, max_ai_credits: int) -> Answer:
            calls.append(model)
            return Answer(text=json.dumps(self._payload(source.source_id)), model=model)

        original = agent_wiki.ask_copilot
        agent_wiki.ask_copilot = fake_ask
        self.addCleanup(setattr, agent_wiki, "ask_copilot", original)

        result = agent_wiki.build_agent_source_note(
            root,
            source.source_id,
            topic_id=topic["topic_id"],
            allow_model_call=True,
        )
        self.assertEqual(result["status"], "CREATED")
        self.assertEqual(result["model_calls"], 1)
        self.assertEqual(result["source_chars"], chars)
        self.assertEqual(result["source_size_mode"], "oversize_single_pass")
        self.assertEqual(calls, [agent_wiki.DEFAULT_MODEL])

        status = agent_wiki_cli._status_text({"status": result["status"], **result})
        self.assertIn("CREATED;source_size_mode=oversize_single_pass", status)
        self.assertIn(f"source_chars={chars}", status)
        self.assertIn("source_preferred_chars=40000", status)
        self.assertIn("source_hard_ceiling_chars=80000", status)

    def test_over_ceiling_failure_is_causal_and_explicitly_not_soft_guard(self):
        failure = agent_wiki_cli._safe_build_failure(
            RuntimeError("agent_wiki_source_too_large:80001>80000")
        )
        self.assertIsNotNone(failure)
        self.assertEqual(failure["status"], "SKIPPED_SOURCE_TOO_LARGE")
        self.assertEqual(failure["failure_code"], "SOURCE_TOO_LARGE")
        self.assertEqual(failure["maintenance_stage"], "preflight")
        self.assertEqual(failure["model_call_attempted"], "no")
        self.assertEqual(failure["source_chars"], 80001)
        self.assertEqual(failure["source_preferred_chars"], 40000)
        self.assertEqual(failure["source_hard_ceiling_chars"], 80000)

        status = agent_wiki_cli._status_text(failure)
        self.assertIn("SKIPPED_SOURCE_TOO_LARGE", status)
        self.assertIn("failure_code=SOURCE_TOO_LARGE", status)
        self.assertIn("stage=preflight", status)
        self.assertIn("model_call_attempted=no", status)
        self.assertIn("source_chars=80001", status)
        self.assertIn("source_preferred_chars=40000", status)
        self.assertIn("source_hard_ceiling_chars=80000", status)
        self.assertIn("soft_guard_prompted=no", status)


if __name__ == "__main__":
    unittest.main()
