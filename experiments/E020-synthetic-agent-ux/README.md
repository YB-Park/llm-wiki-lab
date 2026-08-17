# E020 — Synthetic Agent-Wiki UX contract

Status: **active zero-model product gate for Dogfood 0.1.11**.

This is not a claim that synthetic scenarios replace installed human P7. It exists to remove decision/authority mistakes that can be found deterministically before asking a human tester to absorb them.

`score_contract.py` now freezes **78 representative cases** across ambient read, verified provenance follow, JSON-encoded untrusted memory data, prompt-injection/metadata structural framing, explicit source admission, dirty working-copy handling, same-file revision lineage, verified old/new lineage review, Human Knowledge authorship/lifecycle/fork detection, durable pending authority state, maintenance spend limits, legacy locator migration, and intentionally deferred capabilities.

The scorer distinguishes:

- `supported` — 0.1.11 must expose a concrete deterministic/product mechanism now;
- `partial` — the product has a bounded mechanism but installed/model/process evidence is still required;
- `deferred` — intentionally not implemented because doing so would require a new authority, parser, transaction, or product decision.

Important: a high supported count is **not** a product-quality score. Deferred/partial cases are preserved to prevent the handoff from pretending the problem is solved.

New 0.1.11 hardening after the first 72-case pass:

- every untrusted/user/model-controlled memory text or metadata field returned to an Agent is JSON-encoded as `*_json`, so newline-bearing filenames/titles/content cannot create structural tool-result fields;
- pending lineage resolution shows a bounded verified old/new raw changed region before human confirmation;
- currentness and durable locator/SHA binding are checked before confirmation and again immediately before canonical mutation;
- Human Knowledge lineage forks/cycles fail closed rather than presenting multiple current user commitments;
- legacy 0.1.10 extension-local source locators migrate to durable `.wiki-lab/agent-state.json` when the source is explicitly touched again.

Current intentionally unresolved examples include per-source forget/purge semantics, Human Knowledge deletion detection without an index, cross-source concept-level Agent Wiki compounding, autonomous query write-back, cross-process atomicity between canonical lineage and workflow-state resolution, and model-dependent prompt-injection compliance.

Model calls: **0**. E020 is entirely deterministic/static/runtime-contract validation.
