You maintain one persistent Markdown knowledge artifact for a fictional personal research wiki.

The candidate wiki passed or was repaired through source-grounded transition verification, but a fixed regression suite found that previously answerable knowledge became unavailable or misleading.

Repair the wiki **only as needed** to address the listed regression failures.

## Authority rule

Raw sources are authoritative. Regression expectations are diagnostic signals, not new factual evidence. Never add a fact merely because a regression message suggests it; verify it in the raw sources first.

Requirements:

- Recover answerability for regression failures when supported by raw evidence.
- Preserve current-vs-historical semantics and unresolved disagreement.
- Do not undo legitimate corrections or supersessions merely to reproduce an obsolete answer.
- Keep exact/disputed facts source-grounded with compact `[S###]` references.
- Avoid broad stylistic rewrites unrelated to the failures.

Output only the complete repaired Markdown wiki, with no surrounding commentary or code fence.

## Candidate wiki

{{CANDIDATE_WIKI}}

## Regression failures

{{REGRESSION_FAILURES}}

## Authoritative raw sources available so far

{{ALL_SOURCES}}
