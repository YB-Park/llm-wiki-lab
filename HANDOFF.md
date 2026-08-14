# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, issues, and code history stay in their canonical locations.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. Test architecture-relevant uncertainty rigorously, but do not let the research program delay a usable Wiki after a decision is sufficiently supported.

The product is VS Code-first, while the trustworthy storage/retrieval/provenance core should remain editor-agnostic enough to support later surfaces.

## Current state

- **Raw-first Alpha Core:** ready and post-Alpha red-team hardened. The convergence rule remains active: do not restart open-ended core infrastructure work without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **First full self-hosting dogfood:** E010 Stage A ingested the actual repository: **272/272 Git-tracked UTF-8 files, 1,602,314 bytes**. The preregistered 12 project-recall queries achieved **12/12 top-5 target hits, MRR 0.753, and 12/12 non-empty provenance contexts** with W0 and zero model calls. The current lexical floor can recover this project's own architecture/decision knowledge.
- **Customer readiness:** **NOT READY YET.** E010 found concrete product blockers outside the Alpha Core: basename-only source navigation is ambiguous in a repo with 22 duplicate-basename groups (`README.md` alone appears 14 times); VS Code does not expose correction/change/dispute semantics; E013 helpful/not-helpful feedback is not first-class in VS Code; VS Code search assumes a selected/remembered topic; primary user docs lack a minimal backup/restore story; real VS Code/Copilot exact-Luna behavior and repeated multi-session habitability remain untested.
- **VS Code UI:** useful early command-driven shell, not a finished customer surface. Product work should now be driven by the E010 blockers and real-use friction rather than speculative polish.
- **Retrieval:** `whole_object_v0` (W0) remains visible/default. E014-R1's `structural_expand_v1` (X1) remains a non-default shadow candidate. E010 self-repo success is evidence that W0 is a credible floor, not permission to stop E015 or promote X1.
- **E015:** realistic W0-vs-X1 shadow collection is armed. Natural workload, not synthetic replay, determines whether the E014 mechanism matters in real use.
- **E013:** realistic revisit/update/query-mix calibration remains the gate before any durable compiled provider is activated.
- **Persistent compiled Wiki:** disabled. Controlled E011/E012 results showed a possible high-reuse region, but realistic E013 evidence is still required.
- **Copilot/Luna:** zero-generation discovery tooling exists. The remaining Issue #24 gate requires the user's real VS Code/Copilot Pro session. CI cannot claim or simulate that entitlement.
- **Vectors/graphs/automatic canonical mutation:** not justified by current evidence and not on the default path.

## Immediate product blockers

1. **Original-source navigation:** preserve a safe local workspace locator separately from evidence identity so duplicate basenames can navigate back to the actual source file; raw evidence remains the authority/fallback.
2. **Trust semantics in VS Code:** expose correction, change-with-effective-time, and dispute operations without requiring a terminal or direct core API use.
3. **Feedback in VS Code:** make existing fixed-code E013 helpful/not-helpful feedback easy during natural use.
4. **Forgotten-topic recovery:** add a safe cross-topic discovery flow that searches each topic's current evidence rather than using the unscoped all-history view.
5. **Backup/restore operating story:** define a minimal safe procedure before valuable personal knowledge is entrusted to the local store; do not confuse fail-closed detection with recovery.
6. **Real Copilot session:** run exact-Luna discovery in the user's actual VS Code/Copilot Pro session; only if exact Luna is exposed, permit <=2 tiny synthetic native-generation smoke calls, then a small consented non-sensitive Ask flow.
7. **Repeated use:** run capture -> leave -> recall later -> inspect source -> update/correct/dispute -> feedback across multiple real sessions. Natural E013/E015 evidence should accumulate from this, not from manufactured activity.

## Next actions

1. Finish the E010/product-readiness reset and keep `docs/02`, `docs/03`, and `docs/04` aligned with the actual E013/E015/E010 state rather than the old E011 critical path.
2. Fix blockers 1–5 narrowly, one observed product problem at a time, without reopening unrelated core architecture.
3. Run blocker 6 in the user's real VS Code/Copilot Pro session.
4. Start blocker 7 immediately with the hardened VSIX; collect natural E013/E015 data while using the Wiki for real project work.
5. Re-evaluate customer readiness only after these product gates have evidence. Until then describe the system as **Alpha/dogfood**, not customer-ready.

## Do not accidentally do

- Do not treat this repository's research process as the end goal; the goal is the working LLM Wiki.
- Do not equate Alpha Core readiness with customer readiness.
- Do not restart an open-ended core-infrastructure checklist after Alpha.
- Do not promote X1 to default from E014 synthetic evidence or E010 self-repo retrieval alone.
- Do not enable persistent compiled state from E011/E012 alone.
- Do not add vector/graph/verifier/automation complexity merely because it is available.
- Do not rewrite raw evidence or let generated answers become canonical truth automatically.
- Do not store workspace paths as evidence identity, provenance reliability, or corroboration signals; any navigation locator must remain a local convenience layer.
- Do not implement cross-topic recall by silently feeding superseded all-history evidence to model-backed Ask.
- Do not over-polish visual UI before the concrete E010 product blockers and real-use friction are addressed.
- Do not casually expand Alpha into hash-chained rollback detection, multi-writer transactions, or cross-file atomicity; those remain explicit non-goals absent real evidence that they are needed.
- Missing optional `provenance.jsonl` remains intentionally ambiguous between “never used” and “deleted”; do not invent a durable sentinel/recovery mechanism without a concrete need and explicit decision.

## Fast pointers

- Product/customer gate and self-repo result: `experiments/E010-vscode-dogfood/README.md`, `experiments/E010-vscode-dogfood/results-v0.md`
- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Current persistence decision: `decisions/ADR-0008-canonical-jsonl-crash-containment.md`
- Dogfood usage/current substrate: `dogfood/README.md`
- Realistic compiled-provider gate: Issue #21 / E013
- VS Code-native exact-Luna gate: Issue #24
- Realistic retrieval-shadow gate: Issue #38 / E015

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
