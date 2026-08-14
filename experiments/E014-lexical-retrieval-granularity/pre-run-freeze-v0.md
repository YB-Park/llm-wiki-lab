# E014 pre-run freeze v0

Status: **FROZEN BEFORE HELD-OUT SCORING**

Date: 2026-08-14

## Disclosure

A separate development sandbox was inspected before this freeze and was used to choose G2 over the simpler G1 paragraph-only rule. Development outcomes are non-evidentiary and must not be reported as E014 evidence.

The **held-out split has not been scored before this freeze**. Only deterministic generation/hash/structural validation is permitted before the scored run.

## Frozen held-out corpus

- split: `heldout`
- seed: `20260819`
- topics: 20
- queries: 60
- shapes: 5 each of `short`, `structured`, `flat`, `monolithic`
- frozen flat cross-boundary decision topics: 3
- canonical corpus SHA-256: `4dde1977666bf8f7494f5ca688631cfd2bb878272ccc1b7821456127d6778eed`

Development split canonical SHA-256, for disclosure only: `24c2f57b61804265ca79b24749e8c0ec81f25e461d3adb83066cf05c1029f49c`.

## Frozen code hashes

File-content SHA-256 values at freeze:

- `generate_corpus.py`: `cbd81df876f6bf42e10118737137be6b5bc24edc9b7a30d72f0e4f88f0500c73`
- `retrieval_core.py`: `48c3aff5f365d4a305a5374abc90d0c196d7a312073c9de9f99e837623d3bba5`
- `analysis_v0.py`: `79d9ede37d096679d826e394fc39fa91ae7759b35f3a986efffdfd0168e75853`
- `validate_prescore.py`: `ef65c19751c6b64abc01c25a8655c60c89cdc9c6a001a822cf6f64008031332a`

If repository bytes do not match these values, scored execution must stop until the discrepancy is explained and a new explicit freeze is created. Do not silently update hashes after seeing held-out outcomes.

## Frozen primary comparison

`G2 - W0` over target shapes `structured + flat`, topic as experimental unit.

Primary metrics:

- required-object recall@5;
- required-object MRR;
- required-signal recall@5.

Paired topic bootstrap:

- 20,000 resamples;
- seed `20260815`;
- no query-level pseudo-replication.

## Frozen conditions

- `W0`: one whole-object BM25 scoring unit; current-core paragraph-overlap snippet context.
- `G1`: heading sections else single paragraphs else whole object; diagnostic only.
- `G2`: heading sections else single paragraphs + adjacent two-paragraph windows else whole object; primary candidate.

All use tokenizer `[0-9a-zA-Z_가-힣]+`, casefold, BM25 `k1=1.5`, `b=0.75`, final object score = best unit score, context cap 320 chars/hit, top-k primary=5, secondary=8.

## Frozen gate

All must pass:

1. target recall@5 gain >= +0.15;
2. target recall@5 95% CI lower bound > 0;
3. target MRR gain >= +0.10;
4. short+monolithic recall@5 difference >= -0.05;
5. provenance reversibility 100%;
6. final duplicate object rate zero;
7. G2 indexed-character multiplier <= 3.0x W0;
8. cross-boundary flat decision recall@5 G2-G1 >= +0.10.

Any failure => `DOES_NOT_SURVIVE_DETERMINISTIC_GATE`.

## Forbidden post-score changes

After held-out scoring begins, do not change:

- corpus text/query/gold/lure generation;
- held-out seed;
- target/control shape assignment;
- BM25 parameters/tokenizer;
- section/paragraph/window rule;
- top-k values;
- 320-character context cap;
- primary metrics;
- bootstrap seed/reps/unit;
- gate thresholds.

A bug that invalidates scoring requires a documented abort/amendment, preservation of the invalid run, and a new versioned protocol. It does not permit quiet repair and rescoring.

## Model/network boundary

Stage A uses **zero model calls** and requires no external network data. The only permissible runtime is deterministic local Python plus repository code.

## Interpretation ceiling

Even a pass is only a held-out synthetic mechanism signal for deterministic lexical granularity. It cannot justify embeddings, vector/graph infrastructure, model-based reranking, or compiled Wiki activation.