# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, and code history stay in their canonical files and Git history.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. We should test architecture-relevant uncertainty rigorously, but avoid letting the research program delay a usable Wiki after the decision is sufficiently supported.

The product is VS Code-first, while the trustworthy storage/retrieval/provenance core should remain editor-agnostic enough to support later surfaces.

## Current state

- **Raw-first Alpha Core:** declared ready by ADR-0008 / PR #52 (`2a54e96d...`).
- **Immediate trust fix in flight:** #54 / PR #55. PR #52 left E003 correction/change/dispute writes on a direct text append path; #55 routes them through the canonical `O_APPEND` + full-write + `fsync` helper and adds focused regression coverage.
- **VS Code UI:** already implemented and exercised to a useful early product shape. Deliberately not the current optimization target; resume UX work from real dogfood friction/preferences rather than speculative polish.
- **Retrieval:** `whole_object_v0` (W0) remains visible/default. E014-R1's `structural_expand_v1` (X1) is implemented only as a non-default shadow candidate.
- **E015:** realistic W0-vs-X1 shadow collection is armed. Natural workload, not synthetic replay, determines whether the E014 mechanism matters in real use.
- **E013:** realistic revisit/update/query-mix calibration remains the gate before any durable compiled provider is activated.
- **Persistent compiled Wiki:** disabled. Controlled E011/E012 results showed a possible high-reuse region, but realistic E013 evidence is still required.
- **Vectors/graphs/automatic canonical mutation:** not justified by current evidence and not on the default path.

## Next actions

1. Finish #55 only after the full core/consumer/frozen regression suite is green, then close #54.
2. Move the center of gravity from more core infrastructure to **real VS Code dogfood use**.
3. Accumulate natural E013 and E015 evidence under the existing privacy/sessionization boundaries; do not manufacture readiness with synthetic activity.
4. When a preregistered data-sufficiency/decision boundary is reached, analyze it and make the next narrow architecture decision.
5. Reopen core work only for an observed dogfood blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure in an existing Alpha invariant.
6. Resume UI refinement when repeated real-use friction or preference is visible; expect the UI to evolve with use.

## Do not accidentally do

- Do not treat this repository's research process as the end goal; the goal is the working LLM Wiki.
- Do not restart an open-ended core-infrastructure checklist after Alpha.
- Do not promote X1 to default from E014 synthetic evidence alone.
- Do not enable persistent compiled state from E011/E012 alone.
- Do not add vector/graph/verifier/automation complexity merely because it is available.
- Do not rewrite raw evidence or let generated answers become canonical truth automatically.
- Do not over-polish the VS Code UI before dogfood provides real feedback.

## Fast pointers

- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Current persistence decision: `decisions/ADR-0008-canonical-jsonl-crash-containment.md`
- Dogfood usage/current substrate: `dogfood/README.md`
- Realistic compiled-provider gate: Issue #21 / E013
- Realistic retrieval-shadow gate: Issue #38 / E015
- Immediate Alpha trust fix: Issue #54 / PR #55

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
