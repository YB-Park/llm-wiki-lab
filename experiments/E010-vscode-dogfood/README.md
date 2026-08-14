# E010 — VS Code dogfood and self-hosting product gate

Status: **PREREGISTERED / ACTIVE**

## Question

Has the project progressed from a trustworthy core to a product we could responsibly hand to a real VS Code + GitHub Copilot user?

A core that survives deterministic tests is necessary but not sufficient. A customer-facing LLM Wiki must also prove that it can ingest and recover its own project knowledge, expose its trust semantics through the first-class VS Code surface, and complete at least one real Copilot session without hidden model substitution.

## Product-level hypothesis

The current Alpha Core should be strong enough to support real dogfood, but the product is **not presumed customer-ready**. This gate is intentionally allowed to fail even when all Alpha invariants remain green.

## Stage A — full-repository self-dogfood (automated, zero model calls)

The harness ingests every Git-tracked regular file in the checked-out repository that:

- decodes as UTF-8;
- contains no NUL byte;
- is not the generated local Wiki/result output itself.

All accepted files are ingested into one local project topic using the same raw-first core shipped to the VS Code extension. Binary/non-UTF-8 files are counted and skipped rather than silently converted.

The harness then asks a preregistered set of project questions covering:

- North Star / convergence;
- project charter;
- E013 and E015 gates;
- temporal correction/change/dispute semantics;
- exact provenance;
- canonical JSONL crash containment;
- VS Code-first/editor-agnostic architecture;
- read-only model-answer authority;
- missing canonical-history containment.

For each question it records whether at least one expected tracked source appears in top-5 W0 retrieval, first relevant rank, and reciprocal rank. It also renders context to ensure the result is consumable at the answer boundary.

This experiment evaluates **our own repository as our own Wiki corpus**. It does not use a synthetic mini-corpus as a substitute.

### Stage A preregistered signal

- target-source top-5 hit rate >= 0.90;
- mean reciprocal rank >= 0.60;
- every query renders non-empty provenance-preserving context;
- corpus coverage and skipped-file counts are explicit.

These thresholds are a product signal, not a new Alpha invariant. Failure does not justify arbitrary retrieval complexity; it identifies a concrete dogfood problem to diagnose.

## Stage B — source-navigation and product-surface audit (automated, zero model calls)

A real customer must be able to understand *where evidence came from* and perform the trust-sensitive operations the core already models.

The harness therefore reports, without pretending these are retrieval metrics:

1. duplicate basenames in the ingested repository;
2. whether user-visible search provenance can uniquely identify the original tracked path when basenames collide;
3. whether the VS Code command surface exposes correction/change/dispute semantics;
4. whether VS Code exposes explicit helpful/not-helpful feedback collection already supported by E013;
5. whether VS Code provides a recall path when the user does not remember/select the topic first;
6. whether there is a documented backup/restore story before valuable personal knowledge is entrusted to the local store.

These are product questions. A CLI-only capability does not count as first-class VS Code product coverage.

## Stage C — real VS Code + Copilot Pro / exact Luna gate (requires real user session)

Automation cannot claim this gate from GitHub Actions.

The installed VSIX must be exercised in a real user-initiated VS Code session with GitHub Copilot Pro:

1. run `LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)`;
2. confirm sanitized discovery reports an **exact** `id` or `family` equal to `gpt-5.6-luna`;
3. if exact Luna is unavailable, keep the validated CLI adapter and record the product limitation; do not substitute another model silently;
4. if exact Luna is available, run at most **2 tiny synthetic generation calls** through the candidate VS Code-native adapter before deciding whether to keep it;
5. then run a small customer-like Ask flow on non-sensitive project evidence only after explicit consent.

Paid/model budget is spent here because this gate is specifically about model/product behavior. It must not be spent merely to re-test deterministic storage or retrieval.

## Stage D — customer-like use loop

Before calling the product customer-ready, use the installed VSIX across multiple real sessions for the loop below:

```text
capture evidence
  -> ingest
  -> leave the session
  -> recover it later
  -> ask / inspect provenance
  -> update or correct knowledge
  -> observe disagreement/history when relevant
  -> give feedback
  -> recover from an integrity/operational problem without losing trusted data
```

Record friction, avoided actions, terminal escapes, wrong or unhelpful answers, provenance follows, and corrections. E013/E015 natural telemetry remains the architecture evidence stream; do not manufacture events to satisfy sample minima.

## Customer-readiness gate

`CUSTOMER_READY_CANDIDATE` requires all of the following:

- Alpha Core trust/integrity remains green;
- Stage A self-repo retrieval signal passes;
- original evidence can be identified/navigated without ambiguous basename-only provenance in realistic workspace use;
- core correction/change/dispute semantics are operable from the first-class VS Code surface when needed;
- customer feedback can be captured without requiring a terminal;
- cross-topic / forgotten-topic recovery has an acceptable VS Code story;
- a minimal backup/restore operating story exists for valuable local knowledge;
- Stage C has real-session evidence for the actual Copilot/model path used by the product;
- Stage D has repeated real-session evidence that the Wiki is useful enough to keep using.

Until these are true, call the system **dogfood/Alpha**, not a customer-ready product.

## Guardrail

A failed product gate is not permission to restart open-ended core architecture work. Fix the smallest observed product blocker, retest, and keep the convergence rule active.
