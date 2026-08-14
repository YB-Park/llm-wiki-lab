# E004 — Minimum provenance granularity result v0

Status:

- **Gate A: `SURVIVES_E004_PRECISE_GATE` — 10/10 checks passed**
- **Gate B: `SELECTIVE_PRECISION_NOT_ESTABLISHED_E004_V0` — 6/8 checks passed**

Date: 2026-08-14

Issue: #43  
PR: #44

Model calls: **0**  
AI credits: **0**

## 1. Decision question

Does exact claim-to-raw-span provenance provide a sufficiently large audit/source-ownership advantage over structural provenance to deserve existence as a capability, and does the tested selective high-risk policy reduce that precision burden enough to deserve preference over universal precision?

## 2. Official frozen run

First and only automatic official held-out score:

- workflow: `Score E004 official heldout`
- run: `31796083458`
- branch head: `df59b56b8a67c6b2548fab2fb9fcd524194315da`
- result artifact: `9217412128`
- artifact archive digest: `sha256:20263a677401636810e9048095f99d3bf701e8b44f30fe45bd2199bfe8ad1927`

Frozen corpus SHA-256:

`68317ea91cac451ca59012f62506dbd1a249d76191ae9d06cc7777276a74ad80`

Frozen score-affecting bytes were reverified before scoring:

- generator `f13b35577028b8fa0aca32e942f1fa140f51584fc7db5392d7ea67c752d7dd1b`
- condition/auditor `c7922b38404aac4af0469a79a59ee7f506bb23d04e1d2787141425be57684a3a`
- scorer `56a8b3f95ab9cddff41a35ecb434c2033a92d36ac0e6462ab26207ae84cd1aad`
- validator `8ba66358a05d2485f103db9fccc537d2f6162069589617496f08e6be276d8bfa`

Automatic scoring was immediately removed after the run. Frozen-result validation run `31796161211` is SUCCESS.

## 3. Headline results at the frozen 1,200-character audit budget

| Condition | Critical audit accuracy | Exact ownership | Critical inspected chars | Conflict detection | Metadata bytes | W1 updates |
|---|---:|---:|---:|---:|---:|---:|
| P0 page bibliography + audit-time localization | 0.600 | 0.000 | 1015.1 | 1.000 | 7,368 | 48 |
| P1 structural ownership | 0.700 | 0.000 | 1135.8 | 0.750 | 31,899 | 144 |
| P2 exact claim-to-span | **1.000** | **0.583** | **335.4** | **1.000** | 42,264 | 144 |
| P3 structural + exact only for frozen high-risk | 0.850 | 0.292 | 733.9 | 0.917 | 52,771 | 216 |

Clean false-accusation rate was `0.000` for all four conditions.

Derived-only provenance acceptance:

- P0: `1.000`
- P1: `0.000`
- P2: `0.000`
- P3: `0.000`

The P0 derived-only miss is an explicit example of pooled page evidence verifying a fact somewhere without preserving the fact's actual source ownership.

## 4. Primary paired comparisons

P2 − P1 critical bounded-audit accuracy:

`+0.300`, topic bootstrap 95% CI `[+0.300,+0.300]`

P2 − P1 exact source-ownership rate:

`+0.583`, topic bootstrap 95% CI `[+0.583,+0.583]`

P2/P1 mean critical inspected-character ratio:

`0.295`

So in this controlled corpus P2 inspected about 29.5% as many critical source characters as P1 while improving audit correctness and source ownership.

### Important CI interpretation

The zero-width percentile intervals are **not** evidence of population-level precision. Every topic used the same balanced 12-claim family/risk structure and the deterministic mechanism produced the same topic-level paired effect in all 24 topics. Topic bootstrap therefore resampled identical paired differences.

This strengthens the claim that the controlled mechanism was consistently reproduced across the generated topics, but it does **not** provide realistic workload uncertainty or user-population generalization. Evidence grade remains controlled synthetic mechanism/falsification.

## 5. Gate A audit — exact precision deserves to exist as a capability

All preregistered checks passed:

1. P2 − P1 critical accuracy >= +0.15 — **PASS** (`+0.300`)
2. critical-accuracy CI lower > 0 — **PASS**
3. P2 − P1 exact ownership >= +0.20 — **PASS** (`+0.583`)
4. ownership CI lower > 0 — **PASS**
5. P2 critical chars <= 0.65 × P1 — **PASS** (`0.295 ×`)
6. P2 clean false accusation <= P1 + 0.02 — **PASS** (`0.000` vs `0.000`)
7. P2 conflict detection >= P1 − 0.05 — **PASS** (`1.000` vs `0.750`)
8. P2 exact raw-span reversibility = 100% — **PASS**
9. P2 derived-only acceptance = 0% — **PASS**
10. scoring read-only — **PASS**

Official Gate A result:

**`SURVIVES_E004_PRECISE_GATE`**

### What this allows

Only this conclusion is authorized:

> A local optional record that can bind a derived claim/atom to an exact span of an immutable raw source revision deserves implementation and realistic/shadow evaluation.

It does not establish universal claim-level provenance as a product default.

## 6. Gate B audit — tested selective precision policy fails

P3 matched P2 on the frozen high-risk quality checks:

- high-risk audit accuracy: P3 `1.000`, P2 `1.000`
- high-risk exact ownership: P3 `0.583`, P2 `0.583`
- high-risk conflict detection: P3 `1.000`, P2 `1.000`
- clean false accusation: both `0.000`
- precise-subset raw reversibility: 100%
- derived-only acceptance: 0%

But it failed both burden checks:

- metadata: P3 `52,771` vs P2 `42,264` = **1.249 × P2**, required <= `0.75 ×`
- W1 update actions: P3 `216` vs P2 `144` = **1.50 × P2**, required <= `0.80 ×`

Why: P3 as preregistered retained P1 structural metadata for all claims and then added P2 exact metadata for high-risk claims. In this representation that is a **dual bookkeeping layer**, not a cheaper precision policy.

P3 also exposed the expected low-risk quality ceiling:

- high-risk accuracy `1.000`
- low-risk accuracy `0.750`

Official Gate B result:

**`SELECTIVE_PRECISION_NOT_ESTABLISHED_E004_V0`**

Do not claim that risk-adaptive/selective provenance is preferred based on E004-v0.

## 7. Sensitivity budgets

Critical audit accuracy / inspected chars:

### 600 chars

- P0 `0.600 / 600.0`
- P1 `0.233 / 600.0`
- P2 `1.000 / 325.8`
- P3 `0.600 / 462.9`

### 2,400 chars

- P0 `0.600 / 1467.0`
- P1 `0.800 / 1316.3`
- P2 `1.000 / 335.4`
- P3 `0.900 / 822.9`

P2's controlled advantage is not an artifact of only the 1,200-character primary budget in this corpus. P1 improves with a larger budget, but P2 remains fully correct with much less inspected evidence.

## 8. Fault-family diagnostics

At the primary budget:

- `clean`: all conditions accuracy 1.0; P2 exact ownership 1.0
- `wrong_value`: all conditions accuracy 1.0; only P2 provides exact ownership 1.0 universally
- `wrong_source`: P0 1.0, P1 0.75, P2 1.0 audit accuracy; exact ownership remains 0 for P2 because the injected citation itself names the wrong source
- `derived_only`: P0/P1 accuracy 0.0, P2 1.0; P3 0.5 due its high/low split
- `within_source_conflict`: P0 1.0, P1 0.75, P2 1.0, P3 0.917
- `multi_source_misownership`: P0 0.0, P1/P2/P3 1.0; P2 ownership 0.5 because one of the two injected atom citations is intentionally wrong

These slices show why “fact exists somewhere in the page/context” and “this claim is owned by this raw source” must remain distinct concepts.

## 9. Cost / maintenance diagnostics

Serialized provenance metadata bytes:

- P0 `7,368`
- P1 `31,899`
- P2 `42,264`
- P3 `52,771`

Oracle-minimum W1 current-provenance update actions:

- P0 `48`
- P1 `144`
- P2 `144`
- P3 `216`

D1 derived-rewrite/reorder lower-bound reattachment actions:

- P0 `0`
- P1 `48`
- P2 `288`
- P3 `192`

The D1 numbers intentionally expose a major limitation of precise provenance: if ownership metadata is attached to claim positions rather than a stable local record identity, derived rewrites can create large reattachment burden. Benchmark IDs make these optimistic lower bounds; real maintenance may be worse.

Descriptive Pareto frontier at the frozen measures: `P0, P1, P2`. P3 is not on the frontier.

## 10. Architecture consequence

E004-v0 supports **one** additional core capability:

```text
immutable raw source revision
        + exact [start,end) span
        + local derived claim/atom attachment
        + raw reversibility
```

The capability should be optional and local. It must not become a second authority layer.

The implementation should preserve:

- ADR-0003 append-only current/history source lineage;
- ADR-0004 content/evidence identity separation;
- ADR-0005 explicit temporal/dispute semantics;
- raw source revision as authority;
- no derived-only source as authoritative provenance;
- no automatic provenance inference or repair.

## 11. What E004-v0 explicitly kills or postpones

Do **not** implement from this result:

- P3's tested “structural everywhere + exact on high-risk” dual-storage policy;
- a global claim registry/graph;
- automatic claim extraction;
- automatic risk classification;
- LLM provenance assignment/reassignment;
- derived-to-derived evidence as authority;
- RDF/OWL/full W3C PROV storage;
- graph/vector database;
- compiled-Wiki activation.

A future selective policy would require a materially different representation rather than retroactively relabeling P3 as successful.

## 12. Next action

Implement the smallest **local exact raw-span provenance record** behind an explicit opt-in/shadow boundary.

Required implementation properties before realistic evaluation:

- source revision ID + exact immutable character span;
- deterministic raw-byte reversibility;
- optional atom/local-label identity, not a global claim graph;
- reject derived-only authoritative targets;
- preserve historical source resolution after source supersession;
- preserve E003 temporal/dispute metadata independently;
- fail closed on invalid/out-of-range/stale target metadata;
- no model calls;
- no default product behavior change.

Then use realistic dogfood/shadow tasks to determine whether users actually benefit from this precision enough to pay the D1 rewrite/reattachment burden seen here.
