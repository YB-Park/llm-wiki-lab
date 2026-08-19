from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
BM25_K1 = 1.5
BM25_B = 0.75


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(text)]


def load_sources() -> list[dict]:
    rows = []
    for line in (CORPUS / "sources.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def canonical_question_hash(row: dict) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_corpus(sources: list[dict], questions_doc: dict, manifest: dict) -> None:
    questions = questions_doc["questions"]
    assert manifest["experiment"] == "E023"
    assert manifest["gate"] == "G1_retrieval_composition"
    assert manifest["source_count"] == 18 == len(sources)
    assert manifest["question_count"] == 10 == len(questions)

    source_ids = [row["source_id"] for row in sources]
    question_ids = [row["question_id"] for row in questions]
    assert len(source_ids) == len(set(source_ids))
    assert len(question_ids) == len(set(question_ids))
    assert source_ids == [f"S{i:03d}" for i in range(1, 19)]
    assert question_ids == [f"Q{i:03d}" for i in range(1, 11)]

    family_counts = dict(sorted(Counter(row["family"] for row in sources).items()))
    assert family_counts == manifest["family_counts"]
    assert family_counts == {
        "decision_rationale": 4,
        "identity_attribution": 6,
        "incident_temporal": 4,
        "vendor_constraint": 4,
    }

    source_set = set(source_ids)
    for row in sources:
        assert isinstance(row["text"], str) and row["text"].strip()
        observed = hashlib.sha256(row["text"].encode("utf-8")).hexdigest()
        assert observed == manifest["source_text_sha256"][row["source_id"]]

    for row in questions:
        required = row["required_sources"]
        forbidden = row["forbidden_conflation_sources"]
        assert required and len(required) == len(set(required))
        assert set(required) <= source_set
        assert set(forbidden) <= source_set
        assert not (set(required) & set(forbidden))
        assert row["answer_requirements"]
        observed = canonical_question_hash(row)
        assert observed == manifest["question_spec_sha256"][row["question_id"]]


def bm25_ranking(sources: list[dict], query: str) -> list[tuple[str, float]]:
    docs = {row["source_id"]: tokenize(row["text"]) for row in sources}
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    document_count = len(docs)
    avgdl = sum(len(tokens) for tokens in docs.values()) / document_count
    dfs: Counter[str] = Counter()
    for tokens in docs.values():
        dfs.update(set(tokens))

    scored: list[tuple[str, float]] = []
    for source_id, tokens in docs.items():
        tf = Counter(tokens)
        dl = len(tokens)
        score = 0.0
        for term in query_tokens:
            if tf[term] == 0:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (document_count - df + 0.5) / (df + 0.5))
            denom = tf[term] + BM25_K1 * (1 - BM25_B + BM25_B * dl / avgdl)
            score += idf * (tf[term] * (BM25_K1 + 1)) / denom
        if score > 0:
            scored.append((source_id, score))
    scored.sort(key=lambda row: (-row[1], row[0]))
    return scored


def retrieval_report(sources: list[dict], questions: list[dict]) -> dict:
    rows = []
    for question in questions:
        ranking = bm25_ranking(sources, question["question"])
        ordered_ids = [source_id for source_id, _ in ranking]
        ranks = {
            source_id: (ordered_ids.index(source_id) + 1 if source_id in ordered_ids else None)
            for source_id in question["required_sources"]
        }
        top5 = set(ordered_ids[:5])
        required = set(question["required_sources"])
        forbidden = set(question["forbidden_conflation_sources"])
        rows.append(
            {
                "question_id": question["question_id"],
                "family": question["family"],
                "top5": ordered_ids[:5],
                "required_source_ranks": ranks,
                "required_recall_at_5": len(required & top5) / len(required),
                "forbidden_in_top5": sorted(forbidden & top5),
            }
        )
    return {
        "experiment": "E023",
        "phase": "zero_model_lexical_diagnostic",
        "model_calls": 0,
        "note": (
            "Diagnostic only. Low lexical recall identifies retrieval difficulty; "
            "it is not a semantic FAIL and does not justify persistence."
        ),
        "questions": rows,
    }


def main() -> int:
    sources = load_sources()
    questions_doc = json.loads((CORPUS / "questions.json").read_text(encoding="utf-8"))
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    validate_corpus(sources, questions_doc, manifest)
    report = retrieval_report(sources, questions_doc["questions"])
    print("E023 corpus integrity: PASS")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
