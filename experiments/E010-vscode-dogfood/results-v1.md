# E010 self-repo dogfood — result v1

Status: **AUTOMATED P1–P5 CLOSED / CUSTOMER READY STILL PENDING P6–P7**

Date: 2026-08-15 KST

Validated change: PR #78, branch head `a3aba2cd07efca75f32838fe551e92e1180c62cd`  
E010 workflow: `31827712130`  
PR test merge ref observed by Actions: `f7974d379281e63e2f12647e1557b01857755e34`  
E010 artifact: `9229446184`  
E010 artifact digest: `sha256:ef814c7daec2f18fa0ef3463795f301474cf79a1b19ce1c0953f34e8258da1fa`

Model calls / AI credits: **0 / 0**

## Self-hosting corpus

- Git-tracked files: **278**
- UTF-8 files ingested into the raw-first Wiki: **278**
- skipped binary/non-UTF-8 files: **0**

The corpus is the actual checked-out repository, not a curated mini corpus.

## Frozen Stage A retrieval result

The 12 E010 retrieval questions and expected-source sets were kept unchanged from result v0.

| Metric | v1 | Gate |
|---|---:|---:|
| expected source in W0 top-5 | **11/12 = 0.917** | >= 0.90 |
| mean reciprocal rank | **0.736** | >= 0.60 |
| non-empty rendered context | **12/12** | 12/12 |

**Stage A remains PASS.**

The earlier v0 run on the then-smaller 272-file repository scored 12/12 and MRR 0.753. The repository subsequently grew; v1 records the observed 11/12 / 0.736 rather than moving the threshold or expected-source set after seeing the result.

The single frozen expected-source miss is `luna-discovery`. Its v1 top result is the VS Code README section that correctly explains exact `gpt-5.6-luna` discovery/no-fallback behavior, while the two predeclared implementation files (`lm-discovery.js` / `package.json`) fell outside top-5. This is a useful limitation of expected-file scoring: the user-semantic retrieval can be relevant even when the frozen implementation-file target misses. The official score remains **11/12**.

## Automated product findings after 0.1.4

The five product blockers found in v0 are closed by measured/packaged behavior:

### P1 — original-source navigation: CLOSED for current Alpha product

- canonical evidence still contains no workspace path/URI identity field;
- VS Code stores only a workspace-relative local navigation hint + evidence SHA in extension workspace state;
- the original workspace file is opened only when its current bytes still hash to the immutable evidence SHA;
- moved/changed/missing workspace files fall back to the immutable raw provenance document.

This disambiguates repeated basenames without turning mutable paths into evidence identity or trust weight.

### P2 — correction/change/dispute from VS Code: CLOSED

0.1.4 exposes explicit customer commands for:

- correction;
- change over time with caller-supplied timezone-aware effective instant;
- unresolved dispute with no inferred winner.

The commands call the existing ADR-0005 core semantics; they do not add a second VS Code knowledge model.

### P3 — fixed-code feedback from VS Code: CLOSED

VS Code exposes the existing local E013 helpful/not-helpful feedback path and offers it after Ask. No free-text telemetry is added.

### P4 — forgotten-topic recovery: CLOSED at current Alpha floor

`Global Search Current Evidence Across Topics` searches each registered topic's **current** view and is discovery-only:

- superseded history is not silently treated as current;
- it does not invoke a model;
- it does not manufacture E013 query visits;
- selecting evidence switches the active topic for subsequent normal topic-scoped work.

The flow is exercised through the real VS Code-to-core bridge in both development and packaged VSIX Extension Host tests.

### P5 — backup/restore operating story: CLOSED at current Alpha floor

0.1.4 ships a self-contained minimal whole-directory offline snapshot/restore procedure in the extension README, with a longer repository guide at `docs/11-local-backup-restore.md`.

It deliberately does not pretend to be live transactional backup, cloud sync, multi-writer snapshotting, or automatic recovery.

## Regression / packaging validation

PR #78 final validation was green for:

- Python unit tests and CLI smoke;
- VS Code static/product-helper checks;
- development Extension Host including the new cross-topic product flow;
- shared-core bundling;
- installable 0.1.4 VSIX packaging;
- unpacked packaged-VSIX Extension Host with the same integration suite;
- frozen E004, E014, and E014-R1 validations.

The validated VSIX artifact from run `31827712132` is artifact `9229468095`, GitHub artifact digest `sha256:045c6cdb9d49384d88f0fd101f6591ae3fc0ca79e1e4f092ff1577d894721856`.

## Remaining customer gates

The automated gate now reports only:

1. **P6 — real VS Code/Copilot exact-Luna gate pending.** CI cannot prove the user's Copilot Pro entitlement/model availability. Run zero-generation discovery in the real user session; require exact `id` or `family == gpt-5.6-luna`. Only if exact Luna exists should the separately bounded <=2-generation native-adapter smoke proceed. No silent fallback.
2. **P7 — repeated customer-like multi-session use pending.** One full-repo run and packaged Extension Host tests do not prove the product is habit-forming/useful over time. Use capture → leave → recall later → provenance → correction/change/dispute → feedback across real sessions and let E013/E015 data arise naturally.

## Product verdict

0.1.4 is a substantially stronger **Alpha/dogfood product** and can self-host this repository above the preregistered retrieval floor. It is **not yet a customer-ready release** because P6 and P7 require evidence that automation cannot manufacture.
