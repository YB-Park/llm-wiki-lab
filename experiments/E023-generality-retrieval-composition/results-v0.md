# E023 G1 result v0 — retrieval planning / ephemeral composition

Status: **G1-C NOT EARNED / IMPORTANT FAILURE EVIDENCE**  
Run: `32215941344`  
Frozen execution source: `7315b858ed5ce764fa81ed131ee17f77c1ea11ae`  
Model: exact `gpt-5.6-luna`  
Semantic model-call attempts: **30 / 30**  
Semantic rerolls: **0**

The run completed successfully and its artifact was captured immutably under `evidence/run-32215941344/`. The captured `result.json` SHA-256 is:

`e578feb61454f124fce2294bf1a8e6ce396de213984cd889f760343f788c779a`

## Frozen comparison

### A — simple baseline

Exact frozen user question → production-shaped BM25 → top 5 source objects → one Luna composer.

Cost: **10 model calls**.

### C — blind planned query expansion

One Luna planner sees only the question → 1–3 additional queries → original + planned-query BM25 → deterministic RRF(k=60) → the **same top-5 source-object budget** → same Luna composer.

Cost: **20 model calls**: 10 planner + 10 composer.

No source notes, persistent semantic state, entity store, graph, vector retrieval, or identity database was used by either arm.

## Primary result

| Q | A recall@5 | C recall@5 | A semantic | C semantic | C improvement |
|---|---:|---:|---|---|---|
| Q001 identity / repeated DPA | 0.75 | 0.75 | **CRITICAL_ERROR** | **CRITICAL_ERROR** | no |
| Q002 direct vs attributed | 0.75 | 0.75 | PASS | PASS | no |
| Q003 role change / reversal | 1.00 | 1.00 | PASS | PASS | no |
| Q004 Redis rationale / later test | 0.75 | 0.75 | PASS | PASS | no |
| Q005 incident root cause | 1.00 | 1.00 | PASS | PASS | no |
| Q006 incident timeline / addendum | 1.00 | 1.00 | PASS | PASS | no |
| Q007 recurring EU constraint | 1.00 | 1.00 | PASS | PASS | no |
| Q008 standard DR compliance | 1.00 | 1.00 | PARTIAL | PARTIAL | no |
| Q009 Redis reopening evidence | 1.00 | 1.00 | PASS | PASS | no |
| Q010 unsupported characterization | 0.75 | 0.75 | PASS | PASS | no |

Manual adjudication totals:

- A: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**
- C: **8 PASS / 1 PARTIAL / 1 CRITICAL_ERROR**
- C question-level improvements over A: **0**
- C regressions: **0**
- C new critical errors relative to A: **0**

The preregistered promotion rule required at least **2 net question-level improvements** and no new critical errors. C therefore does **not** earn promotion.

## The most important failure: Q001

Q001 asked:

> Who was the ABC person who repeatedly raised the DPA concern?

The authoritative alias/identity bridge was S004, the directory record that explicitly connected:

- Park Jihoon;
- Jihoon Park;
- J.H. Park;
- the stable ABC contact identifier / email;
- the Privacy Counsel role.

### A

A selected:

`S001, S005, S003, S006, S002`

S004 was absent. The same-surname distractor S005 was present.

Nevertheless the composer asserted that the person was Jihoon Park and said the direct email S002 “confirms his identity.” S002 identifies its own author as Jihoon Park, but it does **not** establish that meeting-record `J.H. Park` is the same person.

### C

C selected:

`S001, S005, S003, S002, S006`

Again S004 was absent and S005 was present. C made the same unsupported identity merge.

This is adjudicated as **CRITICAL_ERROR — retrieval-rooted epistemic upgrade** in both arms.

The fact that the inferred merge matches the frozen gold identity does not rescue the answer. A trustworthy Wiki must distinguish:

> “the answer happened to be true”

from:

> “the supplied authoritative evidence established the answer.”

This is exactly the semantic-laundering / false-merge risk that motivated the Generality Gate.

## Q008 partial result

Both arms correctly said Northstar's standard disaster-recovery configuration fails Cobalt's EU-only requirement because the standard configuration may put encrypted backups in the United States.

Both stopped short of fully stating the frozen third requirement: **the available EU-only disaster-recovery option could satisfy the residency requirement if selected**. C mentioned that the EU-only option is not the default, but did not complete the compliance implication.

This is a bounded composition omission, not a persistence failure.

## What planner/RRF actually did

The planner calls were contract-valid, but the planned retrieval did not close any of the four preflight gaps:

- Q001: S004 remained outside final top 5;
- Q002: S003 remained outside final top 5;
- Q004: S008 remained outside final top 5;
- Q010: S003 remained outside final top 5.

There is useful diagnostic detail inside the failure.

For Q001, S004 had per-query ranks `[7, 3, 7, 8]`: one alias/identity-oriented planned query did surface the identity bridge at rank 3, but consensus-style RRF placed it at fused rank 6.

For Q004, S008 had per-query ranks `[8, 7, 5, 6]`: one query moved the Operations rationale to rank 5, but fused rank remained 6.

For Q002 and Q010 the missing meeting evidence stayed weak across the planned queries.

Therefore the result should **not** be summarized as “LLM planning cannot help retrieval.” The tested mechanism was narrower:

> **blind one-shot query expansion + consensus RRF + fixed top-5 did not outperform exact-query top-5 on this corpus.**

## Cost / usage

Exact locally known usage:

- A: 10 model calls;
- C: 20 model calls;
- total: **30 model calls**.

Machine-readable token totals were not captured by this runner, so token usage is **unknown**.

AI credits / premium requests are also **unknown** and must not be inferred from calls or tokens.

C therefore used twice as many model calls as A without a semantic improvement in the frozen evaluation.

## Architecture consequence

### What E023 G1 does earn

1. The simple raw-evidence baseline is stronger than an architecture-first intuition might suggest: 8/10 questions passed despite heterogeneous cross-source stress.
2. A high-capability model can still make a dangerous **unsupported identity merge** when retrieval omits the explicit bridge. Strong reasoning does not remove the authority problem.
3. Blind pre-retrieval query planning is not enough here. The planner sometimes created useful signal, but the fixed RRF selection policy did not turn that signal into better final context.
4. Query-time semantic work remains a viable architecture family; the tested C implementation simply did not earn default use.

### What it does NOT earn

This result does **not** authorize:

- G2 persistent dossiers;
- a permanent Entity/Relation/KnowledgeUnit layer;
- automatic alias/entity merge/split;
- graph storage;
- vector retrieval as a new default;
- automatic source-note expansion;
- persistence as a fix for Q001.

Q001 first demands a better retrieval/epistemic answer to an identity consequence, not a permanent entity object.

## Next core hypothesis — stay inside G1

The next candidate should remain **G1 Retrieval / Composition**, not move to persistence.

The motivating comparison is now:

### G1a — already tested and not earned

Question-only planner → several blind query rewrites → consensus RRF → composer.

### G1b — candidate, must be separately preregistered

**Iterative evidence-follow retrieval**:

1. retrieve the first raw candidates;
2. expose only bounded metadata/snippets to a follow-up planner;
3. let the planner identify what is missing or ambiguous from the observed candidates;
4. issue targeted follow-up retrieval;
5. compose from the same bounded final evidence budget;
6. when a high-consequence identity/attribution relation lacks an explicit authoritative bridge, require uncertainty rather than confident merge.

This is much closer to how a capable coding Agent actually works: search → inspect → notice a gap → search again, rather than generate three blind keyword variants before seeing any evidence.

Before spending another semantic call, use the frozen G1 artifact for zero-model counterfactual analysis of selection/fusion and preregister any G1b protocol separately.

## Product consequence

Dogfood 0.1.16 remains unchanged.

Do not add a semantic store to the product from this result. Continue natural installed use in parallel. `source-note-v0` remains one source-oriented DERIVED projection under test, not the ontology of LLM Wiki.

The core architectural direction remains:

> **Authority Core + task-appropriate semantic projections + strong raw fallback; persistence must earn itself after a strong ephemeral retrieval/composition path exists.**
