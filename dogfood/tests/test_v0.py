from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.adapters import _final_message, answer_prompt
from dogfood.llm_wiki.cli import main as cli_main
from dogfood.llm_wiki.retrieval import render_context, search, tokenize
from dogfood.llm_wiki.store import history, ingest_file, sources


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
