#!/usr/bin/env python3
"""Run the frozen E009A verifier block and deterministically replay A0-A4 policies."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from copilot_cli import run_prompt
from telemetry import aggregate
from verifier_contract import parse_judgment

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "cases.jsonl"
PLAN = ROOT / "run-plan-v0.json"
PROMPT = ROOT / "prompts" / "transition-verifier.md"
RUN_ROOT = ROOT / "runs" / "stage-a-v0"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases() -> dict[str, dict[str, Any]]:
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["case_id"]: row for row in rows}


def render_evidence(items: list[dict[str, str]]) -> str:
    return "\n\n".join(f"### {row['source_id']}\n{row['text']}" for row in items)


def render_prompt(case: dict[str, Any]) -> str:
    # Deliberately construct the prompt from the allow-listed semantic fields only.
    # Do not serialize the complete case object: it contains evaluator-only gold metadata.
    text = PROMPT.read_text(encoding="utf-8")
    values = {
        "PREVIOUS_STATE": case["previous_state"],
        "NEW_EVIDENCE": render_evidence(case["new_evidence"]),
        "CANDIDATE_STATE": case["candidate_state"],
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    if "{{" in text or "}}" in text:
        raise ValueError("unresolved verifier prompt placeholder")
    return text


def call_name(seq: int, case_id: str, pass_no: int) -> str:
    return f"{seq:03d}-{case_id}-p{pass_no}"


def judgment_path(call_dir: Path) -> Path:
    return call_dir / "judgment.json"


def run_calls(*, model: str) -> None:
    plan = load_json(PLAN)
    cases = load_cases()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)

    for entry in plan["calls"]:
        seq = int(entry["sequence"])
        case_id = str(entry["case_id"])
        pass_no = int(entry["pass"])
        name = call_name(seq, case_id, pass_no)
        call_dir = RUN_ROOT / "calls" / name

        if judgment_path(call_dir).exists():
            print(f"SKIP seq={seq} complete")
            continue
        if call_dir.exists():
            raise SystemExit(
                f"E009A-STOP incomplete_call seq={seq} synthetic_case={case_id} pass={pass_no} "
                "preserve_local_artifact=yes"
            )

        prompt = render_prompt(cases[case_id])
        result = run_prompt(prompt=prompt, model=model, run_dir=call_dir)
        parsed = parse_judgment(str(result["response"]))
        payload = {
            "sequence": seq,
            "case_id": case_id,
            "pass": pass_no,
            "valid": bool(parsed["valid"]),
            "decision": parsed.get("decision"),
            "violations": list(parsed.get("violations", [])),
            "issue_count": int(parsed.get("issue_count", 0) or 0),
            "issue_counts": parsed.get("issue_counts", {}),
            "report": parsed.get("report"),
        }
        judgment_path(call_dir).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"DONE seq={seq} judgment={'valid' if payload['valid'] else 'invalid'}")


def index_calls(plan: dict[str, Any]) -> dict[tuple[str, int], Path]:
    result = {}
    for entry in plan["calls"]:
        key = (str(entry["case_id"]), int(entry["pass"]))
        result[key] = RUN_ROOT / "calls" / call_name(int(entry["sequence"]), key[0], key[1])
    return result


def load_judgments(plan: dict[str, Any]) -> tuple[dict[tuple[str, int], dict[str, Any]], dict[tuple[str, int], Path]]:
    dirs = index_calls(plan)
    out = {}
    for key, call_dir in dirs.items():
        path = judgment_path(call_dir)
        if not path.exists():
            raise SystemExit(f"E009A-STOP missing_judgment synthetic_case={key[0]} pass={key[1]}")
        out[key] = load_json(path)
    return out, dirs


def accepted(j: dict[str, Any]) -> bool:
    return bool(j.get("valid")) and j.get("decision") == "accept"


def policy_action(policy: str, case: dict[str, Any], p1: dict[str, Any], p2: dict[str, Any]) -> dict[str, Any]:
    gold_safe = case["gold_label"] == "safe_commit"
    if policy == "A0":
        return {"final": "commit", "review": False, "auto_commit": True}
    if policy == "A1":
        ok = accepted(p1)
        return {"final": "commit" if ok else "quarantine", "review": False, "auto_commit": ok}
    if policy == "A2":
        ok = accepted(p1) and accepted(p2)
        return {"final": "commit" if ok else "quarantine", "review": False, "auto_commit": ok}
    if policy == "A3":
        if case["risk"] == "low" and accepted(p1):
            return {"final": "commit", "review": False, "auto_commit": True}
        return {"final": "commit" if gold_safe else "quarantine", "review": True, "auto_commit": False}
    if policy == "A4":
        return {"final": "commit" if gold_safe else "quarantine", "review": True, "auto_commit": False}
    raise ValueError(policy)


def verifier_confusion(cases: dict[str, dict[str, Any]], judgments: dict[tuple[str, int], dict[str, Any]], pass_no: int) -> dict[str, Any]:
    c = Counter()
    class_errors = Counter()
    for case_id, case in cases.items():
        j = judgments[(case_id, pass_no)]
        safe = case["gold_label"] == "safe_commit"
        invalid = not j.get("valid")
        if invalid:
            c["invalid"] += 1
        if safe:
            if accepted(j):
                c["safe_accept"] += 1
            else:
                c["safe_flag"] += 1
                class_errors[case["primary_class"]] += 1
        else:
            if accepted(j):
                c["unsafe_accept"] += 1
                class_errors[case["primary_class"]] += 1
            else:
                c["unsafe_flag"] += 1
    return {**c, "class_errors": dict(class_errors)}


def policy_metrics(policy: str, cases: dict[str, dict[str, Any]], judgments: dict[tuple[str, int], dict[str, Any]]) -> dict[str, Any]:
    c = Counter()
    by_class = defaultdict(Counter)
    for case_id, case in cases.items():
        action = policy_action(policy, case, judgments[(case_id, 1)], judgments[(case_id, 2)])
        safe = case["gold_label"] == "safe_commit"
        c["review"] += int(action["review"])
        c["quarantine"] += int(action["final"] == "quarantine")
        if safe:
            c["safe_total"] += 1
            if action["auto_commit"]:
                c["safe_auto_commit"] += 1
            if action["final"] != "commit":
                c["safe_blocked"] += 1
        else:
            c["unsafe_total"] += 1
            if action["final"] == "commit":
                c["unsafe_commit"] += 1
                by_class[case["primary_class"]]["unsafe_commit"] += 1
    return {**c, "by_class": {k: dict(v) for k, v in by_class.items()}}


def policy_telemetry(policy: str, dirs: dict[tuple[str, int], Path], cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if policy in {"A0", "A4"}:
        selected: list[Path] = []
    elif policy in {"A1", "A3"}:
        selected = [dirs[(case_id, 1)] for case_id in sorted(cases)]
    elif policy == "A2":
        selected = [dirs[(case_id, p)] for case_id in sorted(cases) for p in (1, 2)]
    else:
        raise ValueError(policy)
    return aggregate(selected)


def compact_num(value: Any) -> str:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return "0"
    return str(int(x)) if x.is_integer() else f"{x:.3f}".rstrip("0").rstrip(".")


def build_report() -> tuple[dict[str, Any], str]:
    plan = load_json(PLAN)
    cases = load_cases()
    judgments, dirs = load_judgments(plan)

    v1 = verifier_confusion(cases, judgments, 1)
    v2 = verifier_confusion(cases, judgments, 2)
    disagreements = sum(
        int((judgments[(case_id, 1)].get("valid"), judgments[(case_id, 1)].get("decision")) !=
            (judgments[(case_id, 2)].get("valid"), judgments[(case_id, 2)].get("decision")))
        for case_id in cases
    )

    policies = {}
    for policy in ("A0", "A1", "A2", "A3", "A4"):
        policies[policy] = {
            "outcomes": policy_metrics(policy, cases, judgments),
            "telemetry": policy_telemetry(policy, dirs, cases),
        }

    corpus_hash = hashlib.sha256(CORPUS.read_bytes()).hexdigest()[:16]
    report = {
        "format": "E009A-RESULT-v0",
        "corpus_hash": corpus_hash,
        "model": plan["model"],
        "case_count": len(cases),
        "verifier": {"pass1": v1, "pass2": v2, "pass_disagreements": disagreements},
        "policies": policies,
    }

    lines = [
        "E009A-SAFE-HANDOFF-v0",
        f"cases=40 safe=20 unsafe=20 model={plan['model']} corpus={corpus_hash}",
        f"p1 safeAccept={v1.get('safe_accept',0)}/20 safeFlag={v1.get('safe_flag',0)}/20 unsafeFlag={v1.get('unsafe_flag',0)}/20 unsafeAccept={v1.get('unsafe_accept',0)}/20 invalid={v1.get('invalid',0)}",
        f"p2 safeAccept={v2.get('safe_accept',0)}/20 safeFlag={v2.get('safe_flag',0)}/20 unsafeFlag={v2.get('unsafe_flag',0)}/20 unsafeAccept={v2.get('unsafe_accept',0)}/20 invalid={v2.get('invalid',0)} disagree={disagreements}/40",
    ]
    for policy in ("A0", "A1", "A2", "A3", "A4"):
        o = policies[policy]["outcomes"]
        t = policies[policy]["telemetry"]
        lines.append(
            f"{policy} unsafeCommit={o.get('unsafe_commit',0)}/20 safeAuto={o.get('safe_auto_commit',0)}/20 "
            f"safeBlocked={o.get('safe_blocked',0)}/20 review={o.get('review',0)}/40 quarantine={o.get('quarantine',0)}/40 "
            f"calls={t['call_count']} in={compact_num(t['input_tokens'])} out={compact_num(t['output_tokens'])} wall={compact_num(t['wall_seconds'])}"
        )
    lines.append("detail=local-only freeform=none paths=none")
    return report, "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    plan = load_json(PLAN)
    model = args.model or plan["model"]
    if model != plan["model"]:
        raise SystemExit(f"model mismatch: frozen={plan['model']} requested={model}")

    if not args.report_only:
        run_calls(model=model)

    report, handoff = build_report()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    (RUN_ROOT / "result.local.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (RUN_ROOT / "safe-handoff.txt").write_text(handoff, encoding="utf-8")
    print(handoff, end="")


if __name__ == "__main__":
    main()
