# E013 realistic workload calibration — preregistration v0

Status: **measurement semantics fixed before collecting E013 dogfood workload data**

## Purpose

E011/E012 support only a selective hypothesis: query-independent durable compilation may have lifecycle value for sufficiently reused knowledge, while exact/provenance answering remains safer with raw evidence available.

E013 asks whether that favorable region occurs in realistic dogfood use before any compiled provider is enabled as a default product path.

## Primary questions

1. What is the empirical distribution of topic revisits per authoritative maintenance cycle?
2. What fraction of completed topic cycles reach the E012 token break-even region of at least 3 revisits per update/cycle?
3. What is the query-class mix: exact/provenance, synthesis, decision/history, or other/unknown?
4. How often does a user follow an answer/query by opening raw evidence?
5. Is there a meaningful high-reuse synthesis/decision region that justifies keeping durable compilation as more than a research curiosity?

## Data boundary

Dogfood telemetry is **local only**. Raw event files may contain local opaque topic IDs, timestamps, operation names, and user-selected query classes, but must never contain:

- raw document text;
- raw query text;
- answer text;
- filenames or absolute paths;
- source IDs or content hashes in telemetry events;
- usernames, hostnames, environment metadata, or credentials.

Human-readable topic labels may exist only in a separate local topic registry and are never included in sanitized exports.

No company data is placed in the public repository or GitHub remote lab. Sanitized aggregate export is explicit and must contain no topic IDs, labels, raw timestamps, queries, paths, source IDs, or document content.

## Topic identity

The user explicitly creates or selects a local topic. A topic receives an opaque random local ID. The human-readable label remains only in the local registry.

E013 does not infer topics with an LLM or embedding model. Un-tagged activity is excluded from primary topic-level calibration rather than guessed.

## Maintenance cycles

For a topic:

- the first topic-associated ingest starts the baseline maintenance cycle;
- subsequent ordinary ingests do not automatically create a new maintenance cycle;
- only an ingest explicitly marked `authoritative_update=true` starts a new maintenance cycle;
- the previous cycle closes at the authoritative-update timestamp;
- the final open cycle at export time is right-censored and is excluded from the primary completed-cycle revisit distribution, but its count is reported separately.

This explicit update marker is intentionally conservative. E013 does not infer semantic updates from changed bytes.

## Revisit / visit sessionization

A **topic visit** represents one consultation episode, not one CLI command.

For query-like operations (`search`, `context`, `ask`) on the same topic:

- the first query-like event starts a visit;
- later query-like events within 30 minutes of the previous query-like event remain in the same visit;
- a gap strictly greater than 30 minutes starts a new visit;
- an authoritative-update boundary always starts a new maintenance cycle and therefore cannot merge visits across the boundary.

Thus `search -> context -> ask` in one short interaction counts as one revisit, preventing command-level inflation of E012's N=3 threshold.

Sessionization threshold: **30 minutes**, frozen before E013 workload observation.

## Query classes

Optional explicit user tag on each query-like command:

- `exact_provenance`
- `synthesis`
- `decision_history`
- `other`
- omitted/unknown

No model-based automatic query classification is used in v0. Primary reports include both classified fractions and the unclassified fraction so missing labels cannot silently distort the class mix.

## Provenance follow

A raw-source open performed through the dogfood CLI is a provenance-follow event. A visit is counted as provenance-followed when at least one source-open event for the same topic occurs during the visit window or within 30 minutes after its last query-like event and before another topic visit begins.

Direct filesystem/editor opens outside the CLI are unobserved. Therefore the measured provenance-follow rate is a lower bound on all source consultation.

## Primary outputs

Sanitized aggregate export reports only:

- number of local topics with tagged activity;
- number of completed maintenance cycles and right-censored active cycles;
- completed-cycle revisit count distribution: min, median, quartiles, max;
- fraction of completed cycles with revisits >= 3, >= 6, >= 10, >= 20;
- total sessionized visits;
- query-event counts/fractions by explicit query class plus unknown;
- provenance-follow visit rate overall and by query class where class attribution is unambiguous;
- optional explicit helpful/not-helpful feedback counts if collected;
- data sufficiency warnings.

The export must not emit per-topic rows or stable identifiers.

## Sample-size / evidence rule

E013 is observational workload calibration, not a randomized architecture benchmark. Do not make a go/default decision from only a few cycles.

Before treating revisit/update distribution as decision-grade, require at minimum:

- at least 10 topics with tagged query activity;
- at least 20 completed maintenance cycles total;
- at least 30 sessionized topic visits;
- report the number of topics contributing completed cycles and concentration of cycles/visits.

Until those minima are met, the result is `INSUFFICIENT_CALIBRATION_DATA` regardless of point estimates.

These minima are pragmatic anti-overinterpretation thresholds, not a power calculation for a small effect.

## Decision boundary

- If fewer than half of completed cycles reach 3 revisits and no clear high-reuse synthesis/decision subgroup emerges, keep raw/retrieval as the default and do not add maintenance complexity.
- If exact/provenance queries dominate or provenance-follow is high, keep raw-backed answering as the default for that region.
- Only if a meaningful high-reuse synthesis/decision region is observed should a durable compiled provider advance from disabled to shadow/opt-in testing.
- E013 cannot by itself authorize autonomous canonical mutation, verifier stacks, graph databases, or incremental consolidation.

## Model/cost policy

Workload logging, sessionization, aggregation, and export use **zero model calls**. Luna calls made by an explicitly authorized dogfood `ask` command are product-use observations, not required E013 measurement calls. Query classification remains user-tagged/deterministic in v0.

## Evidence grade

Even after sample minima are met, E013 is realistic dogfood workload calibration from a limited user/workflow population. It improves ecological validity over synthetic benchmarks but does not establish organization-wide or cross-user generality.
