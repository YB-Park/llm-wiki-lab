# Current Handoff

Last updated: 2026-08-21 KST — parallel 0.1.17 dogfood + cross-workspace preflight

This is a **living continuation checkpoint**, not project history.
Keep only what independent continuation sessions need to decide and act now.
Historical experiments, PR choreography, branch hashes, review detail, and frozen results belong in their source docs/issues/Git.

If this file conflicts with merged code or an accepted ADR, code/ADR wins.
Before repo work, re-check current `main`, open PRs, relevant issues, and current branches; volatile repository state does not belong in this handoff.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Current product posture:
- validated **Dogfood 0.1.17** release artifact is published and ready for installed natural use;
- 0.1.17 adds the earned opt-in exact-Luna L0 Wiki Query Plane while preserving the Authority Core and low-level memory path;
- current product decision: **GO for installed self-dogfood / Alpha use**;
- public Beta: **not declared**;
- primary product-evidence track: **Issue #141 natural installed dogfood**;
- cross-workspace Personal Wiki scope is now an **active parallel design/preflight track**, not a broad runtime-federation authorization;
- paid E023 semantic calls: **paused**;
- E023 G2/G3 remain closed/parked;
- E024 L1 iterative Librarian remains not earned.

There are now **multiple independent continuation tracks**. Do not force them into one session or make one block the others unnecessarily.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval, organization, compilation, and maintenance inside granted authority.**

The next-level product direction is to let trustworthy memory cross project boundaries **without globalizing or weakening the underlying Authority Cores**.

## Parallel Track A — 0.1.17 installed natural dogfood

Primary issue: **#141**

Validated release:
- `dogfood/releases/llm-wiki-dogfood-0.1.17.vsix`
- stable path: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- SHA-256: `a0d8f19696e12dfa92d643d739fdbf5386f26f4e0338f536406ba78ac85b2962`
- validated build run: `32437729958`
- validated product head: `7348509b83202e473d3ef1925225dec39e6f5121`

Purpose:
- determine whether `wikiConsult` is genuinely useful in ordinary long-horizon Agent work;
- observe whether the Query Plane reduces Main-Agent Wiki context/turn burden without weakening provenance;
- preserve the proven low-level `wikiMemory` / `wikiRead` path as explicit provenance/debug fallback.

Natural evidence to record when it actually occurs:
- whether normal Agent questions naturally trigger the right memory path;
- compact-brief usefulness vs conservative/excessive insufficiency;
- latency and perceived interruption;
- repeated `wikiRead` follow-up rate;
- long-source authority recovery;
- pending/history behavior;
- query-grant and usage-guard comprehension;
- whether Query Plane model spend feels justified by recovered value;
- any data, authority, privacy, provenance, lifecycle, or causal-diagnostic failure.

Do **not** manufacture coverage just because a case exists in a document.
Long-horizon dogfood is intentionally slow and may continue while other zero-model/design work proceeds independently.

### Dogfood blocker rule

Fix promptly if natural installed use shows repeated or high-impact:
- data loss/corruption;
- authority/privacy violation or unauthorized model exposure;
- broken setup/disable/re-enable boundary;
- terminal provenance failure;
- misleading causal diagnostics that make recovery guesswork;
- unusable ordinary Query Plane/core path.

Accumulate evidence before implementing mild one-off friction, navigation wishes, usage dashboards, retrieval-default changes, or broader architecture.

## Parallel Track B — cross-workspace Personal Wiki / named-store federation

Primary issue and continuation source of truth: **#202**.

Status:
- **ACTIVE FOR DESIGN/PREFLIGHT + ZERO-MODEL F0 PREPARATION**;
- **not** authorized for broad runtime federation merge yet;
- the latest #202 discussion records the current off-main advisory/prereg preparation. Re-check it and current branches before continuing; do not assume prepared review/experiment files are already on `main`.

Current architecture judgment:

> **Do not globalize the Authority Core first. Globalize authorized access to multiple independent project Authority Cores.**

Preferred conceptual shape:

```text
Current trusted workspace B
        │
        ├── current project store B     read + explicit write
        │
        └── Personal Wiki Library
               deterministic authorization / scope resolution
               └── named project store A     read only
                        ↓
                 store-scoped Memory Read Service
                        ↓
                 existing Query Plane composer
                        ↓
                 scope-qualified Wiki Brief
```

### First slice is deliberately narrow

The first candidate is **named-store read-only federation**, not library-wide ambient search.

Example:
- while in B, explicitly ask how **Project A** decided something;
- resolve A deterministically before retrieval;
- retrieve only from A;
- preserve A scope on every terminal reference and raw follow-through;
- keep all default writes in B.

Do not start F0/F1 by simultaneously solving:
- library-wide union ranking;
- sync;
- Personal store writes;
- cross-project writes;
- graph/entity/ontology infrastructure;
- vector defaults;
- automatic person/identity routing;
- background cross-project maintenance;
- multi-user or multi-machine concurrency.

### Cross-workspace authority floor

Treat these as design requirements unless an evidence-backed decision changes them:
- authorization is resolved **before retrieval, scoring, candidate counts, diagnostics, or model exposure**;
- Luna never widens scope and never chooses which private store it may inspect;
- a trusted current workspace does not imply access to every registered project;
- the existing 0.1.17 Query Reasoning grant is `current_store` scoped and must not silently become a federation grant;
- external-store registration/model exposure requires a distinct explicit local grant;
- ordinary current-project questions remain current-store-only by default;
- other registered stores are read-only in the first slice;
- bare `src-...` IDs must never be routed against an arbitrary store;
- cross-store terminal provenance must include an opaque logical store scope plus the existing source identity;
- scoped provenance follow-through must read the same store that produced the hit;
- wrong-scope or ambiguous alias resolution fails closed rather than trying another store;
- inaccessible store contents must not influence scoring/IDF/ranking before being filtered out;
- project-local Human Knowledge remains a record of that project's/user's decision context, not an automatically global preference;
- a decision recovered from A does not automatically apply to B;
- external-store pending lineage must not leak into ordinary B-only results;
- external-store readability must not authorize lineage/Human Knowledge/source writes there;
- normal diagnostics should expose logical scope, not absolute private filesystem roots.

### E025 candidate

Prepared direction: **E025 — Cross-Workspace Named-Store Federation**.

F0 is intentionally **zero-model** because E024 already earned the one-shot exact-Luna composer.
F0 should test scope authority/routing/provenance/write isolation only.

Before executing or implementing from E025:
1. read #202 latest state;
2. locate and review the current advisory/prereg branch/material;
3. rebase/reconcile against current `main` as needed;
4. freeze the F0 contract before observing results;
5. make **0 model calls**;
6. require every mandatory authority case to pass before product promotion.

If F0 earns the mechanism, the next product test is a small installed **F1 named-store read-only federation** dogfood. Library-wide union search comes only after named-store scope handling proves safe and useful.

## 0.1.17 Query Plane authority and privacy floor

These remain product invariants during both tracks:
- workspace use is explicit opt-in and trusted-workspace only;
- workspace disable makes Agent tool runtime implementations non-invokable while preserving Wiki data;
- disabling and later re-enabling project memory invalidates the previous Query Plane grant;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- `RAW_MEMORY` = immutable admitted evidence / provenance authority;
- `DERIVED_MEMORY` = noncanonical, rebuildable navigation/synthesis aid;
- `HUMAN_KNOWLEDGE` = explicit user-owned decision, belief, rationale, or approved synthesis;
- pending lineage is workflow state, never terminal authority;
- source admission, Human Knowledge authorship, and lineage semantics remain human-gated;
- Query Plane is read-only with respect to canonical epistemic state;
- Query Plane permission remains distinct from workspace opt-in, source admission, and AI-summary maintenance permission;
- no hidden product-owned Query Plane spend default exists;
- user explicitly chooses daily model-call-attempt and per-response Copilot AI-credit guards;
- unsupported provider guard fails before model call;
- query usage reservation occurs before the model attempt and uncertain attempts are not silently refunded;
- `wikiConsult` does not silently fall back to broad raw `wikiMemory` context on disabled/budget/unavailable/verification failure;
- selected-candidate verification failure fails the consult closed;
- long-source retrieval uses bounded deterministic query-relevant verified regions;
- RAW/DERIVED hints may be merged for navigation, but DERIVED never becomes terminal authority;
- `wikiMemory` and `wikiConsult` share one Memory Read Service candidate/authority seam;
- terminal Wiki Brief refs may terminate only on RAW/HUMAN_KNOWLEDGE;
- exact model for the current Query Plane slice is `gpt-5.6-luna`;
- composer evidence travels through stdin and the Copilot subprocess uses a neutral temporary cwd;
- generic auth/provider/model overrides and generic read/write/url/memory/web-search tool names remain excluded from Query Plane transport;
- no hidden chain-of-thought or retrieval transcript is returned.

## E020 deterministic contract

The existing synthetic product contract remains:

**78 zero-model cases: 60 supported / 7 partial / 11 deferred.**

Do not change case judgments merely to accommodate implementation movement.
Future cross-workspace F0 cases are a separate scope-authority experiment unless deliberately promoted into the frozen product contract later.

## Research posture

- E023 G1 exploratory retrieval/composition mechanism search: closed.
- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning remain unauthorized as a tuning loop.
- paid E023 semantic calls: **paused**.
- E024 L0 Query Plane: **EARNED for opt-in product dogfood**.
- E024 L1 iterative Librarian: **NOT EARNED**.
- cross-workspace scope generality is a separate axis and does not reopen E023 persistence/identity gates.

Frozen E023 continuation marker: **Run the Day-0 installed smoke on the exact 0.1.16 VSIX**. This remains a historical closure invariant required by the E023 closure validator; later E024/0.1.17 work does not change the G2/G3 verdict.

Retained principles:

> A representation may preserve authority globally while a later selection bottleneck destroys it locally.

> Hide retrieval/composition work from the Main Agent's context, not terminal provenance from the user/system.

> Federation decides which stores are authorized/searchable; Query Plane decides who performs retrieval/composition and what reaches the Main Agent.

## Parallel Track C — reliability, only when evidence makes it material

Issue **#132** remains evidence-gated:
- `.wiki-lab/agent-state.json` deletion is not independently detectable;
- canonical lineage append and pending workflow-state resolution are not one transaction;
- Human Knowledge file deletion is not independently detectable without an index.

Do not preemptively replace storage with a DB/WAL.
Do not mix sync design into E025 F0.
If installed dogfood or a narrowly scoped federation test makes a reliability edge material, fix the smallest causal defect first.

## Session entry points

A continuation session should choose one lane explicitly after re-checking repo state:

### If taking 0.1.17 dogfood/product evidence
- read Issue #141 and this handoff;
- keep the validated 0.1.17 binary stable unless a real blocker requires a fix;
- record only meaningful natural observations;
- do not invent architecture work from a quiet dogfood period.

### If taking cross-workspace/federation
- read Issue #202 including its latest comments first;
- inspect current advisory/prereg branches and compare them with current `main`;
- continue with E025 F0 zero-model scope-authority work;
- do not merge runtime federation until the F0 promotion gate is actually earned.

### If taking persistence/identity research
- stop unless genuinely new independent evidence reopens the gate;
- G2/G3 are not available merely because a mechanism is interesting.

### If taking reliability
- read #132;
- act only on concrete product/federation evidence that makes the known edge material.

## Fast pointers

- natural installed dogfood: **#141**
- Query Plane product issue: **#204**
- cross-workspace/federation scope gate and latest continuation notes: **#202**
- reliability follow-up: **#132**
- semantic generality gate: **#160**
- current release metadata: `dogfood/releases/README.md`
- user guide: `dogfood/vscode/README.md`
- E020 deterministic contract: `experiments/E020-synthetic-agent-ux/README.md`
- E024 Query Plane experiment: `experiments/E024-query-plane-token-firewall/`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`

## NEXT ACTION

Run the project as **parallel continuations**, not one serial queue:

1. **Dogfood session:** keep 0.1.17 installed natural use running and record meaningful evidence on #141.
2. **Cross-workspace session:** read #202 latest continuation state, reconcile the prepared advisory/E025 material with current `main`, then execute/implement only the zero-model F0 scope-authority preflight until its promotion gate is earned.
3. **Reliability/research sessions:** remain parked unless independent evidence activates them.

Do not let the slow but valuable natural-dogfood timeline block safe zero-model/preflight work, and do not let speculative parallel work destabilize the validated 0.1.17 installed product.