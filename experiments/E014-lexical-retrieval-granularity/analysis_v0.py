from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from generate_corpus import build_corpus, corpus_sha256
from retrieval_core import index_stats, provenance_reversible, rank_objects

TOP_K_PRIMARY = 5
TOP_K_SECONDARY = 8
BOOTSTRAP_REPS = 20000
BOOTSTRAP_SEED = 20260815
CONDITIONS = ("W0", "G1", "G2")
PRIMARY_CONDITION = "G2"
BASELINE = "W0"
TARGET_SHAPES = {"structured", "flat"}
NEGATIVE_CONTROL_SHAPES = {"short", "monolithic"}


def _query_metrics(topic: dict, query: dict, condition: str) -> dict:
    hits = rank_objects(topic["documents"], query["query"], condition)
    top5 = hits[:TOP_K_PRIMARY]
    top8 = hits[:TOP_K_SECONDARY]
    required = query["required_doc_ids"]
    signals = query["required_signals"]

    def recall(hits_subset):
        ids = {hit.doc_id for hit in hits_subset}
        return sum(doc_id in ids for doc_id in required) / len(required)

    ranks = {hit.doc_id: idx + 1 for idx, hit in enumerate(hits)}
    required_rr = sum((1.0 / ranks[doc_id]) if doc_id in ranks else 0.0 for doc_id in required) / len(required)
    top5_context = "\n".join(hit.context_text for hit in top5)
    signal_recall = sum(signal in top5_context for signal in signals) / len(signals)
    top1_lure = bool(hits and "LURE_" in hits[0].context_text)
    duplicate_final_objects = len({hit.object_id for hit in top5}) != len(top5)
    return {
        "topic_id": topic["topic_id"],
        "shape": topic["shape"],
        "query_id": query["query_id"],
        "query_class": query["query_class"],
        "condition": condition,
        "required_object_recall_at5": recall(top5),
        "required_object_recall_at8": recall(top8),
        "required_object_mrr": required_rr,
        "signal_recall_at5": signal_recall,
        "all_required_at5": recall(top5) == 1.0,
        "top1_lure": top1_lure,
        "context_chars_at5": sum(len(hit.context_text) for hit in top5),
        "duplicate_final_object": duplicate_final_objects,
        "top5": [
            {
                "rank": rank,
                "doc_id": hit.doc_id,
                "object_id": hit.object_id,
                "source_ids": list(hit.source_ids),
                "score": hit.score,
                "locator": hit.unit.locator,
            }
            for rank, hit in enumerate(top5, 1)
        ],
    }


def _topic_metric(rows: list[dict], metric: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["topic_id"]].append(float(row[metric]))
    return {topic: statistics.mean(values) for topic, values in grouped.items()}


def _paired_bootstrap(rows: list[dict], metric: str, *, shapes: set[str] | None = None) -> dict:
    by_condition = {condition: [] for condition in (BASELINE, PRIMARY_CONDITION)}
    for condition in by_condition:
        selected = [
            row for row in rows
            if row["condition"] == condition and (shapes is None or row["shape"] in shapes)
        ]
        by_condition[condition] = _topic_metric(selected, metric)
    topics = sorted(set(by_condition[BASELINE]) & set(by_condition[PRIMARY_CONDITION]))
    diffs = [by_condition[PRIMARY_CONDITION][topic] - by_condition[BASELINE][topic] for topic in topics]
    point = statistics.mean(diffs) if diffs else 0.0
    rng = random.Random(BOOTSTRAP_SEED)
    reps = []
    for _ in range(BOOTSTRAP_REPS):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        reps.append(statistics.mean(sample))
    reps.sort()
    lo = reps[int(0.025 * BOOTSTRAP_REPS)]
    hi = reps[min(BOOTSTRAP_REPS - 1, int(0.975 * BOOTSTRAP_REPS))]
    return {"topics": len(topics), "difference": point, "ci95": [lo, hi]}


def _mean(rows: list[dict], condition: str, metric: str, shapes: set[str] | None = None) -> float:
    values = [
        float(row[metric]) for row in rows
        if row["condition"] == condition and (shapes is None or row["shape"] in shapes)
    ]
    return statistics.mean(values)


def analyze(split: str) -> dict:
    if split != "heldout":
        raise ValueError("official_scoring_requires_heldout_split")
    corpus = build_corpus(split)
    rows = []
    provenance = {}
    index = {}
    for condition in CONDITIONS:
        for topic in corpus["topics"]:
            provenance.setdefault(condition, True)
            provenance[condition] = provenance[condition] and provenance_reversible(topic["documents"], condition)
            stats = index_stats(topic["documents"], condition)
            agg = index.setdefault(condition, {"units": 0, "indexed_chars": 0, "source_chars": 0})
            for key in agg:
                agg[key] += stats[key]
            for query in topic["queries"]:
                rows.append(_query_metrics(topic, query, condition))

    primary = {
        metric: _paired_bootstrap(rows, metric, shapes=TARGET_SHAPES)
        for metric in ("required_object_recall_at5", "required_object_mrr", "signal_recall_at5")
    }
    controls = {
        metric: _paired_bootstrap(rows, metric, shapes=NEGATIVE_CONTROL_SHAPES)
        for metric in ("required_object_recall_at5", "required_object_mrr", "signal_recall_at5")
    }
    cross_boundary_topics = {
        topic["topic_id"] for topic in corpus["topics"]
        if topic["shape"] == "flat" and topic["cross_boundary_decision"]
    }
    cross_boundary = [
        row for row in rows
        if row["topic_id"] in cross_boundary_topics and row["query_class"] == "decision_history"
    ]
    cross_g1 = statistics.mean(float(r["required_object_recall_at5"]) for r in cross_boundary if r["condition"] == "G1")
    cross_g2 = statistics.mean(float(r["required_object_recall_at5"]) for r in cross_boundary if r["condition"] == "G2")

    w0_chars = index["W0"]["indexed_chars"]
    g2_multiplier = index["G2"]["indexed_chars"] / w0_chars
    no_duplicates = not any(row["duplicate_final_object"] for row in rows)

    gate_checks = {
        "target_recall_gain_ge_0_15": primary["required_object_recall_at5"]["difference"] >= 0.15,
        "target_recall_ci_lower_gt_0": primary["required_object_recall_at5"]["ci95"][0] > 0.0,
        "target_mrr_gain_ge_0_10": primary["required_object_mrr"]["difference"] >= 0.10,
        "negative_control_recall_regression_no_worse_than_0_05": controls["required_object_recall_at5"]["difference"] >= -0.05,
        "provenance_reversible_all": all(provenance.values()),
        "final_duplicate_object_rate_zero": no_duplicates,
        "g2_indexed_char_multiplier_le_3_0": g2_multiplier <= 3.0,
        "g2_cross_boundary_recall_ge_g1_plus_0_10": cross_g2 - cross_g1 >= 0.10,
    }
    gate = "SURVIVES_DETERMINISTIC_GATE" if all(gate_checks.values()) else "DOES_NOT_SURVIVE_DETERMINISTIC_GATE"

    summary = {
        "format": "llm-wiki-e014-stage-a-results-v0",
        "model_calls": 0,
        "split": split,
        "corpus_sha256": corpus_sha256(corpus),
        "topic_count": corpus["topic_count"],
        "query_count": corpus["query_count"],
        "conditions": list(CONDITIONS),
        "primary_comparison": "G2-W0",
        "primary_target_shapes": sorted(TARGET_SHAPES),
        "primary": primary,
        "negative_controls": controls,
        "means": {
            condition: {
                "all_recall_at5": _mean(rows, condition, "required_object_recall_at5"),
                "target_recall_at5": _mean(rows, condition, "required_object_recall_at5", TARGET_SHAPES),
                "negative_control_recall_at5": _mean(rows, condition, "required_object_recall_at5", NEGATIVE_CONTROL_SHAPES),
                "target_mrr": _mean(rows, condition, "required_object_mrr", TARGET_SHAPES),
                "target_signal_recall_at5": _mean(rows, condition, "signal_recall_at5", TARGET_SHAPES),
                "target_top1_lure_rate": _mean(rows, condition, "top1_lure", TARGET_SHAPES),
                "mean_context_chars_at5": _mean(rows, condition, "context_chars_at5"),
            }
            for condition in CONDITIONS
        },
        "cross_boundary_flat_decision": {
            "queries": sum(1 for r in cross_boundary if r["condition"] == "W0"),
            "G1_recall_at5": cross_g1,
            "G2_recall_at5": cross_g2,
        },
        "provenance_reversible": provenance,
        "index": {
            condition: {
                **stats,
                "indexed_char_multiplier_vs_W0": stats["indexed_chars"] / w0_chars,
            }
            for condition, stats in index.items()
        },
        "gate_checks": gate_checks,
        "gate": gate,
        "cautions": [
            "synthetic held-out mechanism benchmark",
            "author-designed lexical lure mechanism",
            "development corpus was used to select G2 and is excluded from evidence",
            "no model answer quality measured in Stage A",
            "G2 parameters frozen before held-out scoring and must not be retuned from these results",
            "architecture adoption still requires non-tuned corpus or realistic-workload confirmation",
        ],
    }
    return {"summary": summary, "rows": rows}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=("heldout",), default="heldout")
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = analyze(args.split)
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    s = result["summary"]
    print("E014-STAGE-A-HANDOFF-v0")
    print(f"modelCalls={s['model_calls']} split={s['split']} topics={s['topic_count']} queries={s['query_count']} corpusSha={s['corpus_sha256']}")
    for condition in CONDITIONS:
        m = s["means"][condition]
        print(
            f"{condition} targetRecall5={m['target_recall_at5']:.3f} targetMRR={m['target_mrr']:.3f} "
            f"targetSignal5={m['target_signal_recall_at5']:.3f} top1Lure={m['target_top1_lure_rate']:.3f} "
            f"indexCharsX={s['index'][condition]['indexed_char_multiplier_vs_W0']:.3f}"
        )
    pcmp = s["primary"]["required_object_recall_at5"]
    print(f"paired G2-W0 targetRecall5={pcmp['difference']:+.3f}[{pcmp['ci95'][0]:+.3f},{pcmp['ci95'][1]:+.3f}]")
    mrr = s["primary"]["required_object_mrr"]
    print(f"paired G2-W0 targetMRR={mrr['difference']:+.3f}[{mrr['ci95'][0]:+.3f},{mrr['ci95'][1]:+.3f}]")
    cross = s["cross_boundary_flat_decision"]
    print(f"crossBoundary queries={cross['queries']} G1Recall5={cross['G1_recall_at5']:.3f} G2Recall5={cross['G2_recall_at5']:.3f}")
    print(f"provenanceReversible={all(s['provenance_reversible'].values())} duplicateObjectsZero={s['gate_checks']['final_duplicate_object_rate_zero']}")
    print(f"gate={s['gate']} freeform=none modelCalls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
