# E017 — external-corpus real-user dogfood

Status: **PREREGISTERED BEFORE MODEL SCORING**  
Date: 2026-08-15 KST  
Issue: #96

## Purpose

Use the current LLM Wiki as a user on unfamiliar public knowledge, not on this repository's own project history.

This is not a benchmark leaderboard. The question is whether the product remains useful and inspectable when the corpus is large, externally authored, structurally different, and/or temporally distributed.

## Cost boundary

- exact model: `gpt-5.6-luna`;
- first pass: exactly **3** model-call attempts, one per corpus;
- per-call guard: **30 AI credits**;
- no semantic rerolls;
- W0/default is the user-visible Ask path;
- W0 and X1 rendered contexts are compared with **zero additional model calls** before each Ask;
- if a first-pass failure has a clear deterministic context root cause, only a narrow follow-up may be considered; do not replay all three cases.

## Corpus A — Kubernetes documentation

Source: `kubernetes/website` at commit `551b56f979e1e020bd5ebd6ca1b8da7f32d02ae0`.

Scope: official English `content/en/docs/**/*.md`, excluding generated `content/en/docs/reference/kubernetes-api/**` and unusually large files above the runner safety cap.

Question:

> I set a PodDisruptionBudget with `maxUnavailable: 0`. Does that guarantee zero downtime even if a node crashes or another involuntary disruption happens? Explain what a PDB actually protects against, what it cannot prevent, and any important caveats about voluntary disruptions.

Why this is useful: the corpus contains both API/reference wording and higher-level caveats. A plausible but wrong answer can easily overstate what `maxUnavailable: 0` guarantees.

Expected concepts for later manual/diagnostic scoring, not shown to the model:

- zero means zero **voluntary evictions** through PDB-respecting eviction flows;
- a PDB does not guarantee the replicas are always available and cannot prevent involuntary disruption such as node failure;
- some nominally voluntary actions can bypass PDBs (for example direct deletion / controller changes), so wording must not imply universal protection.

## Corpus B — CPython documentation

Source: `python/cpython` at commit `07624ef11b924b39da97e978536f34f740e39575`.

Scope: official `Doc/**/*.rst`, excluding unusually large files above the runner safety cap.

Question:

> In the current CPython documentation, what is the default `multiprocessing` start method on POSIX, why was the default changed away from `fork`, and what warning/caveat applies if I explicitly use `fork` from a multithreaded process?

Why this is useful: this is a version-sensitive truth that changed in Python 3.14, and the corpus is reStructuredText rather than Markdown. It tests current-vs-old knowledge and format robustness together.

Expected concepts:

- POSIX default is `forkserver` in current docs / changed in 3.14;
- rationale is to retain useful performance while avoiding common multithreaded-process incompatibilities of `fork`;
- `fork` is no longer default on any platform and must be requested explicitly where required;
- `os.fork()` used by that start method can raise `DeprecationWarning` when Python detects multiple threads (documented since 3.12).

## Corpus C — NASA Artemis II article stream

Source: a fixed URL list of official `nasa.gov` Artemis II news releases and mission-update pages captured during the run. The runner records URL, fetch status, raw HTML SHA-256, normalized-text SHA-256, and title. No third-party news is used.

Question:

> Reconstruct the Artemis II timeline from launch through leaving Earth orbit to splashdown. Give dates/times only where the captured NASA articles support them, and identify any later editor correction/update in the corpus without turning that update into a different mission event.

Why this is useful: unlike a code/documentation repository, this knowledge is distributed across dated article updates. It tests temporal synthesis, cautious handling of editor corrections, and multi-source provenance.

Expected concepts:

- launch on April 1, 2026, with the supported launch time if retrieved;
- translunar injection / departure from Earth orbit on April 2, 2026;
- splashdown on April 10, 2026, with the supported splashdown time if retrieved;
- the return release carries an editor note dated May 7, 2026 about correcting/reflecting the official miles flown; the May 7 note is not a new flight event.

## Evaluation

For each case preserve:

1. corpus file/byte counts and immutable external revision or captured-content hashes;
2. forgotten-topic `discover` result;
3. W0 top hits and rendered context;
4. X1 top hits and rendered context, zero model calls;
5. exact Luna answer via the ordinary W0 `ask` path;
6. materialized citation IDs and whether each resolves through `source show`;
7. model/usage telemetry where available;
8. final Wiki integrity.

Automatic keyword checks are only diagnostics. The assistant must manually read the actual answers and exact contexts before assigning the product verdict.

## Stop rule

The first pass stops after the three frozen calls even if a case fails. A follow-up call is justified only when it tests one specific observed mechanism and can change a product decision. Otherwise preserve the failure and continue natural dogfood instead of spending credits to make the score prettier.
