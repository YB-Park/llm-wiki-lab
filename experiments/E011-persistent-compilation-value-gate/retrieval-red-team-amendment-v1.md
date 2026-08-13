# E011 retrieval red-team amendment v1

Status: **pre-scoring; no E011 answer-model result observed**

The preregistration initially named top-k=6 as a candidate. Corpus-only retrieval diagnostics showed that this made the large-scale lexical baseline obviously brittle on global queries because administrative lexical distractors could fill all six slots.

To avoid manufacturing an easy compiled win, Stage 1A freezes a stronger R0/C1 raw retrieval policy:

- deterministically identify the topic scope already available to all conditions;
- run BM25 only within that topic scope;
- use `top-k=12` with deterministic source-ID tie breaking;
- if the topic contains fewer than 12 documents, return all documents.

Prescore payload diagnostics with the frozen generator and BM25 logic:

- small exact/provenance: required-signal coverage 1.000; strict 12/12; approval source 12/12;
- small global synthesis: required-signal coverage 1.000; strict 12/12;
- small decision rationale: required-signal coverage 1.000; strict 12/12;
- large exact/provenance: required-signal coverage 1.000; strict 12/12; approval source 12/12;
- large global synthesis: required-signal coverage 1.000; strict 12/12;
- large decision rationale: required-signal coverage 0.250; strict 0/12.

Interpretation before scoring: R0 is not a weak baseline at small scale and remains evidence-complete for exact/global tasks at large scale. Its deliberate pressure point is large-scale multi-hop decision recovery, where lexical matching finds the decision/option vocabulary but not the distributed constraint names. This is a retrieval limitation to measure, not a defect to repair after answer scoring.

Consequences:

- at small scale (8 documents/topic), R0 sees the full topic corpus and is effectively as evidence-rich as R1;
- at large scale (32 documents/topic), R0 sees a strong 12-document lexical subset;
- C1 receives exactly the same lexical raw set as R0 plus the compiled artifact.

This choice was made from retrieval payload diagnostics only, before scored answer calls. Do not tune k from answer quality later.
