# Current Handoff

Last updated: 2026-08-15 KST

This is the **current continuation state**, not project history. Replace or delete stale items as the project moves. Detailed evidence stays in code, ADRs, experiments, issues, PRs, and Git history.

## North Star

Build a **proper VS Code-first LLM Wiki** where the user owns a verifiable knowledge system and AI participates in retrieval/reasoning rather than becoming the unquestioned owner of memory.

Research is a means, not the product. Preserve the trust substrate while moving the center of gravity to real use, human knowledge compounding, and product operations.

## Current product state

- **Dogfood 0.1.7 is the current installable Alpha.** It packages the 0.1.6 global forgotten-topic discovery fix, fail-closed `C1/C2/...` citation transport, the #101 P0 hardening, and the first human-owned Knowledge Note product slice.
- **Raw-first Alpha Core remains ready and red-team hardened.** Keep the convergence rule: do not restart open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Copilot prompt privacy:** #102 moved the complete question/evidence prompt out of process argv. Copilot receives the transformed prompt over stdin; argv contains control/model flags only. Existing consent, exact-Luna pinning, no-tools mode, and citation validation remain.
- **Single-writer semantic safety:** #104 / #103 added one private store-level OS advisory writer lock across public read/validate/write mutations: ingest, supersede, correction/change, dispute, and exact provenance bind. A deterministic race regression proves a competing correction cannot commit against stale pre-state. This is not a DB/WAL or cross-file transaction claim.
- **Human Knowledge Note v0:** #106 / #105 adds `LLM Wiki: New Human Knowledge Note`. It opens an untitled human-owned Markdown draft with `Current statement`, `Why / reasoning`, `Supporting evidence`, and `Open questions`. Draft creation uses zero model calls, requires no topic, creates no telemetry, and does not mutate canonical Wiki state. Saving is ordinary user file ownership; explicit ingest is still separate.
- **Knowledge Note is deliberately schema-light.** No `Type`, `Status`, ontology, graph, automatic promotion, or LLM-authored durable truth has been introduced. A richer knowledge object must earn its shape through repeated dogfood.
- **Deterministic self-hosting:** frozen E010 v1 remains **278/278 files, 11/12 expected-source top-5, MRR 0.736, context 12/12**. Later growing-repo runs remained above the frozen Stage A gate; do not rewrite frozen historical scores as the corpus grows.
- **Real-model self-use:** completed with exact `gpt-5.6-luna`, including returning/forgetful discovery, Ask, provenance, correction, dispute, manifest-loss reasoning, and citation failure/retest.
- **External E017 dogfood:** completed on 1,515 Kubernetes Markdown docs, 557 CPython RST docs, and 10 NASA Artemis II pages. Kubernetes and NASA produced useful grounded W0 answers. CPython exposed a real context-construction limit.
- **Retrieval:** W0 remains default; X1 remains non-default/shadow. E015-D1 is one full real-user X1 repair and E017-D2 is a second independent material partial repair. That is meaningful real evidence that context granularity matters, but still not enough for global X1 promotion.
- **Known retrieval limit:** long non-Markdown objects can require multiple separated regions. In CPython RST, X1 recovered the current `forkserver` default/rationale but still omitted the distant exact `DeprecationWarning` paragraph. Do not build a broad parser/index stack from one mechanism unless it recurs.
- **Persistent compiled Wiki:** disabled pending natural E013 revisit/update/query-mix evidence.
- **Customer readiness:** **NOT READY YET.** The missing proof is repeated natural multi-session installed use where human notes/evidence are created, left alone, recovered later, corrected/changed/disputed, and reused.

## #101 product-review response

Treat Issue #101 as strong adversarial product input, **not a roadmap that silently overrides evidence**.

Accepted and shipped:
- Copilot prompt argv -> stdin: #102.
- store-level semantic single-writer protection: #103 / #104.

Accepted but deliberately narrowed:
- Evidence Wiki -> Human Knowledge compounding: #105 / #106 Knowledge Note v0, human-owned Markdown first, no ontology.

Conditional on real recurrence/friction:
- X2 format-aware / same-object multi-region retrieval: only when natural cases repeat the CPython mechanism.
- Personal Store / Project Store federation: when cross-workspace knowledge reuse becomes real pain.
- Inbox/staging capture: when repeated capture ceremony becomes observed friction; automate preparation, not truth.
- Tree View / Health UI: when command-driven use reveals repeated navigation/health friction.
- Scale optimization: measure first; start with staged low-cost 1k/10k gates before inventing a persistent index.

Product/Beta engineering backlog, not current Alpha architecture research:
- verified snapshot / restore preview;
- durable migration framework;
- Windows/macOS/WSL/Remote/Codespaces product matrix;
- Python runtime distribution strategy;
- Marketplace/release metadata and support/privacy docs.

Do not do now:
- vector DB or knowledge graph merely because they are available;
- global X1/X2 promotion from two favorable real cases;
- broad document-format parser infrastructure from the single RST case;
- verifier stack revival without an answer contradicting a limitation demonstrably present in the exact model prompt;
- LLM-generated answers/notes automatically becoming canonical truth.

## Immediate next work

1. **Use installed 0.1.7 naturally over multiple sessions.** The product loop is now: capture evidence and/or write a Human Knowledge Note -> leave -> return later -> global recover -> Ask -> provenance -> update/correct/change/dispute -> feedback -> reuse.
2. **Dogfood Knowledge Note v0, not its template.** The question is whether human reasoning/decisions become meaningfully easier to recover later. If nobody repeatedly uses it, do not promote it into a canonical knowledge schema.
3. **Let E013/E015 arise naturally.** Do not manufacture visits, updates, query classes, or divergences to hit thresholds.
4. **Quality-label natural W0/X1 divergence narrowly.** D1/D2 justify inspection, not automatic promotion.
5. **Treat product interaction changes faster than epistemic architecture changes.** Navigation/onboarding/note UX can iterate quickly; canonical semantics/retrieval defaults/automatic mutation still require strong evidence.
6. **Do not spend more Luna calls on frozen E017 cases.** Use paid calls only when a new real-user question can change a product decision.
7. Re-evaluate customer readiness from repeated installed use, operational reliability, and recovered human knowledge—not from CI confidence alone.

## Fast pointers

- External product review: Issue #101
- Human Knowledge Note v0: Issue #105 / PR #106
- P0 prompt transport: PR #102
- P0 single writer: Issue #103 / PR #104
- Project-repo real-user verdict: `experiments/E010-vscode-dogfood/results-v2-real-user-luna.md`
- External real-user result: `experiments/E017-external-real-user-corpora/results-v0.md`
- CPython X1 partial repair: `experiments/E017-external-real-user-corpora/cpython-d2-x1-result-v0.md`
- E015 realistic shadow: Issue #38
- E013 realistic workload gate: Issue #21
- Optional VS Code-native exact-Luna adapter: Issue #24
- Alpha readiness/convergence: `docs/09-alpha-core-readiness-gate.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`
- Dogfood docs: `dogfood/README.md`, `dogfood/vscode/README.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins and this file must be corrected immediately**.
