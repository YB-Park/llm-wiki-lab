#!/usr/bin/env python3
"""Deterministic prescore validation for E012. No model calls."""

from __future__ import annotations

from collections import Counter, defaultdict

import core
import generate_corpus as corpus


def main() -> None:
    docs, queries = corpus.generate()
    assert len(docs) == 432, len(docs)
    assert len(queries) == 108, len(queries)
    assert len({d["source_id"] for d in docs}) == 432
    assert len({q["query_id"] for q in queries}) == 108
    assert {q["class"] for q in queries} == {"current_exact", "current_synthesis", "decision_history"}
    assert {int(q["wave"]) for q in queries} == {0, 1, 2}

    topics = sorted({d["topic_id"] for d in docs})
    assert len(topics) == 12
    qgroup = defaultdict(list)
    for q in queries:
        qgroup[(q["topic_id"], int(q["wave"]))].append(q)

    doc_counts = Counter()
    required_total = 0
    forbidden_total = 0
    compiler_leak_checks = 0

    for topic in topics:
        for wave, expected_docs in ((0, 32), (1, 34), (2, 36)):
            scoped = corpus.docs_through_wave(docs, topic, wave)
            assert len(scoped) == expected_docs, (topic, wave, len(scoped))
            doc_counts[wave] += len(scoped)
            source_ids = {d["source_id"] for d in scoped}
            raw = core.raw_context(scoped).lower()
            qs = qgroup[(topic, wave)]
            assert len(qs) == 3
            assert {q["class"] for q in qs} == {"current_exact", "current_synthesis", "decision_history"}

            prompt = core.compiler_prompt(scoped)
            for q in qs:
                assert q["question"] not in prompt
                compiler_leak_checks += 1
                for signal in q["required_signals"]:
                    assert signal.lower() in raw, (topic, wave, q["query_id"], signal)
                    required_total += 1
                for sid in q["required_source_ids"]:
                    assert sid in source_ids, (topic, wave, q["query_id"], sid)
                for forbidden in q.get("forbidden_current_signals", []):
                    forbidden_total += 1
                    for required in q["required_signals"]:
                        assert forbidden.lower() != required.lower()
                        assert forbidden.lower() not in required.lower()
                        assert required.lower() not in forbidden.lower()

        w0 = corpus.docs_through_wave(docs, topic, 0)
        w1 = corpus.docs_through_wave(docs, topic, 1)
        w2 = corpus.docs_through_wave(docs, topic, 2)
        assert {d["source_id"] for d in w0} < {d["source_id"] for d in w1} < {d["source_id"] for d in w2}
        assert {d["source_id"] for d in w1 if d["wave"] == 1} == {f"{topic}-S33", f"{topic}-S34"}
        assert {d["source_id"] for d in w2 if d["wave"] == 2} == {f"{topic}-S35", f"{topic}-S36"}

    dsha = corpus.sha256_bytes(corpus.jsonl_bytes(docs))
    import json
    qbytes = (json.dumps(queries, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    qsha = corpus.sha256_bytes(qbytes)

    print("E012-PRESCORE-VALIDATION-v0")
    print(f"topics={len(topics)} docsFinal={len(docs)} queries={len(queries)} waves=3")
    print(f"waveDocTotals W0={doc_counts[0]} W1={doc_counts[1]} W2={doc_counts[2]}")
    print(f"requiredSignalsChecked={required_total} forbiddenCollisionChecks={forbidden_total} compilerLeakChecks={compiler_leak_checks}")
    print(f"docsSha={dsha}")
    print(f"queriesSha={qsha}")
    print("status=PASS modelCalls=0")


if __name__ == "__main__":
    main()
