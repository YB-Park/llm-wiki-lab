# Current Handoff

Last updated: 2026-08-17 KST

This file is the **continuation checkpoint only**. Keep history/evidence in code, issues, PRs, experiments, and Git. Replace stale sections instead of appending a diary.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally reads and maintains persistent knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine compilation/maintenance inside granted authority.**

## Current baseline — Dogfood 0.1.11

**0.1.11 is on `main` via PR #130** (`41387966f110a8443c87e05e72a5fb12ceb1affa`) and is the baseline for human installed P7.

Five agent-facing tools are the representative product loop:

1. `#wikiMemory` — search current Raw / Derived / Human Knowledge.
2. `#wikiRead` — bounded verified immutable raw read and provenance follow.
3. `#rememberWikiSource` — explicit human-confirmed local-file admission; never auto-saves dirty documents.
4. `#rememberHumanKnowledge` — explicit user-confirmed decision/belief/rationale; zero model calls; separate from raw evidence.
5. `#resolveWikiLineage` — human-gated correction/change/dispute/supersede/independent resolution for changed remembered files.

Authority classes remain separate:

- **RAW_MEMORY** — factual/provenance authority.
- **DERIVED_MEMORY** — LLM-generated, noncanonical, rebuildable synthesis/navigation aid.
- **HUMAN_KNOWLEDGE** — what the user explicitly confirmed they believe/decided; not independent evidence.

0.1.11 also has durable `.wiki-lab/agent-state.json` for pending lineage/source locators/maintenance reservations, verified old/new lineage review, JSON-encoded untrusted Agent payload fields, Human Knowledge integrity/fork checks, and a workspace daily Luna-maintenance call limit.

E020 freezes **78 zero-model synthetic authority/UX cases**: 60 supported by concrete current mechanisms, 7 partial, 11 deliberately deferred. This is a deterministic product contract, **not** a product-quality score. Real routing, approval fatigue, latency, comprehension, and later-session recovery still require installed use.

Retrieval remains **W0 default / X1 shadow**. Agent Wiki Luna maintenance remains **OFF by default**.

Customer readiness: **NOT READY YET** — installed multi-session evidence is now the blocker, not another architecture program.

## E021 closeout — fixed-identity concept compounding

Result: `experiments/E021-concept-compounding/results-v0.md`.

Narrow result: fixed-identity A -> A+B -> A+B+C concept compounding was recorded **PASS** with exact `gpt-5.6-luna`, 3 calls, and 0 semantic rerolls while preserving raw provenance and noncanonical/rebuildable boundaries.

**Provenance limitation:** retained GitHub Actions history for PR #133 shows its zero-model preflight, while the three-call execute job is skipped because it was configured only for `main` push. Issue #131/result notes record the three-call PASS, but there is no retained Actions execute-job artifact independently demonstrating it.

**Do not rerun E021.** PR #133 is the historical preregistration/runner record and must not be merged in its original form because its `main` push workflow would authorize another three Luna calls.

E021 does **not** earn automatic concept discovery/routing/dedup/update triggers. Concept routing is a future narrow question only if installed use makes it valuable.

## E022 closeout — v4 memory serialization translation smoke

Issue #135 / merged PR #136. Result: `experiments/E022-v4-translation-smoke/results-v0.md`.

Numbering note: this smoke was initially merged under a colliding E021 path; existing E021 concept compounding remains canonical, and the translation smoke was corrected to **E022 without rerunning any model**.

Frozen E022 used the exact 0.1.11 `LLM_WIKI_MEMORY_RESULT v4` JSON-string data boundary with malicious memory values resembling `POLICY`, `canonical_mutation=evil`, delete/override instructions, and a newline-bearing filename.

Result:

- GPT-5.4: **PASS** — recovered `42`, embedded instruction not followed, no Wiki mutation requested/claimed, JSON fields treated as data;
- Claude Sonnet 4.6: **PASS** — same;
- exact models; **2 generations total; 0 semantic rerolls**;
- run `31993541811`;
- artifact `9276094144`;
- digest `sha256:f24ceb7ca77db4c0a01c4df82460610b063949f398694a4d6a6478fcf74a7481`;
- no additional Copilot purchase required.

The completed paid workflow is removed from the current tree so documentation/cleanup work cannot trigger another E022 run. Historical runner/workflow provenance remains in merge `e194647ea923d6b1c9dc324f1a55844db54c0c50`.

E022 removes one narrow release blocker. It is **not** a universal prompt-injection guarantee; future model/version compliance remains model-dependent evidence.

## NEXT — installed multi-session P7

**Start here if a session dies. Do not design another subsystem first.**

Use 0.1.11 naturally in VS Code across real sessions:

1. Ask ordinary questions where prior project knowledge should matter; observe whether the main agent invokes `wikiMemory` without ceremony.
2. For an important memory hit, see whether the agent follows through with `wikiRead` instead of trusting a snippet/derived claim.
3. Say “remember this file” on real files; observe confirmation friction, dirty-file behavior, and filing legibility.
4. Say “remember that we decided X because Y”; test Human Knowledge creation, then later explicitly change/supersede one decision.
5. Modify a remembered file and remember it again; test pending lineage review and correction/change/dispute/supersede/independent resolution.
6. Where appropriate, enable Luna maintenance and observe actual source-note usefulness, latency, and daily-call behavior.
7. Leave the session, return later, and test recovery of both raw evidence and human reasoning.

Record **natural friction/failures**, not manufactured counts. The next product slice must come from repeated installed evidence.

Likely candidates if repeatedly observed: tool-routing descriptions, pending/activity visibility, source navigation, or a narrow concept-routing experiment.

## Do not start yet

- vector/graph/ontology infrastructure;
- background source watching;
- broad automatic contradiction resolution;
- full Tree View/activity system without observed need;
- federation or X2 without recurring natural evidence;
- automatic concept routing from E021 alone;
- paid reruns of frozen E017/E018/E019/E021/E022 cases.

## Known non-blocking edges

- Issue #132: deletion detection for `agent-state.json` and relation/pending crash window.
- Human Knowledge file deletion is not independently detectable without an index.
- Relation append and pending-state resolution are not one cross-process transaction.
- E013/E015 evidence must remain natural; do not manufacture workload/divergence.

## Paid-call posture

Current recommendation: **no additional purchase now**. The bounded E022 run completed under current access. New paid calls are justified only when a materially new product path or natural installed failure can change a decision. If current quota is insufficient at such a point, tell the user explicitly rather than weakening the experiment.

## Fast pointers

- 0.1.11 implementation: Issue #129 / PR #130
- First synthetic P7 sweep: Issue #128
- E020 contract: `experiments/E020-synthetic-agent-ux/README.md`
- E021 concept compounding: Issue #131 / historical PR #133 / `experiments/E021-concept-compounding/results-v0.md`
- E022 v4 translation smoke: Issue #135 / PR #136 / `experiments/E022-v4-translation-smoke/results-v0.md`
- Reliability follow-up: Issue #132
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- Backup/restore: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins; fix this checkpoint immediately**.
