# E015-D1 — first real-user divergent-case result

Status: **PASS / ONE REALISTIC CASE ONLY**  
Date: 2026-08-15 KST

Workflow: `31862013373`  
Artifact: `9240865801`  
Main commit: `8fcc8d8dd490de14ad120fa3e9bfdadd0804e29a`

## Entering evidence

The frozen user question had failed twice under W0-backed Ask:

> E014-R1 passed. Why is `structural_expand_v1` still not the default, and what can E015 actually tell us?

A zero-model reconstruction corrected the initial diagnosis. Run `31861868445` / artifact `9240822200` showed:

- W0 ranked the correct E015 preregistration object;
- W0's best-paragraph excerpt omitted the decisive adjacent statements that E015 measures W0/X1 divergence and is **not a quality proof**;
- increasing W0 top-k did not repair the within-object excerpt loss;
- X1 on the same 299-file corpus/topic/query rendered a section containing both statements.

So D1 tested whether the existing X1 candidate repairs the observed user failure when the missing evidence is actually included in model context.

## Real-Luna result

D1 made exactly one new `gpt-5.6-luna` call. W0 current-only discovery still chose the topic; only the answer context used `structural_expand_v1`.

All preregistered checks passed:

- X1 context contained `E015 measures ... diverge`;
- X1 context contained `E015 is not a quality proof`;
- answer rejected default promotion from E014-R1 alone;
- answer described E015 as measuring realistic W0/X1 divergence/prevalence;
- answer explicitly said E015 is **not a quality proof**, cannot establish which mode is correct, and cannot promote X1 by itself;
- five materialized canonical citations all resolved through `source show`;
- exact response model was `gpt-5.6-luna`;
- final Alpha integrity was clean.

Representative answer excerpt:

> E015 can measure how often default W0 and candidate X1 diverge during natural, topic-scoped dogfood use. It is **not a quality proof**: users see W0 only, so shadow disagreement cannot establish which mode is correct, promote X1, or quantify quality benefit.

## Interpretation

This is the first realistic project-dogfood case where the E014-R1 mechanism is observed outside synthetic corpora: **the correct evidence object was retrieved, but W0 context granularity dropped a decisive neighboring statement; X1 preserved it and the real model answer recovered.**

Do not promote X1 globally from one case. The correct next evidence is additional **natural E015 divergent cases**, evaluated narrowly when they arise. Disagreement frequency remains descriptive and is not itself quality proof.
