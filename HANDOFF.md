# Current Handoff

Last updated: 2026-08-16 KST

This is the **current continuation state**, not project history. Replace stale items as the product moves. Detailed evidence stays in code, experiments, issues, PRs, and Git history.

## North Star

Build a **proper VS Code-first LLM Wiki** where the user owns a verifiable knowledge system and the LLM naturally uses and maintains persistent knowledge inside explicit authority boundaries.

Research is a means, not the product. The next evidence should come primarily from installed use of the representative product loop.

## Current product state

- **Dogfood 0.1.10 is the current installable Alpha.** Product merge: PR #125, `f3451640e0f39361394217e9b1d925cff95c9f89`.
- **Raw-first Alpha Core remains the trust substrate:** immutable/content-addressed raw evidence, explicit temporal semantics, fail-closed integrity/citations, provenance navigation, prompt-over-stdin privacy hardening, and store-level single-writer protection.
- **Human Knowledge Note v0** remains human-owned Markdown. Creating it does not auto-ingest, call a model, or silently become canonical state.
- **Retrieval:** W0 remains default. X1 remains non-default/shadow despite meaningful E015-D1 and E017-D2 improvements. Do not promote without more natural quality evidence.
- **Persistent compiled provider:** still E013-gated as a trusted/default provider.
- **Customer readiness:** **NOT READY YET.** The product now has the first representative Agent Wiki loop, but needs real multi-session installed use before broader UX/marketplace claims.

## Shipped Agent Wiki loop

### Ordinary agent conversation — ambient bounded read

0.1.10 contributes the stable VS Code Language Model Tool:

- `llmWiki_searchMemory` / prompt reference `#wikiMemory`

The user's selected main model can invoke it during ordinary agent conversation. The tool performs local deterministic current-view retrieval and makes **zero model calls** itself.

Tool output keeps two epistemic classes separate:

1. **RAW_MEMORY** — current canonical raw evidence/provenance; factual authority.
2. **DERIVED_MEMORY** — current-source Agent Wiki synthesis/navigation aid; model-generated, noncanonical, not independent corroboration, and not Human Knowledge authorship.

The read tool never authorizes persistence, correction, change, dispute, supersession, or deletion and does not manufacture E013 query/visit telemetry.

### Explicit remember — human admission first

0.1.10 contributes:

- `llmWiki_rememberSource` / prompt reference `#rememberWikiSource`

Invoke only from explicit user intent to remember/save/capture/add a local workspace source.

Flow:

`explicit remember -> raw immutable admission -> selected topic or deterministic Agent Inbox -> optional derived maintenance`

If no clean human-selected topic exists, filing uses deterministic **Agent Inbox**. This is reversible organization, not an epistemic commitment.

Raw admission always happens before any model-backed maintenance. Maintenance failure never rolls back or hides the admitted raw source.

### Opt-in Luna derived maintenance

Agent Wiki maintenance is **OFF by default**.

The user can run:

- `LLM Wiki: Configure Agent Wiki Maintenance`

Enabling is a workspace-scoped standing grant with a modal disclosure that, after explicit source admission, admitted source bytes may be sent to exact `gpt-5.6-luna` under a visible per-call AI-credit guard.

When enabled, one source-scoped derived note is created/reused under:

- `.wiki-lab/agent-wiki/source-notes/<source_id>.json`
- `.wiki-lab/agent-wiki/source-notes/<source_id>.md`

The deterministic wrapper labels it:

> **AGENT WIKI — NONCANONICAL / REBUILDABLE**

The maintenance path:

- requires every load-bearing summary/rule/boundary to cite only admitted evidence;
- fails closed on malformed or uncited model output;
- writes outside canonical manifest/history;
- never re-ingests generated notes as raw evidence;
- cannot perform correction/change/dispute/supersession/delete;
- cannot infer/persist Human Knowledge;
- rejects sources over 40k characters before a model call;
- reuses the same current source+policy note with **0 new model calls**;
- runs the external call without holding the canonical writer lock, then revalidates source currentness/SHA under a short writer lock before derived publish;
- keeps an old derived note inspectable after source supersession but removes it from **current** derived-memory search.

## E018 — per-turn Luna Steward rejected

Issue #113 is complete.

Frozen score:

- GPT-5.4 main-model discretion: **7/8**
- Claude Sonnet 4.6 main-model discretion: **7/8**
- GPT-5.6 Luna dedicated Steward: **6/8**
- relevant-memory false negatives: **0 for all**
- protected/canonical overreach: **0 for all**
- baseline normalized disagreement: **1/8**

The preregistered Phase-2 gate did not pass, so reserved calls were not spent.

Architecture consequence:

> **Product-controlled policy and capability boundaries are required; a product-controlled second model on every turn is not.**

Do not reopen the mandatory Steward from architectural preference. Reopen only if installed use produces repeated main-model policy drift/failures.

Important C5 insight: **reading relevant memory and persisting Human Knowledge are separate permissions.** A tentative/inferred thought may allow contextual read while still forbidding durable human-authorship persistence.

## E019 — Luna earned the maintenance role

Issue #121 is complete.

The frozen one-call E019 source-maintenance run produced a strong provenance-linked noncanonical Agent Wiki artifact. The automatic result was `FAIL` only because one lexical scorer regex missed semantically explicit no-recursive-contamination wording; manual semantic adjudication is **PASS**, with the automatic status preserved and no reroll.

Result: `experiments/E019-agent-wiki-maintenance/results-v0.md`.

This justified the narrow 0.1.10 maintenance slice, not background autonomy or canonical mutation.

### Product-path translation smoke

The actual shipped product CLI was then tested separately with exactly one real Luna generation:

- run `31893676510`
- head `2a70763809d68b1f8085f98ccc42e41fe375f2fa`
- artifact `9249211551`
- artifact digest `sha256:26012f388636b0d856124e7b7aabc149ebd5794519b865065131c1d34bc33763`

All frozen checks passed:

- first real product build: `CREATED`, exact `gpt-5.6-luna`, model_calls=1;
- second identical build: `REUSED`, model_calls=0, without model authorization;
- derived search returned `derived_noncanonical_agent_wiki`;
- generated note retained source provenance and noncanonical/rebuildable banner;
- canonical history remained exactly the original raw admission;
- integrity clean.

No additional Copilot purchase was required.

## Current authority contract

1. **Human controls admission.** A source enters memory because the user explicitly admits it, unless a future separately granted source-watch scope is designed and justified.
2. **Human controls epistemic commitment.** Explicit user-authored decisions/beliefs may be persisted through an authorized Human Knowledge path; inferred beliefs remain proposal-only.
3. **Main model may use bounded memory.** Ordinary agent conversation may consult relevant raw + clearly labeled derived memory.
4. **LLM may maintain Agent Wiki inside grant.** Derived maintenance is useful autonomous work, but remains noncanonical/rebuildable.
5. **Code owns dangerous capability boundaries.** Correction/change/dispute/supersession and destructive provenance operations remain technically unavailable to the autonomous maintenance path.
6. **Generated answers/derived notes are not evidence.** Query write-back must ground itself in admitted evidence / explicit human statements.
7. **No surprise exposure/spend.** External maintenance is default-off and requires a standing workspace grant plus bounded credit guard.

## Immediate next work — installed multi-session P7

**Do not start another architecture program now.** Install and dogfood 0.1.10 across real sessions.

Representative natural loop:

1. Ask an ordinary agent question where old project knowledge should matter; observe whether the main model naturally uses `wikiMemory`.
2. Say `remember this source` on a real workspace file; verify raw admission is low-friction and Agent Inbox/selected-topic filing feels natural.
3. With maintenance grant enabled for an appropriate workspace, observe Luna source-note creation and whether the derived synthesis is genuinely useful later.
4. Return in a later session and ask a question that should benefit from the remembered source; inspect raw vs derived memory use and provenance.
5. Remember the same unchanged source again; expect derived maintenance reuse with **0 new model call**.
6. Admit an updated source and explicitly mark the appropriate temporal relation when warranted; verify the old derived note no longer surfaces as current memory after supersession.
7. Watch for actual friction: approval fatigue, tool non-invocation, bad derived snippets, confusing raw/derived distinction, source navigation pain, maintenance latency/cost, or missing activity/diff visibility.

Let that friction decide the next slice. Likely candidates include activity/health visibility, source-note navigation/diff/rebuild UI, or stronger tool descriptions/routing. Do **not** build Tree View, federation, broad Inbox ontology, X2, vector/graph infrastructure, or background watching merely because they are available ideas.

## Other active constraints

- **Known retrieval limit:** long non-Markdown objects can require multiple separated relevant regions. Build a narrow X2 only if this recurs naturally.
- **E013:** keep workload evidence natural; do not manufacture visits/cycles.
- **E015:** quality-label natural W0/X1 divergences; do not force them.
- **Paid calls:** do not spend more on frozen E017/E018/E019 cases. New paid calls are justified only when they can change a product decision or validate a materially new production path.
- **#101 review:** accepted security/reliability P0s are shipped; remaining feature proposals stay subordinate to installed-use evidence.

## Fast pointers

- Autonomy / agent-first UX umbrella: Issue #110
- Agent Wiki transport slice: Issue #119 / PR #120
- E019 maintenance experiment: Issue #121 / `experiments/E019-agent-wiki-maintenance/results-v0.md`
- Agent Wiki 0.1.10 implementation: Issue #124 / PR #125
- Production-path one-call smoke: PR #126 / run `31893676510`
- Autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
- E018 result: `experiments/E018-steward-policy/results-phase1-v0.md`
- External product review: Issue #101
- E015 realistic shadow: Issue #38
- E013 realistic workload gate: Issue #21
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins and this file must be corrected immediately**.
