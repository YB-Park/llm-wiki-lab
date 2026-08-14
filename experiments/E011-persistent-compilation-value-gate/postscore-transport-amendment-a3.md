# E011 Stage 1A post-score transport amendment A3

Status: methodology amendment after model calls, before semantic interpretation.

The original 252 answer responses and original `parsed.json` artifacts remain immutable. No answer is rerun.

## Trigger

The non-scored preflight had already shown a valid JSON payload preceded by non-JSON prefix material. During Stage 1A, every `ANSWER-DONE` was initially classified contract-invalid. Interpretation was stopped before using those semantic scores.

Local aggregate diagnostics over all 252 actual answer responses, without printing response content, found:

- 252/252 contained a brace-delimited payload;
- 252/252 had prefix material and 0/252 had suffix material;
- 6/252 inner payloads were strict JSON;
- among strict failures, 243 were `Invalid control character` and 3 were `Expecting ',' delimiter` at the first strict failure;
- 232 strict failures decoded under Python JSON `strict=False`;
- smart quotes appeared in only 5 responses and smart-quote normalization did not improve recovery.

This pattern indicates that the initial E011 parser confounded a recurrent serialization boundary with semantic answer validity.

## Prior methodological precedent

Before E011 was scored, E009A's frozen verifier parser already used two narrow transport tolerances inherited from E007 lessons: extraction of a brace-delimited JSON object from surrounding response material, and `strict=False` only when strict decoding failed specifically with `Invalid control character`.

E011 unintentionally removed that established boundary while reusing the same Copilot CLI instrumentation.

## A3 recovery rule

A3 is intentionally limited to that prior precedent:

1. preserve the full original response unchanged;
2. isolate the substring from the first `{` through the last `}` only when no non-whitespace suffix follows it;
3. try strict JSON decoding;
4. only if strict decoding fails with `Invalid control character`, retry the unchanged payload with `strict=False`;
5. apply the original frozen E011 answer schema, source-visibility contract, and deterministic scoring to the decoded object;
6. if any step still fails, keep the answer invalid;
7. do not normalize smart quotes, repair commas/quotes, use JSON5, infer fields, or rerun the model.

Recovered parses are written to new A3-local artifacts. Original `response.txt`, `parsed.json`, telemetry, and original logical results are never overwritten.

## Interpretation constraint

A3 may recover transport-decodable answers but cannot erase the operational observation that the model/CLI path did not reliably emit strict JSON-only stdout under this setup. Report strict-output reliability separately from semantic quality after transport normalization.

Stage 1A remains controlled pilot evidence. This amendment does not change corpus, conditions, prompts, model, retrieval, ground truth, query order, reuse regimes, primary quality definitions, or lifecycle-cost accounting.
