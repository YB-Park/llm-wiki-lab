# Full-Harness Preflight Finding — Literal Control Character in JSON

Date: 2026-08-12
Status: **transport failure found before scored runs; parser fix applied, rerun pending**

## Observation

The first corporate `full_harness_preflight.py` run reached the C3 verifier JSON path and failed while parsing the Luna response.

The observed exception was:

```text
json.decoder.JSONDecodeError: Invalid control character at: line 2 column 76
ValueError: response JSON is malformed: Invalid control character ...
```

The failure occurred in:

```text
full_harness_preflight.py
  -> parse_verification()
  -> extract_json_object()
  -> json.loads()
```

No Corpus C material was used and no scored C0–C4 result had begun.

## Interpretation

This is not evidence that the verifier's semantic judgment was correct or incorrect.

It is evidence that an LLM can violate strict JSON serialization even under a JSON-only contract by emitting a literal newline/tab/control character inside a quoted string. A harness that treats strict JSON decoding as infallible can therefore abort a maintenance workflow before semantic validation even begins.

This is a useful systems lesson for the wider LLM Wiki project:

> structured LLM output needs a deterministic transport/schema boundary that is robust to narrow serialization defects without silently repairing semantic or structural errors.

## Fix boundary

`score_deterministic.extract_json_object()` now:

1. tries normal strict `json.loads`,
2. only when the decoder reports `Invalid control character`, retries the same bytes with `strict=False`,
3. continues to reject missing quotes, commas, braces, ambiguous structure, and other malformed JSON.

The fallback does not rewrite, infer, or repair model meaning. It only permits literal control characters inside already quoted JSON strings.

## Experimental integrity

This fix is classified as **transport robustness**, not prompt/condition tuning.

It does not change:

- Corpus C,
- C0–C4 maintenance prompts,
- condition semantics,
- frozen `n=3` repetition count,
- run order,
- scoring rubrics.

The full-harness preflight must be rerun after the fix. Only a PASS permits the first scored Family N block to begin.
