# E023 preflight result v0 — zero-model lexical diagnostic

Status: **PASS / 0 model calls**  
GitHub Actions: `Validate E023 generality gate` run `32215427145`

This result validates the frozen corpus and records the production-shaped BM25 diagnostic. It is **not** a semantic answer result and is not evidence for persistent semantic state.

## Corpus integrity

- 18/18 source IDs and source-text hashes matched.
- 10/10 question IDs and question-spec hashes matched.
- family counts matched the preregistration.
- all required/forbidden references resolved.
- validator compiled and executed with `model_calls=0`.
- no paid execution runner exists in the preregistration branch.

A first zero-model pass exposed that Q003 had a strong same-surname distractor (S005) at lexical rank 2 while its forbidden-conflation field was empty. Before main freeze, the ground-truth contract was corrected to mark S005 as forbidden for Q003 and its question hash was refreshed. No semantic/model output had been observed.

## Exact-query BM25 diagnostic

| Q | family | required recall@5 | required ranks | forbidden distractor in top-5 |
|---|---|---:|---|---|
| Q001 | identity / attribution | 0.75 | S001=1, S002=5, S003=3, S004=7 | S005 |
| Q002 | identity / attribution | 0.75 | S001=2, S002=4, S003=6, S004=5 | S005 |
| Q003 | identity / attribution | 1.00 | S004=3, S006=1 | S005 |
| Q004 | decision rationale | 0.75 | S007=5, S008=8, S009=2, S010=1 | — |
| Q005 | incident / temporal | 1.00 | S011=1, S012=3, S013=2 | — |
| Q006 | incident / temporal | 1.00 | S011=2, S012=3, S013=4, S014=1 | — |
| Q007 | vendor constraint | 1.00 | S015=2, S016=1, S017=3 | — |
| Q008 | vendor constraint | 1.00 | S015=4, S017=3, S018=2 | — |
| Q009 | decision rationale | 1.00 | S008=3, S009=2, S010=5 | — |
| Q010 | identity / attribution | 0.75 | S001=3, S002=1, S003=8, S006=2 | S005 |

Six questions have complete required-source recall in the first five exact-query lexical hits. Four deliberately expose a retrieval gap before any semantic model is involved.

The strongest controlled stress appears in identity/alias/attribution:

- Q001 misses the directory identity bridge S004 at rank 7 while same-surname S005 is rank 2;
- Q002 misses meeting evidence S003 at rank 6 while S005 is rank 1;
- Q003 has both required identity/role sources in top-3 but still places S005 at rank 2, creating a clean false-merge stress case;
- Q010 misses recurring meeting evidence S003 at rank 8 and again surfaces S005 in top-5.

Q004 separately shows a non-identity cross-source retrieval gap: the Operations rationale S008 is rank 8 even though it is load-bearing for the decision explanation.

## Interpretation frozen before semantic execution

These lexical misses are **retrieval challenges**, not semantic FAILs.

If the later planned-query C arm recovers S004/S003/S008 without introducing false merges or epistemic errors, that is evidence for query-time retrieval planning/composition.

If C still does not retrieve those sources, the result remains retrieval-limited. It does **not** authorize persistence.

If C supplies the required evidence but the composer still confuses Park Jieun with Jihoon Park, collapses direct email and meeting attribution, reverses temporal semantics, or invents a personality characterization, that is a composition/epistemic failure.

No conclusion about G2 persistence or G3 identity/routing is earned by this preflight.
