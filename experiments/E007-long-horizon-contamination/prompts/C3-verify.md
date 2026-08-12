You are a verifier for a proposed update to a fictional personal knowledge wiki.

Evaluate the transition:

`previous wiki + newly available evidence -> candidate next wiki`

Raw sources are authoritative. The previous wiki is derived state and may itself contain mistakes.

Evaluate exactly three dimensions:

1. **coverage** — Does the candidate preserve important new information from the new source wave, including exact details or uncertainty that are reasonably likely to matter later? Flag material omission; do not demand every sentence be copied.
2. **preservation** — Does the candidate accidentally remove or corrupt useful previously represented knowledge that remains supported by the full raw-source set? Do not flag legitimate correction, supersession, or deliberate removal of unsupported derived content.
3. **faithfulness** — Does the candidate contain factual statements, source ownership, temporal claims, or synthesized conclusions that are not supported by the full raw-source set?

Pay special attention to:

- exact numbers/dates/identifiers,
- confusable entities,
- correction vs change over time,
- unresolved disagreement,
- facts that appear only in an early source,
- source IDs attached to claims.

Return **JSON only** with this shape:

{
  "decision": "accept" | "revise",
  "coverage_issues": [
    {"description": "...", "source_ids": ["S..."]}
  ],
  "preservation_issues": [
    {"description": "...", "source_ids": ["S..."]}
  ],
  "faithfulness_issues": [
    {"description": "...", "source_ids": ["S..."]}
  ]
}

Use `accept` only when all three issue arrays are empty. Do not rewrite the wiki yourself.

## Previous wiki

{{CURRENT_WIKI}}

## New source wave

{{NEW_SOURCES}}

## Candidate next wiki

{{CANDIDATE_WIKI}}

## Authoritative raw sources available so far

{{ALL_SOURCES}}
