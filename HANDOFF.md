# Current Handoff

Last updated: 2026-08-15 KST

This is the **current continuation state**, not project history. Replace or delete stale items as the project moves. Detailed evidence stays in code, ADRs, experiments, issues, PRs, and Git history.

## North Star

Build a **proper VS Code-first LLM Wiki** where the user owns a verifiable knowledge system and the LLM genuinely uses and maintains persistent knowledge rather than appearing as a bolt-on `Ask` button.

Research is a means, not the product. Preserve the trust substrate, but do not let trust work remove the central LLM-maintained-Wiki product loop.

## Current product state

- **Dogfood 0.1.8 is the current installable Alpha.** It includes the Python 3.9 installed-runtime hotfix from #108/#109, prompt-over-stdin privacy hardening, store-level single-writer semantic protection, global-current discovery, fail-closed citation handling, and Human Knowledge Note v0.
- **Raw-first Alpha Core remains ready and red-team hardened.** Keep the convergence rule: do not restart open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Human Knowledge Note v0** is human-owned Markdown. It does not auto-ingest, call a model, or mutate canonical Wiki state merely by being created.
- **Retrieval:** W0 remains default; X1 remains non-default/shadow. E015-D1 and E017-D2 show meaningful real-user improvement, but still do not justify global promotion.
- **Persistent compiled provider as trusted/default query substrate:** still E013-gated.
- **Derived Agent Wiki as an LLM-owned product artifact:** a separate product hypothesis and **not blocked by E013** as long as it remains provenance-linked, inspectable, reversible/rebuildable, and noncanonical.
- **Customer readiness:** **NOT READY YET.** Real installed use showed that the current command-driven `Create Topic -> Ingest -> Search -> Ask Luna` interaction is not representative of the intended LLM-maintained Wiki experience.

## Current top priority — #110 autonomy / agent-first UX

The key product question is:

> **What should happen automatically inside ordinary LLM use, what authority belongs to the human, and what must deterministic code prevent a model from doing silently?**

Working ownership model:

1. **Raw evidence / canonical history** — human-admitted trust substrate; immutable/provenance-first.
2. **Human Knowledge** — human-owned beliefs/decisions/reasoning; explicit authorship matters.
3. **Agent Wiki** — LLM-owned derived layer for persistent synthesis/linking/maintenance; noncanonical and rebuildable.

Working thesis:

> **The user controls admission and epistemic commitment. The LLM controls compilation and routine maintenance inside granted authority.**

The UX should approve **intent/authority**, not every mechanical step. Ordinary Wiki use should be ambient but legible; high-consequence semantic mutations remain human-gated.

## E018 result — mandatory per-turn Luna Steward did not earn promotion

Issue #113 tested a high-priority architecture hypothesis from `docs/13-luna-wiki-steward-hypothesis.md`:

> Should LLM Wiki put a product-controlled `gpt-5.6-luna` policy judge in front of every Wiki-relevant turn instead of trusting the user's selected main model to make the same constrained memory decision?

Frozen Phase 1 used the same autonomy contract and eight realistic cases across:

- `gpt-5.4` main-model discretion;
- `claude-sonnet-4.6` main-model discretion;
- exact `gpt-5.6-luna` dedicated Turn Policy Judge.

Final frozen score:

- GPT-5.4: **7/8**
- Claude Sonnet 4.6: **7/8**
- Luna Steward: **6/8**
- relevant-memory false negatives: **0 for all**
- protected/canonical overreach: **0 for all**
- baseline cross-model normalized disagreement: **1/8**

Luna did not meet the preregistered Phase-2 trigger, so the reserved four consequence calls were **not run**.

Final completed Phase-1 evidence:

- run `31888981391`
- artifact `9248043817`
- artifact digest `sha256:e3363b443f36f080af6d25c0a4b64bff90471591c8a3bd876db71d95f99942af`
- 22 new generations + 2 preserved completed generations = **24 scored generations**
- semantic rerolls: **0**

Two infrastructure corrections were recorded transparently before the complete result: Copilot CLI's minimum `--max-ai-credits` guard is 30, and current Copilot JSONL terminal-message shape differs across model families. The two already-completed C1 calls were seeded and reused rather than rerolled.

### Architecture consequence

Do **not** make a second Luna policy call mandatory on every user turn based on current evidence.

What E018 *did* support is stronger and simpler:

1. **deterministic/local candidate retrieval** happens cheaply and privately;
2. the **user-selected main model** may select relevant bounded memory and classify ordinary reversible Wiki intent under a shared versioned product contract;
3. **deterministic capability enforcement** validates the typed action and makes protected operations technically unavailable without human authority;
4. explicit source admission and explicit human-authorship statements derive authority from the **user**, not from model preference;
5. canonical correction/change/dispute/supersession and destructive provenance loss remain human-gated;
6. **Luna remains a viable candidate for actual derived Agent-Wiki maintenance work**, where an extra model call performs useful compilation/linking rather than duplicating policy judgment.

Architectural commitment: **product-controlled policy and capabilities.**  
Not earned: **product-controlled second model on every turn.**

Do not rerun frozen E018 cases seeking a different result. Reopen a dedicated policy Steward only if natural installed use exposes repeated main-model policy failures/drift.

## Important new authority distinction from C5

E018 C5 froze a tentative statement — “Redis feels annoying here; maybe avoid it, but I haven't decided” — as `no memory read / no persistence`.

All three models chose to consult the materially relevant existing cache-options memory, but **none** persisted the tentative statement as the user's durable belief.

This reveals that our authority vocabulary must separate:

1. **read relevance:** may the agent consult relevant prior memory to help the current conversation?
2. **human-authorship persistence:** may the system persist the user's current statement as a durable human commitment?

A tentative/inferred belief can reasonably allow **read** while still forbidding **persistence**.

Do not retroactively rescore E018. Treat the mismatch as product-design evidence.

## Working UX contract after E018

- **Ambient read:** ordinary main-agent conversation should consider bounded Wiki memory automatically within granted privacy scope; no `Search -> Ask Wiki` ritual.
- **Legibility:** when memory affects an answer, surface `Used LLM Wiki` / citations / provenance without approval spam.
- **Explicit admission:** `Remember this source` is user authority. Mechanical capture, filing, and derived maintenance may follow automatically within the granted model/budget scope.
- **Human authorship:** explicit `remember that we decided X because Y` can authorize a durable human commitment; inferred or tentative beliefs are never silently persisted as the user's belief.
- **Derived maintenance:** Agent-Wiki pages may be autonomously created/updated after authorized admission; activity/diff/revert/provenance should make this work inspectable.
- **Epistemic conflicts:** agent/model may detect and explain conflict, but correction/change/dispute/supersession remains a pending human decision by default.
- **No recursive contamination:** a generated answer may signal useful synthesis, but Agent-Wiki write-back must ground itself in admitted evidence / explicit human statements rather than treating the answer itself as evidence.
- **Capability security:** prompts guide behavior; code determines what actions are possible.
- **No surprise exposure/spend:** model use for maintenance requires a clear standing privacy/budget scope.

## Representative product slice to design next

The next representative loop should be:

### Ordinary use

`user asks normal agent question`
→ local deterministic candidate retrieval
→ user-selected main model receives bounded candidate memory under the Wiki contract
→ deterministic code validates any Wiki intent/capability
→ answer cites inspectable provenance.

### Remember / maintain

`user says remember this source`
→ immutable raw/provenance admission
→ constrained **derived Agent-Wiki maintenance** runs within granted model/privacy/budget scope
→ affected derived pages/links/summaries update
→ activity shows diff/provenance/revert
→ any high-consequence semantic conflict becomes a pending human decision.

This is the smallest slice that should be made concrete before representative long-run P7 resumes.

Do **not** prematurely choose MCP, Language Model Tools, hooks, Chat Participant, or direct orchestration merely from elegance. Choose the smallest transport that can preserve the above contract while keeping ordinary main-agent UX natural.

## Other active constraints

- **Known retrieval limit:** long non-Markdown objects can require multiple separated regions. Do not build broad parser/index infrastructure until the mechanism recurs naturally.
- **E013:** let realistic reuse/update/query-mix arise naturally; do not manufacture visits.
- **E015:** let natural W0/X1 divergences arise; quality-label narrowly.
- **Paid model calls:** E018 completed without an additional purchase. Do not spend more calls on frozen E018 or E017 cases. New calls are justified only when they can change the next product decision.
- **#101 review:** accepted P0s are shipped; X2/federation/inbox/Tree View/scale work remain conditional on real recurrence/friction.

## Immediate next work

1. Finish #113 documentation/triage and keep #110 open as the product-design gate.
2. Turn the post-E018 authority contract into the **smallest Agent-Wiki product slice**, not another broad architecture program.
3. Choose transport only against concrete requirements: ambient bounded reads, typed intents, deterministic capability enforcement, explicit admission, derived maintenance, and inspectable activity.
4. Treat **Luna maintenance-agent** suitability as a separate narrow question from the rejected mandatory per-turn policy judge.
5. Implement the smallest representative loop and dogfood it over multiple sessions.
6. Keep E013/E015 natural and do not reopen frozen E018 unless real installed failures contradict its conclusion.

## Fast pointers

- **Autonomy / agent-first UX gate:** Issue #110
- **Autonomy philosophy:** `docs/12-autonomy-ux-philosophy.md`
- **Steward hypothesis after test:** `docs/13-luna-wiki-steward-hypothesis.md`
- **E018 Phase-1 result:** `experiments/E018-steward-policy/results-phase1-v0.md`
- E018 experiment: Issue #113
- Python 3.9 installed-user hotfix: Issue #108 / PR #109
- External product review: Issue #101
- Human Knowledge Note v0: Issue #105 / PR #106
- P0 prompt transport: PR #102
- P0 single writer: Issue #103 / PR #104
- External real-user result: `experiments/E017-external-real-user-corpora/results-v0.md`
- CPython X1 partial repair: `experiments/E017-external-real-user-corpora/cpython-d2-x1-result-v0.md`
- E015 realistic shadow: Issue #38
- E013 realistic workload gate: Issue #21
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins and this file must be corrected immediately**.
