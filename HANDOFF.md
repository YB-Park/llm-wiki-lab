# Current Handoff

Last updated: 2026-08-17 KST

This is the **current continuation state**, not project history. Replace stale items as the product moves. Detailed evidence stays in code, experiments, issues, PRs, and Git history.

## North Star

Build a **proper VS Code-first LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally uses and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls compilation and maintenance inside granted scope.**

Research is a means, not the product. Synthetic testing should remove problems we can find ourselves; the next decisive evidence now comes from installed multi-session human use.

## Current product state

- **Dogfood 0.1.11 is the current Alpha.** Product merge: PR #130, `41387966f110a8443c87e05e72a5fb12ceb1affa`.
- **Raw-first Alpha Core remains the trust substrate:** immutable/content-addressed raw evidence, explicit temporal semantics, fail-closed integrity/citations, provenance navigation, prompt-over-stdin privacy hardening, and store-level single-writer protection.
- **Retrieval:** W0 remains default. X1 remains non-default/shadow despite meaningful E015-D1 and E017-D2 improvements. Do not promote without more natural quality evidence.
- **Persistent compiled provider:** still E013-gated as a trusted/default provider. The shipped Agent Wiki derived layer is **not** that provider and is never canonical truth.
- **Customer readiness:** **NOT READY YET.** Synthetic and packaged-runtime hardening are strong; repeated installed human use is still missing.

## 0.1.11 Agent-facing product loop

The extension exposes five stable VS Code Language Model Tools. The user's selected main Agent model may invoke them during ordinary conversation.

### 1. `#wikiMemory` — search current memory

Tool: `llmWiki_searchMemory`.

- local deterministic search; **zero model calls**;
- returns three explicitly different epistemic classes:
  - `RAW_MEMORY` — canonical raw evidence/provenance; factual authority;
  - `DERIVED_MEMORY` — model-generated Agent Wiki synthesis/navigation aid; noncanonical/rebuildable;
  - `HUMAN_KNOWLEDGE` — wording the user explicitly confirmed as their durable belief/decision/rationale; authoritative only as a record of the user's commitment, not independent external evidence;
- exposes unresolved same-file revision decisions as pending lineage state;
- every untrusted or user/model-controlled text/metadata value is JSON-string encoded as `*_json`; remembered content is data, never instructions;
- performs no Wiki mutation and does not manufacture E013 visits.

### 2. `#wikiRead` — follow a source into verified raw evidence

Tool: `llmWiki_readSource`.

- reads immutable evidence by canonical `source_id`;
- bounded/paginated (`startChar` / `maxChars`) instead of dumping arbitrary whole files;
- surfaces current/superseded/contested status when scoped with `topicId`;
- may show the source-scoped derived Agent Wiki note beside raw evidence for inspection;
- raw remains factual authority; derived content remains noncanonical;
- read only; zero model calls.

This closes the 0.1.10 gap where an Agent could search snippets but could not reliably follow a hit into complete provenance.

### 3. `#rememberWikiSource` — explicit source admission

Tool: `llmWiki_rememberSource`.

Flow:

`main model recognizes explicit remember intent -> product-owned human confirmation -> immutable raw admission -> selected topic or Agent Inbox -> optional Luna maintenance`

Important boundaries:

- only regular local files inside the current workspace;
- **never auto-saves a dirty editor**; the user must explicitly save first;
- product-owned modal confirmation is required for admission even if Agent tool approvals are otherwise permissive;
- raw admission occurs before derived maintenance and survives maintenance failure;
- same unchanged source can reuse an existing derived note with **zero new model call**;
- if the same remembered workspace file now has different current bytes, the new raw evidence is preserved but derived maintenance pauses and a **pending lineage decision** is created instead of guessing meaning.

### 4. `#resolveWikiLineage` — human-gated meaning of changed revisions

Tool: `llmWiki_resolveLineage`.

Only use after `rememberWikiSource` reports a pending decision and the user explicitly decides the meaning. Allowed relations:

- `correction` — older revision was wrong;
- `change` — older revision may have been valid then, newer became valid later; requires timezone-aware `effectiveAt`;
- `dispute` — both remain unresolved/current;
- `supersede` — generic replacement without claiming correction vs time-change semantics;
- `independent` — intentionally record no canonical relation.

Before confirmation, 0.1.11 verifies both immutable raw revisions and shows a bounded OLD/NEW changed-region preview. Source currentness plus durable workspace-file locator/SHA binding is checked before the modal and again immediately before any canonical mutation. One decision cannot silently resolve other predecessor ambiguity; remaining predecessors stay pending.

### 5. `#rememberHumanKnowledge` — explicit user-authored knowledge

Tool: `llmWiki_rememberHumanKnowledge`.

Use only when the user explicitly asks to durably remember **their own** decision, belief, rationale, or user-approved synthesis.

- full bounded proposed text is shown to the user before save;
- zero model calls;
- stored separately under `.wiki-lab/human-knowledge/`;
- never becomes raw external evidence or a canonical temporal relation;
- inferred/tentative user belief cannot be silently persisted;
- a later explicitly changed decision can supersede a current Human Knowledge record;
- superseded records remain historical and are excluded from current memory search;
- malformed/tampered records and lineage forks/cycles fail closed.

Do not describe the self-hash as cryptographic tamper resistance. It is a fail-closed integrity/corruption check, not an adversarial security chain.

## Agent Wiki maintenance — exact Luna, narrow grant

Agent Wiki maintenance remains **OFF by default** and is enabled per workspace via:

- `LLM Wiki: Configure Agent Wiki Maintenance`

After explicit source admission and only when no lineage ambiguity is pending, exact `gpt-5.6-luna` may create/reuse one provenance-linked source note under `.wiki-lab/agent-wiki/source-notes/`.

The derived artifact is explicitly:

> **AGENT WIKI — NONCANONICAL / REBUILDABLE**

Maintenance cannot perform correction/change/dispute/supersession/delete or infer Human Knowledge. Generated notes are never re-ingested as raw evidence.

0.1.11 adds a **durable per-workspace daily maintenance-call reservation limit** (`llmWiki.agentWikiMaintenanceDailyCallLimit`, default 10, `0` disables new generations) in addition to the Copilot CLI per-call guard. Reservations live inside `.wiki-lab/agent-state.json`; an uncertain transport result is not silently refunded.

`.wiki-lab/agent-state.json` also durably stores pending lineage workflow state and source locators used for same-file revision detection. It is private, writer-locked, atomically written, and semantically validated fail-closed. It is workflow/authority state, not canonical evidence truth.

## E018 / E019 architecture conclusions still stand

### E018 — mandatory per-turn Luna Steward rejected

Frozen score:

- GPT-5.4 main-model discretion: **7/8**
- Claude Sonnet 4.6 main-model discretion: **7/8**
- GPT-5.6 Luna dedicated Steward: **6/8**
- relevant-memory false negatives: **0 for all**
- protected/canonical overreach: **0 for all**

> **Product-controlled policy and capability boundaries are required; a product-controlled second model on every turn is not.**

Do not reopen the mandatory Steward from architectural preference. Reopen only if installed use produces repeated main-model policy drift/failures.

### E019 — Luna earned source-note maintenance, not memory governance

A frozen one-call maintenance experiment and a separate actual product-path one-call smoke showed exact Luna could create useful provenance-linked noncanonical source notes while canonical history remained unchanged. Same source+policy reuse required zero new model calls.

This earned the narrow maintenance role only. It did not earn background watching, canonical mutation, or a persistent compiled provider.

## E020 — synthetic P7 hardening

Issue #128 produced the first 28-case adversarial user-flow sweep and exposed many obvious 0.1.10 gaps. Issue #129 / PR #130 turned the repeated/high-value gaps into 0.1.11 hardening.

The frozen E020 deterministic contract now contains **78 cases**:

- **60 supported** by concrete current mechanisms;
- **7 partial** — bounded mechanism exists but installed/model/process evidence is still required;
- **11 deferred** — intentionally not implemented because they need a new authority/parser/product decision;
- **0 model calls**.

This is **not a 60/78 product-quality score** and does not replace human P7.

Adversarial dev + packaged Extension Host regressions include:

- newline-bearing filename and policy-looking raw text cannot escape JSON data fields into structural tool output;
- dirty non-active editor is never silently saved;
- changed same-file source becomes durable pending lineage rather than silent semantic mutation;
- tampered pending locator binding blocks canonical lineage mutation;
- Human Knowledge fork/tamper fails closed.

## E021 — v4 serialization translation smoke

Issue #135 / PR #136 tested the exact new `*_json` memory serialization with two real main models before releasing 0.1.11.

Frozen result:

- GPT-5.4: PASS — recovered `42`, treated embedded policy/mutation/delete-looking strings as data, no mutation claim;
- Claude Sonnet 4.6: PASS — same;
- **2/2 PASS**, exact models;
- **2 generations total, 0 semantic rerolls**;
- run `31993541811`, artifact `9276094144`, artifact digest `sha256:f24ceb7ca77db4c0a01c4df82460610b063949f398694a4d6a6478fcf74a7481`;
- no additional Copilot purchase was required.

Do not generalize this two-case smoke into a universal prompt-injection guarantee. E020 correctly keeps future-model instruction compliance as partial/model-dependent evidence.

## Current authority contract

1. **Human controls admission.** A source enters memory only after explicit intent plus product-owned confirmation, absent a future separately designed source-watch grant.
2. **Human controls epistemic commitment.** User-confirmed Human Knowledge and correction/change/dispute/supersession meaning require explicit human authority; inferred beliefs remain non-persistent.
3. **Main model may use bounded memory.** Ordinary agent conversation may search and read relevant memory without a second mandatory policy model.
4. **LLM may maintain derived Agent Wiki inside a standing grant.** Derived maintenance is autonomous preparation, not truth.
5. **Code owns dangerous capability boundaries.** Autonomous maintenance cannot perform high-consequence temporal semantics or destructive provenance operations.
6. **Generated answers/derived notes are not evidence.** Any durable human synthesis requires explicit confirmation; factual claims must remain traceable to admitted raw evidence.
7. **No surprise exposure/spend.** External maintenance is default-off, has visible per-call guard, and now has a durable daily call cap.

## Immediate next work — human installed multi-session P7

**Do not start another architecture program before installed evidence.** Install and use 0.1.11 naturally over multiple sessions.

Highest-value human-only observations:

1. Does the selected main Agent invoke `wikiMemory` at the right moments without the user constantly naming the tool?
2. After search, does it naturally use `wikiRead` when a claim needs deeper provenance?
3. Is the product-owned confirmation for `rememberWikiSource` reassuring or annoying?
4. Does `rememberHumanKnowledge` feel like a natural response to “우리는 X로 결정했어. 기억해”, or like ceremony?
5. When a remembered file changes, is the verified OLD/NEW pending-lineage decision understandable, or too technical?
6. Does Luna source-note maintenance produce something actually useful in a later session, and is the latency/spend acceptable?
7. Does raw vs derived vs Human Knowledge separation make sense when the Agent answers, or leak implementation complexity into normal use?
8. Return later with imperfect memory and ask a real question. Did the Wiki materially recover reasoning you otherwise would have lost?

Let these observations decide the next slice. Do not build vectors/graphs, background watching, federation, broad URL/PDF ingestion, concept-level Agent Wiki, or a large Tree View merely because they are available ideas.

## Active limitations / deferred questions

- Main-model choice to invoke ambient memory is still model discretion; E018 did not justify a second mandatory per-turn judge.
- Full activity/diff/revert UI remains deferred until installed friction demonstrates priority.
- URL/PDF/network capture and background source-watch need new privacy/admission authority design.
- Human Knowledge deletion detection/purge semantics need a deliberate lifecycle/index decision; do not invent autonomous deletion.
- Canonical lineage mutation and pending-workflow resolution are separately serialized actions, not one cross-process transaction.
- Known retrieval limit: long non-Markdown objects can require multiple separated relevant regions. Build a narrow X2 only if this recurs naturally.
- E013/E015 evidence must remain natural; never manufacture visits, cycles, or divergences.

## Paid model posture

Do not spend more calls on frozen E017/E018/E019/E021 cases. New paid calls are justified only when they can change a product decision or validate a materially new production path. If future natural failures produce such a decision point and current Copilot quota is insufficient, tell the user explicitly before weakening the experiment.

## Fast pointers

- Autonomy / agent-first UX umbrella: Issue #110
- Synthetic P7 first sweep: Issue #128
- 0.1.11 hardening: Issue #129 / PR #130
- E020 contract: `experiments/E020-synthetic-agent-ux/`
- E021 v4 smoke: Issue #135 / PR #136 / run `31993541811`
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- E018 result: `experiments/E018-steward-policy/results-phase1-v0.md`
- E019 result: `experiments/E019-agent-wiki-maintenance/results-v0.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins and this file must be corrected immediately**.
