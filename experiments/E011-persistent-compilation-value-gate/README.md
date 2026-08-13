# E011 — Persistent Compilation Value Gate

Status: **Stage 1A frozen / ready for managed-environment preflight**

Question: under what workloads, if any, does persistent LLM-derived synthesis create enough reusable value to justify its lifecycle cost over raw evidence plus retrieval?

Stage 1A compares:

- `R0`: raw + topic-scoped BM25 top-k=12
- `R1`: all raw topic context
- `C0`: minimal durable topic synthesis only
- `C1`: the same synthesis + the same R0 raw evidence

The experiment uses 12 paired fictional topic scenarios, two nested corpus scales, and three fixed query classes. Reuse economics are frozen at N=1/3/10 and are replayed from measured build/query cost rather than repeated identical calls.

See `preregistration-v0.md`, `pre-scoring-red-team-v0.md`, `retrieval-red-team-amendment-v1.md`, and `pre-run-freeze-v0.md`.

A negative result is a successful gate outcome. Detailed Wiki representation and Stage 1B maintenance work remain blocked until persistent compilation first demonstrates a credible value region.
