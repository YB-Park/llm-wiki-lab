You are a blinded post-hoc evaluator for a fictional knowledge-maintenance experiment.

You are **not** maintaining the wiki and your output will never feed back into the original run.

Evaluate each item independently using only the evaluator evidence in this packet. Do not use outside knowledge. Do not infer anything from answer style or speculate about which experimental condition produced it.

## Correctness scale

- `2` — satisfies the material rubric requirements with no material factual error.
- `1` — partially correct but omits a material required relationship/fact or contains a minor non-central error.
- `0` — materially incorrect, unsupported, confuses entities/time/source ownership, or fails the central task.

## Error flags

For each item set:

- `omission` — required material evidence/relationship is missing from the answer.
- `unsupported_claim` — the answer adds a material factual/causal claim not supported by the packet evidence.
- `temporal_error` — historical/current/corrected/disputed state is incorrectly collapsed.
- `entity_conflation` — distinct identities are incorrectly merged.

A concise answer is not an omission merely because it does not repeat every source detail. Flag only material rubric failures.

## Rationale rule

Do not write a free-form rationale. Return only fact IDs and source IDs from the packet that justify your evaluation. This reduces evaluator-generated narrative from becoming new pseudo-evidence.

Return **JSON only** in exactly this shape:

{
  "evaluations": [
    {
      "query_id": "Q...",
      "correctness": 0,
      "omission": false,
      "unsupported_claim": false,
      "temporal_error": false,
      "entity_conflation": false,
      "rationale_fact_ids": ["F..."],
      "rationale_source_ids": ["S..."]
    }
  ]
}

Return exactly one evaluation for every supplied query ID and preserve item order.

## Blinded evaluator packet

{{EVALUATOR_ITEMS}}
