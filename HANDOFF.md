# Current Handoff

Last updated: 2026-08-20 KST — post-G2 closure checkpoint

This file is the **continuation checkpoint only**. Historical detail belongs in experiments, issues, PRs, ADRs, and Git. If this file conflicts with merged code or an accepted ADR, code/ADR wins.

## Start here

Repository: `YB-Park/llm-wiki-lab`

Latest completed controlled result entering this checkpoint:

- G2 result merge: `83eb3a4e00f65984ee418da06093d22bffde3f21` (#199)
- G2 run: `32353304896`
- execution source: `3cf65d7255b8edc73a9d8cb3d13338e019cc92f8`
- evidence commit: `c0a1cb01fbff29910c270283106217a111d00057`
- exact model: `gpt-5.6-luna`
- 29/29 semantic attempts, zero rerolls

Always re-check current `main` and open PRs before new work.

## North Star

Build a VS Code-first **LLM Wiki** where the user owns a verifiable project-memory system and the coding Agent naturally recovers and compounds useful knowledge inside explicit authority boundaries.

> **Human controls admission and epistemic commitment. LLM controls routine retrieval/compilation/maintenance inside granted authority.**

Architecture thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. Generality is demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

Normal product use should remain ordinary VS Code Agent conversation.

## Product baseline

Dogfood **0.1.16** remains the product baseline. E023 is research-only and has not changed runtime behavior.

Authority floor remains:

- explicit per-workspace opt-in;
- Check Setup and Health = 0 model calls / 0 state changes;
- disabling removes Agent availability while preserving Wiki data;
- new source bytes require human confirmation before durable admission;
- `RAW_MEMORY` = immutable admitted evidence/provenance;
- `DERIVED_MEMORY` = noncanonical/rebuildable synthesis;
- `HUMAN_KNOWLEDGE` = explicit user-owned decision/belief/rationale/hypothesis authority;
- changed remembered files require explicit correction/change/dispute/supersede/independent semantics;
- AI summaries remain off by default until granted.

E020 remains frozen at **78 zero-model cases: 60 supported / 7 partial / 11 deferred**.

Natural installed dogfood on Issue #141 is now the **primary product-evidence track**. Do not manufacture workload.

## Architecture gates — current state

1. **G1 Retrieval / Composition — CLOSED as exploratory mechanism search.**
2. **G2 Persistence — first fixed-identity candidate NOT_EARNED; PARKED.**
3. **G3 Identity / Routing — NOT_OPENED.**

Authority Core remains ontology-agnostic. Every load-bearing derived claim must resolve to terminal `RAW_MEMORY` or `HUMAN_KNOWLEDGE` with epistemic type preserved.

## G1 closure

Complex planner/selector/RRF mechanisms did not earn promotion.

The narrow research comparator carried into G2 was:

- exact whole-object BM25 top-6;
- frozen old composer from `run_g1c.py`;
- planner / selector / RRF = 0.

This is a controlled research baseline, **not a product top-6/default-composer policy**.

G1f on new separated material produced:

- old composer: 7 PASS / 1 PARTIAL / 0 critical;
- `composition_prompt_v1`: 7 PASS / 1 PARTIAL / 0 critical;
- new prompt improvements: 0.

Therefore `composition_prompt_v1` remains NOT_EARNED and DQ material must not be retuned/rerun.

## G2 result — persistence NOT_EARNED

PRs #197/#198/#199; run `32353304896`.

G2 held fixed subject identity and final composer constant.

- Q: current terminal authority -> exact BM25 top-6 -> frozen composer.
- P: query-blind persisted DERIVED projection -> deterministic terminal-anchor selection -> same composer.
- projection text never entered final composer context;
- stale projection snapshot mismatch required exact Q bypass.

Frozen semantic result:

- Q: **9 PASS / 1 FAIL_RETRIEVAL / 2 CRITICAL_ERROR**;
- P: **8 PASS / 1 FAIL_RETRIEVAL / 3 CRITICAL_ERROR**;
- P improvements: **2**;
- P regressions: **3**;
- P new critical errors: **3**.

Fresh selected terminal evidence chars:

- Q: 10,282;
- P: 7,019;
- P/Q: **68.3%**, passing the <=85% efficiency criterion.

But semantic/authority safety dominates efficiency, so:

> **`G2_PERSISTENCE_CANDIDATE_EARNED` = NOT_EARNED.**

### Positive G2 signals retained

- snapshot freshness guard worked on PQ007/PQ011;
- PQ011 primary stale 30 -> 90-day correction control had no stale/current inversion;
- all five query-blind projection builds/rebuilds preserved every terminal anchor in projection state;
- PQ004 repaired one prospectively frozen Q authority miss;
- selected answer context was materially smaller.

Reusable engineering principle:

> **Any future persisted/rebuildable derived state should be bound to a deterministic source-authority snapshot and fail closed to current authority when stale.**

This does not imply that semantic persistence itself should exist.

### Why persistence did not earn value

The projection compiler preserved authority globally, but later query-time retrieval over projection statements discarded load-bearing anchors:

- PQ008: required P021 second close observation existed in rebuilt projection but was not selected;
- PQ009: governing policy P026 existed in projection entry rank 3 but frozen top-2 selection omitted it -> P critical regression;
- PQ012: user-owned superseding decision P034 existed in projection entry rank 3 but was omitted -> P critical regression.

This repeats the broader E023 lesson:

> **A representation can preserve authority globally while a later selection bottleneck destroys it locally.**

Do not immediately increase projection top-k and rerun PQ. P021 was much deeper than rank 3, so a trivial posthoc top-3 tweak does not solve the prospective failure set anyway.

PQ007 is a causal nuance: stale bypass produced byte-identical P/Q terminal context and prompt, but the separate Luna calls diverged. Q safely returned `FAIL_RETRIEVAL`; P asserted unsupported repetition. Count the frozen P regression, but do not misattribute it to stale-projection selection.

## Research posture after G2

**Paid E023 semantic calls pause.**

G2 is parked and G3 is not opened.

Reopen G2 only if independent evidence makes persistence materially relevant, such as repeated natural use showing query-time reconstruction is too slow/costly/unreliable or users repeatedly need a durable derived view that current raw/query-time behavior cannot serve.

Any reopened persistence experiment must use **new separated material + fresh preregistration**. PQ is diagnostic history, not a tuning set.

Do not start from this result:

- product persistent semantic dossiers;
- graph DB / universal Entity/Relation/KnowledgeUnit schema;
- automatic identity discovery/merge/split/routing;
- vector defaults;
- background semantic maintenance;
- same-slice PQ semantic reruns or top-k tuning.

## NEXT CORE — natural installed product evidence

Issue #141 is now the default next work.

Observe naturally:

- whether ordinary Agent conversation uses Wiki memory without tool-name prompting;
- whether useful hits follow through to `wikiRead` provenance;
- whether decisions/reasoning are actually recovered days or weeks later;
- remaining setup/permission/popup friction;
- whether hidden Luna maintenance consumption becomes a **repeated real problem**;
- whether users actually miss a dedicated navigation/history UI.

Do not manufacture multi-session demand, >80k sources, navigation demand, or spend anxiety solely to justify a feature.

If hidden maintenance usage becomes repeated friction, the leading product slice remains **product-owned usage visibility**, keeping local model-call count, tokens, and actual AI credits/premium requests distinct. Do not infer credits from calls/tokens.

## Reliability parallel track

Issue #132 remains evidence-gated:

- agent-state deletion is not independently detectable;
- canonical relation append and pending-state resolution are not one transaction.

Do not replace storage with a database/WAL preemptively. Fix narrowly only if installed use/recovery tests make these edges material.

## Retained operating edges

- Copilot CLI compatibility uses runtime capability probing; version alone is not authority.
- `compiled_provider=disabled` remains expected and unrelated to Agent Wiki maintenance.
- daily maintenance limit is a soft guard; `0` disables new model-backed maintenance generation.
- <=40k chars preferred single pass; 40,001–80k allowed; >80k preserves RAW and skips derived maintenance before model call; never silently truncate.
- exact-current-byte remember is no-op reuse without a second admission modal.
- multi-root remains fail-closed in 0.1.16.
- Human Knowledge file deletion is not independently detectable without an index.
- E013/E015 remain natural/data-gated; do not manufacture workload/divergence.

## Fast pointers

- G1 closure: `experiments/E023-generality-retrieval-composition/g1-closure-decision-v0.md`
- G2 prereg: #197
- G2 execution contract: #198
- G2 result: #199 / run `32353304896`
- G2 result doc: `experiments/E023-generality-retrieval-composition/g2-results-v0.md`
- G2 closure: `experiments/E023-generality-retrieval-composition/g2-closure-decision-v0.md`
- generality gate: Issue #160 / `docs/14-generality-and-semantic-projections.md`
- natural installed dogfood: Issue #141
- reliability follow-up: Issue #132
- current VSIX: `dogfood/releases/llm-wiki-dogfood-latest.vsix`
