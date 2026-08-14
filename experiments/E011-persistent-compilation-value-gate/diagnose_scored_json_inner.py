#!/usr/bin/env python3
"""Local-only aggregate diagnostic for E011 JSON-like inner payload failures.

Prints no response text, prompts, paths, source IDs, or semantic answers.
"""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANS = ROOT / "runs" / "stage-1a-v0" / "answers"

SMART_TRANS = str.maketrans({
    "\u201c": '"',
    "\u201d": '"',
    "\uff02": '"',
})


def parse(s, strict=True):
    try:
        json.loads(s, strict=strict)
        return True, "ok"
    except json.JSONDecodeError as e:
        return False, e.msg.replace(" ", "_")
    except Exception as e:
        return False, type(e).__name__


def main():
    dirs = sorted([p for p in ANS.iterdir() if p.is_dir()]) if ANS.exists() else []
    c = Counter()
    errors = Counter()
    smart_counts = Counter()

    for d in dirs:
        p = d / "response.txt"
        if not p.exists():
            c["missing_response"] += 1
            continue
        s = p.read_text(encoding="utf-8", errors="replace").strip()
        c["responses"] += 1
        first = s.find("{")
        last = s.rfind("}")
        if first < 0 or last <= first:
            c["no_brace_envelope"] += 1
            continue
        inner = s[first:last+1]
        ok, msg = parse(inner, True)
        if ok:
            c["inner_strict"] += 1
            continue
        errors[msg] += 1

        ok_loose, _ = parse(inner, False)
        if ok_loose:
            c["inner_strict_false"] += 1

        left = inner.count("\u201c")
        right = inner.count("\u201d")
        full = inner.count("\uff02")
        if left or right or full:
            c["has_smart_quotes"] += 1
            smart_counts[f"L{left}-R{right}-F{full}"] += 1

        normalized = inner.translate(SMART_TRANS)
        ok_smart, _ = parse(normalized, True)
        if ok_smart:
            c["smart_quote_normalized_strict"] += 1
        else:
            ok_both, _ = parse(normalized, False)
            if ok_both:
                c["smart_quote_plus_strict_false"] += 1

    print("E011-SCORED-JSON-INNER-DIAG-v0")
    for k in (
        "responses","missing_response","no_brace_envelope","inner_strict",
        "inner_strict_false","has_smart_quotes","smart_quote_normalized_strict",
        "smart_quote_plus_strict_false"
    ):
        print(f"{k}={c[k]}")
    if errors:
        print("decodeErrors=" + ";".join(f"{k}:{v}" for k,v in errors.most_common()))
    else:
        print("decodeErrors=none")
    if smart_counts:
        print("smartQuotePatterns=" + ";".join(f"{k}:{v}" for k,v in smart_counts.most_common(12)))
    else:
        print("smartQuotePatterns=none")
    print("content=NOT_PRINTED modelCalls=0 paths=none")


if __name__ == "__main__":
    main()
