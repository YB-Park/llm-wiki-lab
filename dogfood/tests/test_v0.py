from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.adapters import _final_message, answer_prompt
from dogfood.llm_wiki.calibration import create_topic
from dogfood.llm_wiki.cli import main as cli_main
from dogfood.llm_wiki.retrieval import render_context, search, tokenize
from dogfood.llm_wiki.store import (
    find_source,
    history,
    ingest_file,
    source_status,
    sources,
    supersede_source,
)


class DogfoodV0Tests(unittest.TestCase):
    def test_ingest_is_content_addressed_and_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "note.md"
            note.write_text("alpha decision\n", encoding="utf-8")

            first, duplicate1 = ingest_file(root, note)
            second, duplicate2 = ingest_file(root, note)

            self.assertFalse(duplicate1)
            self.assertTrue(duplicate2)
            self.assertEqual(first.source_id, second.source_id)
            self.assertEqual(len(list((root / "raw").iterdir())), 1)
            self.assertEqual(len(history(root)), 2)
            self.assertEqual(len(sources(root)), 1)

    def test_changed_bytes_create_new_source_and_keep_old(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "same-name.md"
            note.write_text("version one", encoding="utf-8")
            one, _ = ingest_file(root, note)
            note.write_text("version two", encoding="utf-8")
            two, _ = ingest_file(root, note)

            self.assertNotEqual(one.source_id, two.source_id)
            self.assertEqual(len(sources(root)), 2)
            self.assertEqual(len(list((root / "raw").iterdir())), 2)

    def test_explicit_supersession_separates_current_and_history_views(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-lineage"
            note = base / "decision.md"

            note.write_text("legacy cedar quota was 17 units", encoding="utf-8")
            old, _ = ingest_file(root, note, topic_id=topic)
            note.write_text("current cedar quota is 41 units", encoding="utf-8")
            new, _ = ingest_file(root, note, topic_id=topic, supersedes_source_id=old.source_id)

            current_ids = [src.source_id for src in sources(root, topic_id=topic)]
            historical_ids = [src.source_id for src in sources(root, topic_id=topic, include_superseded=True)]
            self.assertEqual(current_ids, [new.source_id])
            self.assertEqual(set(historical_ids), {old.source_id, new.source_id})
            self.assertEqual(len(list((root / "raw").iterdir())), 2)

            self.assertEqual(search(root, "legacy", topic_id=topic), [])
            historical_hits = search(root, "legacy", topic_id=topic, include_superseded=True)
            self.assertEqual(historical_hits[0].source.source_id, old.source_id)

            resolved_old = find_source(root, old.source_id, topic_id=topic)
            self.assertEqual(resolved_old.source_id, old.source_id)
            self.assertEqual(
                source_status(root, old.source_id, topic_id=topic),
                {"source_id": old.source_id, "status": "superseded", "superseded_by": new.source_id},
            )
            self.assertEqual(source_status(root, new.source_id, topic_id=topic)["status"], "current")

    def test_supersession_chain_keeps_only_latest_current(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-chain"
            note = base / "state.md"

            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id=topic)
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(root, note, topic_id=topic, supersedes_source_id=a.source_id)
            note.write_text("state gamma", encoding="utf-8")
            c, _ = ingest_file(root, note, topic_id=topic, supersedes_source_id=b.source_id)

            self.assertEqual([src.source_id for src in sources(root, topic_id=topic)], [c.source_id])
            self.assertEqual(
                set(src.source_id for src in sources(root, topic_id=topic, include_superseded=True)),
                {a.source_id, b.source_id, c.source_id},
            )
            self.assertEqual(len(list((root / "raw").iterdir())), 3)
            self.assertEqual(sum(1 for row in history(root) if row.get("event") == "supersede"), 2)

    def test_supersession_rejects_self_conflict_cycle_and_stale_successor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-guards"
            files = []
            sources_by_name = {}
            for name in ("a", "b", "c"):
                p = base / f"{name}.md"
                p.write_text(f"value {name}", encoding="utf-8")
                files.append(p)
                sources_by_name[name], _ = ingest_file(root, p, topic_id=topic)

            a = sources_by_name["a"]
            b = sources_by_name["b"]
            c = sources_by_name["c"]

            with self.assertRaises(ValueError):
                supersede_source(root, a.source_id, a.source_id, topic_id=topic)

            self.assertTrue(supersede_source(root, a.source_id, b.source_id, topic_id=topic))
            self.assertFalse(supersede_source(root, a.source_id, b.source_id, topic_id=topic))

            with self.assertRaises(ValueError):
                supersede_source(root, a.source_id, c.source_id, topic_id=topic)
            with self.assertRaises(ValueError):
                supersede_source(root, b.source_id, a.source_id, topic_id=topic)
            with self.assertRaises(ValueError):
                supersede_source(root, c.source_id, a.source_id, topic_id=topic)

            relations = [row for row in history(root) if row.get("event") == "supersede"]
            self.assertEqual(len(relations), 1)
            self.assertEqual(relations[0]["predecessor_source_id"], a.source_id)
            self.assertEqual(relations[0]["successor_source_id"], b.source_id)

    def test_topic_scoped_supersession_does_not_hide_other_topic_or_unscoped_view(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            old_file = base / "old.md"
            new_file = base / "new.md"
            old_file.write_text("legacy shared evidence", encoding="utf-8")
            new_file.write_text("current shared evidence", encoding="utf-8")

            old_a, _ = ingest_file(root, old_file, topic_id="topic-a")
            new_a, _ = ingest_file(root, new_file, topic_id="topic-a")
            old_b, _ = ingest_file(root, old_file, topic_id="topic-b")
            new_b, _ = ingest_file(root, new_file, topic_id="topic-b")
            self.assertEqual(old_a.source_id, old_b.source_id)
            self.assertEqual(new_a.source_id, new_b.source_id)

            supersede_source(root, old_a.source_id, new_a.source_id, topic_id="topic-a")

            self.assertEqual([src.source_id for src in sources(root, topic_id="topic-a")], [new_a.source_id])
            self.assertEqual(
                set(src.source_id for src in sources(root, topic_id="topic-b")),
                {old_b.source_id, new_b.source_id},
            )
            self.assertEqual(
                set(src.source_id for src in sources(root)),
                {old_a.source_id, new_a.source_id},
            )

    def test_authoritative_update_is_not_implicit_supersession(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = create_topic(root, "Update semantics")
            note = base / "state.md"
            note.write_text("old state", encoding="utf-8")
            cli_main(["--root", str(root), "ingest", str(note), "--topic", topic["topic_id"]])
            note.write_text("new state", encoding="utf-8")
            cli_main([
                "--root", str(root), "ingest", str(note), "--topic", topic["topic_id"], "--authoritative-update"
            ])

            self.assertEqual(len(sources(root, topic_id=topic["topic_id"])), 2)
            self.assertEqual(sum(1 for row in history(root) if row.get("event") == "supersede"), 0)

    def test_cli_ingest_can_explicitly_supersede_with_independent_update_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = create_topic(root, "Explicit lineage")
            note = base / "state.md"
            note.write_text("first state", encoding="utf-8")
            cli_main(["--root", str(root), "ingest", str(note), "--topic", topic["topic_id"]])
            old = sources(root, topic_id=topic["topic_id"])[0]

            note.write_text("second state", encoding="utf-8")
            cli_main([
                "--root", str(root),
                "ingest", str(note),
                "--topic", topic["topic_id"],
                "--authoritative-update",
                "--supersedes", old.source_id,
            ])

            current = sources(root, topic_id=topic["topic_id"])
            self.assertEqual(len(current), 1)
            self.assertNotEqual(current[0].source_id, old.source_id)
            self.assertEqual(source_status(root, old.source_id, topic_id=topic["topic_id"])["status"], "superseded")

    def test_bm25_is_deterministic_and_relevant(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            a = base / "a.md"
            b = base / "b.md"
            a.write_text("cache cache cache decision uses amber window", encoding="utf-8")
            b.write_text("meeting calendar housekeeping", encoding="utf-8")
            sa, _ = ingest_file(root, a)
            ingest_file(root, b)

            first = search(root, "cache decision", top_k=2)
            second = search(root, "cache decision", top_k=2)
            self.assertEqual([h.source.source_id for h in first], [h.source.source_id for h in second])
            self.assertEqual(first[0].source.source_id, sa.source_id)
            self.assertGreater(first[0].score, 0)

    def test_context_preserves_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "decision.md"
            note.write_text("We chose Pine index because of the cedar quota.", encoding="utf-8")
            src, _ = ingest_file(root, note)
            ctx = render_context(root, "Pine cedar", top_k=1)
            self.assertIn(src.source_id, ctx)
            self.assertIn(src.sha256, ctx)
            self.assertIn("Pine index", ctx)

    def test_korean_tokenization(self):
        self.assertEqual(tokenize("검색 기록과 결정"), ["검색", "기록과", "결정"])

    def test_workspace_config_keeps_compiled_disabled(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "x.md"
            note.write_text("x", encoding="utf-8")
            ingest_file(root, note)
            config = json.loads((root / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["compiled_provider"], "disabled")

    def test_copilot_jsonl_extracts_only_final_answer(self):
        stdout = "\n".join([
            json.dumps({"type": "assistant.message", "data": {"phase": "analysis", "content": "ignore"}}),
            json.dumps({"type": "assistant.message", "data": {"phase": "final_answer", "content": "Answer [src-abc]", "model": "gpt-5.6-luna", "toolRequests": []}}),
        ])
        answer = _final_message(stdout)
        self.assertEqual(answer.text, "Answer [src-abc]")
        self.assertEqual(answer.model, "gpt-5.6-luna")

    def test_answer_prompt_is_read_only_and_evidence_bound(self):
        prompt = answer_prompt("Why?", "### SOURCE src-abc\nEvidence")
        self.assertIn("using only the evidence", prompt)
        self.assertIn("src-abc", prompt)
        self.assertIn("Do not claim to update", prompt)

    def test_ask_requires_explicit_model_opt_in_before_any_adapter_call(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "x.md"
            note.write_text("cache decision", encoding="utf-8")
            ingest_file(root, note)
            with self.assertRaises(SystemExit) as cm:
                cli_main(["--root", str(root), "ask", "cache"])
            self.assertIn("model_call_not_authorized", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
