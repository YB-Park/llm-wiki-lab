#!/usr/bin/env python3
"""Audit whether trivial candidate-surface features predict E009A gold labels.

This is a pre-scoring corpus diagnostic, not an evaluation metric. It looks only at
candidate length/line/source-mention counts to detect accidental template leakage.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "corpus" / "cases.jsonl"


def rows():
    return [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]


def features(row):
    text = row["candidate_state"]
    return {
        "bytes": len(text.encode("utf-8")),
        "lines": len(text.splitlines()),
        "source_mentions": len(re.findall(r"\[S\d+\]", text)),
    }


def best_threshold_accuracy(values, labels):
    unique = sorted(set(values))
    if not unique:
        return 0.5, None
    cuts = [unique[0] - 1] + [(a + b) / 2 for a, b in zip(unique, unique[1:])] + [unique[-1] + 1]
    best = (0.0, None, None)
    for cut in cuts:
        for safe_if_high in (True, False):
            pred = [(v >= cut) if safe_if_high else (v < cut) for v in values]
            acc = sum(int(p == y) for p, y in zip(pred, labels)) / len(labels)
            if acc > best[0]:
                best = (acc, cut, safe_if_high)
    return best


def main():
    data = rows()
    labels = [row["gold_label"] == "safe_commit" for row in data]
    safe = [features(row) for row in data if row["gold_label"] == "safe_commit"]
    unsafe = [features(row) for row in data if row["gold_label"] == "unsafe_commit"]

    print("E009A-SURFACE-BALANCE-v0")
    for key in ("bytes", "lines", "source_mentions"):
        sv = [x[key] for x in safe]
        uv = [x[key] for x in unsafe]
        allv = [features(row)[key] for row in data]
        acc, cut, direction = best_threshold_accuracy(allv, labels)
        print(
            f"{key} safeMean={mean(sv):.2f} unsafeMean={mean(uv):.2f} "
            f"safeMedian={median(sv):.2f} unsafeMedian={median(uv):.2f} "
            f"best1DAcc={acc:.3f} cut={cut} safeIfHigh={direction}"
        )

    pair_safe_longer = pair_unsafe_longer = pair_equal = 0
    by_group = {}
    for row in data:
        by_group.setdefault(row["scenario_group"], []).append(row)
    for pair in by_group.values():
        s = next(row for row in pair if row["gold_label"] == "safe_commit")
        u = next(row for row in pair if row["gold_label"] == "unsafe_commit")
        sb = features(s)["bytes"]
        ub = features(u)["bytes"]
        if sb > ub:
            pair_safe_longer += 1
        elif ub > sb:
            pair_unsafe_longer += 1
        else:
            pair_equal += 1
    print(f"pairLengthDirection safeLonger={pair_safe_longer} unsafeLonger={pair_unsafe_longer} equal={pair_equal}")


if __name__ == "__main__":
    main()
