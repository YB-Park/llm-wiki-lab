# E003 — minimum temporal semantics truth-table result v0

Status: **SURVIVES_E003_V0**

Date: 2026-08-14

This is a deterministic correctness/mechanism result. It is not a statistical benchmark and does not establish that users will reliably classify temporal relations correctly in realistic workloads.

## Question

Can the existing append-only, topic-scoped source-lineage core distinguish generic replacement, correction, change-over-time, and unresolved disagreement without introducing inference, destructive migration, a general bitemporal query engine, or hidden consensus?

**Result: yes, within the preregistered v0 boundary. All 20 required checks passed.**

## Accepted minimum semantics

- `generic`: predecessor leaves current membership; successor remains current; no assertion about whether predecessor was wrong or formerly valid.
- `correction`: caller explicitly asserts that predecessor was erroneous and successor corrects it; no valid-time claim is added.
- `change`: caller explicitly asserts a state transition at a timezone-aware `effective_at`; append `recorded_at` remains a separate clock. Future/scheduled change is rejected in v1.
- `dispute`: two specific current evidence revisions remain current and are explicitly marked contested; no winner or consensus is inferred.

All semantics are explicit caller assertions. The core does not infer relation kind from content, path, filename, origin, similarity, timestamps, or model output.

## Gate audit — 20/20

1. **Legacy generic replay — PASS.** Existing `supersede` records without `relation_kind` replay as `generic` and preserve old `source_status` membership behavior.
2. **Explicit generic compatibility/idempotency — PASS.** New explicit generic replacement has the same current/history membership and exact retries do not append duplicate relation events.
3. **Correction — PASS.** A corrected predecessor leaves current membership, remains audit-resolvable, reports `replacement_kind=correction`, and carries no `effective_at`/valid-time assertion.
4. **Change valid-time separation — PASS.** Past timezone-aware `effective_at` is normalized to UTC, stored separately from later `recorded_at`, and exposed as successor `valid_from` when unambiguous.
5. **Invalid/naive/future change time containment — PASS.** Invalid, timezone-naive, future, missing, and non-change `effective_at` cases fail before relation append.
6. **Exact typed retry idempotency — PASS.** Generic, correction, and change exact retries are idempotent while the recorded successor remains current.
7. **Semantic relabel/retarget conflict — PASS.** Different relation kind, different effective time, or different successor cannot retroactively reinterpret a recorded replacement; the existing history remains authoritative.
8. **Dispute has no hidden winner — PASS.** Both endpoints remain current and both project `contested=true` with symmetric `disputes_with` metadata.
9. **Duplicate dispute idempotency — PASS.** Repeating the same active canonical pair does not append another dispute event.
10. **Invalid dispute containment — PASS.** Self, missing, and non-current endpoints fail closed.
11. **Revision-pair dispute expiry — PASS.** Replacing one disputed endpoint removes only that revision-pair from the active dispute projection; the successor does not inherit conflict automatically.
12. **Topic isolation — PASS.** Relation activity in one topic does not alter another topic's projection even when immutable content objects are shared.
13. **A→B→A recurrence for every replacement kind — PASS.** Generic, correction, and change all preserve explicit recurrence through a fresh A2 evidence revision while reusing A's immutable raw object.
14. **Historical citation/raw resolution — PASS.** A1/B historical source IDs remain resolvable after generic/correction/change and after recurrence.
15. **E013/E015 semantics unchanged — PASS.** Existing workload-calibration and privacy-minimal retrieval-shadow tests remain green.
16. **Default retrieval membership — PASS.** Replaced evidence is excluded from topic-current retrieval while both unresolved disputed current sources remain visible.
17. **Post-retrieval contest annotation — PASS.** Topic-scoped rendered context adds temporal/epistemic metadata only after retrieval; object order, scores, source IDs, and snippets are unchanged by asserting a dispute. Unscoped context makes no current/contest claim.
18. **Answer boundary preserves disagreement — PASS.** Prompt contract explicitly treats `epistemic_status: contested` as unresolved disagreement and forbids manufacturing consensus, silently selecting a winner, or collapsing competing evidence into one canonical fact.
19. **Legacy lineage regressions — PASS.** Existing generic supersession, stale-relation, recurrence, identity, and provenance tests remain green without fixture rewrites.
20. **VS Code consumer regressions — PASS.** Development and packaged Extension Host tests remain green; no VS Code feature work was added.

## CI evidence

Latest all-required implementation head before this report: `c5b947b50f27c52244cd0529ef47d25756202e2a`.

GitHub Actions:

- `VS Code Dogfood` run `31794275157` — **SUCCESS**
  - Python unit tests: **62/62 PASS**
  - CLI smoke: PASS
  - VS Code static/safety checks: PASS
  - development Extension Host: **4/4 PASS**
  - bundled shared Python core: PASS
  - packaged VSIX Extension Host: **4/4 PASS**
  - compiled provider remains disabled
- `Validate E014 frozen result` run `31794275191` — SUCCESS
- `Validate E014 R1 prescore` run `31794275119` — SUCCESS
- `Discover E014 R1 freeze hashes` run `31794275134` — SUCCESS

Model calls: **0**. AI credits: **0**.

## Important interpretation ceiling

E003 validates a **minimum explicit representation and projection contract**. It does not prove that automatic temporal classification is safe or that users will correctly choose `correction`, `change`, or `dispute` in realistic use.

In particular, E003 does not authorize:

- a general as-of/bitemporal query engine;
- scheduled future transitions;
- automatic contradiction or relation detection;
- LLM temporal classification;
- dispute clustering/entity resolution;
- claim-level temporal ontology;
- graph/vector storage;
- persistent compiled-Wiki activation.

The lack of an independent dispute-retraction event is deliberate in v0. A dispute currently ends when one specific revision endpoint is replaced. If realistic use shows that explicit retraction is necessary, that is a new requirement and must be evaluated rather than silently widening this ontology.

## Architecture consequence

The trustworthy raw-first core can now distinguish **membership** from the **reason for temporal/epistemic transition**:

```text
immutable raw object
    -> evidence revision
    -> topic current/history membership
    -> explicit relation semantics
         generic | correction | change
       + explicit current-revision dispute
    -> post-retrieval temporal/contest annotation
    -> answer boundary that preserves unresolved disagreement
```

This removes a correctness ambiguity without requiring a full temporal database.

## Next step

Do not expand temporal machinery just because E003 passed. The next core question should test the minimum useful **claim-to-provenance ownership** boundary (E004): when document/object-level provenance is insufficient, what is the smallest span/claim representation that materially improves auditability without creating a claim graph that costs more to maintain than it is worth?
