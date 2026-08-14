# E011 remote Stage 1A conclusion v1

Status: controlled benchmark conclusion after the GitHub Actions JSONL transport replication.

## Research question

Does a persistent, query-independent compiled topic state earn a credible workload region of advantage over raw evidence plus retrieval, before detailed Wiki representation or maintenance machinery is justified?

## Methodological clarification

The first corporate Copilot CLI run was heavily confounded by text-stdout serialization. The same frozen E011 semantic fixture was therefore replicated on GitHub Actions with `gpt-5.6-luna`, changing only the Copilot transport boundary to programmatic JSONL. The final model answer was extracted from the `assistant.message` final-answer event and then passed unchanged to the frozen E011 answer contract.

The replication produced 252/252 contract-valid actual answer responses for 288 logical tasks. Therefore the corporate run's high invalid rate must not be interpreted as evidence that Luna or the Wiki conditions generally failed the answer contract. The corporate run remains useful as transport-boundary evidence.

## Observations

### Compiled-state fidelity

The generic compiler did not receive future questions or answer keys.

- small scale: required signals 108/108, required provenance 12/12, invented source IDs 0, compiled/raw byte ratio 0.536;
- large scale: required signals 108/108, required provenance 12/12, invented source IDs 0, compiled/raw byte ratio 0.183.

Within this synthetic static benchmark, durable query-independent synthesis preserved all preregistered future-critical signals and provenance while compressing the topic representation substantially, especially at larger scale.

### End-to-end answer quality

- R0 raw BM25: strict 60/72, signals 180/216, provenance 24/24;
- R1 all topic raw: strict 72/72, signals 216/216, provenance 24/24;
- C0 compiled synthesis only: strict 72/72, signals 216/216, provenance 24/24;
- C1 compiled synthesis plus R0 evidence: strict 72/72, signals 216/216, provenance 24/24.

R0 was perfect at small scale and for exact/provenance and global-synthesis queries. Its only loss occurred in the preregistered large-scale decision-rationale pressure region: R0 decision rationale 12/24 versus 24/24 for R1, C0, and C1. This matches the prescore retrieval diagnostic that large-scale R0 exposed only part of the required decision-rationale evidence.

C0 exactly matched the strongest raw full-topic condition R1 on every frozen quality metric. The experiment therefore does not show that compilation improves quality over full raw context; it shows that a reusable compiled state can preserve that quality while changing lifecycle economics.

C1 repaired R0's difficult large-scale retrieval misses but did so as an added-cost quality premium rather than a cost-saving architecture.

## Compilation economics

Using corrected single-span token accounting:

- R1 query tokens: 569,200;
- C0 query tokens: 530,025 plus compilation build cost;
- C0 versus R1 aggregate token break-even: approximately 6 topic revisits;
- all 24 topic-scale cells had finite C0 break-even; median 10.5 revisits, minimum 3, maximum 80;
- C1 versus R0 had no finite break-even in any topic-scale cell.

Frozen Pareto frontiers:

- N=1: R0, R1;
- N=3: R0, R1;
- N=10: R0, C0.

This is the first clean positive evidence for the project's materialized-view hypothesis: **reuse frequency is an economic axis of semantic compilation.** Compilation is not justified by default. It becomes competitive when reusable understanding is revisited enough times to amortize its build cost.

## What E011 supports

Controlled benchmark evidence supports the following working hypotheses:

1. A query-independent durable synthesis can preserve future-useful topic knowledge and provenance under the tested static workload.
2. A compiled-only state can match full raw-topic answer quality while reducing repeated query-time context cost.
3. The compiled state earns a credible high-reuse region rather than a universal advantage.
4. Cheap raw retrieval remains the preferred low-reuse baseline and is sufficient for many exact/global tasks.
5. Compiled+raw fallback is useful as a quality-recovery mechanism for hard retrieval cases, but Stage 1A does not justify it as a cost-saving default.

## What E011 does not support

Do not infer production superiority or a universal Wiki architecture. Important limitations remain:

- 12 synthetic author-defined topics;
- static corpus only, no update/maintenance waves;
- same model performs compilation and answering;
- deterministic topic routing is effectively given;
- token volume is an operational proxy, not human utility;
- no realistic distribution of topic revisit frequency has yet been measured;
- no changed-model replication has yet tested model dependence;
- full raw context remained perfect, so compilation's current advantage is amortization rather than superior reasoning over complete evidence.

## Program implication

Persistent compilation has now earned the right to remain in the research program, but only as a **selective high-reuse hypothesis**. Stage 1A does not justify detailed representation optimization or broad automatic canonicalization.

The next controlled falsification target should be maintenance economics: if update/recompilation, staleness, or review cost pushes the required revisit count beyond realistic usage, the apparent compilation dividend disappears.

In parallel, a realistic/shadow calibration should estimate whether personal knowledge topics actually receive enough decision/sensemaking revisits to make a roughly 6-to-10 revisit break-even plausible. A negative answer should narrow or kill durable compilation even if the synthetic static benchmark remains favorable.

## Cost observation

The full remote replication used 277 Luna model calls including one non-scored preflight, 24 compilation calls, and 252 deduplicated answer calls. Published-token-rate estimation was 227.541 AI credits. The 700-credit safety guard was not approached. This cost result also validates the remote GitHub Actions lab as a practical experimental runtime, but future experiments should continue to deduplicate prompts and prefer deterministic diagnostics before model calls.
