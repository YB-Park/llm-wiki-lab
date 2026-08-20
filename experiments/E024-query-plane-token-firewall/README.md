# E024 — Wiki Query Plane / Main-LLM Token Firewall Gate

Status: **Q1 L0 PROMOTION EARNED / Q2 ITERATIVE RETRIEVAL NOT YET EARNED / NO PRODUCT RUNTIME CHANGE IN E024**

Tracking: Issue #204  
Advisory precursor: `research/advisory-reviews/2026-08-20-luna-wiki-query-plane-review.md`  
Frozen result: `q1-v2-results-v0.md`

## Current result

Valid semantic run **32379189525** completed 18/18 exact `gpt-5.6-luna` calls with zero rerolls. The Query Plane arm passed all 9 semantic cases with no critical errors or paired regressions.

Main-Agent-visible context reduction was materially stronger than the preregistered gate:

- median external-character ratio: **0.051865** vs frozen maximum 0.35;
- maximum external-character ratio: **0.076169** vs frozen maximum 0.50;
- largest serialized Wiki Brief: **583 characters** vs frozen maximum 2200.

Therefore **Q1 earns the L0 Query Plane / token-firewall architecture candidate**.

This does not earn iterative Luna retrieval. Q2 remains conditional on independent evidence that one-shot deterministic retrieval misses load-bearing authority.

## Question

As LLM Wiki grows, can the product move Wiki-specific reading/composition work behind a Luna-backed Query Plane so the interactive Main Agent sees a small, authority-backed result instead of a large Wiki evidence context?

The target is not minimum total model tokens.

> **Spend Luna tokens when needed; protect the Main Agent's context and tool-turn budget.**

## Architecture hypothesis

```text
Main Agent
    |
    | wikiConsult(self-contained question)
    v
LLM Wiki Query Plane
    |
    +-- deterministic authorized retrieval
    +-- terminal-authority resolution
    +-- exact gpt-5.6-luna composition
    |
    v
compact Wiki Brief
    |
    v
Main Agent
```

The Query Plane is read-only and derived. It cannot admit sources, mutate Human Knowledge, decide canonical temporal relations, or persist its own synthesis as authority.

## Ordered gates

### Q0 — measurement contract

Freeze what counts as success before any E024 semantic call:

- Main-Agent-visible Wiki characters;
- internal evidence characters;
- model call count;
- citation/authority validity;
- semantic adjudication;
- insufficiency behavior;
- bounded output size.

Q0 explicitly separates local model calls, token usage, and provider billing. Exact token/credit numbers are recorded only when the transport exposes them.

### Q1 — L0 token-firewall comparison — EARNED

Hold **the exact retrieved authority context identical** across paired arms on new separated material.

- **M — Main-context proxy:** the full Wiki context is treated as visible to the interactive model; Luna composes an answer only to provide a controlled semantic comparator.
- **Q — Query Plane:** the same full context is private to internal Luna; only a compact Wiki Brief leaves the Query Plane.

Q1 asks whether compression/delegation itself is safe and valuable. It intentionally does **not** change retrieval.

Observed outcome: semantic parity was preserved on the frozen sample while Main-Agent-visible Wiki context fell to roughly 5% at the median.

See:

- `q1-freeze-correction-v2.md` for the presemantic freeze correction history;
- `evidence/q1-v2-run-32379189525/` for immutable raw evidence;
- `q1-v2-adjudication-v0.json` for semantic adjudication;
- `q1-v2-results-v0.md` for the gate result;
- `validate_q1_v2_result.py` for zero-model gate arithmetic.

### Q2 — iterative evidence-follow, conditional

Q2 is **not automatically opened by Q1 success**.

Only open Q2 from independent evidence that one-shot deterministic retrieval is materially insufficient. If opened, use a new separated corpus and compare the strongest simple Q1 retrieval against a tightly bounded evidence-follow worker. Do not reuse Q1 material to tune retrieval.

Candidate constrained actions:

```text
SEARCH(query, authorized_scope)
READ(source_id, bounded_range)
STATUS(source_id/topic)
FINAL(answer, terminal_refs, insufficient)
```

No shell, web, arbitrary MCP, file writes, memory writes, or canonical mutation.

## Q1 separated material

`q1-corpus/` contains synthetic memory unrelated to E023's AQ/BQ/CQ/DQ/PQ slices.

It deliberately includes:

- user-owned decisions;
- identity bridge + same-name distractor;
- current-vs-historical operational reasoning;
- capability-vs-authorization distinction;
- negative evidence / anti-generalization;
- repeated independent observations;
- a misleading DERIVED navigation note whose terminal sources disagree with its tentative synthesis;
- a raw prompt-injection fixture explicitly stored as quoted data;
- a true insufficient-authority case.

The exact top-6 current mixed-authority selected IDs were prospectively frozen per question. Q1 did not tune retrieval after seeing model outputs.

## Freeze correction history

The first execution contract contained bookkeeping defects in manually generated file/context hashes. CI caught both before Copilot installation or any semantic call. Those attempts are explicitly invalid/no-run history.

Q1-v2 simplified the source lock: the Git frozen-parent commit is the authority, the semantic execution commit changes only its signal file, and actual rendered context hashes/lengths are derived from the frozen sources + renderer and captured in immutable evidence.

No semantic threshold, question, selected ID, prompt, or model was weakened after outputs existed.

## Q007 posthoc product observation

The Q007 brief correctly answered Nimbus ownership from terminal RAW authority and did not cite DERIVED memory. It also included a true but non-load-bearing authorship fact without carrying that fact's R016 provenance in `terminal_refs`.

This did not change the frozen semantic verdict because the load-bearing ownership proposition was fully grounded. It does suggest a product-contract tightening:

> **A Wiki Brief should either omit non-load-bearing factual embellishment or include terminal provenance for it.**

Do not use this observation to rewrite Q1 after the fact.

## Competing hypotheses still open

Q1 establishes that Luna-backed composition can provide a strong token firewall. It does not establish that Luna is necessary for every query. A deterministic bounded evidence packet remains a competing low-cost hypothesis and should be tested separately.

Likewise, Q1 does not establish that iterative Luna retrieval is valuable. Agentic evidence-follow must earn itself on separated miss cases.

## Explicit non-authorizations

E024 Q1 does not authorize:

- semantic persistence;
- graph/entity/KU storage;
- vector defaults;
- automatic identity routing;
- federation;
- storing query chain-of-thought;
- silent fallback that dumps raw Wiki context into the Main Agent;
- provider/model fallback away from exact Luna;
- using DERIVED_MEMORY as terminal authority.

A minimal L0 product prototype is now evidence-backed, but runtime mutation should live in its own implementation slice with explicit privacy/grant semantics and installed tests rather than being mixed into the experiment evidence PR.

## Why this is separate from E023

E023 asked whether richer retrieval/composition/persistent projections earn semantic value.

E024 asks a different systems question:

> **Who should pay the Wiki-reading context/reasoning cost?**

E023 evidence is used only as prior mechanism evidence: planner/selector complexity did not earn itself, so E024 starts from a strong simple retrieval baseline rather than assuming more agentic steps are better.
