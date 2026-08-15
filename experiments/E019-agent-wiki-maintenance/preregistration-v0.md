# E019 — Luna Agent Wiki maintenance experiment preregistration v0

Status: **frozen before model scoring**  
Date: 2026-08-16 KST  
Issue: #121  
Parent design gate: #110

## Product question

After a human explicitly admits a source, can one bounded `gpt-5.6-luna` call do **useful derived Wiki maintenance** while preserving the ownership and provenance boundaries that distinguish Agent Wiki from raw evidence and Human Knowledge?

This is the post-E018 role for Luna. It is **not** a per-turn policy judge. The extra model call must perform actual compilation/maintenance work.

## Frozen source

Use the real repository file:

- `docs/12-autonomy-ux-philosophy.md`
- frozen Git blob: `ce68a3860066a0e795fb196b3b1cf7abc93ad4dc`

The runner creates a temporary Wiki, creates one topic, explicitly ingests this source, and then exposes the **complete immutable admitted bytes** to the maintenance call. The model is not asked to retrieve or choose a source in E019; source admission already happened.

## Frozen model/output shape

Exact model: `gpt-5.6-luna`.

Maximum calls: **1**. No rerolls.

The model receives untrusted quoted evidence plus short citation handles and must return JSON only:

```json
{
  "title": "...",
  "summary": "... C1",
  "operational_rules": ["... C1"],
  "boundaries": ["... C1"],
  "open_questions": ["... C1"]
}
```

The schema is intentionally generic. We are not hard-coding autonomy-specific fields into the maintenance product.

Deterministic code validates/materializes citation handles and wraps the parsed JSON into Markdown headed:

`AGENT WIKI — NONCANONICAL / REBUILDABLE`

with source ID, source object ID, source SHA-256, model, policy version, and generated-at metadata outside the model-authored body.

## Required semantic coverage

The frozen scorer does **not** require exact wording, but the generated artifact must preserve all of these load-bearing source rules:

1. **Admission / epistemic commitment:** the human controls what enters memory and what counts as the user's belief/decision/commitment.
2. **Granted derived autonomy:** the LLM may compile/maintain Agent Wiki within granted authority/scope rather than requiring approval for routine derived mechanics.
3. **Agent Wiki status:** Agent Wiki is derived, noncanonical, and reversible/rebuildable rather than raw/canonical truth.
4. **Human authorship:** explicit user-stated memory intent can authorize a Human Knowledge commitment; inferred belief/decision must not silently become the user's durable statement and is proposal-only by default.
5. **Conflict boundary:** correction/change/dispute/supersession semantics are high-consequence and human-gated/arbitrated by default.
6. **No recursive contamination:** generated answers/derived text must not become raw evidence merely because a model produced or reused them.

Secondary coverage recorded but not required to rescue a failure:

- external model exposure and paid maintenance need standing permission/budget scope.

## Structural/provenance pass conditions

All must hold:

- output is parseable JSON with exactly the allowed top-level fields;
- `title` and `summary` are non-empty strings;
- `operational_rules` has 5–10 strings;
- `boundaries` has 3–8 strings;
- `open_questions` has 0–5 strings;
- every load-bearing generated string in `summary`, `operational_rules`, and `boundaries` cites at least one supplied citation handle before materialization and therefore a canonical `src-...` ID after materialization;
- every materialized citation resolves to the one admitted source;
- all six semantic coverage checks pass;
- no forbidden claim makes Agent Wiki canonical truth, authorizes silent Human Knowledge overwrite, or treats generated output as raw evidence;
- exact model receipt is `gpt-5.6-luna` when reported;
- temporary Wiki integrity remains clean;
- canonical history contains only the original source admission: the generated Agent Wiki artifact is **not re-ingested**;
- exactly one model call was attempted.

## Interpretation

### PASS

A pass supports implementing the smallest **opt-in** product maintenance path:

`explicit remember -> raw admission -> one bounded Luna maintenance call -> noncanonical Agent Wiki artifact`

The product implementation must still require a standing privacy/model/budget grant before admitted source bytes are sent externally. A pass does not authorize background source watching, canonical mutation, Human Knowledge inference, or default compiled-provider promotion.

### FAIL

Do not wire automatic maintenance into the dogfood product merely to preserve the architecture. Inspect whether the failure is:

- source grounding/provenance;
- missing important maintenance content;
- ownership boundary violation;
- structured-output unreliability;
- or transport/infrastructure.

No semantic reroll is allowed on this frozen source.

## Cost discipline

- PR preflight: **0 model calls**.
- scored phase: **1 Luna call maximum**.
- Copilot CLI guard: 30 AI credits because current CLI rejects lower guard values; this is a ceiling, not an expected spend.
- No additional purchase is presumed. If Copilot rejects the bounded call because of available credits, stop and report that blocker rather than silently changing the experiment.
