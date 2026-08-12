# E007 Prompt Set

Status: pre-run prompt design v0

## Isolation goal

E007 is **not** a representation experiment. C1–C4 therefore maintain the same basic derived artifact shape: one Markdown knowledge artifact named logically `wiki.md`.

The artifact may reorganize its prose as knowledge evolves, but conditions do not receive different page ontologies, graph schemas, or retrieval indexes.

The experimental variable is the **maintenance/verification policy**.

## Common inputs

Templates may receive these placeholders:

- `{{CURRENT_WIKI}}` — current derived Markdown; empty at W0
- `{{NEW_SOURCES}}` — the current wave's raw sources
- `{{ALL_SOURCES}}` — every raw source available through the current wave
- `{{CANDIDATE_WIKI}}` — proposed next derived state
- `{{VERIFICATION_REPORT}}` — structured verifier output
- `{{REGRESSION_FAILURES}}` — fixed regression failures when applicable
- `{{QUESTIONS}}` — query batch for evaluation

Raw sources are formatted with stable source IDs such as `S001`.

## Common artifact expectations

All derived conditions should make a good-faith attempt to preserve:

- important current facts,
- exact details likely to matter later,
- historically meaningful prior states,
- unresolved disagreement/uncertainty,
- distinctions among confusable entities.

However, only C2+ receives the stronger rule that raw sources — not derived wiki prose — are the factual authority.

This deliberately makes C1 a plausible but unsafe implementation rather than an absurdly bad strawman.

## Query policy for E007

For primary E007 scoring, C1–C4 answer from their **derived wiki state only**. This makes compilation loss measurable.

C0 answers from all raw sources available at that wave and acts as the strong no-derived-state baseline.

Raw-fallback/agentic retrieval is deferred to E006. We may later report a secondary source-assisted analysis, but it must not replace the primary derived-state coverage metric.

## Prompt changes

Once the first scored run starts, changes to these prompts require a new prompt/protocol version. Do not tune v0 in place against observed comparative results.
