Answer the question using only the supplied context. Do not use external knowledge.

Return exactly one JSON object with this shape:

{"answer":"string","source_ids":["source-id"],"uncertainty":"none|partial|unknown"}

Rules:
- `answer` should directly answer the question.
- `source_ids` must contain only source IDs visible in the context and should identify evidence used for the answer.
- use `partial` if the context supports only part of the requested answer;
- use `unknown` if the context does not establish the answer;
- do not invent missing facts or source IDs;
- output JSON only, with no Markdown fence or commentary.

QUESTION:
{{QUESTION}}

CONTEXT:
{{CONTEXT}}
