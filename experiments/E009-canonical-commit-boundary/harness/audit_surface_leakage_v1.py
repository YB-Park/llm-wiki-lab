#!/usr/bin/env python3
"""Post-freeze superficial-leakage audit for frozen E009A Corpus T-v1.

This diagnostic MUST NOT change the frozen corpus, verifier prompt, labels, risk tiers,
or policy semantics. It exists only to calibrate how much confidence to place in any
future verifier result.

The audit intentionally uses only candidate surface form. It reports:
- scalar-feature leave-one-scenario-group-out (LOSGO) logistic baseline;
- raw word TF-IDF LOSGO logistic baseline;
- scrubbed TF-IDF LOSGO baseline with source IDs and numbers normalized.

All hyperparameters are fixed in this file before scored verifier results are observed.
No hyperparameter search is performed.
"""

from __future__ import annotations

import difflib
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "corpus" / "cases.jsonl"

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_./-]*|\d+(?:\.\d+)?")
SOURCE_RE = re.compile(r"\[S\d+\]")
NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
TEMPORAL_RE = re.compile(
    r"\b(current|currently|previous|previously|former|formerly|before|after|since|until|"
    r"deprecated|supersed|histor|version|release|changed|change|corrected|correction|"
    r"valid|effective|now|later|earlier)\w*\b",
    re.I,
)
NEGATION_RE = re.compile(
    r"\b(no|not|never|none|without|unknown|uncertain|unresolved|disputed|conflict|"
    r"unsupported|cannot|can't|doesn't|didn't|isn't|wasn't)\b",
    re.I,
)

# Frozen diagnostic hyperparameters; do not tune after seeing verifier outcomes.
EPOCHS = 500
LEARNING_RATE = 0.12
L2 = 0.4


def load_rows():
    return [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]


def label(row) -> int:
    return 1 if row["gold_label"] == "safe_commit" else 0


def source_ids(text: str) -> set[str]:
    return set(SOURCE_RE.findall(text))


def diff_counts(previous: str, candidate: str) -> tuple[int, int]:
    prev = previous.split()
    cand = candidate.split()
    added = deleted = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=prev, b=cand, autojunk=False).get_opcodes():
        if tag in {"insert", "replace"}:
            added += j2 - j1
        if tag in {"delete", "replace"}:
            deleted += i2 - i1
    return added, deleted


def scalar_features(row) -> list[float]:
    prev = row["previous_state"]
    cand = row["candidate_state"]
    cb = len(cand.encode("utf-8"))
    pb = max(1, len(prev.encode("utf-8")))
    added, deleted = diff_counts(prev, cand)
    prev_tokens = max(1, len(prev.split()))
    cand_sources = source_ids(cand)
    prev_sources = source_ids(prev)
    evidence_sources = {f"[{item['source_id']}]" for item in row["new_evidence"]}
    return [
        float(cb),
        cb / pb,
        float(added),
        float(deleted),
        (added + deleted) / prev_tokens,
        float(len(cand_sources)),
        float(len(cand_sources - prev_sources)),
        float(len(evidence_sources - cand_sources)),
        float(len(TEMPORAL_RE.findall(cand))),
        float(len(NEGATION_RE.findall(cand))),
    ]


def tokenize(text: str, scrub: bool) -> list[str]:
    if scrub:
        text = SOURCE_RE.sub(" SRCID ", text)
        text = NUM_RE.sub(" NUM ", text)
    return [tok.lower() for tok in TOKEN_RE.findall(text)]


def build_tfidf(train_rows, test_rows, scrub: bool):
    train_tokens = [tokenize(r["candidate_state"], scrub) for r in train_rows]
    test_tokens = [tokenize(r["candidate_state"], scrub) for r in test_rows]
    n = len(train_tokens)
    df = Counter()
    for toks in train_tokens:
        df.update(set(toks))
    vocab = {tok: i for i, tok in enumerate(sorted(df))}
    idf = {tok: math.log((1 + n) / (1 + df[tok])) + 1.0 for tok in vocab}

    def vectorize(toks):
        counts = Counter(tok for tok in toks if tok in vocab)
        total = max(1, sum(counts.values()))
        vec = [0.0] * len(vocab)
        for tok, count in counts.items():
            vec[vocab[tok]] = (count / total) * idf[tok]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    return [vectorize(t) for t in train_tokens], [vectorize(t) for t in test_tokens]


def standardize(train_x, test_x):
    if not train_x:
        return train_x, test_x
    d = len(train_x[0])
    means = [sum(row[j] for row in train_x) / len(train_x) for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((row[j] - means[j]) ** 2 for row in train_x) / max(1, len(train_x) - 1)
        stds.append(math.sqrt(var) or 1.0)

    def z(row):
        return [(row[j] - means[j]) / stds[j] for j in range(d)]

    return [z(r) for r in train_x], [z(r) for r in test_x]


def sigmoid(z: float) -> float:
    if z >= 0:
        e = math.exp(-z)
        return 1.0 / (1.0 + e)
    e = math.exp(z)
    return e / (1.0 + e)


def fit_logistic(x, y):
    d = len(x[0]) if x else 0
    w = [0.0] * d
    b = 0.0
    n = max(1, len(x))
    for _ in range(EPOCHS):
        gw = [0.0] * d
        gb = 0.0
        for row, target in zip(x, y):
            p = sigmoid(sum(a * c for a, c in zip(w, row)) + b)
            err = p - target
            gb += err
            for j, value in enumerate(row):
                gw[j] += err * value
        for j in range(d):
            gw[j] = gw[j] / n + L2 * w[j]
            w[j] -= LEARNING_RATE * gw[j]
        b -= LEARNING_RATE * (gb / n)
    return w, b


def predict(model, x):
    w, b = model
    return [1 if sigmoid(sum(a * c for a, c in zip(w, row)) + b) >= 0.5 else 0 for row in x]


def losgo(rows, kind: str):
    groups = sorted({r["scenario_group"] for r in rows})
    correct = total = 0
    fully_correct_pairs = 0
    pair_count = 0
    predictions = []

    for group in groups:
        train = [r for r in rows if r["scenario_group"] != group]
        test = [r for r in rows if r["scenario_group"] == group]
        train_y = [label(r) for r in train]
        test_y = [label(r) for r in test]

        if kind == "scalar":
            train_x = [scalar_features(r) for r in train]
            test_x = [scalar_features(r) for r in test]
            train_x, test_x = standardize(train_x, test_x)
        elif kind == "tfidf_raw":
            train_x, test_x = build_tfidf(train, test, scrub=False)
        elif kind == "tfidf_scrubbed":
            train_x, test_x = build_tfidf(train, test, scrub=True)
        else:
            raise ValueError(kind)

        pred = predict(fit_logistic(train_x, train_y), test_x)
        fold_correct = sum(int(a == b) for a, b in zip(pred, test_y))
        correct += fold_correct
        total += len(test)
        fully_correct_pairs += int(fold_correct == len(test))
        pair_count += 1
        predictions.extend(zip((r["case_id"] for r in test), test_y, pred))

    return {
        "accuracy": correct / total,
        "correct": correct,
        "total": total,
        "fully_correct_pairs": fully_correct_pairs,
        "pair_count": pair_count,
        "predictions": predictions,
    }


def main():
    rows = load_rows()
    assert len(rows) == 40
    assert len({r["scenario_group"] for r in rows}) == 20

    print("E009A-POSTFREEZE-LEAKAGE-AUDIT-v1")
    print("role=interpretation-calibration frozen_corpus_unchanged=yes scored_verifier_results_used=no")
    print(f"hyperparams=epochs:{EPOCHS},lr:{LEARNING_RATE},l2:{L2} folds=leave-one-scenario-group-out")
    for kind in ("scalar", "tfidf_raw", "tfidf_scrubbed"):
        result = losgo(rows, kind)
        print(
            f"{kind} acc={result['accuracy']:.3f} correct={result['correct']}/{result['total']} "
            f"fullyCorrectPairs={result['fully_correct_pairs']}/{result['pair_count']}"
        )
    print("caution=surface_predictability_does_not_prove_model_shortcut;high_baseline_lowers_benchmark_evidence_grade")


if __name__ == "__main__":
    main()
