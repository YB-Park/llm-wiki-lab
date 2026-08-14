from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.adapters import answer_prompt
from dogfood.llm_wiki.retrieval import render_context, search
from dogfood.llm_wiki.store import ingest_file
from dogfood.llm_wiki.temporal import dispute_sources


class E003TemporalAnswerBoundaryTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_dispute_annotation_is_post_retrieval_and_does_not_change_bm25(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            a, _ = ingest_file(
                root,
                self._write(base, "a.md", "project launch date april decision"),
                topic_id=topic,
                origin_id="origin-a",
            )
            b, _ = ingest_file(
                root,
                self._write(base, "b.md", "project launch date may decision"),
                topic_id=topic,
                origin_id="origin-b",
            )

            before = search(root, "project launch date decision", topic_id=topic, top_k=8)
            before_signature = [(hit.object_id, hit.score, hit.source_ids, hit.snippet) for hit in before]

            dispute_sources(root, a.source_id, b.source_id, topic_id=topic)

            after = search(root, "project launch date decision", topic_id=topic, top_k=8)
            after_signature = [(hit.object_id, hit.score, hit.source_ids, hit.snippet) for hit in after]
            self.assertEqual(after_signature, before_signature)

            context = render_context(root, "project launch date decision", topic_id=topic, top_k=8)
            self.assertEqual(context.count("epistemic_status: contested"), 2)
            self.assertIn(f"contested_source_ids: {a.source_id}", context)
            self.assertIn(f"contested_source_ids: {b.source_id}", context)
            self.assertIn(f"disputes_with: {b.source_id}", context)
            self.assertIn(f"disputes_with: {a.source_id}", context)
            self.assertEqual(context.count("temporal_membership: current"), 2)

    def test_unscoped_context_makes_no_temporal_or_consensus_claim(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic"
            a, _ = ingest_file(
                root,
                self._write(base, "a.md", "release threshold twelve"),
                topic_id=topic,
                origin_id="origin-a",
            )
            b, _ = ingest_file(
                root,
                self._write(base, "b.md", "release threshold thirteen"),
                topic_id=topic,
                origin_id="origin-b",
            )
            dispute_sources(root, a.source_id, b.source_id, topic_id=topic)

            context = render_context(root, "release threshold")
            self.assertNotIn("temporal_membership:", context)
            self.assertNotIn("epistemic_status:", context)
            self.assertNotIn("disputes_with:", context)

    def test_answer_prompt_forbids_manufactured_consensus_from_contested_evidence(self):
        prompt = answer_prompt(
            "What is the launch date?",
            "epistemic_status: contested\nsource_ids: src-a\ndisputes_with: src-b",
        )
        lowered = prompt.casefold()
        self.assertIn("unresolved disagreement", lowered)
        self.assertIn("do not manufacture consensus", lowered)
        self.assertIn("silently choose a winner", lowered)
        self.assertIn("cite the relevant source ids", lowered)
        self.assertIn("competing sides", lowered)


if __name__ == "__main__":
    unittest.main()
