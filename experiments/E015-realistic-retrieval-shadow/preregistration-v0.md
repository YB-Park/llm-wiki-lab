# E015 — realistic retrieval shadow calibration

Status: **preregistered before natural shadow collection**

Date: 2026-08-14

## Purpose

E014-R1 established on a fresh synthetic mechanism corpus that `structural_expand_v1` can outperform whole-object BM25 in the stressed target region while avoiding an overlapping-window index. Production core equivalence is now proven, but that does not establish that the mechanism matters often in natural use.

E015 measures **how often the existing default W0 and candidate X1 actually diverge during natural topic-scoped dogfood use**.

E015 is not a quality proof. The user continues to see W0 only, so shadow disagreement cannot tell us which mode is correct.

## Conditions

- **W0 / default:** `whole_object_v0`.
- **X1 / shadow:** `structural_expand_v1`.
- Both run against the same topic/current-history projection and top-k request.
- W0 alone remains user-visible and alone feeds existing `search`, `context`, and `ask` output.
- X1 may not cause an additional model call or alter canonical state.

## Experimental unit and dependence

Primary exposure unit: a **30-minute-inactivity topic visit**, aligned with E013.

Individual query commands within the same visit are dependent. Event-level disagreement rates are descriptive; visit count is required in the data-readiness floor so repeated command ceremony cannot masquerade as independent workload.

## Per-query shadow record

For a topic-scoped `search`, `context`, or `ask`, local telemetry may store only:

- event type;
- opaque local topic ID (removed by sanitized export);
- operation;
- optional existing explicit query class;
- timestamp (removed by sanitized export);
- default result count;
- candidate result count;
- top-1 same/different;
- ordered top-k same/different;
- top-k object-overlap count;
- default-only object count;
- candidate-only object count;
- default rendered/snippet context characters;
- candidate rendered/snippet context characters.

### Failure containment

E015 is **fail-open with respect to the user-visible W0 path**.

If X1 comparison or shadow telemetry recording fails:

- the existing W0 search/context/Ask path continues unchanged;
- no exception text, query, ID, path, content, or stack trace is appended to telemetry;
- a separate `shadow_failure` event may record only opaque topic ID, operation, timestamp, and optional query class;
- sanitized export may report only aggregate failure counts.

A shadow failure must never trigger fallback to another retrieval/model mode and must never cause an additional model call.

### Forbidden telemetry

Shadow events must never contain:

- raw query text or a query hash/fingerprint;
- source IDs;
- object IDs;
- origin IDs;
- filenames, paths, usernames;
- SHA/content hashes;
- retrieved text/snippets;
- answer/model output;
- exception text/stack traces;
- embeddings or semantic representations.

The comparison may use object IDs transiently in process memory, but only aggregate comparison features may be appended.

## Sanitized aggregate

The existing E013 sanitized export may add an `retrieval_shadow` section containing only aggregate counts/rates. It must contain no topic IDs, timestamps, or forbidden telemetry fields.

Primary descriptive quantities:

1. successful shadow query events;
2. aggregate shadow-failure count;
3. topics with successful shadow activity;
4. 30-minute visits containing successful shadow activity;
5. ordered-result divergence rate;
6. top-1 divergence rate;
7. candidate-addition rate (`candidate_only_count > 0`);
8. default-only rate;
9. mean/aggregate top-k overlap fraction;
10. total candidate/default context-character ratio;
11. the same divergence counts by explicit query class, with `unknown` retained as a first-class bucket.

## Data-readiness floor

`SHADOW_CALIBRATION_READY` requires all:

- >= 50 **successful** shadow query events;
- >= 10 topics with successful shadow activity;
- >= 30 topic visits containing successful shadow activity.

Before then: `INSUFFICIENT_SHADOW_DATA`.

These are calibration minima, not statistical power claims. Failure events do not count toward readiness.

## Interpretation rules

E015 by itself **cannot promote X1 to default** regardless of observed disagreement rate.

Allowed conclusions after readiness:

- if divergence is rare, the synthetic E014 target mechanism may be uncommon in this user's natural workload;
- if divergence is common, realistic evaluation of divergent cases is worth the next evidence step;
- class-specific patterns may define a future routing hypothesis, but no routing rule may be adopted from E015 alone.

Forbidden conclusions:

- X1 is more accurate because it differs;
- W0 is safer because it is current default;
- more candidate-only objects are inherently better;
- a low disagreement rate proves equivalence;
- any default promotion without additional realistic quality evidence.

## Cost and model boundary

- deterministic local retrieval only;
- zero additional model calls;
- zero additional AI credits;
- no network requirement;
- no VS Code feature/UI work.

## Stop / pivot

Once the readiness floor is met, freeze the first sanitized E015 snapshot before designing any divergent-case evaluation. Do not change the shadow feature schema in response to desired rates without versioning a new protocol.

While E015 accumulates naturally, core research proceeds independently on temporal semantics.
