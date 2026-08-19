# E023 authority-sufficiency evaluation preregistration v0

Status before any new semantic generation: **PROSPECTIVELY FROZEN EVALUATION CONTRACT / ZERO MODEL CALLS / NO PAID RUN AUTHORIZED**.

G1a and G1b are complete and both remain `NOT_EARNED` under their frozen promotion rules. G1b nevertheless produced a targeted trust repair on Q001 by recovering the explicit identity bridge that G1a lacked. The posthoc support-clause analysis then exposed a measurement defect: flat `required_sources` conflated uniquely load-bearing authority with redundant corroboration.

This preregistration addresses that measurement defect only. It does **not** introduce a new retrieval mechanism, persistent semantic state, product schema, or model-call authorization.

## 1. Frozen causal question

Before another retrieval/composition mechanism is tuned or executed:

> **Can we prospectively determine whether a selected context contains enough typed terminal authority to establish every load-bearing proposition, without confusing redundant corroboration, missing authority, or a dangerous conflation distractor?**

The evaluator must answer this independently of whether a later composer actually writes a correct answer.

## 2. Why this is prospective rather than another posthoc rewrite

The original E023 G1/G1b corpus and outcomes are already observed. They remain immutable evidence and their promotion verdicts are not changed.

This v0 package uses a new, clearly separated synthetic slice:

- 15 new authoritative anchors with IDs `A001`–`A015`;
- 6 new questions with IDs `AQ001`–`AQ006`;
- four families: identity/attribution, decision rationale, incident temporal correction, and vendor constraint;
- no anchor ID or exact anchor text overlaps the frozen G1 corpus;
- no model answer, semantic verdict, or adjudication exists for these questions at freeze time.

This material is **separated**, not claimed to be secret or permanently hidden. If a future retrieval mechanism is tuned against these exact fixtures, that future mechanism must not call them an untouched holdout. A later execution addendum may require an additional late-frozen slice if clean holdout semantics are needed.

## 3. Terminal authority is typed

Every load-bearing clause resolves only to terminal authority types already allowed by the product philosophy:

- `RAW_MEMORY`;
- `HUMAN_KNOWLEDGE`.

`DERIVED_MEMORY` is intentionally absent as terminal authority.

`AQ003` deliberately requires explicit `HUMAN_KNOWLEDGE` for the first-release no-Kafka decision and rationale. This prevents the evaluator from quietly treating an external benchmark or model synthesis as authority for a user-owned epistemic commitment.

## 4. Evaluation representation

The contract is evaluation-only and lives in `authority-sufficiency-v0/contract.json`.

It supports three deterministic positive-support clause types:

- `all_of` — every listed authoritative anchor is required;
- `any_of` — at least one listed authoritative anchor is sufficient;
- `min_count` — at least N listed authoritative anchors are required, for propositions such as “repeatedly”.

Each clause also records a semantic role so the frozen slice exercises the failure classes that motivated this work, including:

- uniquely load-bearing support;
- alternative support;
- repeated-support minima;
- identity bridges;
- direct-vs-meeting attribution;
- explicit negative evidence;
- temporal correction;
- user-owned Human Knowledge.

This structure is **not a product claim graph, KnowledgeUnit schema, or storage ontology**. The evaluator is allowed to be more structured than the Wiki runtime.

## 5. Forbidden conflation is not the same thing as missing authority

A context can contain enough positive authority while also containing a dangerous distractor.

Therefore v0 does not collapse those conditions into one boolean. It emits one of:

- `INSUFFICIENT_AUTHORITY` — at least one load-bearing clause is not satisfied;
- `SUFFICIENT_CLEAN` — all load-bearing clauses are satisfied and no frozen conflation distractor is present;
- `SUFFICIENT_WITH_CONFLATION_RISK` — all load-bearing clauses are satisfied, but a frozen wrong-subject/distractor anchor is also present.

This distinction is deliberate.

If a later composer receives `SUFFICIENT_WITH_CONFLATION_RISK` and nevertheless attributes the distractor to the target, that is not a retrieval-sufficiency failure. It is a composition/trust failure under a risky context.

Likewise, a `SUFFICIENT_CLEAN` context followed by an omitted implication or unsupported semantic upgrade is a composition failure, not evidence that persistence is required.

## 6. Frozen separated slice

### AQ001 — repeated identity-linked requirement

Tests:

- explicit `M. Chen -> Maya Chen` identity bridge;
- minimum two-source support for “repeatedly”;
- forbidden conflation with `Mira Chen`.

### AQ002 — direct authorship vs meeting attribution

Tests:

- direct-authored wording from a direct email;
- one-of alternative meeting records for attribution;
- explicit identity bridge;
- same-name distractor risk.

### AQ003 — user-owned decision authority

Tests:

- `HUMAN_KNOWLEDGE` as the load-bearing terminal authority for a decision/rationale;
- later RAW performance evidence that does not itself reverse the decision;
- optional corroborating RAW baseline that must not become mandatory.

### AQ004 — hypothesis correction and negative evidence

Tests:

- early unconfirmed hypothesis;
- intermediate causal signal;
- final root cause;
- explicit negative evidence rejecting the initial hypothesis.

### AQ005 — temporal correction

Tests:

- alternative authoritative anchors for the corrected start time;
- intermediate event;
- final root cause;
- addendum scope showing what changed and what did not.

### AQ006 — vendor constraint and composition implication

Tests:

- uniquely authoritative customer residency rule;
- explicit negative evidence that encryption does not waive geography;
- vendor standard configuration and non-default compliant option;
- optional procurement uncertainty as corroboration rather than load-bearing authority.

## 7. Zero-model evaluator verification

`validate_authority_sufficiency.py` must make **zero model calls** and fail closed on contract drift.

It validates:

1. anchor/question IDs and frozen hashes;
2. no exact text overlap with the original E023 G1 corpus;
3. terminal authority types;
4. clause schema and `all_of` / `any_of` / `min_count` semantics;
5. positive, optional, and forbidden anchor disjointness;
6. required semantic-role coverage;
7. presence of a load-bearing `HUMAN_KNOWLEDGE` case;
8. deterministic reference contexts for all three context statuses;
9. at least one clean and one insufficient reference context for every question;
10. a conflation-risk reference context for every question that declares a frozen distractor;
11. minimal sufficient positive contexts, including proof that optional corroboration is not secretly required;
12. absence of model answers, observed semantic verdicts, or adjudication in the prospective contract.

The current frozen reference suite contains 14 deterministic contexts and is itself hashed in the manifest.

## 8. Freeze discipline after merge

Once this contract is merged to `main`:

- do not edit v0 clauses after seeing a model answer merely to improve agreement;
- do not reinterpret a failed future semantic run by changing v0 in place;
- any genuine contract defect must be corrected in a new version with the reason recorded;
- any future semantic execution must pin the exact contract commit;
- G1a/G1b frozen verdicts remain unchanged.

## 9. What this enables next

After the zero-model contract is reviewed and merged, the next decision is:

> **Does another G1 retrieval/selection/composition mechanism comparison deserve semantic calls now that authority sufficiency can be measured prospectively?**

That decision is separate from this PR.

A future mechanism comparison needs its own preregistration/execution addendum, frozen call budget, prompts, evidence budget, and promotion rule before the first semantic call.

## 10. Explicit non-authorization

This preregistration does **not** authorize:

- a G1c paid run;
- a G2 persistent semantic dossier;
- Entity/Relation/KnowledgeUnit storage;
- graph infrastructure;
- vector-default changes;
- automatic identity merge/split;
- automatic subject routing;
- derived state becoming terminal authority;
- any Dogfood 0.1.16 runtime change.

The project remains on the same north star:

> **Human controls admission and epistemic commitment. LLM controls routine retrieval, compilation, and maintenance only inside granted authority.**

The purpose of this evaluator is to make that authority boundary measurable before more semantic optimization.
