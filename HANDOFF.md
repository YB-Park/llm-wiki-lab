# Current Handoff

Last updated: 2026-08-16 KST

This is the **current continuation state**, not project history. Replace stale items as the product moves. Detailed evidence stays in code, experiments, issues, PRs, and Git history.

## North Star

Build a proper VS Code-first **LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally uses and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls compilation and routine maintenance inside granted authority.**

Research is a means, not the product. The highest-value next evidence is installed multi-session use.

## Current product state — Dogfood 0.1.11

**0.1.11 is the current human-P7 Alpha baseline.** It is the synthetic-hardening successor to 0.1.10 (Issue #129 / PR #130).

Trust substrate remains raw-first:

- immutable/content-addressed raw evidence;
- verified reads and provenance;
- explicit correction/change/dispute/supersession semantics;
- fail-closed integrity/citations;
- prompt-over-stdin privacy hardening;
- store-level single-writer protection;
- W0 retrieval remains default; X1 remains shadow/non-default.

Customer readiness remains **NOT READY YET**. 0.1.11 removes many obvious authority/UX gaps before asking a human tester to absorb them, but real installed routing/approval/latency/recovery experience is still missing.

## Agent-facing memory contract in 0.1.11

0.1.11 exposes exactly five bounded Language Model Tools:

1. `#wikiMemory` — local ambient search across current Raw, Derived Agent Wiki, and current Human Knowledge.
2. `#wikiRead` — bounded/paged **verified immutable raw read** by canonical source ID, including current/superseded/contested status when topic-scoped.
3. `#rememberWikiSource` — explicit human-confirmed local-file admission. Raw evidence first; never auto-saves dirty open documents.
4. `#rememberHumanKnowledge` — explicit user-confirmed durable decision/belief/rationale; zero model calls; separate from raw evidence.
5. `#resolveWikiLineage` — human-gated resolution of a pending same-file revision relationship as correction/change/dispute/generic supersession/independent.

### Epistemic classes stay separate

- **RAW_MEMORY** — factual/provenance authority.
- **DERIVED_MEMORY** — LLM-generated noncanonical/rebuildable synthesis/navigation aid; not independent corroboration.
- **HUMAN_KNOWLEDGE** — record of what the user explicitly confirmed they believe/decided; not independent external evidence.

Raw and derived payloads are explicitly framed as **untrusted data, not instructions**. Load-bearing claims surfaced from derived memory should follow source IDs through `wikiRead` before reliance.

## Admission / revision behavior

`rememberWikiSource` now has a product-owned human confirmation boundary; main-model tool routing alone is not enough to admit a source.

If the target is dirty in **any open VS Code document**, remember fails before Wiki mutation and never auto-saves the user's working state.

After admission:

- unchanged source identity reuses existing state;
- a changed previously remembered current revision of the same workspace file becomes a **durable pending lineage decision** instead of silently guessing correction vs time-change vs dispute;
- derived maintenance pauses while lineage is unresolved;
- if multiple predecessor candidates exist, one human choice resolves only one predecessor and a continuation decision remains for the others;
- `change` requires a timezone-aware effective instant;
- canonical relation mutation remains unavailable without explicit human confirmation.

## Durable workflow authority state

Safety-relevant workflow state is no longer only VS Code `workspaceState`.

Private `.wiki-lab/agent-state.json` stores:

- pending lineage decisions;
- same-file source locators used for revision detection;
- daily Luna-maintenance call reservations.

It is inside the whole-Wiki backup boundary and uses private atomic replacement plus the existing writer lock. Unresolved decisions are never silently evicted by a fixed-size queue.

Do **not** overclaim this as a DB/WAL transaction. Known follow-up boundaries remain:

- deletion of `agent-state.json` itself is not independently detectable;
- canonical relation append and pending-state resolution are separate process operations, not one cross-process transaction.

These are tracked separately and are not grounds to reopen a database architecture absent real failure evidence.

## Human Knowledge v1

Ordinary agent conversation can now persist an explicit user-owned decision/rationale after the product shows the **full bounded durable text** and the user confirms it.

Current limits:

- statement <= 1800 chars;
- reasoning <= 1600 chars;
- combined <= 3400 chars;
- <= 12 verified supporting raw source IDs.

Human Knowledge v1:

- uses integrity hashes and fails closed on malformed/tampered JSON;
- may explicitly supersede one **current** prior Human Knowledge record when the user says their decision/belief changed;
- keeps superseded records historically, but excludes them from current `wikiMemory` results;
- never mutates raw evidence or canonical temporal relations;
- uses zero model calls.

Known deferred boundary: deleting a Human Knowledge JSON file is not independently detectable without a durable index. Do not invent autonomous purge/forget semantics yet.

## Luna maintenance / spend contract

Agent Wiki source-note maintenance remains **OFF by default** and exact-model pinned to `gpt-5.6-luna` when the workspace grant is enabled.

0.1.11 adds a workspace **daily maintenance-call reservation limit** (default 10, configurable 0-100) in addition to the Copilot per-call guard. Reservations are persisted before a new model-backed call and are not refunded when transport outcome is uncertain.

Existing same-source/same-policy derived notes are checked for zero-call reuse before reserving spend.

No surprise model call is authorized by `wikiMemory`, `wikiRead`, Human Knowledge, or lineage resolution itself.

## E020 — synthetic P7 hardening

The first 0.1.10 sweep (Issue #128) found 28 realistic cases with 7 PASS / 7 PARTIAL / 14 GAP-or-risk. Those findings drove 0.1.11 rather than being handed to the human tester.

`experiments/E020-synthetic-agent-ux/score_contract.py` now freezes **72 scenarios** as a zero-model product contract. This is **not a product-quality score**; it explicitly keeps partial/deferred boundaries visible.

Major obvious gaps closed before human P7:

- `search -> verified read` depth;
- raw/derived prompt-injection framing;
- product-owned admission confirmation;
- dirty-target no-auto-save, including non-active open documents;
- natural agent-facing Human Knowledge write + explicit supersession lifecycle;
- durable pending lineage decisions;
- human-gated correction/change/dispute/supersession/independent semantics;
- multiple-predecessor ambiguity continuation;
- durable source identity hints and maintenance reservations;
- cumulative daily maintenance-call cap.

Still intentionally partial/deferred in E020:

- main-model decision of when to invoke `wikiMemory`;
- real approval fatigue / latency / natural routing quality;
- exact dollar budget telemetry;
- URL/PDF capture;
- background watching;
- broad semantic contradiction detection across unrelated sources;
- full activity/diff/revert UI;
- per-source forget/privacy purge;
- Human Knowledge file-deletion detection;
- cross-process relation/pending atomicity;
- X2 and federation;
- model-specific prompt-injection compliance beyond framing.

## E018 — mandatory per-turn Luna Steward remains rejected

Do not put Luna in front of every user turn without new natural failure evidence.

Frozen result:

- GPT-5.4 main-model discretion: 7/8
- Claude Sonnet 4.6 main-model discretion: 7/8
- Luna dedicated Steward: 6/8
- relevant-memory false negatives: 0 for all
- protected/canonical overreach: 0 for all

Architecture consequence remains:

> **Product-controlled policy/capability boundaries are required; a product-controlled second model on every turn is not.**

## E019 — Luna source maintenance remains supported

Luna earned a narrow **derived maintenance** role, not a mandatory policy-judge role. The shipped product path was validated as `CREATED(1 call) -> REUSED(0 calls)` with canonical history unchanged beyond raw admission.

Do not rerun frozen E019 cases for a prettier result.

## E021 — cross-source concept compounding mechanism PASS

Result: `experiments/E021-concept-compounding/results-v0.md`.

Three exact Luna calls, semantic rerolls 0, on a frozen sequence:

A. autonomy/UX philosophy
B. E018 mandatory-Steward rejection result
C. E019 Luna-maintenance support result

The same deterministic concept page accumulated across v1/v2/v3 while:

- every load-bearing string retained admitted raw provenance;
- prior generated page citations were redacted before the next update, so prior synthesis could not become evidence;
- v2 genuinely synthesized A+B;
- v3 retained A/B/C;
- v3 explicitly preserved the distinction **mandatory per-turn Steward rejected / Luna maintenance supported** with B+C provenance;
- human admission/epistemic authority from A remained present;
- page remained `DERIVED / NONCANONICAL / REBUILDABLE` with no Human Knowledge or canonical mutation claim.

This is important positive evidence that Karpathy-like **cross-source concept compounding is viable** with Luna under our trust model.

But **do not ship automatic concept routing yet.** E021 supplied a fixed concept identity and deliberately relevant source sequence. It did not test concept discovery/dedup, source-to-concept routing, update trigger policy, Agent Inbox behavior, or scale.

## Immediate next work — human installed P7

**Do not start another broad implementation program before the human test.** Install 0.1.11 and use it naturally over multiple sessions.

Highest-value loop:

1. Ask ordinary questions where prior project memory should matter. Observe whether the main agent naturally calls `wikiMemory`.
2. When a result matters, observe whether the agent follows it through `wikiRead` rather than trusting a snippet/derived claim.
3. Say “remember this file” on real workspace files. Notice confirmation friction, Agent Inbox filing, and whether dirty-file fail-closed behavior feels right.
4. Say “remember that we decided X because Y” and test Human Knowledge creation; later change a decision and see whether explicit supersession feels understandable.
5. Modify a previously remembered file and remember it again. Test the pending lineage conversation: correction vs change vs dispute vs replacement vs independent.
6. With Luna maintenance grant enabled where appropriate, observe actual source-note usefulness, latency, and daily-call behavior.
7. Leave, return later, and ask questions that should recover both raw evidence and human reasoning.

Record **natural failure/friction**, not manufactured E013/E015 counts.

The next product slice should be chosen from installed evidence. Likely candidates are tool-routing descriptions, activity/pending visibility, source navigation, or a narrow concept-routing experiment. Do not promote vectors/graphs/ontology/background watching just because E021 concept generation worked.

## Cost posture

- 0.1.11 / E020 hardening: **0 real model calls**.
- E021: **3 exact Luna calls, semantic rerolls 0**.
- No additional Copilot purchase was required.
- Do not spend more calls on frozen E017/E018/E019/E021 cases. New calls must answer a materially new product decision.

## Fast pointers

- Autonomy / agent-first UX umbrella: Issue #110
- Synthetic P7 first sweep: Issue #128
- 0.1.11 hardening: Issue #129 / PR #130
- E020 contract: `experiments/E020-synthetic-agent-ux/README.md`
- E018: `experiments/E018-steward-policy/results-phase1-v0.md`
- E019: `experiments/E019-agent-wiki-maintenance/results-v0.md`
- E021: `experiments/E021-concept-compounding/results-v0.md`
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins and this file must be corrected immediately**.
