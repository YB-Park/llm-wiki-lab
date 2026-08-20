# Current Handoff

Last updated: 2026-08-20 KST — Dogfood GO checkpoint

This is a **living continuation checkpoint**, not a project history.
Keep only what a new continuation needs to decide and act **now**.
Historical experiments, rationale, PR-by-PR detail, and frozen results belong in their source docs, issues, PRs, ADRs, and Git.

If this file conflicts with merged code or an accepted ADR, code/ADR wins.
Before any new repo work, re-check current `main` and open PRs; volatile repository state does not belong in this handoff.

## NOW

Repository: `YB-Park/llm-wiki-lab`

Current state:
- product baseline: **Dogfood 0.1.16**
- current product decision: **GO for installed self-dogfood / Alpha use**
- public Beta / broad Marketplace readiness: **not declared by this checkpoint**
- primary product-evidence track: **Issue #141 natural installed dogfood**
- E023 research: **parked**
- paid E023 semantic calls: **paused**
- G3 identity/routing: **not opened**

The immediate job is no longer to invent another benchmark or architecture layer.
It is to determine whether LLM Wiki is genuinely useful during normal long-horizon Agent work.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval, organization, compilation, and maintenance inside granted authority.**

Normal product use should remain ordinary VS Code Agent conversation.

## Product baseline — do not casually change during dogfood

Dogfood **0.1.16** is the installed baseline.

Release artifact:
- `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- version: `0.1.16`
- SHA-256: `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`
- validated main run: `32204779167`

E023 changed research conclusions, **not the 0.1.16 runtime product**.

During long-horizon dogfood, prefer to keep this binary fixed.
Do not patch every small annoyance immediately; otherwise the observed product keeps changing.
Interrupt the freeze only for a real P0/P1 class defect such as data loss/corruption risk, broken authority/privacy boundary, provenance failure, unusable core path, or repeated causal failure that blocks normal use.

## Authority floor

These are product invariants unless a separate evidence-backed product decision changes them:

- workspace use is explicit opt-in and trusted-workspace only;
- `Check Setup and Health` = **0 model calls / 0 state changes**;
- disabling removes Agent tool availability while preserving Wiki data;
- new source bytes require human confirmation before durable admission;
- `RAW_MEMORY` = immutable admitted evidence / provenance authority;
- `DERIVED_MEMORY` = noncanonical, rebuildable synthesis/navigation aid;
- `HUMAN_KNOWLEDGE` = explicit user-owned decision, belief, rationale, or approved synthesis;
- changed remembered files require explicit correction/change/dispute/supersede/independent semantics;
- load-bearing facts surfaced from derived memory should resolve back to terminal authority;
- AI summaries are optional and off by default until separately granted;
- source/model-controlled memory text remains untrusted data, not instructions.

E020 remains the deterministic safety/product contract:
**78 zero-model cases: 60 supported / 7 partial / 11 deferred.**

## Before long-horizon dogfood — Day-0 smoke only

Do **one short installed smoke**, then stop synthetic expansion and use the product naturally.

1. Install the validated 0.1.16 VSIX.
2. Open one trusted **single-folder** real workspace.
3. Keep `.wiki-lab/` (or configured Wiki directory) out of Git.
4. Run `LLM Wiki: Check Setup and Health`.
5. Set up project memory explicitly.
6. Keep AI summaries **OFF first** and verify the core loop:
   - remember one small real file;
   - ask a normal historical/project question without naming Wiki tool names;
   - observe whether the Agent uses memory naturally;
   - when a memory hit matters, observe whether it follows to verified raw provenance.
7. Smoke one user-owned decision:
   - “remember that we decided X because Y”;
   - later explicitly supersede/change it once.
8. Smoke one changed remembered file and one explicit lineage resolution.
9. If AI summaries will actually be used, enable them separately and try one small real source.
10. Before valuable long-horizon use, make one approved **whole `.wiki-lab/` snapshot**.

### Day-0 stop/fix conditions

Fix before continuing long-horizon dogfood if any of these appear:

- admitted/canonical data is lost or corrupted;
- a write crosses an authority/privacy boundary without the required user decision;
- provenance cannot resolve a load-bearing remembered claim;
- the installed core path cannot be used reliably;
- a causal failure is hidden enough that the Agent/user cannot recover without guessing;
- setup/disable boundaries leave tools available in an unauthorized state.

Do **not** stop the dogfood merely because retrieval is imperfect, a confirmation feels slightly annoying, usage visibility is missing, or a navigation UI might be nice.
Those are exactly the things natural use should evaluate.

## Primary evidence track — Issue #141

Natural use is now the decisive product test.

Observe, without manufacturing scenarios:

- does ordinary Agent conversation invoke project memory at the right moments?
- does a useful memory hit naturally follow through to `wikiRead` / verified provenance?
- do saved decisions and rationale get recovered days or weeks later?
- does LLM Wiki actually save re-reading/re-discovery effort?
- is source-admission confirmation tolerable or repeatedly disruptive?
- is changed-source lineage understandable in real work?
- are AI summaries useful enough to justify their latency/spend?
- is the daily AI-summary soft guard useful or annoying?
- does hidden maintenance consumption create repeated uncertainty?
- is a dedicated navigation/history surface ever genuinely missed?
- do causal product fields keep the Agent from inventing failure explanations?

Record **natural events worth remembering**, not artificial coverage counts.

## How to react to dogfood evidence

### Fix promptly

A narrow product fix is justified when installed use shows repeated or high-impact:
- data/integrity failure;
- authority/privacy violation or confusing authority decision;
- broken setup/update/recovery path;
- provenance failure;
- misleading causal diagnostics that cause wrong Agent behavior;
- severe recurring UX friction on the normal path.

### Accumulate evidence first

Do not immediately implement from one mild observation:
- usage/token/AI-credit dashboard;
- Tree/Activity/history UI;
- alternate retrieval defaults;
- automatic concept/entity routing;
- large-source chunk/compile pipeline;
- automatic backup/sync;
- broader ingestion formats.

Repeated natural friction should choose the next slice.

If hidden maintenance usage becomes a repeated real problem, the leading candidate is **product-owned usage visibility**.
Keep these distinct:
- local model-call count;
- tokens;
- actual Copilot AI credits / premium requests.

Never infer one from another.

## Research posture

Architecture research is not the current priority.

Current gate state:
- **G1 Retrieval / Composition: closed** as exploratory mechanism search.
- **G2 Persistence: NOT_EARNED; parked.**
- **G3 Identity / Routing: NOT_OPENED.**

The useful retained E023 principle is:

> A representation may preserve authority globally while a later selection bottleneck destroys it locally.

And for any future rebuildable persistent state:

> Bind it to a deterministic source-authority snapshot and fail closed to current authority when stale.

These principles do **not** authorize persistence.

Do not start merely because the mechanism is available:
- same-slice AQ/BQ/CQ/DQ/PQ semantic reruns or tuning;
- product top-6/default-composer promotion;
- persistent semantic dossiers;
- graph DB / universal Entity-Relation-KnowledgeUnit schema;
- automatic identity discovery/merge/split/routing;
- vector retrieval defaults;
- background semantic maintenance/watchers;
- broad automatic contradiction resolution;
- federation/X2;
- evaluator clauses as runtime canonical structure.

Reopen G2 only from **independent natural evidence** that query-time reconstruction is materially too slow, costly, unreliable, or unable to provide a repeatedly needed durable derived view.
Any reopened experiment uses new separated material and fresh preregistration.

## Known reliability edges — not current blockers

Issue #132 remains open and evidence-gated:

- `.wiki-lab/agent-state.json` deletion is not independently detectable;
- canonical lineage relation append and pending workflow-state resolution are not one transaction.

Current posture:
- use whole-directory private snapshots;
- fail closed on detected corruption;
- do not claim atomicity/state-loss detection that does not exist;
- do not preemptively replace storage with a database/WAL;
- fix narrowly if installed use or recovery tests make these edges material.

Also retained:
- Human Knowledge file deletion is not independently detectable without an index.

## Operating edges

- Copilot CLI runtime capability probing is authoritative over version assumptions.
- `compiled_provider=disabled` is expected and unrelated to AI-summary maintenance.
- daily maintenance call threshold is a soft guard; `0` disables new model-backed summary generation.
- source-size policy:
  - `<=40k` chars: preferred single pass;
  - `40,001–80k`: allowed oversize single pass;
  - `>80k`: preserve RAW, skip derived maintenance before model call;
  - never silently truncate.
- exact-current workspace-file bytes reuse existing evidence without a second admission modal.
- multi-root workspaces remain fail-closed in 0.1.16.
- E013/E015 remain natural/data-gated; do not manufacture workload or divergence.

## NEXT ACTION

**Run the Day-0 installed smoke on the exact 0.1.16 VSIX.**

If it passes:
1. take a whole-Wiki backup snapshot;
2. freeze the product binary;
3. use LLM Wiki on real work;
4. record only meaningful natural observations on #141;
5. let repeated installed friction select the next product slice.

Do not add another research gate before this unless the Day-0 smoke exposes a concrete blocker.

## Fast pointers

- installed natural dogfood: Issue #141
- release-readiness audit: Issue #158 / PR #159
- reliability follow-up: Issue #132
- current VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
- user guide: `dogfood/vscode/README.md`
- backup/restore: `docs/11-local-backup-restore.md`
- E020 deterministic contract: `experiments/E020-synthetic-agent-ux/README.md`
- E023 current closure: `experiments/E023-generality-retrieval-composition/README.md`
- G2 closure decision: `experiments/E023-generality-retrieval-composition/g2-closure-decision-v0.md`
- generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- autonomy philosophy: `docs/12-autonomy-ux-philosophy.md`
