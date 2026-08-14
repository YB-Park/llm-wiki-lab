#!/usr/bin/env python3
"""Mechanically verify the frozen E012 semantic fixture before model calls."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import generate_corpus as corpus
import run_remote_v0 as runner

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
LOCK = ROOT / "fixture-lock-v0.json"
EXPECTED_LOCK_BLOB = "db0aa090cc6f0c9ead5682cf8ad29d8c7de99237"
DOCS_SHA = "faa7986fb0644b240857f907f6158b71763aa2a5393c0fe55836b0f918e73b4f"
QUERIES_SHA = "f5702e42b94c4d857a3c99c54af48413879602ac9d42036cc1e018257f3b5e89"


def blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=REPO, text=True).strip()


def main() -> None:
    lock_rel = str(LOCK.relative_to(REPO))
    actual_lock = blob(lock_rel)
    assert actual_lock == EXPECTED_LOCK_BLOB, (actual_lock, EXPECTED_LOCK_BLOB)
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    assert data["format"] == "E012-FIXTURE-LOCK-v0"
    assert data["scored_model_calls_observed_at_lock"] is False
    assert data["documents_sha256"] == DOCS_SHA
    assert data["queries_sha256"] == QUERIES_SHA
    for path, expected in data["files"].items():
        actual = blob(path)
        assert actual == expected, (path, actual, expected)

    docs, queries = corpus.generate()
    dsha, qsha = runner.fingerprints(docs, queries)
    assert dsha == DOCS_SHA == runner.DOCS_SHA
    assert qsha == QUERIES_SHA == runner.QUERIES_SHA
    assert runner.MODEL == "gpt-5.6-luna"
    assert runner.BUILD_SEED == 20260818
    assert runner.ANSWER_SEED == 20260819
    assert tuple(runner.CONDS) == ("R1", "C0")
    assert tuple(runner.WAVES) == (0, 1, 2)

    print("E012-FROZEN-FIXTURE-v0")
    print(f"fixtureLock=PASS files={len(data['files'])} manifest={EXPECTED_LOCK_BLOB[:12]}")
    print(f"docsSha={dsha}")
    print(f"queriesSha={qsha}")
    print("model=gpt-5.6-luna conditions=R1,C0 waves=W0,W1,W2 scoredModelCallsAtLock=0")
    print("status=PASS modelCalls=0 frozen=yes")


if __name__ == "__main__":
    main()
