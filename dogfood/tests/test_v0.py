from __future__ import annotations

import hashlib
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
    def test_ingest_is_content_addressed_and_same_anonymous_current_source_is_idempotent(self):
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
            self.assertEqual(first.object_id, second.object_id)
            self.assertTrue(first.source_id.startswith("src-"))
            self.assertFalse(first.source_id.startswith(f"src-{first.sha256[:16]}"))
            self.assertEqual(len(list((root / "raw").iterdir())), 1)
            self.assertEqual(len(history(root)), 2)
            self.assertEqual(len(sources(root)), 1)

    def test_same_origin_same_current_object_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "note.md"
            note.write_text("stable evidence", encoding="utf-8")

            first, _ = ingest_file(root, note, topic_id="topic", origin_id="origin-alpha")
            second, duplicate = ingest_file(root, note, topic_id="topic", origin_id="origin-alpha")

            self.assertTrue(duplicate)
            self.assertEqual(first.source_id, second.source_id)
            self.assertEqual(first.object_id, second.object_id)
            self.assertEqual(len(sources(root, topic_id="topic")), 1)

    def test_different_origins_same_bytes_create_two_sources_one_object(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "shared.md"
            note.write_text("shared cedar evidence", encoding="utf-8")

            a, duplicate_a = ingest_file(root, note, topic_id="topic", origin_id="origin-a")
            b, duplicate_b = ingest_file(root, note, topic_id="topic", origin_id="origin-b")

            self.assertFalse(duplicate_a)
            self.assertTrue(duplicate_b)
            self.assertNotEqual(a.source_id, b.source_id)
            self.assertEqual(a.object_id, b.object_id)
            self.assertEqual(a.sha256, b.sha256)
            self.assertEqual(len(list((root / "raw").iterdir())), 1)
            self.assertEqual(len(sources(root, topic_id="topic")), 2)

            hits = search(root, "cedar", topic_id="topic", top_k=8)
            self.assertEqual(len(hits), 1, "identical bytes must rank as one lexical object")
            self.assertEqual(set(hits[0].source_ids), {a.source_id, b.source_id})
            self.assertEqual(hits[0].object_id, a.object_id)

    def test_origin_id_must_be_opaque_token_not_path(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            note = base / "note.md"
            note.write_text("evidence", encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                ingest_file(base / "wiki", note, topic_id="topic", origin_id="/Users/alice/private/file.md")
            self.assertIn("origin_id_must_be_opaque_ascii_token", str(cm.exception))

    def test_same_origin_changed_bytes_without_supersession_preserves_ambiguity(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "state.md"
            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id="topic", origin_id="origin-a")
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(root, note, topic_id="topic", origin_id="origin-a")

            self.assertNotEqual(a.source_id, b.source_id)
            self.assertNotEqual(a.object_id, b.object_id)
            self.assertEqual(
                set(src.source_id for src in sources(root, topic_id="topic")),
                {a.source_id, b.source_id},
            )
            self.assertEqual(sum(1 for row in history(root) if row.get("event") == "supersede"), 0)

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
            self.assertNotEqual(one.object_id, two.object_id)
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
            self.assertIn(old.source_id, historical_hits[0].source_ids)

            resolved_old = find_source(root, old.source_id, topic_id=topic)
            self.assertEqual(resolved_old.source_id, old.source_id)
            self.assertEqual(
                source_status(root, old.source_id, topic_id=topic),
                {
                    "source_id": old.source_id,
                    "object_id": old.object_id,
                    "status": "superseded",
                    "superseded_by": new.source_id,
                },
            )
            self.assertEqual(source_status(root, new.source_id, topic_id=topic)["status"], "current")

    def test_plain_reingest_of_stale_anonymous_identity_requires_explicit_supersession(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-no-implicit-reactivation"
            old_file = base / "old.md"
            new_file = base / "new.md"
            old_file.write_text("state alpha", encoding="utf-8")
            new_file.write_text("state beta", encoding="utf-8")

            old, _ = ingest_file(root, old_file, topic_id=topic)
            new, _ = ingest_file(root, new_file, topic_id=topic, supersedes_source_id=old.source_id)

            with self.assertRaises(ValueError) as cm:
                ingest_file(root, old_file, topic_id=topic)
            self.assertIn("stale_source_requires_supersedes", str(cm.exception))
            self.assertEqual([src.source_id for src in sources(root, topic_id=topic)], [new.source_id])
            self.assertEqual(source_status(root, old.source_id, topic_id=topic)["status"], "superseded")

    def test_plain_reingest_of_stale_same_origin_requires_explicit_supersession(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-origin-stale"
            note = base / "state.md"
            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id=topic, origin_id="origin-a")
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(
                root,
                note,
                topic_id=topic,
                origin_id="origin-a",
                supersedes_source_id=a.source_id,
            )
            note.write_text("state alpha", encoding="utf-8")
            with self.assertRaises(ValueError):
                ingest_file(root, note, topic_id=topic, origin_id="origin-a")
            self.assertEqual([src.source_id for src in sources(root, topic_id=topic)], [b.source_id])

    def test_explicit_reversion_creates_new_source_revision_but_reuses_raw_object(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-revert"
            note = base / "state.md"

            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id=topic, origin_id="origin-a")
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(
                root,
                note,
                topic_id=topic,
                origin_id="origin-a",
                supersedes_source_id=a.source_id,
            )

            note.write_text("state alpha", encoding="utf-8")
            reverted, duplicate = ingest_file(
                root,
                note,
                topic_id=topic,
                origin_id="origin-a",
                supersedes_source_id=b.source_id,
            )

            self.assertTrue(duplicate)
            self.assertNotEqual(reverted.source_id, a.source_id)
            self.assertNotEqual(reverted.source_id, b.source_id)
            self.assertEqual(reverted.object_id, a.object_id)
            self.assertEqual(reverted.sha256, a.sha256)
            self.assertEqual([src.source_id for src in sources(root, topic_id=topic)], [reverted.source_id])
            self.assertEqual(source_status(root, a.source_id, topic_id=topic)["superseded_by"], b.source_id)
            self.assertEqual(source_status(root, b.source_id, topic_id=topic)["superseded_by"], reverted.source_id)
            self.assertEqual(source_status(root, reverted.source_id, topic_id=topic)["status"], "current")
            self.assertEqual(len(list((root / "raw").iterdir())), 2)

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

    def test_supersession_rejects_self_conflict_and_inactive_successor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-guards"
            sources_by_name = {}
            for name in ("a", "b", "c"):
                p = base / f"{name}.md"
                p.write_text(f"value {name}", encoding="utf-8")
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

    def test_retry_of_completed_ingest_supersession_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-retry"
            note = base / "state.md"
            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id=topic, origin_id="origin-a")
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(
                root,
                note,
                topic_id=topic,
                origin_id="origin-a",
                supersedes_source_id=a.source_id,
            )
            retry, duplicate = ingest_file(
                root,
                note,
                topic_id=topic,
                origin_id="origin-a",
                supersedes_source_id=a.source_id,
            )
            self.assertTrue(duplicate)
            self.assertEqual(retry.source_id, b.source_id)
            self.assertEqual(sum(1 for row in history(root) if row.get("event") == "supersede"), 1)

    def test_stale_old_relation_cannot_reactivate_superseded_successor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-stale-idempotence"
            note = base / "state.md"

            note.write_text("state alpha", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id=topic)
            note.write_text("state beta", encoding="utf-8")
            b, _ = ingest_file(root, note, topic_id=topic, supersedes_source_id=a.source_id)
            note.write_text("state gamma", encoding="utf-8")
            c, _ = ingest_file(root, note, topic_id=topic, supersedes_source_id=b.source_id)

            note.write_text("state beta", encoding="utf-8")
            with self.assertRaises(ValueError):
                ingest_file(root, note, topic_id=topic, supersedes_source_id=a.source_id)

            self.assertEqual([src.source_id for src in sources(root, topic_id=topic)], [c.source_id])
            self.assertEqual(source_status(root, b.source_id, topic_id=topic)["status"], "superseded")

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
            self.assertNotEqual(old_a.source_id, old_b.source_id)
            self.assertNotEqual(new_a.source_id, new_b.source_id)
            self.assertEqual(old_a.object_id, old_b.object_id)
            self.assertEqual(new_a.object_id, new_b.object_id)

            supersede_source(root, old_a.source_id, new_a.source_id, topic_id="topic-a")

            self.assertEqual([src.source_id for src in sources(root, topic_id="topic-a")], [new_a.source_id])
            self.assertEqual(
                set(src.source_id for src in sources(root, topic_id="topic-b")),
                {old_b.source_id, new_b.source_id},
            )
            self.assertEqual(len(sources(root)), 4)
            self.assertEqual(len(search(root, "shared", top_k=8)), 2, "unscoped retrieval ranks two unique objects, not four evidence records")

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
            self.assertEqual([h.object_id for h in first], [h.object_id for h in second])
            self.assertEqual(first[0].source.source_id, sa.source_id)
            self.assertGreater(first[0].score, 0)

    def test_duplicate_provenance_does_not_change_bm25_score(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            solo_root = base / "solo"
            multi_root = base / "multi"
            note = base / "evidence.md"
            distractor = base / "noise.md"
            note.write_text("cedar quota cache decision", encoding="utf-8")
            distractor.write_text("calendar housekeeping", encoding="utf-8")

            ingest_file(solo_root, note, topic_id="topic", origin_id="origin-a")
            ingest_file(solo_root, distractor, topic_id="topic", origin_id="noise-a")
            solo = search(solo_root, "cedar quota", topic_id="topic")[0]

            ingest_file(multi_root, note, topic_id="topic", origin_id="origin-a")
            ingest_file(multi_root, note, topic_id="topic", origin_id="origin-b")
            ingest_file(multi_root, distractor, topic_id="topic", origin_id="noise-a")
            multi = search(multi_root, "cedar quota", topic_id="topic")[0]

            self.assertAlmostEqual(solo.score, multi.score, places=12)
            self.assertEqual(len(solo.source_ids), 1)
            self.assertEqual(len(multi.source_ids), 2)

    def test_context_preserves_object_and_all_provenance_source_ids(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            note = base / "decision.md"
            note.write_text("We chose Pine index because of the cedar quota.", encoding="utf-8")
            a, _ = ingest_file(root, note, topic_id="topic", origin_id="origin-a")
            b, _ = ingest_file(root, note, topic_id="topic", origin_id="origin-b")
            ctx = render_context(root, "Pine cedar", top_k=1, topic_id="topic")
            self.assertIn(a.source_id, ctx)
            self.assertIn(b.source_id, ctx)
            self.assertIn(a.object_id, ctx)
            self.assertIn(a.sha256, ctx)
            self.assertIn("provenance_records: 2", ctx)
            self.assertIn("Pine index", ctx)

    def test_legacy_content_derived_source_id_remains_resolvable(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            (root / "raw").mkdir(parents=True)
            content = b"legacy evidence bytes\n"
            sha = hashlib.sha256(content).hexdigest()
            legacy_sid = f"src-{sha[:16]}"
            (root / "raw" / f"{sha}.txt").write_bytes(content)
            legacy_event = {
                "event": "ingest",
                "recorded_at": "2026-08-14T00:00:00+00:00",
                "source_id": legacy_sid,
                "sha256": sha,
                "name": "legacy.md",
                "size_bytes": len(content),
                "duplicate_content": False,
                "topic_id": "topic-legacy",
            }
            (root / "manifest.jsonl").write_text(json.dumps(legacy_event) + "\n", encoding="utf-8")

            src = find_source(root, legacy_sid, topic_id="topic-legacy")
            self.assertTrue(src.legacy)
            self.assertEqual(src.source_id, legacy_sid)
            self.assertEqual(src.object_id, f"obj-{sha}")
            self.assertEqual(src.raw_path.read_bytes(), content)
            self.assertEqual(source_status(root, legacy_sid, topic_id="topic-legacy")["status"], "current")

    def test_legacy_source_can_be_superseded_by_new_opaque_revision(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            (root / "raw").mkdir(parents=True)
            old_content = b"legacy state alpha\n"
            old_sha = hashlib.sha256(old_content).hexdigest()
            legacy_sid = f"src-{old_sha[:16]}"
            (root / "raw" / f"{old_sha}.txt").write_bytes(old_content)
            (root / "manifest.jsonl").write_text(json.dumps({
                "event": "ingest",
                "recorded_at": "2026-08-14T00:00:00+00:00",
                "source_id": legacy_sid,
                "sha256": old_sha,
                "name": "legacy.md",
                "size_bytes": len(old_content),
                "duplicate_content": False,
                "topic_id": "topic-legacy",
            }) + "\n", encoding="utf-8")

            new_file = base / "new.md"
            new_file.write_text("new state beta", encoding="utf-8")
            new, _ = ingest_file(
                root,
                new_file,
                topic_id="topic-legacy",
                supersedes_source_id=legacy_sid,
                origin_id="origin-new",
            )
            self.assertNotEqual(new.source_id, legacy_sid)
            self.assertFalse(new.legacy)
            self.assertEqual([src.source_id for src in sources(root, topic_id="topic-legacy")], [new.source_id])
            self.assertEqual(find_source(root, legacy_sid, topic_id="topic-legacy").source_id, legacy_sid)

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
        prompt = answer_prompt("Why?", "### EVIDENCE OBJECT obj-abc\nsource_ids: src-abc\nEvidence")
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
