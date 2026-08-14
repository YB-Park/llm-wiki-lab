# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, issues, and code history stay in their canonical locations.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. Test architecture-relevant uncertainty rigorously, but do not let the research program delay a usable Wiki after a decision is sufficiently supported.

The product is VS Code-first, while the trustworthy storage/retrieval/provenance core should remain editor-agnostic enough to support later surfaces.

## Current state

- **Raw-first Alpha Core:** ready and post-Alpha red-team hardened. Canonical temporal writes use the shared crash-contained log boundary; model-backed Ask is topic/current-only; rendered evidence cannot spoof generated metadata through filenames and is explicitly quoted as untrusted data; POSIX local Wiki state is owner-only by default; new private/raw replacement bytes are completed and `fsync`ed before same-directory atomic publication so failed writes cannot poison the final content-addressed path; partial multi-file ingest cannot hide an E013 maintenance event; Doctor enforces aggregate raw/canonical integrity; missing canonical history fails closed instead of recreating an empty Wiki when either the initialized config or surviving raw evidence proves prior state.
- **Red-team validation:** the above hardening passed Python/CLI, development VS Code Extension Host, packaged VSIX, and frozen E004/E014/E014-R1 regressions. **Paid/model calls used for this deterministic red-team: 0.** Keep paid model budget for questions that genuinely require model behavior rather than deterministic core testing.
- **VS Code UI:** already implemented and exercised to a useful early product shape. Deliberately not the current optimization target; resume UX work from real dogfood friction/preferences rather than speculative polish.
- **Retrieval:** `whole_object_v0` (W0) remains visible/default. E014-R1's `structural_expand_v1` (X1) remains a non-default shadow candidate.
- **E015:** realistic W0-vs-X1 shadow collection is armed. Natural workload, not synthetic replay, determines whether the E014 mechanism matters in real use.
- **E013:** realistic revisit/update/query-mix calibration remains the gate before any durable compiled provider is activated.
- **Persistent compiled Wiki:** disabled. Controlled E011/E012 results showed a possible high-reuse region, but realistic E013 evidence is still required.
- **Vectors/graphs/automatic canonical mutation:** not justified by current evidence and not on the default path.

## Next actions

1. Move the center of gravity to **real VS Code dogfood use**.
2. Accumulate natural E013 and E015 evidence under the existing privacy/sessionization boundaries; do not manufacture readiness with synthetic activity.
3. Use paid Copilot/model calls when a real model-behavior question needs them; avoid spending them on deterministic storage/retrieval/integrity checks.
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
- Do not casually expand Alpha into hash-chained rollback detection, multi-writer transactions, or cross-file atomicity; those remain explicit non-goals absent real evidence that they are needed.
- Missing optional `provenance.jsonl` remains intentionally ambiguous between “never used” and “deleted”; do not invent a durable sentinel/recovery mechanism without a concrete need and explicit decision.

## Fast pointers

- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Current persistence decision: `decisions/ADR-0008-canonical-jsonl-crash-containment.md`
- Dogfood usage/current substrate: `dogfood/README.md`
- Realistic compiled-provider gate: Issue #21 / E013
- Realistic retrieval-shadow gate: Issue #38 / E015

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
