# E011 retrieval red-team amendment v1

Status: **pre-scoring; no E011 answer-model result observed**

The preregistration initially named top-k=6 as a candidate. Corpus-only retrieval diagnostics showed that this made the large-scale lexical baseline obviously brittle on global queries because administrative lexical distractors could fill all six slots.

To avoid manufacturing an easy compiled win, Stage 1A freezes a stronger R0/C1 raw retrieval policy:

- deterministically identify the topic scope already available to all conditions;
- run BM25 only within that topic scope;
- use `top-k=12` with deterministic source-ID tie breaking;
- if the topic contains fewer than 12 documents, return all documents.

Consequences:

- at small scale (8 documents/topic), R0 sees the full topic corpus and is effectively as evidence-rich as R1;
- at large scale (32 documents/topic), R0 sees a strong 12-document lexical subset;
- C1 receives exactly the same lexical raw set as R0 plus the compiled artifact.

This choice was made from retrieval payload diagnostics only, before scored answer calls. Do not tune k from answer quality later.
