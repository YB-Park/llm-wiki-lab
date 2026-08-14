#!/usr/bin/env python3
"""Read-only analysis for E012 reuse-to-update maintenance gate."""

from __future__ import annotations

import importlib.util
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import core
import generate_corpus as corpus

ROOT = Path(__file__).resolve().parent
E011 = ROOT.parent / "E011-persistent-compilation-value-gate"
RUN = ROOT / "runs" / "remote-v0"
RESULTS = RUN / "logical-results.local.json"
CONDS = ("R1", "C0")
WAVES = (0, 1, 2)
REUSE = (1, 3, 6, 10, 20)
BOOT_SEED = 20260820
BOOT_N = 20000

spec = importlib.util.spec_from_file_location("e012_analysis_remote", E011 / "remote_instrumentation_v1.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load remote instrumentation")
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)


def rate(n: float, d: float) -> float:
    return n / d if d else 1.0


def quality(rows: list[dict]) -> dict:
    strict = sum(int(r["score"]["strict_pass"]) for r in rows)
    sh = sum(r["score"]["signal_hits"] for r in rows)
    st = sum(r["score"]["signal_total"] for r in rows)
    ph = sum(r["score"]["source_hits"] for r in rows)
    pt = sum(r["score"]["source_total"] for r in rows)
    invalid = sum(int(not r["score"]["valid"]) for r in rows)
    stale = sum(int(r["score"].get("stale_substitution", False)) for r in rows)
    return {
        "strict": strict, "n": len(rows), "signal_hits": sh, "signal_total": st,
        "prov_hits": ph, "prov_total": pt, "invalid": invalid, "stale": stale,
        "strict_rate": rate(strict, len(rows)), "signal_rate": rate(sh, st), "prov_rate": rate(ph, pt),
    }


def query_tokens(row: dict) -> float:
    m = remote.collect_call(RUN / row["call_dir"])
    return m["input_tokens"] + m["output_tokens"]


def build_map() -> dict[tuple[int, str], dict]:
    out = {}
    for d in sorted((RUN / "build").iterdir()):
        parts = d.name.split("-", 2)
        if len(parts) != 3:
            continue
        _, wave_text, topic = parts
        wave = int(wave_text[1:])
        m = remote.collect_call(d)
        summary = (d / "summary.md").read_text(encoding="utf-8")
        out[(wave, topic)] = {
            "tokens": m["input_tokens"] + m["output_tokens"],
            "credits": m["estimated_ai_credits"], "summary": summary,
            "bytes": len(summary.encode("utf-8")),
        }
    if len(out) != 36:
        raise SystemExit(f"E012-ANALYSIS incomplete_builds got={len(out)} expected=36")
    return out


def topic_values(rows: list[dict], metric: str) -> dict[str, float]:
    by = defaultdict(list)
    for r in rows:
        by[r["topic_id"]].append(r)
    return {topic: quality(rs)[metric] for topic, rs in by.items()}


def paired_boot(a: dict[str, float], b: dict[str, float]) -> tuple[float, float, float]:
    keys = sorted(a)
    diffs = [a[k] - b[k] for k in keys]
    obs = sum(diffs) / len(diffs)
    rng = random.Random(BOOT_SEED)
    draws = [sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(BOOT_N)]
    draws.sort()
    return obs, draws[int(.025 * (len(draws) - 1))], draws[int(.975 * (len(draws) - 1))]


def break_even(build_tokens: float, raw_query_tokens: float, compiled_query_tokens: float):
    saving = raw_query_tokens - compiled_query_tokens
    return None if saving <= 0 else max(1, math.ceil(build_tokens / saving))


def main() -> None:
    if not RESULTS.exists():
        raise SystemExit("E012-ANALYSIS results_missing")
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))
    if len(rows) != 216:
        raise SystemExit(f"E012-ANALYSIS expected_216 got_{len(rows)}")
    docs, queries = corpus.generate()
    builds = build_map()
    bycond = {c: [r for r in rows if r["condition"] == c] for c in CONDS}
    if any(len(v) != 108 for v in bycond.values()):
        raise SystemExit("E012-ANALYSIS condition_count_mismatch")

    print("E012-ANALYSIS-HANDOFF-v0")
    print("mode=read-only modelCalls=0 unit=topic bootstrap=12topics freeform=none paths=none")

    qgroup = defaultdict(list)
    for q in queries:
        qgroup[(q["topic_id"], int(q["wave"]))].append(q)

    for wave in WAVES:
        sig_hit = sig_total = prov_hit = prov_total = state_bytes = raw_bytes = unknown_ids = affected = stale_states = 0
        for topic in sorted({d["topic_id"] for d in docs}):
            summary = builds[(wave, topic)]["summary"]
            lower = summary.lower()
            scoped = corpus.docs_through_wave(docs, topic, wave)
            raw = core.raw_context(scoped)
            state_bytes += builds[(wave, topic)]["bytes"]
            raw_bytes += len(raw.encode("utf-8"))
            allowed = {d["source_id"] for d in scoped}
            unknown = set(core.e011_core.SOURCE_ID_RE.findall(summary)) - allowed
            unknown_ids += len(unknown)
            affected += int(bool(unknown))
            topic_stale = False
            for q in qgroup[(topic, wave)]:
                required_present = sum(s.lower() in lower for s in q["required_signals"])
                sig_hit += required_present; sig_total += len(q["required_signals"])
                prov_hit += sum(sid.lower() in lower for sid in q["required_source_ids"]); prov_total += len(q["required_source_ids"])
                if required_present < len(q["required_signals"]) and any(s.lower() in lower for s in q.get("forbidden_current_signals", [])):
                    topic_stale = True
            stale_states += int(topic_stale)
        print(
            f"compiledState wave=W{wave} signals={sig_hit}/{sig_total} prov={prov_hit}/{prov_total} "
            f"staleStates={stale_states}/12 unknownSourceIDs={unknown_ids} affectedStates={affected}/12 "
            f"bytes={state_bytes} rawBytes={raw_bytes} ratio={state_bytes/raw_bytes:.3f}"
        )

    qmetrics = {}
    qcost = {}
    for cond in CONDS:
        q = quality(bycond[cond]); qmetrics[cond] = q; qcost[cond] = sum(query_tokens(r) for r in bycond[cond])
        print(
            f"{cond} strict={q['strict']}/{q['n']} signals={q['signal_hits']}/{q['signal_total']} "
            f"prov={q['prov_hits']}/{q['prov_total']} invalid={q['invalid']} staleSub={q['stale']} queryTokens={int(qcost[cond])}"
        )
        for wave in WAVES:
            qw = quality([r for r in bycond[cond] if int(r["wave"]) == wave])
            print(
                f"{cond} wave=W{wave} strict={qw['strict']}/{qw['n']} signals={qw['signal_hits']}/{qw['signal_total']} "
                f"prov={qw['prov_hits']}/{qw['prov_total']} invalid={qw['invalid']} staleSub={qw['stale']}"
            )

    bits = []
    for metric in ("strict_rate", "signal_rate", "prov_rate"):
        obs, lo, hi = paired_boot(topic_values(bycond["C0"], metric), topic_values(bycond["R1"], metric))
        bits.append(f"{metric}={obs:+.3f}[{lo:+.3f},{hi:+.3f}]")
    print("paired C0-R1 " + " ".join(bits))

    build_total = sum(v["tokens"] for v in builds.values())
    aggregate_be = break_even(build_total, qcost["R1"], qcost["C0"])
    per_topic = []
    none = 0
    for topic in sorted({r["topic_id"] for r in rows}):
        b = sum(builds[(wave, topic)]["tokens"] for wave in WAVES)
        rq = sum(query_tokens(r) for r in bycond["R1"] if r["topic_id"] == topic)
        cq = sum(query_tokens(r) for r in bycond["C0"] if r["topic_id"] == topic)
        be = break_even(b, rq, cq)
        if be is None:
            none += 1
        else:
            per_topic.append(be)
    if per_topic:
        s = sorted(per_topic); median = (s[(len(s)-1)//2] + s[len(s)//2]) / 2
        detail = f"median={median:g} min={min(s)} max={max(s)}"
    else:
        detail = "median=none min=none max=none"
    print(
        f"breakEven revisitsPerUpdate aggregate={aggregate_be if aggregate_be is not None else 'none'} "
        f"topicFinite={len(per_topic)}/12 none={none} {detail}"
    )

    for n in REUSE:
        r1 = n * qcost["R1"]
        c0 = build_total + n * qcost["C0"]
        quality_noninferior = (
            qmetrics["C0"]["strict_rate"] >= qmetrics["R1"]["strict_rate"]
            and qmetrics["C0"]["signal_rate"] >= qmetrics["R1"]["signal_rate"]
            and qmetrics["C0"]["prov_rate"] >= qmetrics["R1"]["prov_rate"]
        )
        frontier = "C0" if quality_noninferior and c0 <= r1 else "R1"
        if quality_noninferior and c0 == r1:
            frontier = "R1,C0"
        print(f"reusePerUpdate N={n} lifecycleTokens=R1:{int(r1)} C0:{int(c0)} frontier={frontier}")

    for cls in ("current_exact", "current_synthesis", "decision_history"):
        bits = []
        for cond in CONDS:
            q = quality([r for r in bycond[cond] if r["query_class"] == cls])
            bits.append(f"{cond}:{q['strict']}/{q['n']}")
        print(f"class={cls} " + " ".join(bits))

    metas = list(RUN.rglob("remote-meta.json"))
    telemetry = [remote.collect_call(p.parent) for p in metas]
    print("E012-COST-HANDOFF-v0")
    print(
        f"actualModelCalls={len(telemetry)} estimatedCredits={sum(r['estimated_ai_credits'] for r in telemetry):.3f} "
        f"inputTokens={int(sum(r['input_tokens'] for r in telemetry))} outputTokens={int(sum(r['output_tokens'] for r in telemetry))}"
    )
    print("caution=synthetic12;fullRebuild;authorGroundTruth;sameModelBuildAnswer;topicRoutingOracle;tokenProxyNotHumanUtility")


if __name__ == "__main__":
    main()
