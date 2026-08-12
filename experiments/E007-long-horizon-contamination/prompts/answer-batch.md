Answer the provided fictional knowledge questions using **only** the evidence context below.

Do not use outside knowledge. If the evidence does not establish an answer, say that it is unknown, unsupported, ambiguous, or disputed as appropriate rather than guessing.

For time-sensitive questions, distinguish historical state from current state. For provenance questions, name source IDs only when they are present in the evidence context.

Return JSON only with this shape:

{
  "answers": [
    {
      "query_id": "Q...",
      "answer": "concise answer",
      "source_ids": ["S..."],
      "uncertainty": "none | unknown | unsupported | ambiguous | disputed"
    }
  ]
}

Return exactly one answer object for each supplied query_id and preserve query order.

## Evidence context

{{EVIDENCE}}

## Questions

{{QUESTIONS}}
