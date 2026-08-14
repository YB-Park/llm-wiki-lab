# E012 results v0 — reuse-to-update maintenance gate

Status: **completed; frozen remote run succeeded**

Workflow run: `31772119205`
Model: `gpt-5.6-luna`
Actual model calls: 253 (1 non-scored preflight + 36 builds + 216 scored answers)
Estimated AI credits: 224.401
Input tokens: 2,023,311
Output tokens: 36,783

## Headline result

E012 did **not** show update-induced semantic staleness for the full-rebuild compiled condition. The compiled state preserved every required answer signal at every wave, preserved all required provenance references, introduced no unknown source IDs, and produced no stale-current states.

However, `C0` was not strictly non-inferior to `R1` under the preregistered end-to-end frontier rule because three exact/provenance answers omitted required source IDs. Therefore E012 does **not** authorize compiled-only as a default answer path even though its measured lifecycle token break-even was favorable.

The result supports a narrower claim: query-independent durable compilation remains a plausible high-reuse mechanism under authoritative updates, but exact-provenance answering still needs stronger raw-evidence support or routing before architecture commitment.

## Scored answer quality

| condition | strict | required signals | provenance | invalid | stale substitution |
|---|---:|---:|---:|---:|---:|
| R1 | 108/108 | 336/336 | 72/72 | 0 | 0 |
| C0 | 105/108 | 336/336 | 69/72 | 0 | 0 |

By wave:

- R1: W0 36/36, W1 36/36, W2 36/36 strict.
- C0: W0 34/36, W1 36/36, W2 35/36 strict.

By query class:

- `current_exact`: R1 36/36; C0 33/36.
- `current_synthesis`: R1 36/36; C0 36/36.
- `decision_history`: R1 36/36; C0 36/36.

The three C0 strict failures were provenance failures rather than missing semantic answer signals: C0 still achieved 336/336 required-signal coverage and zero stale substitutions.

Topic-cluster paired bootstrap (`n=12` topics, 20,000 draws, frozen seed):

- strict-rate C0-R1: `-0.028 [-0.056, +0.000]`
- signal-rate C0-R1: `+0.000 [+0.000, +0.000]`
- provenance-rate C0-R1: `-0.042 [-0.083, +0.000]`

These intervals touch zero. This controlled pilot therefore does not establish a stable small quality disadvantage, but the frozen architecture frontier uses point-estimate non-inferiority and consequently does not award C0 the frontier.

## Compiled-state diagnostics

The compilation layer itself remained strong across updates:

| wave | required signals | required provenance | stale states | unknown source IDs | compiled/raw bytes |
|---|---:|---:|---:|---:|---:|
| W0 | 108/108 | 24/24 | 0/12 | 0 | 0.194 |
| W1 | 108/108 | 24/24 | 0/12 | 0 | 0.151 |
| W2 | 120/120 | 24/24 | 0/12 | 0 | 0.147 |

Thus the observed end-to-end misses occurred at answer/provenance emission time, not because the compiled state lost the current facts or source references.

## Maintenance economics

Measured query token totals across all three waves:

- R1 query tokens: 927,741
- C0 query tokens: 803,968
- total C0 rebuild tokens implied by lifecycle accounting: 321,358

Finite break-even existed for all 12 topics:

- aggregate revisits/update break-even: **3**
- topic finite: 12/12
- per-topic median/min/max: **3 / 3 / 3**

Frozen lifecycle replay:

| revisits per update | R1 tokens | C0 tokens | frozen frontier |
|---:|---:|---:|---|
| 1 | 927,741 | 1,125,326 | R1 |
| 3 | 2,783,223 | 2,733,262 | R1 |
| 6 | 5,566,446 | 5,145,166 | R1 |
| 10 | 9,277,410 | 8,361,038 | R1 |
| 20 | 18,554,820 | 16,400,718 | R1 |

C0 becomes cheaper from roughly three revisits/update, but the preregistered frontier remains R1 at every regime because C0 did not equal or exceed R1 on every headline quality point estimate. Cost savings do not override the provenance deficit.

## Interpretation

E012 falsifies one important concern: **simple full rebuild from authoritative raw evidence did not collapse under supersession/correction/history updates in this benchmark.** Current-state semantics were retained, historical facts were not substituted as current, and compression improved from 19.4% to 14.7% of raw bytes as the topic accumulated updates.

It also exposes a sharper boundary: **compiled-only works cleanly for synthesis and decision/history here, while exact-provenance questions remain the weak point.** This class result is secondary and should be treated as a hypothesis generator, not as a production routing policy.

Therefore the next evidence step should not be a more elaborate Wiki schema, verifier stack, or incremental-maintenance algorithm. The next step is realistic/shadow calibration of:

1. actual topic revisits per update;
2. query-class mix, especially exact/provenance versus synthesis/decision queries;
3. human utility and navigation friction;
4. whether a conservative raw-first or raw-backed route for exact provenance removes the observed deficit without erasing the compilation dividend.

The dogfood substrate may be used to collect these workload observations while keeping compiled state non-canonical and shadow-only.

## Evidence grade and limits

Evidence grade: controlled synthetic maintenance-mechanism/economics pilot.

Limits remain: 12 synthetic topics, author-defined ground truth, full-rebuild baseline, same model building and consuming compiled state, oracle topic routing, token cost as a proxy for operational value, and no production/human workload evidence.

## Budget note

The run used 224.401 estimated AI credits, well below the preregistered 400-credit infrastructure guard. No semantic rerolls were used and no company data was involved.
