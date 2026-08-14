# E010 self-repo dogfood — result v0

Status: **STAGE A PASS / CUSTOMER READY FAIL**

Date: 2026-08-15 KST

Automation run: GitHub Actions `E010 self-repo dogfood` run `31825703528`  
Artifact: `e010-self-repo-dogfood` (`9228702968`)  
Artifact digest: `sha256:2c3babc827ca38de4ada641fd82300697bd70bf53c6a29073c13347c9b6dad7f`

Model calls / AI credits: **0 / 0**

## Corpus

The experiment ran against the actual checked-out repository, not a hand-picked mini corpus.

- Git-tracked files: **272**
- UTF-8 files ingested into the raw-first Wiki: **272**
- ingested bytes: **1,602,314**
- skipped binary/non-UTF-8 files: **0**
- one project topic: `llm-wiki-lab self dogfood`

## Preregistered retrieval signal

| Metric | Result | Gate |
|---|---:|---:|
| target source in W0 top-5 | **12/12 = 1.000** | >= 0.90 |
| mean reciprocal rank | **0.753** | >= 0.60 |
| non-empty rendered context | **12/12** | 12/12 |

**Stage A: PASS.**

Per-query first relevant rank:

| case | rank |
|---|---:|
| North Star | 1 |
| initial research question | 1 |
| convergence rule | 1 |
| E013 minima | 2 |
| W0/X1 shadow boundary | 2 |
| temporal semantics | 3 |
| exact provenance | 1 |
| canonical JSONL | 1 |
| VS Code-first architecture | 1 |
| answer authority | 2 |
| manifest-loss containment | 1 |
| exact-Luna discovery tooling | 5 |

This is the first formal evidence that the project can ingest **itself** and recover the project's own architecture/decision knowledge with the current default lexical retrieval floor.

## Product-surface findings

The same run found concrete customer-readiness blockers that the Alpha Core tests do not measure.

### P1 — original source navigation is ambiguous

- duplicate basename groups in the repository: **22**;
- `README.md` occurs **14** times;
- several experiment filenames repeat 4–9 times;
- canonical ingest records preserve no original relative path/URI field;
- the current VS Code ingest path does not supply an alternate local locator.

Therefore a search result can preserve exact immutable raw evidence while still failing the ordinary customer question: **“which file in my workspace did this come from?”**

This is a product/provenance-navigation gap, not a raw-integrity failure. Any fix must keep path/location metadata separate from evidence identity and must not turn paths into trust/corroboration signals.

### P2 — temporal trust semantics are core-only

The core implements explicit correction, change-with-`effective_at`, and dispute semantics, but the installed VS Code command surface exposes none of them.

A first-class VS Code product cannot claim those semantics as usable product behavior if the user must escape to lower-level code/CLI plumbing to express them.

### P3 — customer feedback is not first-class in VS Code

E013 supports fixed-code `helpful` / `not_helpful` feedback, but the VS Code command surface does not expose it. Natural product-quality evidence will therefore be under-collected unless this is made easy during real Ask/search use.

### P4 — forgotten-topic recovery is missing from VS Code

Normal VS Code Search requires a selected topic. There is no explicit cross-topic discovery command.

The product currently assumes the user remembers where knowledge was filed. That assumption directly conflicts with a core product promise: recovering previously learned information after the user has forgotten its location.

A safe fix should preserve topic-current semantics rather than simply using the CLI's unscoped all-history view.

### P5 — valuable local knowledge has no primary backup/restore story

The local Wiki is deliberately outside Git and private-by-default, but the primary user docs do not yet provide a minimal backup/restore operating procedure.

Fail-closed corruption detection is not the same as recovery from disk loss or accidental directory deletion.

### P6 — real Copilot/Luna product path remains untested

The repository has zero-generation exact-Luna discovery tooling, but CI cannot claim the user's Copilot Pro entitlement or real VS Code model availability.

The existing Issue #24 real-session gate remains required:

1. run discovery in the user's real VS Code/Copilot Pro session;
2. require exact `gpt-5.6-luna` id/family, no fuzzy substitution;
3. if exact Luna is available, allow at most two tiny synthetic generation calls for the native-adapter smoke;
4. then run a small consented Ask flow on non-sensitive evidence.

### P7 — repeated customer-like use remains untested

One deterministic full-repo run proves retrieval capability, not habitability.

The product still needs repeated real sessions covering capture → leave → recall later → inspect source → update/correct/dispute → feedback → continued use.

## Decision

**Do not call the current build customer-ready.**

Call it a **trustworthy Alpha/dogfood product** whose default retrieval floor successfully self-hosts the repository, with concrete product blockers now identified.

The next work should fix P1–P5 narrowly, then run the real-session P6 gate and repeated-use P7 dogfood. This does **not** reopen open-ended core infrastructure work.
