# Current Handoff

Last updated: 2026-08-15 KST

This file is the **current continuation state**, not a project history. Replace or delete stale items as the project moves. Detailed evidence, experiments, ADRs, issues, and code history stay in their canonical locations.

## North Star

Build a **proper VS Code-first LLM Wiki**: take the useful core idea behind the LLM Wiki concept seriously, fill in the trust/maintenance details that a sketch leaves open, incorporate real implementation experience and failure modes, and converge on something we actually use.

Research and experiments are means, not the product. Test architecture-relevant uncertainty rigorously, but do not let the research program delay a usable Wiki after a decision is sufficiently supported.

The product is VS Code-first, while the trustworthy storage/retrieval/provenance core should remain editor-agnostic enough to support later surfaces.

## Current state

- **Raw-first Alpha Core:** ready and post-Alpha red-team hardened. The convergence rule remains active: do not restart open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Dogfood 0.1.4:** merged in PR #78. The automated E010 product blockers P1–P5 are closed without weakening canonical evidence semantics: SHA-guarded local original-source navigation, explicit correction/change/dispute commands, fixed-code feedback, current-only cross-topic discovery, and a minimal backup/restore operating procedure are now part of the VS Code product surface.
- **Self-hosting:** the project has now formally run its **entire tracked repository through its own Wiki**. Latest frozen E010 run ingested **278/278 UTF-8 files**, scored **11/12 = 0.917 expected-source top-5, MRR 0.736, context 12/12**, and remained above the preregistered Stage A gate with zero model calls. The earlier 272-file v0 scored 12/12 / MRR 0.753; do not rewrite either result to make the trajectory look cleaner.
- **Customer readiness:** **NOT READY YET.** Automated product blockers are no longer the reason. The remaining gates are **P6 real VS Code/Copilot exact-Luna evidence** and **P7 repeated multi-session customer-like use**. CI cannot manufacture either.
- **VS Code UI:** useful command-driven Alpha surface. Resume additional UX work from repeated real-use friction/preferences; do not pivot into speculative visual polish.
- **Retrieval:** `whole_object_v0` (W0) remains visible/default. E010 supports it as a credible self-hosting floor, while E015 still decides whether realistic W0/X1 divergence deserves further quality work. Do not promote X1 from synthetic evidence alone.
- **E013:** natural revisit/update/query-mix evidence remains the gate before any durable compiled provider is activated.
- **E015:** natural W0-vs-X1 shadow evidence remains active; no extra model calls.
- **Persistent compiled Wiki:** disabled pending E013.
- **Copilot/Luna:** zero-generation exact-model discovery is implemented. Issue #24 now needs the user's real VS Code/Copilot Pro session. No fuzzy or silent model substitution is permitted.

## Immediate next gates

### P6 — real VS Code/Copilot exact-Luna

1. Install/use the current 0.1.4 VSIX in the user's real VS Code + Copilot Pro session.
2. Run `LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)`.
3. Inspect only the sanitized JSON. Require exact `id === "gpt-5.6-luna"` or `family === "gpt-5.6-luna"`.
4. If exact Luna is absent/error/unavailable, keep the validated CLI adapter; do **not** silently substitute another model.
5. If exact Luna is present, proceed to the preregistered **<=2 tiny synthetic generation-call** native-adapter smoke before deciding whether to replace the CLI adapter.
6. Then run a small explicitly consented Ask flow on non-sensitive project evidence.

Paid/model calls are appropriate here because this gate is specifically about real model/product behavior. Do not spend them rechecking deterministic storage/retrieval.

### P7 — repeated customer-like use

Use the installed Wiki across multiple real sessions for:

```text
capture evidence
  -> ingest
  -> leave the session
  -> recover it later (including forgotten-topic discovery)
  -> Ask / inspect provenance
  -> update / correction / change / dispute when real semantics require it
  -> give feedback
  -> keep using it
```

Let E013/E015 telemetry arise naturally. Do not manufacture visits, updates, topics, or feedback to satisfy a threshold.

## Next actions

1. Complete P6 in the user's real VS Code/Copilot Pro session.
2. Start P7 immediately with real project work and continue over multiple sessions.
3. While dogfooding, fix only repeated/meaningful product friction; keep core convergence active.
4. When E013/E015 data sufficiency is reached, make the next narrow architecture decision.
5. Re-evaluate customer readiness only from P6 + P7 evidence, not from CI confidence alone.

## Do not accidentally do

- Do not treat this repository's research process as the end goal; the goal is the working LLM Wiki.
- Do not equate Alpha Core or packaged-VSIX CI readiness with customer readiness.
- Do not restart an open-ended core-infrastructure checklist after Alpha.
- Do not change the frozen E010 expected-source benchmark after seeing a miss; semantic retrieval observations may be discussed separately from the official score.
- Do not promote X1 to default from E014/E010 alone.
- Do not enable persistent compiled state from E011/E012 alone.
- Do not store workspace paths as canonical evidence identity, provenance reliability, or corroboration signals; 0.1.4's locator remains VS Code-local convenience metadata guarded by evidence SHA.
- Do not turn cross-topic discovery into unscoped all-history model Ask.
- Do not add vector/graph/verifier/automation complexity merely because it is available.
- Do not rewrite raw evidence or let generated answers become canonical truth automatically.
- Do not casually expand Alpha into hash-chained rollback detection, multi-writer transactions, or cross-file atomicity absent real need.

## Fast pointers

- E010 product/customer gate: `experiments/E010-vscode-dogfood/README.md`
- First self-hosting result: `experiments/E010-vscode-dogfood/results-v0.md`
- 0.1.4 automated product-gate result: `experiments/E010-vscode-dogfood/results-v1.md`
- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`
- Dogfood usage/current substrate: `dogfood/README.md`, `dogfood/vscode/README.md`
- Realistic compiled-provider gate: Issue #21 / E013
- VS Code-native exact-Luna gate: Issue #24
- Realistic retrieval-shadow gate: Issue #38 / E015

If this file disagrees with merged code or an accepted ADR, **the code/ADR wins and this file should be corrected immediately**.
