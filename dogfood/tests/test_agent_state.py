from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from dogfood.llm_wiki.agent_state import (
    add_pending_lineage,
    maintenance_usage,
    open_pending_lineage,
    reserve_maintenance_call,
    resolve_pending_lineage,
    set_source_locator,
    source_locators,
)
from dogfood.llm_wiki.store import ensure_workspace


class AgentStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent-state-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "wiki"
        ensure_workspace(self.root)

    def test_pending_lineage_survives_reopen_and_exact_retry_is_idempotent(self):
        kwargs = dict(
            created_at="2026-08-16T12:00:00+09:00",
            topic_id="topic-abc",
            topic_label="runtime",
            workspace_file="docs/state.md",
            predecessor_source_ids=["src-old"],
            successor_source_id="src-new",
        )
        first = add_pending_lineage(self.root, **kwargs)
        second = add_pending_lineage(self.root, **kwargs)
        self.assertEqual(first["id"], second["id"])
        self.assertEqual([row["id"] for row in open_pending_lineage(self.root)], [first["id"]])

        resolved = resolve_pending_lineage(
            self.root,
            first["id"],
            relation="change",
            predecessor_source_id="src-old",
            resolved_at="2026-08-16T12:10:00+09:00",
        )
        self.assertEqual(resolved["status"], "resolved")
        self.assertEqual(resolved["relation"], "change")
        self.assertEqual(resolved["remaining_predecessor_source_ids"], [])
        self.assertEqual(resolved["continuation_decision_id"], "")
        self.assertEqual(open_pending_lineage(self.root), [])

    def test_multi_predecessor_resolution_keeps_remaining_ambiguity_open(self):
        first = add_pending_lineage(
            self.root,
            created_at="2026-08-16T12:00:00+09:00",
            topic_id="topic-abc",
            topic_label="runtime",
            workspace_file="docs/state.md",
            predecessor_source_ids=["src-old-a", "src-old-b"],
            successor_source_id="src-new",
        )
        resolved = resolve_pending_lineage(
            self.root,
            first["id"],
            relation="correction",
            predecessor_source_id="src-old-a",
            resolved_at="2026-08-16T12:05:00+09:00",
        )
        self.assertEqual(resolved["remaining_predecessor_source_ids"], ["src-old-b"])
        self.assertTrue(resolved["continuation_decision_id"].startswith("pd-"))
        open_rows = open_pending_lineage(self.root)
        self.assertEqual(len(open_rows), 1)
        self.assertEqual(open_rows[0]["id"], resolved["continuation_decision_id"])
        self.assertEqual(open_rows[0]["predecessor_source_ids"], ["src-old-b"])
        self.assertEqual(open_rows[0]["successor_source_id"], "src-new")

    def test_daily_reservation_is_durable_and_resets_only_when_day_changes(self):
        day = "2026-08-16"
        self.assertEqual(maintenance_usage(self.root, day=day)["reserved_calls"], 0)
        first = reserve_maintenance_call(self.root, day=day, limit=2)
        second = reserve_maintenance_call(self.root, day=day, limit=2)
        blocked = reserve_maintenance_call(self.root, day=day, limit=2)
        self.assertTrue(first["allowed"])
        self.assertTrue(second["allowed"])
        self.assertFalse(blocked["allowed"])
        self.assertEqual(maintenance_usage(self.root, day=day)["reserved_calls"], 2)
        self.assertEqual(maintenance_usage(self.root, day="2026-08-17")["reserved_calls"], 0)
        next_day = reserve_maintenance_call(self.root, day="2026-08-17", limit=2)
        self.assertTrue(next_day["allowed"])
        self.assertEqual(next_day["reserved_calls"], 1)

    def test_source_locator_is_private_durable_noncanonical_state(self):
        source_id = "src-abc"
        digest = "a" * 64
        set_source_locator(self.root, source_id, relative_path="docs/example.md", sha256=digest)
        self.assertEqual(source_locators(self.root)[source_id]["relative_path"], "docs/example.md")
        state_path = self.root / "agent-state.json"
        self.assertTrue(state_path.exists())
        if os.name == "posix":
            self.assertEqual(state_path.stat().st_mode & 0o777, 0o600)
        manifest = (self.root / "manifest.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("docs/example.md", manifest)
        self.assertNotIn(source_id, manifest)


if __name__ == "__main__":
    unittest.main()
