# E007 Family N — conclusion v0

Status: **Family N closed for further forensic analysis.** This note freezes what E007 changed in our beliefs and what it did not establish. No new LLM runs are introduced here.

## Objective reminder

The project objective remains:

> Find the minimum architecture and operating discipline in which useful understanding compounds faster than error and maintenance debt.

E007 was a trust gate. It was not a contest to select a winning wiki implementation, model, or IDE adapter.

## What survived repeated review

### 1. Generic recursive rewrite is not trustworthy enough

C1 repeatedly lost provenance in the persistent state itself. This was not merely an answer-format failure. Generic prose maintenance did not reliably preserve the evidence identity needed for later verification.

**Decision-relevant implication:** provenance/evidence identity must be explicit in the maintenance contract or representation. It should not be expected to emerge from a generic instruction to summarize well.

### 2. Raw-source authority materially changes failure behavior

C2 removed the repeated C1 provenance-loss cluster when the wiki was explicitly treated as derived context and authoritative raw sources remained available.

However C2 reread all available raw sources and rewrote the full wiki on every wave. At this scale it used more total inference than C0 and did not reduce answer-context cost. The final wiki was not meaningfully compressed.

**Working implication:** source grounding looks like a safety floor; full-history recompilation on every ingest does not yet look like the right maintenance algorithm.

### 3. State fidelity and answer behavior are separate reliability layers

Several deterministic failures occurred while the committed wiki still contained all preregistered literal anchors needed for the answer. Conversely C1 provenance failures often showed the relevant source identity already absent from the state.

Therefore a failed answer cannot be treated as proof that canonical knowledge is corrupted.

**Decision-relevant implication:** future evaluation and automation must distinguish at least:

1. evidence/source truth,
2. canonical-state fidelity,
3. retrieval/answer behavior,
4. evaluator behavior.

### 4. Verification is not automatically a trust boundary

C3/C4 performed 17 transition repairs. Literal deterministic anchor coverage improved in none of those repairs. Verifier issue counts did often change, so this does not prove zero semantic value.

More importantly, 10 repaired transitions were committed while the final verifier still returned `revise`.

The implemented semantics were therefore:

`detect -> repair once -> reverify -> commit even if still suspect`

That is bounded repair, not a canonical commit gate.

### 5. Behavioral regression failure is too noisy to directly authorize canonical mutation

C4 included a concrete case where measurement-suspect Q025 triggered a regression repair and mutated canonical state. Other failures such as Q018 occurred while the state still contained all required literal facts.

**Decision-relevant implication:** `answer failure -> repair canonical state` is an unsafe default coupling. A state-level diagnosis or stronger confirmation boundary is needed before mutation.

### 6. More maintenance sophistication can create state and operational debt

C4 had the highest operational complexity and the largest state-size outlier. The C4-r01 state grew to roughly 4.5x raw size. Structural diagnostics did not show exact duplicated paragraphs, so the growth was not simple copy-paste duplication; it was path-dependent non-duplicate expansion/verbosity.

This is not proof that regression protection is harmful in general. It is evidence that recursive full-document rewriting plus repair loops can create maintenance debt even while local checks pass.

### 7. C0 remains a mandatory baseline

At six waves / eighteen clean synthetic sources, raw full-context remained extremely competitive in both quality and cost.

This does **not** establish that a wiki is unnecessary. It establishes that persistent compilation has not yet earned its complexity at this scale. Future wiki variants must continue to beat or justify themselves against raw/search/long-context baselines rather than assuming compilation is inherently useful.

## Measurement lessons

### Q025

The preregistered Q025 provenance rule was likely over-strict because S013 restated much of the reasoning that the rule required S007 to support separately. We preserve the original primary score for protocol integrity, but Q025 remains measurement-suspect and is reported with sensitivity analysis.

### Structured-output boundary

The run exposed multiple model-facing contract failures: literal JSON control characters, missing/extra IDs, malformed answer items, boolean type mismatch, and missing answers. The harness itself also had bugs.

These are distinct categories:

- model contract failure -> evidence about automation-interface reliability;
- harness bug -> evidence about orchestration complexity and engineering discipline.

Neither should be hidden by rerolling until a clean output appears.

## Claims E007 does not support

E007 does not establish that:

- C2 is the production architecture;
- transition verification is useless;
- regression testing is harmful in general;
- raw context will remain superior at larger scale;
- a hard rollback policy is better than commit;
- a particular model is the cause of the observed architecture patterns;
- Markdown single-document state is the right representation.

No ADR is justified yet.

## Why the next uncertainty is the canonical commit boundary

The strongest cross-cutting risk exposed by E007 is not proposal generation. It is **mutation authority**.

An LLM may be useful at proposing consolidation, detecting contradictions, or drafting a repair while still being an unsafe authority for deciding that a suspect proposal should replace canonical knowledge.

The next question therefore becomes:

> When a semantic maintenance proposal is uncertain, what evidence is sufficient to mutate canonical knowledge, and when should the system commit, quarantine, retain the previous state, or escalate to human review?

This question is logically prior to optimizing consolidation cost or IDE automation. A cheaper maintenance algorithm is not useful if its commit semantics silently accumulate bad state.

## Next experiment selection

The pre-existing experiment program reserves E008 for error-book learning and E009 for human-review risk tiers. We keep those identifiers intact.

E007 activates **E009A — Canonical Commit Boundary**, a focused first sub-study of E009.

E009A will isolate commit/adjudication policy from proposal-generation quality using frozen controlled transition cases. It will measure bad commits, blocked good updates, quarantine/review burden, verifier cost, and false positives on legitimate semantic changes.

A sequential compounding follow-up will be opened only if the one-step adjudication study identifies a policy worth carrying forward.

## Deferred but still important

After the commit boundary is better understood, the current high-value queue remains:

- E003 temporal update semantics;
- E004 provenance granularity;
- E002 staged/selective consolidation;
- E001 knowledge-unit representation;
- E006 retrieval escalation;
- scale/horizon stress against raw long-context;
- E008 error-book learning;
- E009B behavioral-alarm-to-mutation authorization;
- E010 real VS Code/Copilot usability only after semantics are sufficiently stable.

## Exit statement

E007 Family N succeeded by **changing the research question** rather than selecting a winner.

The strongest emerging architectural direction is provisional:

`LLM semantic proposal != canonical mutation authority`

We now test that statement instead of promoting it to policy by intuition.
