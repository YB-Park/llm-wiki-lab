# E007 Semantic Evaluator Profile v0

Status: **frozen before first scored Family N run**
Date: 2026-08-12

## Purpose

Define a reproducible post-hoc evaluator without turning model selection into another major E007 variable.

Semantic evaluation never feeds back into C0–C4 maintenance.

## Evaluator engine

- model: `gpt-5.6-luna`
- adapter: same isolated Copilot CLI adapter used by the experiment
- passes: **2 independent blinded passes** per semantic evaluation packet
- condition identity: hidden
- maintenance prompt/history: hidden
- token/cost information: hidden

Using the same model family as the experiment is a known limitation. The first block prioritizes controlled, inexpensive, reproducible evaluation over adding another model/runtime variable.

If semantic evaluation materially determines a headline architectural conclusion, replicate the relevant subset later with a different evaluator model/runtime before promoting the conclusion to a broad design principle.

## Items evaluated semantically

Primary Layer C items are the 10 queries in:

- `global_synthesis`,
- `multi_hop`.

State-integrity semantic audits are separate packets and follow `analysis-protocol-v0.md`.

## Time-safe evaluator packet

For a query first asked after wave `W`, the evaluator may receive only evidence that was available through `W`.

Packet contents:

- query ID and question,
- candidate answer/source IDs/uncertainty,
- frozen query rubric,
- required evaluator fact records whose `known_from_wave <= W`,
- authoritative raw sources available through `W` as needed for unsupported-claim checking.

Do **not** expose future source waves or future facts merely because they exist in the final evaluator manifest.

Do not expose:

- C0/C1/C2/C3/C4 label,
- run hypothesis direction,
- maintenance verifier reports,
- cost/tokens,
- other conditions' answers.

## Per-item output

Each pass returns:

```json
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
```

Correctness uses the frozen 0/1/2 scale in `scoring-protocol-v0.md`.

The rationale must reference evaluator IDs rather than inventing new factual prose.

## Disagreement rule

Route an item to `needs_human_audit` when the two passes:

- differ in correctness by more than 1 point, or
- disagree on any major error flag (`unsupported_claim`, `temporal_error`, `entity_conflation`), or
- produce an invalid/failed parse.

Omission disagreement alone is recorded and may also be audited when it changes the interpretation of a headline result.

## Stable human-audit sample

Independently of model agreement, preserve the existing deterministic approximately-20% sample:

```text
sha256(run_id + ':' + query_id)
first_8_hex mod 5 == 0
```

Human audit uses the same blinded packet.

## Aggregation

Do not silently average two contradictory judgments into false precision.

For non-disputed items:

- report the two-pass correctness pair,
- use their mean only as a descriptive aggregate,
- report error flags by pass and consensus.

For audited items, preserve both model judgments and the human adjudication separately; the adjudicated score may be used for the final score record without modifying original model outputs.

## Replication trigger

A different evaluator model/runtime becomes necessary when:

- same-model evaluation is plausibly driving the main conclusion,
- evaluator disagreement is high,
- one condition's answer style appears systematically favored,
- or a decision would become expensive to reverse based primarily on Layer C semantic scores.
