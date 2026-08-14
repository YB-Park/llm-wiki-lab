#!/usr/bin/env python3
"""Run the frozen Stage 1A analysis against A3 transport-reparsed logical results."""

from pathlib import Path
import analysis_stage1a as base

ROOT = Path(__file__).resolve().parent
A3 = ROOT / "runs" / "stage-1a-v0" / "logical-results.transport-a3.local.json"

if __name__ == "__main__":
    if not A3.exists():
        raise SystemExit("E011-A3-ANALYSIS reparse_results_missing run=reparse_stage1a_a3.py")
    print("E011-STAGE1A-A3-ANALYSIS-CONTEXT-v0")
    print("input=transport-a3 modelCalls=0 frozenAnalysisSemantics=yes originalResults=preserved")
    base.RESULTS = A3
    base.main()
