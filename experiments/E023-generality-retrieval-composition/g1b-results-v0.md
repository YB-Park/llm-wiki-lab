# E023 G1b result v0 — iterative evidence-follow retrieval

Status: **G1b PROMOTION NOT EARNED / TARGETED TRUST REPAIR OBSERVED**  
Run: `32217824760`  
Frozen execution source: `7c604dd8d57a90c99526bdce5fb55fe7cdb7056f`  
Model: exact `gpt-5.6-luna`  
Semantic model-call attempts: **12 / 12**  
Semantic rerolls: **0**  
Result SHA-256: `0b092a1b85577a12bb664fc9bee31a648b316fc317277d35454a9a72c0b7c2c1`

GitHub Actions completed the execute job successfully, including raw artifact upload and immutable evidence commit.

## Frozen target

G1b did **not** rerun the ten-question baseline. It targeted only the four questions where both frozen G1a A and C had incomplete required-source recall@5:

- Q001
- Q002
- Q004
- Q010

Each target used:

1. the same exact-query initial top-5 as G1a A;
2. one evidence-gap planner that inspected only bounded metadata/snippets for those hits;
3. 0–2 targeted follow-up BM25 queries;
4. one selector choosing at most five final source IDs from the temporary candidate pool;
5. the **unchanged G1a composer prompt** on the selected full evidence.

No semantic state persisted across questions.

## Frozen promotion result

| Q | frozen A verdict | missing source reached candidate pool? | missing source selected final? | G1b semantic verdict |
|---|---|---|---|---|
| Q001 | CRITICAL_ERROR | yes — S004 | **yes — S004** | **PASS** |
| Q002 | PASS | no — S003 | no | PASS |
| Q004 | PASS | yes — S008 | no | PASS |
| Q010 | PASS | no — S003 | no | PASS |

Totals:

- candidate-pool recovery of previously missing source: **2 / 4**;
- final-context recovery of previously missing source: **1 / 4**;
- semantic verdicts: **4 PASS / 0 PARTIAL / 0 FAIL / 0 CRITICAL**;
- semantic improvements versus frozen A: **1**;
- semantic regressions: **0**;
- new critical errors: **0**.

The preregistered promotion rule required the previously missing source to enter final context for **at least 3/4** targets. Only 1/4 did. Therefore:

> **G1b is NOT_EARNED under its frozen promotion rule.**

Do not retroactively weaken that rule because the semantic answers were good.

## Q001 — the important positive repair

G1a's critical failure was an unsupported identity merge. The initial Q001 top-5 omitted S004, the explicit directory bridge connecting:

- Park Jihoon;
- Jihoon Park;
- J.H. Park;
- the stable ABC contact/email;
- Privacy Counsel.

G1b's planner explicitly recognized the missing identity/disambiguation relation and issued:

- `"J.H. Park" "Jihoon Park" DPA`
- `"same privacy contact" DPA Park`

The first query ranked **S004 at 1**. The temporary candidate pool became complete and the selector chose:

`S001, S003, S004`

while dropping same-surname distractor S005.

The unchanged composer then answered that Jihoon Park / J.H. Park was the ABC Privacy Counsel who repeatedly raised the DPA concern, citing S001/S003/S004.

This is a real mechanism signal:

> **evidence-aware follow-up retrieval repaired the exact authoritative bridge whose absence caused the frozen critical error.**

It matters that the composer prompt was unchanged. The improvement came from context construction, not from adding a special “please be careful with identities” instruction after seeing the failure.

## Q002 — semantic PASS without the frozen missing S003

G1b did not recover S003 into the candidate pool. The selector chose:

`S002, S001, S004`

This set is nevertheless sufficient for the user question:

- S002 — Jihoon's direct-authored DPA statement;
- S001 — meeting-note attribution to J.H. Park;
- S004 — explicit alias/identity bridge.

The answer correctly distinguishes direct authorship from meeting attribution and remains PASS.

This exposes a weakness in the original flat `required_sources` ground truth: S003 is useful corroboration, but it is **not uniquely load-bearing** for this question when S001 and S004 are present.

## Q004 — recovered S008, selector correctly did not need it

Follow-up retrieval brought missing S008 into the candidate pool. The selector then chose only:

`S009, S010`

The final answer remains fully correct:

- S009 directly records the no-Redis decision and operational-complexity rationale;
- S010 directly records the unrealistic 20x burst and says it does not reverse the decision.

S008 is corroborating Operations rationale, but once S009 is present it is not necessary to answer the frozen question.

Again, the frozen promotion rule must still count this as a failure to select the previously missing source. But the semantic outcome shows why future retrieval evaluation should not equate **“all listed supporting sources present”** with **“all load-bearing authority present.”**

## Q010 — broad characterization still safely rejected

G1b did not recover S003. The selector chose:

`S002, S006, S005`

The unchanged composer correctly rejected the broad `risk-averse` / `anti-cloud` characterization:

- S002 explicitly narrows the DPA requirement and says it is not a general objection to cloud services;
- S006 records later closure without establishing a broader reversal;
- S005 is correctly used only to distinguish Park Jieun from Jihoon Park.

The answer remains PASS with no semantic regression.

## The new core finding: flat required-source sets are too coarse

G1b deliberately obeyed a frozen rule that now looks overly strict.

The original E023 questions used one flat `required_sources` list. That was useful for first-pass retrieval diagnostics, but G1b shows at least three evidence roles need to be distinguished in future gates:

1. **load-bearing / uniquely required authority** — absence makes the claim unsupported or unsafe;
2. **alternative or corroborating support** — useful but not required if another authoritative source establishes the same necessary proposition;
3. **forbidden / disambiguating distractor** — presence is not itself failure, but conflation is.

Examples from this run:

- Q001 S004 is genuinely load-bearing for the alias merge. Its recovery repaired a critical trust failure.
- Q002 S003 is redundant if S001 supplies meeting attribution and S004 supplies identity.
- Q004 S008 corroborates rationale already stated directly in S009.
- Q010 S003 is not necessary to reject the broad characterization when S002 supplies explicit negative evidence.

Therefore the next evaluation contract should represent **evidence requirements as logical support clauses**, not as “every source in this flat list must be in final context.”

Illustrative shape only, not yet a frozen schema:

```text
Q002
  direct-authored DPA claim: requires S002
  meeting attribution: requires one of {S001, S003}
  J.H. Park == Jihoon Park bridge: requires S004
```

This is an evaluation improvement, not a proposal for a canonical claim graph.

## Cost / usage

- G1b: **12 model calls** total;
- all planner/selector/composer receipts reported exact `gpt-5.6-luna`;
- zero semantic rerolls;
- token totals: unknown — runner transport did not expose machine-readable totals;
- AI credits/premium requests: unknown — never infer them from calls or tokens.

## Architecture consequence

### Earned

- Evidence-follow retrieval has a **real targeted positive signal**: it repaired Q001's unsupported identity merge by recovering the explicit authoritative bridge and selecting it into context.
- A planner that has inspected existing evidence can be materially different from blind query expansion.
- Selectors may legitimately discard redundant evidence while retaining a sufficient authoritative basis.
- Retrieval evaluation must distinguish load-bearing authority from redundant corroboration before another broad gate is meaningful.

### Not earned

- G1b as a general retrieval/selection policy — frozen promotion failed 1/4 vs required >=3/4.
- G2 persistent semantic dossiers.
- Entity/Relation/KnowledgeUnit core schema.
- automatic identity merge/split.
- graph/vector default changes.
- production addition of two extra Luna calls per memory query.

## NEXT — no more paid retrieval tuning yet

Do **not** immediately run G1c/G2.

The next core work should be zero-model/evaluation design:

1. preserve the frozen E023 results unchanged;
2. define a small evaluation-only representation for **load-bearing support clauses / alternative corroboration / forbidden conflation**;
3. re-score the existing A/C/G1b contexts against that richer authority requirement without new model calls;
4. determine whether the remaining actual failure is retrieval, selection, or composition once redundant-source penalties are removed;
5. only then decide whether another G1 retrieval gate is justified.

Do not turn this evaluation representation into product storage or a claim graph. It exists to measure whether retrieval supplied the authority needed for a trustworthy answer.

Dogfood 0.1.16 remains unchanged and natural installed use continues in parallel.
