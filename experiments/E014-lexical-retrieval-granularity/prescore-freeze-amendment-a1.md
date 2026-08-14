# E014 pre-score freeze amendment A1 — hash-record correction only

Status: **prescore amendment; no held-out scoring has occurred**

Date: 2026-08-14

## Trigger

The first prescore-only CI run (`31782617678`) stopped at the frozen-file SHA check before compilation, corpus validation, or held-out scoring.

A diagnostic-only follow-up run (`31782690451`) printed the actual repository byte hashes and stopped at the same SHA check. It also performed no held-out scoring.

`generate_corpus.py` matched the original freeze record. Three other frozen files did not.

## What changed

**Only the recorded SHA-256 values are corrected.**

No bytes in the corpus generator, retrieval conditions, scorer, prescore validator, preregistered metrics, gate thresholds, top-k, context cap, BM25 parameters, corpus seed, gold labels, or held-out corpus are changed by this amendment.

The affected files were created before `pre-run-freeze-v0.md` was committed and were not edited between their creation and the freeze. The mismatch is therefore a freeze-document/hash-transcription error, not a post-score code change.

## Original recorded hashes -> actual frozen repository hashes

- `generate_corpus.py`
  - recorded: `cbd81df876f6bf42e10118737137be6b5bc24edc9b7a30d72f0e4f88f0500c73`
  - actual:   `cbd81df876f6bf42e10118737137be6b5bc24edc9b7a30d72f0e4f88f0500c73`
  - status: unchanged / matched

- `retrieval_core.py`
  - recorded: `48c3aff5f365d4a305a5374abc90d0c196d7a312073c9de9f99e837623d3bba5`
  - actual:   `30049ba687d3ee99574184a5eb9271896f0e08778ab28fda6455eaf2a94f2bb8`
  - status: recorded hash corrected

- `analysis_v0.py`
  - recorded: `79d9ede37d096679d826e394fc39fa91ae7759b35f3a986efffdfd0168e75853`
  - actual:   `ea3f5d3c369083660f880a49ebd4d52499ffe36d9c6b3f07b23f4a536e55c710`
  - status: recorded hash corrected

- `validate_prescore.py`
  - recorded: `ef65c19751c6b64abc01c25a8655c60c89cdc9c6a001a822cf6f64008031332a`
  - actual:   `85905196a600421ff18141d01918dbc96cc7afeabe6dd2b37c546b40da5f7aad`
  - status: recorded hash corrected

## Evidence that no score informed this amendment

Both runs failed in the first SHA-verification step. The workflow's compile, core-test, prescore-validation, and scoring-capable analysis steps were not executed. The workflow was explicitly prescore-only and contained a guard rejecting an `analysis_v0.py` scoring command.

Therefore the held-out outcomes remained unseen when this amendment was made.

## Corpus freeze remains unchanged

Held-out corpus canonical SHA-256 remains:

`4dde1977666bf8f7494f5ca688631cfd2bb878272ccc1b7821456127d6778eed`

Development corpus disclosure-only SHA-256 remains:

`24c2f57b61804265ca79b24749e8c0ec81f25e461d3adb83066cf05c1029f49c`

## Next allowed action

Update only the SHA-verification records in `pre-run-freeze-v0.md` and `.github/workflows/validate-e014.yml`, rerun the prescore-only validation, and require it to pass before enabling the first official held-out score.

If any non-hash frozen experiment byte changes before the official score, this A1 amendment is insufficient and scoring must stop for a new explicit protocol version.