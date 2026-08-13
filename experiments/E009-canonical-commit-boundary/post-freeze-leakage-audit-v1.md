# E009A Post-Freeze Leakage Audit v1

Status: **interpretation-only diagnostic; frozen semantic corpus unchanged**

This audit was added after an external critical review noted that T-v1 still had residual one-dimensional surface predictability. It was run before any scored Corpus T verifier result was observed.

It does **not** authorize any edit to:

- Corpus T-v1;
- gold/risk labels;
- verifier prompt;
- A0-A4 policy semantics;
- call order;
- primary model.

Its only purpose is to calibrate the evidence grade of future E009A results.

## Method

Leave-one-scenario-group-out (LOSGO) validation over 20 paired scenario groups / 40 candidate states.

Fixed pre-result baselines:

1. scalar surface logistic model using candidate length, candidate/previous length ratio, token diff size, source-count deltas, temporal markers, and negation/conflict markers;
2. word TF-IDF + fixed logistic model over raw candidate text;
3. word TF-IDF + fixed logistic model after normalizing source IDs and numeric literals.

No hyperparameter search was performed. Diagnostic hyperparameters are frozen in `harness/audit_surface_leakage_v1.py`.

## Results

```text
scalar          26/40 = 0.650; fully correct pairs 7/20
TF-IDF raw      28/40 = 0.700; fully correct pairs 9/20
TF-IDF scrubbed 28/40 = 0.700; fully correct pairs 10/20
```

The workflow completed successfully in GitHub Actions.

## Interpretation

### Observation

A cheap surface/lexical model can predict the author-defined safe/unsafe label materially above chance even when evaluation leaves out an entire paired scenario group.

Normalizing source IDs and numbers did not remove the 0.700 TF-IDF result, so residual predictability is not explained solely by citation-count or numeric-literal leakage.

### What this does NOT prove

It does not prove that GPT-5.6 Luna will use the same shortcut.

Some lexical cues can be semantically legitimate: words expressing uncertainty, historical state, or unsupported certainty may genuinely correlate with transition safety.

The audit also uses only 40 cases, so the exact 0.650/0.700 point estimates should not be treated as stable production baselines.

### Evidence-grade consequence

E009A must be treated as a **controlled pilot/benchmark** rather than direct production evidence even if verifier performance is strong.

Future interpretation should compare the verifier against these cheap baselines. A narrow improvement over ~0.70 is weak evidence that the verifier learned the intended semantic transition task.

If an architecture-level conclusion depends on E009A, require replication on a materially different corpus, preferably with independently authored/labeled candidates and a renewed leakage audit.

## Frozen-corpus rule

Do not edit T-v1 to force cheap-baseline accuracy toward 0.50 after this result. Doing so would optimize the benchmark against a post-freeze diagnostic and create a new form of benchmark overfitting.
