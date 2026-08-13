You are evaluating a proposed update to a fictional knowledge artifact.

Judge only whether the **proposed next canonical state** is a faithful and sufficiently complete integration of the previous canonical state and the newly available authoritative evidence.

Do not judge writing style unless it changes meaning. A large rewrite or reorganization can be valid. Deleting or changing prior wording can also be valid when authoritative evidence corrects or supersedes it, but historically meaningful prior states must not be silently rewritten as if they were never true.

Check these dimensions:

1. **coverage** — important information established by the new evidence is not silently omitted;
2. **preservation** — still-valid prior knowledge, historical states, qualifiers, and unrelated facts are not accidentally lost;
3. **faithfulness** — the candidate does not invent claims, causality, consensus, scope, or current-state conclusions not supported by the evidence;
4. **provenance** — when source identity is present and important to verification, disagreement, or decision rationale, the candidate does not silently erase it;
5. **temporal/epistemic semantics** — correction, change over time, disagreement, uncertainty, experimental status, and historical aliases are represented according to the evidence rather than flattened together.

Return `accept` only when you find no material issue in these dimensions. Return `revise` when one or more material issues exist.

Do not propose a repaired document. Do not infer any hidden benchmark label. Do not be conservative merely because the candidate differs substantially from the previous state.

Return JSON only:

{
  "decision": "accept | revise",
  "coverage_issues": [
    {"id":"short-id","description":"concise issue"}
  ],
  "preservation_issues": [],
  "faithfulness_issues": [],
  "provenance_issues": [],
  "temporal_epistemic_issues": []
}

If an issue plausibly belongs to more than one category, put it in the single category that best describes the primary failure. Do not duplicate the same issue across arrays.

## Previous canonical state

{{PREVIOUS_STATE}}

## New authoritative evidence

{{NEW_EVIDENCE}}

## Proposed next canonical state

{{CANDIDATE_STATE}}
