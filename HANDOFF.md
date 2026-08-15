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
- **Customer readiness:** **NOT READY YET.** Installed use has now exposed that the current command-driven interaction is not yet representative of the intended LLM-maintained Wiki product.

## Current top priority — #110 autonomy / UX design gate

A short real install produced a more important product question than another retrieval experiment:

> **What should the LLM do autonomously, what should require human intent/approval, and what must never be silently delegated?**

Do **not** jump directly to MCP, VS Code Language Model Tools, Chat Participants, or a background worker. Those are transport choices. First settle the product authority model in `docs/12-autonomy-ux-philosophy.md` and Issue #110.

Working thesis:

> **The user controls admission and epistemic commitment. The LLM controls compilation and maintenance inside the authority it has been granted.**

Working ownership model:

1. **Raw evidence / canonical history** — human-admitted trust substrate; immutable/provenance-first; LLM may read but not silently reinterpret correction/change/dispute semantics.
2. **Human Knowledge Notes** — human-owned beliefs/decisions/reasoning; explicit user instruction can authorize writing, inferred human commitments should be proposals.
3. **Agent Wiki** — missing LLM-owned persistent derived layer; provenance-linked, inspectable, reversible/rebuildable, explicitly noncanonical. This is where routine autonomous compilation/linking/maintenance should live.

Important distinction:

- **Persistent compiled provider as trusted/default retrieval substrate** remains gated by E013 realistic reuse/cost/update evidence.
- **Persistent Agent Wiki as an LLM-owned derived product artifact** is a different thing and should not be blocked merely because the compiled-provider promotion gate has not passed.

The E013 gate still protects a default/query architecture decision. It must not accidentally become a ban on dogfooding the central Karpathy-style persistent Wiki hypothesis.

## Working UX principles

- **Approve intent and authority, not routine mechanics.** A high-level `Remember this` or standing maintenance grant should not lead to approval dialogs for every search, link, summary, or derived-page edit.
- **Human controls admission by default.** The user chooses which source/file/folder/class enters memory. Mechanical ingest and filing may happen automatically after that grant.
- **Agent Wiki reads should be ambient.** During ordinary agent conversation, the agent should consult Wiki memory automatically within granted scope; the user should not have to remember topic names or manually run `Search -> Ask` every time.
- **Automatic must remain legible.** Answers should show that LLM Wiki was used and provide citations/provenance; derived maintenance should have compact activity/diff/revert visibility.
- **Derived maintenance can be autonomous.** Once maintenance/model/budget scope is granted, LLM-owned Agent Wiki pages should not require per-page human approval.
- **Epistemic mutations remain special.** Correction/change/dispute/supersession and destructive provenance loss are not ordinary filing operations; agent may detect/propose, human arbitrates by default.
- **Human authorship is protected.** Explicit `remember that we decided X because Y` can count as authorization; model-inferred beliefs should not silently become the user's durable statement.
- **No surprise external exposure or spend.** Sending evidence to an external model and paid maintenance need explicit standing scope/budget.
- **Query output must not recursively become evidence.** Reusable synthesis may update Agent Wiki from underlying admitted evidence, but a model answer is not promoted into raw/canonical evidence merely because it was generated.

## Representative product loop to design before long-run P7

Do not spend weeks evaluating the current command ceremony as if it were the finished product.

The smallest representative loop should feel like:

1. User says **“remember this source”** or explicitly admits a source.
2. Raw/provenance capture happens under the existing trust rules.
3. LLM autonomously updates a small **derived Agent Wiki** within granted budget/privacy scope.
4. Later the user asks an **ordinary Copilot/agent question**, without `Ask Wiki` ceremony.
5. The agent autonomously consults the Wiki and answers with inspectable provenance.
6. If a high-consequence semantic conflict appears, the system surfaces a **pending human decision** rather than silently choosing correction/change/dispute.

Only after this loop is coherent should we choose Language Model Tool vs MCP vs another transport and resume representative multi-session P7.

0.1.8 remains useful for runtime/core smoke and can still produce product friction, but its command-driven `Create Topic -> Ingest -> Search -> Ask Luna` flow is **not sufficient evidence for the intended UX**.

## Other active constraints

- **Known retrieval limit:** long non-Markdown objects can require multiple separated regions. Do not build broad parser/index infrastructure until the mechanism recurs naturally.
- **Persistent compiled provider:** still disabled as a trusted/default provider pending natural E013 evidence.
- **E015:** let natural W0/X1 divergences arise; do not manufacture them.
- **Paid Luna calls:** do not spend more on frozen E017 cases. Use paid calls only when a new real-user question can change a product decision.
- **#101 review:** accepted P0s are shipped; X2/federation/inbox/Tree View/scale work remain conditional on real recurrence/friction.

## Immediate next work

1. **Design first, no agent integration code yet:** refine and challenge Issue #110 / `docs/12-autonomy-ux-philosophy.md` until the authority model is coherent.
2. Decide the **minimal end-to-end Agent Wiki slice**, including admission boundary, autonomous derived writes, model/privacy/budget grant, inspectability, and pending human decisions.
3. Only then choose the **transport** (VS Code Language Model Tool, MCP, Chat Participant, direct extension flow, or combination) that best preserves the product contract.
4. Implement the smallest representative loop and dogfood that loop over multiple sessions.
5. Keep E013/E015 natural; do not bend user behavior to hit research thresholds.
6. Re-evaluate customer readiness from the real agent-maintained Wiki experience, not from command-surface CI confidence.

## Fast pointers

- **Autonomy / agent-first UX design gate:** Issue #110
- **Working autonomy philosophy:** `docs/12-autonomy-ux-philosophy.md`
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
