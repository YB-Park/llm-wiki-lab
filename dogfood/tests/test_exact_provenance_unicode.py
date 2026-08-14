from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.provenance import bind_exact_raw_span, resolve_exact_raw_span
from dogfood.llm_wiki.store import ingest_file


class ExactProvenanceUnicodeTests(unittest.TestCase):
    def test_korean_character_offsets_round_trip_exact_utf8_text(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "wiki"
            path = base / "note.md"
            text = "서론🙂\n결정 근거는 원본 증거를 우선한다.\n끝"
            path.write_text(text, encoding="utf-8")
            source, _ = ingest_file(root, path, topic_id="topic-ko", origin_id="origin-ko")

            target = "결정 근거는 원본 증거를 우선한다."
            start = text.index(target)
            record, created = bind_exact_raw_span(
                root,
                topic_id="topic-ko",
                source_id=source.source_id,
                start=start,
                end=start + len(target),
                local_label="decision.ko",
            )
            resolved = resolve_exact_raw_span(root, record.record_id, topic_id="topic-ko")

            self.assertTrue(created)
            self.assertEqual(resolved.text, target)
            self.assertEqual(resolved.text.encode("utf-8"), target.encode("utf-8"))
            self.assertEqual(record.start, start)
            self.assertEqual(record.end, start + len(target))


if __name__ == "__main__":
    unittest.main()
