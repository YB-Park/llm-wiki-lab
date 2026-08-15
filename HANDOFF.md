# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, issues, and code history stay in their canonical locations.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. The product is VS Code-first; the trustworthy storage/retrieval/provenance core remains editor-agnostic.

## Current state

- **Raw-first Alpha Core:** ready and post-Alpha red-team hardened. Keep the convergence rule active: no open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Dogfood 0.1.4:** P1–P5 are closed: SHA-guarded local original-source navigation, correction/change/dispute commands, fixed-code feedback, current-only cross-topic discovery, and minimal backup/restore guidance are part of the VS Code surface.
- **Deterministic self-hosting:** the full repo has been ingested into its own Wiki. Frozen E010 v1: 278/278 UTF-8 files, 11/12 = 0.917 expected-source top-5, MRR 0.736, context 12/12. Earlier v0 was 272/272, 12/12, MRR 0.753. Preserve both results.
- **Real-model self-use:** completed. Assistant-as-user E010 runs used the actual Wiki plus exact `gpt-5.6-luna` through GitHub Actions Copilot entitlement. See `results-v2-real-user-luna.md`.
- **What worked in real Luna use:** customer-readiness reasoning, compiled-Wiki decision recall, correction semantics, unresolved-dispute semantics, and navigable provenance all produced genuinely useful answers in tested flows.
- **Observed answer-layer failures:** E014/E015 was misinterpreted in two independent calls despite correct retrieval and explicit negative evidence; the manifest-loss question produced non-context citations in two independent calls.
- **Citation safety:** PR #83 now fails closed on missing/non-context model citations before display. The repeated manifest case is therefore safe but still not reliably useful; #85 tracks per-context citation handles.
- **Semantic answer trust:** prompt strengthening did not fix the repeated E015 forbidden-conclusion error. #86 tracks a narrow structured/verification experiment; do not silently add a verifier stack.
- **Customer readiness:** **NOT READY YET.** The reason is now concrete real-model evidence, not merely lack of testing. Resolve the observed answer-layer blockers and accumulate repeated natural multi-session VS Code use before a strong customer-ready claim.
- **VS Code UI:** useful command-driven Alpha surface. Additional UX work should follow repeated real-use friction/preferences rather than speculative polish.
- **Retrieval:** W0 remains default. E015 measures realistic W0/X1 divergence only; it is **not a quality proof** and cannot promote X1 by itself.
- **Persistent compiled Wiki:** disabled pending realistic E013 reuse/update/query-mix evidence.
- **Copilot/Luna:** actual `gpt-5.6-luna` CLI/remote entitlement is proven now and was also used heavily in E011. Issue #24 is only the remaining **VS Code-native LM API adapter** question: whether the user's authenticated VS Code session exposes exact Luna without silent substitution.

## Immediate next work

1. **#85 — citation transport reliability.** Test per-context citation handles on the frozen manifest-loss failure so evidence-body `src-...` strings cannot collide with the answer citation namespace. Keep deterministic mapping back to canonical provenance and fail closed on unknown handles.
2. **#86 — semantic constraint reliability.** Preregister the smallest gate comparing current single-call behavior, a one-call structured constraint extraction/final answer, and only if needed a bounded separate verifier call. The observed E015 failure is the primary negative case; correction/dispute and ordinary positive answers are controls.
3. **Real VS Code-native Luna adapter (#24).** In the user's actual VS Code + Copilot Pro session, run zero-generation discovery. Exact Luna only; no fuzzy fallback. Native transport is optional if the validated CLI adapter remains safer/simpler.
4. **Repeated natural dogfood.** Use the installed Wiki over multiple sessions: capture -> leave -> recover later -> Ask -> provenance -> update/correct/dispute -> feedback. Let E013/E015 telemetry arise naturally; do not manufacture thresholds.
5. Re-evaluate customer readiness only after the observed answer-layer blockers and repeated-use evidence have been addressed.

## Do not accidentally do

- Do not treat the research repo as the end goal; the working LLM Wiki is the goal.
- Do not equate Alpha Core, deterministic retrieval, or packaged-VSIX CI with customer readiness.
- Do not dismiss the E015 real-answer failure because its citations were valid; valid provenance does not make an unsupported inference correct.
- Do not disable fail-closed citation validation to make Ask look more reliable.
- Do not add a general verifier stack before #86 shows that a cheaper contract is insufficient.
- Do not promote X1 from E014 or E015 disagreement alone.
- Do not enable persistent compiled state from E011/E012 alone.
- Do not store workspace paths or citation handles as canonical evidence identity/trust signals.
- Do not turn cross-topic discovery into unscoped all-history model Ask.
- Do not add vector/graph/automation complexity merely because it is available.
- Do not rewrite raw evidence or let generated answers become canonical truth automatically.

## Fast pointers

- E010 product/customer gate: `experiments/E010-vscode-dogfood/README.md`
- Deterministic self-hosting: `experiments/E010-vscode-dogfood/results-v0.md`, `results-v1.md`
- Real-user Luna verdict: `experiments/E010-vscode-dogfood/results-v2-real-user-luna.md`
- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`
- Dogfood substrate: `dogfood/README.md`, `dogfood/vscode/README.md`
- Realistic compiled-provider gate: Issue #21 / E013
- VS Code-native exact-Luna adapter gate: Issue #24
- Realistic retrieval-shadow gate: Issue #38 / E015
- Citation reliability follow-up: Issue #85
- Semantic answer verification candidate: Issue #86

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
