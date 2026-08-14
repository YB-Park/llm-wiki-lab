#!/usr/bin/env python3
"""Run frozen E011 Stage 1A analysis against remote-v1 JSONL results."""

from pathlib import Path

import analysis_stage1a as base
import remote_instrumentation_v1 as remote

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "stage-1a-remote-v1"
RESULTS = RUN / "logical-results.local.json"


def main():
    if not RESULTS.exists():
        raise SystemExit("E011-REMOTE-ANALYSIS scored_results_missing")
    remote.configure(RUN, 30, 1000)
    base.RUN = RUN
    base.RESULTS = RESULTS
    base.inst = remote
    print("E011-STAGE1A-REMOTE-ANALYSIS-CONTEXT-v1")
    print("transport=copilot-jsonl modelCalls=0 frozenAnalysisSemantics=yes telemetry=invoke_agent_dedup")
    base.main()

    metas = list(RUN.rglob("remote-meta.json"))
    rows = [remote.collect_call(p.parent) for p in metas]
    print("E011-STAGE1A-REMOTE-COST-HANDOFF-v1")
    print(
        f"actualModelCalls={len(rows)} estimatedCredits={sum(r['estimated_ai_credits'] for r in rows):.3f} "
        f"otelCostRaw={sum(r['otel_cost_raw'] for r in rows):.3f} "
        f"inputTokens={int(sum(r['input_tokens'] for r in rows))} "
        f"outputTokens={int(sum(r['output_tokens'] for r in rows))} "
        f"cacheReadTokens={int(sum(r['cache_read_tokens'] for r in rows))}"
    )
    print("pricingEstimate=luna-default-or-long-tier creditUnitUSD=0.01 rawContent=artifact-only")


if __name__ == "__main__":
    main()
