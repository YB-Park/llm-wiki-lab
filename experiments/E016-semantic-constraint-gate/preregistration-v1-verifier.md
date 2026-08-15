# E016 — read-only verifier V1 preregistration

Status: **PREREGISTERED BEFORE VERIFIER SCORING**  
Date: 2026-08-15 KST

## Entry evidence

The observed E015 answer failure survived:

1. ordinary one-call answering twice;
2. stronger prose negative-constraint prompting;
3. a one-call structured `supported / forbidden / insufficient` extraction gate (S1).

S1 failed before its control set, so S2 was not run.

## V1 question

Can a **separate read-only Luna verifier call** reliably identify the exact observed forbidden/unsupported claims when given:

- the user's E015 question;
- the current retrieved Wiki evidence context, which must contain the literal E015 limitation `E015 is not a quality proof` before the verifier call is allowed;
- the exact frozen failing S1 draft answer/constraint payload;
- no tools and no ability to mutate canonical state?

## Frozen failing draft

The verifier receives the exact S1 user-facing draft:

> `structural_expand_v1` is not yet the default because E014-R1 established an advantage only on a fresh synthetic stressed-mechanism corpus, plus production-core equivalence; it did not show that the mechanism matters often in natural use. E015 can therefore provide evidence about real-use frequency **and quality** only if its actual design and results measure those questions. The supplied evidence does not include E015's protocol, results, or threshold, so it cannot establish that E015 passed, justify a default switch, or quantify production benefit.

The frozen structured fields are stored separately as fixture data. No draft regeneration call is permitted in V1.

## V1 verifier output contract

Return exactly one JSON object:

```json
{
  "verdict": "ACCEPT or REJECT",
  "unsupported_or_forbidden_claims": [],
  "evidence_misreadings": [],
  "missing_required_limitations": [],
  "reason": "..."
}
```

The verifier must cite Wiki evidence handles in its `reason` or finding strings. Product citation-handle validation/materialization remains active.

## V1 GO

One verifier call passes only if all hold:

1. exact model is `gpt-5.6-luna`;
2. verdict is `REJECT`;
3. the verifier identifies the **quality** overclaim as unsupported/forbidden because E015 is explicitly not a quality proof / cannot determine which mode is correct;
4. it identifies the draft's claim that E015 evidence/protocol is absent as an evidence misreading, because the E015 preregistration is actually in context;
5. materialized citations resolve through `source show`;
6. no canonical mutation or semantic reroll occurs.

## V1 KILL

Any `ACCEPT`, failure to flag the quality overclaim, failure to notice the false `evidence absent` assertion, unusable structured output, or citation failure kills this verifier candidate. If V1 fails, do not spend control calls.

## V2 controls — only after V1 GO

Four verifier calls, no draft-generation calls:

1. ordinary positive supported draft — must ACCEPT;
2. explicit insufficient-evidence draft — must ACCEPT the refusal/insufficiency;
3. correct correction-vs-change draft — must ACCEPT;
4. correct unresolved-dispute draft — must ACCEPT.

Primary V2 purpose is false-refusal detection. A verifier that catches bad drafts but rejects useful good answers does not earn product integration.

## Cost / execution boundary

- V1: exactly **1** Luna verifier call;
- V2: exactly 4 only after V1 GO;
- per-call CLI guard: 30 AI credits;
- no draft-generation calls inside verifier stages;
- no rerolls;
- no company/private evidence;
- no tools, no canonical mutation;
- current retrieval/provenance/citation-handle behavior unchanged.

Even V1+V2 success does not automatically ship a verifier. It only earns a product-integration candidate whose extra latency/cost must be explicit and whose user-facing fail behavior must remain inspectable.
