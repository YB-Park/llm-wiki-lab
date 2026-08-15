# E019 — Luna Agent Wiki maintenance result v0

Date: 2026-08-16 KST  
Issue: #121  
Parent: #110  
Preregistration: `preregistration-v0.md`

## Verdict

**AUTO FAIL / MANUAL SEMANTIC PASS — do not reroll.**

The one frozen `gpt-5.6-luna` maintenance generation produced a strong provenance-linked noncanonical Agent Wiki artifact and preserved the required product boundaries. The automatic scorer nevertheless marked the run `FAIL` because one lexical regex did not recognize the model's semantically correct phrasing for the no-recursive-contamination rule.

Do not rewrite the frozen automatic status and do not call the model again. Treat this as a harness false negative, analogous to prior manual adjudications where the preregistered semantic criterion was satisfied but the keyword implementation was too narrow.

Product consequence: **Luna earned a narrow derived-maintenance product slice, not a mandatory per-turn policy role.**

## Executed evidence

- workflow run: `31892566917`
- head: `0f15d99b9d7ce727a30bf34f534fa2e38654e8a5`
- artifact: `9248930797`
- artifact digest: `sha256:da10a67fb9021d95c13335856a7d41d8cca6ea71ed7675201cb3b0d38e855d1e`
- exact model: `gpt-5.6-luna`
- model calls: **1**
- semantic rerolls: **0**
- recorded CLI/subprocess latency: **10.833 s**
- source chars: **15,035**
- additional Copilot purchase: **not required**

No trustworthy complete dollar/token total is asserted from this run.

## What Luna produced

The deterministic wrapper created a Markdown artifact headed:

> **AGENT WIKI — NONCANONICAL / REBUILDABLE**

The model-derived body contained:

- 1 compact summary;
- 9 operational rules;
- 6 boundaries;
- 4 open questions.

Every load-bearing string in the summary, operational rules, and boundaries contained the supplied provenance citation, which the existing fail-closed citation-handle layer materialized to the one admitted canonical source ID.

Representative derived rules included:

- explicit source admission authorizes mechanical ingest and derived maintenance only within granted scope/budget;
- ordinary agent conversations may automatically search/read admitted Wiki evidence under scoped trust;
- Agent Wiki summaries/links/indexes/tensions may be maintained without per-page approval after maintenance opt-in;
- Agent Wiki remains inspectable, diffable, reversible, rebuildable, and separate from canonical evidence/Human Knowledge;
- explicit user-stated authorship may create Human Knowledge, while inferred belief/decision is proposal-only;
- source conflicts may be recorded as derived tension, but correction/change/dispute/supersession semantics remain a pending human decision;
- external-model use and paid maintenance require standing permission/budget;
- query-derived synthesis must use underlying admitted evidence rather than treating a prior agent answer as new evidence.

## Frozen automatic checks

The runner recorded all of these as `true`:

- `human_controls_admission_and_commitment`
- `derived_maintenance_within_granted_authority`
- `agent_wiki_derived_noncanonical_rebuildable`
- `human_authorship_boundary_preserved`
- `conflict_semantics_human_gated`
- `forbidden_claim_absent`
- `all_load_bearing_strings_cited`
- `citations_present`
- `citations_only_admitted_source`
- `exact_model`
- `integrity_clean`
- `generated_artifact_not_reingested`
- `exactly_one_model_call`

One required checker was `false`:

- `generated_text_not_raw_evidence`

A secondary non-gating checker was also `false`:

- `privacy_budget_scope_preserved`

## Why the automatic FAIL is a harness false negative

The preregistered criterion was semantic and explicitly said the scorer did **not** require exact wording.

The generated artifact directly said:

- Agent Wiki content is derived/noncanonical and **must never silently become raw evidence** merely because a model authored it.
- Query-derived synthesis should use underlying admitted evidence **rather than treating the agent's prior answer as new evidence**.

Those statements satisfy the frozen no-recursive-contamination requirement. The implementation regex expected a narrower word order involving tokens such as `generated` or `answer` followed by an explicit `not/never` before `evidence`; it missed both correct phrasings.

The secondary privacy/budget miss was similarly lexical: the output used `external-model` with a hyphen while the checker looked for `external model` / `model exposure` / `privacy`. The same generated operational rule explicitly required standing permission plus visible budgets/caps and no surprise background cost.

Because the model output is frozen and already satisfies the semantic criteria, **do not rerun or rescore it as a new model trial**. Record the harness limitation and move on.

## Trust-boundary evidence

The temporary Wiki remained integrity-clean after generation.

Canonical history contained exactly **one ingest event**: the original human-admitted source. The generated Agent Wiki artifact was written only as experiment output and was not re-ingested into raw/canonical evidence.

The generated note also explicitly separated itself from:

- raw evidence;
- canonical truth;
- Human Knowledge authorship.

This is the key property needed before allowing model-owned maintenance to persist in the product.

## Product decision

Proceed with the smallest opt-in maintenance implementation:

`explicit remember -> immutable raw admission -> if standing maintenance/privacy/budget grant is enabled, one bounded Luna call -> provenance-linked noncanonical Agent Wiki source note`

Required implementation constraints:

1. maintenance is **OFF by default** until the user grants standing workspace permission for external model use/spend;
2. the derived artifact is stored outside canonical manifest/history and is clearly labeled noncanonical/rebuildable;
3. every generated load-bearing string must pass citation-handle validation against admitted evidence;
4. inferred Human Knowledge is never written;
5. correction/change/dispute/supersession/destructive operations remain unavailable to the maintenance path;
6. generated Agent Wiki text is never re-ingested as raw evidence;
7. duplicate admission of the same current source should reuse an existing derived note rather than spend another model call when nothing changed;
8. a hard source-size/call budget guard prevents surprise maintenance cost;
9. derived-memory use must remain visibly distinct from canonical/raw evidence in ordinary agent reads.

E019 does **not** justify background source watching, a broad ontology, autonomous canonical semantics, or promotion of the persistent compiled provider.
