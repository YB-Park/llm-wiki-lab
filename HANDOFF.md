# Current Handoff

Last updated: 2026-08-21 KST — 0.1.17 L0 Query Plane installed-dogfood posture

This is a **living continuation checkpoint**, not project history. Historical experiments, PR choreography, review detail, and frozen results belong in their source docs/issues/Git.

If this file conflicts with merged code or an accepted ADR, code/ADR wins. Before repo work, re-check current `main` and open work.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Current product posture:
- installed baseline remains **0.1.16** until the next installed smoke replaces it;
- **0.1.17** is the next opt-in installed-dogfood candidate and adds the earned L0 Luna-backed Wiki Query Plane;
- current product decision: **GO for installed self-dogfood / Alpha use**;
- public Beta: **not declared**;
- primary product-evidence track: **Issue #141 natural installed dogfood**;
- paid E023 semantic calls: **paused**;
- 0.1.16 artifact remains a frozen historical baseline and must not be silently replaced under the same version.

## Why 0.1.17 exists

E024 tested whether Wiki retrieval/composition could be kept out of the Main Agent context while preserving terminal authority. The frozen Q1 result earned the L0 Query Plane:
- 18/18 exact `gpt-5.6-luna` paired calls completed;
- Query Plane semantic adjudication: **9/9 PASS**;
- critical failures: **0**;
- paired regressions: **0**;
- Main-visible Wiki character ratio: median **5.19%**, max **7.62%**;
- max compact brief: **583 chars**.

E024 earned **bounded one-shot retrieval/composition isolation**, not iterative agentic retrieval. L1 remains **NOT EARNED**.

## 0.1.17 architecture

```text
Main Agent
   │ wikiConsult(self-contained question)
   ▼
Query Controller
 local grant / current-store scope / user-chosen usage guards
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

Authority Core stays below this layer and is not redesigned by the Query Plane.

## 0.1.17 authority and privacy floor

Treat these as product invariants unless a separate evidence-backed decision changes them:

- workspace use remains explicit opt-in and trusted-workspace only;
- workspace disable makes Agent tool runtime implementations non-invokable while preserving Wiki data;
- disabling and later re-enabling project memory invalidates the previous Query Plane grant; query reasoning must be explicitly granted again;
- `Check Setup and Health` remains **0 model calls / 0 state changes**;
- `RAW_MEMORY` stays immutable admitted evidence/provenance authority;
- `DERIVED_MEMORY` remains noncanonical, rebuildable, and navigation-only;
- `HUMAN_KNOWLEDGE` remains explicit user-owned knowledge, not independent external factual corroboration;
- pending lineage is workflow state, never terminal authority and never model-resolved automatically;
- source admission, Human Knowledge authorship, and lineage semantics stay human-gated;
- Query Plane is read-only and cannot mutate canonical epistemic state;
- Query Plane permission is separate from workspace opt-in, source admission, and AI-summary maintenance permission;
- Query Plane grant lives in local VS Code `workspaceState`, not a committable workspace setting;
- no product-owned hidden Query Plane spend default exists: the user explicitly chooses both a daily model-call-attempt cap and a per-response Copilot AI-credit soft guard before the grant exists;
- the local daily counter is not an exact billing/token/AI-credit estimate;
- the per-response provider guard must be enforceable by the installed Copilot CLI or Query Plane fails before a model call;
- query usage reservation happens before the model attempt and uncertain attempts are not silently refunded;
- `wikiConsult` never silently falls back to broad `wikiMemory` raw context on disabled, budget-paused, unavailable, or verification-failure states;
- selected candidate verification failure fails the consult closed;
- long-source evidence uses bounded deterministic **query-relevant verified regions**, not a fixed first-6k read;
- RAW and DERIVED navigation hints for the same source may be deterministically merged for region selection, but DERIVED never becomes terminal authority;
- `wikiMemory` and `wikiConsult` share one Memory Read Service so candidate/authority semantics do not drift independently;
- terminal Wiki Brief refs are scope-qualified and may terminate only on RAW/HUMAN_KNOWLEDGE;
- exact model for this slice is `gpt-5.6-luna`;
- composer evidence travels through stdin and the actual Copilot subprocess runs from a neutral temporary cwd;
- Query Plane transport strips generic `GH_TOKEN`/`GITHUB_TOKEN`, Copilot allow-all/model overrides, and `COPILOT_PROVIDER_*` routing overrides before launching the composer;
- current generic read/write/url/memory/web-search tool names remain in the Query Plane exclusion boundary in addition to existing hardened adapter exclusions;
- no hidden chain-of-thought or retrieval transcript is returned;
- existing `wikiMemory`/`wikiRead` remain available for explicit low-level provenance/debug fallback;
- no L1 iterative retrieval, federation, graph/vector/entity layer, semantic persistence, or canonical mutation is opened by 0.1.17.

## Versioned query policy

The current-store L0 policy is represented as the versioned internal query profile `current-store-l0-v1`.

Do not turn current candidate counts, top-k values, or region sizes into universal architectural truths. Revise query profiles only from evidence while preserving the authority floor.

## Future federation compatibility

Cross-workspace Personal Wiki Library/federation (#202) and Query Plane (#204) remain separate axes:
- federation decides **which stores are authorized/searchable**;
- Query Plane decides **who performs retrieval/composition and what reaches the Main Agent**.

0.1.17 searches only the current store. Terminal references already carry a scope shape so future federation can add store-qualified refs without replacing the Main-Agent `wikiConsult` contract.

Future rule remains: authorization is resolved **before retrieval/scoring/model exposure**. Luna never widens scope.

## E020 deterministic contract

The existing synthetic product contract remains:

**78 zero-model cases: 60 supported / 7 partial / 11 deferred.**

Ambient candidate collection now lives in the shared Memory Read Service. E020 may follow that product seam, but its case judgments must not be changed merely to accommodate implementation movement.

## E023 closure invariants remain closed

The Query Plane product slice does not reopen persistence/identity research.

- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning remain unauthorized as a tuning loop.
- paid E023 semantic calls: **paused**.

Frozen E023 continuation marker: **Run the Day-0 installed smoke on the exact 0.1.16 VSIX**. E024 later earned a separate 0.1.17 Query Plane slice without changing the E023 G2/G3 verdicts or Issue #141's role as the primary natural product-evidence track.

## Installed dogfood rollout

Do not immediately retire the proven low-level memory path.

For 0.1.17 installed dogfood:
1. install the validated 0.1.17 VSIX in one trusted single-folder workspace;
2. verify existing project memory, source admission, Human Knowledge, and lineage behavior first;
3. keep Query Reasoning off and confirm the baseline path still works;
4. explicitly enable Query Reasoning and choose both local usage guards;
5. smoke one real `wikiConsult` question;
6. verify a compact brief, terminal refs, no raw-context fallback, and no canonical mutation;
7. disable project memory, re-enable it, and verify the old Query Plane grant does not revive;
8. then use naturally rather than manufacturing benchmark coverage.

Natural evidence should decide whether `wikiConsult` later becomes the ordinary preferred memory path.

Observe:
- Main-visible Wiki chars/tool turns;
- repeated `wikiRead` follow-up rate;
- latency;
- conservative vs excessive insufficiency;
- long-source authority recovery;
- pending/history behavior;
- grant/usage-guard comprehension;
- whether deterministic bounded evidence without Luna remains a viable competing hypothesis.

## Research posture

- E023 G1 exploratory retrieval/composition mechanism search: closed.
- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**
- E024 L0 Query Plane: **EARNED for opt-in product dogfood**.
- E024 L1 iterative Librarian: **NOT EARNED**.

Retained principle:

> A representation may preserve authority globally while a later selection bottleneck destroys it locally.

Query Plane principle:

> Hide retrieval/composition work from the Main Agent's context, not terminal provenance from the user/system.

## Known reliability edges

Issue #132 remains evidence-gated:
- `.wiki-lab/agent-state.json` deletion is not independently detectable;
- canonical lineage append and pending workflow-state resolution are not one transaction;
- Human Knowledge file deletion is not independently detectable without an index.

Do not preemptively replace storage with a DB/WAL merely because Query Plane exists.

## Fast pointers

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

After the 0.1.17 package/runtime gate is green, install the validated 0.1.17 VSIX and run the short installed-dogfood rollout above. Keep the existing low-level memory path available, gather natural evidence on Issue #141, and let repeated real-world friction choose the next product slice.
