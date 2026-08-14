#!/usr/bin/env python3
"""Classify only residual E011 JSON failures after envelope extraction + strict=False.

Prints no response text, prompts, paths, source IDs, answer text, or JSON values.
"""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANS = ROOT / "runs" / "stage-1a-v0" / "answers"


def loads(s, strict):
    try:
        json.loads(s, strict=strict)
        return True, None
    except json.JSONDecodeError as e:
        return False, (e.msg.replace(" ", "_"), e.lineno, e.colno)


def main():
    c = Counter()
    residual = Counter()
    char_classes = Counter()

    dirs = sorted([p for p in ANS.iterdir() if p.is_dir()]) if ANS.exists() else []
    for d in dirs:
        p = d / "response.txt"
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8", errors="replace").strip()
        first, last = s.find("{"), s.rfind("}")
        if first < 0 or last <= first:
            continue
        inner = s[first:last+1]
        ok, _ = loads(inner, True)
        if ok:
            continue
        ok, err = loads(inner, False)
        if ok:
            continue

        c["residual"] += 1
        msg, line, col = err
        residual[msg] += 1

        # Character-class metadata only; never print characters or content.
        controls = sum(1 for ch in inner if ord(ch) < 32 and ch not in "\r\n\t")
        smart = sum(inner.count(x) for x in ("\u201c", "\u201d", "\uff02"))
        replacement = inner.count("\ufffd")
        non_ascii = sum(1 for ch in inner if ord(ch) > 127)
        newline = inner.count("\n")
        tab = inner.count("\t")
        char_classes[f"ctrl{min(controls,9)}-smart{min(smart,9)}-repl{min(replacement,9)}-nonascii{min(non_ascii,9)}-nl{min(newline,9)}-tab{min(tab,9)}"] += 1

    print("E011-SCORED-JSON-RESIDUAL-DIAG-v0")
    print(f"residual={c['residual']}")
    print("errors=" + (";".join(f"{k}:{v}" for k,v in residual.most_common()) or "none"))
    print("charClasses=" + (";".join(f"{k}:{v}" for k,v in char_classes.most_common()) or "none"))
    print("content=NOT_PRINTED modelCalls=0 paths=none")


if __name__ == "__main__":
    main()
