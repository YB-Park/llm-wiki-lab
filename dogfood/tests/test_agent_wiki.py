from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki import agent_wiki
from dogfood.llm_wiki.adapters import Answer
from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.store import ensure_workspace, history, ingest_file, supersede_source


class AgentWikiTests(unittest.TestCase):
    def _wiki_with_source(self, text: str = "Agent Wiki should stay rebuildable and provenance linked."):
        temp = tempfile.TemporaryDirectory(prefix="agent-wiki-test-")
        base = Path(temp.name)
        root = base / "wiki"
        source_path = base / "source.md"
        source_path.write_text(text, encoding="utf-8")
        ensure_workspace(root)
        topic = create_topic(root, "agent note topic")
        source, _ = ingest_file(root, source_path, topic_id=topic["topic_id"])
        return temp, root, topic, source

    @staticmethod
    def _payload(source_id: str) -> dict:
        return {
            "title": "Agent Wiki source memory",
            "summary": f"Keep a provenance-linked derived memory for future use [{source_id}]",
            "operational_rules": [
                f"Maintain derived notes only inside granted scope [{source_id}]",
                f"Preserve provenance on every durable rule [{source_id}]",
                f"Treat human authorship as a separate permission [{source_id}]",
                f"Keep conflict semantics human-gated [{source_id}]",
                f"Use admitted evidence rather than prior generated answers [{source_id}]",
            ],
            "boundaries": [
                f"Agent Wiki is noncanonical and rebuildable [{source_id}]",
                f"Never turn generated notes into raw evidence [{source_id}]",
                f"Never infer and persist Human Knowledge automatically [{source_id}]",
            ],
            "open_questions": [f"When should this source note be refreshed? [{source_id}]"],
        }

    def test_build_publishes_derived_note_without_mutating_canonical_history_and_reuses_it(self):
        temp, root, topic, source = self._wiki_with_source()
        self.addCleanup(temp.cleanup)
        before = history(root)
        calls = []

        def fake_ask(prompt: str, model: str, max_ai_credits: int) -> Answer:
            calls.append((prompt, model, max_ai_credits))
            return Answer(text=json.dumps(self._payload(source.source_id)), model=model)

        original = agent_wiki.ask_copilot
        agent_wiki.ask_copilot = fake_ask
        self.addCleanup(setattr, agent_wiki, "ask_copilot", original)

        created = agent_wiki.build_agent_source_note(
            root,
            source.source_id,
            topic_id=topic["topic_id"],
            allow_model_call=True,
        )
        self.assertEqual(created["status"], "CREATED")
        self.assertEqual(created["model_calls"], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(history(root), before, "derived note publication must not touch canonical history")

        note_json = root / "agent-wiki" / "source-notes" / f"{source.source_id}.json"
        note_md = root / "agent-wiki" / "source-notes" / f"{source.source_id}.md"
        self.assertTrue(note_json.exists())
        self.assertTrue(note_md.exists())
        markdown = note_md.read_text(encoding="utf-8")
        self.assertIn("AGENT WIKI — NONCANONICAL / REBUILDABLE", markdown)
        self.assertIn(source.source_id, markdown)
        self.assertIn("never recover canonical state", markdown)

        def should_not_call(*_args, **_kwargs):
            raise AssertionError("existing current derived note must be reused with zero model calls")

        agent_wiki.ask_copilot = should_not_call
        reused = agent_wiki.build_agent_source_note(
            root,
            source.source_id,
            topic_id=topic["topic_id"],
            allow_model_call=True,
        )
        self.assertEqual(reused["status"], "REUSED")
        self.assertEqual(reused["model_calls"], 0)
        self.assertEqual(history(root), before)

        hits = agent_wiki.search_agent_notes(root, "rebuildable provenance", top_k=3)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].source_id, source.source_id)
        self.assertIn("noncanonical", hits[0].snippet.casefold())

    def test_superseded_source_note_is_not_returned_as_current_derived_memory(self):
        temp, root, topic, source = self._wiki_with_source("Old cobalt timeout was 15 seconds.")
        self.addCleanup(temp.cleanup)
        original = agent_wiki.ask_copilot
        agent_wiki.ask_copilot = lambda *_args, **kwargs: Answer(
            text=json.dumps(self._payload(source.source_id)),
            model=kwargs.get("model", "gpt-5.6-luna"),
        )
        self.addCleanup(setattr, agent_wiki, "ask_copilot", original)
        agent_wiki.build_agent_source_note(
            root,
            source.source_id,
            topic_id=topic["topic_id"],
            allow_model_call=True,
        )
        self.assertEqual(len(agent_wiki.search_agent_notes(root, "cobalt timeout", top_k=3)), 1)

        successor_path = Path(temp.name) / "successor.md"
        successor_path.write_text("Current cobalt timeout is 20 seconds.", encoding="utf-8")
        successor, _ = ingest_file(root, successor_path, topic_id=topic["topic_id"])
        supersede_source(root, source.source_id, successor.source_id, topic_id=topic["topic_id"])

        hits = agent_wiki.search_agent_notes(root, "cobalt timeout", top_k=3)
        self.assertEqual(hits, [], "a derived note for a superseded source must not surface as current Agent Wiki memory")
        self.assertIsNotNone(agent_wiki.read_agent_source_note(root, source.source_id), "derived history may remain inspectable even when no longer current")

    def test_maintenance_requires_explicit_model_authorization(self):
        temp, root, topic, source = self._wiki_with_source()
        self.addCleanup(temp.cleanup)
        with self.assertRaisesRegex(RuntimeError, "agent_wiki_model_call_not_authorized"):
            agent_wiki.build_agent_source_note(root, source.source_id, topic_id=topic["topic_id"])
        self.assertEqual(len(history(root)), 1)
        self.assertFalse((root / "agent-wiki").exists())

    def test_large_source_fails_before_model_call(self):
        temp, root, topic, source = self._wiki_with_source("x" * (agent_wiki.MAX_SOURCE_CHARS + 1))
        self.addCleanup(temp.cleanup)
        original = agent_wiki.ask_copilot
        agent_wiki.ask_copilot = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("model call must not happen"))
        self.addCleanup(setattr, agent_wiki, "ask_copilot", original)
        with self.assertRaisesRegex(RuntimeError, "agent_wiki_source_too_large"):
            agent_wiki.build_agent_source_note(
                root,
                source.source_id,
                topic_id=topic["topic_id"],
                allow_model_call=True,
            )
        self.assertFalse((root / "agent-wiki").exists())

    def test_invalid_model_citation_scope_fails_closed_without_publishing(self):
        temp, root, topic, source = self._wiki_with_source()
        self.addCleanup(temp.cleanup)
        payload = self._payload(source.source_id)
        payload["summary"] = "This summary has no canonical provenance handle."
        original = agent_wiki.ask_copilot
        agent_wiki.ask_copilot = lambda *_args, **_kwargs: Answer(text=json.dumps(payload), model="gpt-5.6-luna")
        self.addCleanup(setattr, agent_wiki, "ask_copilot", original)
        with self.assertRaisesRegex(RuntimeError, "agent_wiki_load_bearing_citation_missing"):
            agent_wiki.build_agent_source_note(
                root,
                source.source_id,
                topic_id=topic["topic_id"],
                allow_model_call=True,
            )
        self.assertFalse((root / "agent-wiki").exists())
        self.assertEqual(len(history(root)), 1)


if __name__ == "__main__":
    unittest.main()
