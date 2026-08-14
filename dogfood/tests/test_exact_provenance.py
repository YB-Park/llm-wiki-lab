from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.calibration import create_topic, record_query, summarize
from dogfood.llm_wiki.provenance import (
    PROVENANCE_FILE,
    bind_exact_raw_span,
    list_exact_provenance,
    provenance_history,
    resolve_exact_raw_span,
)
from dogfood.llm_wiki.retrieval import search
from dogfood.llm_wiki.store import ensure_workspace, ingest_file, source_status
from dogfood.llm_wiki.temporal import change_source, correct_source, dispute_sources


class ExactProvenanceTests(unittest.TestCase):
    def _write(self, base: Path, name: str, text: str) -> Path:
        path = base / name
        path.write_text(text, encoding="utf-8")
        return path

    def _ingest(self, base: Path, root: Path, topic: str, name: str, text: str, origin: str):
        return ingest_file(
            root,
            self._write(base, name, text),
            topic_id=topic,
            origin_id=origin,
        )[0]

    def test_create_resolve_and_exact_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-a"
            text = "header\nDecision quota is 42.\nfooter"
            source = self._ingest(base, root, topic, "a.md", text, "origin-a")
            target = "Decision quota is 42."
            start = text.index(target)
            end = start + len(target)

            first, created1 = bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=source.source_id,
                start=start,
                end=end,
                local_label="decision.quota",
            )
            second, created2 = bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=source.source_id,
                start=start,
                end=end,
                local_label="decision.quota",
            )

            self.assertTrue(created1)
            self.assertFalse(created2)
            self.assertEqual(first, second)
            self.assertEqual(resolve_exact_raw_span(root, first.record_id, topic_id=topic).text, target)
            self.assertEqual(len(provenance_history(root)), 1)
            self.assertEqual(len((root / PROVENANCE_FILE).read_text(encoding="utf-8").splitlines()), 1)

    def test_multiple_local_labels_can_share_one_span_without_raw_duplication(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-a"
            text = "alpha exact evidence omega"
            source = self._ingest(base, root, topic, "a.md", text, "origin-a")
            start = text.index("exact evidence")
            end = start + len("exact evidence")

            a, _ = bind_exact_raw_span(
                root, topic_id=topic, source_id=source.source_id,
                start=start, end=end, local_label="claim.a",
            )
            b, _ = bind_exact_raw_span(
                root, topic_id=topic, source_id=source.source_id,
                start=start, end=end, local_label="claim.b",
            )

            self.assertNotEqual(a.record_id, b.record_id)
            self.assertEqual(len(provenance_history(root)), 2)
            self.assertEqual(len(list((root / "raw").glob("*.txt"))), 1)
            self.assertEqual(resolve_exact_raw_span(root, a.record_id, topic_id=topic).text, "exact evidence")
            self.assertEqual(resolve_exact_raw_span(root, b.record_id, topic_id=topic).text, "exact evidence")
            self.assertEqual([r.record_id for r in list_exact_provenance(root, topic_id=topic, local_label="claim.a")], [a.record_id])

    def test_invalid_spans_missing_sources_topic_mismatch_and_unsafe_labels_fail_before_append(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            source = self._ingest(base, root, "topic-a", "a.md", "abcdef", "origin-a")

            bad_calls = [
                dict(topic_id="topic-a", source_id=source.source_id, start=-1, end=2),
                dict(topic_id="topic-a", source_id=source.source_id, start=2, end=2),
                dict(topic_id="topic-a", source_id=source.source_id, start=2, end=99),
                dict(topic_id="topic-a", source_id="src-missing", start=0, end=1),
                dict(topic_id="topic-b", source_id=source.source_id, start=0, end=1),
            ]
            for kwargs in bad_calls:
                with self.subTest(kwargs=kwargs), self.assertRaises((ValueError, RuntimeError)):
                    bind_exact_raw_span(root, **kwargs)

            for label in ("../claim", "folder/claim", "hello world", "☃", ""):
                with self.subTest(label=label), self.assertRaises(ValueError):
                    bind_exact_raw_span(
                        root,
                        topic_id="topic-a",
                        source_id=source.source_id,
                        start=0,
                        end=1,
                        local_label=label,
                    )
            self.assertEqual(provenance_history(root), [])

    def test_derived_only_authoritative_target_is_not_a_valid_source_revision(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            with self.assertRaisesRegex(ValueError, "source_not_found"):
                bind_exact_raw_span(
                    root,
                    topic_id="topic-a",
                    source_id="derived-page-123",
                    start=0,
                    end=3,
                    local_label="claim.a",
                )
            self.assertEqual(provenance_history(root), [])

    def test_supersession_does_not_auto_follow_current_successor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-a"
            a_text = "The threshold is 10."
            b_text = "The threshold is 20."
            a = self._ingest(base, root, topic, "a.md", a_text, "origin-state")
            record, _ = bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=a.source_id,
                start=a_text.index("10"),
                end=a_text.index("10") + 2,
                local_label="threshold",
            )
            b = self._ingest(base, root, topic, "b.md", b_text, "origin-next")
            correct_source(root, a.source_id, b.source_id, topic_id=topic)

            self.assertEqual(source_status(root, a.source_id, topic_id=topic)["status"], "superseded")
            resolved = resolve_exact_raw_span(root, record.record_id, topic_id=topic)
            self.assertEqual(resolved.text, "10")
            self.assertEqual(resolved.record.source_id, a.source_id)
            self.assertNotEqual(resolved.record.source_id, b.source_id)
            self.assertEqual(list_exact_provenance(root, topic_id=topic)[0].source_id, a.source_id)

    def test_correction_change_and_dispute_semantics_remain_independent_of_pointer(self):
        cases = ("correction", "change", "dispute")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                base = Path(td)
                root = base / "wiki"
                topic = "topic-a"
                a_text = "State alpha."
                b_text = "State beta."
                a = self._ingest(base, root, topic, "a.md", a_text, "origin-a")
                b = self._ingest(base, root, topic, "b.md", b_text, "origin-b")
                record, _ = bind_exact_raw_span(
                    root,
                    topic_id=topic,
                    source_id=a.source_id,
                    start=0,
                    end=len(a_text),
                    local_label=f"state.{case}",
                )

                if case == "correction":
                    correct_source(root, a.source_id, b.source_id, topic_id=topic)
                elif case == "change":
                    change_source(
                        root, a.source_id, b.source_id,
                        topic_id=topic, effective_at="2025-01-02T03:04:05+00:00",
                    )
                else:
                    dispute_sources(root, a.source_id, b.source_id, topic_id=topic)

                resolved = resolve_exact_raw_span(root, record.record_id, topic_id=topic)
                self.assertEqual(resolved.text, a_text)
                self.assertEqual(resolved.record.source_id, a.source_id)
                self.assertFalse(hasattr(resolved.record, "relation_kind"))
                self.assertFalse(hasattr(resolved.record, "contested"))

    def test_raw_object_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-a"
            source = self._ingest(base, root, topic, "a.md", "immutable evidence", "origin-a")
            record, _ = bind_exact_raw_span(
                root, topic_id=topic, source_id=source.source_id,
                start=0, end=9, local_label="claim.a",
            )
            source.raw_path.write_text("tampered evidence", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "provenance_raw_object_integrity_mismatch"):
                resolve_exact_raw_span(root, record.record_id, topic_id=topic)

    def test_provenance_log_identity_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-a"
            source = self._ingest(base, root, topic, "a.md", "immutable evidence", "origin-a")
            bind_exact_raw_span(
                root, topic_id=topic, source_id=source.source_id,
                start=0, end=9, local_label="claim.a",
            )
            path = root / PROVENANCE_FILE
            row = json.loads(path.read_text(encoding="utf-8").strip())
            row["object_id"] = "obj-" + "0" * 64
            path.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "provenance_record_identity_digest_mismatch"):
                provenance_history(root)

    def test_binding_exact_provenance_does_not_change_default_retrieval(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic = "topic-a"
            a = self._ingest(base, root, topic, "a.md", "alpha quota decision forty two", "origin-a")
            self._ingest(base, root, topic, "b.md", "beta calendar archive", "origin-b")

            before = search(root, "alpha quota decision", topic_id=topic, top_k=8)
            signature_before = [(h.object_id, h.score, h.source_ids, h.snippet) for h in before]
            bind_exact_raw_span(
                root,
                topic_id=topic,
                source_id=a.source_id,
                start=0,
                end=len("alpha quota decision"),
                local_label="claim.search",
            )
            after = search(root, "alpha quota decision", topic_id=topic, top_k=8)
            signature_after = [(h.object_id, h.score, h.source_ids, h.snippet) for h in after]
            self.assertEqual(signature_after, signature_before)

    def test_e013_sanitized_export_does_not_leak_provenance_identity_or_span(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            topic_row = create_topic(root, "Private calibration topic")
            source = self._ingest(
                base, root, topic_row["topic_id"], "a.md",
                "secret exact evidence material", "origin-secret",
            )
            record, _ = bind_exact_raw_span(
                root,
                topic_id=topic_row["topic_id"],
                source_id=source.source_id,
                start=7,
                end=21,
                local_label="SECRET_LOCAL_LABEL_7f31",
            )
            record_query(root, topic_row["topic_id"], "search", "exact_provenance")

            payload = json.dumps(summarize(root), ensure_ascii=False, sort_keys=True)
            self.assertNotIn("SECRET_LOCAL_LABEL_7f31", payload)
            self.assertNotIn(source.source_id, payload)
            self.assertNotIn(record.record_id, payload)
            self.assertNotIn(PROVENANCE_FILE, payload)
            self.assertNotIn("origin-secret", payload)

    def test_workspace_config_still_keeps_compiled_provider_disabled(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            ensure_workspace(root)
            config = json.loads((root / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["compiled_provider"], "disabled")


if __name__ == "__main__":
    unittest.main()
