# E009A corpus red-team amendment v1

Status: **pre-scoring corpus correction; no scored verifier output had been generated when this amendment was made.**

## Trigger

The preregistered pre-scoring red-team review warned that safe candidates could accidentally be longer or more detailed than unsafe candidates, allowing a verifier to predict the gold label from surface form rather than transition semantics.

A deterministic surface audit of Corpus T-v0 found exactly that failure:

- candidate UTF-8 byte length alone achieved best one-dimensional threshold accuracy **0.925** against the 20/20 gold labels;
- mean candidate bytes: safe 188.0 vs unsafe 102.8;
- all **20/20** paired scenarios had the safe candidate longer than the unsafe candidate;
- line count and source-mention count each also reached 0.675 best one-dimensional threshold accuracy.

The paired semantic design was therefore compromised by a trivial verbosity cue.

## Decision

Corpus T-v0 is retained in Git history but is **not eligible for scored use**.

Create Corpus T-v1 before any scored verifier call by editing candidate text only. Previous state, new evidence, gold semantics, case IDs, scenario grouping, and the 20/20 safe/unsafe balance remain conceptually fixed.

## Rebalancing principles

Do not merely pad strings to hit a numeric target. Make the counterexamples realistic:

- some **unsafe** candidates should be polished, detailed, source-rich, and longer while containing a subtle semantic defect;
- some **safe** candidates should be concise but fully preserve the required meaning;
- large diffs must exist on both labels;
- source citations may legitimately differ in provenance-loss cases, but citation density must not become a corpus-wide label shortcut;
- unsafe candidates should include both omission failures and additive/invented failures so `more text = safer` is false;
- safe candidates may legitimately delete/rewrite invalidated or redundant wording so `preserve more text = safer` is false.

## Acceptance before scoring

Rerun the deterministic surface audit after T-v1.

No single threshold is treated as a formal benchmark, but the corpus is not frozen if there remains an obvious near-deterministic shortcut such as T-v0's 0.925 byte-length classifier or a near-unidirectional pair-length pattern.

The audit result itself is not model performance and may be used to improve the corpus because no scored model judgment has yet been inspected.

## Frozen elements unaffected

- research question;
- A0-A4 policy semantics;
- verifier prompt objectives;
- 40-case / 20-scenario paired design;
- safe/unsafe labels and intended semantic fault classes;
- model choice for the first block;
- two-pass judgment design;
- primary reporting metrics.

The 80-call order may remain the same because case IDs are unchanged, but its corpus identifier/hash must be updated to T-v1 before scoring.
