# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, issues, and code history stay in their canonical locations.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. The product is VS Code-first while the trustworthy storage/retrieval/provenance core remains editor-agnostic.

## Current state

- **Raw-first Alpha Core:** ready and post-Alpha red-team hardened. Keep the convergence rule active: no open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Packaged Dogfood 0.1.5:** last installable artifact. It includes fail-closed model citations and per-context `C1/C2/...` citation handles. **Main is now ahead of that package** because E017 fixed global forgotten-topic discovery under uneven topic sizes. Before starting the next real installed P7 cycle, cut and packaged-test a small 0.1.6 containing the merged discovery fix rather than knowingly using stale 0.1.5 behavior.
- **Deterministic self-hosting:** frozen E010 v1 remains **278/278 files, 11/12 expected-source top-5, MRR 0.736, context 12/12**. A later 303-file run remained above the gate at **11/12 top-5, MRR 0.674, context 12/12**. Do not rewrite frozen historical scores as the repo grows.
- **Real-model self-use:** completed with exact `gpt-5.6-luna`; project-repo Ask/provenance/correction/dispute/citation handling were exercised and real failures were preserved. See `experiments/E010-vscode-dogfood/results-v2-real-user-luna.md`.
- **Citation reliability:** real Luna fabricated/non-context `src-...` citations in early dogfood. #83/#87 now fail closed and expose only per-call citation handles, then deterministically materialize canonical provenance. The frozen post-fix manifest-loss retest PASSed.
- **E017 external real-user dogfood:** completed on three unfamiliar public corpora: **1,515 Kubernetes Markdown docs, 557 CPython reStructuredText docs, and 10 official NASA Artemis II pages**. First pass used exactly three Luna calls; only the CPython failure earned one narrow X1 follow-up. See `experiments/E017-external-real-user-corpora/results-v0.md`.
- **Global forgotten-topic discovery:** E017 zero-model preflight found a correctness bug before any paid call. Topic-local BM25 scores from very uneven corpora were being sorted globally; the NASA question selected CPython. Main now scores the union of topic-current immutable objects in one shared BM25 space for `discover`, while topic W0 search/Ask remains unchanged. Regression coverage preserves current-only/no-E013-visit semantics.
- **Kubernetes external case:** manual **PASS**. W0 produced a useful non-overclaiming answer: `maxUnavailable: 0` blocks PDB-respecting voluntary eviction but does not guarantee zero downtime or prevent involuntary node failure. All citations resolved.
- **NASA external case:** **PASS**. W0 reconstructed launch -> Earth-orbit departure -> splashdown with supported dates/times, refused unsupported precision, and correctly treated the May 7 editor update as a mileage correction rather than a new mission event. All citations resolved.
- **CPython external case:** W0 was safely insufficient rather than hallucinating, but failed the user's actual question because its best paragraph from the correct `multiprocessing.rst` object was irrelevant to start methods. X1 materially repaired the same frozen question in one additional Luna call: POSIX=`forkserver`, Python 3.14, and the multithread-safety rationale were recovered with resolvable citations and clean integrity.
- **Remaining CPython/RST limit:** D2 is only a **partial repair**. The exact 3.12 `DeprecationWarning` paragraph exists in the same long `multiprocessing.rst` source but was still absent from X1 context. Current structural splitting recognizes Markdown `#` headings; reStructuredText falls back to paragraphs, and X1 currently keeps one best unit per object plus one neighbor. This is concrete evidence for a possible non-Markdown / multi-aspect same-object limitation, not permission to build a parser/index stack yet.
- **X1 evidence:** E015-D1 is one full real-user repair on the project repo; E017-D2 is a second independent external case with **material partial repair**. This strengthens the case that context granularity matters in reality, but is still not enough for global X1 promotion. Continue quality-labeling natural divergent cases.
- **E016 verifier detour:** stopped. Do not restart verification unless a future real answer contradicts a material limitation demonstrably present in the exact model context.
- **Copilot/Luna:** exact `gpt-5.6-luna` access is proven. Issue #24 is only the optional VS Code-native LM API transport question, not a model-availability blocker.
- **Persistent compiled Wiki:** disabled pending realistic E013 revisit/update/query-mix evidence.
- **Customer readiness:** **NOT READY YET.** Repeated natural multi-session installed VS Code use is still missing; retrieval now has stronger real-world evidence but also a newly observed non-Markdown/multi-aspect limit.

## Immediate next work

1. **Package 0.1.6 from current main before installed P7.** Keep it a small release: merged global discovery correctness fix plus already-current 0.1.5 boundaries; packaged VSIX Extension Host must pass before use.
2. **Start/continue real P7 use in VS Code.** Capture -> leave -> recover later -> Ask -> provenance -> update/correct/change/dispute -> feedback -> reuse again.
3. **Let E013/E015 arise naturally.** Do not manufacture visits, updates, topics, queries, or feedback to hit thresholds.
4. **Quality-label natural W0/X1 divergence narrowly.** E015-D1 and E017-D2 justify looking. Do not promote X1 from disagreement frequency alone.
5. **Watch for recurrence of the CPython mechanism.** If multi-aspect questions over long non-Markdown objects repeatedly lose a second relevant region, preregister the smallest candidate that can recover multiple relevant units or format structure without exploding context/index cost.
6. **Do not spend more Luna calls on the frozen E017 cases.** The 3+1 calls already separated useful success, W0 context failure, X1 repair, and the remaining X1 boundary.
7. **Use UI friction as product evidence.** Resume UI work from repeated real installed-use friction/preferences, not speculative polish.
8. Re-evaluate customer readiness after repeated natural use and enough realistic retrieval evidence, not from CI confidence alone.

## Do not accidentally do

- Do not treat the research repo as the end goal; the working LLM Wiki is the goal.
- Do not equate Alpha Core, deterministic self-retrieval, external-corpus success, or packaged-VSIX CI with customer readiness.
- Do not use full `source show` content as a proxy for what the model actually received; inspect exact rendered context before diagnosing semantic failure.
- Do not disable fail-closed citation validation to make Ask look more reliable.
- Do not compare raw BM25 scores produced independently by different topics; global discovery now has a shared scoring space for this reason.
- Do not store citation handles or workspace paths as canonical evidence identity/trust signals.
- Do not add a verifier stack because E016 exists.
- Do not promote X1 globally from E014 synthetic evidence, E015 disagreement rate, E015-D1, or E017-D2 alone.
- Do not immediately add RST/AsciiDoc/parser/index infrastructure from one CPython case; require recurrence or a strong low-cost candidate test.
- Do not enable persistent compiled state from E011/E012 alone.
- Do not turn cross-topic discovery into unscoped all-history model Ask.
- Do not add vector/graph/automation complexity merely because it is available.
- Do not rewrite raw evidence or let generated answers become canonical truth automatically.

## Fast pointers

- Project-repo real-user verdict: `experiments/E010-vscode-dogfood/results-v2-real-user-luna.md`
- External real-user first pass: `experiments/E017-external-real-user-corpora/results-v0.md`
- CPython X1 follow-up: `experiments/E017-external-real-user-corpora/cpython-d2-x1-preregistration-v0.md`, `cpython-d2-x1-result-v0.md`
- First full realistic X1 repair: `experiments/E015-realistic-retrieval-shadow/divergent-case-d1-result-v0.md`
- E015 realistic shadow gate: Issue #38
- E013 realistic compiled-provider gate: Issue #21
- Optional VS Code-native exact-Luna adapter gate: Issue #24
- Stopped semantic-verifier candidate: Issue #86 / `experiments/E016-semantic-constraint-gate/`
- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`
- Dogfood usage/current substrate: `dogfood/README.md`, `dogfood/vscode/README.md`

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
