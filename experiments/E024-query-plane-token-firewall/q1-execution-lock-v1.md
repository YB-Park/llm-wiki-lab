# E024 Q1 — execution/source lock v1

Status: **FROZEN BEFORE ANY E024 SEMANTIC MODEL CALL**

The first execution-signal attempt (`e135d3679af6b2d974eb63d7908b527c19d394f9`) produced zero CI/check runs and no evidence artifact. It is therefore **not an execution** and carries no semantic information. The signal was removed in `bff17b875e8d3c65e94072d39d6bc415e5a7d97a`.

Q1 v1 strengthens the execution boundary without changing the corpus, questions, retrieval, prompts, output contracts, model, call count, or promotion thresholds.

## Source-lock rules

A valid execution commit must:

1. have exactly one parent;
2. name that parent in `remote-lab/e024-q1-execute.json` as `frozen_parent_sha`;
3. differ from that parent by exactly one path: `remote-lab/e024-q1-execute.json`;
4. match the frozen prereg manifest SHA-256 in that signal;
5. match every SHA-256 listed in the prereg manifest;
6. match the Git blob identity of imported production `dogfood/llm_wiki/adapters.py`;
7. use exact `gpt-5.6-luna`, 18 maximum attempts, and zero rerolls.

Any mismatch invalidates the execution before a semantic call.

## Trigger transport

The preferred trigger remains a push of the one-file execution-signal commit to `experiment/e024-query-plane-gate`.

Because connector-authored ref updates did not produce a push Actions run in the first no-run attempt, the frozen workflow also supports a same-repository pull-request trigger **only** when the PR head branch is exactly `experiment/e024-query-plane-gate`. The PR trigger checks out the exact PR head commit and applies the same source lock.

The PR fallback is execution transport only. Opening a PR remains a separately authorized repository action and does not alter the semantic experiment.

## No post-output tuning

After a valid model run begins, do not change Q1 corpus, context freeze, prompts, thresholds, or reroll policy based on outputs. Any new hypothesis uses a new separated gate/version.
