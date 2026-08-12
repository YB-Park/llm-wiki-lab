You maintain one persistent Markdown knowledge artifact for a fictional personal research wiki.

A candidate wiki update was checked for coverage, preservation, and faithfulness. Repair only the issues identified by the verifier while preserving useful structure and avoiding unrelated rewrites.

## Authority rule

Raw sources are authoritative. The current/previous wiki and candidate wiki are derived state, not independent evidence.

Requirements:

- Resolve every verifier issue that can be resolved from the available raw sources.
- Preserve unresolved source disagreement rather than choosing a winner without evidence.
- Distinguish corrections from real changes over time.
- Preserve useful historically valid states when later evidence supersedes them.
- Do not reintroduce unsupported derived content.
- For exact numbers, dates, identifiers, configuration values, and disputed claims, keep compact source IDs such as `[S007]` near the relevant statement.
- Do not make unrelated stylistic rewrites unless needed to repair the identified issue.

Output only the complete repaired Markdown wiki, with no surrounding commentary or code fence.

## Previous wiki

{{CURRENT_WIKI}}

## Candidate wiki

{{CANDIDATE_WIKI}}

## Verification report

{{VERIFICATION_REPORT}}

## Authoritative raw sources available so far

{{ALL_SOURCES}}
