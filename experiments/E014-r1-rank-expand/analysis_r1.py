from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from generate_corpus import build_corpus, corpus_sha256
from retrieval_r1 import index_stats, provenance_reversible, rank_objects, ranking_identity

CONDITIONS = ("W0", "G1", "X1", "G2")
TARGET_SHAPES = {"structured", "flat_contained", "flat_cross"}
CROSS_SHAPES = {"flat_cross"}
NEGATIVE_SHAPES = {"short", "monolithic"}
TOP_K = 5
TOP_K_SECONDARY = 8
BOOTSTRAP_REPS = 20000
BOOTSTRAP_SEED = 20260824


def query_metrics(topic: dict, query: dict, condition: str) -> dict:
    hits = rank_objects(topic["documents"], query["query"], condition)
    top5 = hits[:TOP_K]
    top8 = hits[:TOP_K_SECONDARY]
    required = query["required_doc_ids"]
    required_signals = query["required_signals"]

    def object_recall(rows) -> float:
        ids = {hit.doc_id for hit in rows}
        return sum(doc_id in ids for doc_id in required) / len(required)

    ranks = {hit.doc_id: idx + 1 for idx, hit in enumerate(hits)}
    mrr = sum((1.0 / ranks[doc_id]) if doc_id in ranks else 0.0 for doc_id in required) / len(required)
    context = "\n".join(hit.context_text for hit in top5)
    signal_recall = sum(signal in context for signal in required_signals) / len(required_signals)
    duplicate_objects = len({hit.object_id for hit in top5}) != len(top5)

    return {
        "topic_id": topic["topic_id"],
        "shape": topic["shape"],
        "query_id": query["query_id"],
        "query_class": query["query_class"],
        "condition": condition,
        "required_object_recall_at5": object_recall(top5),
        "required_object_recall_at8": object_recall(top8),
        "required_object_mrr": mrr,
        "required_signal_recall_at5": signal_recall,
        "all_required_signals_at5": signal_recall == 1.0,
        "context_chars_at5": sum(len(hit.context_text) for hit in top5),
        "duplicate_final_object": duplicate_objects,
        "top5": [
            {
                "rank": rank,
                "doc_id": hit.doc_id,
                "object_id": hit.object_id,
                "source_ids": list(hit.source_ids),
                "score": hit.score,
                "ranking_locator": hit.ranking_unit.locator,
                "context_locator": hit.context_locator,
            }
            for rank, hit in enumerate(top5, 1)
        ],
    }


def _topic_means(rows: list[dict], condition: str, metric: str, shapes: set[str]) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["condition"] != condition or row["shape"] not in shapes:
            continue
        grouped[row["topic_id"]].append(float(row[metric]))
    return {topic: statistics.mean(values) for topic, values in grouped.items()}


def paired_bootstrap(
    rows: list[dict],
    left: str,
    right: str,
    metric: str,
    shapes: set[str],
) -> dict:
    # Report right-left so comparisons read candidate - baseline.
    a = _topic_means(rows, left, metric, shapes)
    b = _topic_means(rows, right, metric, shapes)
    topics = sorted(set(a) & set(b))
    diffs = [b[topic] - a[topic] for topic in topics]
    point = statistics.mean(diffs)
    rng = random.Random(BOOTSTRAP_SEED)
    reps = []
    for _ in range(BOOTSTRAP_REPS):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        reps.append(statistics.mean(sample))
    reps.sort()
    lo = reps[int(0.025 * BOOTSTRAP_REPS)]
    hi = reps[min(BOOTSTRAP_REPS - 1, int(0.975 * BOOTSTRAP_REPS))]
    return {"topics": len(topics), "difference": point, "ci95": [lo, hi]}


def mean_metric(rows: list[dict], condition: str, metric: str, shapes: set[str]) -> float:
    values = [
        float(row[metric]) for row in rows
        if row["condition"] == condition and row["shape"] in shapes
    ]
    return statistics.mean(values)


def analyze() -> dict:
    corpus = build_corpus()
    rows: list[dict] = []
    provenance = {condition: True for condition in CONDITIONS}
    ranking_identity_all = True
    index = {condition: {"units": 0, "indexed_chars": 0, "source_chars": 0} for condition in CONDITIONS}

    for topic in corpus["topics"]:
        for condition in CONDITIONS:
            stats = index_stats(topic["documents"], condition)
            for key in index[condition]:
                index[condition][key] += stats[key]
        for query in topic["queries"]:
            ranking_identity_all = ranking_identity_all and ranking_identity(topic["documents"], query["query"])
            for condition in CONDITIONS:
                provenance[condition] = provenance[condition] and provenance_reversible(
                    topic["documents"], condition, query["query"]
                )
                rows.append(query_metrics(topic, query, condition))

    ranking_recall = paired_bootstrap(rows, "W0", "X1", "required_object_recall_at5", TARGET_SHAPES)
    ranking_mrr = paired_bootstrap(rows, "W0", "X1", "required_object_mrr", TARGET_SHAPES)
    expansion_signal = paired_bootstrap(rows, "G1", "X1", "required_signal_recall_at5", CROSS_SHAPES)
    negative_object = paired_bootstrap(rows, "W0", "X1", "required_object_recall_at5", NEGATIVE_SHAPES)
    negative_signal = paired_bootstrap(rows, "G1", "X1", "required_signal_recall_at5", NEGATIVE_SHAPES)

    cross_x1_signal = mean_metric(rows, "X1", "required_signal_recall_at5", CROSS_SHAPES)
    cross_g2_signal = mean_metric(rows, "G2", "required_signal_recall_at5", CROSS_SHAPES)
    cross_x1_chars = mean_metric(rows, "X1", "context_chars_at5", CROSS_SHAPES)
    cross_g2_chars = mean_metric(rows, "G2", "context_chars_at5", CROSS_SHAPES)

    w0_chars = index["W0"]["indexed_chars"]
    g1_chars = index["G1"]["indexed_chars"]
    x1_chars = index["X1"]["indexed_chars"]
    no_duplicates = not any(row["duplicate_final_object"] for row in rows)

    gate_checks = {
        "ranking_identity_x1_equals_g1": ranking_identity_all,
        "target_recall_gain_ge_0_15": ranking_recall["difference"] >= 0.15,
        "target_recall_ci_lower_gt_0": ranking_recall["ci95"][0] > 0.0,
        "target_mrr_gain_ge_0_10": ranking_mrr["difference"] >= 0.10,
        "cross_signal_gain_x1_g1_ge_0_30": expansion_signal["difference"] >= 0.30,
        "cross_signal_ci_lower_gt_0": expansion_signal["ci95"][0] > 0.0,
        "cross_signal_x1_noninferior_g2_0_05": cross_x1_signal >= cross_g2_signal - 0.05,
        "x1_index_exactly_g1_and_le_1_05_w0": x1_chars == g1_chars and x1_chars <= 1.05 * w0_chars,
        "negative_object_regression_no_worse_0_05": negative_object["difference"] >= -0.05,
        "negative_signal_regression_no_worse_0_05": negative_signal["difference"] >= -0.05,
        "provenance_reversible_all": all(provenance.values()),
        "duplicate_final_object_rate_zero": no_duplicates,
        "x1_cross_context_chars_le_1_10_g2": cross_x1_chars <= 1.10 * cross_g2_chars,
    }
    gate = "SURVIVES_R1_GATE" if all(gate_checks.values()) else "DOES_NOT_SURVIVE_R1_GATE"

    summary = {
        "format": "llm-wiki-e014-r1-results-v0",
        "model_calls": 0,
        "corpus_sha256": corpus_sha256(corpus),
        "topic_count": corpus["topic_count"],
        "query_count": corpus["query_count"],
        "conditions": list(CONDITIONS),
        "primary_ranking": {
            "recall_at5_x1_minus_w0": ranking_recall,
            "mrr_x1_minus_w0": ranking_mrr,
        },
        "primary_expansion": {
            "signal_recall_x1_minus_g1": expansion_signal,
            "cross_x1_signal_recall_at5": cross_x1_signal,
            "cross_g1_signal_recall_at5": mean_metric(rows, "G1", "required_signal_recall_at5", CROSS_SHAPES),
            "cross_g2_signal_recall_at5": cross_g2_signal,
            "cross_x1_context_chars_at5": cross_x1_chars,
            "cross_g2_context_chars_at5": cross_g2_chars,
        },
        "negative_controls": {
            "object_recall_x1_minus_w0": negative_object,
            "signal_recall_x1_minus_g1": negative_signal,
        },
        "means": {
            condition: {
                "target_recall_at5": mean_metric(rows, condition, "required_object_recall_at5", TARGET_SHAPES),
                "target_mrr": mean_metric(rows, condition, "required_object_mrr", TARGET_SHAPES),
                "target_signal_recall_at5": mean_metric(rows, condition, "required_signal_recall_at5", TARGET_SHAPES),
                "cross_signal_recall_at5": mean_metric(rows, condition, "required_signal_recall_at5", CROSS_SHAPES),
                "cross_context_chars_at5": mean_metric(rows, condition, "context_chars_at5", CROSS_SHAPES),
                "negative_object_recall_at5": mean_metric(rows, condition, "required_object_recall_at5", NEGATIVE_SHAPES),
            }
            for condition in CONDITIONS
        },
        "index": {
            condition: {
                **stats,
                "indexed_char_multiplier_vs_w0": stats["indexed_chars"] / w0_chars,
            }
            for condition, stats in index.items()
        },
        "ranking_identity_x1_g1": ranking_identity_all,
        "provenance_reversible": provenance,
        "gate_checks": gate_checks,
        "gate": gate,
        "cautions": [
            "fresh synthetic mechanism corpus designed after E014-v0 post-score hypothesis",
            "author-designed lexical lure and cross-boundary mechanisms",
            "no model answer quality measured",
            "no realistic user workload",
            "R1 may confirm mechanism but cannot justify default production rollout alone",
        ],
    }
    return {"summary": summary, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = result["summary"]
    print("E014-R1-HANDOFF-v0")
    print(f"modelCalls=0 topics={s['topic_count']} queries={s['query_count']} corpusSha={s['corpus_sha256']}")
    for condition in CONDITIONS:
        m = s["means"][condition]
        print(
            f"{condition} targetRecall5={m['target_recall_at5']:.3f} targetMRR={m['target_mrr']:.3f} "
            f"targetSignal5={m['target_signal_recall_at5']:.3f} crossSignal5={m['cross_signal_recall_at5']:.3f} "
            f"crossContextChars5={m['cross_context_chars_at5']:.1f} indexCharsX={s['index'][condition]['indexed_char_multiplier_vs_w0']:.3f}"
        )
    r = s["primary_ranking"]["recall_at5_x1_minus_w0"]
    print(f"paired X1-W0 targetRecall5={r['difference']:+.3f}[{r['ci95'][0]:+.3f},{r['ci95'][1]:+.3f}]")
    mrr = s["primary_ranking"]["mrr_x1_minus_w0"]
    print(f"paired X1-W0 targetMRR={mrr['difference']:+.3f}[{mrr['ci95'][0]:+.3f},{mrr['ci95'][1]:+.3f}]")
    sig = s["primary_expansion"]["signal_recall_x1_minus_g1"]
    print(f"paired X1-G1 crossSignal5={sig['difference']:+.3f}[{sig['ci95'][0]:+.3f},{sig['ci95'][1]:+.3f}]")
    print(f"rankingIdentity={s['ranking_identity_x1_g1']} provenance={all(s['provenance_reversible'].values())}")
    print(f"gate={s['gate']} freeform=none modelCalls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
