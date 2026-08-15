# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, issues, and code history stay in their canonical locations.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. The product is VS Code-first while the trustworthy storage/retrieval/provenance core remains editor-agnostic.

## Current state

- **Raw-first Alpha Core:** ready and post-Alpha red-team hardened. Keep the convergence rule active: no open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Dogfood 0.1.5:** current installable Alpha. It includes the 0.1.4 product surface plus real-user answer hardening: fail-closed model citations and per-context `C1/C2/...` citation handles that are validated and mapped back to canonical provenance before display. PR #94 packaged and tested the current core in a real packaged VSIX Extension Host.
- **Deterministic self-hosting:** frozen E010 v1 remains **278/278 files, 11/12 expected-source top-5, MRR 0.736, context 12/12**. Do not rewrite that historical gate as the repo grows. A current 0.1.5 PR run on **303/303 UTF-8 files** still passed Stage A at **11/12 top-5, MRR 0.674, context 12/12**.
- **Real-model self-use:** completed. The assistant used the actual Wiki as a returning/forgetful user with exact `gpt-5.6-luna`: cross-topic discovery, Ask, provenance follow-through, correction, dispute, manifest-loss reasoning, and retrieval-candidate comparison. See `experiments/E010-vscode-dogfood/results-v2-real-user-luna.md`.
- **What worked in real use:** customer-readiness reasoning, compiled-Wiki decision recall, correction-vs-change, unresolved dispute, exact provenance navigation, fail-closed citation handling, and the post-fix manifest-loss answer all produced useful grounded behavior.
- **Citation reliability:** the real model fabricated/non-context `src-...` citations twice on one question. #83 made that safe; #87 replaced direct canonical-ID emission with per-call citation handles. Frozen real-Luna retest `31861139058` PASSed with five resolvable citations and clean integrity. Issue #85 is closed.
- **Retrieval/context risk:** W0 remains default, but real dogfood found one reproducible case where W0 retrieved the correct E015 document and still omitted the decisive neighboring paragraphs from model context. Merely increasing W0 top-k did not repair the within-object excerpt loss.
- **First realistic X1 quality case:** E015-D1 used the same user question and same current topic/corpus but X1 answer context. One exact-Luna call `31862013373` PASSed: E015 was correctly described as divergence/prevalence calibration only, **not a quality proof or default-promotion gate**, with five resolvable citations and clean integrity. This is the first realistic case matching the E014-R1 mechanism, not enough evidence for global X1 promotion.
- **E016 verifier detour:** stopped. The earlier semantic-failure diagnosis incorrectly conflated full `source show` content with the exact W0 model context. S1 therefore did not validly test a supplied negative constraint; V1 stopped before a verifier model call because the prerequisite limitation was absent from context. Issue #86 is closed `not_planned`. Do not restart verification unless a future real failure contradicts a material limitation demonstrably present in the exact model prompt.
- **Copilot/Luna:** actual `gpt-5.6-luna` access is proven through GitHub Actions/Copilot CLI and was used heavily in E011 plus the real-user evaluation. Issue #24 is only the optional **VS Code-native LM API transport** question; exact-Luna CLI/remote availability itself is not a blocker.
- **Persistent compiled Wiki:** disabled pending realistic E013 revisit/update/query-mix evidence.
- **Customer readiness:** **NOT READY YET.** The remaining evidence gap is now concrete: repeated natural multi-session VS Code use is still missing, and the default W0 path has only one quality-labeled realistic X1 repair case.

## Immediate next work

1. **Start real P7 use with 0.1.5.** Use the Wiki during ordinary project work over multiple sessions: capture -> leave -> recover later -> Ask -> provenance -> update/correct/change/dispute -> feedback -> reuse again.
2. **Let E013/E015 arise naturally.** Do not manufacture visits, updates, topics, queries, or feedback to hit thresholds.
3. **When natural W0/X1 divergence appears, inspect the divergent case narrowly.** D1 proves this is worth doing. Record whether X1 actually repairs user-visible quality; disagreement frequency by itself remains non-quality evidence.
4. **Do not promote X1 globally from D1 alone.** If several natural divergent cases show the same repair pattern without material regressions, then make the next narrow routing/default decision.
5. **Use UI friction as product evidence.** The command-driven VS Code Alpha is intentionally good enough to dogfood; resume UI work only from repeated real-use friction/preferences.
6. **Treat #24 as optional adapter work.** If replacing the validated CLI path still matters, run zero-generation exact-Luna discovery in the user's authenticated VS Code session and proceed only with exact model identity/no fallback.
7. Re-evaluate customer readiness after repeated natural use and enough realistic retrieval evidence, not from CI confidence alone.

## Do not accidentally do

- Do not treat the research repo as the end goal; the working LLM Wiki is the goal.
- Do not equate Alpha Core, deterministic self-retrieval, or packaged-VSIX CI with customer readiness.
- Do not use full `source show` content as a proxy for what the model actually received; inspect the exact rendered context before diagnosing an answer-semantic failure.
- Do not disable fail-closed citation validation to make Ask look more reliable.
- Do not store citation handles or workspace paths as canonical evidence identity/trust signals.
- Do not add a verifier stack because E016 exists; its motivating diagnosis was corrected and the experiment was stopped.
- Do not promote X1 from E014 synthetic evidence, E015 disagreement rate, or the single D1 PASS alone.
- Do not enable persistent compiled state from E011/E012 alone.
- Do not turn cross-topic discovery into unscoped all-history model Ask.
- Do not add vector/graph/automation complexity merely because it is available.
- Do not rewrite raw evidence or let generated answers become canonical truth automatically.

## Fast pointers

- Current real-user verdict: `experiments/E010-vscode-dogfood/results-v2-real-user-luna.md`
- Frozen deterministic self-hosting: `experiments/E010-vscode-dogfood/results-v0.md`, `results-v1.md`
- First realistic X1 quality case: `experiments/E015-realistic-retrieval-shadow/divergent-case-d1-preregistration-v0.md`, `divergent-case-d1-result-v0.md`
- E015 realistic shadow gate: Issue #38
- E013 realistic compiled-provider gate: Issue #21
- Optional VS Code-native exact-Luna adapter gate: Issue #24
- Stopped semantic-verifier candidate: Issue #86 / `experiments/E016-semantic-constraint-gate/`
- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`
- Dogfood usage/current substrate: `dogfood/README.md`, `dogfood/vscode/README.md`

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
