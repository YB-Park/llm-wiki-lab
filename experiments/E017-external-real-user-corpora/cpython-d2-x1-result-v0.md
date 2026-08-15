# E017-D2 — CPython X1 partial-repair result

Status: **PASS / MATERIAL PARTIAL REPAIR / REMAINING FORMAT-MULTI-ASPECT LIMIT**  
Date: 2026-08-15 KST  
Workflow: `31864607654`  
Artifact: `9241625353`  
Main commit: `87060c336413e08c9f37eefc52acac7c04f67c42`

## Frozen question

> In the current CPython documentation, what is the default `multiprocessing` start method on POSIX, why was the default changed away from `fork`, and what warning or caveat applies if I explicitly use `fork` from a multithreaded process?

D2 used the same pinned CPython revision and the same user question as the failed W0 first pass. Only answer context changed from W0 to `structural_expand_v1`.

Exactly **one** new `gpt-5.6-luna` call was made. No semantic reroll.

## Frozen X1 evidence boundary before the call

The D2 preflight rebuilt all 557 pinned CPython `Doc/**/*.rst` files with zero model calls and asserted:

- X1 context contains `forkserver`;
- X1 contains the current POSIX default-change statement;
- X1 contains the multithreaded-incompatibility rationale;
- X1 **does not contain** the exact `DeprecationWarning` paragraph from `multiprocessing.rst`.

The source itself contains all of these facts. The missing warning is therefore a context-selection limitation rather than missing corpus evidence.

## Real-Luna answer

The D2 answer correctly recovered:

- **Default:** POSIX now uses **`forkserver`**;
- **Version:** this is the Python **3.14** change away from `fork`;
- **Rationale:** retain much of `fork`'s performance while avoiding common multithreaded-process incompatibilities;
- **Explicit-fork caveat:** fork is threading-incompatible / should be done from the main thread, and must be requested explicitly where needed.

Representative answer:

> On POSIX systems, the default is now `forkserver` (since Python 3.14), replacing `fork`.

> `forkserver` retains much of `fork`'s performance while avoiding common incompatibilities with multithreaded processes.

Crucially, because the X1 context did not contain the exact 3.12 `DeprecationWarning` paragraph, Luna did **not** fabricate it. It instead said the supplied documentation did not establish that every explicit use of `fork` emits a warning.

Four canonical citations resolved through `source show`; exact model identity passed; final Alpha integrity was clean.

## Comparison with W0

The W0 first-pass answer could not establish the global current `multiprocessing` default and retreated to the `ProcessPoolExecutor` default.

X1 therefore produced a **material user-visible repair** on the same external corpus and same frozen question.

This is independent of the earlier project-repo E015-D1 case and broadens the evidence that structural/context granularity is a real product issue rather than only a synthetic-corpus artifact.

## Remaining limitation

D2 is intentionally classified **partial repair**, not proof that X1 fully solves CPython-style documentation.

`multiprocessing.rst` is reStructuredText. The current structural splitter recognizes Markdown `#` headings, so this `.rst` document falls back to paragraph units. X1 currently selects one best structural unit per immutable object and expands by only one neighboring paragraph.

The frozen question needs facts from multiple separated parts of the same long `multiprocessing.rst` object:

- the current default/rationale paragraph;
- the earlier `fork` / multiple-threads warning paragraph.

X1 chose the current default/rationale area and therefore still omitted the exact warning.

This creates a concrete future hypothesis: non-Markdown structure awareness and/or allowing multiple relevant units from the same long object may matter for multi-aspect questions. Do **not** turn that observation directly into a new parser/index stack without additional real cases.

## Decision

- Count D2 as a second independent **real-user case where X1 materially improves W0 context quality**, but only a partial repair.
- Do not globally promote X1 from E015-D1 + E017-D2 alone.
- Keep collecting natural divergent cases.
- If non-Markdown / multi-aspect same-object misses recur, then test the smallest candidate that can recover multiple relevant regions without exploding context or index cost.
- No further paid calls are justified for this frozen CPython case.
