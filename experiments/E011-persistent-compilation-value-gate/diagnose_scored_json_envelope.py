#!/usr/bin/env python3
"""Local-only aggregate diagnostic for E011 scored answer serialization envelopes.

Prints no response text, prompts, paths, source IDs, or semantic answers.
"""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANS = ROOT / "runs" / "stage-1a-v0" / "answers"
BULLET = "\u2022"


def strict_ok(s):
    try:
        json.loads(s)
        return True
    except Exception:
        return False


def main():
    dirs = sorted([p for p in ANS.iterdir() if p.is_dir()]) if ANS.exists() else []
    counts = Counter()
    prefix_codepoints = Counter()

    for d in dirs:
        p = d / "response.txt"
        if not p.exists():
            counts["missing_response"] += 1
            continue
        s = p.read_text(encoding="utf-8", errors="replace").strip()
        counts["responses"] += 1
        if strict_ok(s):
            counts["strict_json"] += 1
            continue

        first = s.find("{")
        last = s.rfind("}")
        if first >= 0 and last > first:
            counts["brace_envelope"] += 1
            inner = s[first:last+1]
            if strict_ok(inner):
                counts["inner_strict_json"] += 1
            prefix = s[:first]
            suffix = s[last+1:]
            if prefix.strip():
                counts["prefix_noise"] += 1
                cps = ",".join(f"U+{ord(ch):04X}" for ch in prefix.strip()[:4])
                prefix_codepoints[cps] += 1
                if prefix.strip() == BULLET:
                    counts["exact_bullet_prefix"] += 1
            if suffix.strip():
                counts["suffix_noise"] += 1
        else:
            counts["no_single_brace_envelope"] += 1

    print("E011-SCORED-JSON-ENVELOPE-DIAG-v0")
    for k in (
        "responses","missing_response","strict_json","brace_envelope","inner_strict_json",
        "prefix_noise","exact_bullet_prefix","suffix_noise","no_single_brace_envelope"
    ):
        print(f"{k}={counts[k]}")
    if prefix_codepoints:
        summary = ";".join(f"{k}:{v}" for k,v in sorted(prefix_codepoints.items()))
        print(f"prefixCodepoints={summary}")
    else:
        print("prefixCodepoints=none")
    print("content=NOT_PRINTED modelCalls=0 paths=none")


if __name__ == "__main__":
    main()
