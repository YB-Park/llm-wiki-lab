# E024 Q1 v2 — Luna Query Plane token-firewall result

Status: **Q1 L0 PROMOTION EARNED**  
Valid semantic run: **32379189525**  
Model: **exact `gpt-5.6-luna`**  
Frozen parent: `499958ec5263a41f6ab28a2448c4c0608c0046f9`  
Execution signal head: `435dae2b89aeddc62a4470db1a043ee331fa93ff`

## Verdict

The frozen Q1 hypothesis is supported:

> **A Luna-backed internal Query Plane can absorb the composition/authority-reading step for the tested Wiki questions while preserving semantic/authority quality and reducing the Wiki context exposed to the interactive Main Agent by far more than the preregistered threshold.**

This earns the **L0 Query Plane / token-firewall architecture candidate**.

It does **not** earn iterative Luna retrieval, semantic persistence, federation, vectors, graph/ontology, or opaque answer-only memory.

## Frozen primary gate

| Gate | Frozen threshold | Observed | Verdict |
|---|---:|---:|---|
| exact Luna attempts | 18/18, rerolls 0 | 18/18, rerolls 0 | PASS |
| Q output contract | 9/9 | 9/9 | PASS |
| Q terminal refs | current RAW/HK only; no DERIVED terminal | 9/9 valid | PASS |
| Q semantic | >=8/9 PASS, 0 CRITICAL | 9/9 PASS, 0 CRITICAL | PASS |
| new Q critical vs M | 0 | 0 | PASS |
| paired semantic regression vs M | 0 | 0 | PASS |
| median external-char ratio | <=0.35 | **0.051865** | PASS |
| maximum external-char ratio | <=0.50 | **0.076169** | PASS |
| maximum serialized Q brief | <=2200 chars | **583 chars** | PASS |
| hard cases | Q001/Q007/Q009 preserved | preserved | PASS |

The median Query Plane brief was about **5.2%** of the full Wiki context proxy; the worst tested case was about **7.6%**. This is not a token-count claim: character count is the prospectively frozen transport-independent proxy. Upstream token/billing information was unavailable and is not inferred.

## Semantic adjudication

Both M and Q were adjudicated PASS on all 9 questions.

The cases covered:

- prompt-like instructions embedded inside RAW memory;
- explicit user/project Human Knowledge ownership;
- personal identity disambiguation;
- current vs prior state;
- capability vs authorization;
- negative evidence and anti-overgeneralization;
- repeated independent observations;
- deliberately misleading DERIVED navigation;
- true proposition-scoped insufficiency.

### Q007 audit observation

Q007 correctly ignored the misleading DERIVED note as terminal authority and correctly answered that Mateo Ruiz owns Nimbus. It also included a true non-load-bearing statement that Asha Patel authored the cache invalidation design, while listing only R017 in `terminal_refs`; R016 is the source for the authorship statement.

This does not change the frozen Q1 PASS because the load-bearing ownership proposition is fully established by R017. It does produce a product-contract tightening candidate:

> **A compact Wiki Brief should either omit non-load-bearing factual embellishment or carry terminal provenance for it.**

Do not retroactively modify the Q1 prompt or threshold because of this observation.

## Invalid/no-run history

Before the valid v2 run, fail-closed infrastructure caught two freeze-bookkeeping defects before any semantic model call. Those attempts are execution history only and are not part of the semantic sample.

- connector-authored signal `e135d3679af6b2d974eb63d7908b527c19d394f9`: no Actions check, zero semantic calls;
- PR run `32378526834`: source-lock validation failed before Copilot installation, zero semantic calls;
- zero-model run `32378526759`: prereg diagnostic mismatch, zero semantic calls.

The v2 correction was frozen and zero-model validated before the valid semantic signal. Q1 corpus semantics, questions, selected IDs, prompts, model, request budget, and promotion thresholds were not weakened after outputs existed.

## What Q1 actually establishes

Q1 deliberately held the user question, exact deterministic retrieval selection, and rendered Wiki evidence context identical between M and Q. Therefore the result isolates the **composition/context-boundary** hypothesis rather than retrieval quality.

The result supports this near-term product shape:

```text
Main Agent
    |
    | wikiConsult(question)
    v
LLM Wiki Query Plane
    |
    +-- deterministic authority retrieval
    |
    +-- exact Luna composition
    |
    v
compact provenance-backed Wiki Brief
    |
    v
Main Agent
```

The Main Agent should not receive the hidden retrieval/composition trace by default. The compact result must retain terminal authority/provenance and bounded insufficiency.

## What should happen next

### Product implication

A minimal L0 `wikiConsult` slice is now evidence-backed enough to prototype. It should stay above the existing Authority Core and avoid schema migration.

### Competing hypothesis still open

Q1 does **not** prove Luna is necessary for every compression step. A deterministic bounded evidence packet may protect Main-Agent context sufficiently in some cases. That is a valid competing hypothesis and should be tested separately rather than assumed away.

### Iterative Luna is not yet earned

Q1 provides no evidence that a Luna search/read loop is needed because required authority was intentionally present in the frozen top-6 context. Iterative search should require a separate failure-driven gate on cases where one-shot deterministic retrieval misses load-bearing authority.

## Promotion boundary

**E024 Q1 L0 promotion: EARNED.**

This promotion authorizes architectural/product prototyping of the L0 Query Plane candidate, subject to normal code review, permissions/privacy design, and installed validation. It does not itself alter canonical Wiki authority or authorize broader semantic infrastructure.
