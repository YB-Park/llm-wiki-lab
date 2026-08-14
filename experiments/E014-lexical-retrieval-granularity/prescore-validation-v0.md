# E014 prescore validation v0

Status: **PASS — held-out scoring authorized but not yet run at this record**

Date: 2026-08-14

## Prescore run

GitHub Actions run: `31782803222`

Branch head: `b1f0a2c91e48970025b391e1212965fa11b5d918`

Outcome: **SUCCESS**

## Checks passed

1. A1-corrected frozen experiment file hashes matched repository bytes:
   - `generate_corpus.py` = `cbd81df876f6bf42e10118737137be6b5bc24edc9b7a30d72f0e4f88f0500c73`
   - `retrieval_core.py` = `30049ba687d3ee99574184a5eb9271896f0e08778ab28fda6455eaf2a94f2bb8`
   - `analysis_v0.py` = `ea3f5d3c369083660f880a49ebd4d52499ffe36d9c6b3f07b23f4a536e55c710`
   - `validate_prescore.py` = `85905196a600421ff18141d01918dbc96cc7afeabe6dd2b37c546b40da5f7aad`
2. Frozen experiment and dogfood core compiled successfully.
3. Existing core regression suite: **34/34 PASS**, including all E013 calibration/privacy tests and evidence-identity/current-history invariants.
4. Held-out corpus canonical SHA-256 matched:
   `4dde1977666bf8f7494f5ca688631cfd2bb878272ccc1b7821456127d6778eed`
5. Held-out structure validated without scoring:
   - 20 topics;
   - 60 queries;
   - 5 topics each across 4 frozen shapes;
   - 3 frozen cross-boundary flat-decision cases;
   - required gold signals unique and located in required objects;
   - query strings contain no gold/lure marker leakage.
6. Provenance reversibility validated for W0/G1/G2: every retrieval unit maps exactly to object/source IDs and exact character slice.
7. W0 experimental implementation matched the current production dogfood whole-object BM25 order and numeric scores to <1e-12 on a separate non-held-out fixture.
8. Workflow asserted prescore-only mode; `analysis_v0.py` held-out scoring command was absent.
9. Model calls: **0**.

## Prior red runs

Two earlier prescore-only runs (`31782617678`, `31782690451`) stopped before scoring because three freeze-document SHA records were incorrect. `prescore-freeze-amendment-a1.md` documents the correction. The experiment/corpus/scorer bytes and preregistered gate did not change.

## Authorization

The next allowed repository change is a workflow-only transition that:

- preserves all frozen scorer/corpus bytes and A1-corrected SHA checks;
- reruns the prescore gate on the same bytes;
- only after that job succeeds, executes the **first official** `analysis_v0.py --split heldout` score;
- preserves the resulting output whether it passes or fails;
- performs no post-score retuning.

At the time this document is committed, official held-out outcomes remain unseen.