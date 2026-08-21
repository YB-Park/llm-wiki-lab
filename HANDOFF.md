# Current Handoff

Last updated: 2026-08-21 KST — Query Plane 0.1.17 candidate / PR #207 hardening

This is a **living continuation checkpoint**, not project history. Historical experiments, PR detail, and frozen results belong in their source docs/issues/Git.

If this file conflicts with merged code or an accepted ADR, code/ADR wins. Before repo work, re-check current `main` and open PRs.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Merged baseline on `main`:
- installed dogfood baseline: **0.1.16**
- current product decision: **GO for installed self-dogfood / Alpha use**
- public Beta: **not declared**
- primary product-evidence track: **Issue #141 natural installed dogfood**
- paid E023 semantic calls: **paused**
- 0.1.16 artifact remains the frozen previous baseline and must not be silently replaced under the same version.

Active product candidate:
- **0.1.17** on `product/luna-query-plane-l0`
- PR **#207 — `L0: add opt-in Luna Wiki Query Plane`**
- PR stays **draft until implementation/release hygiene and required CI are green**.
- Once only peer review / merge approval remains, notify the project owner before merge so the original developer can perform a final peer review.
- **Do not merge #207 before that peer-review handoff.**

## Why 0.1.17 exists

E024 tested the Main-LLM token-firewall hypothesis with separated frozen material and exact `gpt-5.6-luna`.

Q1 result already merged to `main` via PR #206:
- 18/18 exact-Luna paired calls completed;
- Query Plane semantic adjudication: **9/9 PASS**;
- critical failures: **0**;
- paired regressions: **0**;
- Main-visible Wiki character ratio: median **5.19%**, max **7.62%**;
- max compact brief: **583 chars**;
- result: **L0 Query Plane promotion EARNED**.

E024 earned **bounded one-shot retrieval/composition isolation**, not iterative agentic retrieval. L1 remains **NOT EARNED**.

## 0.1.17 architecture

```text
Main Agent
   │ wikiConsult(self-contained question)
   ▼
Query Controller
 grant / current-store scope / local call cap
   ▼
Shared Memory Read Service
 RAW discovery / DERIVED navigation / Human Knowledge / pending lineage
   ▼
verified query-relevant RAW regions
   ▼
Evidence Packet
   ▼
Isolated exact-Luna Query Composer
   ▼
Deterministic result validation
   ▼
Compact Wiki Brief
 answer / scope-qualified terminal refs / insufficiency
```

Authority Core stays below this layer and is not redesigned by #207.

## Product boundaries for #207

These are merge blockers if violated:

- workspace use remains explicit opt-in and trusted-workspace only;
- workspace disable removes actual Agent tool registrations while preserving Wiki data;
- `Check Setup and Health` remains **0 model calls / 0 state changes**;
- `RAW_MEMORY` stays immutable admitted evidence/provenance authority;
- `DERIVED_MEMORY` remains noncanonical/rebuildable/navigation only;
- `HUMAN_KNOWLEDGE` remains explicit user-owned knowledge, not external factual corroboration;
- pending lineage is workflow state, never terminal authority and never model-resolved automatically;
- source admission / HK authorship / lineage semantics stay human-gated;
- Query Plane is read-only and cannot mutate canonical state;
- Query Plane grant is separate from workspace opt-in, source admission, and AI-summary maintenance permission;
- Query Plane grant lives in local VS Code `workspaceState`, not a committable workspace setting;
- a user-chosen local daily model-call-attempt cap is required before ambient query model calls;
- that counter is **not** an exact billing/token/AI-credit estimate;
- query call reservation happens before the model attempt and uncertain failures are not silently refunded;
- `wikiConsult` does **not** silently fall back to broad `wikiMemory` raw context on disabled/budget/unavailable/verification failure;
- candidate verification failure fails the consult closed;
- long-source evidence uses bounded deterministic **query-relevant verified regions**, not a fixed first-6k read;
- `wikiMemory` and `wikiConsult` share one Memory Read Service so authority/retrieval semantics cannot drift independently;
- terminal brief refs are scope-qualified and may terminate only on RAW/HUMAN_KNOWLEDGE;
- exact model remains `gpt-5.6-luna` for this candidate;
- composer evidence travels through stdin and the Copilot process is launched from a neutral temporary cwd;
- no hidden chain-of-thought/retrieval transcript is returned;
- existing `wikiMemory`/`wikiRead` remain available as explicit low-level provenance/debug fallback;
- no L1 iterative retrieval, federation, graph/vector/entity layer, semantic persistence, or canonical mutation is opened by #207.

## Versioned query policy

0.1.17 current-store policy is represented as a versioned internal query profile (`current-store-l0-v1`).

Do not turn current candidate counts/top-k values into universal architectural truths. They are internal profile mechanics that may be revised only from evidence while preserving authority boundaries.

## Future federation compatibility

Cross-workspace Personal Wiki Library/federation (#202) and Query Plane (#204) are separate axes:

- federation decides **which stores are authorized/searchable**;
- Query Plane decides **who performs retrieval/composition and what reaches the Main Agent**.

0.1.17 searches only the current store. Terminal references already carry a scope shape so future federation can add store-qualified refs without replacing the Main-Agent `wikiConsult` contract.

Future rule remains: authorization must be resolved **before retrieval/scoring/model exposure**. Luna never widens scope.

## E020 deterministic contract

The existing synthetic product contract remains:

**78 zero-model cases: 60 supported / 7 partial / 11 deferred.**

#207 moves ambient candidate collection into the shared Memory Read Service, so the E020 product-surface scanner must inspect that service rather than requiring retrieval code to physically live in `agent-tools.js`.

This is harness maintenance only: do not change E020 case judgments merely to make #207 pass.

## E023 closure invariants remain closed

The Query Plane product slice does not reopen the persistence/identity research axis.

- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning remain unauthorized as a tuning loop.
- paid E023 semantic calls: **paused**.

The previous E023 closure continuation instruction was: **Run the Day-0 installed smoke on the exact 0.1.16 VSIX**. That sentence remains here as a closure marker for the frozen E023 decision; E024 subsequently earned a separate opt-in 0.1.17 Query Plane candidate without changing the E023 G2/G3 verdicts or Issue #141's role as the primary natural product-evidence track.

## Current PR #207 validation posture

PR #207 is a **zero-model product-hardening PR**. Do not rerun a new paid E024 semantic benchmark as part of this PR.

Required before peer-review handoff:

- Python 3.9 bundled-core compatibility;
- full Python unit regression suite;
- E004 prescore validation;
- E014 R1 prescore/freeze/frozen-result validation;
- E010 self-repo dogfood;
- E020 78-case zero-model contract;
- E023 G2 closure validator remains green;
- VS Code syntax/static boundaries;
- VS Code Extension Host integration tests;
- shared-core bundle verification;
- VSIX packaging;
- packaged VSIX Extension Host execution;
- final diff audit confirming no unintended Authority Core/write-path change;
- README/HANDOFF accurately describe the 0.1.17 opt-in slice.

Recent CI fixes on #207:

1. new Query Plane unit tests accidentally imported `pytest` although repo CI uses stdlib `unittest`; converted to `unittest` rather than adding a dependency;
2. E020 scanner initially assumed ambient retrieval physically lived in `agent-tools.js`; updated scanner to follow the shared Memory Read Service without changing the 78 case judgments;
3. a static ordering check initially matched the `runComposerStdin` function definition instead of the invocation; runtime source confirmed the real order is grant → reserve call → budget gate → collect evidence → composer, and the marker was made unambiguous;
4. living HANDOFF refresh preserves the exact E023 closure markers required by its zero-model validator while clearly separating the newer E024 product slice.

Treat later CI failures as real until inspected.

## Installed dogfood rollout after peer review / merge

Do not immediately retire 0.1.16 behavior.

0.1.17 rollout is:

1. install candidate in one trusted single-folder workspace;
2. verify existing project memory / source admission / HK / lineage behavior first;
3. keep Query Reasoning off and confirm baseline still works;
4. explicitly enable Query Reasoning and choose a local daily model-call cap;
5. smoke one real `wikiConsult` question;
6. verify compact brief + terminal refs + no canonical mutation;
7. then use naturally and observe rather than manufacturing coverage.

Natural evidence should decide whether `wikiConsult` later becomes the ordinary preferred memory path.

Observe:
- Main-visible Wiki chars/tool turns;
- repeated `wikiRead` follow-up rate;
- latency;
- conservative vs excessive insufficiency;
- long-source authority recovery;
- pending/history behavior;
- grant/call-cap comprehension;
- whether deterministic bounded evidence without Luna remains a viable competing hypothesis.

## Research posture

- E023 G1 exploratory retrieval/composition mechanism search: closed.
- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- E024 L0 Query Plane: **EARNED for opt-in product dogfood**.
- E024 L1 iterative Librarian: **NOT EARNED**.

Retained principle:

> A representation may preserve authority globally while a later selection bottleneck destroys it locally.

And Query Plane principle:

> Hide retrieval/composition work from the Main Agent's context, not terminal provenance from the user/system.

## Known reliability edges not opened by #207

Issue #132 remains evidence-gated:
- `.wiki-lab/agent-state.json` deletion is not independently detectable;
- canonical lineage append and pending workflow-state resolution are not one transaction;
- Human Knowledge file deletion is not independently detectable without an index.

Do not preemptively replace storage with a DB/WAL just because 0.1.17 adds a Query Plane.

## Fast pointers

- active product PR: **#207**
- Query Plane product issue: **#204**
- natural installed dogfood: **#141**
- cross-workspace/federation advisory gate: **#202**
- reliability follow-up: **#132**
- user guide: `dogfood/vscode/README.md`
- E020 deterministic contract: `experiments/E020-synthetic-agent-ux/README.md`
- E024 Query Plane experiment: `experiments/E024-query-plane-token-firewall/`
- Query Plane advisory review: `research/advisory-reviews/2026-08-20-luna-wiki-query-plane-review.md`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`

## NEXT ACTION

Continue fixing/verifying **PR #207** until all required zero-model/runtime/package checks are green and the final diff/release docs are coherent.

Then **stop before merge**, mark/prepare it for peer review, and notify the project owner with:
- final diff scope;
- CI status;
- safety/authority boundaries;
- specific peer-review hotspots.

Merge only after that requested human peer review is complete.
