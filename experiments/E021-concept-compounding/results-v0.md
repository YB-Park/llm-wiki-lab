# E021 result — cross-source Agent Wiki concept compounding v0

Status: **PASS for the narrow mechanism tested.**  
Product promotion: **NO automatic concept routing yet.**

## Frozen question

Can exact `gpt-5.6-luna` maintain one stable, derived/noncanonical/rebuildable Agent Wiki concept page across multiple admitted raw sources, while preserving raw provenance and treating prior generated concept state as working state rather than evidence?

## Frozen source sequence

1. A — `docs/12-autonomy-ux-philosophy.md`
2. B — `experiments/E018-steward-policy/results-phase1-v0.md`
3. C — `experiments/E019-agent-wiki-maintenance/results-v0.md`

The main workflow froze the exact source bytes and SHA-256 values before generation and executed against those frozen copies.

## Budget / integrity

- exact model: `gpt-5.6-luna`
- model calls: **3** — one each for v1, v2, v3
- semantic rerolls: **0**
- prior generated page citations were redacted before the next update
- every load-bearing output string was required to cite admitted raw evidence through the existing product citation-handle transport

## Automated frozen checks — all passed

- one stable deterministic concept identity/title across v1/v2/v3;
- v2 and v3 were meaningful updates rather than identical re-emissions;
- no unknown provenance IDs;
- every summary/principle/boundary/open-question string retained admitted raw provenance;
- v2 contained genuine A+B cross-source synthesis;
- v3 retained A, B, and C;
- v3 contained a B+C-grounded distinction between the **rejected mandatory per-turn policy-judge/Steward role** and the **supported Luna maintenance role**;
- v3 retained the A-grounded human admission / epistemic-authority boundary;
- deterministic wrapper remained `DERIVED / NONCANONICAL / REBUILDABLE`, with prior generated state explicitly not evidence, no Human Knowledge authorship, and no canonical mutation.

The workflow completed successfully under the preregistered scorer. No reroll or threshold change was used to obtain the result.

## What this earns

E021 provides real evidence that **cross-source concept compounding is technically viable with Luna** under our raw-first authority contract. This is meaningfully closer to the Karpathy-style persistent Wiki than source-scoped summaries alone.

It earns investigation of the **smallest concept-page product slice**.

## What this does NOT earn

The experiment supplied a fixed concept identity and a deliberately relevant source sequence. It did **not** test:

- automatic concept discovery / identity / deduplication;
- deciding which admitted source belongs to which concept page;
- when a concept page should be refreshed automatically;
- topic-to-concept mapping or Agent Inbox behavior;
- large-scale concept-page retrieval;
- vectors, graphs, ontology infrastructure, background watching, or autonomous canonical mutation.

Therefore do **not** ship automatic concept routing from this result alone. The next concept-level question is routing/identity under realistic admission, not whether Luna can write a page when the concept and sources are already supplied.

## Product consequence

Keep Dogfood 0.1.11 as the human-installed P7 baseline. Its source-scoped Agent Wiki remains valid and useful. Record E021 as a positive mechanism result, then let installed use plus a narrow future routing experiment decide whether concept pages enter the next product slice.
