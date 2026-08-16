# E021 — Cross-source Agent Wiki concept compounding

Status: **preregistered product experiment; no product implementation before evidence.**

## Question

Can exact `gpt-5.6-luna` maintain one persistent **derived concept page** across multiple explicitly admitted raw sources, rather than merely producing one disconnected note per source?

This is the narrow missing Karpathy-like behavior after 0.1.11. It is deliberately not a vector/graph/ontology/background-agent experiment.

## Frozen source sequence

The workflow freezes the exact bytes and SHA-256 values before any generation, then executes only against those frozen copies:

1. **A** — `docs/12-autonomy-ux-philosophy.md`
2. **B** — `experiments/E018-steward-policy/results-phase1-v0.md`
3. **C** — `experiments/E019-agent-wiki-maintenance/results-v0.md`

The sequence is intentionally cumulative:

- A defines the human/LLM authority contract.
- B adds empirical evidence that a mandatory per-turn Luna Steward did not earn promotion.
- C adds empirical evidence that Luna did earn a narrow derived-maintenance role.

The third update therefore tests whether a concept page can retain a **role distinction** rather than collapsing the evidence into “use Luna” or “do not use Luna.”

## Frozen generation protocol

- model: exact `gpt-5.6-luna`
- maximum / expected calls: **3** — exactly one call for v1, v2, v3
- semantic rerolls: **0**
- per-call Copilot guard: 30 AI credits (CLI guard ceiling, not expected spend)
- each source <= 40k bytes; total frozen sources <= 100k bytes
- at every update the model receives **all admitted raw evidence to date**
- prior concept state is supplied only as `UNTRUSTED WORKING STATE, NOT EVIDENCE`
- all raw source IDs are redacted from prior derived state before it is supplied to the next call
- every load-bearing string must cite admitted raw evidence; the normal product adapter validates/materializes citation handles

## Automated pass boundary

A PASS requires all of the following without changing the thresholds after seeing output:

1. one stable deterministic concept ID and exact title across v1/v2/v3;
2. each later payload differs from its predecessor;
3. every summary/principle/boundary/open-question string cites admitted raw evidence and no unknown source;
4. v2 contains at least one string that genuinely cites both A and B;
5. v3 cites A, B, and C somewhere in the page;
6. v3 contains at least one B+C-cited string that explicitly distinguishes a per-turn policy-judge/Steward role from a maintenance role;
7. v3 retains an A-grounded human admission/epistemic-authority boundary;
8. deterministic page wrapper remains `DERIVED / NONCANONICAL / REBUILDABLE`, with `prior_derived_state_is_evidence=no`, `human_knowledge_authorship=none`, and `canonical_mutation=none`;
9. model call count is exactly 3 and semantic rerolls remain 0.

A transport/model/shape/citation failure is a FAIL, not a reason to reroll.

## Decision rule

- **Material PASS:** concept-level compounding has earned a tiny product slice candidate. Implement the smallest concept-page maintenance path only; do not infer permission for vectors, graphs, background watching, canonical compiled truth, or autonomous epistemic mutations.
- **FAIL:** keep source-scoped Agent Wiki maintenance. Do not create a concept-Wiki architecture from preference.

## Cost discipline

PR validation is zero-model only. After merge, the path-restricted main workflow performs the three frozen calls once. Current Copilot access is used first. If the run is actually rejected for credits, stop and report the rejection before asking for payment.
