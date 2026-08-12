# Project Charter

## 1. Mission

Design and validate a personal LLM Wiki that can accumulate useful knowledge over long periods without quietly degrading into an opaque collection of stale, duplicated, or hallucinated documents.

The target usage environment is primarily:

- VS Code
- Git/GitHub
- GitHub Copilot
- Markdown-first local files

Additional infrastructure such as embeddings, databases, knowledge graphs, MCP servers, or scheduled maintenance may be introduced only when there is a demonstrated need.

## 2. What we are optimizing for

The system should improve a person's ability to:

1. recover previously learned information,
2. understand relationships across sources and time,
3. preserve why a belief or decision was formed,
4. notice when knowledge has become stale or contradicted,
5. reuse prior reasoning without blindly trusting prior LLM output,
6. inspect and repair the system when it makes mistakes.

Convenience matters, but trustworthy compounding is the primary objective.

## 3. Non-goals for the initial phase

We are not yet trying to:

- build a polished PKM application,
- maximize ingestion volume,
- create a universal ontology,
- automate every maintenance action,
- choose a vector database,
- build a graph database,
- optimize for multi-user collaboration,
- preserve every conversation forever,
- produce an autonomous agent that mutates the wiki without review.

These may become later research questions.

## 4. Threat model

The wiki can fail even when every individual action looks reasonable.

### T1. Recursive contamination

An unsupported LLM synthesis becomes an input to later synthesis and gradually acquires the appearance of fact.

### T2. Premature overwrite

New evidence replaces older information even when the older state remains historically relevant or the evidence is not truly contradictory.

### T3. Stale truth

A once-correct statement remains canonical after the world, project, preference, or evidence changes.

### T4. Taxonomy drift

Classification rules change over time, leaving duplicated concepts, abandoned branches, ambiguous names, and inconsistent navigation.

### T5. Destructive maintenance

A cleanup pass deletes evidence, context, minority views, or historical reasoning that later proves useful.

### T6. Summary collapse

Repeated compression removes qualifiers, dates, uncertainty, or source-specific differences until only a misleading generic summary remains.

### T7. False precision

Confidence scores, metadata, or structural form give uncertain LLM output an unjustified appearance of certainty.

### T8. Retrieval blindness

A useful fact exists but routing, indexing, chunking, naming, or summarization prevents the model from finding it.

### T9. Maintenance debt

The wiki grows faster than it can be reconciled, reviewed, linked, or cleaned.

### T10. Automation complacency

Because the system usually works, users stop inspecting changes and rare errors compound for long periods.

## 5. Design principles — provisional, not yet policies

These are starting hypotheses to test.

### P-H1. Preserve primary evidence

Raw source material should normally be immutable or append-only. A synthesis should be replaceable; its evidence should not be.

### P-H2. Separate evidence from derived knowledge

Primary sources, observations, LLM-derived summaries, personal interpretations, and decisions should not silently share the same epistemic status.

### P-H3. Prefer reversible operations

Supersede, archive, redirect, split, and merge should generally be preferred over irreversible deletion until deletion policy is validated.

### P-H4. Consolidate deliberately

Immediate rewrite after every new observation may create churn. A staging/buffer layer and explicit consolidation process may be safer.

### P-H5. Retrieval should be progressive

Start from indexes or summaries and drill toward detail and sources when the query requires precision or verification.

### P-H6. Maintenance needs diagnostics

Broken links, unsupported claims, duplicate topics, oversized pages, ambiguous naming, stale statements, and unresolved contradictions should be detectable rather than merely left to intuition.

### P-H7. The librarian must learn from failures

Repeated failure modes should become explicit rules, tests, or an error book rather than being corrected only once.

### P-H8. Human review should be risk-sensitive

Not every change needs the same approval burden. Destructive, high-impact, or evidence-changing operations should receive more scrutiny than additive low-risk changes.

## 6. Success criteria

A mature candidate architecture should demonstrate, on a repeatable evaluation corpus:

- high factual faithfulness to source material,
- good retrieval of both broad concepts and exact details,
- correct handling of temporal updates and contradictions,
- low duplicate/fragmentation rate,
- recoverability from intentionally injected errors,
- inspectable provenance,
- manageable maintenance cost,
- useful answers under realistic VS Code + Copilot workflows.

No single score will be treated as sufficient.

## 7. Decision discipline

A design choice becomes a project policy only when recorded in an ADR.

Every ADR should contain:

- context,
- competing alternatives,
- evidence or experiment results,
- chosen decision,
- known trade-offs,
- expected failure modes,
- reversal or re-evaluation conditions.

The absence of an ADR means the behavior remains provisional.

## 8. Initial research question

> What is the minimum architecture and operating discipline required for an LLM-assisted personal knowledge base to compound useful understanding faster than it compounds error and maintenance debt?
