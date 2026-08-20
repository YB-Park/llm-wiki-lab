# E024 — Wiki Query Plane / Main-LLM Token Firewall Gate

Status: **ACTIVE / Q0+Q1 PROSPECTIVE GATE / NO PRODUCT RUNTIME CHANGE YET**

Tracking: Issue #204  
Advisory precursor: `research/advisory-reviews/2026-08-20-luna-wiki-query-plane-review.md`

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

### Q1 — L0 token-firewall comparison

Hold **the exact retrieved authority context identical** across paired arms on new separated material.

- **M — Main-context proxy:** the full Wiki context is treated as visible to the interactive model; Luna composes an answer only to provide a controlled semantic comparator.
- **Q — Query Plane:** the same full context is private to internal Luna; only a compact Wiki Brief leaves the Query Plane.

Q1 asks whether compression/delegation itself is safe and valuable. It intentionally does **not** change retrieval.

Primary hypothesis:

> Q can reduce Main-Agent-visible Wiki context by a large margin with no semantic regression, no new critical authority error, and terminal provenance preserved.

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

The exact top-6 current mixed-authority context is prospectively frozen per question. Q1 does not tune retrieval after seeing model outputs.

## Promotion is strict

Q1 earns the L0 Query Plane hypothesis only if all primary thresholds in `q1-evaluation-contract-v0.json` pass.

A failure does not authorize prompt tuning on Q1 material.

Interpret failures by root cause:

- **retrieval/context insufficiency in both arms** -> candidate new Q2 retrieval question;
- **Q-only semantic regression** -> Query Plane/brief contract not earned;
- **provenance/authority violation** -> stop; trust boundary failure;
- **token reduction weak but semantics good** -> token-firewall value not earned;
- **transport/runtime failure** -> execution invalid, not a semantic verdict.

## Explicit non-authorizations

E024 does not authorize:

- product runtime changes before the gate result is reviewed;
- replacing `wikiMemory`/`wikiRead` diagnostics;
- semantic persistence;
- graph/entity/KU storage;
- vector defaults;
- automatic identity routing;
- federation;
- storing query chain-of-thought;
- silent fallback that dumps raw Wiki context into the Main Agent;
- provider/model fallback away from exact Luna;
- using DERIVED_MEMORY as terminal authority.

## Why this is separate from E023

E023 asked whether richer retrieval/composition/persistent projections earn semantic value.

E024 asks a different systems question:

> **Who should pay the Wiki-reading context/reasoning cost?**

E023 evidence is used only as prior mechanism evidence: planner/selector complexity did not earn itself, so E024 starts from a strong simple retrieval baseline rather than assuming more agentic steps are better.
