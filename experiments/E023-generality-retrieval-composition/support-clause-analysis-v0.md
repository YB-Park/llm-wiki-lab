# E023 posthoc support-clause analysis v0

Status: **EXPLORATORY / ZERO MODEL CALLS / DOES NOT CHANGE FROZEN VERDICTS**

G1b exposed an evaluation problem: the preregistered flat `required_sources` list treated every listed source as equally necessary, but several correct answers legitimately used a smaller authoritative basis.

This posthoc analysis asks a narrower question:

> Can a logical representation of **load-bearing authority requirements** explain the already-frozen semantic outcomes better than flat all-source recall?

It uses no model calls and does not alter G1a/G1b promotion decisions.

## Evaluation-only hypothesis

`support-clauses-hypothesis-v0.json` distinguishes:

- **load-bearing clauses** — authority required to support a specific proposition;
- **alternative support** — one of several admitted sources can establish the same needed proposition;
- **minimum repeated support** — e.g. two independent records to justify “repeatedly”;
- **corroborating optional sources** — useful but not necessary when another source establishes the proposition;
- **forbidden conflation sources** — distractors that must not be merged into the target subject.

This is **not** a product KnowledgeUnit/claim-graph schema. It is an evaluation representation only.

## Zero-model result

`analyze_support_clauses.py` evaluates frozen selected contexts:

| context | flat required-source complete | load-bearing support clauses complete |
|---|---:|---:|
| G1a A top-5 | 6 / 10 | **9 / 10** |
| G1a C top-5 | 6 / 10 | **9 / 10** |
| G1b four target finals | 1 / 4 recovered prior missing source | **4 / 4 support-complete** |

The unique support-incomplete G1a question under this hypothesis is **Q001** — exactly the question that produced the frozen CRITICAL_ERROR.

G1b makes Q001 support-complete by retrieving/selecting S004 and the semantic verdict becomes PASS.

## Why this matters

### Q001 — genuinely load-bearing missing authority

The answer needed two things:

1. explicit identity bridge `J.H. Park == Park Jihoon / Jihoon Park` — S004;
2. at least two admitted records establishing repeated DPA concern — any two of S001/S002/S003.

G1a lacked S004 and overclaimed identity. G1b recovered S004 and repaired the critical failure.

This is a real retrieval/authority failure.

### Q002 — S003 is corroborating, not uniquely required

The actual support clauses are:

- direct authorship — S002;
- meeting attribution — either S001 or S003;
- cross-alias identity bridge — S004.

G1b selected S002/S001/S004 and answered correctly. Penalizing it because S003 was absent mistakes redundant corroboration for missing authority.

### Q004 — S008 is corroborating when S009 is present

S009 directly records both the decision and operational-complexity rationale. S010 records the later unrealistic burst and non-reversal.

S008 strengthens the Operations rationale but is not required once S009 is in context.

### Q008 — support complete, answer still partial

Both G1a A and C contexts satisfy the load-bearing support clauses:

- Cobalt backup/replica requirement — S017;
- Northstar standard US-backup behavior and EU-only option — S018.

Yet both answers were PARTIAL because they failed to explicitly complete the implication that selecting the EU-only option could satisfy residency.

This is exactly the desired diagnostic separation:

> **authority was present; composition omitted a required implication.**

## Core consequence

Future generality/retrieval gates should avoid a flat `required_sources` metric as the primary authority criterion.

A better evaluation question is:

> **Did the context contain enough authoritative support to establish every load-bearing proposition in the expected answer?**

That can involve:

- one uniquely required source;
- one-of alternatives;
- a minimum count for repeated observations;
- explicit negative evidence;
- a required identity/attribution bridge.

This does **not** mean the product should persist proposition nodes or a claim graph. The evaluator can use richer structure than the product storage architecture.

## What remains unearned

- G1b product rollout — frozen promotion remains NOT_EARNED.
- G2 persistence.
- universal semantic schema.
- entity/graph storage.
- automatic identity routing.

## Next step

Before any more paid semantic experiment, turn this posthoc evaluator hypothesis into a **prospectively frozen evaluation contract** on a new/held-out mini-corpus or a carefully separated question set. Do not reuse it to rewrite E023's primary verdicts.

The useful research direction is now narrower:

1. evaluate **authority sufficiency**, not source-list completeness;
2. keep retrieval vs composition failure separable;
3. preserve consequence-sensitive identity/attribution requirements;
4. only then decide whether another G1 mechanism comparison is worth model calls.
