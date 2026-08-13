#!/usr/bin/env python3
"""Run frozen E007 semantic evaluator with A2 answer-item containment policy."""

from __future__ import annotations

import evaluate_semantic
from answer_contract_a2 import parse_answer_batch_valid_only


def main() -> None:
    # Only primary-response parsing changes. Evaluator prompts/rubrics remain frozen.
    evaluate_semantic.parse_answer_batch = parse_answer_batch_valid_only
    evaluate_semantic.main()


if __name__ == "__main__":
    main()
