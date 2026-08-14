#!/usr/bin/env python3
"""Run E012 reuse-to-update maintenance gate on the GitHub remote lab."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import core
import generate_corpus as corpus

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
E011 = ROOT.parent / "E011-persistent-compilation-value-gate"
REQUEST = REPO / "remote-lab" / "e012-request.json"
RUN = ROOT / "runs" / "remote-v0"
MODEL = "gpt-5.6-luna"
DOCS_SHA = "faa7986fb0644b240857f907f6158b71763aa2a5393c0fe55836b0f918e73b4f"
QUERIES_SHA = "e539ace24e7eb516c93ce564b48f78e4dd2af45cf3dc5b4746f38ff995314430"
BUILD_SEED = 20260818
ANSWER_SEED = 20260819
CONDS = ("R1", "C0")
WAVES = (0, 1, 2)

spec = importlib.util.spec_from_file_location("e012_remote", E011 / "remote_instrumentation_v1.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load remote instrumentation")
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprints(docs: list[dict], queries: list[dict]) -> tuple[str, str]:
    dsha = corpus.sha256_bytes(corpus.jsonl_bytes(docs))
    qbytes = (json.dumps(queries, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    return dsha, corpus.sha256_bytes(qbytes)


def load_request() -> dict:
    data = json.loads(REQUEST.read_text(encoding="utf-8"))
    required = {"request_id", "kind", "model", "per_call_max_ai_credits", "total_estimated_ai_credit_guard"}
    if set(data) != required or data["kind"] != "e012-remote-v0" or data["model"] != MODEL:
        raise SystemExit("E012-STOP request_invalid")
    if not isinstance(data["per_call_max_ai_credits"], int):
        raise SystemExit("E012-STOP per_call_guard_invalid")
    if not isinstance(data["total_estimated_ai_credit_guard"], (int, float)):
        raise SystemExit("E012-STOP total_guard_invalid")
    return data


def remote_preflight() -> None:
    d = RUN / "preflight"
    p = d / "status.json"
    if p.exists():
        s = json.loads(p.read_text(encoding="utf-8"))
        if s.get("status") == "PASS" and s.get("model") == MODEL:
            print("E012-PREFLIGHT status=PASS reused=yes modelCallsThisRun=0 corpus=NOT_USED quality=NONE")
            return
        raise SystemExit("E012-STOP preflight_status_invalid")
    if d.exists():
        raise SystemExit("E012-STOP incomplete_preflight artifact_preserved=yes")
    context = "### SOURCE T99-S01 — Note\nZephyr Meadow currently approves the cobalt card."
    question = "What card is currently approved for Zephyr Meadow, and which source states it?"
    r = remote.call(core.answer_prompt(question, context), MODEL, d, "e012-preflight")
    parsed = core.parse_answer(str(r["response"]), context, {"T99-S01"})
    if not parsed["valid"]:
        raise SystemExit(f"E012-STOP preflight_contract_{parsed.get('violation')} artifact_preserved=yes")
    p.write_text(json.dumps({"status":"PASS","model":MODEL,"corpus_used":False}, indent=2) + "\n", encoding="utf-8")
    print("E012-PREFLIGHT status=PASS reused=no modelCallsThisRun=1 corpus=NOT_USED quality=NONE")


def build_tasks(topics: list[str]) -> list[tuple[int, str]]:
    rows = [(w, t) for w in WAVES for t in topics]
    random.Random(BUILD_SEED).shuffle(rows)
    return rows


def build_all(docs: list[dict], topics: list[str]) -> dict[tuple[int, str], str]:
    out = {}
    for seq, (wave, topic) in enumerate(build_tasks(topics), 1):
        d = RUN / "build" / f"{seq:03d}-W{wave}-{topic}"
        p = d / "summary.md"
        if p.exists():
            out[(wave, topic)] = p.read_text(encoding="utf-8")
            print(f"BUILD-SKIP seq={seq}")
            continue
        if d.exists():
            raise SystemExit(f"E012-STOP incomplete_build synthetic_call={seq:03d}-W{wave}-{topic} artifact_preserved=yes")
        scoped = corpus.docs_through_wave(docs, topic, wave)
        r = remote.call(core.compiler_prompt(scoped), MODEL, d, f"e012-build-{seq:03d}-W{wave}-{topic}")
        text = str(r["response"]).strip()
        if not text:
            raise SystemExit(f"E012-STOP empty_build synthetic_call={seq:03d}-W{wave}-{topic}")
        p.write_text(text + "\n", encoding="utf-8")
        out[(wave, topic)] = text + "\n"
        print(f"BUILD-DONE seq={seq}")
    return out


def answer_tasks(queries: list[dict]) -> list[tuple[str, str]]:
    rows = [(q["query_id"], c) for q in queries for c in CONDS]
    random.Random(ANSWER_SEED).shuffle(rows)
    return rows


def run_answers(docs: list[dict], queries: list[dict], summaries: dict[tuple[int, str], str]) -> list[dict]:
    qmap = {q["query_id"]: q for q in queries}
    results = []
    cache = {}
    dirs = {}
    actual = 0
    for qid, cond in answer_tasks(queries):
        q = qmap[qid]
        wave = int(q["wave"])
        scoped = corpus.docs_through_wave(docs, q["topic_id"], wave)
        ctx, raw_n = core.context_for(cond, scoped, summaries[(wave, q["topic_id"])])
        prompt = core.answer_prompt(q["question"], ctx)
        ph = h(prompt)
        if ph not in cache:
            actual += 1
            d = RUN / "answers" / f"{actual:03d}-{ph[:12]}"
            p = d / "parsed.json"
            if p.exists():
                parsed = json.loads(p.read_text(encoding="utf-8"))
                print(f"ANSWER-SKIP seq={actual}")
            elif d.exists():
                raise SystemExit(f"E012-STOP incomplete_answer synthetic_call={actual:03d}-{ph[:12]} artifact_preserved=yes")
            else:
                r = remote.call(prompt, MODEL, d, f"e012-answer-{actual:03d}-{ph[:12]}")
                parsed = core.parse_answer(str(r["response"]), ctx)
                p.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"ANSWER-DONE seq={actual} contract={'valid' if parsed['valid'] else 'invalid'}")
            cache[ph] = parsed
            dirs[ph] = d
        score = core.score(q, cache[ph])
        results.append({
            "topic_id": q["topic_id"], "wave": wave, "query_id": qid, "query_class": q["class"],
            "condition": cond, "prompt_hash": ph, "call_dir": str(dirs[ph].relative_to(RUN)),
            "raw_docs_exposed": raw_n, "score": score,
        })
    if len(results) != 216:
        raise SystemExit(f"E012-STOP logical_result_count got={len(results)}")
    (RUN / "logical-results.local.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results


def summarize(results: list[dict]) -> str:
    by = defaultdict(list)
    for row in results:
        by[row["condition"]].append(row)
    lines = ["E012-SAFE-HANDOFF-v0", f"logicalAnswers={len(results)} actualAnswerCalls={len({r['prompt_hash'] for r in results})} buildCalls=36 model={MODEL}"]
    for cond in CONDS:
        c = Counter()
        for row in by[cond]:
            s = row["score"]
            c["strict"] += int(s["strict_pass"])
            c["signals"] += s["signal_hits"]; c["signal_total"] += s["signal_total"]
            c["sources"] += s["source_hits"]; c["source_total"] += s["source_total"]
            c["invalid"] += int(not s["valid"]); c["stale"] += int(s["stale_substitution"])
        lines.append(
            f"{cond} strict={c['strict']}/{len(by[cond])} signals={c['signals']}/{c['signal_total']} "
            f"prov={c['sources']}/{c['source_total']} invalid={c['invalid']} staleSub={c['stale']}"
        )
    lines.append("analysis=required reusePerUpdate=N1,N3,N6,N10,N20 freeform=none paths=none")
    return "\n".join(lines) + "\n"


def main() -> None:
    req = load_request()
    docs, queries = corpus.generate()
    dsha, qsha = fingerprints(docs, queries)
    if dsha != DOCS_SHA or qsha != QUERIES_SHA:
        raise SystemExit("E012-STOP corpus_fingerprint_mismatch")
    remote.configure(RUN, int(req["per_call_max_ai_credits"]), float(req["total_estimated_ai_credit_guard"]))
    RUN.mkdir(parents=True, exist_ok=True)
    remote_preflight()
    topics = sorted({d["topic_id"] for d in docs})
    summaries = build_all(docs, topics)
    results = run_answers(docs, queries, summaries)
    text = summarize(results)
    (RUN / "safe-handoff.txt").write_text(text, encoding="utf-8")
    print(text, end="")
    print("E012-RUNTIME-HANDOFF-v0")
    print(
        f"request={req['request_id']} estimatedCredits={remote.estimated_used():.3f} "
        f"totalGuard={float(req['total_estimated_ai_credit_guard']):.0f} perCallGuard={int(req['per_call_max_ai_credits'])}"
    )
    print("modelRerolls=none companyData=NOT_ALLOWED")


if __name__ == "__main__":
    main()
