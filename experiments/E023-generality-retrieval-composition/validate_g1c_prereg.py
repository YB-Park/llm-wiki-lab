from __future__ import annotations

import importlib.util
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "authority-sufficiency-v0"
ANCHORS = PKG / "anchors.jsonl"
QUESTIONS = PKG / "questions.json"
CONTRACT = PKG / "contract.json"
AUTH_VALIDATOR = ROOT / "validate_authority_sufficiency.py"

TOKEN_RE = re.compile(r"[0-9a-zA-Z_가-힣]+", re.UNICODE)
BM25_K1 = 1.5
BM25_B = 0.75
TOP_K = 5

EXPECTED = {
    "AQ001": {
        "top5": ["A005", "A002", "A001", "A006", "A004"],
        "status": "INSUFFICIENT_AUTHORITY",
    },
    "AQ002": {
        "top5": ["A005", "A002", "A004", "A001", "A003"],
        "status": "SUFFICIENT_WITH_CONFLATION_RISK",
    },
    "AQ003": {
        "top5": ["A007", "A008", "A006", "A004", "A013"],
        "status": "SUFFICIENT_CLEAN",
    },
    "AQ004": {
        "top5": ["A009", "A011", "A010", "A012", "A014"],
        "status": "SUFFICIENT_CLEAN",
    },
    "AQ005": {
        "top5": ["A012", "A009", "A010", "A011", "A005"],
        "status": "SUFFICIENT_CLEAN",
    },
    "AQ006": {
        "top5": ["A014", "A015", "A013", "A003", "A007"],
        "status": "SUFFICIENT_CLEAN",
    },
}


def _load_authority_module():
    spec = importlib.util.spec_from_file_location("e023_authority", AUTH_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("authority_validator_import_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUTH = _load_authority_module()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(text)]


def bm25_ranking(anchors: list[dict[str, Any]], query: str) -> list[tuple[str, float]]:
    docs = {row["anchor_id"]: tokenize(row["text"]) for row in anchors}
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    count = len(docs)
    avgdl = sum(len(tokens) for tokens in docs.values()) / count
    dfs: Counter[str] = Counter()
    for tokens in docs.values():
        dfs.update(set(tokens))
    scored = []
    for anchor_id, tokens in docs.items():
        tf = Counter(tokens)
        dl = len(tokens)
        score = 0.0
        for term in query_tokens:
            if tf[term] == 0:
                continue
            df = dfs[term]
            idf = math.log(1.0 + (count - df + 0.5) / (df + 0.5))
            denom = tf[term] + BM25_K1 * (1 - BM25_B + BM25_B * dl / avgdl)
            score += idf * (tf[term] * (BM25_K1 + 1)) / denom
        if score > 0:
            scored.append((anchor_id, score))
    scored.sort(key=lambda row: (-row[1], row[0]))
    return scored


def main() -> int:
    anchors = load_jsonl(ANCHORS)
    questions_doc = load_json(QUESTIONS)
    contract = load_json(CONTRACT)

    assert contract["status"] == "PROSPECTIVE_ZERO_MODEL_EVALUATION_CONTRACT"
    assert questions_doc["status"] == "SEPARATED_PROSPECTIVE_MATERIAL_NO_MODEL_ANSWERS"

    question_by_id = {
        row["question_id"]: row
        for row in questions_doc["questions"]
    }
    assert sorted(question_by_id) == [f"AQ00{i}" for i in range(1, 7)]
    assert set(question_by_id) == set(EXPECTED) == set(contract["questions"])

    rows = {}
    status_counts: Counter[str] = Counter()
    for question_id in sorted(question_by_id):
        ranking = bm25_ranking(anchors, question_by_id[question_id]["question"])
        top5 = [anchor_id for anchor_id, _ in ranking[:TOP_K]]
        evaluation = AUTH.evaluate_context(contract["questions"][question_id], top5)
        expected = EXPECTED[question_id]
        assert top5 == expected["top5"], (question_id, top5, expected["top5"])
        assert evaluation["status"] == expected["status"], (question_id, evaluation, expected)
        rows[question_id] = {
            "top5": top5,
            "status": evaluation["status"],
            "missing_clause_ids": evaluation["missing_clause_ids"],
            "forbidden_conflation_anchor_ids_present": evaluation[
                "forbidden_conflation_anchor_ids_present"
            ],
        }
        status_counts[evaluation["status"]] += 1

    assert status_counts == Counter({
        "SUFFICIENT_CLEAN": 4,
        "SUFFICIENT_WITH_CONFLATION_RISK": 1,
        "INSUFFICIENT_AUTHORITY": 1,
    }), status_counts
    assert "identity_bridge" in rows["AQ001"]["missing_clause_ids"]
    assert rows["AQ001"]["forbidden_conflation_anchor_ids_present"] == ["A004"]
    assert rows["AQ002"]["forbidden_conflation_anchor_ids_present"] == ["A004"]
    assert all(
        rows[qid]["status"] == "SUFFICIENT_CLEAN"
        for qid in ["AQ003", "AQ004", "AQ005", "AQ006"]
    )

    output = {
        "model_calls": 0,
        "target_question_ids": sorted(question_by_id),
        "baseline_top_k": TOP_K,
        "baseline_context_status_counts": dict(sorted(status_counts.items())),
        "baseline": rows,
        "candidate_structure": (
            "reuse_G1b_evidence_follow_initial_top5_then_0_to_2_followup_BM25_queries_"
            "then_selector_max5_then_same_composer"
        ),
        "max_semantic_calls_if_later_executed": 24,
        "semantic_calls_authorized_on_this_pr": False,
        "g2_persistence_authorized": False,
        "g3_identity_routing_authorized": False,
    }

    print("E023 G1c prereg baseline validation: PASS")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
