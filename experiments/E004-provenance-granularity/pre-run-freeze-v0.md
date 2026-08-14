# E004 — Pre-run freeze v0

Status: **FROZEN BEFORE FIRST HELD-OUT SCORE**

Date: 2026-08-14

Issue: #43  
PR: #44

## 1. Integrity statement

As of this freeze, `analysis_v0.py` has **never been executed on the 24-topic held-out E004 corpus**.

Development before freeze was limited to:

- corpus generation / shape counting / canonical hashing;
- structural and span-reversibility validation of the held-out corpus;
- P3 construction after removing `fault_family` and `gold_outcome` fields;
- a separate hand-written non-held-out fixture for bounded-auditor behavior;
- compile checks and hash discovery.

Model calls: **0**.  
AI credits: **0**.

## 2. Frozen corpus

Generator seed: `20260830`.

Canonical corpus:

- topics: `24`
- claims: `288`
- raw W0 sources/topic: `6`
- derived sections/topic: `3`
- claims/section: `4`
- risk: `144 high / 144 low`
- every fault family: `48` rows total = `24 high + 24 low`

Canonical corpus SHA-256:

`68317ea91cac451ca59012f62506dbd1a249d76191ae9d06cc7777276a74ad80`

## 3. Frozen score-affecting bytes

SHA-256 over exact Git file bytes:

- `generate_corpus.py`  
  `f13b35577028b8fa0aca32e942f1fa140f51584fc7db5392d7ea67c752d7dd1b`
- `provenance_v0.py`  
  `c7922b38404aac4af0469a79a59ee7f506bb23d04e1d2787141425be57684a3a`
- `analysis_v0.py`  
  `56a8b3f95ab9cddff41a35ecb434c2033a92d36ac0e6462ab26207ae84cd1aad`

Frozen validator byte SHA-256:

- `validate_prescore.py`  
  `8ba66358a05d2485f103db9fccc537d2f6162069589617496f08e6be276d8bfa`

The validator is bound to the canonical corpus SHA above.

## 4. Frozen conditions

- `P0`: page/object bibliography; no per-claim ownership. At audit time, deterministic BM25 localization is allowed **only inside cited raw sources**.
- `P1`: section-level structural provenance inherited by claims in that section.
- `P2`: exact per-atom raw source-revision character spans for every claim provenance record.
- `P3`: P1 for all claims plus P2 exact spans only where the fixture's already-frozen `risk=high`. P3 is not allowed to inspect fault family or gold outcome.

Benchmark claim/atom IDs are scorer oracle machinery and do not constitute a product claim-graph decision.

## 5. Frozen audit protocol

Primary source-character budget per claim: **1,200**.

Sensitivity only: `600`, `2,400`.

No condition may search an uncited source during primary audit.

Inspection order:

- P0: BM25-ranked structural units within page-level cited raw sources;
- P1: mapped structural units in deterministic order;
- P2: exact atom spans first, then their containing structural units while budget remains;
- P3: P2 order for high risk, P1 order for low risk.

Overlapping exact/unit inspection is charged only once for source characters actually inspected.

Audit outcomes are frozen as:

- `verified`
- `invalid_or_unsupported`
- `contested`
- `unresolved_budget`

## 6. Frozen fault/risk balance

Every topic contains each family exactly twice, once high risk and once low risk:

- clean
- wrong_value
- wrong_source
- derived_only
- within_source_conflict
- multi_source_misownership

Risk is therefore orthogonal to whether a row is faulty. P3 receives only the risk field for precision selection.

## 7. Frozen W1 / D1 maintenance interpretation

W1 changes exactly 3 of 6 source revisions/topic and includes:

- structure/text shift while support facts remain addressable;
- a synthetic factual control correction;
- a synthetic control conflict addition.

Historical W0 bytes/IDs remain part of the immutable fixture. W1 update actions are an **oracle minimum metadata-edit lower bound**, not performance of an automatic updater.

D1 reverses section order and claim order. Stable benchmark IDs are available only to compute an optimistic minimum reattachment lower bound. They do not prove stable product claim IDs are free.

## 8. Frozen statistics

Primary unit: topic.

Paired topic bootstrap:

- reps: `20,000`
- seed: `20260831`
- all dependent claim rows remain inside their sampled topic cluster.

Claim-level rows/slices are diagnostics, not independent evidence.

## 9. Frozen Gate A — precise capability

All required:

1. P2 − P1 critical bounded-audit accuracy >= `+0.15`
2. topic-bootstrap 95% CI lower bound > `0`
3. P2 − P1 exact source ownership >= `+0.20`
4. ownership CI lower bound > `0`
5. P2 critical inspected chars <= `0.65 × P1`
6. P2 clean false accusation <= P1 + `0.02`
7. P2 conflict detection >= P1 − `0.05`
8. P2 raw exact-span reversibility = `100%`
9. P2 derived-only acceptance = `0%`
10. scoring is read-only with respect to corpus/raw/core state

Fail label: `DOES_NOT_SURVIVE_E004_PRECISE_GATE`.

Pass label: `SURVIVES_E004_PRECISE_GATE`.

## 10. Frozen Gate B — selective precision

Evaluated as an architecture signal only if Gate A passes. All required:

1. P3 high-risk audit accuracy >= P2 − `0.03`
2. P3 high-risk exact ownership >= P2 − `0.03`
3. P3 high-risk conflict detection >= P2 − `0.03`
4. P3 metadata bytes <= `0.75 × P2`
5. P3 W1 update actions <= `0.80 × P2`
6. P3 clean false accusation <= P2 + `0.02`
7. P3 precise-subset exact raw-span reversibility = `100%`
8. P3 derived-only acceptance = `0%`

Pass label: `SELECTIVE_PRECISION_SURVIVES_E004_V0`.

Otherwise: `SELECTIVE_PRECISION_NOT_ESTABLISHED_E004_V0`.

Low-risk P3 performance remains reported and cannot be hidden by Gate B's high-risk comparison.

## 11. Prescore evidence already obtained

Hash-discovery run `31795828504`:

- compile PASS;
- corpus shape/hash PASS;
- structural held-out validation PASS;
- hand-written non-held-out auditor fixture PASS;
- scoring command absent;
- artifact `9217313038` preserved the initial hash manifest.

Final hash-discovery run `31795941307` after binding the validator to the corpus SHA:

- all steps PASS;
- corpus and the three score-affecting file hashes unchanged;
- only validator hash changed as expected;
- scoring command absent;
- model calls / AI credits = 0.

## 12. Post-freeze forbidden changes

Before the first official score, do **not** change:

- corpus seed/shape/text/fault/risk prevalence;
- P0/P1/P2/P3 condition construction;
- audit order or budgets;
- source-ownership definition;
- W1/D1 maintenance accounting;
- bootstrap seed/reps/unit;
- Gate A/B thresholds;
- scorer formulas.

Only non-semantic CI/plumbing repairs may be made before scoring, and any such repair must be documented before the first score. A semantic bug requires a new freeze/fresh corpus rather than silently repairing this benchmark.

After the first official score, v0 is immutable for interpretation. Any semantic correction then requires an explicit post-score amendment or fresh replication depending impact.

## 13. Interpretation ceiling

A Gate A pass authorizes at most a **local exact provenance record / shadow capability**. A Gate B pass may make selective precision a candidate policy for realistic testing.

Neither gate authorizes a global claim graph, automatic claim extraction/risk classification, model provenance assignment, derived-to-derived authority, RDF/OWL, vector/graph storage, or persistent compiled-Wiki activation.
