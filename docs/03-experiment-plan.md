# Experiment Program

This is the **current experiment map**, not a historical catalog. Detailed preregistrations, frozen corpora, outputs, and analyses live under `experiments/`; accepted policy lives in ADRs. Update this file when the active program changes instead of appending old critical paths indefinitely.

## Experimental principles

1. Compare alternatives on the same corpus/questions when a controlled comparison is the right tool.
2. Freeze important protocol/scorer choices before looking at held-out results when practical.
3. Preserve negative and ambiguous results.
4. Separate measured result from interpretation and policy.
5. Pair LLM evaluation with deterministic checks or sampled human review where practical.
6. Measure lifecycle/model/human cost, not just one-shot answer quality.
7. Use synthetic/controlled data for mechanism questions and real dogfood for product/workload questions.
8. Do not manufacture realistic evidence to satisfy a readiness threshold.
9. Do not spend model calls on deterministic questions merely because credits are available.
10. A successful experiment does not automatically authorize production promotion; follow the stated decision boundary.

## Evaluation dimensions

### Trust / integrity

- raw/evidence identity correctness;
- history preservation;
- temporal/dispute correctness;
- provenance reversibility;
- corruption/data-loss containment;
- unsupported or stale derived claims.

### Retrieval / answer utility

- target-source recall and rank;
- exact/provenance success;
- synthesis/decision-history utility;
- temporal/disagreement awareness;
- source-follow rate;
- wrong/missing/incomplete answer feedback.

### Product utility

- steps/ceremony for capture, recall, verification, and correction;
- forgotten-location recovery;
- terminal escapes from the VS Code-first surface;
- repeated-session usefulness;
- abandoned/avoided actions;
- original-source navigation quality;
- operational safety such as backup/restore.

### Lifecycle / economics

- model calls/tokens per ingest/update/query;
- revisits per authoritative update;
- maintenance actions and repair effort;
- human review burden;
- whether a derived/compiled layer earns reusable value.

## Corpus strategy

Use both:

- **Controlled corpora** for known-ground-truth failure mechanisms and held-out comparisons.
- **Realistic corpora** for emergent friction and workload distributions.

The actual `llm-wiki-lab` repository is now an explicit self-hosting realistic corpus in E010. Private/company data must not be copied into public experiment artifacts.

## Completed evidence that currently constrains the architecture

These are not the active critical path; consult their experiment directories/ADRs for detail.

- **E007 long-horizon contamination:** established that recursive derived reuse can compound error and that raw/source verification boundaries matter.
- **E009 / E009A commit-boundary work:** informed risk-sensitive canonical mutation discipline.
- **E011/E012 persistent-compilation value/economics:** found a credible controlled high-reuse synthesis/decision region, with a roughly three-revisit-per-authoritative-update break-even in the frozen maintenance benchmark; exact/provenance remained a reason to preserve raw-backed routing. This did **not** authorize default compiled state.
- **E014 v0 / E014-R1:** whole-object lexical dilution was real; indexed overlapping windows failed the formal gate; rank-then-expand survived a fresh held-out gate and became non-default X1 shadow only.
- **E003:** minimum explicit generic/correction/change/dispute semantics passed its deterministic gate and became ADR-0005.
- **E004:** exact raw-span provenance Gate A passed; the tested selective dual-bookkeeping policy failed. ADR-0006 accepts only the narrow local exact-pointer capability.
- **Alpha integrity/red-team:** raw identity, canonical log containment, answer boundary, local privacy, atomic raw publication, and missing-manifest fail-closed behavior are implemented and regression-tested.

## Active experiments / gates

### E010 — VS Code product dogfood and self-hosting gate

**Status: ACTIVE.**

Question: is the trustworthy core actually a product a VS Code + Copilot user can live with?

The first full-repository automated stage is complete:

- 272/272 tracked UTF-8 files ingested;
- 1,602,314 bytes;
- 12/12 preregistered project questions recovered an expected source in W0 top-5;
- MRR 0.753;
- 12/12 non-empty provenance contexts;
- zero model calls.

This validates self-hosting retrieval capability, **not customer readiness**.

Concrete E010 product blockers now drive work:

1. original workspace source navigation is ambiguous because ingest keeps basename but no safe relative locator; the repository has 22 duplicate-basename groups;
2. correction/change/dispute semantics exist in core but are not first-class VS Code operations;
3. E013 feedback is not first-class in VS Code;
4. VS Code recall assumes a selected/remembered topic;
5. there is no primary backup/restore operating story for valuable local knowledge;
6. the actual VS Code/Copilot exact-Luna path still needs a real user session;
7. repeated multi-session habitability remains unmeasured.

See `experiments/E010-vscode-dogfood/`.

### E013 — realistic revisit/update/query-mix calibration

**Status: ACTIVE / NATURAL DATA REQUIRED.**

Question: does the controlled high-reuse region for persistent compilation occur materially in real use?

Current preregistered readiness floor:

- >= 10 topics with query activity;
- >= 20 completed maintenance cycles;
- >= 30 sessionized visits.

Key outputs include revisit/update distribution, query-class mix, provenance-follow rate, concentration, and a go/narrow/kill decision for any durable compiled provider.

Synthetic activity must not be used to satisfy this gate.

### E015 — realistic W0 vs X1 retrieval shadow calibration

**Status: ACTIVE / NATURAL DATA REQUIRED.**

Question: how often does the E014-R1 structural-expand mechanism materially change realistic topic-scoped retrieval?

W0 remains user-visible/default. X1 runs deterministically in privacy-minimal shadow with zero extra model calls. Disagreement frequency alone cannot prove X1 is better; it only determines whether a later quality trial on real divergent cases is worth doing.

### Issue #24 — VS Code-native exact-Luna adapter spike

**Status: REAL-SESSION GATE PENDING.**

Zero-generation discovery tooling is already shipped. The remaining step must run in the user's actual VS Code/Copilot Pro session:

1. inspect sanitized Copilot model metadata;
2. require exact `id` or `family == gpt-5.6-luna`;
3. reject fuzzy/silent fallback;
4. only if exact Luna exists, permit <=2 tiny synthetic native-generation smoke calls before an adapter decision.

GitHub Actions cannot substitute for this evidence.

## Parked experiment families

Do not revive these just because they are interesting. Reopen when active dogfood or E013/E015 produces a concrete need.

- E001 representation/knowledge-unit variants;
- E002 immediate vs staged derived consolidation;
- E005 split/merge policy;
- E006 retrieval escalation architecture;
- E008 error-book learning;
- verifier/regression experiments for compiled edits;
- taxonomy/schema evolution;
- claim graph / entity graph;
- automatic contradiction/relation inference;
- vector/embedding/graph retrieval bake-offs.

## Artifact discipline

A substantial experiment should keep enough material for replay/inspection under its own directory, typically:

```text
experiments/E###-short-name/
  README.md            # question/protocol/boundaries
  corpus/              # when a controlled corpus exists
  prompts/             # when model prompts matter
  runs/ or results/    # measured outputs
  analysis*.md         # interpretation / threats / decision boundary
```

For real dogfood, privacy may forbid raw event/query artifacts from entering the public repo. In that case commit only the preregistered protocol and sanitized aggregate evidence that is safe to share.

## Current critical path

1. **E010 product blockers:** fix source navigation, VS Code temporal operations, feedback, forgotten-topic recall, and backup/restore safety narrowly.
2. **Issue #24 real-session exact-Luna gate.**
3. **Repeated E010 dogfood:** use the installed product across multiple sessions and tasks; collect actual friction and usefulness.
4. **E013 natural evidence:** decide whether any persistent compiled region earns activation.
5. **E015 natural evidence:** decide whether realistic retrieval divergence merits a quality trial/default reconsideration.
6. Reopen parked research only when one of the above produces a concrete observed need.

The program is now deliberately **product/reality-first**. Core infrastructure is no longer the default place to look for progress.
