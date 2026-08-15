# E017 external-corpus real-user dogfood — first-pass result

Status: **2 MANUAL PASS / 1 CONTEXT-LIMITED FAIL / PRODUCT BUG FOUND AND FIXED**  
Date: 2026-08-15 KST  
Issue: #96  
Zero-model repaired preflight: `31864044817`  
Real-Luna run: `31864222594`  
Real-Luna artifact: `9241538528`

## Purpose

Test the current LLM Wiki as a user on unfamiliar public knowledge rather than this repository's own project history.

The three corpora were chosen to stress different product boundaries:

1. large Markdown documentation with important caveats;
2. large reStructuredText documentation with version-sensitive truth;
3. a dated official article stream requiring multi-source temporal synthesis.

The first pass used exactly **three** `gpt-5.6-luna` calls, one per frozen question, with no semantic rerolls. The artifact's OTEL files did not expose reliable token/cost totals, so this result does not invent a token count.

## Corpora

| corpus | frozen revision / capture | files | normalized bytes |
|---|---|---:|---:|
| Kubernetes official English docs | `kubernetes/website@551b56f979e1e020bd5ebd6ca1b8da7f32d02ae0` | 1,515 | 9,574,561 |
| CPython `Doc/**/*.rst` | `python/cpython@07624ef11b924b39da97e978536f34f740e39575` | 557 | 13,283,416 |
| NASA Artemis II official pages | 10 fixed official URLs, raw + normalized SHA-256 recorded at run | 10 | 96,486 |

The NASA capture represented about 2.9 MB of raw HTML before normalization.

## Preflight finding before any paid call — global discovery score bug

The first zero-model preflight exposed a real product defect before any Copilot spend.

The product previously ran BM25 separately inside each topic and the VS Code forgotten-topic flow sorted those **topic-local raw scores** as if they were globally comparable. With extremely uneven topic sizes (1,515 Kubernetes docs / 557 CPython docs / 10 NASA articles), the Artemis II question incorrectly selected the CPython topic.

That would have spent a model call on the wrong topic.

The fix merged with E017:

- gather only each topic's **current** evidence;
- deduplicate immutable content objects;
- score the current-object union once in one shared BM25 space;
- attach topic membership after scoring;
- leave topic-scoped W0 `search`, `context`, and `ask` unchanged;
- preserve current-only / no-E013-visit behavior.

A regression fixture first proves the old uneven-topic raw-score trap, then requires the shared-space discover path to choose the small correct topic.

Re-preflight `31864044817` used **zero model calls** and selected the intended topic for all three frozen questions. E010, E004, E014, E014-R1, Python/CLI, dev VS Code, bundled core, and packaged VSIX CI remained green.

## Case A — Kubernetes PDB

Question:

> I set a PodDisruptionBudget with `maxUnavailable: 0`. Does that guarantee zero downtime even if a node crashes or another involuntary disruption happens? Explain what a PDB actually protects against, what it cannot prevent, and any important caveats about voluntary disruptions.

### Manual verdict: **PASS**

The automatic keyword gate marked this case false because it looked for an unformatted substring such as `does not guarantee` while the answer emitted Markdown emphasis (`does **not** guarantee`). Manual review is authoritative for E017.

The real answer correctly said:

- `maxUnavailable: 0` does **not** guarantee zero downtime;
- PDB protects voluntary eviction / drain behavior from reducing healthy replicas below the budget;
- PDB cannot prevent involuntary disruption such as node crash/failure;
- a single-instance application may require an explicit operational agreement and temporary PDB removal to permit maintenance;
- the evidence does not establish uninterrupted service during failures.

Six canonical citations were emitted and all resolved through `source show`; final Wiki integrity was clean.

### W0 vs X1 observation

W0 already supplied enough evidence for a useful answer, so no paid X1 follow-up is justified here.

X1's zero-model context was nevertheless more coherent. In particular, it surfaced the Kubernetes priority/preemption section saying PDB support during preemption is best effort rather than absolute. This is useful descriptive evidence, but not a quality-labeled X1 win because W0 already answered correctly.

## Case B — CPython multiprocessing

Question:

> In the current CPython documentation, what is the default `multiprocessing` start method on POSIX, why was the default changed away from `fork`, and what warning or caveat applies if I explicitly use `fork` from a multithreaded process?

### First-pass W0 verdict: **FAIL AS A USER ANSWER / SAFE INSUFFICIENCY**

The real answer did **not** hallucinate a global default. It correctly said the supplied evidence did not fully establish the global `multiprocessing` default, then recovered only the `ProcessPoolExecutor` forkserver change plus a general multithreaded-fork deadlock caveat.

That caution is preferable to confident fabrication, but it still fails the user's actual question because the current CPython docs do contain the answer.

All three emitted citations resolved and integrity was clean.

### Root cause: context construction, not Luna overriding supplied truth

W0 had actually retrieved `Doc/library/multiprocessing.rst`, but its single best paragraph was an unrelated paragraph containing another use of the word `default`. The decisive start-method paragraphs were not present in the model context.

The same W0 context also surfaced:

- Python 3.12 prospective text saying the default **will** change in 3.14;
- Python 3.14 text about `ProcessPoolExecutor` specifically;
- a C-API fork/thread deadlock caveat.

So the model's refusal to claim the global current default was grounded in what the Wiki actually supplied.

Zero-model X1 context materially repaired this:

- `multiprocessing.rst`: POSIX default changed from `fork` to `forkserver` to retain performance while avoiding common multithreaded-process incompatibilities;
- Python 3.14 notes: Unix/POSIX default is now `forkserver`, `fork` must be requested explicitly.

But X1 still omitted the nearby 3.12 paragraph saying detected multiple threads cause the internal `os.fork()` call to raise `DeprecationWarning`.

This motivated the single-call D2 follow-up recorded separately in `cpython-d2-x1-result-v0.md`.

## Case C — NASA Artemis II article stream

Question:

> Reconstruct the Artemis II timeline from launch through leaving Earth orbit to splashdown. Give dates and times only where the captured NASA articles support them, and identify any later editor correction or update in the corpus without turning that update into a different mission event.

### Verdict: **PASS**

The real answer reconstructed:

- **April 1, 2026, 6:35 p.m. EDT** — launch from Kennedy Space Center;
- **April 2, 2026** — translunar injection / departure from Earth orbit, while explicitly refusing to invent an exact burn time absent from the captured evidence;
- **April 10, 2026, 5:07 p.m. PDT** — splashdown in the Pacific off California;
- **May 7, 2026** — later editor update correcting the official mileage figure, correctly treated as an editorial correction rather than a new mission event.

Four unique citations were used (some reused across claims), all resolved, and integrity was clean.

This is strong evidence that the raw-first/provenance boundary can support useful multi-document article synthesis with cautious precision.

## First-pass product verdict

The external-corpus pass was substantially more informative than another self-repo replay.

It demonstrated that:

- the product can ingest and query roughly 23 MB / 2,082 public text documents across very different corpus shapes;
- the original cross-topic discovery design had a real correctness bug under uneven topic sizes, and the zero-model preflight caught it before paid inference;
- Kubernetes caveat-heavy Markdown can produce a useful, non-overclaiming answer from W0;
- NASA dated article streams can produce a useful, provenance-grounded temporal reconstruction without turning an editor update into a mission event;
- CPython reStructuredText exposed a new retrieval/context boundary: W0 can retrieve the right long object but choose the wrong paragraph, and X1 can recover major facts while still losing a second distant aspect in the same object.

Do not interpret the first-pass `2/3` as a benchmark score. The mechanisms and inspectability matter more than the count.

## Cost decision

Exactly three real Luna calls were used in this first pass. No semantic rerolls were used. Only the CPython failure earned one narrow follow-up call because zero-model evidence showed X1 could materially change the answer and therefore inform a real retrieval decision.
