# Current Handoff

Last updated: 2026-08-15 KST

This is the **current continuation state**, not project history. Replace or delete stale items as the project moves. Detailed evidence stays in code, ADRs, experiments, issues, PRs, and Git history.

## North Star

Build a **proper VS Code-first LLM Wiki** where the user owns a verifiable knowledge system and the LLM genuinely uses and maintains persistent knowledge rather than appearing as a bolt-on `Ask` button.

Research is a means, not the product. Preserve the trust substrate, but do not let trust work accidentally remove the central LLM-maintained-Wiki product loop.

## Current product state

- **Dogfood 0.1.8 is the current installable Alpha.** 0.1.8 hotfixed the real installed-user Python 3.9 startup blocker from #108/#109. CI now has an explicit Python 3.9 bundled-core compatibility job in addition to the normal dev + packaged VSIX Extension Host regression.
- **Raw-first Alpha Core remains ready and red-team hardened.** Keep the convergence rule: do not restart open-ended core infrastructure without an observed product blocker, an E013/E015 boundary crossing, or a reproducible trust/data-loss failure.
- **Copilot prompt privacy:** #102 moved the complete question/evidence prompt out of process argv. Copilot receives the transformed prompt over stdin; argv contains control/model flags only.
- **Single-writer semantic safety:** #104 / #103 added one private store-level OS advisory writer lock across public read/validate/write mutations.
- **Human Knowledge Note v0:** #106 / #105 adds `LLM Wiki: New Human Knowledge Note`, a human-owned Markdown draft. It does not auto-ingest, call the model, or mutate canonical Wiki state.
- **Deterministic self-hosting:** frozen E010 v1 remains **278/278 files, 11/12 expected-source top-5, MRR 0.736, context 12/12**. Later growing-repo runs remained above the frozen Stage A gate.
- **Real-model self-use:** completed with exact `gpt-5.6-luna`, including returning/forgetful discovery, Ask, provenance, correction, dispute, manifest-loss reasoning, and citation failure/retest.
- **External E017 dogfood:** completed on Kubernetes Markdown, CPython RST, and NASA Artemis II pages. It found the uneven-topic global discovery bug and a real same-object context-granularity limit.
- **Retrieval:** W0 remains default; X1 remains non-default/shadow. E015-D1 and E017-D2 are two meaningful real-user cases where X1 materially helped, but they are still not enough for global promotion.
- **Customer readiness:** **NOT READY YET.** Installed use has exposed that the current command-driven interaction is not representative of the intended LLM-maintained Wiki product.

## Current top priority — #110 autonomy / UX design gate

A short real install produced a more important product question than another retrieval experiment:

> **What should the LLM do autonomously, what should require human intent/approval, what judgment must happen inside ordinary LLM use, and what must never be silently delegated?**

Do **not** jump directly to MCP, VS Code Language Model Tools, Chat Participants, hooks, or a background worker. Those are transport/orchestration choices. First settle the authority and memory-governance model in:

- `docs/12-autonomy-ux-philosophy.md`
- `docs/13-luna-wiki-steward-hypothesis.md`
- Issue #110

Working thesis:

> **The user controls admission and epistemic commitment. The LLM controls compilation and maintenance inside the authority it has been granted.**

Working ownership model:

1. **Raw evidence / canonical history** — human-admitted trust substrate; immutable/provenance-first; LLM may read but not silently reinterpret correction/change/dispute semantics.
2. **Human Knowledge Notes** — human-owned beliefs/decisions/reasoning; explicit user instruction can authorize writing, inferred human commitments should be proposals.
3. **Agent Wiki** — missing LLM-owned persistent derived layer; provenance-linked, inspectable, reversible/rebuildable, explicitly noncanonical. This is where routine autonomous compilation/linking/maintenance should live.

Important distinction:

- **Persistent compiled provider as trusted/default retrieval substrate** remains gated by E013 realistic reuse/cost/update evidence.
- **Persistent Agent Wiki as an LLM-owned derived product artifact** is a different thing and should not be blocked merely because the compiled-provider promotion gate has not passed.

## New working hypothesis — dedicated Wiki Steward / memory governor

The user's main model should probably **not** be the sole authority deciding whether/how Wiki memory is used. If memory behavior depends entirely on whichever main model the user selected, it becomes model-dependent, difficult to regression-test, and easy to bypass accidentally.

Candidate architecture:

- the **main LLM** remains whatever model the user wants for coding/research/answering;
- a product-controlled **Wiki Steward** performs Wiki-relevant judgment;
- initial concrete candidate model is **`gpt-5.6-luna`** because it is lightweight, cost-efficient, available in Copilot, and already validated in this project;
- the architectural commitment, if any, should be **separate memory governance from the main answering model**, not “Luna forever.”

Current GitHub official pricing fact as of 2026-08-15 for GPT-5.6 Luna default context (<=200K input tokens): **$0.20 / 1M input tokens**, $0.02 / 1M cached input, $0.25 / 1M cache write, $1.20 / 1M output. `$0.20` is not a flat per-call price. The relevance is that a deliberately small structured policy call may be cheap enough for ordinary interaction paths. Re-verify external pricing before release decisions.

Do **not** use Luna as a single `should_search=yes/no` gate. A model false negative must not hide memory that exists. Prefer:

1. cheap/private **deterministic local candidate retrieval** first;
2. Luna **Turn Policy Judge** to interpret relevance, memory intent, authorship, conflict, and action class;
3. validated typed output and deterministic capability enforcement;
4. user-selected main model receives only bounded, provenance-preserving Wiki context;
5. a separate Luna **maintenance agent loop** runs only when derived Wiki work is actually needed.

Candidate policy classes include:

- ordinary Wiki read/context injection;
- explicit source `remember` intent;
- explicit human commitment;
- derived maintenance;
- possible conflict requiring a pending human decision;
- no-op.

Explicit human intent outranks model preference: `Remember this file` means admission is authorized; the Steward files/compiles rather than vetoing the user's memory boundary. Inferred human beliefs remain proposal-only.

## Why this changes transport selection

Language Model Tools and MCP are useful capability surfaces, but the normal agent model decides whether to invoke them. That may be insufficient if the product contract requires a **mandatory Wiki-policy phase independent of main-model discretion**.

Transport/orchestration candidates must therefore be judged by this stronger requirement:

> **Can LLM Wiki enforce a product-controlled memory-policy phase while still letting the user choose their main LLM?**

Current VS Code capabilities make this plausible but not solved:

- Chat Participants can own end-to-end interaction but require participant-oriented UX;
- custom agents/subagents can use a different model for a focused subagent;
- lifecycle hooks can execute deterministic code at `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, etc., but hooks are Preview and their documented per-event context/control surfaces differ;
- direct Language Model API orchestration gives stronger control but risks rebuilding too much of the chat experience;
- MCP/extension tools remain valuable capability ports but are not, by themselves, the memory-governance contract.

Do not choose a transport until the smallest Steward experiment is specified.

## Working UX principles

- **Approve intent and authority, not routine mechanics.** A high-level `Remember this` or standing maintenance grant should not lead to approval dialogs for every search, link, summary, or derived-page edit.
- **Human controls admission by default.** The user chooses which source/file/folder/class enters memory. Mechanical ingest and filing may happen automatically after that grant.
- **Wiki reads should be ambient.** During ordinary agent conversation, memory should be considered automatically within granted scope; the user should not have to remember topic names or manually run `Search -> Ask` every time.
- **Automatic must remain legible.** Answers should show that LLM Wiki was used and provide citations/provenance; derived maintenance should have compact activity/diff/revert visibility.
- **Derived maintenance can be autonomous.** Once maintenance/model/budget scope is granted, LLM-owned Agent Wiki pages should not require per-page human approval.
- **Epistemic mutations remain special.** Correction/change/dispute/supersession and destructive provenance loss are not ordinary filing operations; Steward may detect/propose, human arbitrates by default.
- **Human authorship is protected.** Explicit `remember that we decided X because Y` can count as authorization; model-inferred beliefs should not silently become the user's durable statement.
- **No surprise external exposure or spend.** A Steward means some prompts/snippets may be sent to Luna in addition to the main model; this requires explicit standing privacy/budget scope.
- **Query output must not recursively become evidence.** A useful answer can trigger derived maintenance, but the maintenance must resynthesize from admitted evidence / explicit human statements rather than treating the generated answer as evidence.
- **Capability boundaries, not prompt wording, enforce safety.** The Turn Policy Judge should emit typed decisions; the maintenance agent should only have derived-write capabilities; canonical/destructive operations remain technically unavailable without the proper human-gated path.

## Representative product loop to design before long-run P7

Do not spend weeks evaluating the current command ceremony as if it were the finished product.

The smallest representative loop should feel like:

1. User says **“remember this source”** or explicitly admits a source.
2. Raw/provenance capture happens under the existing trust rules.
3. Luna Steward classifies/files the event and a constrained maintenance agent updates a small **derived Agent Wiki** within granted budget/privacy scope.
4. Later the user asks an **ordinary agent question** with their preferred main model, without `Ask Wiki` ceremony.
5. Local retrieval finds candidate memory; the Steward judges bounded relevance/action; the main model receives governed Wiki context and answers with inspectable provenance.
6. If a high-consequence semantic conflict appears, the Steward surfaces a **pending human decision** rather than silently choosing correction/change/dispute.

0.1.8 remains useful for runtime/core smoke and can still produce product friction, but its command-driven `Create Topic -> Ingest -> Search -> Ask Luna` flow is **not sufficient evidence for the intended UX**.

## Failure modes that now matter

- relevant Wiki exists but Steward withholds it (false negative);
- irrelevant/stale memory pollutes the main model (false positive);
- inferred belief becomes a human commitment;
- Steward silently performs correction/change/dispute;
- generated answers recursively contaminate evidence;
- main model bypasses the governed write path;
- admitted evidence prompt-injects the Steward;
- controller behavior drifts across model/prompt versions;
- added per-turn latency makes the product worse despite cheap tokens;
- second-model exposure or spend surprises the user;
- Luna/controller outage blocks the whole product unnecessarily.

Likely degradation hypothesis to test: **read/query may fall back to clearly labeled deterministic local retrieval; persistent writes/epistemic actions fail closed or queue when the Steward is unavailable.**

## Other active constraints

- **Known retrieval limit:** long non-Markdown objects can require multiple separated regions. Do not build broad parser/index infrastructure until the mechanism recurs naturally.
- **Persistent compiled provider:** still disabled as a trusted/default provider pending natural E013 evidence.
- **E015:** let natural W0/X1 divergences arise; do not manufacture them.
- **Paid Luna calls:** do not spend more on frozen E017 cases. New Luna calls are justified when they test the actual Steward/product decision.
- **#101 review:** accepted P0s are shipped; X2/federation/inbox/Tree View/scale work remain conditional on real recurrence/friction.

## Immediate next work

1. **Design first, no integration code yet:** refine and attack Issue #110 plus `docs/12` and `docs/13` until the authority/governor model survives obvious failure cases.
2. Specify one **small controlled Steward experiment**, not a platform implementation: compare (A) main-model-discretion over Wiki tools/instructions vs (B) deterministic candidate retrieval + Luna policy judgment + constrained execution.
3. Include realistic multi-turn cases where memory should be used, should not be used, explicit `remember` appears, inferred beliefs appear, and conflicts appear.
4. Measure relevant-memory recall/false negatives, irrelevant injection, correct autonomy class, protected-operation violations, added latency, actual token/AI-credit cost, and stability across at least two different main models.
5. Only if the dedicated Steward earns its complexity, choose the transport/orchestration mechanism that can enforce the contract.
6. Then implement the smallest representative Agent Wiki loop and resume real multi-session P7.
7. Keep E013/E015 natural; do not bend user behavior to hit research thresholds.

## Fast pointers

- **Autonomy / agent-first UX design gate:** Issue #110
- **Working autonomy philosophy:** `docs/12-autonomy-ux-philosophy.md`
- **Dedicated Luna Steward hypothesis:** `docs/13-luna-wiki-steward-hypothesis.md`
- Python 3.9 installed-user hotfix: Issue #108 / PR #109
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
- Backup/restore Alpha procedure: `docs/11-local-backup-restore.md`

If this file conflicts with merged code or an accepted ADR, **code/ADR wins and this file must be corrected immediately**.