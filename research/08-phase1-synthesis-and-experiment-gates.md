# Phase 1 Synthesis and Experiment Gates

Date: 2026-08-12
Status: Phase 1 synthesis; not production architecture
Depends on: Research Batches A–F

## 1. Phase 1 question

We began with a deceptively simple idea:

```text
sources -> LLM -> personal wiki -> better future reasoning
```

Phase 1 asked whether this pattern is safe and useful enough to design directly, or whether important semantics and failure modes must be resolved first.

The answer is clear:

> The pattern is promising, but a naive "summarize and keep rewriting Markdown" implementation is not trustworthy enough to productize without controlled experiments.

The research landscape now gives us enough structure to stop broad exploration and begin targeted experiments.

---

## 2. The problem we are actually solving

A personal LLM Wiki is a **probabilistically maintained, lossy materialized knowledge view** over heterogeneous evidence and personal reasoning.

It must simultaneously optimize:

- future answerability,
- human comprehension,
- evidence traceability,
- tolerance of changing facts,
- preservation of history where valuable,
- repairability after model mistakes,
- retrieval efficiency,
- maintenance/token cost,
- sustainable human review.

This is closer to maintaining a semantic database/build artifact than to writing notes.

---

## 3. Evidence-supported recurring patterns

These are not yet production policies. They are the strongest cross-domain hypotheses because multiple independent fields/systems converge on them.

### P1 — Preserve an authoritative evidence path

Raw/source-of-record material and derived synthesis should not silently collapse into one authority layer.

Observed across:

- direct LLM Wiki implementations,
- Wikipedia source discipline,
- provenance models,
- agent memory with source-grounded records,
- materialized-view/event-history analogies.

### P2 — Capture and consolidation are different operations

Incoming information does not need to immediately rewrite canonical synthesis.

Observed across:

- Infini Memory buffers,
- Mem0-like extraction/consolidation pipelines,
- ingest triage/no-material outcomes,
- database refresh semantics.

### P3 — Compression must remain reversible enough for evidence recovery

WiCER demonstrates that coherent compilation can lose future-critical facts. LeanMem and layered retrieval systems preserve a path to detail/raw evidence.

### P4 — Maintenance should be selective

Stable, exact-record, dynamic-event, and speculative/personal knowledge may not deserve the same rewrite schedule or provenance burden.

### P5 — A semantic edit is a state transition that can regress

A proposed update can:

- omit important new evidence,
- delete valid old information,
- introduce unsupported claims,
- improve one query while degrading another.

Therefore final prose quality is not enough; transition/regression testing is required for high-impact edits.

### P6 — Time and revision semantics matter

Correction, supersession, disagreement, late discovery, and mere reorganization are distinct operations.

### P7 — Structure must be allowed to evolve

Folders/page boundaries/aliases are hypotheses about navigation. Split/merge/redirect/ambiguity are expected lifecycle states, not exceptional failures.

### P8 — Progressive disclosure is preferable to uniform context loading

Overview -> detail -> raw evidence is repeatedly supported by hierarchical retrieval, memory tiers, Wikipedia summary style, and direct LLM Wiki implementations.

### P9 — Retrieval strategy is query-dependent

Local exact, global sensemaking, multi-hop, temporal, provenance, and exploratory queries have different optimal access patterns.

### P10 — Cheap deterministic work should precede expensive LLM work

Filesystem/metadata filters, lint, dependency tracking, exact checks, and cheap relevance routing can reduce semantic calls and risk.

### P11 — Uncertainty is a legitimate system state

`disputed`, `ambiguous`, `needs_verification`, `dirty`, `possible_split`, etc. can be safer than forced automatic resolution.

### P12 — Automation should be judged on lifecycle economics

The wiki succeeds only if downstream value exceeds:

- ingest cost,
- repeated consolidation,
- indexing,
- verification/testing,
- repair after autonomous errors,
- and human review attention.

---

## 4. The failure model

We now distinguish at least these failure classes.

### F1 — Fabrication

Derived state contains unsupported information.

### F2 — Compilation loss

Derived state is factually clean but omits information needed later.

### F3 — Temporal corruption

Past/current truth, correction, or disagreement is represented incorrectly.

### F4 — Structural corruption

Knowledge exists but page identity, taxonomy, aliases, or links make it hard to retrieve/maintain.

### F5 — Maintenance regression

A change improves one area while silently harming previously useful knowledge or queries.

### F6 — Source-ownership error

A fact exists in the corpus but is attributed to the wrong source.

### F7 — Cost runaway

The wiki spends more tokens/model calls/human attention maintaining itself than the avoided rediscovery is worth.

### F8 — Automation trust failure

The system makes semantically consequential changes that are difficult for the user to notice, understand, or reverse.

The controlled corpus and metrics must contain explicit cases for all eight.

---

## 5. Architecture choices that are still intentionally undecided

Phase 1 does **not** justify choosing:

- atomic notes vs topic docs vs claim/event store,
- fixed page types,
- exact folder hierarchy,
- vector DB,
- graph DB,
- MCP service,
- claim-level provenance everywhere,
- automatic consolidation schedule,
- automatic split/merge/delete,
- temporal schema fields for every page,
- one universal retrieval method,
- maximum automation.

Any prototype that silently embeds these choices before experiments would violate ADR-0001.

---

## 6. Mandatory baseline principle

Every sophisticated representation must compete against simple alternatives.

For relevant experiments:

```text
B0 raw + filesystem/text search
B1 raw + lexical retrieval
B2 raw + vector retrieval
B3 raw + large-context retrieval
B4 minimal compiled topic wiki
B5 layered compiled wiki + raw fallback
```

Graph/hierarchical/agentic variants are added only when a query class provides a plausible reason.

A complex wiki that cannot beat a simpler baseline on our workload is not justified merely because its documents look organized.

---

## 7. Experiment gates before product architecture

### Gate G1 — Trustworthiness

Before we decide page templates or UX, demonstrate that derived state can survive repeated updates without unacceptable fabrication, omission, or regression.

Required experiments:

- E007 long-horizon contamination,
- Issue #3 compilation-loss/repair,
- Issue #7 transition verification.

**Pass condition:** no fixed universal threshold yet; establish an empirical frontier and identify mechanisms that materially reduce persistent errors at tolerable cost.

### Gate G2 — Representation value

Determine what derived representation, if any, beats raw/search/long-context baselines across our query classes.

Required:

- E001 representation,
- E006 retrieval escalation,
- representation × retrieval interaction.

### Gate G3 — Maintenance economics

Determine whether capture/consolidation separation and selective maintenance control lifecycle cost without unacceptable staleness.

Required:

- E002,
- Issue #8,
- full lifecycle token/model-call accounting.

### Gate G4 — Change semantics

Demonstrate acceptable behavior under corrections, temporal changes, disagreements, and taxonomy evolution.

Required:

- E003 temporal update,
- E004 provenance/source ownership,
- E005 + Issue #5 schema migration.

### Gate G5 — Human control

Only after semantic reliability is credible, determine the best IDE/automation boundary.

Required:

- E009 risk-tier review,
- E010 VS Code/Copilot workflow,
- `docs/05-future-research-automation-boundary.md`.

---

## 8. First experimental sequence

Recommended order:

### Stage 1 — Trust Gate

1. Build Controlled Corpus C v0.
2. Pre-register E007 protocol.
3. Compare naive recursive compilation against source-grounded and verified variants.
4. Inject controlled errors and observe propagation/repair radius.
5. Add compilation-loss probes and transition checks.

### Stage 2 — Representation/Retrieval Gate

Use the same corpus/questions to compare raw/search baselines vs compiled representations.

### Stage 3 — Temporal/Maintenance Gate

Introduce waves of changing evidence and measure selective/staged maintenance.

### Stage 4 — Realistic Corpus R

Only after the synthetic harness works, incorporate a user-realistic heterogeneous corpus to detect workflow/friction failures that controlled data misses.

This is the point where user input will become particularly valuable.

---

## 9. What the first controlled corpus must contain

Corpus C v0 should be intentionally adversarial rather than realistic prose only.

Minimum categories:

- exact numbers and dates,
- easy-to-confuse entities/aliases,
- repeated facts across sources,
- facts present only in one source,
- changing facts with known validity sequence,
- correction of previously wrong information,
- unresolved disagreement,
- derived inference that is plausible but unsupported,
- related-but-distinct concepts,
- irrelevant distractors,
- information needed only by a later question,
- source ownership traps,
- structural rename/split cases.

The ground truth should make omission, contamination, attribution, and temporal correctness mechanically scorable where possible.

---

## 10. Metrics hierarchy

### Tier 1 — deterministic integrity

- broken/invalid references,
- source existence,
- exact fact preservation,
- source ownership where encoded,
- duplicate identities,
- allowed lifecycle transitions.

### Tier 2 — semantic integrity

- unsupported claim rate,
- important omission rate,
- preservation failure,
- contradiction classification,
- temporal correctness.

### Tier 3 — behavioral utility

- local/exact QA,
- global/sensemaking QA,
- multi-hop QA,
- historical QA,
- provenance QA,
- regression of previously passing questions.

### Tier 4 — economics

- tokens/model calls per source wave,
- tokens/model calls per query class,
- reconsolidation count,
- human approvals/reviews,
- repair effort after injected errors,
- total lifecycle cost.

No single accuracy number should decide the architecture.

---

## 11. Human role during experiments

To avoid smuggling human intelligence into one condition more than another:

- predefine when human review is allowed,
- record every intervention,
- preserve rejected and accepted diffs,
- never manually repair one variant without accounting for that cost,
- keep model/prompt versions with run artifacts,
- separate researcher interpretation from measured outputs.

---

## 12. Phase 1 exit decision

The evidence landscape is now sufficient to proceed to controlled experiments.

We are **not** declaring an LLM Wiki architecture ready.

We are declaring that:

1. the main risk dimensions are explicit,
2. meaningful competing strategies are identified,
3. simple baselines are defined,
4. the first experiments can be pre-registered without choosing a favored architecture.

The next project phase is therefore **experimental architecture discovery**, beginning with the Trust Gate.
