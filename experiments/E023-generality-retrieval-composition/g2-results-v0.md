# E023 G2 — fixed-identity persistence result v0

Status: **COMPLETE / STRICT PROMOTION NOT EARNED / STALE GUARD EARNED AS A MECHANISM SIGNAL**  
Run: `32353304896`  
Execution source: `3cf65d7255b8edc73a9d8cb3d13338e019cc92f8`  
Evidence commit: `c0a1cb01fbff29910c270283106217a111d00057`  
Exact model: `gpt-5.6-luna`  
Semantic attempts: **29 / 29**  
Projection build/rebuild calls: **5 / 5**  
Q composer calls: **12 / 12**  
P composer calls: **12 / 12**  
Planner / selector / vector calls: **0 / 0 / 0**  
Rerolls: **0**  
Result SHA-256: `f241d3059bb174aacff84f2e54ad30ed390fc575c8141a2965558fe93dd9adfa`

## Frozen question

G2 asked whether, with fixed subject identity and the final composer held constant, a rebuildable persisted DERIVED retrieval projection could beat the strong G1 query-time comparator enough to justify maintenance and stale-state risk.

- **Q:** current fixed-subject terminal authority -> exact BM25 top-6 -> frozen old composer.
- **P:** query-blind persisted projection -> deterministic projection retrieval of terminal anchors -> the same frozen old composer.
- Projection text was retrieval-only and never entered final composer context.
- Snapshot mismatch required exact `STALE_PROJECTION_BYPASS` to Q.

This was not a graph/entity/identity-routing experiment.

## Execution integrity

The one-shot run completed exactly as frozen:

- 29 semantic attempts;
- exact `gpt-5.6-luna` throughout;
- 5 projection build/rebuild calls;
- 24 answer calls;
- zero rerolls;
- all five projection contracts parsed successfully;
- every build/rebuild projection referenced every terminal anchor in its source snapshot;
- no projection compiler call occurred inside a query event.

## Frozen semantic adjudication

Q:

- **10 PASS**;
- **0 PARTIAL**;
- **0 FAIL_RETRIEVAL**;
- **0 FAIL_COMPOSITION**;
- **2 CRITICAL_ERROR**.

P:

- **8 PASS**;
- **0 PARTIAL**;
- **1 FAIL_RETRIEVAL**;
- **0 FAIL_COMPOSITION**;
- **3 CRITICAL_ERROR**.

P paired semantic improvements vs Q: **2** (`PQ004`, `PQ008`).  
P paired semantic regressions vs Q: **3** (`PQ007`, `PQ009`, `PQ012`).  
P new critical errors vs Q: **3**.

The frozen promotion required >=10/12 P PASS, >=2 improvements, **0 regressions**, and **0 new critical errors**. It therefore fails strictly.

> **G2 fixed-identity persistence promotion is NOT_EARNED. Do not weaken the frozen rule.**

## What persistence genuinely improved

### PQ004 — one prospective authority miss repaired

Q exact top-6 omitted P004, the broader portfolio evidence required prospectively to support the negative characterization that Dana Cho was not generally opposed to managed key services. Q still answered the full proposition and marked authority sufficient, so Q is a truth-by-luck-style `CRITICAL_ERROR`.

The Iris projection had compressed P003 + P004 into a query-relevant entry. Fresh P retrieval selected both terminal anchors. P then answered the narrow regulated-release exception and broader portfolio policy safely.

**PQ004: CRITICAL_ERROR -> PASS.**

### PQ008 — safer outcome, but the persistence opportunity itself failed

The rebuilt Juniper projection did contain P021, the required second independent month-close observation. However, projection-statement retrieval did not select its entry. P therefore remained authority-incomplete and safely returned insufficiency, while Q incorrectly claimed repetition from P014 + P022.

Semantically this is an improvement from Q `CRITICAL_ERROR` to P `FAIL_RETRIEVAL`, but the prospectively required persistence mechanism result was stronger: fresh P authority itself had to recover P021 and become sufficient.

That did **not** happen. PQ008 therefore fails the required authority-opportunity gate.

## Stale-state guard worked

The strongest positive G2 mechanism result is the freshness boundary.

### PQ011 — primary stale negative control

Keystone changed from the old 30-day state to a new 90-day policy and superseding project decision while the S0 projection was stale.

P detected snapshot mismatch, did not use stale projection text, and reproduced the exact Q terminal-anchor context. Both arms correctly stated the current P033 90-day policy, P034 superseding project decision, P035 implementation, and historical status of the old 30-day decision.

**PQ011: stale/current inversion avoided; PASS.**

### PQ007 — guard correct, separate model-call variance unsafe

Juniper also hit `STALE_PROJECTION_BYPASS`. P and Q used the exact same selected anchors, rendered context, question, and prompt hash.

Q safely recognized that the selected context lacked required P021 and returned insufficiency. The independent P Luna call nevertheless treated P022 as completing repeated evidence and marked authority sufficient.

This is **not a persistence-selection failure** because stale projection selection was bypassed correctly. It is paired model-call variance on identical input. The frozen gate nevertheless counts the observed P semantic regression; we do not erase it post hoc.

## Where the persistence retrieval mechanism regressed

The critical architecture signal is not that the projection compiler forgot authority. It did not: every projection build referenced every supplied terminal anchor.

The failures arose when query-time retrieval over projection statements reduced that preserved authority back to a small terminal set.

### PQ009 — governing policy dropped

The Keystone S0 projection explicitly contained P026, the governing customer retention policy, in entry E02. For PQ009 the query ranking placed:

1. E01 — project decision / meeting context;
2. E04 — implementation / audit;
3. E02 — governing customer policy P026.

The frozen top-2 projection-entry rule selected E01 + E04 and omitted P026. P then presented project-owned/meeting authority as the governing customer requirement.

**PQ009: Q PASS -> P CRITICAL_ERROR.**

### PQ012 — superseding user-owned decision dropped

The Keystone S1 rebuilt projection explicitly contained P034, the user-owned superseding 30 -> 90-day decision, in E08. For PQ012 the entry ranked third, behind historical implementation/audit and current policy entries.

Top-2 projection retrieval omitted P034. P still answered the current decision/supersession as sufficient using policy, implementation, and historical anchors.

**PQ012: Q PASS -> P CRITICAL_ERROR.**

This is the same broad failure class seen earlier in G1 selector experiments:

> **A representation may preserve load-bearing authority globally while a later selection stage discards it locally.**

Persistence does not remove the evidence-selection problem; it can simply move that problem onto the projection.

## Evidence-context efficiency did pass

Across the ten fresh-projection queries, excluding stale-gap PQ007/PQ011:

- Q selected raw terminal evidence characters: **10,282**;
- P selected raw terminal evidence characters: **7,019**;
- P / Q = **68.3%**;
- frozen maximum = **85%**.

So the candidate produced substantial terminal-context compression.

That efficiency does not compensate for authority regressions or critical semantic errors. The project explicitly requires semantic safety/value before lifecycle cost or context savings can justify persistence.

## Frozen promotion arithmetic

Failed requirements include:

- PQ008 required fresh authority opportunity did not improve;
- fresh authority regressions occurred on PQ009 and PQ012;
- PQ012 post-rebuild correction/supersession was `CRITICAL_ERROR`, not PASS;
- P PASS count was 8, below required 10;
- P semantic regressions were 3, above allowed 0;
- P new critical errors were 3, above allowed 0;
- P unsupported load-bearing claims were nonzero.

Passed requirements include:

- exact execution integrity;
- both stale bypass mechanics;
- PQ011 stale negative control;
- at least two paired semantic improvements;
- <=85% fresh evidence-character ratio;
- exact five maintenance calls and zero query-time compiler calls.

Strict result remains **NOT_EARNED**.

## Project implication

Do **not** respond by immediately increasing projection top-k and rerunning the same PQ slice.

The posthoc rank trace is useful diagnostically:

- P026 in PQ009 was only one projection-entry boundary outside top-2;
- P034 in PQ012 was also rank 3;
- but required P021 in PQ008 was much deeper in the projection ranking, so a trivial top-3 rule would not solve the full prospective failure set.

The evidence supports a narrower conclusion:

> **Fixed-identity persistent semantic projection has not earned itself. Its stale-state snapshot guard is credible, and its query-time context can be smaller, but the projection retrieval layer reintroduces destructive authority selection risk.**

Do not start G3. Do not introduce graph/entity/KU storage, automatic identity routing, vector defaults, or product persistence from this result.

## Next deliberate step

No further paid G2 rerun is justified on this material.

The next work should be zero-model/project-level closure:

1. freeze this G2 result and source-lock the completed workflow;
2. record the diagnostic that compiler coverage was complete but projection retrieval discarded load-bearing authority;
3. decide whether G2 should remain parked until natural dogfood demonstrates a repeated-use problem large enough to justify another separated persistence experiment;
4. continue Dogfood 0.1.16 natural installed observation on Issue #141;
5. keep Issue #132 reliability edges evidence-gated.

A future persistence experiment, if natural evidence reopens the question, must use new separated material and a prospectively justified selection mechanism. This result does not authorize same-slice tuning.
