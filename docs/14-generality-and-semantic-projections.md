# Generality and semantic projections — working design gate

Status: **WORKING DESIGN GATE / NOT AN ADR / NOT A STORAGE DECISION**  
Date: 2026-08-20 KST  
Tracking: Issue #160  
Experiment: E023

## Design target

LLM Wiki must not define “Wiki” as developer-shaped source summaries merely because that was the smallest useful Agent Wiki slice. But “generality” must not become an excuse to install a universal Entity/Relation/KnowledgeUnit schema, graph database, vector default, or automatic identity machinery before the workload earns it.

> **Capability generality before storage uniformity.**

Working thesis:

> **LLM Wiki is a trustworthy Authority Core plus task-appropriate semantic projections. The Agent should reconstruct and use the right semantic view at the moment of need; every useful view does not need to exist as permanent semantic state.**

## Authority Core and projection boundary

The durable Authority Core remains semantic-ontology agnostic. It owns admitted evidence identity/integrity/provenance, current/history and explicit correction/change/dispute semantics, Human Knowledge authorship, privacy/permission boundaries, and deterministic repairable storage invariants.

Semantic projections may be source notes, ephemeral cross-source dossiers, timelines, project summaries, decision histories, or later persistent views **if persistence earns itself**.

Common projection safety properties matter more than one common schema:

- DERIVED;
- NONCANONICAL;
- authority-anchor resolvable;
- inspectable;
- reversible/rebuildable;
- unable to silently impersonate RAW evidence or Human Knowledge.

## Authoritative-anchor invariant

> **Every load-bearing derived claim must resolve to an authoritative anchor whose epistemic type remains explicit.**

Terminal authority may be admitted `RAW_MEMORY` or explicit `HUMAN_KNOWLEDGE`. Persistence never makes DERIVED state terminal authority by itself.

E023 now sharpens this into an end-to-end requirement:

> **Retrieval must expose sufficient authority; evidence budgeting must preserve it; composition must state only what that authority permits and preserve its epistemic type.**

## Ordered architecture gates

1. **G1 Retrieval / Composition** — can authority be found, budgeted, preserved, and faithfully composed at query time?
2. **G2 Persistence** — only after a strong G1 path exists, hold retrieval/composition strong and test repeated-use benefit after lifecycle cost.
3. **G3 Identity / Routing** — only if persistent semantic targets earn value, test automatic discovery/routing/merge-split.

A G1 failure is not evidence for G2. A G2 success is not evidence for G3.

## E023 findings that remain architectural

### Truth-by-luck is a trust failure

G1a first showed that a correct-looking alias merge is unsafe when the explicit identity bridge is absent. Later E023 slices reproduced the same class for identity and governing policy/compliance.

Strong identifiers and similarity are evidence, not automatic identity truth. Missing governing policy cannot be replaced by a plausible compliance inference.

> **Truth-by-luck is not trustworthy semantic recovery.**

None of these failures implies a persistent identity graph is required. They first require sufficient query-time authority and disciplined composition.

### Planner/selector complexity has not earned itself

- G1a blind planner/RRF: NOT_EARNED.
- G1b evidence-follow: broad NOT_EARNED, but targeted identity-bridge repair signal.
- G1c-R1: candidate pools became authority-sufficient on 6/6, then a free-form model selector destructively dropped load-bearing evidence; NOT_EARNED.
- G1d: replacing the model selector with deterministic RRF top-4 did not generalize; lexical consensus amplified same-name/product/capability distractors and missed governing policy; NOT_EARNED.

Determinism is not authority awareness, and planner diagnosis does not guarantee retrieval of the authoritative object.

## G1e — prospective simple evidence-budget replication

G1d's zero-model frontier found consequential authority immediately outside fixed top-5. G1e tested that signal prospectively on a new 35-anchor / 8-question slice.

### Phase 0 — authority sufficiency, zero model

PR #187:

| arm | clean | risk | insufficient |
| --- | ---: | ---: | ---: |
| A5 exact BM25 top-5 | 2 | 4 | 2 |
| B6 same ranking top-6 | 3 | 5 | **0** |

B6 authority improvements: **2**; regressions: **0**.

Rank-6 evidence repaired:

- an explicit R. Singh/Rina Singh identity bridge;
- the second independent monthly-close observation required to establish recurrence.

### Phase 1 — semantic safety/value

Run `32324460519`, source `505740b74776fc7b7988e9c168c9c9d0ed2067fa`, exact `gpt-5.6-luna`, 16/16 composer calls, planner 0, selector 0, zero rerolls.

Semantic result:

- A5: **5 PASS / 1 PARTIAL / 1 FAIL_RETRIEVAL / 1 CRITICAL_ERROR**;
- B6: **6 PASS / 2 PARTIAL / 0 FAIL / 0 CRITICAL_ERROR**;
- B6 improvements: **2**;
- B6 regressions: **0**;
- B6 new critical errors: **0**.

Strict promotion required >=7/8 B6 PASS, so G1e remains **NOT_EARNED**.

The important positive signal is still prospective:

- CQ001 A5 made an unsupported identity merge; B6 added the explicit bridge and moved `CRITICAL_ERROR -> PASS`;
- CQ008 A5 safely lacked enough independent evidence to establish “repeated”; B6 added the second observation and repaired the authority deficiency;
- the extra sixth object caused **no semantic regression** across the slice;
- no planner/selector calls were required.

This makes exact BM25 with a modestly larger evidence prefix the current **strong simple retrieval baseline**, not a product `k=6` rule.

## Composition is now the leading controlled bottleneck

B6 had **0 authority-incomplete contexts**. The two remaining partials are composition-side and recur across E023:

1. **Overcautious insufficiency calibration** — the answer has enough authority for the proposition actually asked, but declares insufficiency because it silently demands a stronger guarantee.
2. **Epistemic-type omission** — a user-owned decision is available as `HUMAN_KNOWLEDGE`, but the answer presents it as an ordinary project fact rather than preserving that terminal authority type.

This is the key architecture shift:

> **The leading controlled question is no longer simply whether enough evidence can be retrieved. It is whether the Agent expresses exactly what the retrieved authority permits, with the correct epistemic type.**

## What a composition contract may and may not do

A future G1 composition mechanism should remain generic and ontology-agnostic. It may require behaviors such as:

- user-owned decisions/beliefs/rationale remain explicitly user-owned in the answer;
- direct authorship is not collapsed into third-party attribution;
- an absent identity/policy bridge causes uncertainty rather than synthesis-by-similarity;
- insufficiency is scoped to the proposition actually asked, not an unstated stronger proposition;
- corrections/temporal state and explicit negative evidence are preserved;
- load-bearing citations point to terminal authority rather than DERIVED intermediates.

It should **not** import evaluator clauses, Cxxx/AQ/BQ-specific rules, a universal claim graph, or domain-specific ontology into runtime.

User-facing language also need not expose internal labels like `HUMAN_KNOWLEDGE`; preserving epistemic meaning can be natural language such as “we decided…”, “your project decision says…”, or “the source records…”.

## Evidence-budget translation remains open

G1e does not establish six sources as a product default.

The current product's 6,000/12,000 character boundaries are per-source `wikiRead` windows, not global multi-source answer-context budgets. E014's 320 characters are per-hit retrieval snippets. A later product-facing budget should therefore be designed explicitly, likely in character/token terms, after the simple G1 mechanism is semantically sound.

## Evaluation discipline

Keep separate:

- positive authority sufficiency;
- conflation risk;
- rank/candidate cutoff;
- evidence size;
- semantic correctness;
- unsupported claims / epistemic upgrades;
- direct-vs-attributed authorship;
- terminal authority type;
- proposition-scoped insufficiency;
- temporal/correction correctness;
- model calls/cost.

A sufficient context can still be composed badly. A risky context can still yield a correct answer. Do not collapse these into one score.

## Current action

Stay inside **G1 Retrieval / Composition**. Paid calls pause at this checkpoint.

Immediate research question:

> **Can a generic composer contract preserve terminal epistemic type and calibrate insufficiency to the actual load-bearing proposition without exposing storage jargon or importing evaluator/domain schemas into runtime?**

Before another paid run:

1. freeze the composition rules prospectively and generically;
2. validate them with zero-model/adversarial fixtures;
3. use new separated material for any semantic comparison;
4. hold retrieval/evidence budget fixed to the strong simple baseline rather than retuning retrieval simultaneously;
5. measure PASS/critical errors, authority-type preservation, insufficiency calibration, citations, and model calls separately;
6. do not rerun AQxxx/BQxxx/CQxxx semantically;
7. keep Dogfood 0.1.16 unchanged while natural installed use continues.

Do **not** jump to persistent dossiers, graph/entity infrastructure, universal KnowledgeUnit schema, vector defaults, automatic identity/routing, or evaluator clauses as runtime canonical structure.

Any durable semantic architecture still requires its own evidence gate and, if promoted to policy, an ADR.
