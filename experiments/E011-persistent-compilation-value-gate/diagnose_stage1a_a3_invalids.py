#!/usr/bin/env python3
"""Aggregate A3 invalid causes without printing semantic content."""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "stage-1a-v0"
RESULTS = RUN / "logical-results.transport-a3.local.json"
CONDS = ("R0", "R1", "C0", "C1")


def cause(score):
    if score.get("valid"):
        return "valid"
    return score.get("violation") or "unknown"


def fmt_counter(c):
    keys = ("valid", "json", "schema", "source_visibility_or_existence", "object", "unknown")
    return " ".join(f"{k}={c[k]}" for k in keys if c[k]) or "none"


def main():
    if not RESULTS.exists():
        raise SystemExit("E011-A3-INVALID-DIAG missing_results run=reparse_stage1a_a3.py")
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))
    if len(rows) != 288:
        raise SystemExit(f"E011-A3-INVALID-DIAG expected_288 got={len(rows)}")

    actual = Counter()
    modes = defaultdict(Counter)
    answer_root = RUN / "answers"
    dirs = [d for d in answer_root.iterdir() if d.is_dir()] if answer_root.exists() else []
    for d in dirs:
        p = d / "parsed.transport-a3.json"
        if not p.exists():
            actual["missing"] += 1
            continue
        parsed = json.loads(p.read_text(encoding="utf-8"))
        c = "valid" if parsed.get("valid") else (parsed.get("violation") or "unknown")
        actual[c] += 1
        modes[parsed.get("transport_mode") or "none"][c] += 1

    print("E011-STAGE1A-A3-INVALID-DIAG-v0")
    print(f"actualResponses={len(dirs)} " + fmt_counter(actual))
    for mode in ("strict_inner", "control_char_strict_false", "transport_residual"):
        if mode in modes:
            print(f"actual transport={mode} " + fmt_counter(modes[mode]))

    for cond in CONDS:
        rs = [r for r in rows if r["condition"] == cond]
        c = Counter(cause(r["score"]) for r in rs)
        valid = [r for r in rs if r["score"].get("valid")]
        strict = sum(int(r["score"].get("strict_pass")) for r in valid)
        sh = sum(r["score"].get("signal_hits",0) for r in valid)
        st = sum(r["score"].get("signal_total",0) for r in valid)
        ph = sum(r["score"].get("source_hits",0) for r in valid)
        pt = sum(r["score"].get("source_total",0) for r in valid)
        print(
            f"{cond} logical={len(rs)} {fmt_counter(c)} "
            f"validOnlyStrict={strict}/{len(valid)} validOnlySignals={sh}/{st} validOnlyProv={ph}/{pt}"
        )
        for scale in ("small", "large"):
            xs = [r for r in rs if r["scale"] == scale]
            cc = Counter(cause(r["score"]) for r in xs)
            print(f"{cond} scale={scale} " + fmt_counter(cc))

    for cls in ("exact_provenance", "global_synthesis", "decision_rationale"):
        bits=[]
        for cond in CONDS:
            xs=[r for r in rows if r["condition"]==cond and r["query_class"]==cls]
            cc=Counter(cause(r["score"]) for r in xs)
            bits.append(f"{cond}[v={cc['valid']},j={cc['json']},s={cc['schema']},p={cc['source_visibility_or_existence']}]")
        print(f"class={cls} " + " ".join(bits))

    print("content=NOT_PRINTED modelCalls=0 paths=none interpretation=decompose_contract_from_semantics")


if __name__ == "__main__":
    main()
