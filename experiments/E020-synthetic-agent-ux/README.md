# E020 — Synthetic Agent-Wiki UX contract

Status: **active zero-model product gate for Dogfood 0.1.11**.

This is not a claim that synthetic scenarios replace installed human P7. It exists to remove decision/authority mistakes that can be found deterministically before asking a human tester to absorb them.

`score_contract.py` currently freezes **72 representative cases** across ambient read, provenance follow, prompt-injection framing, explicit source admission, dirty working-copy handling, same-file revision lineage, Human Knowledge authorship/lifecycle, durable pending authority state, maintenance spend limits, and intentionally deferred capabilities.

The scorer distinguishes:

- `supported` — 0.1.11 must expose a concrete deterministic/product mechanism now;
- `partial` — the product has a bounded mechanism but installed/model/process evidence is still required;
- `deferred` — intentionally not implemented because doing so would require a new authority, parser, transaction, or product decision.

Important: a high supported count is **not** a product-quality score. Deferred/partial cases are preserved to prevent the handoff from pretending the problem is solved.

Current intentionally unresolved examples include per-source forget/purge semantics, Human Knowledge deletion detection without an index, cross-source concept-level Agent Wiki compounding, autonomous query write-back, cross-process atomicity between canonical lineage and workflow-state resolution, and model-dependent prompt-injection compliance.

Model calls: **0**. E020 is entirely deterministic/static/runtime-contract validation.
