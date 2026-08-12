# Experiments

This directory contains controlled tests of competing LLM Wiki design choices.

## Directory convention

```text
experiments/
  E001-short-name/
    README.md
    corpus/
    prompts/
    runs/
    results/
    analysis.md
```

Not every experiment needs every directory. Preserve enough material to reproduce the claim being made.

## Before running

Write down:

- question,
- hypothesis,
- variants,
- corpus,
- metrics,
- expected failure modes.

When possible, freeze these before examining results.

## During a run

Record:

- date,
- model/tool identity,
- relevant configuration,
- prompt/instruction version,
- corpus commit/ref,
- raw outputs or a stable representation of them,
- deterministic evaluation output.

## After a run

Keep these separate:

1. **Results** — what happened.
2. **Interpretation** — what we think it means.
3. **Threats to validity** — why that interpretation may be wrong or narrow.
4. **Decision impact** — which design questions or ADRs this should influence.

## Anti-patterns

Do not:

- delete failed runs merely because they are messy,
- tune the metric after seeing the preferred architecture lose without documenting the change,
- rely only on LLM-as-judge for factual faithfulness,
- compare alternatives on different corpora and call the result causal,
- treat a statistically or numerically better result as automatically better for daily personal use.

See `docs/03-experiment-plan.md` for the initial experiment program.
