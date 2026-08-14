from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.adapters import answer_prompt
from dogfood.llm_wiki.store import history, ingest_file, source_status, sources


class EvidenceIdentityV2EdgeTests(unittest.TestCase):
    def test_late_known_lineage_reuses_existing_current_successor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-late-lineage"
            note = base / "state.md"

            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id=topic, origin_id="origin-a")
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(root, note, topic_id=topic, origin_id="origin-a")
            self.assertEqual(
                set(src.source_id for src in sources(root, topic_id=topic)),
                {a.source_id, b.source_id},
            )

            linked, duplicate = ingest_file(
                root,
                note,
                topic_id=topic,
                origin_id="origin-a",
                supersedes_source_id=a.source_id,
            )

            self.assertTrue(duplicate)
            self.assertEqual(linked.source_id, b.source_id)
            self.assertEqual([src.source_id for src in sources(root, topic_id=topic)], [b.source_id])
            self.assertEqual(source_status(root, a.source_id, topic_id=topic)["superseded_by"], b.source_id)
            self.assertEqual(sum(1 for row in history(root) if row.get("event") == "supersede"), 1)
            self.assertEqual(
                len({row["source_id"] for row in history(root) if row.get("event") == "ingest"}),
                2,
                "late lineage declaration must not invent a third source revision",
            )

    def test_answer_prompt_forbids_treating_same_object_source_multiplicity_as_corroboration(self):
        prompt = answer_prompt(
            "What is the quota?",
            "### EVIDENCE OBJECT obj-x\nsource_ids: src-a, src-b\nquota=41",
        )
        self.assertIn("identical bytes", prompt)
        self.assertIn("do not count that multiplicity as independent corroboration", prompt)


if __name__ == "__main__":
    unittest.main()
