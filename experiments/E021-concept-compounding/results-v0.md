# E021 result — cross-source Agent Wiki concept compounding v0

Status: **PASS for the narrow mechanism tested.**  
Product promotion: **NO automatic concept routing yet.**

## Frozen question

Can exact `gpt-5.6-luna` maintain one stable, derived/noncanonical/rebuildable Agent Wiki concept page across multiple admitted raw sources, while preserving raw provenance and treating prior generated concept state as working state rather than evidence?

## Frozen source sequence

1. A — `docs/12-autonomy-ux-philosophy.md`
2. B — `experiments/E018-steward-policy/results-phase1-v0.md`
3. C — `experiments/E019-agent-wiki-maintenance/results-v0.md`

The run used frozen source bytes and SHA-256 values under the preregistered E021 protocol preserved in PR #133.

## Budget / integrity

- exact model: `gpt-5.6-luna`
- recorded model calls: **3** — one each for v1, v2, v3
- semantic rerolls: **0**
- prior generated page citations were redacted before the next update
- every load-bearing output string was required to cite admitted raw evidence through the existing product citation-handle transport

## Recorded frozen checks — all passed

- one stable deterministic concept identity/title across v1/v2/v3;
- v2 and v3 were meaningful updates rather than identical re-emissions;
- no unknown provenance IDs;
- every summary/principle/boundary/open-question string retained admitted raw provenance;
- v2 contained genuine A+B cross-source synthesis;
- v3 retained A, B, and C;
- v3 contained a B+C-grounded distinction between the **rejected mandatory per-turn policy-judge/Steward role** and the **supported Luna maintenance role**;
- v3 retained the A-grounded human admission / epistemic-authority boundary;
- deterministic wrapper remained `DERIVED / NONCANONICAL / REBUILDABLE`, with prior generated state explicitly not evidence, no Human Knowledge authorship, and no canonical mutation.

No reroll or threshold change was recorded to obtain the result.

## Execution provenance note

The repository's retained GitHub Actions history for PR #133 contains the zero-model preregistration preflight, while its three-call `execute` job is recorded as skipped because that job was configured only for a push to `main`. The three-call PASS is recorded in Issue #131 and this result note, but there is no retained GitHub Actions execute-job artifact that independently demonstrates those three calls.

Treat this as an explicit provenance limitation, **not** as permission to rerun the frozen experiment. PR #133 remains the historical preregistration/runner record and should not be merged in its original form because its `main` push trigger would authorize another three Luna calls.

## What this earns

E021 is positive evidence that **fixed-identity cross-source concept compounding is viable with Luna** under the raw-first authority contract. It earns consideration of the smallest concept-page product slice.

## What this does NOT earn

The experiment supplied a fixed concept identity and a deliberately relevant source sequence. It did **not** test:

- automatic concept discovery / identity / deduplication;
- deciding which admitted source belongs to which concept page;
- when a concept page should be refreshed automatically;
- topic-to-concept mapping or Agent Inbox behavior;
- large-scale concept-page retrieval;
- vectors, graphs, ontology infrastructure, background watching, or autonomous canonical mutation.

Therefore do **not** ship automatic concept routing from this result alone. The next concept-level question is routing/identity under realistic admission, only if installed use makes it relevant.

## Product consequence

Keep Dogfood 0.1.11 as the human-installed P7 baseline. Do not spend more calls on frozen E021. Let installed use decide whether concept pages deserve the next product slice.
