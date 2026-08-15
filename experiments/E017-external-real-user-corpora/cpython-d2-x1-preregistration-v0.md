# E017-D2 — CPython X1 follow-up

Status: **PREREGISTERED BEFORE D2 MODEL SCORING**  
Date: 2026-08-15 KST  
Parent: #96 / E017 first pass `31864222594`

## Observed first-pass failure

The frozen CPython user question asked three things at once:

> In the current CPython documentation, what is the default `multiprocessing` start method on POSIX, why was the default changed away from `fork`, and what warning or caveat applies if I explicitly use `fork` from a multithreaded process?

W0 selected the correct CPython topic but its rendered context did not establish the current global `multiprocessing` default. The real Luna answer therefore stopped cautiously and only established the `ProcessPoolExecutor` default plus a general multithreaded-fork deadlock caveat. Citations resolved.

Zero-model inspection of the same corpus/query showed X1 materially improves the evidence:

- it includes `multiprocessing.rst`: POSIX default changed from `fork` to `forkserver` to retain performance while avoiding common multithreaded-process incompatibilities;
- it includes the Python 3.14 change note that Unix/POSIX default is now `forkserver` and `fork` must be requested explicitly;
- but it still does **not** include the nearby `multiprocessing.rst` paragraph stating that, since 3.12, detected multiple threads cause the internal `os.fork()` call to raise `DeprecationWarning`.

The exact source proves all three facts exist in the same long reStructuredText document. X1 falls back to paragraph structure because its structural parser recognizes Markdown `#` headings, not reStructuredText underline headings, and currently keeps only one best structural unit per immutable object plus one neighbor.

## D2 question

Use the **same frozen user question**. Do not rewrite it to make X1 look better.

## D2 candidate

- same CPython revision `07624ef11b924b39da97e978536f34f740e39575`;
- same `Doc/**/*.rst` corpus and file-size boundary as E017;
- X1 (`structural_expand_v1`) supplies the answer context;
- exact `gpt-5.6-luna`;
- exactly **one** new model call;
- 30-credit per-call guard;
- no semantic reroll;
- citation-handle validation/materialization stays active;
- no canonical mutation.

## Interpretation gate

D2 is a **partial-repair test**, not an all-or-nothing benchmark.

Evidence for X1 repair requires the final answer to correctly recover all of:

1. POSIX default is `forkserver`;
2. the change happened in Python 3.14 / `fork` is no longer the default;
3. rationale is retaining performance while avoiding common multithreaded-process incompatibilities / safer behavior than plain fork.

Because the X1 context still lacks the exact `DeprecationWarning` paragraph, the answer must **not invent** that exact warning from outside supplied evidence. It may give the supported multithreaded-fork caveat or explicitly say the exact runtime warning is not established by the supplied context.

All emitted citations must resolve and integrity must remain clean.

A D2 repair does **not** promote X1 globally. A partial repair plus missing warning is specifically evidence for a remaining non-Markdown / multi-aspect same-object context limitation.
