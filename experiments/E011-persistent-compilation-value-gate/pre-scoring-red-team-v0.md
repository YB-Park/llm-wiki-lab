# E011 Stage 1A pre-scoring red-team v0

Status: **before corpus freeze and before all scored model calls**

## Purpose

Try to make the Value Gate fail honestly before spending inference on it.

## Threat 1 — trivial amortization

R1 re-reads all topic raw documents for every query, while C0 pays one build cost. At sufficiently high reuse, C0 can become cheaper almost by arithmetic.

Mitigation: R0 lexical is a serious low-cost raw competitor; the final frontier compares all four conditions. Report N=1,3,10 separately. A late break-even against R1 alone does not justify compilation.

## Threat 2 — free topic routing for compilation

C0/C1 receive all documents assigned to a topic. This is an oracle-like organizational assumption if a real system would first need to discover topic membership.

Mitigation: R1 receives the same topic grouping. Interpret R1-vs-C0 as a controlled precompute comparison, not end-to-end production architecture. Realistic workload validation must later include routing/organization cost.

## Threat 3 — same-model self-consistency

The same model family builds the synthesis and later answers from it. The compiled artifact may be unusually easy for that model to consume.

Mitigation: label all Stage 1A conclusions model-conditional. A headline architecture conclusion requires a replication that changes the build or answer model axis.

## Threat 4 — benchmark shaped like a summary

Global and decision-rationale questions can accidentally reward exactly the prose structure a topic summary produces.

Mitigation: include exact/provenance questions where raw retrieval should be competitive or superior. Keep query-class conclusions separate. A win only on global/high-reuse workloads supports selective compilation, not a universal Wiki.

## Threat 5 — lexical baseline tuning

Choosing top-k after observing model answers can manufacture the desired R0 strength.

Mitigation: choose and freeze tokenizer, ranking, tie-break, and top-k using corpus-only retrieval diagnostics before scored answer calls. Do not tune on answer quality.

## Threat 6 — templated synthetic corpus

Generated scenarios may contain repeated structural patterns that make synthesis or answering easier than realistic personal material.

Mitigation: treat Stage 1A as controlled benchmark evidence. A surviving value region must later face a materially different realistic/shadow workload.

## Threat 7 — nested scales are dependent

Large scale contains the small core plus added material. Small and large rows are not independent samples.

Mitigation: topic scenario remains the uncertainty cluster. Scale is a paired within-topic factor.

## Threat 8 — build quality is itself a hidden variable

A poor compiled artifact can make compilation look bad; an over-engineered compiler prompt can make it look artificially good.

Mitigation: use one minimal generic topic-synthesis prompt with source IDs and no query access. No verifier, repair, recursive rewrite, or question-specific optimization in Stage 1A.

## Threat 9 — token value is not human utility

Fewer tokens or fewer raw documents shown to the model does not prove better human understanding.

Mitigation: call these cost/navigation proxies. Stage 1A cannot replace later realistic measures of rediscovery time, decision recovery, verification effort, and subjective usefulness.

## Threat 10 — static win may vanish under maintenance

Stage 1A charges build cost but no update/staleness/review cost.

Mitigation: a static win is necessary but not sufficient. Only a surviving region may proceed to Stage 1B maintenance stress.

## Stop rule

Do not add more representation complexity to rescue a losing compiled condition. If the minimal compiled candidates are dominated at the frozen reuse regimes, record the negative result and pivot the default hypothesis toward raw + retrieval + selective/on-demand synthesis.
